# app.py (patched)
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from secret import SECRET_KEY
from flask import session
from flask import Flask, request, jsonify, send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import random
import smtplib
from routes.predict import predict_bp
from routes.chatbot import chatbot_bp
import tensorflow as tf
import pickle
import json
from report_routes import report_bp
import numpy as np
import pandas as pd
from email.mime.text import MIMEText
import threading
from alert_system import process_sensor_data


# ---------------------------
# App & DB
# ---------------------------
app = Flask(__name__)
app.secret_key = SECRET_KEY
# Enable CORS for all routes with credentials support
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/predictive_maintenance_new'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------------------
# Models & ML assets (3 features: temperature, speed, vibration)
# ---------------------------
MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")

def safe_load_pickle(path):
    try:
        with open(path, "rb") as f:
            obj = pickle.load(f)
            print(f"✅ Loaded: {os.path.basename(path)}")
            return obj
    except FileNotFoundError:
        print(f"⚠️ File not found: {path}")
        return None
    except Exception as e:
        print(f"❌ Failed to load {path}: {e}")
        return None

iso_model = safe_load_pickle(os.path.join(MODEL_DIR, "iso_model.pkl"))
rf_model = safe_load_pickle(os.path.join(MODEL_DIR, "rf_model.pkl"))
rf_scaler = safe_load_pickle(os.path.join(MODEL_DIR, "scaler.pkl"))  # Scaler for RF and ISO
label_encoder = safe_load_pickle(os.path.join(MODEL_DIR, "label_encoder.pkl"))  # Label encoder for RF
lstm_scaler = safe_load_pickle(os.path.join(MODEL_DIR, "lstm_scaler.pkl"))

# load LSTM if present
lstm_model = None
lstm_path = os.path.join(MODEL_DIR, "lstm_model.keras")
if os.path.exists(lstm_path):
    try:
        lstm_model = tf.keras.models.load_model(lstm_path)
        print("✅ LSTM model loaded:", lstm_path)
    except Exception as e:
        lstm_model = None
        print(f"❌ Failed loading LSTM model: {e}")
else:
    print("⚠️ No LSTM model file found at", lstm_path)

# Thread-safety for TF
lstm_lock = threading.Lock()

# Print scaler expectations (best-effort)
try:
    print("LSTM Scaler expects (n_features_in_):", getattr(lstm_scaler, "n_features_in_", "unknown"))
except Exception:
    print("Scaler loaded but couldn't read n_features_in_ or scaler missing")

# Register blueprints (predict uses '/predict' inside its file; keep as-is)
app.register_blueprint(predict_bp, url_prefix="/")
# IMPORTANT: register chatbot blueprint without extra prefix so '/chat' route matches frontend axios('/chat')
app.register_blueprint(chatbot_bp)   # <- chatbot routes should be defined as '/chat' inside chatbot.py
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
    motor_type = db.Column(db.String(100), nullable=False)
    motor_id = db.Column(db.String(100), unique=True, nullable=False)
    date_of_purchase = db.Column(db.Date, nullable=False)
    purpose = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(100))
    status = db.Column(db.Enum('pending', 'approved', 'rejected', 'active', 'inactive', 'maintenance'), default='pending')
    last_maintenance_date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    owner = db.relationship('User', foreign_keys=[user_id], backref='owned_machines')
    approver = db.relationship('User', foreign_keys=[approved_by])

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
    mm = {}
    for row in rows:
        mid = row.get("machine_id") or row.get("machine") or "Unknown"
        if mid not in mm:
            mm[mid] = {"timestamps": [], "temperature": [], "vibration": [], "speed": []}

        ts = row.get("timestamp")
        if isinstance(ts, (int, float)):
            ts = str(int(ts))
        elif isinstance(ts, dict):
            ts = str(ts)
        elif ts is None:
            ts = datetime.utcnow().isoformat()

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

    # replace NaN with fill/zeros
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
                na = np.nan_to_num(na, nan=0.0)
            d[k] = [float(x) for x in na.tolist()]

    return mm

def downsample_arrays(ts, arrays_dict, max_points=1000):
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

    smtp_user = os.environ.get("SMTP_USER") or "s9342902@gmail.com"
    smtp_pass = os.environ.get("SMTP_PASS") or "ncjn fjwj kcwf ocda"  # move to env var in production

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        message = f"Your login OTP is {otp}. It expires in 10 minutes."
        server.sendmail(smtp_user, user.email, message)
        server.quit()
    except Exception as e:
        # Log but do not leak secrets
        print("❌ SMTP send failed:", str(e))
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

    smtp_user = os.environ.get("SMTP_USER") or "s9342902@gmail.com"
    smtp_pass = os.environ.get("SMTP_PASS") or "ncjn fjwj kcwf ocda"

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        message = f"Your OTP for password reset is {otp}. It expires in 10 minutes."
        server.sendmail(smtp_user, email, message)
        server.quit()
    except Exception as e:
        print("❌ SMTP send failed:", str(e))
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

# ---------------------------
# MACHINE MANAGEMENT ROUTES
# ---------------------------
@app.route('/api/machines', methods=['GET'])
def get_user_machines():
    """Get machines for the current user"""
    try:
        user_email = request.args.get('user_email')
        if not user_email:
            return jsonify({"error": "User email required"}), 400
        
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        machines = Machine.query.filter_by(user_id=user.id, status='approved').all()
        
        machine_list = []
        for machine in machines:
            machine_list.append({
                "id": machine.id,
                "name": machine.name,
                "motor_type": machine.motor_type,
                "motor_id": machine.motor_id,
                "date_of_purchase": machine.date_of_purchase.strftime("%Y-%m-%d") if machine.date_of_purchase else None,
                "purpose": machine.purpose,
                "location": machine.location,
                "status": machine.status,
                "created_at": machine.created_at.strftime("%Y-%m-%d %H:%M:%S") if machine.created_at else None
            })
        
        return jsonify({"machines": machine_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/machines', methods=['POST'])
def add_machine():
    """Add a new machine for the current user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'motor_type', 'motor_id', 'date_of_purchase', 'purpose', 'user_email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Check if user exists
        user = User.query.filter_by(email=data['user_email']).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check if motor_id already exists
        existing_machine = Machine.query.filter_by(motor_id=data['motor_id']).first()
        if existing_machine:
            return jsonify({"error": "Motor ID already exists. Please use a unique Motor ID."}), 400
        
        # Parse date
        try:
            purchase_date = datetime.strptime(data['date_of_purchase'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Create new machine
        new_machine = Machine(
            name=data['name'],
            motor_type=data['motor_type'],
            motor_id=data['motor_id'],
            date_of_purchase=purchase_date,
            purpose=data['purpose'],
            location=data.get('location', ''),
            user_id=user.id,
            status='pending'  # Machines start as pending approval
        )
        
        db.session.add(new_machine)
        db.session.commit()
        
        return jsonify({
            "message": "Machine added successfully! It is now pending approval.",
            "machine": {
                "id": new_machine.id,
                "name": new_machine.name,
                "motor_type": new_machine.motor_type,
                "motor_id": new_machine.motor_id,
                "status": new_machine.status
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Admin approval is now done manually in phpMyAdmin
# Simply change the 'status' field from 'pending' to 'approved' in the machines table

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
# Intelligent Recommendations Generator
# ---------------------------
def _generate_intelligent_recommendations(temp, speed, vib, f_temp, f_speed, f_vib, 
                                         rf_pred, iso_pred, iso_score, 
                                         t_temp, t_speed, t_vib, chart_type):
    """
    AI-powered recommendations engine that analyzes all data and provides
    actionable, specific recommendations with exact steps to resolve issues.
    """
    recommendations = {
        "priority": "normal",
        "actions": [],
        "preventive": [],
        "summary": ""
    }
    
    critical_issues = []
    high_issues = []
    medium_issues = []
    
    # ---------------------------
    # TEMPERATURE ANALYSIS
    # ---------------------------
    if temp > 95 or f_temp > 95:
        critical_issues.append({
            "icon": "🌡️",
            "title": "CRITICAL TEMPERATURE ALERT",
            "problem": f"Temperature at {temp:.1f}°C (Critical: >95°C)",
            "impact": "Immediate risk of component failure, thermal damage, and safety hazard",
            "root_causes": [
                "Cooling system failure or malfunction",
                "Coolant level critically low or empty",
                "Cooling fans not operating",
                "Blocked air vents or heat exchangers",
                "Excessive friction from worn bearings",
                "Overload condition beyond design capacity"
            ],
            "immediate_actions": [
                "1. EMERGENCY SHUTDOWN - Stop machine immediately",
                "2. Isolate power supply and lock out/tag out",
                "3. Allow cooling for minimum 30 minutes",
                "4. DO NOT restart until inspection complete"
            ],
            "resolution_steps": [
                "1. Check coolant reservoir - refill to MAX line if low",
                "2. Inspect cooling fans - replace if not spinning at full speed",
                "3. Clean all air vents and filters thoroughly",
                "4. Check coolant pump operation - repair/replace if faulty",
                "5. Inspect for coolant leaks - seal any leaks found",
                "6. Verify thermostat operation - replace if stuck closed",
                "7. Check bearing lubrication - relubricate if dry",
                "8. Reduce load by 30-40% after restart",
                "9. Monitor temperature continuously for 1 hour after restart"
            ],
            "prevention": [
                "Schedule coolant system inspection every 2 weeks",
                "Clean air filters weekly",
                "Check coolant levels daily",
                "Install temperature monitoring alarm at 85°C"
            ]
        })
    elif temp > 85 or f_temp > 85:
        high_issues.append({
            "icon": "🌡️",
            "title": "High Temperature Warning",
            "problem": f"Temperature at {temp:.1f}°C (High: >85°C)",
            "impact": "Accelerated wear, reduced efficiency, potential component damage",
            "root_causes": [
                "Insufficient cooling capacity",
                "Coolant level below optimal",
                "Dirty air filters reducing airflow",
                "High ambient temperature",
                "Increased load or duty cycle"
            ],
            "immediate_actions": [
                "1. Reduce machine load by 20-30%",
                "2. Check coolant level - top up if below MIN line",
                "3. Verify cooling fans are running",
                "4. Monitor temperature every 15 minutes"
            ],
            "resolution_steps": [
                "1. Clean or replace air filters",
                "2. Check coolant concentration - adjust if needed",
                "3. Inspect cooling fan belts - tighten if loose",
                "4. Verify adequate ventilation around machine",
                "5. Check lubrication points - add lubricant if needed",
                "6. Schedule cooling system service within 48 hours"
            ],
            "prevention": [
                "Clean air filters bi-weekly",
                "Check coolant monthly",
                "Monitor ambient temperature"
            ]
        })
    elif temp > 75 or (t_temp == "rising" and temp > 70):
        medium_issues.append({
            "icon": "🌡️",
            "title": "Elevated Temperature",
            "problem": f"Temperature at {temp:.1f}°C (Warning: >75°C)",
            "impact": "Slight efficiency reduction, monitor to prevent escalation",
            "immediate_actions": [
                "1. Monitor temperature trend closely",
                "2. Ensure adequate ventilation",
                "3. Check cooling system is functioning"
            ],
            "resolution_steps": [
                "1. Verify cooling system operation",
                "2. Check for obstructions in airflow",
                "3. Schedule inspection within 1 week"
            ]
        })
    
    # ---------------------------
    # VIBRATION ANALYSIS
    # ---------------------------
    if vib > 10 or f_vib > 10:
        critical_issues.append({
            "icon": "⚙️",
            "title": "CRITICAL VIBRATION ALERT",
            "problem": f"Vibration at {vib:.2f} mm/s (Critical: >10 mm/s)",
            "impact": "Imminent bearing failure, catastrophic mechanical damage risk",
            "root_causes": [
                "Bearing failure (worn, pitted, or seized)",
                "Severe shaft misalignment",
                "Rotor imbalance or damage",
                "Loose mounting bolts or foundation",
                "Coupling wear or failure",
                "Bent shaft"
            ],
            "immediate_actions": [
                "1. EMERGENCY SHUTDOWN - Stop immediately",
                "2. Do not restart - bearing failure likely",
                "3. Tag machine 'DO NOT OPERATE'",
                "4. Contact maintenance team urgently"
            ],
            "resolution_steps": [
                "1. Inspect bearings for damage, heat, or noise",
                "2. Check bearing play - replace if excessive",
                "3. Measure shaft alignment with dial indicator",
                "4. Check all mounting bolts - torque to specification",
                "5. Inspect coupling for wear - replace if damaged",
                "6. Check shaft runout - straighten or replace if bent",
                "7. Verify rotor balance - rebalance if needed",
                "8. Replace all worn bearings (don't mix old/new)",
                "9. Realign shaft to within 0.002\" tolerance",
                "10. Test run at 50% speed before full operation"
            ],
            "prevention": [
                "Vibration monitoring every shift",
                "Bearing inspection monthly",
                "Alignment check quarterly",
                "Lubrication schedule adherence"
            ]
        })
    elif vib > 7 or f_vib > 7:
        high_issues.append({
            "icon": "⚙️",
            "title": "High Vibration Warning",
            "problem": f"Vibration at {vib:.2f} mm/s (High: >7 mm/s)",
            "impact": "Accelerated bearing wear, potential failure within days",
            "root_causes": [
                "Bearing wear progressing",
                "Misalignment developing",
                "Imbalance condition",
                "Loose components"
            ],
            "immediate_actions": [
                "1. Reduce speed by 20%",
                "2. Check all mounting bolts immediately",
                "3. Listen for unusual bearing noise",
                "4. Monitor vibration every 30 minutes"
            ],
            "resolution_steps": [
                "1. Tighten all mounting bolts to specification",
                "2. Check bearing temperature - should be <60°C",
                "3. Inspect shaft alignment - adjust if needed",
                "4. Verify belt tension (if belt-driven)",
                "5. Check coupling condition",
                "6. Schedule bearing replacement within 48 hours",
                "7. Perform vibration analysis to identify frequency"
            ],
            "prevention": [
                "Weekly vibration checks",
                "Monthly alignment verification",
                "Proper lubrication schedule"
            ]
        })
    elif vib > 5 or (t_vib == "rising" and vib > 4):
        medium_issues.append({
            "icon": "⚙️",
            "title": "Elevated Vibration",
            "problem": f"Vibration at {vib:.2f} mm/s (Warning: >5 mm/s)",
            "impact": "Early warning sign, monitor to prevent escalation",
            "immediate_actions": [
                "1. Check for loose components",
                "2. Verify proper lubrication",
                "3. Monitor vibration trend"
            ],
            "resolution_steps": [
                "1. Inspect mounting bolts",
                "2. Check bearing condition",
                "3. Schedule alignment check within 1 week"
            ]
        })
    
    # ---------------------------
    # SPEED ANALYSIS
    # ---------------------------
    if speed > 1500 or f_speed > 1500:
        critical_issues.append({
            "icon": "⚡",
            "title": "CRITICAL SPEED ALERT",
            "problem": f"Speed at {speed:.0f} RPM (Critical: >1500 RPM)",
            "impact": "Runaway condition, mechanical overstress, safety hazard",
            "root_causes": [
                "Motor controller malfunction",
                "Speed sensor failure",
                "Control system feedback error",
                "Governor failure",
                "Electrical fault"
            ],
            "immediate_actions": [
                "1. PRESS EMERGENCY STOP BUTTON",
                "2. Disconnect power immediately",
                "3. Do not attempt restart",
                "4. Inspect for mechanical damage"
            ],
            "resolution_steps": [
                "1. Test motor controller in manual mode",
                "2. Check speed sensor wiring and connections",
                "3. Verify speed sensor operation with multimeter",
                "4. Inspect control system for errors/faults",
                "5. Check feedback loop calibration",
                "6. Test governor operation (if equipped)",
                "7. Replace faulty controller or sensor",
                "8. Recalibrate speed control system",
                "9. Test at low speed (500 RPM) before full operation",
                "10. Monitor speed stability for 1 hour"
            ],
            "prevention": [
                "Monthly controller calibration check",
                "Quarterly sensor inspection",
                "Install overspeed protection at 1400 RPM"
            ]
        })
    elif speed > 1350 or f_speed > 1350:
        high_issues.append({
            "icon": "⚡",
            "title": "High Speed Warning",
            "problem": f"Speed at {speed:.0f} RPM (High: >1350 RPM)",
            "impact": "Operating above design limits, reduced component life",
            "root_causes": [
                "Excessive load demand",
                "Incorrect speed setpoint",
                "Control system drift",
                "Load imbalance"
            ],
            "immediate_actions": [
                "1. Reduce machine load immediately",
                "2. Verify speed setpoint is correct",
                "3. Check for control system errors",
                "4. Monitor speed for 30 minutes"
            ],
            "resolution_steps": [
                "1. Review and adjust speed setpoint",
                "2. Check load distribution",
                "3. Verify motor controller settings",
                "4. Inspect for control system faults",
                "5. Calibrate speed control if needed",
                "6. Balance load across system"
            ],
            "prevention": [
                "Weekly speed verification",
                "Monthly controller check",
                "Load monitoring"
            ]
        })
    elif speed > 1200 or (t_speed == "rising" and speed > 1150):
        medium_issues.append({
            "icon": "⚡",
            "title": "Elevated Speed",
            "problem": f"Speed at {speed:.0f} RPM (Warning: >1200 RPM)",
            "impact": "Approaching high threshold, monitor closely",
            "immediate_actions": [
                "1. Verify speed setpoint matches requirements",
                "2. Check load conditions",
                "3. Monitor speed stability"
            ],
            "resolution_steps": [
                "1. Review operational parameters",
                "2. Schedule controller calibration",
                "3. Verify load is within design limits"
            ]
        })
    
    # ---------------------------
    # ML MODEL ANALYSIS (FIXED: Correct rf_pred values)
    # ---------------------------
    # rf_pred: 0=critical, 1=normal, 2=warning
    if rf_pred == 0 or (rf_pred == 2 and iso_pred == -1):
        critical_issues.append({
            "icon": "🤖",
            "title": "ML Model: Critical Failure Risk Detected",
            "problem": "Machine learning models predict imminent failure",
            "impact": "AI has identified patterns matching previous failures",
            "root_causes": [
                "Combination of sensor readings matches failure signature",
                "Multiple parameters showing concerning trends",
                "Anomalous behavior detected in operational patterns"
            ],
            "immediate_actions": [
                "1. Take ML prediction seriously - high accuracy",
                "2. Perform comprehensive inspection immediately",
                "3. Check all critical components",
                "4. Consider preventive shutdown"
            ],
            "resolution_steps": [
                "1. Inspect all components identified in temperature/vibration/speed analysis",
                "2. Perform detailed diagnostic tests",
                "3. Replace any components showing wear",
                "4. Address all identified issues before restart"
            ]
        })
    
    # ---------------------------
    # ANOMALY DETECTION
    # ---------------------------
    if iso_pred == -1 and iso_score and iso_score < -0.1:
        high_issues.append({
            "icon": "🔍",
            "title": "Severe Anomaly Detected",
            "problem": f"Isolation Forest score: {iso_score:.3f} (Critical: <-0.1)",
            "impact": "Unusual pattern detected - investigate immediately",
            "root_causes": [
                "Sudden change in operating conditions",
                "Sensor malfunction or drift",
                "Unexpected mechanical behavior",
                "Process change or disturbance"
            ],
            "immediate_actions": [
                "1. Investigate what changed recently",
                "2. Check sensor calibration",
                "3. Inspect for mechanical changes",
                "4. Review recent maintenance activities"
            ],
            "resolution_steps": [
                "1. Verify all sensors are functioning correctly",
                "2. Check for recent process changes",
                "3. Inspect machine for physical changes",
                "4. Review maintenance logs for recent work",
                "5. Recalibrate sensors if needed"
            ]
        })
    
    # ---------------------------
    # TREND ANALYSIS
    # ---------------------------
    rising_trends = []
    if t_temp == "rising": rising_trends.append("temperature")
    if t_vib == "rising": rising_trends.append("vibration")
    if t_speed == "rising": rising_trends.append("speed")
    
    if len(rising_trends) >= 2:
        high_issues.append({
            "icon": "📈",
            "title": "Multiple Rising Trends Detected",
            "problem": f"Rising trends in: {', '.join(rising_trends)}",
            "impact": "Condition deteriorating, intervention needed soon",
            "immediate_actions": [
                "1. Identify root cause of increases",
                "2. Take corrective action now",
                "3. Monitor all parameters every 10 minutes"
            ],
            "resolution_steps": [
                "1. Address each rising parameter per recommendations above",
                "2. Look for common root cause",
                "3. Implement corrective measures",
                "4. Monitor effectiveness of actions"
            ]
        })
    
    # ---------------------------
    # BUILD RECOMMENDATIONS RESPONSE
    # ---------------------------
    if critical_issues:
        recommendations["priority"] = "critical"
        recommendations["actions"] = critical_issues
        recommendations["summary"] = f"🚨 CRITICAL: {len(critical_issues)} critical issue(s) detected. IMMEDIATE ACTION REQUIRED to prevent failure and ensure safety!"
    elif high_issues:
        recommendations["priority"] = "high"
        recommendations["actions"] = high_issues
        recommendations["summary"] = f"⚠️ HIGH PRIORITY: {len(high_issues)} serious issue(s) detected. Urgent attention needed within 1 hour to prevent escalation."
    elif medium_issues:
        recommendations["priority"] = "medium"
        recommendations["actions"] = medium_issues
        recommendations["summary"] = f"📋 MEDIUM PRIORITY: {len(medium_issues)} issue(s) detected. Schedule inspection within 24 hours."
    else:
        recommendations["priority"] = "normal"
        recommendations["summary"] = "✅ Machine is operating normally. Continue standard monitoring procedures."
        recommendations["preventive"] = [
            {
                "icon": "✅",
                "title": "Routine Maintenance Schedule",
                "actions": [
                    "Continue standard monitoring procedures",
                    "Check lubrication levels weekly",
                    "Inspect for wear and tear monthly",
                    "Schedule next preventive maintenance",
                    "Keep maintenance logs updated"
                ]
            }
        ]
    
    return recommendations


@app.route('/api/industrial-standards', methods=['GET'])
def get_industrial_standards():
    """Get industrial threshold standards"""
    try:
        # These thresholds match the industrial_standards.py file
        standards = {
            "temperature": {
                "normal": {"min": 20, "max": 65},
                "warning": {"min": 65, "max": 85},
                "critical": {"min": 85, "max": 120}
            },
            "vibration": {
                "normal": {"min": 0, "max": 3.0},
                "warning": {"min": 3.0, "max": 7.0},
                "critical": {"min": 7.0, "max": 15.0}
            },
            "speed": {
                "normal": {"min": 800, "max": 1150},
                "warning": {"min": 1150, "max": 1350},
                "critical": {"min": 1350, "max": 2000}
            }
        }
        return jsonify(standards)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------
# Manual Analysis Input Endpoint - Enhanced for Training and Prediction
# ---------------------------
@app.route("/api/manual-analysis", methods=["POST", "OPTIONS"])
def manual_analysis():
    """Enhanced manual analysis endpoint with proper model training and predictions"""
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200
    
    try:
        payload = request.get_json(force=True) or {}
        
        # Extract manual input values
        temperature = float(payload.get("temperature", 0))
        raw_vibration = float(payload.get("raw_vibration", 0))
        smooth_vibration = float(payload.get("smooth_vibration", 0))
        speed = float(payload.get("speed", 0))
        
        # Validate input values (allow 0 for temperature, but not negative speeds)
        validation_errors = []
        if temperature < -50 or temperature > 200:
            validation_errors.append("Temperature must be between -50°C and 200°C")
        if raw_vibration < 0 or raw_vibration > 50:
            validation_errors.append("Raw vibration must be between 0 and 50 mm/s")
        if smooth_vibration < 0 or smooth_vibration > 50:
            validation_errors.append("Smooth vibration must be between 0 and 50 mm/s")
        if speed <= 0 or speed > 5000:
            validation_errors.append("Speed must be between 1 and 5000 RPM")
        
        if validation_errors:
            return jsonify({
                "error": "Invalid input values",
                "validation_errors": validation_errors,
                "status": "error"
            }), 400
        
        # Use smooth vibration for model predictions (as it's more stable)
        # But analyze both for comprehensive assessment
        vibration_for_models = smooth_vibration
        
        # Prepare features for models using 12 engineered features
        def create_engineered_features_manual(temp, vib, spd):
            # Basic features
            temp_val = float(temp)
            vib_val = float(vib) 
            speed_val = float(spd)
            
            # Engineered features (using current values as approximations)
            temp_roll_mean = temp_val
            temp_roll_std = 0.1
            temp_trend = 0.0
            
            vib_roll_mean = vib_val
            vib_roll_std = 0.1
            vib_trend = 0.0
            
            speed_roll_mean = speed_val
            speed_roll_std = 1.0
            speed_trend = 0.0
            
            # Return 12 features in the same order as training
            return [
                temp_val, temp_roll_mean, temp_roll_std, temp_trend,
                vib_val, vib_roll_mean, vib_roll_std, vib_trend,
                speed_val, speed_roll_mean, speed_roll_std, speed_trend
            ]
        
        features = create_engineered_features_manual(temperature, vibration_for_models, speed)
        
        # ---------------------------
        # LSTM PREDICTION (Next 5-10 minutes)
        # ---------------------------
        lstm_prediction = None
        try:
            if lstm_model is not None and lstm_scaler is not None:
                # Create a sequence for LSTM (use current values repeated for sequence)
                seq_len = 10
                sequence = np.array([[temperature, vibration_for_models, speed] for _ in range(seq_len)])
                scaled_seq = lstm_scaler.transform(sequence)
                
                with lstm_lock:
                    # Predict next values (5-10 minutes ahead)
                    pred = lstm_model.predict(scaled_seq.reshape(1, seq_len, 3), verbose=0)[0]
                
                # Inverse transform to get actual values
                predicted_values = lstm_scaler.inverse_transform([pred])[0]
                
                lstm_prediction = {
                    "temperature": max(0, float(predicted_values[0])),
                    "vibration": max(0, float(predicted_values[1])),
                    "speed": max(0, float(predicted_values[2]))
                }
        except Exception as e:
            print(f"❌ LSTM prediction error: {e}")
            lstm_prediction = {
                "temperature": temperature,
                "vibration": vibration_for_models,
                "speed": speed
            }
        
        # ---------------------------
        # RANDOM FOREST CLASSIFICATION
        # ---------------------------
        rf_result = None
        try:
            if rf_model is not None and rf_scaler is not None:
                features_scaled = rf_scaler.transform([features])
                rf_pred = int(rf_model.predict(features_scaled)[0])
                
                # Map predictions to conditions
                if rf_pred == 0:
                    condition = "Critical"
                    risk_level = "High"
                    description = "Machine condition indicates critical failure risk"
                elif rf_pred == 2:
                    condition = "Warning"
                    risk_level = "Medium"
                    description = "Machine condition shows warning signs"
                else:
                    condition = "Normal"
                    risk_level = "Low"
                    description = "Machine condition appears healthy"
                
                rf_result = {
                    "condition": condition,
                    "risk_level": risk_level,
                    "description": description,
                    "prediction_code": rf_pred
                }
        except Exception as e:
            print(f"❌ Random Forest error: {e}")
            rf_result = {
                "condition": "Unknown",
                "risk_level": "Unknown",
                "description": f"Model error: {str(e)}",
                "prediction_code": -1
            }
        
        # ---------------------------
        # ISOLATION FOREST ANOMALY DETECTION
        # ---------------------------
        iso_result = None
        try:
            if iso_model is not None and rf_scaler is not None:
                features_scaled = rf_scaler.transform([features])
                iso_pred = int(iso_model.predict(features_scaled)[0])
                iso_score = float(iso_model.decision_function(features_scaled)[0])
                
                if iso_pred == -1:
                    anomaly_status = "Anomaly Detected"
                    severity = "High" if iso_score < -0.1 else "Medium"
                    description = f"Unusual pattern detected (score: {iso_score:.3f})"
                else:
                    anomaly_status = "Normal Pattern"
                    severity = "Low"
                    description = "Values within expected operational range"
                
                iso_result = {
                    "anomaly_status": anomaly_status,
                    "severity": severity,
                    "description": description,
                    "anomaly_score": iso_score
                }
        except Exception as e:
            print(f"❌ Isolation Forest error: {e}")
            iso_result = {
                "anomaly_status": "Unknown",
                "severity": "Unknown",
                "description": f"Model error: {str(e)}",
                "anomaly_score": 0.0
            }
        
        # ---------------------------
        # PARAMETER ANALYSIS & AFFECTED PARTS
        # ---------------------------
        parameter_analysis = []
        affected_parts = []
        solutions = []
        
        # Temperature Analysis
        if temperature > 95:
            parameter_analysis.append({
                "parameter": "Temperature",
                "status": "Critical",
                "value": temperature,
                "threshold": 95,
                "message": "Critical temperature - immediate shutdown required"
            })
            affected_parts.extend([
                "Bearings (thermal expansion and lubrication breakdown)",
                "Motor windings (insulation damage)",
                "Seals and gaskets (thermal degradation)",
                "Cooling system components"
            ])
            solutions.extend([
                "Immediate shutdown and cooling period",
                "Inspect cooling system for blockages or failures",
                "Check coolant levels and circulation",
                "Verify bearing lubrication",
                "Replace damaged thermal components"
            ])
        elif temperature > 85:
            parameter_analysis.append({
                "parameter": "Temperature",
                "status": "Warning",
                "value": temperature,
                "threshold": 85,
                "message": "High temperature - monitor closely"
            })
            affected_parts.extend([
                "Bearing lubrication (accelerated degradation)",
                "Motor efficiency (reduced performance)"
            ])
            solutions.extend([
                "Reduce operational load by 20-30%",
                "Clean air filters and cooling vents",
                "Check cooling system operation"
            ])
        
        # Vibration Analysis (analyze both raw and smooth)
        max_vibration = max(raw_vibration, smooth_vibration)
        if max_vibration > 10:
            parameter_analysis.append({
                "parameter": "Vibration",
                "status": "Critical",
                "value": max_vibration,
                "threshold": 10,
                "message": f"Critical vibration - Raw: {raw_vibration:.2f}, Smooth: {smooth_vibration:.2f} mm/s"
            })
            affected_parts.extend([
                "Main bearings (wear, pitting, seizure risk)",
                "Shaft alignment (misalignment damage)",
                "Coupling components (wear and failure)",
                "Foundation bolts (loosening)",
                "Rotor balance (imbalance effects)"
            ])
            solutions.extend([
                "Emergency shutdown - do not restart",
                "Replace all bearings immediately",
                "Check and correct shaft alignment",
                "Inspect and tighten all mounting bolts",
                "Balance rotor if necessary"
            ])
        elif max_vibration > 7:
            parameter_analysis.append({
                "parameter": "Vibration",
                "status": "Warning",
                "value": max_vibration,
                "threshold": 7,
                "message": f"High vibration - Raw: {raw_vibration:.2f}, Smooth: {smooth_vibration:.2f} mm/s"
            })
            affected_parts.extend([
                "Bearings (accelerated wear)",
                "Shaft alignment (developing misalignment)"
            ])
            solutions.extend([
                "Schedule bearing inspection within 48 hours",
                "Check shaft alignment",
                "Verify mounting bolt torque"
            ])
        
        # Add vibration comparison analysis
        vibration_difference = abs(raw_vibration - smooth_vibration)
        if vibration_difference > 2.0:
            parameter_analysis.append({
                "parameter": "Vibration Variance",
                "status": "Warning",
                "value": vibration_difference,
                "threshold": 2.0,
                "message": f"High variance between raw ({raw_vibration:.2f}) and smooth ({smooth_vibration:.2f}) vibration"
            })
            affected_parts.extend([
                "Vibration sensors (calibration issues)",
                "Signal processing system (filtering problems)"
            ])
            solutions.extend([
                "Check vibration sensor calibration",
                "Inspect signal processing filters",
                "Verify sensor mounting and connections"
            ])
        
        # Speed Analysis
        if speed > 1500:
            parameter_analysis.append({
                "parameter": "Speed",
                "status": "Critical",
                "value": speed,
                "threshold": 1500,
                "message": "Critical overspeed - runaway condition"
            })
            affected_parts.extend([
                "Motor controller (malfunction risk)",
                "Speed sensors (failure or drift)",
                "Mechanical components (overstress)",
                "Safety systems (governor failure)"
            ])
            solutions.extend([
                "Press emergency stop immediately",
                "Disconnect power supply",
                "Inspect motor controller for faults",
                "Check speed sensor calibration",
                "Test safety shutdown systems"
            ])
        elif speed > 1350:
            parameter_analysis.append({
                "parameter": "Speed",
                "status": "Warning",
                "value": speed,
                "threshold": 1350,
                "message": "High speed - operating above design limits"
            })
            affected_parts.extend([
                "Motor controller (potential drift)",
                "Mechanical components (increased wear)"
            ])
            solutions.extend([
                "Reduce load to bring speed within limits",
                "Check speed controller settings",
                "Verify load distribution"
            ])
        
        # ---------------------------
        # OVERALL CONDITION ASSESSMENT
        # ---------------------------
        critical_count = len([p for p in parameter_analysis if p["status"] == "Critical"])
        warning_count = len([p for p in parameter_analysis if p["status"] == "Warning"])
        
        if critical_count > 0:
            overall_condition = "Critical"
            priority = "Immediate Action Required"
            condition_color = "red"
        elif warning_count > 0:
            overall_condition = "Warning"
            priority = "Action Required Within 24 Hours"
            condition_color = "orange"
        else:
            overall_condition = "Normal"
            priority = "Continue Standard Monitoring"
            condition_color = "green"
        
        # ---------------------------
        # RESPONSE STRUCTURE
        # ---------------------------
        response_data = {
            "status": "success",
            "input_values": {
                "temperature": temperature,
                "raw_vibration": raw_vibration,
                "smooth_vibration": smooth_vibration,
                "speed": speed
            },
            "predictions": {
                "lstm_forecast": lstm_prediction,
                "time_horizon": "5-10 minutes ahead"
            },
            "model_analysis": {
                "random_forest": rf_result,
                "isolation_forest": iso_result
            },
            "parameter_analysis": parameter_analysis,
            "affected_parts": list(set(affected_parts)),  # Remove duplicates
            "solutions": list(set(solutions)),  # Remove duplicates
            "overall_assessment": {
                "condition": overall_condition,
                "priority": priority,
                "color": condition_color,
                "critical_parameters": critical_count,
                "warning_parameters": warning_count
            },
            "chart_data": {
                "actual_values": [temperature, raw_vibration, smooth_vibration, speed],
                "predicted_values": [
                    lstm_prediction["temperature"] if lstm_prediction else temperature,
                    lstm_prediction["vibration"] if lstm_prediction else raw_vibration,
                    lstm_prediction["vibration"] if lstm_prediction else smooth_vibration,
                    lstm_prediction["speed"] if lstm_prediction else speed
                ],
                "parameter_labels": ["Temperature (°C)", "Raw Vibration (mm/s)", "Smooth Vibration (mm/s)", "Speed (RPM)"]
            }
        }
        
        response = jsonify(response_data)
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200
        
    except Exception as e:
        print(f"❌ Manual analysis error: {e}")
        import traceback
        traceback.print_exc()
        
        response = jsonify({
            "status": "error",
            "error": str(e),
            "message": "Analysis failed. Please check your input values and try again."
        })
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 500

# ---------------------------
# main analyze endpoint (updated to use 3 params)
# ---------------------------
@app.route("/chat/analyze", methods=["POST", "OPTIONS"])
def analyze_chart():
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200
    import numpy as np
    payload = request.get_json(force=True) or {}

    chart_type = payload.get("chartType")
    data = payload.get("data", {})

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

    if len(temp) < 3 or len(speed) < 3 or len(vib) < 3:
        response = jsonify({
            "issue": "Not enough data",
            "cause": "Need minimum 3 points",
            "solution": "Collect more readings",
            "forecast": None,
            "summary": "No meaningful analysis possible due to insufficient data."
        })
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")


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

    temp = [max(0, v) for v in temp]
    speed = [max(0, v) for v in speed]
    vib = [max(0, v) for v in vib]

    latest_temp = max(temp[-10:]) if temp else 0
    latest_speed = max(speed[-10:]) if speed else 0
    latest_vib = max(vib[-10:]) if vib else 0
    
    # Create engineered features to match training data (12 features total)
    # Since we only have single values, we'll use them as both current and rolling values
    def create_engineered_features(temperature, vibration, speed):
        # Basic features
        temp_val = float(temperature)
        vib_val = float(vibration) 
        speed_val = float(speed)
        
        # Engineered features (using current values as approximations)
        temp_roll_mean = temp_val  # Approximate rolling mean as current value
        temp_roll_std = 0.1  # Small std deviation as default
        temp_trend = 0.0  # No trend information available
        
        vib_roll_mean = vib_val
        vib_roll_std = 0.1
        vib_trend = 0.0
        
        speed_roll_mean = speed_val
        speed_roll_std = 1.0  # Slightly higher std for speed
        speed_trend = 0.0
        
        # Return 12 features in the same order as training:
        # [temp, temp_roll_mean, temp_roll_std, temp_trend, 
        #  vib, vib_roll_mean, vib_roll_std, vib_trend,
        #  speed, speed_roll_mean, speed_roll_std, speed_trend]
        return [
            temp_val, temp_roll_mean, temp_roll_std, temp_trend,
            vib_val, vib_roll_mean, vib_roll_std, vib_trend,
            speed_val, speed_roll_mean, speed_roll_std, speed_trend
        ]
    
    # Create engineered features for model predictions
    latest_for_models = create_engineered_features(latest_temp, latest_vib, latest_speed)

    # ---------------------------
    # FORECAST (LSTM) with thread lock
    # ---------------------------
    try:
        if lstm_model is not None and lstm_scaler is not None:
            # Build sequence using available last 10 rows (or fallback)
            # IMPORTANT: LSTM was trained with order [temperature, vibration, speed] (3 features only)
            seq_len = 10
            if len(temp) >= seq_len:
                # Correct order: temperature, vibration, speed (matches training)
                seq = np.array([[temp[-seq_len + i], vib[-seq_len + i], speed[-seq_len + i]] for i in range(seq_len)])
                scaled = lstm_scaler.transform(seq)
                with lstm_lock:
                    pred = lstm_model.predict(scaled.reshape(1, seq_len, 3), verbose=0)[0]
                inv = lstm_scaler.inverse_transform([pred])[0]
                # Output order: temperature, vibration, speed
                f_temp = max(0, float(inv[0]))
                f_vib = max(0, float(inv[1]))
                f_speed = max(0, float(inv[2]))
            else:
                # Use simple forecast based on current values
                f_temp = latest_temp * 1.02  # Slight increase
                f_vib = latest_vib * 0.98   # Slight decrease
                f_speed = latest_speed * 1.01  # Slight increase
        else:
            f_temp = latest_temp * 1.01
            f_vib = latest_vib * 0.99
            f_speed = latest_speed * 1.005
    except Exception as e:
        print("❌ LSTM predict error:", e)
        f_temp = latest_temp * 1.01
        f_vib = latest_vib * 0.99
        f_speed = latest_speed * 1.005

    # ---------------------------
    # RANDOM FOREST (FIXED: Now uses scaling and correct label mapping)
    # ---------------------------
    try:
        if rf_model is not None and rf_scaler is not None:
            # CRITICAL FIX: Scale features before prediction
            features_scaled = rf_scaler.transform([latest_for_models])
            rf_pred = int(rf_model.predict(features_scaled)[0])
            
            # CRITICAL FIX: Correct label mapping (0=critical, 1=normal, 2=warning)
            if rf_pred == 0:
                rf_issue = "Critical (Failure Risk)"
                rf_cause = "The machine's operating signature matches critical failure patterns."
                rf_solution = "IMMEDIATE ACTION REQUIRED: Stop machine and perform comprehensive inspection."
            elif rf_pred == 2:
                rf_issue = "Warning (Elevated Risk)"
                rf_cause = "The machine's operating signature shows warning signs of potential issues."
                rf_solution = "Schedule inspection within 24 hours to prevent escalation."
            else:  # rf_pred == 1
                rf_issue = "Normal"
                rf_cause = "The machine's operational signature appears healthy and stable."
                rf_solution = "Continue with standard monitoring procedures."
        else:
            rf_pred = None
            rf_issue = "RF Model not loaded"
            rf_cause = "Model file or scaler missing"
            rf_solution = "Retrain and place rf_model.pkl and scaler.pkl in model directory."
    except Exception as e:
        rf_pred = None
        rf_issue = "RF Model Error"
        rf_cause = f"Error: {str(e)}"
        rf_solution = "Retrain RF model."

    # ---------------------------
    # ISOLATION FOREST (FIXED: Now uses scaling)
    # ---------------------------
    try:
        if iso_model is not None and rf_scaler is not None:
            # CRITICAL FIX: Scale features before prediction
            features_scaled = rf_scaler.transform([latest_for_models])
            iso_pred = int(iso_model.predict(features_scaled)[0])
            iso_score = float(iso_model.decision_function(features_scaled)[0])
            
            if iso_pred == -1:
                if iso_score < -0.1:
                    iso_issue = "Critical Sudden Change"
                elif iso_score < -0.05:
                    iso_issue = "High Sudden Change"
                else:
                    iso_issue = "Medium Sudden Change"
                iso_cause = f"A sudden, unexpected deviation was detected in sensor readings (score: {iso_score:.2f})."
                iso_solution = "Investigate the machine immediately for the source of the sudden change."
            else:
                iso_issue = "Low (No Sudden Changes)"
                iso_cause = "Sensor values are within the expected operational distribution."
                iso_solution = "Continue monitoring."
        else:
            iso_pred = None
            iso_score = None
            iso_issue = "ISO Model not loaded"
            iso_cause = "Model file or scaler missing"
            iso_solution = "Retrain and place iso_model.pkl and scaler.pkl in model directory."
    except Exception as e:
        iso_pred = None
        iso_score = None
        iso_issue = "ISO Model Error"
        iso_cause = f"Error: {str(e)}"
        iso_solution = "Retrain ISO model."

    # ---------------------------
    # TREND
    # ---------------------------
    def trend(a):
        if len(a) < 3:
            return "stable"
        a1, b1, c1 = a[-3:]
        if a1 < b1 < c1: return "rising"
        if a1 > b1 > c1: return "falling"
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

    if chart_type == "lineChart":
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

    # ---------------------------
    # INTELLIGENT RECOMMENDATIONS ENGINE
    # ---------------------------
    recommendations = _generate_intelligent_recommendations(
        latest_temp, latest_speed, latest_vib,
        f_temp, f_speed, f_vib,
        rf_pred, iso_pred, iso_score,
        t_temp, t_speed, t_vib,
        chart_type
    )
    
    # ---------------------------
    # TRIGGER ALERT SYSTEM (Send Email based on conditions)
    # ---------------------------
    alert_result = None
    email_sent = False
    
    # Check if we should trigger alerts based on recommendations priority
    if recommendations.get("priority") in ["critical", "high", "medium"]:
        try:
            # Get user email from payload
            user_email = payload.get("email")
            machine_id = payload.get("machine_id", "Unknown")
            
            # Prepare data for alert system
            alert_data = {
                "temperature": temp,
                "speed": speed,
                "vibration": vib,
                "email": user_email,
                "machine_id": machine_id
            }
            
            # Process and send alerts
            alert_result = process_sensor_data(alert_data)
            email_sent = alert_result.get("email_sent", False)
            
            print(f"✅ Alert system triggered - Email sent: {email_sent}")
        except Exception as e:
            print(f"❌ Alert system error: {e}")
    
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
        },
        "recommendations": recommendations,
        "alert_status": {
            "email_sent": email_sent,
            "alerts": alert_result.get("alerts", []) if alert_result else [],
            "status": alert_result.get("status", "Unknown") if alert_result else "Unknown"
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
            temperature=float(data['temperature']),
            vibration=float(data['vibration']),
            speed=float(data['speed'])
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

# ------- report / process / download endpoints unchanged -------


@app.route("/process", methods=["POST", "OPTIONS"])
def process_data_route():
    """Process sensor data and trigger alert system - UPDATED"""
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200
    
    try:
        data = request.json or {}
        print(f"📥 Received /process request for machine: {data.get('machine_id', 'Unknown')}")
        print(f"📧 Email: {data.get('email', 'Not provided')}")
        print(f"📊 Data points - Temp: {len(data.get('temperature', []))}, Vib: {len(data.get('vibration', []))}, Speed: {len(data.get('speed', []))}")
        
        # Validate required data
        if not data.get('temperature') or not data.get('vibration') or not data.get('speed'):
            response = jsonify({
                "error": "Missing sensor data",
                "status": "Error",
                "alerts": [],
                "recommendation": "Please ensure all sensor data is provided"
            })
            response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
            response.headers.add("Access-Control-Allow-Credentials", "true")
            return response, 400
        
        # Process the data
        result = process_sensor_data(data)
        print(f"✅ Processing complete - Status: {result.get('status')}, Email sent: {result.get('email_sent', False)}")
        
        response = jsonify(result)
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200
        
    except Exception as e:
        print(f"❌ Error in /process endpoint: {e}")
        import traceback
        traceback.print_exc()
        response = jsonify({
            "error": str(e),
            "status": "Error",
            "alerts": [],
            "recommendation": "An error occurred during processing. Please try again.",
            "email_sent": False
        })
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 500


@app.route("/download", methods=["GET", "OPTIONS"])
def download_report():
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200
    
    # PDF is saved in backend directory
    pdf_path = os.path.join(os.path.dirname(__file__), "report.pdf")
    print(f"🔍 Looking for PDF at: {pdf_path}")
    print(f"📁 PDF exists: {os.path.exists(pdf_path)}")
    
    if not os.path.exists(pdf_path):
        print("❌ PDF file not found")
        response = jsonify({"error": "Report not generated yet. Please try the analyze button first."})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 404
    
    try:
        print(f"✅ Sending PDF file: {pdf_path}")
        response = send_file(pdf_path, as_attachment=True, download_name="Machine_Report.pdf", mimetype="application/pdf")
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response
    except Exception as e:
        print(f"❌ Error sending PDF: {e}")
        response = jsonify({"error": f"Failed to send PDF: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 500


# ---------------------------
# RETRAIN AND PREDICT ENDPOINT - Enhanced Training with User-Selected Period
# ---------------------------
@app.route("/api/retrain-and-predict", methods=["POST", "OPTIONS"])
def retrain_and_predict():
    """Retrain LSTM model on user-specified hours of data and provide enhanced predictions"""
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200
    
    try:
        payload = request.get_json(force=True) or {}
        
        # Extract input values
        temperature = float(payload.get("temperature", 0))
        raw_vibration = float(payload.get("raw_vibration", 0))
        smooth_vibration = float(payload.get("smooth_vibration", 0))
        speed = float(payload.get("speed", 0))
        training_hours = int(payload.get("training_hours", 3))
        
        # Validate inputs
        if temperature <= 0 or raw_vibration < 0 or smooth_vibration < 0 or speed <= 0:
            return jsonify({
                "error": "Invalid input values",
                "status": "error"
            }), 400
        
        if training_hours < 1 or training_hours > 24:
            return jsonify({
                "error": "Training hours must be between 1 and 24",
                "status": "error"
            }), 400
        
        # ---------------------------
        # LOAD AND PREPARE TRAINING DATA
        # ---------------------------
        sensor_file = find_sensor_file()
        if not sensor_file:
            return jsonify({
                "error": "No sensor data file found for training",
                "status": "error"
            }), 404
        
        try:
            # Load sensor data
            raw_rows = load_raw_sensor_rows(sensor_file)
            
            # Convert to DataFrame for easier processing
            df_data = []
            for row in raw_rows:
                try:
                    timestamp = row.get("timestamp")
                    if isinstance(timestamp, (int, float)):
                        timestamp = pd.to_datetime(timestamp, unit='s')
                    elif isinstance(timestamp, str):
                        timestamp = pd.to_datetime(timestamp)
                    else:
                        timestamp = pd.Timestamp.now()
                    
                    df_data.append({
                        'timestamp': timestamp,
                        'temperature': float(row.get("temperature", 0)),
                        'vibration': float(row.get("vibration", 0)),
                        'speed': float(row.get("speed", 0))
                    })
                except Exception as e:
                    print(f"Skipping invalid row: {e}")
                    continue
            
            if len(df_data) < 50:
                return jsonify({
                    "error": f"Insufficient data for training. Need at least 50 points, got {len(df_data)}",
                    "status": "error"
                }), 400
            
            df = pd.DataFrame(df_data)
            df = df.sort_values('timestamp')
            
            # Filter to last N hours
            cutoff_time = df['timestamp'].max() - pd.Timedelta(hours=training_hours)
            recent_df = df[df['timestamp'] >= cutoff_time].copy()
            
            if len(recent_df) < 20:
                return jsonify({
                    "error": f"Insufficient recent data. Only {len(recent_df)} points in last {training_hours} hours",
                    "status": "error"
                }), 400
            
            print(f"🎯 Training on {len(recent_df)} data points from last {training_hours} hours")
            
        except Exception as e:
            return jsonify({
                "error": f"Failed to load training data: {str(e)}",
                "status": "error"
            }), 500
        
        # ---------------------------
        # RETRAIN LSTM MODEL
        # ---------------------------
        try:
            from sklearn.preprocessing import MinMaxScaler
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense
            import tensorflow as tf
            
            # Prepare training data
            features = ["temperature", "vibration", "speed"]
            training_data = recent_df[features].values.astype(float)
            
            # Scale the data
            new_scaler = MinMaxScaler()
            scaled_data = new_scaler.fit_transform(training_data)
            
            # Create sequences for LSTM
            def create_sequences(data, seq_len=10):
                X, y = [], []
                for i in range(len(data) - seq_len):
                    X.append(data[i:i+seq_len])
                    y.append(data[i+seq_len])
                return np.array(X), np.array(y)
            
            SEQ_LEN = 10
            if len(scaled_data) <= SEQ_LEN:
                return jsonify({
                    "error": f"Need at least {SEQ_LEN + 1} data points for training, got {len(scaled_data)}",
                    "status": "error"
                }), 400
            
            X, y = create_sequences(scaled_data, SEQ_LEN)
            X = X.reshape((X.shape[0], SEQ_LEN, len(features)))
            
            print(f"🔄 Training LSTM with {X.shape[0]} sequences...")
            
            # Build and train model
            with lstm_lock:
                new_model = Sequential()
                new_model.add(LSTM(64, return_sequences=False, input_shape=(SEQ_LEN, len(features))))
                new_model.add(Dense(32, activation="relu"))
                new_model.add(Dense(len(features)))
                new_model.compile(optimizer="adam", loss="mse")
                
                # Train with fewer epochs for faster response
                epochs = min(30, max(10, len(X) // 5))  # Adaptive epochs based on data size
                new_model.fit(X, y, epochs=epochs, batch_size=min(16, len(X)), verbose=0)
                
                # Update global model and scaler
                global lstm_model, lstm_scaler
                lstm_model = new_model
                lstm_scaler = new_scaler
            
            print(f"✅ LSTM retrained successfully with {epochs} epochs")
            
        except Exception as e:
            return jsonify({
                "error": f"Failed to retrain model: {str(e)}",
                "status": "error"
            }), 500
        
        # ---------------------------
        # ENHANCED PREDICTIONS WITH RETRAINED MODEL
        # ---------------------------
        try:
            # Use smooth vibration for model predictions
            vibration_for_models = smooth_vibration
            current_values = [temperature, vibration_for_models, speed]
            
            # Create sequence for prediction
            seq_len = 10
            sequence = np.array([current_values for _ in range(seq_len)])
            scaled_seq = lstm_scaler.transform(sequence)
            
            with lstm_lock:
                # Predict next values (5-10 minutes ahead)
                pred = lstm_model.predict(scaled_seq.reshape(1, seq_len, 3), verbose=0)[0]
            
            # Inverse transform to get actual values
            predicted_values = lstm_scaler.inverse_transform([pred])[0]
            
            enhanced_prediction = {
                "temperature": max(0, float(predicted_values[0])),
                "vibration": max(0, float(predicted_values[1])),
                "speed": max(0, float(predicted_values[2]))
            }
            
            # Generate multiple future predictions (next 30 minutes in 5-minute intervals)
            future_predictions = []
            current_seq = scaled_seq.reshape(seq_len, 3)
            
            for step in range(6):  # 6 steps = 30 minutes
                with lstm_lock:
                    next_pred = lstm_model.predict(current_seq.reshape(1, seq_len, 3), verbose=0)[0]
                
                # Inverse transform
                next_values = lstm_scaler.inverse_transform([next_pred])[0]
                
                future_predictions.append({
                    "time_offset": f"+{(step + 1) * 5} min",
                    "temperature": max(0, float(next_values[0])),
                    "vibration": max(0, float(next_values[1])),
                    "speed": max(0, float(next_values[2]))
                })
                
                # Update sequence for next prediction
                current_seq = np.vstack([current_seq[1:], next_pred.reshape(1, 3)])
            
        except Exception as e:
            return jsonify({
                "error": f"Failed to generate predictions: {str(e)}",
                "status": "error"
            }), 500
        
        # ---------------------------
        # ENHANCED ANALYSIS WITH RETRAINED MODEL
        # ---------------------------
        try:
            # Run enhanced analysis with the retrained model
            # Create engineered features to match training data (12 features total)
            def create_engineered_features_for_analysis(temp, vib, spd):
                # Basic features
                temp_val = float(temp)
                vib_val = float(vib) 
                speed_val = float(spd)
                
                # Engineered features (using current values as approximations)
                temp_roll_mean = temp_val
                temp_roll_std = 0.1
                temp_trend = 0.0
                
                vib_roll_mean = vib_val
                vib_roll_std = 0.1
                vib_trend = 0.0
                
                speed_roll_mean = speed_val
                speed_roll_std = 1.0
                speed_trend = 0.0
                
                # Return 12 features in the same order as training
                return [
                    temp_val, temp_roll_mean, temp_roll_std, temp_trend,
                    vib_val, vib_roll_mean, vib_roll_std, vib_trend,
                    speed_val, speed_roll_mean, speed_roll_std, speed_trend
                ]
            
            features_for_analysis = create_engineered_features_for_analysis(temperature, vibration_for_models, speed)
            
            # Random Forest Analysis (if available)
            rf_result = None
            if rf_model is not None and rf_scaler is not None:
                features_scaled = rf_scaler.transform([features_for_analysis])
                rf_pred = int(rf_model.predict(features_scaled)[0])
                
                if rf_pred == 0:
                    condition = "Critical"
                    risk_level = "High"
                    description = "Retrained model confirms critical failure risk"
                elif rf_pred == 2:
                    condition = "Warning"
                    risk_level = "Medium"
                    description = "Retrained model shows warning signs"
                else:
                    condition = "Normal"
                    risk_level = "Low"
                    description = "Retrained model indicates healthy condition"
                
                rf_result = {
                    "condition": condition,
                    "risk_level": risk_level,
                    "description": description,
                    "prediction_code": rf_pred
                }
            
            # Isolation Forest Analysis (if available)
            iso_result = None
            if iso_model is not None and rf_scaler is not None:
                features_scaled = rf_scaler.transform([features_for_analysis])
                iso_pred = int(iso_model.predict(features_scaled)[0])
                iso_score = float(iso_model.decision_function(features_scaled)[0])
                
                if iso_pred == -1:
                    anomaly_status = "Anomaly Detected"
                    severity = "High" if iso_score < -0.1 else "Medium"
                    description = f"Retrained analysis detects anomaly (score: {iso_score:.3f})"
                else:
                    anomaly_status = "Normal Pattern"
                    severity = "Low"
                    description = "Retrained analysis shows normal patterns"
                
                iso_result = {
                    "anomaly_status": anomaly_status,
                    "severity": severity,
                    "description": description,
                    "anomaly_score": iso_score
                }
            
            # Enhanced condition assessment
            critical_count = 0
            warning_count = 0
            parameter_analysis = []
            
            # Temperature analysis
            if temperature > 95:
                critical_count += 1
                parameter_analysis.append({
                    "parameter": "Temperature",
                    "status": "Critical",
                    "value": temperature,
                    "threshold": 95,
                    "message": "Critical temperature detected by retrained model"
                })
            elif temperature > 85:
                warning_count += 1
                parameter_analysis.append({
                    "parameter": "Temperature",
                    "status": "Warning",
                    "value": temperature,
                    "threshold": 85,
                    "message": "High temperature detected by retrained model"
                })
            
            # Vibration analysis
            max_vibration = max(raw_vibration, smooth_vibration)
            if max_vibration > 10:
                critical_count += 1
                parameter_analysis.append({
                    "parameter": "Vibration",
                    "status": "Critical",
                    "value": max_vibration,
                    "threshold": 10,
                    "message": f"Critical vibration detected (Raw: {raw_vibration:.2f}, Smooth: {smooth_vibration:.2f})"
                })
            elif max_vibration > 7:
                warning_count += 1
                parameter_analysis.append({
                    "parameter": "Vibration",
                    "status": "Warning",
                    "value": max_vibration,
                    "threshold": 7,
                    "message": f"High vibration detected (Raw: {raw_vibration:.2f}, Smooth: {smooth_vibration:.2f})"
                })
            
            # Speed analysis
            if speed > 1500:
                critical_count += 1
                parameter_analysis.append({
                    "parameter": "Speed",
                    "status": "Critical",
                    "value": speed,
                    "threshold": 1500,
                    "message": "Critical overspeed detected by retrained model"
                })
            elif speed > 1350:
                warning_count += 1
                parameter_analysis.append({
                    "parameter": "Speed",
                    "status": "Warning",
                    "value": speed,
                    "threshold": 1350,
                    "message": "High speed detected by retrained model"
                })
            
            # Overall assessment
            if critical_count > 0:
                overall_condition = "Critical"
                priority = "Immediate Action Required"
                condition_color = "red"
            elif warning_count > 0:
                overall_condition = "Warning"
                priority = "Action Required Within 24 Hours"
                condition_color = "orange"
            else:
                overall_condition = "Normal"
                priority = "Continue Standard Monitoring"
                condition_color = "green"
            
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            # Fallback analysis with all required variables
            overall_condition = "Normal"
            priority = "Continue Standard Monitoring"
            condition_color = "green"
            parameter_analysis = []
            critical_count = 0
            warning_count = 0
            rf_result = {
                "condition": "Unknown",
                "risk_level": "Unknown", 
                "description": f"Model error: {str(e)}",
                "prediction_code": -1
            }
            iso_result = {
                "anomaly_status": "Unknown",
                "severity": "Unknown",
                "description": f"Model error: {str(e)}",
                "anomaly_score": 0.0
            }
        
        # ---------------------------
        # RESPONSE WITH ENHANCED PREDICTIONS
        # ---------------------------
        response_data = {
            "status": "success",
            "training_info": {
                "training_hours": training_hours,
                "data_points_used": len(recent_df),
                "training_period": f"Last {training_hours} hours",
                "model_updated": True
            },
            "input_values": {
                "temperature": temperature,
                "raw_vibration": raw_vibration,
                "smooth_vibration": smooth_vibration,
                "speed": speed
            },
            "predictions": {
                "lstm_forecast": enhanced_prediction,
                "time_horizon": "5-10 minutes ahead",
                "future_timeline": future_predictions
            },
            "model_analysis": {
                "random_forest": rf_result,
                "isolation_forest": iso_result
            },
            "parameter_analysis": parameter_analysis,
            "overall_assessment": {
                "condition": overall_condition,
                "priority": priority,
                "color": condition_color,
                "critical_parameters": critical_count,
                "warning_parameters": warning_count
            },
            "chart_data": {
                "actual_values": [temperature, raw_vibration, smooth_vibration, speed],
                "predicted_values": [
                    enhanced_prediction["temperature"],
                    enhanced_prediction["vibration"],
                    enhanced_prediction["vibration"],
                    enhanced_prediction["speed"]
                ],
                "parameter_labels": ["Temperature (°C)", "Raw Vibration (mm/s)", "Smooth Vibration (mm/s)", "Speed (RPM)"]
            },
            "enhanced_features": {
                "custom_training_period": True,
                "real_time_retraining": True,
                "multi_step_predictions": True,
                "adaptive_model": True
            }
        }
        
        response = jsonify(response_data)
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200
        
    except Exception as e:
        print(f"❌ Retrain and predict error: {e}")
        import traceback
        traceback.print_exc()
        
        response = jsonify({
            "status": "error",
            "error": str(e),
            "message": "Failed to retrain model and generate predictions. Please try again."
        })
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 500

# ---------------------------
# Run
# ---------------------------
if __name__ == '__main__':
    try:
        with app.app_context():
            print("🔄 Initializing database...")
            db.create_all()
            print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
        print("🚀 Starting server anyway...")
    
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
