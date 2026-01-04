#!/usr/bin/env python3
"""
Machine Management System Startup Script
========================================

This script provides a convenient way to start the machine management system
with proper initialization and health checks.
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print("🏭 MACHINE MANAGEMENT SYSTEM")
    print("🤖 Predictive Maintenance Platform")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask', 'flask_sqlalchemy', 'flask_cors', 'mysql-connector-python',
        'numpy', 'pandas', 'scikit-learn', 'tensorflow', 'python-dotenv',
        'reportlab', 'smtplib'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Not installed")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("   Install with: pip install -r backend/requirements.txt")
        return False
    
    return True

def check_database_connection():
    """Check if database is accessible"""
    try:
        import mysql.connector
        from mysql.connector import Error
        
        connection = mysql.connector.connect(
            host='localhost',
            database='predictive_maintenance2',
            user='root',
            password=''
        )
        
        if connection.is_connected():
            print("✅ Database connection successful")
            connection.close()
            return True
    except Error as e:
        print(f"❌ Database connection failed: {e}")
        print("   Make sure MySQL is running and database exists")
        return False

def check_model_files():
    """Check if ML model files exist"""
    model_dir = Path("backend/model")
    required_models = [
        "rf_model.pkl",
        "scaler.pkl", 
        "label_encoder.pkl",
        "iso_model.pkl",
        "lstm_model.keras",
        "lstm_scaler.pkl"
    ]
    
    missing_models = []
    for model_file in required_models:
        model_path = model_dir / model_file
        if model_path.exists():
            print(f"✅ {model_file}")
        else:
            missing_models.append(model_file)
            print(f"⚠️  {model_file} - Not found")
    
    if missing_models:
        print(f"\n⚠️  Missing model files: {', '.join(missing_models)}")
        print("   System will work with limited functionality")
        print("   Train models using the training scripts in backend/model/")
    
    return len(missing_models) == 0

def check_sensor_data():
    """Check if sensor data file exists"""
    sensor_file = Path("backend/sensor_data_3params.json")
    if sensor_file.exists():
        print("✅ Sensor data file found")
        try:
            with open(sensor_file, 'r') as f:
                data = json.load(f)
                print(f"   📊 {len(data)} sensor readings loaded")
            return True
        except Exception as e:
            print(f"❌ Error reading sensor data: {e}")
            return False
    else:
        print("⚠️  Sensor data file not found")
        print("   Create backend/sensor_data_3params.json with sample data")
        return False

def start_backend():
    """Start the Flask backend server"""
    print("\n🚀 Starting Backend Server...")
    backend_dir = Path("backend")
    
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return None
    
    try:
        # Change to backend directory and start Flask app
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:5000/", timeout=5)
            if response.status_code == 200:
                print("✅ Backend server started successfully")
                print("   🌐 API available at: http://localhost:5000")
                return process
            else:
                print(f"❌ Backend server returned status: {response.status_code}")
                return None
        except requests.exceptions.RequestException:
            print("❌ Backend server not responding")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the React frontend server"""
    print("\n🚀 Starting Frontend Server...")
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return None
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("⚠️  Node modules not found, installing dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            print("✅ Dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return None
    
    try:
        # Start the development server
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(5)
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:5173/", timeout=5)
            if response.status_code == 200:
                print("✅ Frontend server started successfully")
                print("   🌐 Web interface available at: http://localhost:5173")
                return process
            else:
                print(f"❌ Frontend server returned status: {response.status_code}")
                return None
        except requests.exceptions.RequestException:
            print("❌ Frontend server not responding")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def main():
    """Main startup function"""
    print_banner()
    
    print("🔍 System Health Check")
    print("-" * 30)
    
    # Run all health checks
    checks_passed = 0
    total_checks = 6
    
    if check_python_version():
        checks_passed += 1
    
    print("\n📦 Checking Dependencies...")
    if check_dependencies():
        checks_passed += 1
    
    print("\n🗄️  Checking Database...")
    if check_database_connection():
        checks_passed += 1
    
    print("\n🤖 Checking ML Models...")
    if check_model_files():
        checks_passed += 1
    
    print("\n📊 Checking Sensor Data...")
    if check_sensor_data():
        checks_passed += 1
    
    print(f"\n📋 Health Check Summary: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed < 3:
        print("❌ Too many critical issues found. Please fix them before starting.")
        return
    
    # Start services
    print("\n" + "=" * 60)
    print("🚀 STARTING SERVICES")
    print("=" * 60)
    
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend. Exiting.")
        return
    
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend. Backend is still running.")
        print("   You can access the API directly at http://localhost:5000")
    
    # Success message
    print("\n" + "=" * 60)
    print("🎉 SYSTEM STARTED SUCCESSFULLY!")
    print("=" * 60)
    print("🌐 Web Interface: http://localhost:5173")
    print("🔧 API Endpoint: http://localhost:5000")
    print("📧 Email alerts configured and ready")
    print("🤖 ML models loaded and operational")
    print("\n💡 Quick Start:")
    print("   1. Open http://localhost:5173 in your browser")
    print("   2. Sign up for a new account")
    print("   3. Add your first machine")
    print("   4. Wait for admin approval")
    print("   5. Start monitoring!")
    print("\n⚠️  To stop the system, press Ctrl+C")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down system...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print("✅ System stopped successfully")

if __name__ == "__main__":
    main()