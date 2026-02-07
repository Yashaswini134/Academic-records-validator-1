@echo off
echo ===================================================
echo Starting Certificate Verification System
echo ===================================================

echo.
echo [1/2] Starting Backend Server...
start "Backend Server" cmd /k "python backend/app.py"

echo.
echo [2/2] Starting Frontend Application...
cd frontend
start "Frontend App" cmd /k "npm start"

echo.
echo System started! 
echo Backend running on http://localhost:5000
echo Frontend running on http://localhost:3000
echo.
echo Press any key to exit this launcher (servers will keep running)...
pause
exit
