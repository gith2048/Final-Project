#!/usr/bin/env python3
"""
Test script for machine management API endpoints.
Run this after starting the Flask app to test the functionality.
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5000'

def test_machine_management():
    print("🧪 Testing Machine Management API")
    print("=" * 50)
    
    # Test data
    test_user_email = "test@example.com"
    admin_email = "admin@example.com"
    
    test_machine = {
        "name": "Test Production Motor",
        "motor_type": "AC Induction Motor",
        "motor_id": "TEST-001",
        "date_of_purchase": "2023-01-15",
        "purpose": "Main production line motor for manufacturing process",
        "location": "Factory Floor A",
        "user_email": test_user_email
    }
    
    print("1. Testing Add Machine API...")
    try:
        response = requests.post(f"{BASE_URL}/api/machines", json=test_machine)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 201:
            print("   ✅ Machine added successfully!")
            machine_id = response.json().get('machine', {}).get('id')
        else:
            print("   ❌ Failed to add machine")
            return
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection failed. Make sure the Flask app is running on localhost:5000")
        return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    print("\n2. Testing Get User Machines API...")
    try:
        response = requests.get(f"{BASE_URL}/api/machines?user_email={test_user_email}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            machines = response.json().get('machines', [])
            print(f"   ✅ Found {len(machines)} machines for user")
        else:
            print("   ❌ Failed to get user machines")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n3. Manual Approval Required...")
    print("   ℹ️  To approve the machine:")
    print("   1. Open phpMyAdmin")
    print("   2. Go to 'predictive_maintenance2' database")
    print("   3. Open 'machines' table")
    print(f"   4. Find machine with ID {machine_id if 'machine_id' in locals() else 'N/A'}")
    print("   5. Change 'status' from 'pending' to 'approved'")
    print("   6. Save the changes")
    
    print("\n4. Testing Get User Machines (Before Approval)...")
    try:
        response = requests.get(f"{BASE_URL}/api/machines?user_email={test_user_email}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            machines = response.json().get('machines', [])
            approved_machines = [m for m in machines if m.get('status') == 'approved']
            print(f"   ✅ Found {len(approved_machines)} approved machines for user")
            
            if approved_machines:
                print("   📋 Approved machine details:")
                for machine in approved_machines:
                    print(f"      - {machine['name']} ({machine['motor_id']}) - Status: {machine['status']}")
        else:
            print("   ❌ Failed to get user machines")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Machine Management API Test Complete!")
    print("\nNext Steps:")
    print("1. Start the frontend: cd frontend && npm run dev")
    print("2. Login with a test user account")
    print("3. Try adding a machine through the UI")
    print("4. Approve machines manually in phpMyAdmin:")
    print("   - Open phpMyAdmin → predictive_maintenance2 → machines table")
    print("   - Change status from 'pending' to 'approved'")
    print("5. User will see approved machines in their dashboard")

if __name__ == '__main__':
    test_machine_management()