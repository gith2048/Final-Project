from flask import Blueprint, request, jsonify
import pickle
import pandas as pd
from keras.models import load_model
import numpy as np

predict_bp = Blueprint("predict", __name__)

# Load models
with open("model/iso_model.pkl", "rb") as f:
    iso_model = pickle.load(f)
with open("model/rf_model.pkl", "rb") as f:
    rf_model = pickle.load(f)

@predict_bp.route("/predict/anomaly", methods=["POST"])
def predict_anomaly():
    data = request.json
    df = pd.DataFrame([data])
    result = iso_model.predict(df[["temperature", "current", "speed"]])
    return jsonify({"anomaly": int(result[0])})

@predict_bp.route("/predict/failure", methods=["POST"])
def predict_failure():
    data = request.json
    df = pd.DataFrame([data])
    result = rf_model.predict(df[["temperature", "current", "speed"]])
    return jsonify({"failure_risk": int(result[0])})


# Load LSTM model and scaler
lstm_model = load_model("model/lstm_model.keras")
with open("model/temp_scaler.pkl", "rb") as f:
    temp_scaler = pickle.load(f)

@predict_bp.route("/predict/forecast", methods=["POST"])
def forecast_temperature():
    data = request.json["sequence"]  # expects last 10 temperature values
    scaled = temp_scaler.transform(np.array(data).reshape(-1, 1))
    X_input = scaled.reshape((1, len(data), 1))
    prediction = lstm_model.predict(X_input)
    next_temp = temp_scaler.inverse_transform(prediction)[0][0]
    return jsonify({"forecast_temperature": round(next_temp, 2)})