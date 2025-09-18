#!/usr/bin/env python3
"""
Add a test user to the SysManage database for screenshot purposes
"""

import sys
import os
import sqlite3
from datetime import datetime, timezone
from argon2 import PasswordHasher

# Add the backend to the Python path so we can import the models
sys.path.append('/home/bceverly/dev/sysmanage/backend')

def add_test_user():
    """Add a test user to the database"""

    # Database configuration from /etc/sysmanage.yaml
    db_path = '/home/bceverly/dev/sysmanage/sysmanage.db'

    # User details
    userid = 'admin@sysmanage.local'
    password = 'AdminPassword123!'  # Meets policy: uppercase, lowercase, number, special char
    first_name = 'System'
    last_name = 'Administrator'

    # Hash the password using Argon2 (same as backend)
    argon2_hasher = PasswordHasher()
    hashed_password = argon2_hasher.hash(password)

    print(f"Creating user: {userid}")
    print(f"Password: {password}")
    print(f"Hashed password: {hashed_password[:50]}...")

    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE userid = ?", (userid,))
        existing = cursor.fetchone()

        if existing:
            print(f"User {userid} already exists, updating password...")
            cursor.execute("""
                UPDATE users
                SET hashed_password = ?,
                    last_access = ?,
                    is_locked = 0,
                    failed_login_attempts = 0
                WHERE userid = ?
            """, (hashed_password, datetime.now(timezone.utc).isoformat(), userid))
        else:
            print(f"Creating new user {userid}...")
            cursor.execute("""
                INSERT INTO users
                (userid, active, first_name, last_name, hashed_password, last_access, is_locked, failed_login_attempts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                userid,
                True,  # active
                first_name,
                last_name,
                hashed_password,
                datetime.now(timezone.utc).isoformat(),
                False,  # is_locked
                0  # failed_login_attempts
            ))

        conn.commit()
        print("✅ User created/updated successfully!")

        # Verify the user was created
        cursor.execute("SELECT userid, active, first_name, last_name FROM users WHERE userid = ?", (userid,))
        user = cursor.fetchone()
        if user:
            print(f"✅ Verified user in database: {user}")
        else:
            print("❌ Failed to verify user creation")

    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

    return True

if __name__ == "__main__":
    print("Adding test user to SysManage database...")
    success = add_test_user()
    if success:
        print("\n🎉 Test user added successfully!")
        print("You can now login with:")
        print("  Email: admin@sysmanage.local")
        print("  Password: AdminPassword123!")
    else:
        print("\n❌ Failed to add test user")
        sys.exit(1)