@echo off
echo 🎯 Lancement de l'interface web du Générateur de Cas de Test
echo =================================================================
echo.

REM Change to the script's directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python and make sure it's in your PATH.
    pause
    exit /b 1
)

echo Lancement de l'application web...
echo Ouvrez votre navigateur à l'adresse: http://localhost:5000
echo.

REM Run the web application
python web_app.py

echo.
echo Appuyez sur une touche pour quitter...
pause >nul