#!/usr/bin/env python3
"""
Database migration script to add new columns to the machines table.
Run this script to update your existing database schema.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import app, db
from sqlalchemy import text

def migrate_machines_table():
    """Add new columns to the existing machines table"""
    
    with app.app_context():
        try:
            # Check if the new columns already exist
            result = db.session.execute(text("DESCRIBE machines"))
            existing_columns = [row[0] for row in result.fetchall()]
            
            print("📋 Current columns in machines table:")
            for col in existing_columns:
                print(f"   - {col}")
            
            # List of new columns to add
            new_columns = [
                ("motor_type", "VARCHAR(100) NOT NULL DEFAULT 'Unknown'"),
                ("motor_id", "VARCHAR(100) UNIQUE NOT NULL DEFAULT CONCAT('MTR-', id)"),
                ("date_of_purchase", "DATE NOT NULL DEFAULT '2023-01-01'"),
                ("purpose", "VARCHAR(255) NOT NULL DEFAULT 'General Purpose'"),
                ("user_id", "INT NOT NULL DEFAULT 1"),
                ("approved_at", "DATETIME NULL"),
                ("approved_by", "INT NULL")
            ]
            
            # Add missing columns
            columns_added = 0
            for column_name, column_definition in new_columns:
                if column_name not in existing_columns:
                    try:
                        print(f"➕ Adding column: {column_name}")
                        
                        if column_name == "motor_id":
                            # Special handling for motor_id with unique constraint
                            db.session.execute(text(f"ALTER TABLE machines ADD COLUMN {column_name} {column_definition}"))
                            # Update existing records with unique motor_ids
                            db.session.execute(text("UPDATE machines SET motor_id = CONCAT('MTR-', LPAD(id, 3, '0')) WHERE motor_id = CONCAT('MTR-', id)"))
                        elif column_name == "user_id":
                            # Add user_id column and foreign key
                            db.session.execute(text(f"ALTER TABLE machines ADD COLUMN {column_name} {column_definition}"))
                            # Add foreign key constraint
                            db.session.execute(text("ALTER TABLE machines ADD CONSTRAINT fk_machines_user_id FOREIGN KEY (user_id) REFERENCES users(id)"))
                        elif column_name == "approved_by":
                            # Add approved_by column and foreign key
                            db.session.execute(text(f"ALTER TABLE machines ADD COLUMN {column_name} {column_definition}"))
                            # Add foreign key constraint
                            db.session.execute(text("ALTER TABLE machines ADD CONSTRAINT fk_machines_approved_by FOREIGN KEY (approved_by) REFERENCES users(id)"))
                        else:
                            db.session.execute(text(f"ALTER TABLE machines ADD COLUMN {column_name} {column_definition}"))
                        
                        columns_added += 1
                        print(f"   ✅ Added {column_name}")
                        
                    except Exception as e:
                        print(f"   ⚠️  Failed to add {column_name}: {e}")
                        # Continue with other columns
                        continue
                else:
                    print(f"   ✅ Column {column_name} already exists")
            
            # Update the status column to include new enum values
            try:
                print("🔄 Updating status column enum values...")
                db.session.execute(text("""
                    ALTER TABLE machines 
                    MODIFY COLUMN status ENUM('pending', 'approved', 'rejected', 'active', 'inactive', 'maintenance') 
                    DEFAULT 'pending'
                """))
                print("   ✅ Status column updated")
            except Exception as e:
                print(f"   ⚠️  Failed to update status column: {e}")
            
            # Commit all changes
            db.session.commit()
            
            print(f"\n🎉 Migration completed! Added {columns_added} new columns.")
            
            # Show final table structure
            result = db.session.execute(text("DESCRIBE machines"))
            final_columns = [row for row in result.fetchall()]
            
            print("\n📋 Final table structure:")
            for row in final_columns:
                print(f"   - {row[0]}: {row[1]} {row[2]} {row[3]} {row[4]} {row[5]}")
                
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            return False
            
    return True

def create_default_user():
    """Create a default user if none exists"""
    
    with app.app_context():
        from app import User
        from werkzeug.security import generate_password_hash
        
        try:
            # Check if any users exist
            user_count = User.query.count()
            
            if user_count == 0:
                print("👤 Creating default user...")
                
                # Create default user
                default_user = User(
                    name='Default User',
                    email='user@example.com',
                    password=generate_password_hash('user123'),
                    role='viewer'
                )
                
                db.session.add(default_user)
                db.session.commit()
                
                print("   ✅ Default user created: user@example.com / user123")
                return default_user.id
            else:
                # Return first user's ID
                first_user = User.query.first()
                print(f"   ✅ Using existing user: {first_user.email}")
                return first_user.id
                
        except Exception as e:
            print(f"   ❌ Failed to create default user: {e}")
            return 1  # Fallback to ID 1

def update_existing_machines():
    """Update existing machines with default values"""
    
    with app.app_context():
        try:
            # Get default user ID
            default_user_id = create_default_user()
            
            # Update existing machines that don't have user_id set properly
            result = db.session.execute(text("""
                UPDATE machines 
                SET user_id = :user_id 
                WHERE user_id = 1 OR user_id IS NULL
            """), {"user_id": default_user_id})
            
            updated_count = result.rowcount
            db.session.commit()
            
            if updated_count > 0:
                print(f"🔄 Updated {updated_count} existing machines with user ownership")
            
        except Exception as e:
            print(f"⚠️  Failed to update existing machines: {e}")

def main():
    print("🔧 Database Migration for Machine Management System")
    print("=" * 60)
    
    # Run migration
    if migrate_machines_table():
        # Update existing data
        update_existing_machines()
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Restart your Flask application")
        print("2. Run: python create_admin.py")
        print("3. Test the machine management features")
        print("\nDefault credentials created:")
        print("- User: user@example.com / user123")
        print("- Admin: Run create_admin.py for admin@example.com / admin123")
    else:
        print("\n❌ Migration failed. Please check the errors above.")

if __name__ == '__main__':
    main()