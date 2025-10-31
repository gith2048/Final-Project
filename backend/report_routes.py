from flask import Blueprint, request, jsonify, send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import pandas as pd
import os

report_bp = Blueprint("report", __name__)

@report_bp.route("/process", methods=["POST"])
def process_data():
    data = request.json
    df = pd.DataFrame(data)

    avg_temp = df["temperature"].mean()
    avg_speed = df["speed"].mean()
    status = "Healthy" if avg_temp < 75 and avg_speed > 1000 else "Check Required"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    pdf_path = "report.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, "Machine Status Report")
    c.setFont("Helvetica", 12)
    c.drawString(100, 770, f"Generated on: {timestamp}")
    c.drawString(100, 740, f"Average Temperature: {avg_temp:.2f} °C")
    c.drawString(100, 720, f"Average Speed: {avg_speed:.2f} RPM")
    c.drawString(100, 700, f"Status: {status}")
    c.save()

    return jsonify({
        "status": status,
        "avg_temp": avg_temp,
        "avg_speed": avg_speed,
        "report_url": "/download"
    })

@report_bp.route("/download", methods=["GET"])
def download_report():
    return send_file("report.pdf", as_attachment=True)