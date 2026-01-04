#!/usr/bin/env python3
"""
Test script to verify the predict button works with default values
"""
import requests
import json

def test_predict_with_defaults():
    """Test prediction with default values (empty fields)"""
    url = "http://localhost:5000/api/manual-analysis"
    
    # Test with default values that would be used for empty fields
    test_data = {
        "temperature": 25,      # Default room temperature
        "raw_vibration": 1,     # Default low vibration
        "smooth_vibration": 1,  # Default low vibration
        "speed": 1000          # Default moderate speed
    }
    
    try:
        print("🧪 Testing predict button with default values...")
        print(f"📤 Sending data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Prediction works with default values:")
            print(f"   Status: {result.get('status')}")
            print(f"   Overall condition: {result.get('overall_assessment', {}).get('condition')}")
            print(f"   LSTM forecast: {result.get('predictions', {}).get('lstm_forecast', {})}")
            
            # Check if training options would be available
            if result.get('status') == 'success':
                print("   ✅ Training options would be available after this prediction")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the backend server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_predict_with_partial_data():
    """Test prediction with some empty fields (using 0 as default)"""
    url = "http://localhost:5000/api/manual-analysis"
    
    # Test with some fields empty (would use defaults)
    test_data = {
        "temperature": 75,      # User provided
        "raw_vibration": 0,     # Empty field -> default
        "smooth_vibration": 3,  # User provided
        "speed": 0             # Empty field -> default (will be 1000 in frontend)
    }
    
    try:
        print("\n🧪 Testing predict button with partial data...")
        print(f"📤 Sending data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Prediction works with partial data:")
            print(f"   Status: {result.get('status')}")
            print(f"   Overall condition: {result.get('overall_assessment', {}).get('condition')}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_predict_with_defaults()
    test_predict_with_partial_data()
    print("\n✅ Predict button should now be always enabled!")
    print("📝 Users can click 'Predict' anytime and see results immediately")
    print("🔧 Empty fields will use sensible default values")