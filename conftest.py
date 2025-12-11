import pytest
import os
import sys
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from config import Config

# Add project root to sys.path to allow for module imports
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

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
            from selenium.webdriver.chrome.service import Service as ChromeService
            from webdriver_manager.chrome import ChromeDriverManager
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        elif browser_name == "firefox":
            from selenium.webdriver.firefox.service import Service as FirefoxService
            from webdriver_manager.firefox import GeckoDriverManager
            driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
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
    """Capture screenshot on failure and store report for Jira integration."""
    outcome = yield
    report = outcome.get_result()

    # Store the report on the item object
    setattr(item, "report", report)

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

@pytest.fixture(scope="function")
def jira_reporter(request):
    """
    Fixture to automatically create a Jira ticket if a test fails.
    To use, add @pytest.mark.usefixtures("jira_reporter") to your test.
    """
    yield

    # This code runs after the test has finished
    report = getattr(request.node, "report", None)
    if report and report.failed:
        print("\nTest failed, creating Jira ticket...")
        try:
            from jira_automation_enhanced import JiraTicketCreator
            import os

            # Get Jira configuration
            jira_url = os.getenv("JIRA_URL")
            jira_username = os.getenv("JIRA_USERNAME")
            jira_api_token = os.getenv("JIRA_API_TOKEN")
            jira_project_key = os.getenv("JIRA_PROJECT_KEY")

            if not all([jira_url, jira_username, jira_api_token, jira_project_key]):
                print("Jira configuration not found. Please set environment variables.")
                return

            # Initialize Jira ticket creator
            jira_creator = JiraTicketCreator(jira_url, jira_username, jira_api_token, jira_project_key)
            
            # Discover custom fields from environment variables
            jira_creator.custom_fields['custom_priority'] = os.getenv("JIRA_CUSTOM_FIELD_PRIORITY")
            jira_creator.custom_fields['severity'] = os.getenv("JIRA_CUSTOM_FIELD_SEVERITY")

            # Create a single ticket for the failed test
            failure = {
                'test_name': request.node.nodeid,
                'error': report.longreprtext,
                'timestamp': datetime.now().isoformat()
            }
            
            summary = f"Test Failure: {failure['test_name']}"
            description = f"""
h2. Automated Test Failure Report

h3. Test Details
*Test Case:* {failure['test_name']}
*Time of Failure:* {failure['timestamp']}

h3. Error Message
{{code:python}}
{failure['error']}
{{code}}

h3. Environment
*Browser:* {request.config.getoption("--browser")}
*Platform:* {os.getenv("PLATFORM", "N/A")}

h3. Automation Info
This ticket was automatically generated by the test automation pipeline.
            """.strip()

            priority, severity = jira_creator._determine_priority_and_severity(failure['error'])

            ticket = jira_creator.create_jira_ticket(
                summary=summary,
                description=description,
                issue_type="Bug",
                labels=['automated-test-failure', 'qa', 'selenium', 'regression'],
                priority=priority,
                severity=severity
            )

            if ticket:
                print(f"Created Jira ticket {ticket['key']} for test: {failure['test_name']}")
            else:
                print(f"Failed to create Jira ticket for test: {failure['test_name']}")

        except ImportError as e:
            print(f"Error importing Jira automation: {e}")
        except Exception as e:
            print(f"Error creating Jira ticket: {e}")


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
