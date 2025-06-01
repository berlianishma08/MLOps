from flask import Flask, request, jsonify, render_template
import pandas as pd
import joblib
import os

app = Flask(__name__)

# Load model
MODEL_PATH = "Model/model/RandomForestClassifier_deployed_20250523_065425.pkl"
model = joblib.load(MODEL_PATH)

# Halaman 1: Home page (GET)
@app.route("/")
def home():
    return render_template("index.html")

# Halaman 2: Prediction endpoint (POST)
@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Ambil data dari form atau API
        input_data = request.get_json() or request.form.to_dict()
        df = pd.DataFrame([input_data])
        prediction = model.predict(df)[0]
        return jsonify({"prediction": int(prediction)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="54.166.16.28", port=3000)
