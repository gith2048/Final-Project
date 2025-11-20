# app.py
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

# ---------------------------
# App & DB
# ---------------------------
app = Flask(__name__)
app.secret_key = SECRET_KEY
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/predictive_maintenance2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------------------
# Models & ML assets (3 features: temperature, speed, vibration)
# ---------------------------
MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")

def safe_load_pickle(path):
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        print(f"❌ Failed to load {path}: {e}")
        return None

iso_model = safe_load_pickle(os.path.join(MODEL_DIR, "iso_model.pkl"))
rf_model = safe_load_pickle(os.path.join(MODEL_DIR, "rf_model.pkl"))
# load the LSTM scaler (saved during training as lstm_scaler.pkl / lstm_scaler)
lstm_scaler = safe_load_pickle(os.path.join(MODEL_DIR, "lstm_scaler.pkl"))

# load LSTM if present
lstm_model = None
lstm_path = os.path.join(MODEL_DIR, "lstm_model.keras")
if os.path.exists(lstm_path):
    try:
        lstm_model = tf.keras.models.load_model(lstm_path)
        print("✅ LSTM model loaded:", lstm_path)
    except Exception as e:
        print(f"❌ Failed loading LSTM model: {e}")
else:
    print("⚠️ No LSTM model file found at", lstm_path)

# Print scaler expectations (best-effort)
try:
    print("LSTM Scaler expects (n_features_in_):", getattr(lstm_scaler, "n_features_in_", "unknown"))
except Exception:
    print("Scaler loaded but couldn't read n_features_in_ or scaler missing")

# Register blueprints (keep original behavior)
app.register_blueprint(predict_bp, url_prefix="/")
app.register_blueprint(chatbot_bp)
app.register_blueprint(report_bp)

# ---------------------------
# DB Models (unchanged)
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
# Utilities: read sensor JSON -> grouped per-machine arrays (3 params)
# ---------------------------
DATA_FILE_CANDIDATES = [
    os.path.join(os.path.dirname(__file__), "sensor_data_3params.json"),
    os.path.join(os.path.dirname(__file__), "sensor_data.json"),
    os.path.join(os.path.dirname(__file__), "backend", "sensor_data.json"),
]

def find_sensor_file():
    for p in DATA_FILE_CANDIDATES:
        if os.path.exists(p):
            return p
    return None

def load_raw_sensor_rows(path):
    with open(path, "r") as f:
        raw = json.load(f)
    if not isinstance(raw, list):
        raise ValueError("sensor data JSON must be a list of objects")
    return raw

def make_machine_map_from_rows(rows):
    """
    Build a dict:
      { "Machine_A": { timestamps: [...], temperature: [...], vibration: [...], speed: [...] }, ... }
    Ensures values are numeric (floats) and timestamps are strings.
    """
    mm = {}
    for row in rows:
        mid = row.get("machine_id") or row.get("machine") or "Unknown"
        if mid not in mm:
            mm[mid] = {"timestamps": [], "temperature": [], "vibration": [], "speed": []}

        # timestamp string
        ts = row.get("timestamp")
        if isinstance(ts, (int, float)):
            ts = str(int(ts))
        elif isinstance(ts, dict):
            ts = str(ts)
        elif ts is None:
            ts = datetime.utcnow().isoformat()

        # cast numeric, handle missing/invalid gracefully
        def to_float(x):
            try:
                if x is None: return float("nan")
                return float(x)
            except Exception:
                try:
                    return float(x.get("value"))
                except Exception:
                    return float("nan")

        temp = to_float(row.get("temperature"))
        vib = to_float(row.get("vibration"))
        spd = to_float(row.get("speed"))

        mm[mid]["timestamps"].append(str(ts))
        mm[mid]["temperature"].append(temp)
        mm[mid]["vibration"].append(vib)
        mm[mid]["speed"].append(spd)

    # replace NaN with 0 or interpolated values (simple fallback: forward-fill then back-fill then zeros)
    for mid, d in mm.items():
        for k in ("temperature", "vibration", "speed"):
            arr = d[k]
            na = np.array(arr, dtype=float)
            if np.isnan(na).any():
                # forward fill
                for i in range(len(na)):
                    if np.isnan(na[i]) and i > 0:
                        na[i] = na[i-1]
                # backfill
                for i in range(len(na)-1, -1, -1):
                    if np.isnan(na[i]) and i < len(na)-1:
                        na[i] = na[i+1]
                # remaining NaNs -> zeros
                na = np.nan_to_num(na, nan=0.0)
            d[k] = [float(x) for x in na.tolist()]

    return mm

def downsample_arrays(ts, arrays_dict, max_points=1000):
    """
    Downsamples arrays keeping shape:
      Input: ts: list timestamps, arrays_dict: {"temperature": [...], ...}
      Output: {"timestamps": [...], "temperature": [...], ...}
    If n <= max_points returns raw arrays.
    Downsampling uses simple bucketing average.
    """
    n = len(ts)
    if n <= max_points:
        return {"timestamps": ts, **arrays_dict}

    bucket = max(1, n // max_points)
    out_ts = []
    out = {k: [] for k in arrays_dict}
    for i in range(0, n, bucket):
        out_ts.append(ts[i])
        for k in arrays_dict:
            chunk = arrays_dict[k][i:i+bucket]
            clean = [float(x) for x in chunk if not (isinstance(x, float) and np.isnan(x))]
            out[k].append(float(sum(clean) / len(clean)) if clean else 0.0)
    return {"timestamps": out_ts, **out}


# ---------------------------
# Routes (mostly unchanged, plus robust /api/sensor-data and /chat/analyze)
# ---------------------------

@app.route('/')
def home():
    return jsonify({"message": "Predictive Maintenance API Running 🚀"})

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data or not all(k in data for k in ('name','email','password')):
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
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get('email')).first()
    if not user or not check_password_hash(user.password, data.get('password')):
        return jsonify({"message": "Invalid email or password"}), 401
    otp = str(random.randint(100000, 999999))
    expiry = datetime.utcnow() + timedelta(minutes=10)
    user.otp = otp
    user.otp_expires = expiry
    db.session.commit()
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('s9342902@gmail.com', 'ncjn fjwj kcwf ocda')  # use env in prod
        message = f"Your login OTP is {otp}. It expires in 10 minutes."
        server.sendmail('s9342902@gmail.com', user.email, message)
        server.quit()
    except Exception as e:
        return jsonify({'message': 'Failed to send OTP', 'error': str(e)}), 500
    return jsonify({"message": "OTP sent to email", "email": user.email})

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json() or {}
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
    data = request.get_json() or {}
    email = data.get('email')
    otp = data.get('otp')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    if user.otp != otp or datetime.utcnow() > user.otp_expires:
        return jsonify({'message': 'Invalid or expired OTP'}), 400
    session["user_email"] = user.email
    return jsonify({'message': 'OTP verified'})

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json() or {}
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
    data = request.get_json() or {}
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
    data = request.get_json() or {}
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
    # simple sample dashboard data (kept as you had before)
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
    return jsonify([{"id": m.id, "name": m.name, "location": m.location, "status": m.status} for m in machines])


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



# ---------------------------
# main analyze endpoint (updated to use 3 params)
# ---------------------------
# Replace existing analyze_chart with this implementation
@app.route("/chat/analyze", methods=["POST"])
def analyze_chart():
    import numpy as np
    payload = request.get_json(force=True) or {}

    chart_type = payload.get("chartType")
    data = payload.get("data", {})

    # ---------------------------
    # SAFE EXTRACTION
    # ---------------------------
    def safe(v):
        out = []
        for x in v or []:
            try:
                out.append(float(x))
            except:
                out.append(np.nan)
        return out

    temp = safe(data.get("temperature"))
    speed = safe(data.get("speed"))
    vib = safe(data.get("vibration"))

    # Validate
    if len(temp) < 3 or len(speed) < 3 or len(vib) < 3:
        return jsonify({
            "issue": "Not enough data",
            "cause": "Need minimum 3 points",
            "solution": "Collect more readings",
            "forecast": None,
            "summary": "No meaningful analysis possible due to insufficient data."
        })

    # clean NaN
    def clean(a):
        a = np.array(a, float)
        for i in range(1, len(a)):
            if np.isnan(a[i]): a[i] = a[i-1]
        for i in range(len(a)-2, -1, -1):
            if np.isnan(a[i]): a[i] = a[i+1]
        return a.tolist()

    temp = clean(temp)
    speed = clean(speed)
    vib = clean(vib)

    # Ensure no negative values before analysis
    temp = [max(0, v) for v in temp]
    speed = [max(0, v) for v in speed]
    vib = [max(0, v) for v in vib]

    # ✅ Analyze the most significant recent value (max), not just the last one.
    # This ensures the analysis matches the chart visuals (e.g., a recent red spike).
    latest_temp = max(temp[-10:]) if temp else 0
    latest_speed = max(speed[-10:]) if speed else 0
    latest_vib = max(vib[-10:]) if vib else 0
    latest_for_models = [latest_temp, latest_speed, latest_vib]

    # ---------------------------
    # FORECAST
    # ---------------------------
    try:
        # The LSTM model was trained with a sequence length of 10.
        seq = np.array([[temp[-10+i], speed[-10+i], vib[-10+i]] for i in range(10)])
        scaled = lstm_scaler.transform(seq) # Use original sequence for trend
        pred = lstm_model.predict(scaled.reshape(1, 10, 3), verbose=0)[0]
        inv = lstm_scaler.inverse_transform([pred])[0]
        # ✅ Ensure no negative forecast values
        f_temp = max(0, float(inv[0]))
        f_speed = max(0, float(inv[1]))
        f_vib = max(0, float(inv[2]))
    except:
        f_temp, f_speed, f_vib = latest_for_models

    # ---------------------------
    # RANDOM FOREST
    # ---------------------------
    try:
        rf_pred = int(rf_model.predict([latest_for_models])[0])
        if rf_pred == 1:
            rf_issue = "Abnormal (Alert)"
            rf_cause = "The machine's operating signature matches known failure patterns."
            rf_solution = "An immediate inspection is recommended to prevent potential failure."
        else:
            rf_issue = "Normal"
            rf_cause = "The machine's operational signature appears healthy and stable."
            rf_solution = "Continue with standard monitoring procedures."
    except:
        rf_pred = None
        rf_issue = "RF Model Error"
        rf_cause = "Shape mismatch"
        rf_solution = "Retrain RF model."

    # ---------------------------
    # ISOLATION FOREST
    # ---------------------------
    try:
        iso_pred = int(iso_model.predict([latest_for_models])[0])
        iso_score = float(iso_model.decision_function([latest_for_models])[0])
        if iso_pred == -1:
            # ✅ Categorize anomaly severity based on score
            if iso_score < -0.1:
                iso_issue = "Critical Sudden Change"
            elif iso_score < -0.05:
                iso_issue = "High Sudden Change"
            else:
                iso_issue = "Medium Sudden Change"
            
            iso_cause = f"A sudden, unexpected deviation was detected in sensor readings (score: {iso_score:.2f}). This often points to an abrupt event like a component jam, load shock, or sensor malfunction."
            iso_solution = "Investigate the machine immediately for the source of the sudden change. Check for any unusual noises or obstructions."
        else:
            iso_issue = "Low (No Sudden Changes)"
            iso_cause = "Sensor values are within the expected operational distribution, indicating stable performance."
            iso_solution = "The machine is operating smoothly without any sudden anomalies."
    except:
        iso_pred = None
        iso_score = None
        iso_issue = "ISO Model Error"
        iso_cause = "Shape mismatch"
        iso_solution = "Retrain ISO model."

    # ---------------------------
    # TREND
    # ---------------------------
    def trend(a):
        a, b, c = a[-3:]
        if a < b < c: return "rising"
        if a > b > c: return "falling"
        return "stable"

    t_temp = trend(temp)
    t_speed = trend(speed)
    t_vib = trend(vib)

    # ---------------------------
    # NATURAL SUMMARY (4–5 lines)
    # ---------------------------
    summary_parts = []
    issues = []
    causes = []
    solutions = []

    # Chart-specific analysis
    if chart_type == "lineChart":
        # Focus on Temperature and Vibration
        summary_parts.append(f"Analyzing Temperature and Vibration. Recent peak values are {latest_temp:.1f}°C and {latest_vib:.1f} mm/s.")
        if latest_temp > 85:
            issues.append("Critical Temperature")
            causes.append("Severe overheating detected.")
            solutions.append("Immediate shutdown is required. Inspect the cooling system.")
            summary_parts.append(f"🚨 Temperature recently reached a critical level of {latest_temp:.1f}°C.")
        elif latest_temp > 75:
            issues.append("High Temperature")
            causes.append("Potential cooling inefficiency.")
            solutions.append("Monitor closely and check cooling system.")
            summary_parts.append(f"⚠️ Temperature recently reached a high of {latest_temp:.1f}°C.")

        if latest_vib > 7:
            issues.append("Critical Vibration")
            causes.append("Severe mechanical imbalance or bearing failure.")
            solutions.append("Immediate shutdown for mechanical inspection is advised.")
            summary_parts.append(f"🚨 Critical vibration at {latest_vib:.1f} mm/s indicates a high failure risk.")
        elif latest_vib > 5:
            issues.append("High Vibration")
            causes.append("Possible misalignment or worn components.")
            solutions.append("Schedule inspection for bearings and alignment.")
            summary_parts.append(f"⚠️ Vibration is high at {latest_vib:.1f} mm/s.")

    elif chart_type == "barChart":
        # Focus on Speed
        summary_parts.append(f"Analyzing Speed. Recent peak RPM is {latest_speed:.0f}.")
        if latest_speed > 1350:
            issues.append("Critical Speed")
            causes.append("Motor is running at excessive RPM.")
            solutions.append("Reduce load or inspect motor controller immediately.")
            summary_parts.append("🚨 Machine speed is critically high.")
        elif latest_speed > 1200:
            issues.append("High Speed")
            causes.append("Operating above optimal speed.")
            solutions.append("Verify load and motor settings.")
            summary_parts.append("⚠️ Machine is running faster than recommended.")
        else:
            summary_parts.append("✅ Speed has remained within the normal operating range.")

    elif chart_type == "pieChart":
        # Focus on Load (inferred from speed)
        summary_parts.append(f"Analyzing estimated machine load based on recent peak speed of {latest_speed:.0f} RPM.")
        if latest_speed > 1200:
            issues.append("High Machine Load")
            causes.append("The machine is operating under heavy load, indicated by high speed.")
            solutions.append("Consider distributing the workload or scheduling a brief cooldown period.")
            summary_parts.append("⚠️ The machine appears to be under high load.")
        elif latest_speed > 1000:
            issues.append("Medium Machine Load")
            causes.append("The machine is operating at a moderate load.")
            solutions.append("Continue monitoring. No immediate action needed.")
            summary_parts.append("✅ Machine load is moderate and appears stable.")
        else:
            issues.append("Low Machine Load")
            causes.append("The machine is currently under a light load.")
            solutions.append("This is a good time for routine checks if needed.")
            summary_parts.append("✅ Machine is operating under a light load.")
    else:
        # Fallback to a general summary if chart type is unknown
        summary_parts.append("Performing a general health check.")
        if not issues:
             summary_parts.append("All systems appear normal.")

    if not issues:
        summary = "✅ Machine is running normally. All sensor values are within their expected ranges. No action is required."
        issue = "Normal Operation"
        cause = "Values inside safe limits."
        solution = "No action required."
    else:
        summary = " ".join(summary_parts) + " Please review the suggested actions."
        issue = ", ".join(issues) if issues else "Normal Operation"
        cause = ", ".join(causes) if causes else "Values are within safe limits."
        solution = ", ".join(solutions) if solutions else "No action required."

    # Restructure the response to be nested as the frontend expects
    return jsonify({
        "overall_summary": summary,
        "lstm": {
            "issue": "LSTM Forecast",
            "cause": "Forecasting future sensor values based on recent trends.",
            "solution": "Use these values to anticipate future states.",
            "forecast": {
                "temperature": f_temp,
                "speed": f_speed,
                "vibration": f_vib
            }
        },
        "random_forest": {
            "issue": rf_issue,
            "cause": rf_cause,
            "solution": rf_solution
        },
        "isolation_forest": {
            "issue": iso_issue,
            "cause": iso_cause,
            "solution": iso_solution,
            "score": iso_score
        },
        "trends": {
            "temperature": t_temp,
            "speed": t_speed,
            "vibration": t_vib
        }
    })



# ---------------------------
# Endpoint to return grouped sensor-data per-machine (frontend-friendly)
# ---------------------------
@app.route("/api/sensor-data", methods=["GET"])
def api_sensor_data():
    sensor_file = find_sensor_file()
    if not sensor_file:
        return jsonify({"error": "No sensor_data file found (looked for sensor_data_3params.json and sensor_data.json)"}), 404
    try:
        raw_rows = load_raw_sensor_rows(sensor_file)
        machine_map = make_machine_map_from_rows(raw_rows)

        # Downsample each machine to at most 1000 points (avoids huge payloads)
        final_output = {}
        for mid, d in machine_map.items():
            final_output[mid] = downsample_arrays(d["timestamps"], {
                "temperature": d["temperature"],
                "vibration": d["vibration"],
                "speed": d["speed"]
            }, max_points=1000)

        return jsonify(final_output)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------
# Sensor data ingestion
# ---------------------------
@app.route('/add_sensor', methods=['POST'])
def add_sensor():
    data = request.get_json()
    try:
        new_entry = SensorData(
            machine_id=data['machine_id'],
            temperature=data['temperature'],
            vibration=data['vibration'],
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
    return jsonify([{"machine_id": l.machine_id, "issue": l.issue_detected, "action": l.action_taken} for l in logs])

# ------- report / process / download endpoints left unchanged from your original app (if present) -------
@app.route("/process", methods=["POST"])
def process_data():
    """
    Keep your original processing behavior but adapted to 3 params.
    This endpoint replicates previous behavior but uses temp/speed/vibration only.
    """
    data = request.json or {}
    temp = data.get("temperature", [])
    speed = data.get("speed", [])
    vibration = data.get("vibration", [])

    min_len = min(len(temp), len(speed), len(vibration)) if (temp and speed and vibration) else 0
    if min_len == 0:
        return jsonify({"error": "No valid sensor arrays provided."}), 400

    df = pd.DataFrame({
        "temperature": [float(x) for x in temp[:min_len]],
        "speed": [float(x) for x in speed[:min_len]],
        "vibration": [float(x) for x in vibration[:min_len]]
    })

    avg_temp = df["temperature"].mean()
    avg_speed = df["speed"].mean()
    avg_vibration = df["vibration"].mean()
    status = "Healthy" if (avg_temp < 75 and avg_speed <= 1200 and avg_vibration <= 5.0) else "Check Required"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    alerts = []
    if avg_temp > 75:
        alerts.append(f"High temperature: {avg_temp:.2f} °C")
    if avg_vibration > 5.0:
        alerts.append(f"High vibration: {avg_vibration:.2f} mm/s")
    if avg_speed > 1200:
        alerts.append(f"High speed: {avg_speed:.2f} RPM")

    recommendation = "✅ Machine is operating within safe parameters."
    if avg_temp > 75 and avg_speed > 1200:
        recommendation = "⚠️ High temperature and high speed detected. Inspect cooling system and motor load."
    elif avg_temp > 75:
        recommendation = "⚠️ Temperature exceeds safe threshold. Check for overheating or poor lubrication."
    elif avg_speed > 1200:
        recommendation = "⚠️ Speed exceeds optimal range. Verify motor calibration and load conditions."
    elif avg_vibration > 5.0:
        recommendation = "⚠️ Vibration exceeds safe limits. Inspect bearings and alignment."

    # keep PDF generation minimal for 3 params
    pdf_path = "report.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, "Machine Status Report")
    c.setFont("Helvetica", 12)
    c.drawString(100, 770, f"Generated on: {timestamp}")
    c.drawString(100, 750, f"Average Temperature: {avg_temp:.2f} °C")
    c.drawString(100, 730, f"Average Vibration: {avg_vibration:.2f} mm/s")
    c.drawString(100, 710, f"Average Speed: {avg_speed:.2f} RPM")
    c.drawString(100, 690, f"Status: {status}")
    c.drawString(100, 670, f"Recommendation: {recommendation}")
    if alerts:
        c.drawString(100, 640, "Alerts:")
        for i, a in enumerate(alerts):
            c.drawString(120, 620 - i*20, f"- {a}")
    c.showPage()
    c.save()

    return jsonify({
        "status": status,
        "avg_temp": float(avg_temp),
        "avg_vibration": float(avg_vibration),
        "avg_speed": float(avg_speed),
        "recommendation": recommendation,
        "alerts": alerts,
        "report_url": "/download"
    })

@app.route("/download", methods=["GET"])
def download_report():
    if not os.path.exists("report.pdf"):
        return jsonify({"error": "Report not generated"}), 404
    return send_file("report.pdf", as_attachment=True, download_name="Machine_Report.pdf", mimetype="application/pdf")


# ---------------------------
# Run
# ---------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
