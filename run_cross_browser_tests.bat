@echo off
REM Script to run cross-browser tests with Docker Selenium Grid
REM Note: Safari is not supported with Docker; it requires local execution on macOS

set HUB_HOST=localhost
set HUB_PORT=4444

echo Starting cross-browser tests with Docker Selenium Grid...
echo Hub URL: http://%HUB_HOST%:%HUB_PORT%/wd/hub

if "%1"=="" (
    echo Usage: run_cross_browser_tests.bat [test_file_or_directory]
    echo Example: run_cross_browser_tests.bat tests/cross_browser/
    echo Example: run_cross_browser_tests.bat tests/cross_browser/test_smoke_cross_browser.py
    exit /b 1
)

echo.
echo Starting Docker containers if not already running...
docker-compose up -d

echo.
echo Waiting for Selenium Grid to be ready...
timeout /t 10 /nobreak >nul

echo.
echo Running tests on Chrome...
python -m pytest %1 --remote --browser=chrome --tb=short -v

echo.
echo Running tests on Firefox...
python -m pytest %1 --remote --browser=firefox --tb=short -v

echo.
echo Running tests on Edge...
python -m pytest %1 --remote --browser=edge --tb=short -v

echo.
echo Tests completed. Docker containers are still running.
echo Note: Safari tests are not supported with Docker. On macOS, run Safari tests separately with:
echo python -m pytest %1 --browser=safari
echo.
echo To stop Docker containers, run: docker-compose down