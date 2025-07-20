#!/usr/bin/env python3
"""
Create driver record for transport user HAL002
"""

from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.models.driver import Driver
from datetime import date

def create_transport_driver():
    """Create driver record for HAL002 transport user"""
    
    # Create a database session
    db = Session(bind=engine)
    
    try:
        # Check if driver already exists for HAL002
        existing_driver = db.query(Driver).filter(Driver.employee_id == "HAL002").first()
        if existing_driver:
            print(f"✅ Driver record already exists for HAL002: {existing_driver.first_name} {existing_driver.last_name}")
            return True
        
        # Create driver record for HAL002
        driver_data = {
            "employee_id": "HAL002",
            "first_name": "Transport",
            "last_name": "Manager",
            "phone": "+91-9876543220",
            "license_number": "KA0120230005",
            "license_expiry": date(2026, 12, 31),
            "experience_years": 10,
            "is_active": True,
            "is_available": True
        }
        
        driver = Driver(**driver_data)
        db.add(driver)
        db.commit()
        db.refresh(driver)
        
        print(f"✅ Driver record created for HAL002: {driver.first_name} {driver.last_name}")
        print(f"   - Employee ID: {driver.employee_id}")
        print(f"   - License: {driver.license_number}")
        print(f"   - Phone: {driver.phone}")
        print(f"   - Active: {driver.is_active}")
        print(f"   - Available: {driver.is_available}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating driver record: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚗 Creating Driver Record for Transport User HAL002...")
    success = create_transport_driver()
    if success:
        print("✅ Transport driver setup completed!")
    else:
        print("❌ Failed to create transport driver!")
