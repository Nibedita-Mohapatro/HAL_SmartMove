#!/usr/bin/env python3
"""
Fix database schema by adding missing columns to transport_requests table
"""

import sqlite3
import os

def fix_transport_requests_schema():
    """Add missing columns to transport_requests table"""
    db_path = 'hal_transport_system.db'

    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check current schema
        cursor.execute("PRAGMA table_info(transport_requests)")
        columns = cursor.fetchall()
        existing_columns = [col[1] for col in columns]

        print("Current transport_requests columns:")
        for col in existing_columns:
            print(f"  - {col}")

        # Add missing columns if they don't exist
        missing_columns = []

        if 'approved_by' not in existing_columns:
            cursor.execute('ALTER TABLE transport_requests ADD COLUMN approved_by INTEGER')
            missing_columns.append('approved_by')

        if 'approved_at' not in existing_columns:
            cursor.execute('ALTER TABLE transport_requests ADD COLUMN approved_at DATETIME')
            missing_columns.append('approved_at')

        if 'rejection_reason' not in existing_columns:
            cursor.execute('ALTER TABLE transport_requests ADD COLUMN rejection_reason TEXT')
            missing_columns.append('rejection_reason')

        conn.commit()

        if missing_columns:
            print(f"\nSuccessfully added missing columns to transport_requests: {', '.join(missing_columns)}")
        else:
            print("\nAll required transport_requests columns already exist!")

        # Verify the schema
        cursor.execute("PRAGMA table_info(transport_requests)")
        columns = cursor.fetchall()
        print("\nUpdated transport_requests columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")

        conn.close()
        return True

    except Exception as e:
        print(f"Error fixing database schema: {e}")
        return False


def fix_vehicle_assignments_schema():
    """Add missing columns to vehicle_assignments table"""
    db_path = 'hal_transport_system.db'

    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check current schema
        cursor.execute("PRAGMA table_info(vehicle_assignments)")
        columns = cursor.fetchall()
        existing_columns = [col[1] for col in columns]

        print("Current vehicle_assignments columns:")
        for col in existing_columns:
            print(f"  - {col}")

        # Add missing columns if they don't exist
        missing_columns = []

        if 'assigned_by' not in existing_columns:
            cursor.execute('ALTER TABLE vehicle_assignments ADD COLUMN assigned_by INTEGER')
            missing_columns.append('assigned_by')

        if 'assignment_date' not in existing_columns:
            cursor.execute('ALTER TABLE vehicle_assignments ADD COLUMN assignment_date DATE')
            missing_columns.append('assignment_date')

        if 'estimated_departure' not in existing_columns:
            cursor.execute('ALTER TABLE vehicle_assignments ADD COLUMN estimated_departure TIME')
            missing_columns.append('estimated_departure')

        if 'estimated_arrival' not in existing_columns:
            cursor.execute('ALTER TABLE vehicle_assignments ADD COLUMN estimated_arrival TIME')
            missing_columns.append('estimated_arrival')

        conn.commit()

        if missing_columns:
            print(f"\nSuccessfully added missing columns to vehicle_assignments: {', '.join(missing_columns)}")
        else:
            print("\nAll required vehicle_assignments columns already exist!")

        # Verify the schema
        cursor.execute("PRAGMA table_info(vehicle_assignments)")
        columns = cursor.fetchall()
        print("\nUpdated vehicle_assignments columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")

        conn.close()
        return True

    except Exception as e:
        print(f"Error fixing vehicle_assignments schema: {e}")
        return False


def fix_drivers_schema():
    """Add missing columns to drivers table"""
    db_path = 'hal_transport_system.db'

    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check current schema
        cursor.execute("PRAGMA table_info(drivers)")
        columns = cursor.fetchall()
        existing_columns = [col[1] for col in columns]

        print("Current drivers columns:")
        for col in existing_columns:
            print(f"  - {col}")

        # Add missing columns if they don't exist
        missing_columns = []

        if 'is_available' not in existing_columns:
            cursor.execute('ALTER TABLE drivers ADD COLUMN is_available BOOLEAN DEFAULT 1')
            missing_columns.append('is_available')

        conn.commit()

        if missing_columns:
            print(f"\nSuccessfully added missing columns to drivers: {', '.join(missing_columns)}")
        else:
            print("\nAll required drivers columns already exist!")

        # Verify the schema
        cursor.execute("PRAGMA table_info(drivers)")
        columns = cursor.fetchall()
        print("\nUpdated drivers columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")

        conn.close()
        return True

    except Exception as e:
        print(f"Error fixing drivers schema: {e}")
        return False


if __name__ == "__main__":
    print("🔧 Fixing HAL Transport Database Schema...")
    success1 = fix_transport_requests_schema()
    success2 = fix_vehicle_assignments_schema()
    success3 = fix_drivers_schema()
    if success1 and success2 and success3:
        print("✅ Database schema fixed successfully!")
    else:
        print("❌ Failed to fix database schema!")
