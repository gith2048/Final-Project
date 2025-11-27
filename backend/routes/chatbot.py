# routes/chatbot.py
from flask import Blueprint, request, jsonify
import requests
import os

chatbot_bp = Blueprint("chatbot", __name__)

PREDICT_URL = "http://localhost:5000/predict"

def detect_intent(message):
    msg = (message or "").lower()
    if any(w in msg for w in ["anomaly", "abnormal"]): return "anomaly"
    if any(w in msg for w in ["failure", "risk", "breakdown"]): return "failure"
    if any(w in msg for w in ["forecast", "predict", "temperature", "vibration", "speed"]): return "forecast"
    if any(w in msg for w in ["recommend", "suggest"]): return "recommend"
    if any(w in msg for w in ["help"]): return "help"
    return "unknown"

@chatbot_bp.route("/", methods=["POST"])
def chat():
    payload = request.json or {}
    message = payload.get("message", "")
    chartData = payload.get("chartData") or payload.get("chart") or None

    intent = detect_intent(message)

    # If chartData exists, construct predict payload; else require sequence + latest
    predict_payload = {}
    if chartData:
        predict_payload["chartData"] = chartData
    else:
        # allow directly sent sequence/latest values
        predict_payload["temperature"] = payload.get("temperature")
        predict_payload["vibration"] = payload.get("vibration")
        predict_payload["speed"] = payload.get("speed")
        predict_payload["sequence"] = payload.get("sequence", [])

    # call the predict endpoint
    try:
        res = requests.post(PREDICT_URL, json=predict_payload, timeout=5)
        result = res.json()
    except Exception as e:
        return jsonify({"response": "❌ Prediction engine is unavailable."})

    # Build natural language response depending on intent
    # Always include summary + structured recommendations
    lstm_f = result.get("lstm", {}).get("forecast", {})
    rf = result.get("random_forest", {})
    iso = result.get("isolation_forest", {})
    thresholds = result.get("thresholds", {})

    # Build a succinct summary
    summary_lines = []
    summary_lines.append(result.get("overall_summary") or "Machine health summary:")

    # Temperature note
    summary_lines.append(f"Temperature (latest): {thresholds.get('temperature','N/A')} - {lstm_f.get('temperature', 'N/A'):.2f}°C" if lstm_f.get("temperature") is not None else f"Temperature: {thresholds.get('temperature','N/A')}")

    # RF & ISO quick notes
    rf_label = rf.get("label") or ("critical" if rf.get("pred")==2 else "warning" if rf.get("pred")==1 else "normal")
    iso_note = "Anomaly detected" if iso.get("pred") == -1 else "No anomaly"

    # Intent-specific responses
    if intent == "anomaly":
        response = f"🔎 Anomaly Check: {iso_note}. Isolation score: {iso.get('score'):.3f}." if iso.get('score') is not None else f"🔎 Anomaly Check: {iso_note}."
        return jsonify({"response": response, "detail": result})

    if intent == "failure":
        if rf.get("pred") == 2:
            return jsonify({"response": f"🚨 Random Forest indicates CRITICAL risk ({rf_label}). Immediate inspection recommended.", "detail": result})
        if rf.get("pred") == 1:
            return jsonify({"response": f"⚠️ Random Forest indicates WARNING ({rf_label}). Schedule inspection soon.", "detail": result})
        return jsonify({"response": "🟢 Random Forest indicates normal operation.", "detail": result})

    if intent == "forecast":
        return jsonify({"response": (f"📈 Forecast (next cycle): Temp {lstm_f.get('temperature'):.2f}°C, Vib {lstm_f.get('vibration'):.2f} mm/s, Speed {lstm_f.get('speed'):.2f} RPM"), "detail": result})

    if intent == "recommend":
        # Merge RF/ISO/LSTM suggestions into single actionable recommendation
        actions = []
        if iso.get("pred") == -1:
            actions.append("Investigate immediately for sudden anomalies (sensor check / mechanical inspection).")
        if rf.get("pred") == 2:
            actions.append("Immediate shutdown & inspection recommended (high failure risk).")
        if lstm_f.get("temperature") and lstm_f.get("temperature") > 75:
            actions.append("Cooling check: potential overheating predicted.")
        if not actions:
            actions.append("Continue standard monitoring; no immediate action required.")
        return jsonify({"response": "🛠 Recommendations:\n- " + "\n- ".join(actions), "detail": result})

    if intent == "help":
        return jsonify({"response": "I can detect anomalies, check failure risk, forecast next cycle, and provide recommendations. Provide chartData or ask about a machine."})

    # default
    overall = result.get("overall_summary") or "Machine operating within expected parameters."
    return jsonify({"response": overall, "detail": result})
