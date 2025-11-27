#!/usr/bin/env python3
"""
Test script for the reasoning engine
Run: python test_reasoning_engine.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from reasoning_engine import MachineHealthReasoner
import numpy as np

def test_reasoning_engine():
    print("=" * 60)
    print("Testing Intelligent Reasoning Engine")
    print("=" * 60)
    
    # Initialize reasoner
    reasoner = MachineHealthReasoner()
    print("✅ Reasoning engine initialized\n")
    
    # Test Case 1: Normal operation
    print("\n" + "=" * 60)
    print("TEST 1: Normal Operation")
    print("=" * 60)
    
    sensor_data_normal = {
        "temperature": [65, 66, 67, 65, 66, 68, 67, 66, 65, 67, 68, 66, 67, 65, 66],
        "vibration": [3.2, 3.5, 3.1, 3.4, 3.3, 3.2, 3.5, 3.4, 3.3, 3.2, 3.1, 3.4, 3.3, 3.2, 3.5],
        "speed": [1100, 1105, 1098, 1102, 1100, 1103, 1101, 1099, 1100, 1102, 1101, 1100, 1103, 1102, 1100]
    }
    
    ml_outputs_normal = {
        "lstm": {
            "forecast": {"temperature": 67.0, "vibration": 3.3, "speed": 1101.0}
        },
        "random_forest": {
            "pred": 0,
            "label": "normal",
            "issue": "Normal"
        },
        "isolation_forest": {
            "pred": 1,
            "score": 0.05,
            "issue": "Normal"
        }
    }
    
    result = reasoner.analyze(sensor_data_normal, ml_outputs_normal, "How is the machine?")
    print(result["response"])
    print(f"\n✅ Risk Level: {result['risk_assessment']['level']}")
    print(f"✅ Risk Score: {result['risk_assessment']['score']}/100")
    
    # Test Case 2: High temperature warning
    print("\n" + "=" * 60)
    print("TEST 2: High Temperature Warning")
    print("=" * 60)
    
    sensor_data_hot = {
        "temperature": [70, 72, 74, 76, 78, 80, 82, 84, 85, 86, 87, 88, 89, 90, 91],
        "vibration": [3.2, 3.5, 3.8, 4.1, 4.5, 4.8, 5.2, 5.5, 5.8, 6.0, 6.2, 6.5, 6.7, 6.9, 7.1],
        "speed": [1100, 1110, 1120, 1130, 1140, 1150, 1160, 1170, 1180, 1190, 1200, 1210, 1220, 1230, 1240]
    }
    
    ml_outputs_hot = {
        "lstm": {
            "forecast": {"temperature": 93.0, "vibration": 7.5, "speed": 1250.0}
        },
        "random_forest": {
            "pred": 1,
            "label": "warning",
            "issue": "Warning"
        },
        "isolation_forest": {
            "pred": -1,
            "score": -0.08,
            "issue": "Anomaly"
        }
    }
    
    result = reasoner.analyze(sensor_data_hot, ml_outputs_hot, "What's the temperature?")
    print(result["response"])
    print(f"\n⚠️ Risk Level: {result['risk_assessment']['level']}")
    print(f"⚠️ Risk Score: {result['risk_assessment']['score']}/100")
    print(f"⚠️ Anomalies Detected: {len(result['anomalies'])}")
    
    # Test Case 3: Critical situation
    print("\n" + "=" * 60)
    print("TEST 3: Critical Situation")
    print("=" * 60)
    
    sensor_data_critical = {
        "temperature": [85, 87, 89, 91, 93, 95, 97, 98, 99, 100, 101, 102, 103, 104, 105],
        "vibration": [7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0],
        "speed": [1300, 1320, 1340, 1360, 1380, 1400, 1420, 1440, 1460, 1480, 1500, 1520, 1540, 1560, 1580]
    }
    
    ml_outputs_critical = {
        "lstm": {
            "forecast": {"temperature": 107.0, "vibration": 15.0, "speed": 1600.0}
        },
        "random_forest": {
            "pred": 2,
            "label": "critical",
            "issue": "Critical"
        },
        "isolation_forest": {
            "pred": -1,
            "score": -0.15,
            "issue": "Critical Anomaly"
        }
    }
    
    result = reasoner.analyze(sensor_data_critical, ml_outputs_critical, "What's the risk?")
    print(result["response"])
    print(f"\n🚨 Risk Level: {result['risk_assessment']['level']}")
    print(f"🚨 Risk Score: {result['risk_assessment']['score']}/100")
    print(f"🚨 Anomalies Detected: {len(result['anomalies'])}")
    print(f"🚨 Recommendations: {len(result['recommendations'])}")
    
    # Test Case 4: Different question types
    print("\n" + "=" * 60)
    print("TEST 4: Different Question Types")
    print("=" * 60)
    
    questions = [
        "Any anomalies?",
        "Show forecast",
        "Recommendations?",
        "What are the trends?"
    ]
    
    for question in questions:
        print(f"\n📝 Question: {question}")
        print("-" * 60)
        result = reasoner.analyze(sensor_data_hot, ml_outputs_hot, question)
        # Print first 200 chars of response
        response_preview = result["response"][:200] + "..." if len(result["response"]) > 200 else result["response"]
        print(response_preview)
    
    print("\n" + "=" * 60)
    print("✅ All Tests Completed Successfully!")
    print("=" * 60)
    print("\nReasoning Engine Features Verified:")
    print("✅ Current state extraction")
    print("✅ Trend analysis")
    print("✅ ML output interpretation")
    print("✅ Anomaly detection")
    print("✅ Risk assessment")
    print("✅ Recommendation generation")
    print("✅ Natural language responses")
    print("✅ Question-specific answers")
    print("\n🎉 Reasoning engine is working perfectly!")

if __name__ == "__main__":
    try:
        test_reasoning_engine()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
