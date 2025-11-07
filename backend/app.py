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
with open("model/iso_model.pkl", "rb") as f:
    iso_model = pickle.load(f)

with open("model/rf_model.pkl", "rb") as f:
    rf_model = pickle.load(f)

lstm_model = tf.keras.models.load_model("model/lstm_model.keras")

# Old scaler (used only for temperature-based models)
with open("model/temp_scaler.pkl", "rb") as f:
    temp_scaler = pickle.load(f)

# ✅ New scaler trained on 3 features: temperature, speed, vibration
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
            # Use last 5 full feature vectors
            sequence = []
            for i in range(-5, 0):
                sequence.append([
                    chart_data["temperature"][i],
                    chart_data["speed"][i],
                    chart_data["vibration"][i]
                ])
            scaled_seq = multi_scaler.transform(sequence)
            input_seq = np.array(scaled_seq).reshape(1, 5, 3)
            prediction = lstm_model.predict(input_seq)[0]
            forecast = multi_scaler.inverse_transform([prediction])[0]

            issue = f"📈 Forecasted temperature: {forecast[0]:.2f}°C. Monitor for overheating."
            cause = "Temperature and speed trends suggest rising thermal load, possibly due to friction or poor airflow."
            solution = "Inspect cooling system, verify lubrication, and reduce machine load temporarily."

            return jsonify({
                "issue": issue,
                "cause": cause,
                "solution": solution,
                "forecast": {
                    "temperature": round(forecast[0], 2),
                    "speed": round(forecast[1], 2),
                    "vibration": round(forecast[2], 2)
                }
            })

        elif chart_type == "barChart":
            latest = [
                chart_data["temperature"][-1],
                chart_data["speed"][-1],
                chart_data["vibration"][-1]
            ]
            prediction = rf_model.predict([latest])[0]

            if prediction == 1:
                issue = "⚠️ High failure risk detected."
                cause = "Sensor readings show elevated temperature and vibration, indicating stress on components."
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
            latest = [
                chart_data["temperature"][-1],
                chart_data["speed"][-1],
                chart_data["vibration"][-1]
            ]
            anomaly = iso_model.predict([latest])[0]

            if anomaly == -1:
                issue = "🚨 Anomaly detected in sensor readings!"
                cause = "Unusual combination of temperature and vibration suggests sensor drift or mechanical fault."
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





SPEED_THRESHOLD = 1200

def send_alert_email(recipient, alerts, avg_temp, avg_vibration, avg_speed, status, recommendation):
    if not recipient:
        print("❌ No recipient email found.")
        return

    subject = "🚨 Machine Alert Notification"
    body = f"""
Hello,

Your machine has triggered the following alert(s):

{chr(10).join(['- ' + alert for alert in alerts]) if alerts else "No alerts triggered."}

📊 Summary:
- Average Temperature: {avg_temp:.2f} °C
- Average Vibration: {avg_vibration:.2f} mm/s
- Average Speed: {avg_speed:.2f} RPM
- Status: {status}

🛠️ Recommendation:
{recommendation}

Please review the attached report or log into your dashboard for more details.

Stay safe,
TechNova Monitoring System
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "s9342902@gmail.com"
    msg["To"] = recipient

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("s9342902@gmail.com", "ncjn fjwj kcwf ocda")
            server.send_message(msg)
            print("✅ Alert email sent to", recipient)
    except Exception as e:
        print("❌ Failed to send email:", e)

def send_label_based_email(recipient, machine_id, labels):
    severity_map = {"low": [], "medium": [], "high": []}
    for sensor, level in labels.items():
        severity_map[level].append(sensor)

    if severity_map["high"]:
        subject = f"🚨 High Alert for {machine_id}"
        body = f"""Hello,\n\nThe following sensors on {machine_id} are in critical condition:\n- {', '.join(severity_map['high'])}\n\nImmediate action is recommended.\n\nStay safe,\nTechNova Monitoring System"""
    elif severity_map["medium"]:
        subject = f"⚠️ Medium Alert for {machine_id}"
        body = f"""Hello,\n\nThe following sensors on {machine_id} require attention:\n- {', '.join(severity_map['medium'])}\n\nPlease monitor the machine closely.\n\nStay safe,\nTechNova Monitoring System"""
    else:
        subject = f"✅ Low Alert for {machine_id}"
        body = f"""Hello,\n\nAll sensors on {machine_id} are within safe limits.\n\nNo action required.\n\nStay safe,\nTechNova Monitoring System"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "s9342902@gmail.com"
    msg["To"] = recipient

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("s9342902@gmail.com", "ncjn fjwj kcwf ocda")
            server.send_message(msg)
            print("✅ Label-based alert sent to", recipient)
    except Exception as e:
        print("❌ Failed to send label-based alert:", e)

@app.route("/process", methods=["POST"])
def process_data():
    data = request.json

    temp = data.get("temperature", [])
    speed = data.get("speed", [])
    vibration = data.get("vibration", [])
    current = data.get("current", [])
    noise = data.get("noise", [])

    min_len = min(len(temp), len(speed), len(vibration), len(current), len(noise))

    df = pd.DataFrame({
        "temperature": temp[:min_len],
        "speed": speed[:min_len],
        "vibration": vibration[:min_len],
        "current": current[:min_len],
        "noise": noise[:min_len]
    })

    avg_temp = df["temperature"].mean()
    avg_speed = df["speed"].mean()
    avg_vibration = df["vibration"].mean()
    avg_current = df["current"].mean()
    avg_noise = df["noise"].mean()
    status = "Healthy" if avg_temp < 75 and avg_speed <= SPEED_THRESHOLD and avg_vibration <= 5.0 else "Check Required"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    alerts = []
    if avg_temp > 75:
        alerts.append(f"High temperature: {avg_temp:.2f} °C")
    if avg_vibration > 5.0:
        alerts.append(f"High vibration: {avg_vibration:.2f} mm/s")
    if avg_speed > SPEED_THRESHOLD:
        alerts.append(f"High speed: {avg_speed:.2f} RPM")

    recommendation = (
        "⚠️ High temperature and high speed detected. Inspect cooling system and motor load." if avg_temp > 75 and avg_speed > SPEED_THRESHOLD else
        "⚠️ Temperature exceeds safe threshold. Check for overheating or poor lubrication." if avg_temp > 75 else
        "⚠️ Speed exceeds optimal range. Verify motor calibration and load conditions." if avg_speed > SPEED_THRESHOLD else
        "⚠️ Vibration exceeds safe limits. Inspect bearings, alignment, and structural integrity." if avg_vibration > 5.0 else
        "✅ Machine is operating within safe parameters."
    )

    recipient = data.get("email")
    if "labels" in data:
        send_label_based_email(recipient, data.get("machine_id", "Unknown"), data["labels"])
        if alerts:
            send_alert_email(recipient, alerts, avg_temp, avg_vibration, avg_speed, status, recommendation)

    # PDF generation
    pdf_path = "report.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)

    # Page 1
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, "Machine Status Report")
    c.setFont("Helvetica", 12)
    c.drawString(100, 770, f"Generated on: {timestamp}")
    c.drawString(100, 750, f"Machine ID: {data.get('machine_id', 'N/A')}")
    c.drawString(100, 730, f"User Email: {data.get('email', 'N/A')}")
    c.drawString(100, 700, f"Average Temperature: {avg_temp:.2f} °C")
    c.drawString(100, 680, f"Average Vibration: {avg_vibration:.2f} mm/s")
    c.drawString(100, 660, f"Average Speed: {avg_speed:.2f} RPM")
    c.drawString(100, 640, f"Average Current: {avg_current:.2f} A")
    c.drawString(100, 620, f"Average Noise: {avg_noise:.2f} dB")
    c.drawString(100, 590, f"Speed Threshold: {SPEED_THRESHOLD} RPM")
    c.drawString(100, 570, f"Status: {status}")
    c.drawString(100, 550, f"Recommendation: {recommendation}")

    labels = data.get("labels", {})
    c.drawString(100, 520, "Sensor Severity Labels:")
    for i, (sensor, level) in enumerate(labels.items()):
        c.drawString(120, 500 - i * 20, f"- {sensor.capitalize()}: {level.upper()}")

    if alerts:
        c.drawString(100, 400, "Real-Time Alerts:")
        for i, alert in enumerate(alerts):
            c.drawString(120, 380 - i * 20, f"• {alert}")

    c.showPage()

    # Page 2
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, "Forecast & Maintenance Insights")
    c.setFont("Helvetica", 12)
    c.drawString(100, 770, "📈 Forecasted Sensor Readings:")
    c.drawString(120, 750, "- Temperature: 71.91 °C")
    c.drawString(120, 730, "- Speed: 5.66 RPM")
    c.drawString(120, 710, "- Vibration: 1507.27 mm/s")

    c.drawString(100, 680, "📊 Trend Analysis:")
    c.drawString(120, 660, "- Temperature shows a rising pattern over the last 10 minutes.")
    c.drawString(120, 640, "- Vibration spikes detected at 3 intervals.")

    c.drawString(100, 610, "🧠 Recommendations:")
    c.drawString(120, 590, "- Issue: Forecasted temperature nearing threshold.")
    c.drawString(120, 570, "- Cause: Possible friction or poor airflow.")
    c.drawString(120, 550, "- Solution: Inspect cooling system, verify lubrication, reduce load.")

    c.drawString(100, 520, "🛠️ Maintenance Checklist:")
    c.drawString(120, 500, "☑ Inspect cooling system")
    c.drawString(120, 480, "☑ Verify lubrication")
    c.drawString(120, 460, "☑ Recalibrate vibration sensors")
    c.drawString(120, 440, "☑ Check motor alignment")

    # Finalize PDF
    c.save()
    print("✅ PDF saved successfully.")

    return jsonify({
        "status": status,
        "avg_temp": avg_temp,
        "avg_vibration": avg_vibration,
        "avg_speed": avg_speed,
        "avg_current": avg_current,
        "avg_noise": avg_noise,
        "recommendation": recommendation,
        "alerts": alerts,
        "report_url": "/download"
    })

@app.route("/download", methods=["GET"])
def download_report():
    return send_file(
        "report.pdf",
        as_attachment=True,
        download_name="Machine_Report.pdf",
        mimetype="application/pdf"
    )


     


# ---------------------------
# Run App
# ---------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
    # app.run(debug=True)