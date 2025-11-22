import os
import time
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

def pytest_addoption(parser):
    """Adds command-line options to pytest."""
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser to use for tests. Supported: chrome, firefox, edge.",
    )

@pytest.fixture(scope="session")
def browser(request):
    """
    Creates and manages a WebDriver instance for the test session.
    The browser type is determined by the --browser command-line option.
    """
    browser_name = request.config.getoption("--browser").lower()
    
    # Let Selenium Manager handle the drivers automatically
    if browser_name == "chrome":
        options = ChromeOptions()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
    elif browser_name == "firefox":
        options = FirefoxOptions()
        # Firefox doesn't have a simple '--start-maximized' argument
        # It's generally better to set a large window size
        options.add_argument("-width=1920")
        options.add_argument("-height=1080")
        driver = webdriver.Firefox(options=options)
    elif browser_name == "edge":
        options = EdgeOptions()
        options.add_argument("--start-maximized")
        driver = webdriver.Edge(options=options)
    else:
        raise ValueError(f"Unsupported browser: {browser_name}. Use 'chrome', 'firefox', or 'edge'.")

    driver.implicitly_wait(10)
    
    yield driver
    
    driver.quit()

@pytest.fixture(scope="session")
def base_url() -> str:
    """Provides the base URL for the application under test."""
    return "https://www.data.gov.tn/"

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Takes a screenshot on test failure and saves it to reports/screenshots/.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("browser")
        if driver is None:
            return  # Not a browser-based test

        screenshots_dir = Path("reports") / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        # Sanitize the test name for use as a filename
        safe_nodeid = report.nodeid.replace("::", "__").replace("/", "_").replace("\\", "_")
        filename = f"{safe_nodeid}_{timestamp}.png"
        filepath = screenshots_dir / filename

        try:
            driver.save_screenshot(str(filepath))
            print(f"\n[pytest] Screenshot saved to: {filepath}")
        except Exception as e:
            print(f"\n[pytest] Failed to save screenshot to {filepath}: {e}")
