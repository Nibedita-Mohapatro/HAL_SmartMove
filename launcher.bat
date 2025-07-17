@echo off
REM HAL Transport Management System - Windows Launcher
REM This script installs dependencies and runs both frontend and backend simultaneously

setlocal enabledelayedexpansion

REM Configuration
set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%backend"
set "FRONTEND_DIR=%PROJECT_ROOT%frontend"
set "VENV_DIR=%BACKEND_DIR%\venv"
set "LOG_DIR=%PROJECT_ROOT%logs"

REM Colors (limited support in Windows)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "PURPLE=[95m"
set "CYAN=[96m"
set "NC=[0m"

echo.
echo %PURPLE%========================================%NC%
echo %PURPLE%  HAL Transport Management System%NC%
echo %PURPLE%  Windows Launcher%NC%
echo %PURPLE%========================================%NC%
echo.

REM Function to check if command exists
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%NC% Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%NC% Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)

where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%NC% npm is not installed or not in PATH
    echo Please install Node.js which includes npm
    pause
    exit /b 1
)

echo %BLUE%[INFO]%NC% Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%NC% Failed to get Python version
    pause
    exit /b 1
)

echo %BLUE%[INFO]%NC% Checking Node.js version...
node --version
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%NC% Failed to get Node.js version
    pause
    exit /b 1
)

REM Create log directory
if not exist "%LOG_DIR%" (
    mkdir "%LOG_DIR%"
    echo %BLUE%[INFO]%NC% Created log directory: %LOG_DIR%
)

REM Setup Python virtual environment
echo.
echo %CYAN%[STEP]%NC% Setting up Python virtual environment...
cd /d "%BACKEND_DIR%"

if not exist "%VENV_DIR%" (
    echo %BLUE%[INFO]%NC% Creating Python virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo %RED%[ERROR]%NC% Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo %BLUE%[INFO]%NC% Activating virtual environment...
call venv\Scripts\activate.bat

echo %BLUE%[INFO]%NC% Upgrading pip...
python -m pip install --upgrade pip

echo %BLUE%[INFO]%NC% Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%NC% Failed to install Python dependencies
    pause
    exit /b 1
)

echo %GREEN%[SUCCESS]%NC% Python environment setup completed

REM Setup Node.js environment
echo.
echo %CYAN%[STEP]%NC% Setting up Node.js environment...
cd /d "%FRONTEND_DIR%"

echo %BLUE%[INFO]%NC% Installing Node.js dependencies...
npm install
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%NC% Failed to install Node.js dependencies
    pause
    exit /b 1
)

echo %GREEN%[SUCCESS]%NC% Node.js environment setup completed

REM Setup database (optional)
echo.
echo %CYAN%[STEP]%NC% Database setup...
echo %YELLOW%[WARNING]%NC% Please ensure MySQL is installed and running
echo %YELLOW%[WARNING]%NC% Run database setup manually if needed:
echo %YELLOW%[WARNING]%NC% mysql -u root -p ^< backend\database_setup.sql

REM Start backend server
echo.
echo %BLUE%[INFO]%NC% Starting backend server...
cd /d "%BACKEND_DIR%"
call venv\Scripts\activate.bat

REM Start the main application
if exist "main.py" (
    start "Backend Server" cmd /k "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
) else (
    echo %RED%[ERROR]%NC% Backend entry point main.py not found
    pause
    exit /b 1
)

echo %GREEN%[SUCCESS]%NC% Backend server starting...

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server
echo.
echo %BLUE%[INFO]%NC% Starting frontend server...
cd /d "%FRONTEND_DIR%"
start "Frontend Server" cmd /k "npm start"

echo %GREEN%[SUCCESS]%NC% Frontend server starting...

REM Wait a moment for frontend to start
timeout /t 3 /nobreak >nul

REM Show status
echo.
echo %PURPLE%========================================%NC%
echo %PURPLE%  Application Status%NC%
echo %PURPLE%========================================%NC%
echo.
echo %GREEN%[SUCCESS]%NC% Backend running at: http://localhost:8000
echo %BLUE%[INFO]%NC% Backend API docs: http://localhost:8000/docs
echo %GREEN%[SUCCESS]%NC% Frontend running at: http://localhost:3000
echo.
echo %BLUE%[INFO]%NC% Both servers are running in separate windows
echo %YELLOW%[WARNING]%NC% Close the server windows to stop the application
echo.

REM Open browser to frontend
echo %BLUE%[INFO]%NC% Opening application in browser...
start http://localhost:3000

echo %GREEN%[SUCCESS]%NC% Application launched successfully!
echo.
echo Press any key to exit this launcher window...
pause >nul

endlocal
