from flask import Flask, request, jsonify
import joblib
import pandas as pd

app = Flask(__name__)

# Load model yang sudah di-deploy
model = joblib.load("Model/model/RandomForestClassifier_deployed_20250523_065425.pkl")

@app.route('/')
def home():
    return "🚀 Model is running!"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    df = pd.DataFrame([data])
    prediction = model.predict(df)
    return jsonify({'prediction': int(prediction[0])})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
