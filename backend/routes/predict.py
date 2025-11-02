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
with open("model/temp_scaler.pkl", "rb") as f:
    temp_scaler = pickle.load(f)
lstm_model = load_model("model/lstm_model.keras")

# Thresholds
TEMP_THRESHOLD = 70.0
VIBRATION_THRESHOLD = 5.0
SPEED_THRESHOLD = 1200

def generate_overall_summary(temp, current, speed, next_temp, rf_result, iso_result):
    summary = []

    if current > VIBRATION_THRESHOLD:
        summary.append("⚠️ Vibration levels are high. Inspect bearings, alignment, and structural integrity.")
        summary.append("Elevated vibration may signal imbalance or wear in rotating parts.")
        summary.append("If ignored, this can lead to mechanical failure or safety risks.")
        summary.append("A preventive maintenance check is strongly recommended.")

    elif speed > SPEED_THRESHOLD:
        summary.append("⚠️ Speed exceeds optimal range. Verify motor calibration and load conditions.")
        summary.append("Excessive RPM may cause wear, imbalance, or noise.")
        summary.append("Monitor for signs of mechanical strain or instability.")
        summary.append("Adjust operational parameters to maintain safe speed.")

    elif next_temp > TEMP_THRESHOLD:
        summary.append("⚠️ Temperature is forecasted to rise. Inspect cooling and lubrication systems.")
        summary.append("Sustained high temperatures can degrade components and affect performance.")
        summary.append("Ensure cooling systems are functioning properly.")
        summary.append("Schedule a thermal inspection to avoid downtime.")

    elif rf_result == 1:
        summary.append("⚠️ Random Forest model indicates high failure risk.")
        summary.append("Sensor readings show elevated stress on components.")
        summary.append("Immediate inspection is advised to prevent breakdown.")
        summary.append("Check motor alignment and load distribution.")

    elif iso_result == -1:
        summary.append("⚠️ Anomaly detected by Isolation Forest.")
        summary.append("Unusual sensor combination suggests drift or fault.")
        summary.append("Recalibrate sensors and inspect components.")
        summary.append("Investigate for hidden mechanical issues.")

    else:
        summary.append("✅ The machine is operating within safe parameters.")
        summary.append("All metrics are stable and below critical thresholds.")
        summary.append("No immediate action is required.")
        summary.append("Continue monitoring and preventive maintenance.")

    return "\n".join(summary)

@predict_bp.route("/predict", methods=["POST"])
def predict_all():
    payload = request.json

    temp = float(payload["temperature"])
    current = float(payload["current"])
    speed = float(payload["speed"])
    sequence = payload["sequence"]

    df = pd.DataFrame([{
        "temperature": temp,
        "current": current,
        "speed": speed
    }])

    # Isolation Forest
    iso_result = int(iso_model.predict(df[["temperature", "current", "speed"]])[0])
    iso_score = float(iso_model.decision_function(df[["temperature", "current", "speed"]])[0])

    # Random Forest
    rf_result = int(rf_model.predict(df[["temperature", "current", "speed"]])[0])

    # LSTM Forecast
    scaled_seq = temp_scaler.transform(np.array(sequence).reshape(-1, 1))
    X_input = scaled_seq.reshape((1, len(sequence), 1))
    prediction = lstm_model.predict(X_input)
    next_temp = float(temp_scaler.inverse_transform(prediction)[0][0])

    # Build response
    response = {
        "lstm": {
            "forecast_temperature": round(next_temp, 2),
            "issue": f"📈 Forecasted temperature: {round(next_temp, 2)}°C" + (" 🚨 High!" if next_temp > TEMP_THRESHOLD else ""),
            "cause": "Temperature trend indicates rising pattern due to poor lubrication or high load." if next_temp > TEMP_THRESHOLD else "Temperature trend is stable.",
            "solution": "Inspect cooling system, verify lubrication, and reduce load." if next_temp > TEMP_THRESHOLD else "No action needed."
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
                "value": current,
                "status": "🚨 High" if current > VIBRATION_THRESHOLD else "✅ Normal"
            },
            "speed": {
                "value": speed,
                "status": "🚨 High" if speed > SPEED_THRESHOLD else "✅ Normal"
            }
        },
        "overall_summary": generate_overall_summary(temp, current, speed, next_temp, rf_result, iso_result)
    }

    # Save to database
    entry = MachineData(
    temperature=temp,
    current=current,
    speed=speed,
    forecast_temperature=next_temp,
    failure_risk=rf_result,
    anomaly_score=iso_score,
    anomaly_flag=(iso_result == -1),
    summary=response["overall_summary"]
    )
    db.session.add(entry)
    db.session.commit()
   
    return jsonify(response)