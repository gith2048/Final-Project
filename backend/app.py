import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
from secret import SECRET_KEY
from flask import session
from flask import Flask, request, jsonify, send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import random, smtplib
from routes.predict import predict_bp
from routes.chatbot import chatbot_bp
import tensorflow as tf
import pickle
import json
from report_routes import report_bp
import numpy as np
import pandas as pd
from email.mime.text import MIMEText





app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

# ---------------------------
# Database Configuration
# ---------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/predictive_maintenance2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------------------
# Models
# 🔹 Load models



# Load Isolation Forest
with open("model/iso_model.pkl", "rb") as f:
    iso_model = pickle.load(f)

# Load Random Forest
with open("model/rf_model.pkl", "rb") as f:
    rf_model = pickle.load(f)

# Load LSTM model
lstm_model = tf.keras.models.load_model("model/lstm_model.keras")

# ✅ Load scaler trained on 5 features: temperature, speed, vibration, current, noise
with open("model/multi_scaler.pkl", "rb") as f:
    multi_scaler = pickle.load(f)
    print("Scaler expects:", multi_scaler.n_features_in_)  # Should print 3


app.register_blueprint(predict_bp, url_prefix="/")
app.register_blueprint(chatbot_bp) 
app.register_blueprint(report_bp)
# ---------------------------
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'engineer', 'viewer'), default='viewer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    otp = db.Column(db.String(6))
    otp_expires = db.Column(db.DateTime)

class Machine(db.Model):
    __tablename__ = 'machines'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    status = db.Column(db.Enum('active', 'inactive', 'maintenance'), default='active')
    last_maintenance_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SensorData(db.Model):
    __tablename__ = 'sensor_data'
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machines.id', ondelete='CASCADE'), nullable=False)
    temperature = db.Column(db.Float)
    vibration = db.Column(db.Float)
    current = db.Column(db.Float)
    noise = db.Column(db.Float)
    speed = db.Column(db.Float)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

class MaintenanceLog(db.Model):
    __tablename__ = 'maintenance_logs'
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey('machines.id', ondelete='CASCADE'), nullable=False)
    performed_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    issue_detected = db.Column(db.String(255))
    action_taken = db.Column(db.String(255))
    maintenance_date = db.Column(db.DateTime, default=datetime.utcnow)

class WorkloadDistribution(db.Model):
    __tablename__ = 'workload_distribution'
    id = db.Column(db.Integer, primary_key=True)
    source_machine_id = db.Column(db.Integer, db.ForeignKey('machines.id', ondelete='CASCADE'), nullable=False)
    target_machine_id = db.Column(db.Integer, db.ForeignKey('machines.id', ondelete='CASCADE'), nullable=False)
    transferred_load = db.Column(db.Float)
    transfer_date = db.Column(db.DateTime, default=datetime.utcnow)

# ---------------------------
# Routes
# ---------------------------
@app.route('/')
def home():
    return jsonify({"message": "Predictive Maintenance API Running 🚀"})

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not all(k in data for k in ('name','email','password')):
        return jsonify({"message": "Name, email, and password required"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already registered"}), 400

    hashed_pw = generate_password_hash(data['password'])
    user = User(name=data['name'], email=data['email'], password=hashed_pw)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Signup successful!", "user": {"name": user.name, "email": user.email}})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()

    if not user or not check_password_hash(user.password, data.get('password')):
        return jsonify({"message": "Invalid email or password"}), 401

    # Generate OTP
    otp = str(random.randint(100000, 999999))
    expiry = datetime.utcnow() + timedelta(minutes=10)
    user.otp = otp
    user.otp_expires = expiry
    db.session.commit()

    # Send OTP to user's email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('s9342902@gmail.com', 'ncjn fjwj kcwf ocda')  # 🔐 Use env vars in production
        message = f"Your login OTP is {otp}. It expires in 10 minutes."
        server.sendmail('s9342902@gmail.com', user.email, message)
        server.quit()
    except Exception as e:
        return jsonify({'message': 'Failed to send OTP', 'error': str(e)}), 500

    return jsonify({"message": "OTP sent to email", "email": user.email})

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    otp = str(random.randint(100000, 999999))
    expiry = datetime.utcnow() + timedelta(minutes=10)

    user.otp = otp
    user.otp_expires = expiry
    db.session.commit()

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('s9342902@gmail.com', 'ncjn fjwj kcwf ocda')
        message = f"Your OTP for password reset is {otp}. It expires in 10 minutes."
        server.sendmail('s9342902@gmail.com', email, message)
        server.quit()
    except Exception as e:
        return jsonify({'message': 'Failed to send email', 'error': str(e)}), 500

    return jsonify({'message': 'OTP sent to email'})

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if user.otp != otp or datetime.utcnow() > user.otp_expires:
        return jsonify({'message': 'Invalid or expired OTP'}), 400

    # ✅ Store email in session after successful OTP verification
    session["user_email"] = user.email

    return jsonify({'message': 'OTP verified'})


@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    new_password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    hashed_pw = generate_password_hash(new_password)
    user.password = hashed_pw
    user.otp = None
    user.otp_expires = None
    db.session.commit()

    return jsonify({'message': 'Password reset successful'})

@app.route('/api/verify-login-otp', methods=['POST'])
def verify_login_otp():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if user.otp != otp or datetime.utcnow() > user.otp_expires:
        return jsonify({'message': 'Invalid or expired OTP'}), 400

    user.otp = None
    user.otp_expires = None
    db.session.commit()

    return jsonify({'message': 'Login successful', 'user': {'name': user.name, 'email': user.email}})

@app.route('/api/update-profile', methods=['POST'])
def update_profile():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user.name = name
    db.session.commit()

    return jsonify({'message': 'Profile updated successfully', 'user': {'name': user.name, 'email': user.email}})

@app.route('/api/dashboard-data', methods=['GET'])
def dashboard_data():
    labels = [f"Day {i}" for i in range(1, 11)]
    line = [random.randint(70, 100) for _ in range(10)]
    bar = [random.randint(0, 10) for _ in range(10)]
    categories = {
        "labels": ["Machine A", "Machine B", "Machine C", "Machine D", "Machine E"],
        "values": [random.randint(1, 10) for _ in range(5)]
    }
    contact_requests = [
        {
            "id": i,
            "name": f"User {i}",
            "email": f"user{i}@example.com",
            "company": f"Company {i}",
            "meeting_date": "2025-10-15",
            "message": "This is a sample request",
            "created_at": "2025-10-12"
        } for i in range(1, 4)
    ]
    return jsonify({"labels": labels, "line": line, "bar": bar, "categories": categories, "contact_requests": contact_requests})

@app.route('/machines', methods=['GET'])
def get_machines():
    machines = Machine.query.all()
    return jsonify([
        {"id": m.id, "name": m.name, "location": m.location, "status": m.status}
        for m in machines
    ])

@app.route("/chat/analyze", methods=["POST"])
def analyze_chart():
    data = request.get_json(force=True)
    chart_type = data.get("chartType")
    chart_data = data.get("data")

    if not chart_type or not chart_data:
        return jsonify({
            "issue": "⚠️ Missing chart data",
            "cause": "No chart type or sensor values provided",
            "solution": "Drop a valid chart again."
        })

    # ---------------------------
    # Extract last 5 samples
    # ---------------------------
    sequence = []
    for i in range(-5, 0):
        sequence.append([
            chart_data["temperature"][i],
            chart_data["speed"][i],
            chart_data["vibration"][i],
            chart_data["current"][i],
            chart_data["noise"][i]
        ])

    # Latest point
    latest = sequence[-1]

    # ---------------------------
    # 1️⃣ LSTM FORECAST (Next point)
    # ---------------------------
    scaled_seq = multi_scaler.transform(sequence)
    input_seq = np.array(scaled_seq).reshape(1, 5, 5)
    lstm_raw = lstm_model.predict(input_seq)[0]
    forecast = multi_scaler.inverse_transform([lstm_raw])[0]

    f_temp, f_speed, f_vib, f_curr, f_noise = forecast

    # ---------------------------
    # 2️⃣ RANDOM FOREST FAILURE RISK
    # ---------------------------
    rf_pred = rf_model.predict([latest])[0]  # 1 = risky

    # ---------------------------
    # 3️⃣ ISOLATION FOREST ANOMALY
    # ---------------------------
    iso_pred = iso_model.predict([latest])[0]  # -1 = anomaly

    # ---------------------------
    # 4️⃣ TREND CHECK
    # ---------------------------
    def trend(vals):
        if vals[-1] > vals[-2] > vals[-3]:
            return "rising"
        elif vals[-1] < vals[-2] < vals[-3]:
            return "falling"
        return "stable"

    trends = {
        "temperature": trend(chart_data["temperature"]),
        "speed": trend(chart_data["speed"]),
        "vibration": trend(chart_data["vibration"]),
        "current": trend(chart_data["current"]),
        "noise": trend(chart_data["noise"]),
    }

    # ---------------------------
    # 5️⃣ THRESHOLD LEVEL CHECK
    # ---------------------------
    def level(val, low, high, critical):
        if val >= critical: return "critical"
        if val > high: return "high"
        if val > low: return "medium"
        return "low"

    levels = {
        "temperature": level(latest[0], 65, 75, 85),
        "speed": level(latest[1], 1150, 1250, 1350),
        "vibration": level(latest[2], 3, 5, 7),
        "current": level(latest[3], 3.5, 4.5, 5.0),
        "noise": level(latest[4], 70, 80, 90),
    }

    # ---------------------------
    # 6️⃣ FINAL AI DECISION ENGINE
    # (Combines LSTM + RF + IsoForest + Threshold + Trends)
    # ---------------------------
    if iso_pred == -1:
        issue = "🚨 Anomaly Detected"
        cause = "Sensor pattern is unusual. Possible hardware fault."
        solution = "Inspect sensors, check alignment & verify connections."

    elif rf_pred == 1:
        issue = "⚠️ High Failure Risk"
        cause = "ML model predicts breakdown risk from current data."
        solution = "Reduce load & perform immediate maintenance."

    elif "critical" in levels.values():
        issue = "🚨 Critical Sensor Level"
        cause = "One or more sensors exceeded industrial critical limits."
        solution = "SHUTDOWN recommended within minutes."

    elif "high" in levels.values():
        issue = "⚠️ High Operating Stress"
        cause = "Sensors reading above safe high limits."
        solution = "Inspect machine immediately."

    elif "rising" in trends.values():
        issue = "📈 Rising Trend Detected"
        cause = "Values steadily increasing over last readings."
        solution = "Monitor closely. Maintenance may be needed soon."

    elif f_temp > 75 or f_vib > 5.5:
        issue = "📉 Unsafe Forecast Ahead"
        cause = "LSTM prediction indicates possible future overheating/vibration."
        solution = "Prepare preventive maintenance."

    else:
        issue = "✅ Machine Operating Normally"
        cause = "All sensors stable & forecast looks healthy."
        solution = "No action needed."

    # ---------------------------
    # Response
    # ---------------------------
    return jsonify({
        "chart_type": chart_type,
        "issue": issue,
        "cause": cause,
        "solution": solution,
        "forecast": {
            "temperature": float(f_temp),
            "speed": float(f_speed),
            "vibration": float(f_vib),
            "current": float(f_curr),
            "noise": float(f_noise)
        },
        "levels": levels,
        "trends": trends,
        "rf_prediction": int(rf_pred),
        "anomaly_detection": int(iso_pred)
    })


@app.route('/api/machine-summary', methods=['GET'])
def machine_summary():
    machines = Machine.query.all()
    return jsonify({
        "count": len(machines),
        "machines": [
            {
                "id": m.id,
                "name": m.name,
                "location": m.location,
                "status": m.status,
                "last_maintenance_date": m.last_maintenance_date.strftime("%Y-%m-%d") if m.last_maintenance_date else None
            }
            for m in machines
        ]
    })

@app.route('/add_sensor', methods=['POST'])
def add_sensor():
    data = request.get_json()
    try:
        new_entry = SensorData(
            machine_id=data['machine_id'],
            temperature=data['temperature'],
            vibration=data['vibration'],
            current=data['current'],
            noise=data['noise'],
            speed=data['speed']
        )
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"message": "Sensor data added successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/maintenance_logs', methods=['GET'])
def get_logs():
    logs = MaintenanceLog.query.all()
    return jsonify([
        {"machine_id": l.machine_id, "issue": l.issue_detected, "action": l.action_taken}
        for l in logs
    ])

@app.route("/api/sensor-data", methods=["GET"])
def get_sensor_data_json():
    try:
        with open("sensor_data.json", "r") as f:
            raw = json.load(f)

        # Convert list of objects into arrays
        timestamps = [row.get("timestamp") for row in raw]
        temperature = [row.get("temperature") for row in raw]
        vibration = [row.get("vibration") for row in raw]
        speed = [row.get("speed") for row in raw]
        current = [row.get("current") for row in raw]
        noise = [row.get("noise") for row in raw]

        return jsonify({
            "timestamps": timestamps,
            "temperature": temperature,
            "vibration": vibration,
            "speed": speed,
            "current": current,
            "noise": noise
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500




# ---------------------------
# Run App
# ---------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
    # app.run(debug=True)