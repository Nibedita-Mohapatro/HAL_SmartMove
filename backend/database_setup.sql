-- HAL Transport Management System - Production Database Setup
-- MySQL Database Schema

-- Create database
CREATE DATABASE IF NOT EXISTS hal_transport CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user and grant privileges
CREATE USER IF NOT EXISTS 'hal_user'@'localhost' IDENTIFIED BY 'secure_password_here';
GRANT ALL PRIVILEGES ON hal_transport.* TO 'hal_user'@'localhost';
FLUSH PRIVILEGES;

USE hal_transport;

-- Users table
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    department VARCHAR(100),
    designation VARCHAR(100),
    role ENUM('employee', 'admin', 'super_admin') NOT NULL DEFAULT 'employee',
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(20),
    updated_by VARCHAR(20),
    INDEX idx_employee_id (employee_id),
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_is_active (is_active)
);

-- Vehicles table
CREATE TABLE vehicles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    registration_number VARCHAR(20) UNIQUE NOT NULL,
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INT NOT NULL,
    type ENUM('sedan', 'suv', 'bus', 'van', 'truck') NOT NULL,
    capacity INT,
    fuel_type ENUM('petrol', 'diesel', 'cng', 'electric', 'hybrid') NOT NULL DEFAULT 'petrol',
    status ENUM('available', 'in_use', 'maintenance', 'out_of_service') NOT NULL DEFAULT 'available',
    insurance_expiry DATE,
    last_maintenance DATE,
    next_maintenance DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(20),
    updated_by VARCHAR(20),
    INDEX idx_registration (registration_number),
    INDEX idx_status (status),
    INDEX idx_type (type),
    INDEX idx_is_active (is_active)
);

-- Drivers table
CREATE TABLE drivers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    license_number VARCHAR(50) UNIQUE NOT NULL,
    license_type ENUM('Light Vehicle', 'Heavy Vehicle', 'Commercial', 'Transport') NOT NULL,
    license_expiry DATE NOT NULL,
    date_of_birth DATE NOT NULL,
    address TEXT,
    emergency_contact VARCHAR(100),
    emergency_phone VARCHAR(20),
    status ENUM('active', 'inactive', 'on_leave', 'on_trip') NOT NULL DEFAULT 'active',
    rating DECIMAL(3,2) DEFAULT 0.00,
    total_trips INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(20),
    updated_by VARCHAR(20),
    INDEX idx_employee_id (employee_id),
    INDEX idx_license_number (license_number),
    INDEX idx_status (status),
    INDEX idx_license_expiry (license_expiry),
    INDEX idx_is_active (is_active)
);

-- Transport requests table
CREATE TABLE transport_requests (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id VARCHAR(20) NOT NULL,
    origin VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    request_date DATE NOT NULL,
    request_time TIME NOT NULL,
    passenger_count INT NOT NULL DEFAULT 1,
    purpose TEXT NOT NULL,
    priority ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'medium',
    status ENUM('pending', 'approved', 'rejected', 'completed', 'cancelled') NOT NULL DEFAULT 'pending',
    assigned_vehicle_id INT,
    assigned_driver_id INT,
    assignment_notes TEXT,
    approved_by VARCHAR(20),
    approved_at TIMESTAMP NULL,
    rejected_by VARCHAR(20),
    rejected_at TIMESTAMP NULL,
    completed_by VARCHAR(20),
    completed_at TIMESTAMP NULL,
    cancelled_by VARCHAR(20),
    cancelled_at TIMESTAMP NULL,
    assigned_by VARCHAR(20),
    assigned_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_employee_id (employee_id),
    INDEX idx_status (status),
    INDEX idx_request_date (request_date),
    INDEX idx_priority (priority),
    INDEX idx_assigned_vehicle (assigned_vehicle_id),
    INDEX idx_assigned_driver (assigned_driver_id),
    FOREIGN KEY (assigned_vehicle_id) REFERENCES vehicles(id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_driver_id) REFERENCES drivers(id) ON DELETE SET NULL
);

-- Documents table
CREATE TABLE documents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    entity_type ENUM('request', 'vehicle', 'driver') NOT NULL,
    entity_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    uploaded_by VARCHAR(20) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_uploaded_by (uploaded_by)
);

-- Audit log table
CREATE TABLE audit_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(20) NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INT,
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_created_at (created_at)
);

-- System settings table
CREATE TABLE system_settings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    description TEXT,
    updated_by VARCHAR(20),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_setting_key (setting_key)
);

-- Insert default super admin user (password: admin123)
INSERT INTO users (employee_id, email, first_name, last_name, phone, department, designation, role, password_hash, created_by) 
VALUES (
    'HAL001', 
    'admin@hal.co.in', 
    'System', 
    'Administrator', 
    '+91-9876543210', 
    'IT', 
    'System Administrator', 
    'super_admin', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L6W5whe7G',  -- admin123
    'SYSTEM'
);

-- Insert default system settings
INSERT INTO system_settings (setting_key, setting_value, description, updated_by) VALUES
('app_name', 'HAL Transport Management System', 'Application name', 'SYSTEM'),
('app_version', '1.0.0', 'Application version', 'SYSTEM'),
('max_advance_booking_days', '30', 'Maximum days in advance for booking', 'SYSTEM'),
('default_trip_duration_hours', '8', 'Default trip duration in hours', 'SYSTEM'),
('maintenance_reminder_days', '7', 'Days before maintenance to send reminder', 'SYSTEM'),
('license_expiry_reminder_days', '30', 'Days before license expiry to send reminder', 'SYSTEM'),
('insurance_expiry_reminder_days', '30', 'Days before insurance expiry to send reminder', 'SYSTEM');

-- Create indexes for performance
CREATE INDEX idx_requests_date_status ON transport_requests(request_date, status);
CREATE INDEX idx_vehicles_status_type ON vehicles(status, type);
CREATE INDEX idx_drivers_status_rating ON drivers(status, rating);

-- Create views for common queries
CREATE VIEW active_vehicles AS
SELECT * FROM vehicles WHERE is_active = TRUE AND status IN ('available', 'in_use');

CREATE VIEW active_drivers AS
SELECT * FROM drivers WHERE is_active = TRUE AND status IN ('active', 'on_trip');

CREATE VIEW pending_requests AS
SELECT r.*, u.first_name, u.last_name, u.department 
FROM transport_requests r 
JOIN users u ON r.employee_id = u.employee_id 
WHERE r.status = 'pending';

-- Grant permissions to application user
GRANT SELECT, INSERT, UPDATE, DELETE ON hal_transport.* TO 'hal_user'@'localhost';
GRANT EXECUTE ON hal_transport.* TO 'hal_user'@'localhost';

COMMIT;
