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
    
    driver = None
    options = None

    if browser_name == "chrome":
        from selenium.webdriver.chrome.options import Options
        options = Options()
        if headless:
            options.add_argument("--headless=new")
    elif browser_name == "firefox":
        from selenium.webdriver.firefox.options import Options
        options = Options()
        if headless:
            options.add_argument("-headless")
    elif browser_name == "edge":
        from selenium.webdriver.edge.options import Options
        options = Options()
        if headless:
            options.add_argument("--headless=new")
    
    if options:
        options.add_argument(f"--window-size={Config.WINDOW_WIDTH},{Config.WINDOW_HEIGHT}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

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
            from selenium.webdriver.edge.service import Service as EdgeService
            from webdriver_manager.microsoft import EdgeChromiumDriverManager
            driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
        else:
            raise ValueError(f"Unsupported browser: {browser_name}")

    driver.implicitly_wait(0)
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def logged_in_browser(browser):
    """
    Handles the login process and yields a logged-in browser instance.
    """
    from pages.auth_page import AuthPage
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import os

    auth_page = AuthPage(browser)
    auth_page.open_login_page()
    
    username = os.getenv("TEST_USERNAME")
    password = os.getenv("TEST_PASSWORD")
    if not username or not password:
        pytest.skip("Real login credentials not configured (TEST_USERNAME/TEST_PASSWORD).")

    auth_page.login(username, password)

    print("\\n---> Please solve the CAPTCHA manually. The test will continue automatically after login...")
    try:
        WebDriverWait(browser, 60).until(
            EC.url_contains("contributions")
        )
        print("Login successful, proceeding with test.")
    except Exception as e:
        pytest.fail(f"Login failed or redirect took too long after manual CAPTCHA solve. Error: {e}")

    yield browser # Provide the logged-in browser to the test


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


@pytest.fixture(scope="session")
def ui_documentation():
    from utils.ui_documentation import UIDocumentationSystem
    doc_system = UIDocumentationSystem()
    yield doc_system
    # This runs after ALL tests finish, guaranteed
    report_path = doc_system.generate_report("session_final")
    print(f"\nUI Documentation Report generated: {report_path}")


@pytest.fixture(scope="function")
def ui_monitor(browser, ui_documentation):
    """
    Gives tests access to the monitor, which automatically records
    to the global documentation system.
    """
    from utils.ui_monitor import UIStateMonitor
    monitor = UIStateMonitor(browser)
    # Link the monitor to the global doc system could be added here if needed
    return monitor


@pytest.fixture(scope="function")
def auto_setup_monitoring(browser, ui_monitor, ui_documentation):
    """
    Automatically set up monitoring for all page objects without repeated code
    """
    def _setup_page_monitoring(page_object):
        """Setup monitoring for a page object"""
        if hasattr(page_object, 'setup_monitoring'):
            page_object.setup_monitoring(ui_monitor=ui_monitor, doc_system=ui_documentation)
        return page_object
    return _setup_page_monitoring
