#!/bin/bash

# HAL Transport Management System - Automated Setup Script
# This script installs all dependencies and starts both frontend and backend applications

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Node.js
    if command_exists node; then
        NODE_VERSION=$(node --version | cut -d'v' -f2)
        print_success "Node.js found: v$NODE_VERSION"
    else
        print_error "Node.js is not installed. Please install Node.js 16+ from https://nodejs.org/"
        exit 1
    fi
    
    # Check npm
    if command_exists npm; then
        NPM_VERSION=$(npm --version)
        print_success "npm found: v$NPM_VERSION"
    else
        print_error "npm is not installed. Please install npm."
        exit 1
    fi
    
    # Check Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python found: v$PYTHON_VERSION"
    else
        print_error "Python 3 is not installed. Please install Python 3.8+ from https://python.org/"
        exit 1
    fi
    
    # Check pip
    if command_exists pip3; then
        PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
        print_success "pip found: v$PIP_VERSION"
    else
        print_error "pip3 is not installed. Please install pip3."
        exit 1
    fi
    
    # Check MySQL (optional check)
    if command_exists mysql; then
        MYSQL_VERSION=$(mysql --version | cut -d' ' -f3)
        print_success "MySQL found: v$MYSQL_VERSION"
    else
        print_warning "MySQL not found. Please ensure MySQL is installed and running."
        print_warning "You can install MySQL from: https://dev.mysql.com/downloads/"
    fi
    
    print_success "All requirements check completed!"
}

# Function to setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created!"
    else
        print_status "Virtual environment already exists."
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    print_success "Backend dependencies installed!"
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating backend .env file..."
        cat > .env << EOF
# Database Configuration
DATABASE_URL=mysql://root:password@localhost/hal_transport_db

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Maps API (optional)
GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here

# Environment
ENVIRONMENT=development
EOF
        print_success "Backend .env file created!"
        print_warning "Please update the database credentials in backend/.env"
    else
        print_status "Backend .env file already exists."
    fi
    
    cd ..
}

# Function to setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    print_success "Frontend dependencies installed!"
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating frontend .env file..."
        cat > .env << EOF
# API Configuration
REACT_APP_API_URL=http://localhost:8000

# Google Maps API (optional)
REACT_APP_GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here

# Environment
REACT_APP_ENVIRONMENT=development
EOF
        print_success "Frontend .env file created!"
    else
        print_status "Frontend .env file already exists."
    fi
    
    cd ..
}

# Function to setup database
setup_database() {
    print_status "Setting up database..."
    
    # Check if MySQL is running
    if ! pgrep -x "mysqld" > /dev/null; then
        print_warning "MySQL doesn't appear to be running."
        print_warning "Please start MySQL service and run this script again."
        print_warning "On Ubuntu/Debian: sudo systemctl start mysql"
        print_warning "On macOS: brew services start mysql"
        return 1
    fi
    
    print_status "Creating database (if it doesn't exist)..."
    
    # Try to create database
    mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS hal_transport_db;" 2>/dev/null || {
        print_warning "Could not create database automatically."
        print_warning "Please create the database manually:"
        print_warning "mysql -u root -p"
        print_warning "CREATE DATABASE hal_transport_db;"
    }
    
    print_success "Database setup completed!"
}

# Function to start applications
start_applications() {
    print_status "Starting applications..."
    
    # Start backend in background
    print_status "Starting backend server..."
    cd backend
    source venv/bin/activate
    nohup python main.py > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    cd ..
    
    # Wait a moment for backend to start
    sleep 3
    
    # Check if backend is running
    if kill -0 $BACKEND_PID 2>/dev/null; then
        print_success "Backend server started! (PID: $BACKEND_PID)"
        print_status "Backend logs: tail -f backend.log"
    else
        print_error "Failed to start backend server!"
        return 1
    fi
    
    # Start frontend in background
    print_status "Starting frontend server..."
    cd frontend
    nohup npm start > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    cd ..
    
    # Wait for frontend to start
    sleep 5
    
    # Check if frontend is running
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        print_success "Frontend server started! (PID: $FRONTEND_PID)"
        print_status "Frontend logs: tail -f frontend.log"
    else
        print_error "Failed to start frontend server!"
        return 1
    fi
}

# Function to display final information
display_info() {
    echo ""
    echo "🎉 HAL Transport Management System Setup Complete!"
    echo "=================================================="
    echo ""
    echo "📱 Frontend Application: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo ""
    echo "👥 Default Login Credentials:"
    echo "   Admin: HAL001 / admin123"
    echo "   Transport: HAL002 / transport123"
    echo "   Employee: HAL003 / employee123"
    echo ""
    echo "📋 Useful Commands:"
    echo "   Stop Backend: kill \$(cat backend.pid)"
    echo "   Stop Frontend: kill \$(cat frontend.pid)"
    echo "   View Backend Logs: tail -f backend.log"
    echo "   View Frontend Logs: tail -f frontend.log"
    echo ""
    echo "⚠️  Important Notes:"
    echo "   - Update database credentials in backend/.env"
    echo "   - Add Google Maps API key for GPS features"
    echo "   - Check logs if applications don't start properly"
    echo ""
}

# Function to cleanup on exit
cleanup() {
    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            print_status "Stopping backend server..."
            kill $BACKEND_PID
        fi
        rm -f backend.pid
    fi
    
    if [ -f "frontend.pid" ]; then
        FRONTEND_PID=$(cat frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            print_status "Stopping frontend server..."
            kill $FRONTEND_PID
        fi
        rm -f frontend.pid
    fi
}

# Main execution
main() {
    echo "🚗 HAL Transport Management System - Setup Script"
    echo "================================================="
    echo ""
    
    # Check if we're in the right directory
    if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
        print_error "Please run this script from the project root directory."
        print_error "The directory should contain 'frontend' and 'backend' folders."
        exit 1
    fi
    
    # Trap to cleanup on script exit
    trap cleanup EXIT
    
    # Run setup steps
    check_requirements
    echo ""
    
    setup_backend
    echo ""
    
    setup_frontend
    echo ""
    
    setup_database
    echo ""
    
    start_applications
    echo ""
    
    display_info
    
    # Keep script running to maintain processes
    print_status "Setup complete! Press Ctrl+C to stop all services."
    
    # Wait for user interrupt
    while true; do
        sleep 1
    done
}

# Run main function
main "$@"
