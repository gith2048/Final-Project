from flask import Blueprint, request, jsonify, send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import pandas as pd
import os

report_bp = Blueprint("report", __name__)

# Thresholds for each sensor
THRESHOLDS = {
    "temperature": 75,   # °C
    "vibration": 5.0,    # mm/s
    "speed": 1200        # RPM
}

@report_bp.route("/process", methods=["POST"])
def process_data():
    data = request.json
    df = pd.DataFrame(data)

    # Calculate averages
    avg_temp = df["temperature"].mean()
    avg_vibration = df["vibration"].mean()
    avg_speed = df["speed"].mean()

    # Check thresholds
    exceeded = []
    alerts = []

    if avg_temp > THRESHOLDS["temperature"]:
        alerts.append(f"Temperature exceeded threshold: {avg_temp:.2f} °C")
        exceeded.append("temperature")

    if avg_vibration > THRESHOLDS["vibration"]:
        alerts.append(f"Vibration exceeded threshold: {avg_vibration:.2f} mm/s")
        exceeded.append("vibration")

    if avg_speed > THRESHOLDS["speed"]:
        alerts.append(f"Speed exceeded threshold: {avg_speed:.2f} RPM")
        exceeded.append("speed")

    # Determine status and recommendation
    status = "Healthy" if not exceeded else "Alert"
    shutdown = len(exceeded) >= 2
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    summary = (
        "Machine is operating normally."
        if status == "Healthy"
        else "Warning: Sensor thresholds exceeded. Immediate action recommended."
    )

    # Generate PDF report
    pdf_path = "report.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, "Machine Status Report")
    c.setFont("Helvetica", 12)
    c.drawString(100, 770, f"Generated on: {timestamp}")
    c.drawString(100, 740, f"Average Temperature: {avg_temp:.2f} °C")
    c.drawString(100, 720, f"Average Vibration: {avg_vibration:.2f} mm/s")
    c.drawString(100, 700, f"Average Speed: {avg_speed:.2f} RPM")
    c.drawString(100, 680, f"Status: {status}")
    c.drawString(100, 660, f"Summary: {summary}")

    if alerts:
        c.drawString(100, 640, "Alerts:")
        y = 620
        for alert in alerts:
            c.drawString(120, y, f"- {alert}")
            y -= 20
        if shutdown:
            c.drawString(100, y, "⚠️ Recommendation: Turn off system for a few hours.")

    c.save()

    # Return response to frontend
    return jsonify({
        "status": status,
        "avg_temp": avg_temp,
        "avg_vibration": avg_vibration,
        "avg_speed": avg_speed,
        "alerts": alerts,
        "shutdown": shutdown,
        "health_summary": summary,
        "report_url": "/download"
    })

@report_bp.route("/download", methods=["GET"])
def download_report():
    return send_file("report.pdf", as_attachment=True)