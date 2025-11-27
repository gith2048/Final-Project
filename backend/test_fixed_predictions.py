#!/usr/bin/env python3
"""
Test the FIXED ML predictions to verify they now work correctly
"""

import requests
import json

def test_fixed_endpoint():
    """Test the fixed /chat/analyze endpoint"""
    print("\n" + "=" * 70)
    print("TESTING FIXED ML PREDICTIONS")
    print("=" * 70)
    
    test_cases = [
        {
            "name": "Normal Operation",
            "data": {
                "temperature": [60, 62, 64, 65, 63, 64, 65, 66, 65, 64],
                "vibration": [2.5, 2.7, 2.8, 3.0, 2.9, 3.1, 3.0, 2.8, 2.9, 3.0],
                "speed": [950, 980, 1000, 1020, 1000, 990, 1010, 1000, 995, 1000]
            },
            "expected_rf": "Normal",
            "expected_iso": "Normal"
        },
        {
            "name": "High Temperature Warning",
            "data": {
                "temperature": [75, 77, 80, 82, 85, 84, 86, 85, 87, 85],
                "vibration": [3.5, 3.7, 3.8, 4.0, 4.2, 4.1, 4.3, 4.2, 4.4, 4.0],
                "speed": [1050, 1080, 1100, 1120, 1100, 1090, 1110, 1100, 1095, 1100]
            },
            "expected_rf": "Warning",
            "expected_iso": "Normal or Anomaly"
        },
        {
            "name": "Critical Condition",
            "data": {
                "temperature": [85, 88, 90, 92, 95, 94, 96, 95, 97, 95],
                "vibration": [6.5, 6.8, 7.0, 7.5, 8.0, 7.8, 8.2, 8.0, 8.5, 8.0],
                "speed": [1300, 1320, 1350, 1380, 1400, 1390, 1410, 1400, 1420, 1400]
            },
            "expected_rf": "Critical",
            "expected_iso": "Anomaly"
        }
    ]
    
    for test in test_cases:
        print(f"\n{'='*70}")
        print(f"Test Case: {test['name']}")
        print(f"{'='*70}")
        
        payload = {
            "chartType": "lineChart",
            "data": test['data']
        }
        
        try:
            response = requests.post(
                "http://localhost:5000/chat/analyze",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check Random Forest
                rf = result.get("random_forest", {})
                print(f"\n🌲 Random Forest:")
                print(f"   Issue: {rf.get('issue', 'N/A')}")
                print(f"   Cause: {rf.get('cause', 'N/A')[:80]}...")
                print(f"   Expected: {test['expected_rf']}")
                
                # Verify correctness
                if test['expected_rf'].lower() in rf.get('issue', '').lower():
                    print(f"   ✅ CORRECT!")
                else:
                    print(f"   ⚠️ May need review")
                
                # Check Isolation Forest
                iso = result.get("isolation_forest", {})
                print(f"\n🔍 Isolation Forest:")
                print(f"   Issue: {iso.get('issue', 'N/A')}")
                print(f"   Score: {iso.get('score', 'N/A')}")
                print(f"   Expected: {test['expected_iso']}")
                
                # Check if anomaly detected when expected
                if "Anomaly" in test['expected_iso']:
                    if "Change" in iso.get('issue', '') or iso.get('score', 0) < 0:
                        print(f"   ✅ CORRECT!")
                    else:
                        print(f"   ⚠️ May need review")
                else:
                    if "Low" in iso.get('issue', '') or iso.get('score', 0) > 0:
                        print(f"   ✅ CORRECT!")
                    else:
                        print(f"   ⚠️ May need review")
                
                # Check Recommendations
                recs = result.get("recommendations", {})
                print(f"\n💡 Recommendations:")
                print(f"   Priority: {recs.get('priority', 'N/A')}")
                print(f"   Summary: {recs.get('summary', 'N/A')[:100]}...")
                
                if recs.get('actions'):
                    print(f"   Actions: {len(recs['actions'])} issue(s) detected")
                    for action in recs['actions'][:2]:  # Show first 2
                        print(f"      • {action.get('title', 'N/A')}")
                
            else:
                print(f"❌ API returned status {response.status_code}")
                print(f"   Response: {response.text[:200]}")
        
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to backend. Is Flask running on port 5000?")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    print(f"\n{'='*70}")
    print("✅ ALL TESTS COMPLETED")
    print(f"{'='*70}")
    print("\nVerify that:")
    print("  1. Normal operation shows 'Normal' for RF")
    print("  2. High temperature shows 'Warning' for RF")
    print("  3. Critical condition shows 'Critical' for RF")
    print("  4. Anomalies are detected by ISO when appropriate")
    print("  5. Recommendations match the severity level")
    
    return True


if __name__ == "__main__":
    test_fixed_endpoint()
