@echo off
echo 🎯 Générateur de Cas de Test avec Gemini AI
echo ===========================================
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

REM Check if GEMINI_API_KEY is set
if "%GEMINI_API_KEY%"=="" (
    echo GEMINI_API_KEY environment variable not found.
    echo If you used 'setx' command, please open a NEW command prompt and try again.
    echo.
    set /p API_KEY="Enter your Gemini API key (or press Enter to exit): "
    if "%API_KEY%"=="" (
        echo No API key provided. Exiting...
        pause
        exit /b 1
    )
    set GEMINI_API_KEY=%API_KEY%
)

REM Run the Python script
python generate_test_cases.py

echo.
echo Appuyez sur une touche pour quitter...
pause >nul