# routes/predict.py
from flask import Blueprint, request, jsonify
import pickle
import numpy as np
import pandas as pd
from keras.models import load_model
from models.machine_data import MachineData
from extensions import db
import os

predict_bp = Blueprint("predict", __name__)

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model")

# -----------------------------
# Safe Loader
# -----------------------------
def load_pickle(path):
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Failed loading {path}: {e}")
        return None

# -----------------------------
# Load MODELS (3-parameter versions)
# -----------------------------
iso_model = load_pickle(os.path.join(MODEL_DIR, "iso_model.pkl"))
rf_model = load_pickle(os.path.join(MODEL_DIR, "rf_model.pkl"))

# FIXED — load the correct scaler
multi_scaler = load_pickle(os.path.join(MODEL_DIR, "lstm_scaler.pkl"))

# LSTM model
lstm_path = os.path.join(MODEL_DIR, "lstm_model.keras")
lstm_model = load_model(lstm_path) if os.path.exists(lstm_path) else None

# -----------------------------
# Thresholds
# -----------------------------
TEMP_THRESHOLD = 70.0
VIBRATION_THRESHOLD = 5.0
SPEED_THRESHOLD = 1200

# -----------------------------
# Summary Generator
# -----------------------------
def generate_overall_summary(temp, vib, speed, next_temp, rf_result, iso_result):

    if vib > VIBRATION_THRESHOLD:
        return "⚠️ High vibration detected. Inspect bearings & alignment."

    if speed > SPEED_THRESHOLD:
        return "⚠️ Speed exceeds optimal range. Check calibration & load."

    if next_temp > TEMP_THRESHOLD:
        return "⚠️ Forecast shows overheating. Inspect cooling system."

    if rf_result == 1:
        return "⚠️ Random Forest indicates high failure risk."

    if iso_result == -1:
        return "⚠️ Isolation Forest detected anomaly."

    return "✅ Machine operating safely."

# -----------------------------
# PREDICT ENDPOINT (3 parameters only)
# -----------------------------
@predict_bp.route("/predict", methods=["POST"])
def predict_all():
    data = request.json

    temp = float(data["temperature"])
    speed = float(data["speed"])
    vibration = float(data["vibration"])

    sequence = data["sequence"]      # last 5 readings, shape (5,3)

    # ===============================================
    # Isolation Forest
    # ===============================================
    features = pd.DataFrame([{
        "temperature": temp,
        "speed": speed,
        "vibration": vibration
    }])

    iso_result = int(iso_model.predict(features)[0])
    iso_score = float(iso_model.decision_function(features)[0])

    # ===============================================
    # Random Forest
    # ===============================================
    rf_result = int(rf_model.predict(features)[0])

    # ===============================================
    # LSTM Forecast
    # ===============================================
    seq = np.array(sequence).astype(float)
    scaled = multi_scaler.transform(seq)

    X = scaled.reshape(1, scaled.shape[0], scaled.shape[1])
    pred = lstm_model.predict(X, verbose=0)[0]

    inv = multi_scaler.inverse_transform([pred])[0]

    next_temp, next_speed, next_vibration = float(inv[0]), float(inv[1]), float(inv[2])

    # ===============================================
    # Final Response
    # ===============================================
    response = {
        "forecast": {
            "temperature": next_temp,
            "speed": next_speed,
            "vibration": next_vibration
        },
        "random_forest": rf_result,
        "isolation_forest": iso_result,
        "iso_score": iso_score,
        "thresholds": {
            "temperature": "High" if temp > TEMP_THRESHOLD else "Normal",
            "speed": "High" if speed > SPEED_THRESHOLD else "Normal",
            "vibration": "High" if vibration > VIBRATION_THRESHOLD else "Normal"
        },
        "overall_summary": generate_overall_summary(
            temp, vibration, speed, next_temp, rf_result, iso_result
        )
    }

    # Save to DB
    entry = MachineData(
        temperature=temp,
        speed=speed,
        vibration=vibration,
        forecast_temperature=next_temp,
        forecast_speed=next_speed,
        forecast_vibration=next_vibration,
        failure_risk=rf_result,
        anomaly_score=iso_score,
        anomaly_flag=(iso_result == -1),
        summary=response["overall_summary"]
    )

    db.session.add(entry)
    db.session.commit()

    return jsonify(response)
