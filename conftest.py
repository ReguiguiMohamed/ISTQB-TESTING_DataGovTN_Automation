import pytest
import os
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from config import Config

def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default=Config.DEFAULT_BROWSER, help="Browser: chrome, firefox, edge")
    parser.addoption("--remote", action="store_true", default=False, help="Run on Docker Selenium Grid")
    parser.addoption("--headless", action="store_true", default=False, help="Run in headless mode")

@pytest.fixture(scope="session")
def base_url():
    return Config.BASE_URL

@pytest.fixture(scope="function")
def browser(request):
    """
    Initializes the WebDriver based on CLI options and Config.
    """
    browser_name = request.config.getoption("--browser").lower()
    use_remote = request.config.getoption("--remote")
    headless = request.config.getoption("--headless") or Config.HEADLESS

    options = None

    if browser_name == "chrome":
        from selenium.webdriver.chrome.options import Options
        options = Options()
        if headless: options.add_argument("--headless=new")

    elif browser_name == "firefox":
        from selenium.webdriver.firefox.options import Options
        options = Options()
        if headless: options.add_argument("-headless")

    elif browser_name == "edge":
        from selenium.webdriver.edge.options import Options
        options = Options()
        if headless: options.add_argument("--headless=new")

    # Common options
    if options:
        options.add_argument(f"--window-size={Config.WINDOW_WIDTH},{Config.WINDOW_HEIGHT}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    driver = None
    if use_remote:
        # Docker Execution
        driver = webdriver.Remote(command_executor=Config.REMOTE_URL, options=options)
    else:
        # Local Execution
        if browser_name == "chrome":
            driver = webdriver.Chrome(options=options)
        elif browser_name == "firefox":
            driver = webdriver.Firefox(options=options)
        elif browser_name == "edge":
            driver = webdriver.Edge(options=options)
        elif browser_name == "safari":
            driver = webdriver.Safari()
        else:
            raise ValueError(f"Unsupported browser: {browser_name}")

    driver.implicitly_wait(Config.IMPLICIT_WAIT)

    yield driver

    driver.quit()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture screenshot on failure."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("browser")
        if driver:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            # Clean filename
            node_id = report.nodeid.replace("::", "_").replace("/", "_").replace("\\", "_")
            file_name = f"reports/screenshots/{node_id}_{timestamp}.png"

            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            try:
                driver.save_screenshot(file_name)
                print(f"\nScreenshot saved: {file_name}")
            except Exception as e:
                print(f"Failed to save screenshot: {e}")
