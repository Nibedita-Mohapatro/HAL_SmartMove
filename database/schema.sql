-- HAL SmartMove Transport Management System
-- Complete Database Schema
-- Generated from hal_transport_system.db
-- 
-- This file contains the complete database schema for the HAL SmartMove
-- transport management system. It can be used to recreate the database
-- structure if needed.
--
-- Usage: sqlite3 new_database.db < schema.sql

-- ============================================
-- CORE TABLES
-- ============================================

-- Users table - System users with role-based access
CREATE TABLE users (
	id INTEGER NOT NULL, 
	employee_id VARCHAR(20) NOT NULL, 
	email VARCHAR(100) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	first_name VARCHAR(50) NOT NULL, 
	last_name VARCHAR(50) NOT NULL, 
	phone VARCHAR(15), 
	department VARCHAR(100), 
	designation VARCHAR(100), 
	role VARCHAR(11), 
	is_active BOOLEAN, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	last_login DATETIME, 
	PRIMARY KEY (id)
);

-- Vehicles table - Fleet management
CREATE TABLE vehicles (
	id INTEGER NOT NULL, 
	vehicle_number VARCHAR(20) NOT NULL, 
	vehicle_type VARCHAR(7) NOT NULL, 
	capacity INTEGER NOT NULL, 
	fuel_type VARCHAR(8) NOT NULL, 
	model VARCHAR(50), 
	year_of_manufacture INTEGER, 
	insurance_expiry DATE, 
	fitness_certificate_expiry DATE, 
	is_active BOOLEAN, 
	current_location VARCHAR(255), 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id)
);

-- Drivers table - Driver management with licensing
CREATE TABLE drivers (
	id INTEGER NOT NULL, 
	employee_id VARCHAR(20) NOT NULL, 
	first_name VARCHAR(50) NOT NULL, 
	last_name VARCHAR(50) NOT NULL, 
	phone VARCHAR(15), 
	license_number VARCHAR(20) NOT NULL, 
	license_expiry DATE, 
	experience_years INTEGER, 
	is_active BOOLEAN, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	is_available BOOLEAN DEFAULT 1, 
	PRIMARY KEY (id), 
	UNIQUE (license_number)
);

-- Transport requests table - Employee transport requests
CREATE TABLE transport_requests (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	origin VARCHAR(255) NOT NULL, 
	destination VARCHAR(255) NOT NULL, 
	request_date DATE NOT NULL, 
	request_time TIME NOT NULL, 
	return_date DATE, 
	return_time TIME, 
	passenger_count INTEGER, 
	purpose TEXT, 
	status VARCHAR(9), 
	priority VARCHAR(6), 
	admin_comments TEXT, 
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	approved_by INTEGER, 
	approved_at DATETIME, 
	rejection_reason TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

-- Vehicle assignments table - Trip assignments and tracking
CREATE TABLE vehicle_assignments (
	id INTEGER NOT NULL, 
	request_id INTEGER NOT NULL, 
	vehicle_id INTEGER NOT NULL, 
	driver_id INTEGER NOT NULL, 
	status VARCHAR(11), 
	assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
	started_at DATETIME, 
	completed_at DATETIME, 
	notes TEXT, 
	assigned_by INTEGER, 
	assignment_date DATE, 
	estimated_departure TIME, 
	estimated_arrival TIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(request_id) REFERENCES transport_requests (id), 
	FOREIGN KEY(vehicle_id) REFERENCES vehicles (id), 
	FOREIGN KEY(driver_id) REFERENCES drivers (id)
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- User indexes
CREATE UNIQUE INDEX ix_users_employee_id ON users (employee_id);
CREATE INDEX ix_users_id ON users (id);
CREATE UNIQUE INDEX ix_users_email ON users (email);

-- Vehicle indexes
CREATE UNIQUE INDEX ix_vehicles_vehicle_number ON vehicles (vehicle_number);
CREATE INDEX ix_vehicles_id ON vehicles (id);

-- Driver indexes
CREATE INDEX ix_drivers_id ON drivers (id);
CREATE UNIQUE INDEX ix_drivers_employee_id ON drivers (employee_id);

-- Transport request indexes
CREATE INDEX ix_transport_requests_id ON transport_requests (id);

-- Vehicle assignment indexes
CREATE INDEX ix_vehicle_assignments_id ON vehicle_assignments (id);

-- ============================================
-- ENUM VALUES REFERENCE
-- ============================================

-- User Roles:
-- - 'employee': Regular employee
-- - 'admin': Administrator
-- - 'super_admin': Super administrator
-- - 'transport': Transport manager

-- Vehicle Types:
-- - 'bus': Bus
-- - 'car': Car
-- - 'van': Van
-- - 'shuttle': Shuttle

-- Fuel Types:
-- - 'petrol': Petrol
-- - 'diesel': Diesel
-- - 'electric': Electric
-- - 'hybrid': Hybrid

-- Request Status:
-- - 'pending': Pending approval
-- - 'approved': Approved
-- - 'rejected': Rejected
-- - 'completed': Completed
-- - 'cancelled': Cancelled

-- Request Priority:
-- - 'low': Low priority
-- - 'medium': Medium priority
-- - 'high': High priority
-- - 'urgent': Urgent

-- Assignment Status:
-- - 'assigned': Assigned
-- - 'in_progress': In progress
-- - 'completed': Completed
-- - 'cancelled': Cancelled

-- ============================================
-- SAMPLE DATA REFERENCE
-- ============================================

-- Default Users:
-- HAL001 - Super Admin (admin123)
-- HAL002 - Transport Manager (transport123)
-- HAL003 - Employee (employee123)

-- Default Drivers:
-- DRV001 - Rajesh Kumar (License: KA0120230001)
-- DRV002 - Suresh Reddy (License: KA0120230002)
-- DRV003 - Mahesh Singh (License: KA0120230003)
-- DRV004 - Venkat Rao (License: KA0120230004)

-- ============================================
-- MAINTENANCE NOTES
-- ============================================

-- To recreate database:
-- 1. sqlite3 new_database.db < schema.sql
-- 2. python backend/create_default_users.py
-- 3. python backend/create_default_drivers.py
-- 4. python backend/verify_system_integrity.py

-- To extract current schema:
-- sqlite3 hal_transport_system.db ".schema" > schema.sql

-- To backup data:
-- sqlite3 hal_transport_system.db ".dump" > backup.sql
