@echo off
echo ========================================
echo Starting Predictive Maintenance Backend
echo ========================================
echo.

cd backend

echo Checking Python...
python --version
echo.

echo Starting Flask server on port 5000...
echo Press Ctrl+C to stop
echo.

python app.py

pause
