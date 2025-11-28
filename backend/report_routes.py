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

# NOTE: /process and /download routes moved to app.py with better implementation
# This blueprint is kept for future report-related routes