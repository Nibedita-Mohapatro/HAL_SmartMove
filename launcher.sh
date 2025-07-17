#!/bin/bash

# HAL Transport Management System - Development Launcher
# This script installs dependencies and runs both frontend and backend simultaneously

set -e  # Exit on any error

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
VENV_DIR="$BACKEND_DIR/venv"
LOG_DIR="$PROJECT_ROOT/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
print_header() {
    echo -e "\n${PURPLE}========================================${NC}"
    echo -e "${PURPLE}  $1${NC}"
    echo -e "${PURPLE}========================================${NC}\n"
}

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

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        local version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
        local major=$(echo $version | cut -d. -f1)
        local minor=$(echo $version | cut -d. -f2)
        
        if [ "$major" -eq 3 ] && [ "$minor" -ge 8 ]; then
            return 0
        fi
    fi
    return 1
}

# Function to check Node.js version
check_node_version() {
    if command_exists node; then
        local version=$(node --version | sed 's/v//' | cut -d. -f1)
        if [ "$version" -ge 16 ]; then
            return 0
        fi
    fi
    return 1
}

# Function to install system dependencies
install_system_dependencies() {
    print_step "Checking and installing system dependencies..."
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt-get; then
            # Ubuntu/Debian
            print_status "Detected Ubuntu/Debian system"
            
            # Update package list
            print_status "Updating package list..."
            sudo apt-get update
            
            # Install Python if not available or version is too old
            if ! check_python_version; then
                print_status "Installing Python 3.8+..."
                sudo apt-get install -y python3 python3-pip python3-venv python3-dev
            fi
            
            # Install Node.js if not available or version is too old
            if ! check_node_version; then
                print_status "Installing Node.js 16+..."
                curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
                sudo apt-get install -y nodejs
            fi
            
            # Install MySQL if not installed
            if ! command_exists mysql; then
                print_status "Installing MySQL..."
                sudo apt-get install -y mysql-server mysql-client
                print_warning "Please configure MySQL root password and create database"
            fi
            
            # Install other dependencies
            print_status "Installing additional dependencies..."
            sudo apt-get install -y curl wget git build-essential
            
        elif command_exists yum; then
            # CentOS/RHEL/Fedora
            print_status "Detected CentOS/RHEL/Fedora system"
            print_warning "Please install Python 3.8+, Node.js 16+, and MySQL manually"
        fi
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        print_status "Detected macOS system"
        
        # Check if Homebrew is installed
        if ! command_exists brew; then
            print_status "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        # Install dependencies using Homebrew
        if ! check_python_version; then
            print_status "Installing Python..."
            brew install python@3.11
        fi
        
        if ! check_node_version; then
            print_status "Installing Node.js..."
            brew install node
        fi
        
        if ! command_exists mysql; then
            print_status "Installing MySQL..."
            brew install mysql
            brew services start mysql
        fi
    fi
}

# Function to setup Python virtual environment
setup_python_env() {
    print_step "Setting up Python virtual environment..."
    
    cd "$BACKEND_DIR"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install Python dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    print_success "Python environment setup completed"
}

# Function to setup Node.js environment
setup_node_env() {
    print_step "Setting up Node.js environment..."
    
    cd "$FRONTEND_DIR"
    
    # Install Node.js dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    print_success "Node.js environment setup completed"
}

# Function to setup database
setup_database() {
    print_step "Setting up database..."
    
    # Check if MySQL is running
    if command_exists systemctl; then
        sudo systemctl start mysql 2>/dev/null || true
    elif command_exists brew; then
        brew services start mysql 2>/dev/null || true
    fi
    
    # Run database setup if file exists
    if [ -f "$BACKEND_DIR/database_setup.sql" ]; then
        print_status "Setting up database schema..."
        mysql -u root -p < "$BACKEND_DIR/database_setup.sql" 2>/dev/null || {
            print_warning "Database setup failed. Please run manually:"
            print_warning "mysql -u root -p < backend/database_setup.sql"
        }
    fi
    
    # Run Python database setup if available
    if [ -f "$BACKEND_DIR/setup_db.py" ]; then
        print_status "Running Python database setup..."
        cd "$BACKEND_DIR"
        source venv/bin/activate
        python setup_db.py || print_warning "Python database setup failed"
    fi
}

# Function to create log directory
create_log_dir() {
    if [ ! -d "$LOG_DIR" ]; then
        mkdir -p "$LOG_DIR"
        print_status "Created log directory: $LOG_DIR"
    fi
}

# Function to run backend
run_backend() {
    print_status "Starting backend server..."
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # Start the main application
    if [ -f "main.py" ]; then
        uvicorn main:app --host 0.0.0.0 --port 8000 --reload > "$LOG_DIR/backend.log" 2>&1 &
    else
        print_error "Backend entry point main.py not found"
        exit 1
    fi
    
    BACKEND_PID=$!
    echo $BACKEND_PID > "$LOG_DIR/backend.pid"
    print_success "Backend started with PID: $BACKEND_PID"
}

# Function to run frontend
run_frontend() {
    print_status "Starting frontend server..."
    cd "$FRONTEND_DIR"
    npm start > "$LOG_DIR/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$LOG_DIR/frontend.pid"
    print_success "Frontend started with PID: $FRONTEND_PID"
}

# Function to cleanup processes
cleanup() {
    print_status "Shutting down servers..."
    
    if [ -f "$LOG_DIR/backend.pid" ]; then
        BACKEND_PID=$(cat "$LOG_DIR/backend.pid")
        kill $BACKEND_PID 2>/dev/null || true
        rm -f "$LOG_DIR/backend.pid"
        print_status "Backend server stopped"
    fi
    
    if [ -f "$LOG_DIR/frontend.pid" ]; then
        FRONTEND_PID=$(cat "$LOG_DIR/frontend.pid")
        kill $FRONTEND_PID 2>/dev/null || true
        rm -f "$LOG_DIR/frontend.pid"
        print_status "Frontend server stopped"
    fi
    
    print_success "Cleanup completed"
    exit 0
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --install-deps    Install system dependencies (requires sudo)"
    echo "  --setup-only      Only setup environments, don't run servers"
    echo "  --backend-only    Run only backend server"
    echo "  --frontend-only   Run only frontend server"
    echo "  --help           Show this help message"
    echo ""
    echo "Default: Setup environments and run both servers"
}

# Main execution
main() {
    print_header "HAL Transport Management System Launcher"
    
    # Parse command line arguments
    INSTALL_DEPS=false
    SETUP_ONLY=false
    BACKEND_ONLY=false
    FRONTEND_ONLY=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --install-deps)
                INSTALL_DEPS=true
                shift
                ;;
            --setup-only)
                SETUP_ONLY=true
                shift
                ;;
            --backend-only)
                BACKEND_ONLY=true
                shift
                ;;
            --frontend-only)
                FRONTEND_ONLY=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Install system dependencies if requested
    if [ "$INSTALL_DEPS" = true ]; then
        install_system_dependencies
    fi
    
    # Verify required commands
    if ! check_python_version; then
        print_error "Python 3.8+ is required but not found"
        print_warning "Run with --install-deps to install system dependencies"
        exit 1
    fi
    
    if ! check_node_version; then
        print_error "Node.js 16+ is required but not found"
        print_warning "Run with --install-deps to install system dependencies"
        exit 1
    fi
    
    # Create log directory
    create_log_dir
    
    # Setup environments
    if [ "$FRONTEND_ONLY" != true ]; then
        setup_python_env
        setup_database
    fi
    
    if [ "$BACKEND_ONLY" != true ]; then
        setup_node_env
    fi
    
    # Exit if setup-only mode
    if [ "$SETUP_ONLY" = true ]; then
        print_success "Environment setup completed"
        exit 0
    fi
    
    # Setup signal handlers for cleanup
    trap cleanup SIGINT SIGTERM
    
    # Start servers
    if [ "$FRONTEND_ONLY" != true ]; then
        run_backend
        sleep 3  # Give backend time to start
    fi
    
    if [ "$BACKEND_ONLY" != true ]; then
        run_frontend
        sleep 3  # Give frontend time to start
    fi
    
    # Show status
    print_header "Application Status"
    if [ "$FRONTEND_ONLY" != true ]; then
        print_success "Backend running at: http://localhost:8000"
        print_status "Backend API docs: http://localhost:8000/docs"
    fi
    
    if [ "$BACKEND_ONLY" != true ]; then
        print_success "Frontend running at: http://localhost:3000"
    fi
    
    print_status "Logs available in: $LOG_DIR"
    print_warning "Press Ctrl+C to stop all servers"
    
    # Wait for user interrupt
    while true; do
        sleep 1
    done
}

# Run main function
main "$@"
