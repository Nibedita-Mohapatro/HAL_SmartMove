#!/usr/bin/env python3
"""
HAL Transport Management System - Complete System Integrity Verification
Run this script after restart/deployment to ensure all components are working correctly.
"""

import requests
import sqlite3
import os
import sys
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def verify_database_schema():
    """Verify database schema integrity"""
    print_header("DATABASE SCHEMA VERIFICATION")
    
    db_path = 'hal_transport_system.db'
    if not os.path.exists(db_path):
        print_error(f"Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check drivers table schema
        cursor.execute("PRAGMA table_info(drivers)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        required_columns = ['id', 'employee_id', 'first_name', 'last_name', 'phone', 
                          'license_number', 'license_expiry', 'experience_years', 
                          'is_active', 'is_available', 'created_at', 'updated_at']
        
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print_error(f"Missing columns in drivers table: {missing_columns}")
            return False
        
        print_success("Drivers table schema is complete")
        
        # Check data integrity
        cursor.execute("SELECT COUNT(*) FROM drivers WHERE employee_id = 'HAL002'")
        hal002_count = cursor.fetchone()[0]
        
        if hal002_count == 0:
            print_error("HAL002 driver record not found!")
            return False
        
        print_success("HAL002 driver record exists")
        
        # Check total drivers
        cursor.execute("SELECT COUNT(*) FROM drivers")
        total_drivers = cursor.fetchone()[0]
        print_info(f"Total drivers in database: {total_drivers}")
        
        conn.close()
        return True
        
    except Exception as e:
        print_error(f"Database verification failed: {e}")
        return False

def verify_api_endpoints():
    """Verify all critical API endpoints"""
    print_header("API ENDPOINTS VERIFICATION")
    
    base_url = "http://localhost:8000/api/v1"
    
    # Test admin login
    try:
        admin_response = requests.post(f"{base_url}/auth/login", json={
            'employee_id': 'HAL001',
            'password': 'admin123'
        }, timeout=10)
        
        if admin_response.status_code == 200:
            print_success("Admin login endpoint working")
            admin_token = admin_response.json()['access_token']
            admin_headers = {'Authorization': f'Bearer {admin_token}', 'Content-Type': 'application/json'}
        else:
            print_error(f"Admin login failed: {admin_response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Admin login test failed: {e}")
        return False
    
    # Test transport login
    try:
        transport_response = requests.post(f"{base_url}/auth/login", json={
            'employee_id': 'HAL002',
            'password': 'transport123'
        }, timeout=10)
        
        if transport_response.status_code == 200:
            print_success("Transport login endpoint working")
            transport_token = transport_response.json()['access_token']
            transport_headers = {'Authorization': f'Bearer {transport_token}', 'Content-Type': 'application/json'}
        else:
            print_error(f"Transport login failed: {transport_response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Transport login test failed: {e}")
        return False
    
    # Test admin requests endpoint
    try:
        requests_response = requests.get(f"{base_url}/admin/requests", headers=admin_headers, timeout=10)
        if requests_response.status_code == 200:
            print_success("Admin requests endpoint working")
            requests_data = requests_response.json()
            print_info(f"Total requests: {len(requests_data['requests'])}")
        else:
            print_error(f"Admin requests endpoint failed: {requests_response.status_code}")
            return False
    except Exception as e:
        print_error(f"Admin requests test failed: {e}")
        return False
    
    # Test transport assigned trips endpoint
    try:
        trips_response = requests.get(f"{base_url}/transport/assigned-trips", headers=transport_headers, timeout=10)
        if trips_response.status_code == 200:
            print_success("Transport assigned trips endpoint working")
            trips_data = trips_response.json()
            print_info(f"HAL002 assigned trips: {trips_data['count']}")
            print_info(f"Driver info: {trips_data['driver']['name']} (License: {trips_data['driver']['license_number']})")
        else:
            print_error(f"Transport assigned trips endpoint failed: {trips_response.status_code}")
            return False
    except Exception as e:
        print_error(f"Transport assigned trips test failed: {e}")
        return False
    
    return True

def verify_frontend_accessibility():
    """Verify frontend is accessible"""
    print_header("FRONTEND ACCESSIBILITY VERIFICATION")
    
    try:
        frontend_response = requests.get("http://localhost:3000", timeout=10)
        if frontend_response.status_code == 200:
            print_success("Frontend is accessible")
            return True
        else:
            print_error(f"Frontend not accessible: {frontend_response.status_code}")
            return False
    except Exception as e:
        print_error(f"Frontend accessibility test failed: {e}")
        print_info("Make sure the frontend server is running (npm start)")
        return False

def main():
    """Run complete system verification"""
    print_header("HAL TRANSPORT MANAGEMENT SYSTEM - INTEGRITY VERIFICATION")
    print_info(f"Verification started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Run all verification tests
    results.append(("Database Schema", verify_database_schema()))
    results.append(("API Endpoints", verify_api_endpoints()))
    results.append(("Frontend Accessibility", verify_frontend_accessibility()))
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    all_passed = True
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 ALL VERIFICATION TESTS PASSED!")
        print("✅ System is ready for production use")
    else:
        print("⚠️  SOME VERIFICATION TESTS FAILED!")
        print("❌ Please check the failed components before proceeding")
    print(f"{'='*60}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
