#!/usr/bin/env python3
"""
Check transport users and their driver records
"""

import sqlite3

def check_transport_users():
    """Check transport users and corresponding driver records"""
    db_path = 'hal_transport_system.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check transport users
        cursor.execute('SELECT id, employee_id, first_name, last_name, role FROM users WHERE role = "transport"')
        transport_users = cursor.fetchall()
        
        print("Transport users:")
        for user in transport_users:
            print(f"  ID: {user[0]}, Employee: {user[1]}, Name: {user[2]} {user[3]}, Role: {user[4]}")
        
        print(f"\nTotal transport users: {len(transport_users)}")
        
        # Check drivers
        cursor.execute('SELECT id, employee_id, first_name, last_name, is_active, is_available FROM drivers')
        drivers = cursor.fetchall()
        
        print("\nDrivers:")
        for driver in drivers:
            print(f"  ID: {driver[0]}, Employee: {driver[1]}, Name: {driver[2]} {driver[3]}, Active: {driver[4]}, Available: {driver[5]}")
        
        print(f"\nTotal drivers: {len(drivers)}")
        
        # Check for matching employee IDs
        transport_employee_ids = [user[1] for user in transport_users]
        driver_employee_ids = [driver[1] for driver in drivers]
        
        print("\nMatching employee IDs:")
        matches = set(transport_employee_ids) & set(driver_employee_ids)
        for match in matches:
            print(f"  {match} - has both user and driver record")
        
        print("\nTransport users without driver records:")
        no_driver = set(transport_employee_ids) - set(driver_employee_ids)
        for emp_id in no_driver:
            print(f"  {emp_id} - missing driver record")
        
        print("\nDrivers without transport user records:")
        no_user = set(driver_employee_ids) - set(transport_employee_ids)
        for emp_id in no_user:
            print(f"  {emp_id} - missing transport user record")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    check_transport_users()
