@echo off
echo Starting cross-browser testing...

echo Opening Selenium Grid dashboard in browser...
start "" "http://localhost:4444"

echo Starting parallel cross-browser tests...
echo Running tests on Chrome, Firefox, and Edge simultaneously...

REM Change to project root directory
cd ..\..

REM Run all browser tests in parallel using the parallel execution script
python run_parallel_cross_browser.py

REM Return to the cross_browser directory
cd tests\cross_browser

echo.
echo All parallel cross-browser tests completed!
echo Individual reports are available in the reports folder.
echo View Selenium Grid dashboard: http://localhost:4444
echo Press any key to exit...
pause >nul