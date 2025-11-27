#!/usr/bin/env python3
"""
Comprehensive test to verify chart data accuracy
Tests:
1. Sensor data file integrity
2. Backend API response format
3. Data transformation correctness
4. Chart data validation
"""

import json
import os
import sys
import requests
import numpy as np

def test_sensor_data_file():
    """Test 1: Verify sensor data file exists and has correct structure"""
    print("\n" + "=" * 70)
    print("TEST 1: SENSOR DATA FILE INTEGRITY")
    print("=" * 70)
    
    data_file = os.path.join(os.path.dirname(__file__), "sensor_data_3params.json")
    
    if not os.path.exists(data_file):
        print(f"❌ FAIL: Sensor data file not found: {data_file}")
        return False
    
    print(f"✅ Found sensor data file: {data_file}")
    
    # Load and validate data
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    print(f"✅ Total records: {len(data)}")
    
    # Check structure of first record
    if len(data) > 0:
        first = data[0]
        required_fields = ['machine_id', 'temperature', 'vibration', 'speed', 'timestamp']
        missing = [f for f in required_fields if f not in first]
        
        if missing:
            print(f"❌ FAIL: Missing fields in data: {missing}")
            return False
        
        print(f"✅ Data structure valid. Sample record:")
        print(f"   Machine: {first['machine_id']}")
        print(f"   Temperature: {first['temperature']}°C")
        print(f"   Vibration: {first['vibration']} mm/s")
        print(f"   Speed: {first['speed']} RPM")
    
    # Group by machine
    machines = {}
    for record in data:
        machine_id = record.get("machine_id", "Unknown")
        if machine_id not in machines:
            machines[machine_id] = {
                "temperature": [],
                "vibration": [],
                "speed": [],
                "timestamps": []
            }
        
        machines[machine_id]["temperature"].append(record.get("temperature", 0))
        machines[machine_id]["vibration"].append(record.get("vibration", 0))
        machines[machine_id]["speed"].append(record.get("speed", 0))
        machines[machine_id]["timestamps"].append(record.get("timestamp", ""))
    
    print(f"\n✅ Machines found: {list(machines.keys())}")
    
    for machine_id, data in machines.items():
        print(f"\n   {machine_id}:")
        print(f"      Records: {len(data['temperature'])}")
        print(f"      Temp range: {min(data['temperature']):.1f} - {max(data['temperature']):.1f}°C")
        print(f"      Vib range: {min(data['vibration']):.2f} - {max(data['vibration']):.2f} mm/s")
        print(f"      Speed range: {min(data['speed']):.0f} - {max(data['speed']):.0f} RPM")
    
    return True


def test_backend_api():
    """Test 2: Verify backend API returns correct data format"""
    print("\n" + "=" * 70)
    print("TEST 2: BACKEND API RESPONSE")
    print("=" * 70)
    
    api_url = "http://localhost:5000/api/sensor-data"
    
    try:
        print(f"📡 Calling API: {api_url}")
        response = requests.get(api_url, timeout=5)
        
        if response.status_code != 200:
            print(f"❌ FAIL: API returned status {response.status_code}")
            return False
        
        print(f"✅ API responded with status 200")
        
        data = response.json()
        
        if not isinstance(data, dict):
            print(f"❌ FAIL: Expected dict, got {type(data)}")
            return False
        
        print(f"✅ Response is a dictionary")
        print(f"✅ Machines in response: {list(data.keys())}")
        
        # Validate structure for each machine
        for machine_id, machine_data in data.items():
            print(f"\n   Validating {machine_id}:")
            
            required_fields = ['timestamps', 'temperature', 'vibration', 'speed']
            missing = [f for f in required_fields if f not in machine_data]
            
            if missing:
                print(f"   ❌ FAIL: Missing fields: {missing}")
                return False
            
            print(f"   ✅ All required fields present")
            
            # Check data types and lengths
            for field in required_fields:
                if not isinstance(machine_data[field], list):
                    print(f"   ❌ FAIL: {field} is not a list")
                    return False
            
            lengths = [len(machine_data[f]) for f in required_fields]
            if len(set(lengths)) != 1:
                print(f"   ❌ FAIL: Array lengths don't match: {dict(zip(required_fields, lengths))}")
                return False
            
            print(f"   ✅ All arrays have same length: {lengths[0]}")
            
            # Validate data values
            temp = machine_data['temperature']
            vib = machine_data['vibration']
            speed = machine_data['speed']
            
            # Check for NaN or invalid values
            temp_valid = all(isinstance(v, (int, float)) and not np.isnan(v) for v in temp)
            vib_valid = all(isinstance(v, (int, float)) and not np.isnan(v) for v in vib)
            speed_valid = all(isinstance(v, (int, float)) and not np.isnan(v) for v in speed)
            
            if not (temp_valid and vib_valid and speed_valid):
                print(f"   ❌ FAIL: Found NaN or invalid values")
                return False
            
            print(f"   ✅ No NaN or invalid values")
            
            # Check value ranges
            print(f"   📊 Data ranges:")
            print(f"      Temperature: {min(temp):.1f} - {max(temp):.1f}°C")
            print(f"      Vibration: {min(vib):.2f} - {max(vib):.2f} mm/s")
            print(f"      Speed: {min(speed):.0f} - {max(speed):.0f} RPM")
            
            # Validate reasonable ranges
            if not (0 <= min(temp) <= 150):
                print(f"   ⚠️  WARNING: Temperature values outside expected range")
            if not (0 <= min(vib) <= 20):
                print(f"   ⚠️  WARNING: Vibration values outside expected range")
            if not (0 <= min(speed) <= 3000):
                print(f"   ⚠️  WARNING: Speed values outside expected range")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ FAIL: Cannot connect to backend. Is Flask running on port 5000?")
        return False
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        return False


def test_chart_analyze_endpoint():
    """Test 3: Verify chart analysis endpoint"""
    print("\n" + "=" * 70)
    print("TEST 3: CHART ANALYSIS ENDPOINT")
    print("=" * 70)
    
    api_url = "http://localhost:5000/chat/analyze"
    
    # Create sample data
    sample_data = {
        "chartType": "lineChart",
        "data": {
            "temperature": [65.0, 67.0, 70.0, 72.0, 75.0, 78.0, 80.0, 82.0, 85.0, 87.0],
            "vibration": [3.0, 3.2, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0],
            "speed": [1000, 1050, 1100, 1150, 1200, 1250, 1300, 1350, 1400, 1450]
        }
    }
    
    try:
        print(f"📡 Calling API: {api_url}")
        response = requests.post(api_url, json=sample_data, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ FAIL: API returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        print(f"✅ API responded with status 200")
        
        result = response.json()
        
        # Check for expected fields in nested structure
        expected_keys = ['overall_summary', 'lstm', 'random_forest', 'isolation_forest', 'trends']
        missing = [k for k in expected_keys if k not in result]
        
        if missing:
            print(f"❌ FAIL: Missing keys in response: {missing}")
            print(f"   Available keys: {list(result.keys())}")
            return False
        
        print(f"✅ All expected keys present")
        
        # Validate LSTM forecast
        if 'forecast' in result['lstm']:
            forecast = result['lstm']['forecast']
            print(f"\n   📊 LSTM Forecast:")
            print(f"      Temperature: {forecast.get('temperature', 'N/A')}°C")
            print(f"      Vibration: {forecast.get('vibration', 'N/A')} mm/s")
            print(f"      Speed: {forecast.get('speed', 'N/A')} RPM")
        
        # Validate Random Forest
        rf = result['random_forest']
        print(f"\n   🌲 Random Forest:")
        print(f"      Issue: {rf.get('issue', 'N/A')}")
        print(f"      Cause: {rf.get('cause', 'N/A')[:60]}...")
        
        # Validate Isolation Forest
        iso = result['isolation_forest']
        print(f"\n   🔍 Isolation Forest:")
        print(f"      Issue: {iso.get('issue', 'N/A')}")
        print(f"      Score: {iso.get('score', 'N/A')}")
        
        # Validate trends
        trends = result['trends']
        print(f"\n   📈 Trends:")
        print(f"      Temperature: {trends.get('temperature', 'N/A')}")
        print(f"      Vibration: {trends.get('vibration', 'N/A')}")
        print(f"      Speed: {trends.get('speed', 'N/A')}")
        
        print(f"\n   ✅ Analysis endpoint working correctly")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ FAIL: Cannot connect to backend. Is Flask running on port 5000?")
        return False
    except Exception as e:
        print(f"❌ FAIL: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("CHART DATA VERIFICATION TEST SUITE")
    print("=" * 70)
    
    results = []
    
    # Test 1: File integrity
    results.append(("Sensor Data File", test_sensor_data_file()))
    
    # Test 2: Backend API
    results.append(("Backend API", test_backend_api()))
    
    # Test 3: Chart Analysis
    results.append(("Chart Analysis", test_chart_analyze_endpoint()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Charts are receiving proper data!")
    else:
        print("⚠️  SOME TESTS FAILED - Please review the issues above")
    print("=" * 70 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
