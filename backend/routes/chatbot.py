from flask import Blueprint, request, jsonify
import requests

chatbot_bp = Blueprint("chatbot", __name__)

# Simple intent detection (can be replaced with NLP later)
def detect_intent(message):
    message = message.lower()
    if "anomaly" in message:
        return "anomaly"
    elif "failure" in message or "risk" in message:
        return "failure"
    elif "forecast" in message or "temperature" in message:
        return "forecast"
    else:
        return "unknown"

@chatbot_bp.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]
    intent = detect_intent(user_input)

    if intent == "anomaly":
        payload = {
            "temperature": 70,
            "vibration": 4.5,
            "speed": 1250
        }
        res = requests.post("http://localhost:5000/predict/anomaly", json=payload)
        result = res.json()
        if result.get("anomaly") == -1:
            return jsonify({"response": "⚠️ Anomaly detected in sensor readings."})
        else:
            return jsonify({"response": "✅ Sensor readings look normal."})

    elif intent == "failure":
        payload = {
            "temperature": 70,
            "vibration": 4.5,
            "speed": 1250
        }
        res = requests.post("http://localhost:5000/predict/failure", json=payload)
        result = res.json()
        if result.get("failure_risk") == 1:
            return jsonify({"response": "⚠️ High risk of machine failure."})
        else:
            return jsonify({"response": "✅ Machine is operating normally."})

    elif intent == "forecast":
        sequence = [65, 66, 67, 68, 69, 70, 71, 72, 73, 74]  # last 10 temperature values
        res = requests.post("http://localhost:5000/predict/forecast", json={"sequence": sequence})
        result = res.json()
        return jsonify({"response": f"📈 Forecasted temperature: {result['forecast_temperature']}°C"})

    else:
        return jsonify({"response": "🤖 I can help with anomalies, failure risk, and forecasts. Try asking about one!"})