#!/usr/bin/env python3
"""
Database reset script - drops and recreates all tables with the new schema.
WARNING: This will delete all existing data!
Use this only for development/testing.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import app, db, User, Machine
from werkzeug.security import generate_password_hash
from datetime import datetime, date

def reset_database():
    """Drop and recreate all tables"""
    
    with app.app_context():
        try:
            print("⚠️  WARNING: This will delete ALL existing data!")
            response = input("Are you sure you want to continue? (yes/no): ")
            
            if response.lower() != 'yes':
                print("❌ Operation cancelled.")
                return False
            
            print("🗑️  Dropping existing tables...")
            db.drop_all()
            
            print("🏗️  Creating new tables with updated schema...")
            db.create_all()
            
            print("✅ Database reset completed!")
            return True
            
        except Exception as e:
            print(f"❌ Database reset failed: {e}")
            return False

def create_sample_data():
    """Create sample users and machines for testing"""
    
    with app.app_context():
        try:
            print("👥 Creating sample users...")
            
            # Create admin user
            admin_user = User(
                name='Admin User',
                email='admin@example.com',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin_user)
            
            # Create regular user
            regular_user = User(
                name='John Doe',
                email='user@example.com',
                password=generate_password_hash('user123'),
                role='viewer'
            )
            db.session.add(regular_user)
            
            # Create engineer user
            engineer_user = User(
                name='Jane Engineer',
                email='engineer@example.com',
                password=generate_password_hash('engineer123'),
                role='engineer'
            )
            db.session.add(engineer_user)
            
            db.session.commit()
            
            print("🏭 Creating sample machines...")
            
            # Sample machines for regular user
            sample_machines = [
                {
                    'name': 'Production Line Motor A',
                    'motor_type': 'AC Induction Motor',
                    'motor_id': 'PROD-A-001',
                    'date_of_purchase': date(2022, 6, 15),
                    'purpose': 'Main production line conveyor belt motor',
                    'location': 'Factory Floor A',
                    'user_id': regular_user.id,
                    'status': 'approved',
                    'approved_at': datetime.utcnow(),
                    'approved_by': admin_user.id
                },
                {
                    'name': 'Packaging Unit Motor',
                    'motor_type': 'Servo Motor',
                    'motor_id': 'PKG-001',
                    'date_of_purchase': date(2023, 1, 10),
                    'purpose': 'Automated packaging system motor',
                    'location': 'Packaging Department',
                    'user_id': regular_user.id,
                    'status': 'approved',
                    'approved_at': datetime.utcnow(),
                    'approved_by': admin_user.id
                },
                {
                    'name': 'Quality Control Scanner',
                    'motor_type': 'Stepper Motor',
                    'motor_id': 'QC-SCAN-001',
                    'date_of_purchase': date(2023, 3, 20),
                    'purpose': 'Quality control scanning system motor',
                    'location': 'Quality Control Lab',
                    'user_id': regular_user.id,
                    'status': 'pending'  # This one is pending approval
                }
            ]
            
            # Sample machines for engineer user
            engineer_machines = [
                {
                    'name': 'Test Bench Motor',
                    'motor_type': 'DC Motor',
                    'motor_id': 'TEST-BENCH-001',
                    'date_of_purchase': date(2023, 2, 5),
                    'purpose': 'Engineering test bench motor for R&D',
                    'location': 'Engineering Lab',
                    'user_id': engineer_user.id,
                    'status': 'approved',
                    'approved_at': datetime.utcnow(),
                    'approved_by': admin_user.id
                }
            ]
            
            # Add all sample machines
            for machine_data in sample_machines + engineer_machines:
                machine = Machine(**machine_data)
                db.session.add(machine)
            
            db.session.commit()
            
            print("✅ Sample data created successfully!")
            
            # Print summary
            print("\n📊 Sample Data Summary:")
            print("=" * 40)
            print("👥 Users created:")
            print(f"   - Admin: admin@example.com / admin123")
            print(f"   - User: user@example.com / user123")
            print(f"   - Engineer: engineer@example.com / engineer123")
            
            print("\n🏭 Machines created:")
            all_machines = Machine.query.all()
            for machine in all_machines:
                owner = User.query.get(machine.user_id)
                print(f"   - {machine.name} ({machine.motor_id}) - {machine.status} - Owner: {owner.name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create sample data: {e}")
            db.session.rollback()
            return False

def main():
    print("🔄 Database Reset for Machine Management System")
    print("=" * 60)
    
    # Reset database
    if reset_database():
        # Create sample data
        if create_sample_data():
            print("\n" + "=" * 60)
            print("🎉 Database reset and sample data creation completed!")
            print("\nYou can now:")
            print("1. Start the Flask application: python app.py")
            print("2. Start the frontend: cd ../frontend && npm run dev")
            print("3. Login with any of the sample accounts")
            print("4. Test the machine management features")
            
            print("\n🔑 Login Credentials:")
            print("   Admin Panel: admin@example.com / admin123")
            print("   Regular User: user@example.com / user123")
            print("   Engineer: engineer@example.com / engineer123")
        else:
            print("\n⚠️  Database reset completed but sample data creation failed.")
    else:
        print("\n❌ Database reset failed.")

if __name__ == '__main__':
    main()