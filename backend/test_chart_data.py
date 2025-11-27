#!/usr/bin/env python3
"""
Test script to verify chart data is correct
Run: python test_chart_data.py
"""

import json
import os

def test_sensor_data():
    print("=" * 70)
    print("TESTING CHART DATA ACCURACY")
    print("=" * 70)
    
    # Find sensor data file
    data_file = os.path.join(os.path.dirname(__file__), "sensor_data_3params.json")
    
    if not os.path.exists(data_file):
        print(f"❌ Sensor data file not found: {data_file}")
        return False
    
    print(f"✅ Found sensor data file: {data_file}\n")
    
    # Load data
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    print(f"📊 Total records: {len(data)}\n")
    
    # Group by machine
    machines = {}
    for record in data:
        machine_id = record.get("machine_id", "Unknown")
        if machine_id not in machines:
            machines[machine_id] = {
                "temperature": [],
                "vibration": [],
                "speed": [],
                "count": 0
            }
        
        machines[machine_id]["temperature"].ap