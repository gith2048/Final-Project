#!/usr/bin/env python3
"""
Test script for the dual vibration analysis endpoint
"""
import requests
import json

def test_dual_vibration_analysis():
    """Test the manual analysis endpoint with dual vibration data"""
    
    # Test data with different raw and smooth vibration values
    test_cases = [
        {
            "name": "Normal Operation - Similar Vibrations",
            "data": {
                "temperature": 60.0,
                "raw_vibration": 2.5,
                "smooth_vibration": 2.3,
                "speed": 1100.0
            }
        },
        {
            "name": "High Variance - Raw vs Smooth",
            "data": {
                "temperature": 70.0,
                "raw_vibration": 6.5,
                "smooth_vibration": 3.2,
                "speed": 1200.0
            }
        },
        {
            "name": "Critical Condition - Both High",
            "data": {
                "temperature": 85.0,
                "raw_vibration": 9.5,
                "smooth_vibration": 8.8,
                "speed": 1350.0
            }
        },
        {
            "name": "Smooth Higher Than Raw",
            "data": {
                "temperature": 75.0,
                "raw_vibration": 4.2,
                "smooth_vibration": 5.8,
                "speed": 1250.0
            }
        }
    ]
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Dual Vibration Analysis Endpoint")
    print("=" * 60)
    
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
                
                # Display input values
                input_vals = result['input_values']
                print(f"📥 Input Values:")
                print(f"   Temperature: {input_vals['temperature']}°C")
                print(f"   Raw Vibration: {input_vals['raw_vibration']} mm/s")
                print(f"   Smooth Vibration: {input_vals['smooth_vibration']} mm/s")
                print(f"   Speed: {input_vals['speed']} RPM")
                
                # Display chart data
                chart_data = result['chart_data']
                print(f"📊 Chart Data:")
                for i, label in enumerate(chart_data['parameter_labels']):
                    actual = chart_data['actual_values'][i]
                    predicted = chart_data['predicted_values'][i]
                    print(f"   {label}: Actual={actual:.2f}, Predicted={predicted:.2f}")
                
                # Display parameter analysis
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
        
        print("-" * 40)

if __name__ == "__main__":
    test_dual_vibration_analysis()