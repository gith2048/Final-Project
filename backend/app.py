import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import random, smtplib
from routes.predict import predict_bp
from routes.chatbot import chatbot_bp
import tensorflow as tf
import pickle
from report_routes import report_bp
import numpy as np


app = Flask(__name__)
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
with open("model/iso_model.pkl", "rb") as f:
    iso_model = pickle.load(f)

with open("model/rf_model.pkl", "rb") as f:
    rf_model = pickle.load(f)

lstm_model = tf.keras.models.load_model("model/lstm_model.keras")

with open("model/temp_scaler.pkl", "rb") as f:
    temp_scaler = pickle.load(f)


app.register_blueprint(predict_bp)
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

    print("Received chartType:", chart_type)
    print("Received chartData:", chart_data)

    if not chart_type or not chart_data:
        return jsonify({
            "issue": "⚠️ Missing chart data.",
            "cause": "Chart type or data was not provided.",
            "solution": "Please ensure a valid chart is dropped with complete sensor data."
        })

    try:
        if chart_type == "lineChart":
            temps = chart_data["temperature"][-5:]
            scaled = temp_scaler.transform([[t] for t in temps])
            input_seq = np.array(scaled).reshape(1, 5, 1)
            prediction = lstm_model.predict(input_seq)[0][0]
            predicted_temp = temp_scaler.inverse_transform([[prediction]])[0][0]

            issue = f"📈 Forecasted temperature: {predicted_temp:.2f}°C. Monitor for overheating."
            cause = "Temperature trend indicates a rising pattern, possibly due to poor lubrication or high load."
            solution = "Inspect cooling system, verify lubrication levels, and reduce machine load temporarily."

            return jsonify({
                "issue": issue,
                "cause": cause,
                "solution": solution
            })

        elif chart_type == "barChart":
            latest = {
                "temperature": chart_data["temperature"][-1],
                "current": chart_data["current"][-1],
                "speed": chart_data["speed"][-1]
            }
            features = [[latest["temperature"], latest["current"], latest["speed"]]]
            prediction = rf_model.predict(features)[0]

            if prediction == 1:
                issue = "⚠️ High failure risk detected."
                cause = "Sensor readings show elevated temperature and current, indicating stress on components."
                solution = "Schedule immediate inspection, check for wear in bearings and motor alignment."
            else:
                issue = "✅ Machine is operating normally."
                cause = "Sensor readings are within safe operating thresholds."
                solution = "Continue regular monitoring and preventive maintenance."

            return jsonify({
                "issue": issue,
                "cause": cause,
                "solution": solution
            })

        elif chart_type == "pieChart":
            features = [[
                chart_data["temperature"][-1],
                chart_data["current"][-1],
                chart_data["speed"][-1]
            ]]
            anomaly = iso_model.predict(features)[0]

            if anomaly == -1:
                issue = "🚨 Anomaly detected in sensor readings!"
                cause = "Unusual combination of temperature, current, and speed suggests sensor drift or mechanical fault."
                solution = "Recalibrate sensors and inspect mechanical components for misalignment or wear."
            else:
                issue = "✅ No anomalies detected."
                cause = "Sensor readings are consistent with expected patterns."
                solution = "No action needed. Maintain regular monitoring."

            return jsonify({
                "issue": issue,
                "cause": cause,
                "solution": solution
            })

        else:
            return jsonify({
                "issue": "🤔 Unrecognized chart type.",
                "cause": "Chart type not supported by analysis engine.",
                "solution": "Use lineChart, barChart, or pieChart for insights."
            })

    except Exception as e:
        return jsonify({
            "issue": "⚠️ Error analyzing chart.",
            "cause": str(e),
            "solution": "Check data format and model availability."
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



# ---------------------------
# Run App
# ---------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)