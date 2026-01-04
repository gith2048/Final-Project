#!/usr/bin/env python3
"""
Test script for the new retrain-and-predict endpoint
"""
import requests
import json

# Test data
test_data = {
    "temperature": 75.5,
    "raw_vibration": 4.2,
    "smooth_vibration": 3.8,
    "speed": 1200,
    "training_hours": 3
}

def test_retrain_endpoint():
    """Test the retrain-and-predict endpoint"""
    url = "http://localhost:5000/api/retrain-and-predict"
    
    try:
        print("🧪 Testing retrain-and-predict endpoint...")
        print(f"📤 Sending data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, timeout=120)
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Response received:")
            print(f"   Status: {result.get('status')}")
            print(f"   Training info: {result.get('training_info', {})}")
            print(f"   Predictions: {result.get('predictions', {}).get('lstm_forecast', {})}")
            print(f"   Overall condition: {result.get('overall_assessment', {}).get('condition')}")
            
            if result.get('predictions', {}).get('future_timeline'):
                print("   Future timeline predictions:")
                for pred in result['predictions']['future_timeline'][:3]:  # Show first 3
                    print(f"     {pred['time_offset']}: T={pred['temperature']:.1f}°C, V={pred['vibration']:.2f}mm/s, S={pred['speed']:.0f}RPM")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the backend server is running on localhost:5000")
    except requests.exceptions.Timeout:
        print("❌ Request timed out - training may take longer than expected")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_manual_analysis_endpoint():
    """Test the existing manual analysis endpoint for comparison"""
    url = "http://localhost:5000/api/manual-analysis"
    
    # Remove training_hours for this endpoint
    manual_test_data = {k: v for k, v in test_data.items() if k != 'training_hours'}
    
    try:
        print("\n🧪 Testing manual-analysis endpoint for comparison...")
        response = requests.post(url, json=manual_test_data, timeout=30)
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Manual analysis response:")
            print(f"   Status: {result.get('status')}")
            print(f"   Overall condition: {result.get('overall_assessment', {}).get('condition')}")
            print(f"   LSTM forecast: {result.get('predictions', {}).get('lstm_forecast', {})}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_retrain_endpoint()
    test_manual_analysis_endpoint()