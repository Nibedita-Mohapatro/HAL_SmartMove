#!/usr/bin/env python3
"""
Create default drivers for the HAL Transport Management System
"""

from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.models.driver import Driver
from datetime import date

def create_default_drivers():
    """Create default drivers for testing"""
    
    # Create a database session
    db = Session(bind=engine)
    
    try:
        # Check if drivers already exist
        existing_drivers = db.query(Driver).count()
        if existing_drivers >= 4:
            print(f"✅ {existing_drivers} drivers already exist in the database")
            return True
        
        # Default drivers data
        drivers_data = [
            {
                "employee_id": "DRV001",
                "first_name": "Rajesh",
                "last_name": "Kumar",
                "phone": "+91-9876543210",
                "license_number": "KA0120230001",
                "license_expiry": date(2026, 12, 31),
                "experience_years": 8,
                "is_active": True,
                "is_available": True
            },
            {
                "employee_id": "DRV002", 
                "first_name": "Suresh",
                "last_name": "Reddy",
                "phone": "+91-9876543211",
                "license_number": "KA0120230002",
                "license_expiry": date(2027, 6, 30),
                "experience_years": 12,
                "is_active": True,
                "is_available": True
            },
            {
                "employee_id": "DRV003",
                "first_name": "Mahesh",
                "last_name": "Singh",
                "phone": "+91-9876543212", 
                "license_number": "KA0120230003",
                "license_expiry": date(2025, 9, 15),
                "experience_years": 5,
                "is_active": True,
                "is_available": True
            },
            {
                "employee_id": "DRV004",
                "first_name": "Venkat",
                "last_name": "Rao",
                "phone": "+91-9876543213",
                "license_number": "KA0120230004", 
                "license_expiry": date(2026, 3, 20),
                "experience_years": 15,
                "is_active": True,
                "is_available": True
            }
        ]
        
        # Create drivers
        created_drivers = []
        for driver_data in drivers_data:
            driver = Driver(**driver_data)
            db.add(driver)
            created_drivers.append(driver)
        
        # Commit the changes
        db.commit()
        
        print("✅ Default drivers created successfully:")
        for driver in created_drivers:
            print(f"   - {driver.employee_id}: {driver.first_name} {driver.last_name} (License: {driver.license_number})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating default drivers: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚗 Creating Default Drivers for HAL Transport System...")
    success = create_default_drivers()
    if success:
        print("✅ Default drivers setup completed!")
    else:
        print("❌ Failed to create default drivers!")
