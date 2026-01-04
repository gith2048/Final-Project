#!/usr/bin/env python3
"""
Test script for the manual analysis endpoint
"""
import requests
import json

def test_manual_analysis():
    """Test the manual analysis endpoint with sample data"""
    
    # Test data
    test_cases = [
        {
            "name": "Normal Operation",
            "data": {
                "temperature": 60.0,
                "vibration": 2.5,
                "speed": 1100.0
            }
        },
        {
            "name": "Warning Condition",
            "data": {
                "temperature": 80.0,
                "vibration": 5.5,
                "speed": 1250.0
            }
        },
        {
            "name": "Critical Condition",
            "data": {
                "temperature": 95.0,
                "vibration": 8.5,
                "speed": 1400.0
            }
        }
    ]
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Manual Analysis Endpoint")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\n📊 Test Case: {test_case['name']}")
        print(f"Input: {test_case['data']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/manual-analysis",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Status: {result['status']}")
                print(f"🔍 Overall Condition: {result['overall_assessment']['condition']}")
                print(f"⚡ Priority: {result['overall_assessment']['priority']}")
                
                if result.get('predictions', {}).get('lstm_forecast'):
                    forecast = result['predictions']['lstm_forecast']
                    print(f"🔮 LSTM Forecast:")
                    print(f"   Temperature: {forecast['temperature']:.2f}°C")
                    print(f"   Vibration: {forecast['vibration']:.2f} mm/s")
                    print(f"   Speed: {forecast['speed']:.2f} RPM")
                
                if result.get('parameter_analysis'):
                    print(f"⚠️ Parameter Issues: {len(result['parameter_analysis'])}")
                    for param in result['parameter_analysis']:
                        print(f"   - {param['parameter']}: {param['status']} ({param['message']})")
                
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error: {e}")
            print("💡 Make sure the backend server is running on http://localhost:5000")
        
        print("-" * 30)

if __name__ == "__main__":
    test_manual_analysis()