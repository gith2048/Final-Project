#!/usr/bin/env python3
"""
Startup script for the Machine Management System.
This script helps set up and start the complete system.
"""

import os
import sys
import subprocess
import time
import requests

def check_python():
    """Check if Python is available"""
    try:
        result = subprocess.run([sys.executable, '--version'], capture_output=True, text=True)
        print(f"✅ Python: {result.stdout.strip()}")
        return True
    except:
        print("❌ Python not found")
        return False

def check_node():
    """Check if Node.js is available"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        print(f"✅ Node.js: {result.stdout.strip()}")
        return True
    except:
        print("❌ Node.js not found. Please install Node.js to run the frontend.")
        return False

def install_backend_deps():
    """Install backend dependencies"""
    print("\n📦 Installing backend dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'backend/requirements.txt'], 
                      check=True, cwd=os.getcwd())
        print("✅ Backend dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install backend dependencies")
        return False

def install_frontend_deps():
    """Install frontend dependencies"""
    print("\n📦 Installing frontend dependencies...")
    try:
        subprocess.run(['npm', 'install'], check=True, cwd='frontend')
        print("✅ Frontend dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install frontend dependencies")
        return False

def check_and_setup_database():
    """Check database status and setup if needed"""
    print("\n🔍 Checking database status...")
    try:
        result = subprocess.run([sys.executable, 'check_database.py'], 
                              capture_output=True, text=True, cwd='backend')
        
        print(result.stdout)
        
        # Check if migration is needed
        if "migrate_database.py" in result.stdout:
            print("🔄 Running database migration...")
            subprocess.run([sys.executable, 'migrate_database.py'], cwd='backend')
        elif "reset_database.py" in result.stdout:
            print("🔄 Database reset recommended...")
            response = input("Reset database? This will delete existing data (y/n): ")
            if response.lower() == 'y':
                subprocess.run([sys.executable, 'reset_database.py'], cwd='backend')
            else:
                print("⚠️  Continuing without reset - may encounter errors")
        
        return True
    except Exception as e:
        print(f"⚠️  Database check failed: {e}")
        return True  # Continue anyway

def start_backend():
    """Start the backend server"""
    print("\n🚀 Starting backend server...")
    try:
        # Start backend in background
        process = subprocess.Popen([sys.executable, 'app.py'], cwd='backend')
        
        # Wait for server to start
        print("⏳ Waiting for backend to start...")
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get('http://localhost:5000/', timeout=1)
                if response.status_code == 200:
                    print("✅ Backend server is running on http://localhost:5000")
                    return process
            except:
                pass
            time.sleep(1)
        
        print("❌ Backend server failed to start")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def create_admin_user():
    """Create admin user"""
    print("\n👤 Creating admin user...")
    try:
        subprocess.run([sys.executable, 'create_admin.py'], check=True, cwd='backend')
        print("✅ Admin user created")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Admin user creation failed (may already exist)")
        return True  # Continue anyway

def test_api():
    """Test the API endpoints"""
    print("\n🧪 Testing API endpoints...")
    try:
        subprocess.run([sys.executable, 'test_machine_api.py'], check=True, cwd='backend')
        return True
    except subprocess.CalledProcessError:
        print("⚠️  API test failed")
        return True  # Continue anyway

def start_frontend():
    """Start the frontend server"""
    print("\n🌐 Starting frontend server...")
    print("📝 The frontend will open in your browser at http://localhost:5173")
    print("🔑 Admin credentials: admin@example.com / admin123")
    print("\n" + "="*60)
    print("MACHINE MANAGEMENT SYSTEM IS READY!")
    print("="*60)
    print("1. Create a user account or login")
    print("2. Add machines using the 'Add Machine' button")
    print("3. Login as admin to approve machines")
    print("4. Select approved machines to access monitoring features")
    print("="*60)
    
    try:
        # Start frontend (this will block)
        subprocess.run(['npm', 'run', 'dev'], cwd='frontend')
    except KeyboardInterrupt:
        print("\n👋 Shutting down frontend...")
    except subprocess.CalledProcessError:
        print("❌ Failed to start frontend")

def main():
    print("🏭 Machine Management System Startup")
    print("="*50)
    
    # Check prerequisites
    if not check_python():
        return
    
    if not check_node():
        return
    
    # Install dependencies
    if not install_backend_deps():
        return
    
    if not install_frontend_deps():
        return
    
    # Check and setup database
    if not check_and_setup_database():
        return
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        return
    
    try:
        # Setup admin user
        create_admin_user()
        
        # Test API
        test_api()
        
        # Start frontend
        start_frontend()
        
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        if backend_process:
            backend_process.terminate()
            print("✅ Backend server stopped")

if __name__ == '__main__':
    main()