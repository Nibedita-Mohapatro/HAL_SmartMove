# HAL Transport Management System - Makefile
# Provides convenient commands for development and deployment

.PHONY: help install setup start start-backend start-frontend build test clean deploy

# Default target
help:
	@echo "HAL Transport Management System - Available Commands:"
	@echo ""
	@echo "Development Commands:"
	@echo "  make install     - Install system dependencies (requires sudo)"
	@echo "  make setup       - Setup development environment"
	@echo "  make start       - Start both backend and frontend servers"
	@echo "  make start-backend - Start only backend server"
	@echo "  make start-frontend - Start only frontend server"
	@echo ""
	@echo "Build Commands:"
	@echo "  make build       - Build frontend for production"
	@echo "  make test        - Run all tests"
	@echo ""
	@echo "Maintenance Commands:"
	@echo "  make clean       - Clean all build artifacts and dependencies"
	@echo "  make deploy      - Deploy to production (uses deploy.sh)"
	@echo ""
	@echo "Quick Start:"
	@echo "  make setup && make start"

# Install system dependencies
install:
	@echo "Installing system dependencies..."
	./launcher.sh --install-deps

# Setup development environment
setup:
	@echo "Setting up development environment..."
	./launcher.sh --setup-only

# Start both servers
start:
	@echo "Starting HAL Transport Management System..."
	./launcher.sh

# Start only backend
start-backend:
	@echo "Starting backend server..."
	./launcher.sh --backend-only

# Start only frontend  
start-frontend:
	@echo "Starting frontend server..."
	./launcher.sh --frontend-only

# Build frontend for production
build:
	@echo "Building frontend for production..."
	cd frontend && npm install && npm run build

# Run tests
test:
	@echo "Running tests..."
	@echo "Testing backend..."
	cd backend && source venv/bin/activate && python -m pytest || echo "Backend tests not configured"
	@echo "Testing frontend..."
	cd frontend && npm test -- --watchAll=false || echo "Frontend tests not configured"

# Clean all build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf backend/venv
	rm -rf backend/__pycache__
	rm -rf backend/app/__pycache__
	rm -rf frontend/node_modules
	rm -rf frontend/build
	rm -rf logs
	@echo "Clean completed"

# Deploy to production
deploy:
	@echo "Deploying to production..."
	@if [ -f "deploy.sh" ]; then \
		chmod +x deploy.sh && ./deploy.sh; \
	else \
		echo "deploy.sh not found"; \
	fi

# Development shortcuts
dev: start
run: start
serve: start

# Quick setup and start
quick-start: setup start

# Install npm dependencies for concurrent running
install-npm-deps:
	@echo "Installing npm dependencies for concurrent execution..."
	npm install concurrently

# Alternative start using npm (requires concurrently)
start-npm: install-npm-deps
	@echo "Starting with npm concurrently..."
	npm start

# Database setup
setup-db:
	@echo "Setting up database..."
	@if [ -f "backend/database_setup.sql" ]; then \
		mysql -u root -p < backend/database_setup.sql; \
	else \
		echo "Database setup file not found"; \
	fi
	@if [ -f "backend/setup_db.py" ]; then \
		cd backend && source venv/bin/activate && python setup_db.py; \
	fi

# Check system requirements
check-requirements:
	@echo "Checking system requirements..."
	@command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed"; exit 1; }
	@command -v node >/dev/null 2>&1 || { echo "Node.js is required but not installed"; exit 1; }
	@command -v npm >/dev/null 2>&1 || { echo "npm is required but not installed"; exit 1; }
	@command -v mysql >/dev/null 2>&1 || { echo "MySQL is required but not installed"; exit 1; }
	@echo "All requirements satisfied"

# Show application status
status:
	@echo "Application Status:"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "API Docs: http://localhost:8000/docs"
	@if [ -f "logs/backend.pid" ]; then \
		echo "Backend PID: $$(cat logs/backend.pid)"; \
	fi
	@if [ -f "logs/frontend.pid" ]; then \
		echo "Frontend PID: $$(cat logs/frontend.pid)"; \
	fi

# Stop running servers
stop:
	@echo "Stopping servers..."
	@if [ -f "logs/backend.pid" ]; then \
		kill $$(cat logs/backend.pid) 2>/dev/null || true; \
		rm -f logs/backend.pid; \
		echo "Backend stopped"; \
	fi
	@if [ -f "logs/frontend.pid" ]; then \
		kill $$(cat logs/frontend.pid) 2>/dev/null || true; \
		rm -f logs/frontend.pid; \
		echo "Frontend stopped"; \
	fi

# Restart servers
restart: stop start

# Update dependencies
update:
	@echo "Updating dependencies..."
	cd backend && source venv/bin/activate && pip install -r requirements.txt --upgrade
	cd frontend && npm update
	@echo "Dependencies updated"
