#!/usr/bin/env python3
"""
Clean sensor data by removing unrealistic values
Run: python clean_sensor_data.py
"""

import json
import os

def clean_sensor_data():
    print("=" * 60)
    print("Cleaning Sensor Data")
    print("=" * 60)
    
    # Read original data
    json_path = os.path.join(os.path.dirname(__file__), "sensor_data_3params.json")
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    print(f"\n📁 Loaded {len(data)} records")
    
    # Clean data
    cleaned_data = []
    issues_fixed = 0
    
    for i, record in enumerate(data):
        temp = record.get("temperature")
        vib = record.get("vibration")
        speed = record.get("speed")
        
        fixed = False
        
        # Fix temperature (should be 20-120°C for industrial machines)
        if temp is not None and temp < 20:
            record["temperature"] = abs(temp) if abs(temp) >= 20 else 20 + abs(temp)
            fixed = True
        elif temp is not None and temp > 120:
            record["temperature"] = 120
            fixed = True
        
        # Fix vibration (should be 0-15 mm/s)
        if vib is not None and vib < 0:
            record["vibration"] = abs(vib)
            fixed = True
        elif vib is not None and vib > 15:
            record["vibration"] = 15
            fixed = True
        
        # Fix speed (should be 0-3000 RPM)
        if speed is not None and speed < 0:
            record["speed"] = abs(speed)
            fixed = True
        elif speed is not None and speed > 3000:
            record["speed"] = 3000
            fixed = True
        
        if fixed:
            issues_fixed += 1
        
        cleaned_data.append(record)
    
    print(f"✅ Fixed {issues_fixed} records with unrealistic values")
    
    # Save cleaned data
    backup_path = json_path.replace(".json", "_backup.json")
    
    # Create backup
    with open(backup_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Backup saved to: {backup_path}")
    
    # Save cleaned data
    with open(json_path, 'w') as f:
        json.dump(cleaned_data, f, indent=2)
    print(f"✅ Cleaned data saved to: {json_path}")
    
    # Verify cleaned data
    print("\n📊 Verifying cleaned data:")
    
    machines = {}
    for record in cleaned_data:
        mid = record.get("machine_id", "Unknown")
        if mid not in machines:
            machines[mid] = {"temperature": [], "vibration": [], "speed": []}
        
        machines[mid]["temperature"].append(record.get("temperature"))
        machines[mid]["vibration"].append(record.get("vibration"))
        machines[mid]["speed"].append(record.get("speed"))
    
    for machine_id, machine_data in machines.items():
        print(f"\n✅ {machine_id}:")
        print(f"   • Temperature: {min(machine_data['temperature']):.2f} - {max(machine_data['temperature']):.2f}°C")
        print(f"   • Vibration: {min(machine_data['vibration']):.2f} - {max(machine_data['vibration']):.2f} mm/s")
        print(f"   • Speed: {min(machine_data['speed']):.2f} - {max(machine_data['speed']):.2f} RPM")
    
    print("\n" + "=" * 60)
    print("✅ DATA CLEANING COMPLETE")
    print("=" * 60)
    print(f"\nSummary:")
    print(f"✅ Records processed: {len(cleaned_data)}")
    print(f"✅ Issues fixed: {issues_fixed}")
    print(f"✅ Backup created: {backup_path}")
    print(f"✅ Data is now clean and realistic")
    
    print("\n🎉 You can now restart the backend and charts will show correct data!")

if __name__ == "__main__":
    try:
        clean_sensor_data()
    except Exception as e:
        print(f"\n❌ Cleaning failed: {e}")
        import traceback
        traceback.print_exc()
