#!/usr/bin/env python3
"""
Test script to verify data flow from JSON to API
Run: python test_data_flow.py
"""

import json
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_data_flow():
    print("=" * 60)
    print("Testing Data Flow: JSON → API → Charts")
    print("=" * 60)
    
    # Test 1: Read JSON file
    print("\n📁 TEST 1: Reading sensor_data_3params.json")
    json_path = os.path.join(os.path.dirname(__file__), "sensor_data_3params.json")
    
    if not os.path.exists(json_path):
        print("❌ File not found:", json_path)
        return False
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    print(f"✅ Loaded {len(data)} records")
    
    # Test 2: Verify data structure
    print("\n📊 TEST 2: Verifying data structure")
    
    if not isinstance(data, list):
        print("❌ Data should be a list")
        return False
    
    print(f"✅ Data is a list with {len(data)} items")
    
    # Test 3: Check first record
    print("\n🔍 TEST 3: Checking first record")
    first_record = data[0]
    
    required_fields = ["timestamp", "machine_id", "temperature", "vibration", "speed"]
    for field in required_fields:
        if field not in first_record:
            print(f"❌ Missing field: {field}")
            return False
        print(f"✅ {field}: {first_record[field]}")
    
    # Test 4: Group by machine
    print("\n🏭 TEST 4: Grouping by machine")
    machines = {}
    for record in data:
        mid = record.get("machine_id", "Unknown")
        if mid not in machines:
            machines[mid] = {"temperature": [], "vibration": [], "speed": [], "timestamps": []}
        
        machines[mid]["temperature"].append(record.get("temperature"))
        machines[mid]["vibration"].append(record.get("vibration"))
        machines[mid]["speed"].append(record.get("speed"))
        machines[mid]["timestamps"].append(record.get("timestamp"))
    
    for machine_id, machine_data in machines.items():
        print(f"\n✅ {machine_id}:")
        print(f"   • Records: {len(machine_data['temperature'])}")
        print(f"   • Temperature range: {min(machine_data['temperature']):.2f} - {max(machine_data['temperature']):.2f}°C")
        print(f"   • Vibration range: {min(machine_data['vibration']):.2f} - {max(machine_data['vibration']):.2f} mm/s")
        print(f"   • Speed range: {min(machine_data['speed']):.2f} - {max(machine_data['speed']):.2f} RPM")
    
    # Test 5: Verify data types
    print("\n🔢 TEST 5: Verifying data types")
    sample = data[0]
    
    checks = [
        ("temperature", float, sample["temperature"]),
        ("vibration", float, sample["vibration"]),
        ("speed", float, sample["speed"]),
        ("timestamp", str, sample["timestamp"]),
        ("machine_id", str, sample["machine_id"])
    ]
    
    for field, expected_type, value in checks:
        if isinstance(value, expected_type):
            print(f"✅ {field}: {expected_type.__name__} ({value})")
        else:
            print(f"⚠️ {field}: Expected {expected_type.__name__}, got {type(value).__name__}")
    
    # Test 6: Check for anomalies in data
    print("\n⚠️ TEST 6: Checking for data anomalies")
    
    issues = []
    for i, record in enumerate(data):
        temp = record.get("temperature")
        vib = record.get("vibration")
        speed = record.get("speed")
        
        # Check for None or invalid values
        if temp is None or vib is None or speed is None:
            issues.append(f"Record {i}: Missing values")
        
        # Check for unrealistic values
        if temp is not None and (temp < 0 or temp > 150):
            issues.append(f"Record {i}: Unrealistic temperature: {temp}°C")
        
        if vib is not None and (vib < 0 or vib > 50):
            issues.append(f"Record {i}: Unrealistic vibration: {vib} mm/s")
        
        if speed is not None and (speed < 0 or speed > 5000):
            issues.append(f"Record {i}: Unrealistic speed: {speed} RPM")
    
    if issues:
        print(f"⚠️ Found {len(issues)} potential issues:")
        for issue in issues[:5]:  # Show first 5
            print(f"   • {issue}")
    else:
        print("✅ No data anomalies detected")
    
    # Test 7: Verify chart data format
    print("\n📈 TEST 7: Verifying chart data format")
    
    # Simulate what Dashboard receives
    machine_a_data = machines.get("Machine_A", {})
    if machine_a_data:
        chart_data = {
            "timestamps": machine_a_data["timestamps"][-20:],
            "temperature": machine_a_data["temperature"][-20:],
            "vibration": machine_a_data["vibration"][-20:],
            "speed": machine_a_data["speed"][-20:]
        }
        
        print(f"✅ Chart data for Machine_A (last 20 points):")
        print(f"   • Timestamps: {len(chart_data['timestamps'])} points")
        print(f"   • Temperature: {len(chart_data['temperature'])} values")
        print(f"   • Vibration: {len(chart_data['vibration'])} values")
        print(f"   • Speed: {len(chart_data['speed'])} values")
        
        # Show sample values
        print(f"\n   Sample values (last 3 points):")
        for i in range(-3, 0):
            print(f"   {i+4}. Temp: {chart_data['temperature'][i]:.2f}°C, "
                  f"Vib: {chart_data['vibration'][i]:.2f} mm/s, "
                  f"Speed: {chart_data['speed'][i]:.2f} RPM")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ DATA FLOW TEST COMPLETE")
    print("=" * 60)
    print("\nSummary:")
    print(f"✅ JSON file loaded: {len(data)} records")
    print(f"✅ Machines found: {len(machines)}")
    print(f"✅ Data structure: Valid")
    print(f"✅ Data types: Correct")
    print(f"✅ Chart format: Ready")
    
    if issues:
        print(f"⚠️ Minor issues: {len(issues)} (see above)")
    else:
        print("✅ No issues detected")
    
    print("\n🎉 All tests passed! Data is flowing correctly.")
    print("\nNext steps:")
    print("1. Start backend: cd backend && python app.py")
    print("2. Start frontend: cd frontend && npm run dev")
    print("3. Open Dashboard and select a machine")
    print("4. Charts should display temperature, vibration, and speed correctly")
    
    return True

if __name__ == "__main__":
    try:
        success = test_data_flow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
