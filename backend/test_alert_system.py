#!/usr/bin/env python3
"""
Test script for alert system
Tests email sending and PDF generation
"""

from alert_system import process_sensor_data

# Test data with CRITICAL conditions
test_data_critical = {
    "temperature": [90, 92, 95, 88, 91, 93, 96, 94, 92, 95],  # High temps
    "vibration": [8, 9, 10, 11, 9, 10, 12, 11, 10, 9],  # High vibration
    "speed": [1400, 1450, 1500, 1480, 1460, 1490, 1510, 1500, 1480, 1470],  # High speed
    "email": "test@example.com",  # Replace with your email for testing
    "machine_id": "Machine_A"
}

# Test data with NORMAL conditions
test_data_normal = {
    "temperature": [70, 71, 69, 72, 70, 71, 70, 69, 71, 70],  # Normal temps
    "vibration": [4, 4.5, 4.2, 4.3, 4.1, 4.4, 4.2, 4.3, 4.1, 4.2],  # Normal vibration
    "speed": [1180, 1190, 1185, 1195, 1188, 1192, 1187, 1190, 1185, 1188],  # Normal speed
    "email": "test@example.com",  # Replace with your email for testing
    "machine_id": "Machine_B"
}

def test_critical_alert():
    print("\n" + "="*60)
    print("TEST 1: CRITICAL CONDITION")
    print("="*60)
    result = process_sensor_data(test_data_critical)
    
    print(f"\nStatus: {result['status']}")
    print(f"Avg Temperature: {result['avg_temp']:.2f}°C")
    print(f"Avg Vibration: {result['avg_vibration']:.2f} mm/s")
    print(f"Avg Speed: {result['avg_speed']:.0f} RPM")
    print(f"\nAlerts ({len(result['alerts'])}):")
    for alert in result['alerts']:
        print(f"  - {alert}")
    print(f"\nRecommendation: {result['recommendation']}")
    print(f"Email Sent: {result.get('email_sent', False)}")
    print(f"PDF Report: {result.get('report_url', 'Not generated')}")

def test_normal_condition():
    print("\n" + "="*60)
    print("TEST 2: NORMAL CONDITION")
    print("="*60)
    result = process_sensor_data(test_data_normal)
    
    print(f"\nStatus: {result['status']}")
    print(f"Avg Temperature: {result['avg_temp']:.2f}°C")
    print(f"Avg Vibration: {result['avg_vibration']:.2f} mm/s")
    print(f"Avg Speed: {result['avg_speed']:.0f} RPM")
    print(f"\nAlerts ({len(result['alerts'])}):")
    if result['alerts']:
        for alert in result['alerts']:
            print(f"  - {alert}")
    else:
        print("  No alerts - Machine healthy!")
    print(f"\nRecommendation: {result['recommendation']}")
    print(f"Email Sent: {result.get('email_sent', False)}")
    print(f"PDF Report: {result.get('report_url', 'Not generated')}")

if __name__ == "__main__":
    print("\n🧪 ALERT SYSTEM TEST SUITE")
    print("="*60)
    print("NOTE: Update email addresses in test data before running")
    print("="*60)
    
    # Run tests
    test_critical_alert()
    test_normal_condition()
    
    print("\n" + "="*60)
    print("✅ TESTS COMPLETE")
    print("="*60)
    print("\nCheck your email inbox for alert notifications!")
    print("Check current directory for 'report.pdf' file")
