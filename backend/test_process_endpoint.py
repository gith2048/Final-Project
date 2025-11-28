#!/usr/bin/env python3
"""
Test the /process endpoint directly
"""
import requests
import json

# Test data
test_data = {
    "temperature": [70, 71, 72, 73, 74, 75, 76, 77, 78, 79],
    "vibration": [4, 4.5, 4.2, 4.3, 4.1, 4.4, 4.2, 4.3, 4.1, 4.2],
    "speed": [1180, 1190, 1185, 1195, 1188, 1192, 1187, 1190, 1185, 1188],
    "email": "test@example.com",
    "machine_id": "Machine_A"
}

print("Testing /process endpoint...")
print(f"URL: http://localhost:5000/process")
print(f"Data: {json.dumps(test_data, indent=2)}")
print("\n" + "="*60)

try:
    response = requests.post(
        "http://localhost:5000/process",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print("\nResponse Body:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        print("\n✅ SUCCESS - Endpoint working correctly!")
    else:
        print(f"\n❌ ERROR - Status code {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR - Cannot connect to backend")
    print("Make sure the backend is running: python backend/app.py")
except Exception as e:
    print(f"\n❌ ERROR - {e}")
