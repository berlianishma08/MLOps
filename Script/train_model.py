import os
import argparse
import pandas as pd
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, confusion_matrix
import joblib
import logging
import mlflow
import mlflow.sklearn
import matplotlib.pyplot as plt
from mlflow.models.signature import infer_signature


log_dir = os.path.join(os.getcwd(), "Log")
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, "train.log")

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def load_data(data_dir):
    logging.info(f"Loading data from {data_dir}...")
    X_train_path = os.path.join(data_dir, "X_train.csv")
    y_train_path = os.path.join(data_dir, "y_train.csv")
    X_test_path = os.path.join(data_dir, "X_test.csv")
    y_test_path = os.path.join(data_dir, "y_test.csv")

    if not all(map(os.path.exists, [X_train_path, y_train_path, X_test_path, y_test_path])):
        raise FileNotFoundError("One or more dataset files not found in the provided directory.")

    X_train = pd.read_csv(X_train_path)
    y_train = pd.read_csv(y_train_path)
    X_test = pd.read_csv(X_test_path)
    y_test = pd.read_csv(y_test_path)

    y_train = y_train.iloc[:, 0] if isinstance(y_train, pd.DataFrame) else y_train
    y_test = y_test.iloc[:, 0] if isinstance(y_test, pd.DataFrame) else y_test

    logging.info("Data loaded successfully.")
    return X_train, X_test, y_train, y_test


def log_confusion_matrix(model, X_test, y_test):
    preds = model.predict(X_test)
    cm = confusion_matrix(y_test, preds)

    plt.figure(figsize=(6, 4))
    plt.title("Confusion Matrix")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.tight_layout()
    cm_path = "confusion_matrix.png"
    plt.savefig(cm_path)
    plt.close()
    mlflow.log_artifact(cm_path)


def train_model(X_train, X_test, y_train, y_test, model_name="xgboost", params=None):
    # Optional: set a tracking URI to a remote MLflow server
    # mlflow.set_tracking_uri("http://your-mlflow-server:5000")

    with mlflow.start_run():
        mlflow.autolog()
        logging.info(f"Training the model: {model_name}...")
        if params:
            mlflow.log_params(params)

        # Model selection
        if model_name == "xgboost":
            model = XGBClassifier(**params or {})
        elif model_name in ["lgbm", "gbdt"]:
            model = LGBMClassifier(**params or {})
        elif model_name == "random_forest":
            model = RandomForestClassifier(n_estimators=100, random_state=42, **(params or {}))
        elif model_name == "svm":
            model = SVC(**params or {})
        elif model_name == "logistic_regression":
            model = LogisticRegression(**params or {})
        else:
            raise ValueError(f"Model '{model_name}' not supported.")

        try:
            model.fit(X_train, y_train)
            logging.info(f"Model {model_name} trained successfully.")

            # Evaluate
            accuracy = evaluate_model(model, X_test, y_test)
            mlflow.log_metric("accuracy", accuracy)

            # Signature + example
            signature = infer_signature(X_test, model.predict(X_test))
            input_example = X_test.head(3)

            # Model logging
            if model_name == "xgboost":
                mlflow.xgboost.log_model(model, "model", signature=signature, input_example=input_example)
            elif model_name in ["lgbm", "gbdt"]:
                mlflow.lightgbm.log_model(model, "model", signature=signature, input_example=input_example)
            else:
                mlflow.sklearn.log_model(model, "model", signature=signature, input_example=input_example)

            # Save confusion matrix as artifact
            log_confusion_matrix(model, X_test, y_test)

        except Exception as e:
            logging.error(f"Error during training: {e}")
            raise

        return model


def evaluate_model(model, X_test, y_test):
    logging.info("Evaluating the model...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    logging.info(f"Accuracy: {accuracy:.4f}")
    return accuracy


def save_model(model, model_dir, model_name, timestamp):
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, f"{model_name}_{timestamp}.pkl")
    logging.info(f"Saving model to {model_path}...")

    try:
        joblib.dump(model, model_path)
        logging.info("Model saved successfully.")
    except Exception as e:
        logging.error(f"Error saving model: {e}")
        raise

    return model_path


def main(data_dir, model_dir, timestamp, model_name="xgboost", params=None):
    X_train, X_test, y_train, y_test = load_data(data_dir)
    model = train_model(X_train, X_test, y_train, y_test, model_name, params)
    save_model(model, model_dir, model_name, timestamp)
    logging.info("Model training and saving completed successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a machine learning model.")
    parser.add_argument("-d", "--data_dir", type=str, required=True, help="Path to data directory.")
    parser.add_argument("-m", "--model_dir", type=str, required=True, help="Path to save model.")
    parser.add_argument("-n", "--model_name", type=str, default="xgboost",
                        help="Model name: 'xgboost', 'lgbm', 'random_forest', 'svm', 'logistic_regression'.")
    parser.add_argument("-p", "--params", type=str, default=None, help="Model hyperparameters as JSON string.")
    parser.add_argument("-t", "--timestamp", type=str, required=True, help="Timestamp for saved model.")

    args = parser.parse_args()
    params = None
    if args.params:
        import json
        params = json.loads(args.params)

    main(args.data_dir, args.model_dir, args.timestamp, args.model_name, params)
