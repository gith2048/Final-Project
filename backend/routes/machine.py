from flask import Blueprint, request, jsonify
from models.machine_data import MachineData
from db import db

machine_bp = Blueprint('machine', __name__)

@machine_bp.route('/sensor', methods=['POST'])
def add_sensor_data():
    data = request.get_json()
    entry = MachineData(
        temperature=data['temperature'],
        vibration=data['vibration'],
        current=data['current'],
        noise=data['noise'],
        speed=data['speed']
    )
    db.session.add(entry)
    db.session.commit()
    return jsonify({"message": "Sensor data added"})
