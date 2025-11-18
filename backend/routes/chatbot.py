from flask import Blueprint, request, jsonify
import requests

chatbot_bp = Blueprint("chatbot", __name__)

# ----------------------------------------
# SIMPLE INTENT DETECTION
# ----------------------------------------
def detect_intent(message):
    msg = message.lower()
    if "anomaly" in msg or "abnormal" in msg:
        return "anomaly"
    elif "failure" in msg or "risk" in msg or "breakdown" in msg:
        return "failure"
    elif "forecast" in msg or "predict" in msg or "temperature" in msg:
        return "forecast"
    elif "help" in msg or "what can you do" in msg:
        return "help"
    return "unknown"


# ----------------------------------------
# MAIN CHAT ENDPOINT
# ----------------------------------------
@chatbot_bp.route("/chat", methods=["POST"])
def chat():
    message = request.json.get("message", "")
    intent = detect_intent(message)

    # Dummy real-time sample values
    sample_payload = {
        "temperature": 70,
        "vibration": 4.5,
        "speed": 1250,
        "sequence": [
            [65, 1200, 4.2],
            [66, 1210, 4.3],
            [67, 1225, 4.4],
            [68, 1230, 4.6],
            [69, 1240, 4.7]
        ]
    }

    # ----------------------------------------
    # ANOMALY CHECK — Isolation Forest
    # ----------------------------------------
    if intent == "anomaly":
        try:
            res = requests.post(
                "http://localhost:5000/predict",
                json=sample_payload
            )
            result = res.json()["isolation_forest"]

            if result["anomaly"] == -1:
                return jsonify({
                    "response": "⚠️ Anomaly detected! Sensor pattern deviates from expected behavior."
                })
            else:
                return jsonify({
                    "response": "✅ No anomaly detected. All sensor patterns look normal."
                })
        except:
            return jsonify({"response": "❌ Unable to process anomaly check. Backend not reachable."})

    # ----------------------------------------
    # FAILURE RISK — Random Forest
    # ----------------------------------------
    if intent == "failure":
        try:
            res = requests.post(
                "http://localhost:5000/predict",
                json=sample_payload
            )
            result = res.json()["random_forest"]["failure_risk"]

            if result == 1:
                return jsonify({
                    "response": "⚠️ High failure risk detected! Recommend immediate inspection."
                })
            else:
                return jsonify({
                    "response": "🟢 Failure risk is low. Machine is operating normally."
                })
        except:
            return jsonify({"response": "❌ Unable to calculate failure risk."})

    # ----------------------------------------
    # FORECAST — LSTM prediction
    # ----------------------------------------
    if intent == "forecast":
        try:
            res = requests.post(
                "http://localhost:5000/predict",
                json=sample_payload
            )
            forecast = res.json()["lstm"]["forecast"]

            return jsonify({
                "response": (
                    "📈 *LSTM-Based Forecast*\n"
                    f"- Temperature (next cycle): **{forecast['temperature']}°C**\n"
                    f"- Speed (next cycle): **{forecast['speed']} RPM**\n"
                    f"- Vibration (next cycle): **{forecast['vibration']} mm/s**"
                )
            })
        except:
            return jsonify({"response": "❌ Forecast engine is unavailable right now."})

    # ----------------------------------------
    # HELP INTENT
    # ----------------------------------------
    if intent == "help":
        return jsonify({
            "response": (
                "🤖 I can help you with:\n"
                "• Detecting anomalies\n"
                "• Checking machine failure risk\n"
                "• Forecasting temperature, speed & vibration\n"
                "Try asking:\n"
                "→ *Check anomaly*\n"
                "→ *What is the failure risk?*\n"
                "→ *Forecast temperature*"
            )
        })

    # ----------------------------------------
    # UNKNOWN INTENT
    # ----------------------------------------
    return jsonify({
        "response": "🤖 I'm not sure I understood. You can ask about *anomalies, failure risk, or forecast*."
    })
