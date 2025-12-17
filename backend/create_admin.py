#!/usr/bin/env python3
"""
Script to create an admin user for testing the machine approval system.
Run this after starting the Flask app to create the database tables.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import app, db, User
from werkzeug.security import generate_password_hash

def create_admin_user():
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@example.com').first()
        if admin:
            print("✅ Admin user already exists: admin@example.com")
            return
        
        # Create admin user
        admin_user = User(
            name='Admin User',
            email='admin@example.com',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("✅ Admin user created successfully!")
        print("📧 Email: admin@example.com")
        print("🔑 Password: admin123")
        print("👤 Role: admin")
        print("\nYou can now log in with these credentials to access the admin panel.")

if __name__ == '__main__':
    create_admin_user()