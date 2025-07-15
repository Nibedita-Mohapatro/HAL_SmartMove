-- HAL Smart Vehicle Transport Management System Database Schema
-- MySQL 8.0+ Compatible

CREATE DATABASE IF NOT EXISTS hal_transport_system;
USE hal_transport_system;

-- Enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- Users table (Employees and Admins)
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(15),
    department VARCHAR(100),
    designation VARCHAR(100),
    role ENUM('employee', 'admin', 'super_admin') DEFAULT 'employee',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    
    INDEX idx_employee_id (employee_id),
    INDEX idx_email (email),
    INDEX idx_department (department),
    INDEX idx_role (role)
);

-- Vehicles table
CREATE TABLE vehicles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    vehicle_number VARCHAR(20) UNIQUE NOT NULL,
    vehicle_type ENUM('bus', 'car', 'van', 'shuttle') NOT NULL,
    capacity INT NOT NULL,
    fuel_type ENUM('petrol', 'diesel', 'electric', 'hybrid') NOT NULL,
    model VARCHAR(50),
    year_of_manufacture YEAR,
    insurance_expiry DATE,
    fitness_certificate_expiry DATE,
    is_active BOOLEAN DEFAULT TRUE,
    current_location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_vehicle_number (vehicle_number),
    INDEX idx_vehicle_type (vehicle_type),
    INDEX idx_is_active (is_active)
);

-- Drivers table
CREATE TABLE drivers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id VARCHAR(20) UNIQUE NOT NULL,
    license_number VARCHAR(30) UNIQUE NOT NULL,
    license_expiry DATE NOT NULL,
    phone VARCHAR(15) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    experience_years INT DEFAULT 0,
    is_available BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_employee_id (employee_id),
    INDEX idx_license_number (license_number),
    INDEX idx_is_available (is_available)
);

-- Routes table (Predefined routes)
CREATE TABLE routes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    route_name VARCHAR(100) NOT NULL,
    origin VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    distance_km DECIMAL(8,2),
    estimated_duration_minutes INT,
    route_type ENUM('fixed', 'shuttle', 'adhoc') DEFAULT 'fixed',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_route_name (route_name),
    INDEX idx_origin (origin),
    INDEX idx_destination (destination),
    INDEX idx_route_type (route_type)
);

-- Transport requests table
CREATE TABLE transport_requests (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    origin VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    request_date DATE NOT NULL,
    request_time TIME NOT NULL,
    passenger_count INT DEFAULT 1,
    purpose TEXT,
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    status ENUM('pending', 'approved', 'rejected', 'completed', 'cancelled') DEFAULT 'pending',
    approved_by INT NULL,
    approved_at TIMESTAMP NULL,
    rejection_reason TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL,
    
    INDEX idx_user_id (user_id),
    INDEX idx_request_date (request_date),
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_approved_by (approved_by)
);

-- Vehicle assignments table
CREATE TABLE vehicle_assignments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    request_id INT NOT NULL,
    vehicle_id INT NOT NULL,
    driver_id INT NOT NULL,
    assigned_by INT NOT NULL,
    assignment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estimated_departure TIME,
    estimated_arrival TIME,
    actual_departure TIME NULL,
    actual_arrival TIME NULL,
    status ENUM('assigned', 'in_progress', 'completed', 'cancelled') DEFAULT 'assigned',
    notes TEXT,
    
    FOREIGN KEY (request_id) REFERENCES transport_requests(id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE RESTRICT,
    FOREIGN KEY (driver_id) REFERENCES drivers(id) ON DELETE RESTRICT,
    FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE RESTRICT,
    
    INDEX idx_request_id (request_id),
    INDEX idx_vehicle_id (vehicle_id),
    INDEX idx_driver_id (driver_id),
    INDEX idx_assignment_date (assignment_date),
    INDEX idx_status (status)
);

-- Scheduled trips table (Regular/recurring trips)
CREATE TABLE scheduled_trips (
    id INT PRIMARY KEY AUTO_INCREMENT,
    route_id INT NOT NULL,
    vehicle_id INT NOT NULL,
    driver_id INT NOT NULL,
    trip_name VARCHAR(100) NOT NULL,
    departure_time TIME NOT NULL,
    days_of_week SET('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'),
    start_date DATE NOT NULL,
    end_date DATE NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE RESTRICT,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE RESTRICT,
    FOREIGN KEY (driver_id) REFERENCES drivers(id) ON DELETE RESTRICT,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT,
    
    INDEX idx_route_id (route_id),
    INDEX idx_vehicle_id (vehicle_id),
    INDEX idx_driver_id (driver_id),
    INDEX idx_departure_time (departure_time),
    INDEX idx_is_active (is_active)
);

-- Trip history table (Completed trips for analytics)
CREATE TABLE trip_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    request_id INT NULL,
    scheduled_trip_id INT NULL,
    vehicle_id INT NOT NULL,
    driver_id INT NOT NULL,
    origin VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    trip_date DATE NOT NULL,
    departure_time TIME NOT NULL,
    arrival_time TIME NOT NULL,
    passenger_count INT DEFAULT 1,
    distance_km DECIMAL(8,2),
    fuel_consumed_liters DECIMAL(6,2),
    trip_cost DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (request_id) REFERENCES transport_requests(id) ON DELETE SET NULL,
    FOREIGN KEY (scheduled_trip_id) REFERENCES scheduled_trips(id) ON DELETE SET NULL,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE RESTRICT,
    FOREIGN KEY (driver_id) REFERENCES drivers(id) ON DELETE RESTRICT,
    
    INDEX idx_trip_date (trip_date),
    INDEX idx_vehicle_id (vehicle_id),
    INDEX idx_driver_id (driver_id),
    INDEX idx_origin (origin),
    INDEX idx_destination (destination)
);

-- Vehicle maintenance table
CREATE TABLE vehicle_maintenance (
    id INT PRIMARY KEY AUTO_INCREMENT,
    vehicle_id INT NOT NULL,
    maintenance_type ENUM('routine', 'repair', 'inspection', 'emergency') NOT NULL,
    description TEXT NOT NULL,
    maintenance_date DATE NOT NULL,
    cost DECIMAL(10,2),
    next_maintenance_date DATE,
    performed_by VARCHAR(100),
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
    
    INDEX idx_vehicle_id (vehicle_id),
    INDEX idx_maintenance_date (maintenance_date),
    INDEX idx_maintenance_type (maintenance_type),
    INDEX idx_is_completed (is_completed)
);

-- System notifications table
CREATE TABLE notifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('info', 'success', 'warning', 'error') DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    INDEX idx_user_id (user_id),
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at)
);

-- ML model predictions table (for storing ML predictions)
CREATE TABLE ml_predictions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    model_type ENUM('demand_forecast', 'route_optimization', 'vehicle_assignment') NOT NULL,
    input_data JSON NOT NULL,
    prediction_result JSON NOT NULL,
    confidence_score DECIMAL(5,4),
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_accurate BOOLEAN NULL, -- To be updated after actual results
    
    INDEX idx_model_type (model_type),
    INDEX idx_prediction_date (prediction_date)
);

-- Create views for common queries
CREATE VIEW active_requests AS
SELECT 
    tr.*,
    u.first_name,
    u.last_name,
    u.department,
    u.phone
FROM transport_requests tr
JOIN users u ON tr.user_id = u.id
WHERE tr.status IN ('pending', 'approved');

CREATE VIEW vehicle_utilization AS
SELECT 
    v.id,
    v.vehicle_number,
    v.vehicle_type,
    v.capacity,
    COUNT(va.id) as total_assignments,
    COUNT(CASE WHEN va.status = 'completed' THEN 1 END) as completed_trips
FROM vehicles v
LEFT JOIN vehicle_assignments va ON v.id = va.vehicle_id
WHERE v.is_active = TRUE
GROUP BY v.id;

-- Insert sample data for testing
INSERT INTO users (employee_id, email, password_hash, first_name, last_name, department, role) VALUES
('HAL001', 'admin@hal.co.in', '$2b$12$example_hash', 'System', 'Administrator', 'IT', 'super_admin'),
('HAL002', 'transport@hal.co.in', '$2b$12$example_hash', 'Transport', 'Manager', 'Transport', 'admin'),
('HAL003', 'john.doe@hal.co.in', '$2b$12$example_hash', 'John', 'Doe', 'Engineering', 'employee');

INSERT INTO vehicles (vehicle_number, vehicle_type, capacity, fuel_type, model) VALUES
('KA01AB1234', 'bus', 40, 'diesel', 'Tata Starbus'),
('KA01CD5678', 'car', 4, 'petrol', 'Maruti Suzuki Dzire'),
('KA01EF9012', 'van', 12, 'diesel', 'Mahindra Bolero');

INSERT INTO drivers (employee_id, license_number, phone, first_name, last_name, experience_years) VALUES
('DRV001', 'KA0120230001', '9876543210', 'Ravi', 'Kumar', 10),
('DRV002', 'KA0120230002', '9876543211', 'Suresh', 'Singh', 8);

INSERT INTO routes (route_name, origin, destination, distance_km, estimated_duration_minutes, route_type) VALUES
('HAL Main Gate to Whitefield', 'HAL Main Gate, Bangalore', 'Whitefield, Bangalore', 15.5, 45, 'fixed'),
('HAL to Electronic City', 'HAL Complex, Bangalore', 'Electronic City, Bangalore', 25.2, 60, 'shuttle'),
('HAL to Airport', 'HAL Headquarters', 'Kempegowda International Airport', 45.0, 90, 'adhoc');

-- Performance optimization indexes
CREATE INDEX idx_transport_requests_date_status ON transport_requests(request_date, status);
CREATE INDEX idx_vehicle_assignments_date_status ON vehicle_assignments(assignment_date, status);
CREATE INDEX idx_trip_history_date_vehicle ON trip_history(trip_date, vehicle_id);
CREATE INDEX idx_users_department_role ON users(department, role);

-- Triggers for audit trail
DELIMITER //

CREATE TRIGGER tr_transport_requests_update
BEFORE UPDATE ON transport_requests
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END//

CREATE TRIGGER tr_vehicle_assignments_update
BEFORE UPDATE ON vehicle_assignments
FOR EACH ROW
BEGIN
    -- Auto-complete request when assignment is completed
    IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
        UPDATE transport_requests
        SET status = 'completed', updated_at = CURRENT_TIMESTAMP
        WHERE id = NEW.request_id;
    END IF;
END//

DELIMITER ;

-- Stored procedures for common operations
DELIMITER //

CREATE PROCEDURE GetAvailableVehicles(IN request_date DATE, IN request_time TIME)
BEGIN
    SELECT v.*
    FROM vehicles v
    WHERE v.is_active = TRUE
    AND v.id NOT IN (
        SELECT va.vehicle_id
        FROM vehicle_assignments va
        JOIN transport_requests tr ON va.request_id = tr.id
        WHERE tr.request_date = request_date
        AND tr.status IN ('approved', 'completed')
        AND (
            (va.estimated_departure <= request_time AND va.estimated_arrival >= request_time)
            OR (va.estimated_departure >= request_time AND va.estimated_departure <= ADDTIME(request_time, '02:00:00'))
        )
    );
END//

CREATE PROCEDURE GetDemandAnalytics(IN start_date DATE, IN end_date DATE)
BEGIN
    SELECT
        DATE(tr.request_date) as date,
        COUNT(*) as total_requests,
        COUNT(CASE WHEN tr.status = 'approved' THEN 1 END) as approved_requests,
        COUNT(CASE WHEN tr.status = 'rejected' THEN 1 END) as rejected_requests,
        AVG(tr.passenger_count) as avg_passengers,
        tr.origin,
        tr.destination
    FROM transport_requests tr
    WHERE tr.request_date BETWEEN start_date AND end_date
    GROUP BY DATE(tr.request_date), tr.origin, tr.destination
    ORDER BY date DESC;
END//

DELIMITER ;
