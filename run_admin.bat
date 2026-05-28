@echo off
setlocal

:: Set environment variables
set FLASK_APP=admin.py
set FLASK_ENV=development
set SECRET_KEY=your-secret-key-change-this-in-production

:: Create necessary directories if they don't exist
if not exist "admin\static" mkdir "admin\static"
if not exist "admin\static\css" mkdir "admin\static\css"
if not exist "admin\static\js" mkdir "admin\static\js"
if not exist "admin\static\images" mkdir "admin\static\images"
if not exist "admin\templates\admin" mkdir "admin\templates\admin"
if not exist "admin\uploads" mkdir "admin\uploads"
if not exist "admin\backups" mkdir "admin\backups"

echo Starting Admin Panel...
echo ==========================
echo Admin Panel will be available at: http://localhost:5001/admin
echo Default credentials:
echo Username: admin
echo Password: admin123
echo ==========================

:: Open browser
start http://localhost:5001/admin

echo Press Ctrl+C to stop the server

:: Run the Flask application
python run_admin.py
