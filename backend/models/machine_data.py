from db import db
from datetime import datetime

class MachineData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    vibration = db.Column(db.Float)
    current = db.Column(db.Float)
    noise = db.Column(db.Float)
    speed = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Prediction fields
    forecast_temperature = db.Column(db.Float)
    forecast_speed = db.Column(db.Float)
    forecast_vibration = db.Column(db.Float)
    failure_risk = db.Column(db.Integer)
    anomaly_score = db.Column(db.Float)
    anomaly_flag = db.Column(db.Boolean)
    summary = db.Column(db.Text)