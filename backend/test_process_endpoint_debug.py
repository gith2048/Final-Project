"""
Test script to debug the /process endpoint
"""
import requests
import json

# Test data
test_data = {
    "machine_id": "Machine_1",
    "email": "test@example.com",
    "temperature": [70, 72, 75, 78, 80, 82, 85, 87, 90, 92],
    "vibration": [3.5, 3.8, 4.0, 4.2, 4.5, 4.8, 5.0, 5.2, 5.5, 5.8],
    "speed": [1100, 1120, 1140, 1160, 1180, 1200, 1220, 1240, 1260, 1280]
}

print("🧪 Testing /process endpoint...")
print(f"📊 Sending data: {json.dumps(test_data, indent=2)}")

try:
    response = requests.post(
        "http://localhost:5000/process",
        json=test_data,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f"\n📡 Response Status: {response.status_code}")
    print(f"📋 Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print(f"✅ Success! Response:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Error Response:")
        print(response.text)
        
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
