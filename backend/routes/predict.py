from flask import Blueprint, request, jsonify
import pickle
import pandas as pd
import numpy as np
from keras.models import load_model
from models.machine_data import MachineData
from extensions import db

predict_bp = Blueprint("predict", __name__)

# Load models
with open("model/iso_model.pkl", "rb") as f:
    iso_model = pickle.load(f)
with open("model/rf_model.pkl", "rb") as f:
    rf_model = pickle.load(f)
with open("model/multi_scaler.pkl", "rb") as f:
    temp_scaler = pickle.load(f)
lstm_model = load_model("model/lstm_model.keras")

# Thresholds
TEMP_THRESHOLD = 70.0
VIBRATION_THRESHOLD = 5.0
SPEED_THRESHOLD = 1200
NOISE_THRESHOLD = 80.0

def generate_overall_summary(temp, vib, speed, noise, next_temp, rf_result, iso_result):
    summary = []

    if vib > VIBRATION_THRESHOLD:
        summary.append("⚠️ Vibration levels are high. Inspect bearings, alignment, and structural integrity.")
    elif speed > SPEED_THRESHOLD:
        summary.append("⚠️ Speed exceeds optimal range. Verify motor calibration and load conditions.")
    elif noise > NOISE_THRESHOLD:
        summary.append("⚠️ Noise levels are elevated. Check for loose components or worn-out insulation.")
    elif next_temp > TEMP_THRESHOLD:
        summary.append("⚠️ Temperature is forecasted to rise. Inspect cooling and lubrication systems.")
    elif rf_result == 1:
        summary.append("⚠️ Random Forest model indicates high failure risk.")
    elif iso_result == -1:
        summary.append("⚠️ Anomaly detected by Isolation Forest.")
    else:
        summary.append("✅ The machine is operating within safe parameters.")

    return "\n".join(summary)

@predict_bp.route("/predict", methods=["POST"])
def predict_all():
    payload = request.json

    temp = float(payload["temperature"])
    speed = float(payload["speed"])
    vibration = float(payload["vibration"])
    current = float(payload["current"])
    noise = float(payload["noise"])
    sequence = payload["sequence"]  # List of 5-feature vectors

    # Prepare input for models
    features = pd.DataFrame([{
        "temperature": temp,
        "speed": speed,
        "vibration": vibration,
        "current": current,
        "noise": noise
    }])

    # Isolation Forest
    iso_result = int(iso_model.predict(features)[0])
    iso_score = float(iso_model.decision_function(features)[0])

    # Random Forest
    rf_result = int(rf_model.predict(features)[0])

    # LSTM Forecast
    scaled_seq = temp_scaler.transform(sequence)
    X_input = scaled_seq.reshape((1, len(sequence), 5))
    prediction = lstm_model.predict(X_input)[0]
    forecast = temp_scaler.inverse_transform([prediction])[0]

    # Build response
    response = {
        "lstm": {
            "forecast": {
                "temperature": round(forecast[0], 2),
                "speed": round(forecast[1], 2),
                "vibration": round(forecast[2], 2),
                "current": round(forecast[3], 2),
                "noise": round(forecast[4], 2)
            },
            "issue": f"📈 Forecasted temperature: {round(forecast[0], 2)}°C" + (" 🚨 High!" if forecast[0] > TEMP_THRESHOLD else ""),
            "cause": "Temperature trend indicates rising pattern due to poor lubrication or high load." if forecast[0] > TEMP_THRESHOLD else "Temperature trend is stable.",
            "solution": "Inspect cooling system, verify lubrication, and reduce load." if forecast[0] > TEMP_THRESHOLD else "No action needed."
        },
        "random_forest": {
            "failure_risk": rf_result,
            "issue": "⚠️ Fault detected" if rf_result == 1 else "✅ Machine is operating normally",
            "cause": "Sensor readings show elevated stress on components." if rf_result == 1 else "Sensor readings are within safe thresholds.",
            "solution": "Schedule inspection and check motor alignment." if rf_result == 1 else "Continue preventive maintenance."
        },
        "isolation_forest": {
            "anomaly": iso_result,
            "score": round(iso_score, 2),
            "issue": "🚨 Anomaly detected!" if iso_result == -1 else "✅ No anomalies detected",
            "cause": "Unusual sensor combination suggests drift or fault." if iso_result == -1 else "Sensor readings are consistent.",
            "solution": "Recalibrate sensors and inspect components." if iso_result == -1 else "No action needed."
        },
        "thresholds": {
            "temperature": {
                "value": temp,
                "status": "🚨 High" if temp > TEMP_THRESHOLD else "✅ Normal"
            },
            "vibration": {
                "value": vibration,
                "status": "🚨 High" if vibration > VIBRATION_THRESHOLD else "✅ Normal"
            },
            "speed": {
                "value": speed,
                "status": "🚨 High" if speed > SPEED_THRESHOLD else "✅ Normal"
            },
            "noise": {
                "value": noise,
                "status": "🚨 High" if noise > NOISE_THRESHOLD else "✅ Normal"
            }
        },
        "overall_summary": generate_overall_summary(temp, vibration, speed, noise, forecast[0], rf_result, iso_result)
    }

    # Save to database
    entry = MachineData(
        temperature=temp,
        speed=speed,
        vibration=vibration,
        current=current,
        noise=noise,
        forecast_temperature=forecast[0],
        forecast_speed=forecast[1],
        forecast_vibration=forecast[2],
        forecast_current=forecast[3],
        forecast_noise=forecast[4],
        failure_risk=rf_result,
        anomaly_score=iso_score,
        anomaly_flag=(iso_result == -1),
        summary=response["overall_summary"]
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify(response)