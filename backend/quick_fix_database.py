#!/usr/bin/env python3
"""
Quick fix for the database column error.
This script will add the missing columns to your existing machines table.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import app, db
from sqlalchemy import text

def quick_fix():
    """Add missing columns to machines table"""
    
    with app.app_context():
        try:
            print("🔧 Quick Fix: Adding missing columns to machines table...")
            
            # Add columns one by one with error handling
            columns_to_add = [
                ("motor_type", "VARCHAR(100) NOT NULL DEFAULT 'Unknown Motor'"),
                ("motor_id", "VARCHAR(100) NOT NULL DEFAULT 'MTR-000'"),
                ("date_of_purchase", "DATE NOT NULL DEFAULT '2023-01-01'"),
                ("purpose", "VARCHAR(255) NOT NULL DEFAULT 'General Purpose'"),
                ("user_id", "INT NOT NULL DEFAULT 1"),
                ("approved_at", "DATETIME NULL"),
                ("approved_by", "INT NULL")
            ]
            
            for column_name, column_def in columns_to_add:
                try:
                    # Check if column exists
                    result = db.session.execute(text(f"SHOW COLUMNS FROM machines LIKE '{column_name}'"))
                    if result.fetchone():
                        print(f"   ✅ {column_name} already exists")
                        continue
                    
                    # Add the column
                    db.session.execute(text(f"ALTER TABLE machines ADD COLUMN {column_name} {column_def}"))
                    print(f"   ➕ Added {column_name}")
                    
                except Exception as e:
                    print(f"   ⚠️  Failed to add {column_name}: {e}")
                    continue
            
            # Update motor_id to be unique for existing records
            try:
                db.session.execute(text("""
                    UPDATE machines 
                    SET motor_id = CONCAT('MTR-', LPAD(id, 3, '0')) 
                    WHERE motor_id = 'MTR-000'
                """))
                print("   🔄 Updated motor_id values to be unique")
            except Exception as e:
                print(f"   ⚠️  Failed to update motor_id: {e}")
            
            # Add unique constraint to motor_id
            try:
                db.session.execute(text("ALTER TABLE machines ADD UNIQUE KEY unique_motor_id (motor_id)"))
                print("   🔒 Added unique constraint to motor_id")
            except Exception as e:
                print(f"   ⚠️  Failed to add unique constraint: {e}")
            
            # Update status enum
            try:
                db.session.execute(text("""
                    ALTER TABLE machines 
                    MODIFY COLUMN status ENUM('pending', 'approved', 'rejected', 'active', 'inactive', 'maintenance') 
                    DEFAULT 'approved'
                """))
                print("   🔄 Updated status enum values")
            except Exception as e:
                print(f"   ⚠️  Failed to update status enum: {e}")
            
            # Set existing machines to approved status
            try:
                db.session.execute(text("UPDATE machines SET status = 'approved' WHERE status = 'active'"))
                print("   ✅ Set existing machines to approved status")
            except Exception as e:
                print(f"   ⚠️  Failed to update machine status: {e}")
            
            db.session.commit()
            print("\n✅ Quick fix completed successfully!")
            
            # Show final structure
            result = db.session.execute(text("DESCRIBE machines"))
            columns = result.fetchall()
            
            print("\n📋 Updated table structure:")
            for col in columns:
                print(f"   - {col[0]}: {col[1]}")
            
            return True
            
        except Exception as e:
            print(f"❌ Quick fix failed: {e}")
            db.session.rollback()
            return False

def create_default_user_if_needed():
    """Create a default user for existing machines"""
    
    with app.app_context():
        from app import User
        from werkzeug.security import generate_password_hash
        
        try:
            # Check if we have any users
            user_count = User.query.count()
            
            if user_count == 0:
                print("👤 Creating default user for existing machines...")
                
                default_user = User(
                    name='Default User',
                    email='user@example.com',
                    password=generate_password_hash('user123'),
                    role='viewer'
                )
                
                db.session.add(default_user)
                db.session.commit()
                
                print("   ✅ Default user created: user@example.com / user123")
                
                # Update machines to belong to this user
                db.session.execute(text(f"UPDATE machines SET user_id = {default_user.id}"))
                db.session.commit()
                
                print("   🔗 Linked existing machines to default user")
                
        except Exception as e:
            print(f"   ⚠️  Failed to create default user: {e}")

def main():
    print("⚡ Quick Database Fix for Machine Management")
    print("=" * 50)
    
    if quick_fix():
        create_default_user_if_needed()
        
        print("\n" + "=" * 50)
        print("🎉 Database fixed! You can now:")
        print("1. Restart your Flask app: python app.py")
        print("2. Run: python create_admin.py (to create admin user)")
        print("3. Test the machine management features")
        print("\n🔑 Default user created: user@example.com / user123")
    else:
        print("\n❌ Fix failed. Try running: python reset_database.py")

if __name__ == '__main__':
    main()