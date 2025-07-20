#!/usr/bin/env python3
"""
Check database tables and schema
"""

import sqlite3
import os

def check_database():
    """Check what tables exist in the database"""
    db_path = 'hal_transport_system.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
        tables = cursor.fetchall()
        
        print("Existing tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_database()
