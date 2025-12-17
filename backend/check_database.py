#!/usr/bin/env python3
"""
Database status checker - helps determine the best migration approach.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import app, db
from sqlalchemy import text

def check_database_status():
    """Check current database status and recommend migration approach"""
    
    with app.app_context():
        try:
            # Check if machines table exists
            result = db.session.execute(text("SHOW TABLES LIKE 'machines'"))
            table_exists = result.fetchone() is not None
            
            if not table_exists:
                print("📋 Status: No machines table found")
                print("✅ Recommendation: Run 'python app.py' to create fresh tables")
                return "fresh_install"
            
            # Check table structure
            result = db.session.execute(text("DESCRIBE machines"))
            existing_columns = [row[0] for row in result.fetchall()]
            
            print("📋 Current machines table columns:")
            for col in existing_columns:
                print(f"   - {col}")
            
            # Check for new columns
            required_columns = [
                'motor_type', 'motor_id', 'date_of_purchase', 
                'purpose', 'user_id', 'approved_at', 'approved_by'
            ]
            
            missing_columns = [col for col in required_columns if col not in existing_columns]
            
            if missing_columns:
                print(f"\n❌ Missing columns: {', '.join(missing_columns)}")
                
                # Check if there's existing data
                result = db.session.execute(text("SELECT COUNT(*) FROM machines"))
                machine_count = result.fetchone()[0]
                
                print(f"📊 Existing machines: {machine_count}")
                
                if machine_count > 0:
                    print("\n🔄 Recommendation: Run migration to preserve existing data")
                    print("   Command: python migrate_database.py")
                    return "migrate"
                else:
                    print("\n🔄 Recommendation: Reset database (no data to lose)")
                    print("   Command: python reset_database.py")
                    return "reset"
            else:
                print("\n✅ All required columns present!")
                
                # Check users table
                result = db.session.execute(text("SELECT COUNT(*) FROM users"))
                user_count = result.fetchone()[0]
                
                if user_count == 0:
                    print("👤 No users found - run: python create_admin.py")
                    return "create_users"
                else:
                    print(f"👥 Found {user_count} users")
                    print("✅ Database appears to be ready!")
                    return "ready"
                    
        except Exception as e:
            print(f"❌ Database check failed: {e}")
            print("\n🔄 Recommendation: Reset database")
            print("   Command: python reset_database.py")
            return "error"

def main():
    print("🔍 Database Status Check")
    print("=" * 40)
    
    status = check_database_status()
    
    print("\n" + "=" * 40)
    print("📋 NEXT STEPS:")
    
    if status == "fresh_install":
        print("1. Run: python app.py")
        print("2. Run: python create_admin.py")
        print("3. Start frontend and test")
        
    elif status == "migrate":
        print("1. Run: python migrate_database.py")
        print("2. Run: python create_admin.py (if needed)")
        print("3. Restart Flask app")
        
    elif status == "reset":
        print("1. Run: python reset_database.py")
        print("2. Start Flask app")
        print("3. Start frontend and test")
        
    elif status == "create_users":
        print("1. Run: python create_admin.py")
        print("2. Start frontend and test")
        
    elif status == "ready":
        print("1. Start Flask app: python app.py")
        print("2. Start frontend: cd ../frontend && npm run dev")
        print("3. Login and test features")
        
    else:  # error
        print("1. Run: python reset_database.py")
        print("2. Start Flask app")
        print("3. Start frontend and test")

if __name__ == '__main__':
    main()