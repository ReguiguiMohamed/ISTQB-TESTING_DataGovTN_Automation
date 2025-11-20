import os
import time
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService

# 🔴 CHANGE THIS to your real full path:
EDGE_DRIVER_PATH = r"C:\Users\ahmed\Downloads\edgedriver_win64\msedgedriver.exe"


def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        action="store",
        default="edge",
        help="Browser to use (only 'edge' is supported for now).",
    )


@pytest.fixture(scope="session")
def browser(request):
    """
    Unique WebDriver instance for the whole test session.
    Uses Microsoft Edge + msedgedriver at EDGE_DRIVER_PATH.
    """
    browser_name = request.config.getoption("--browser").lower()
    if browser_name != "edge":
        raise RuntimeError("Seul --browser=edge est supporté pour l’instant.")

    if not EDGE_DRIVER_PATH:
        raise RuntimeError("EDGE_DRIVER_PATH n'est pas configuré dans conftest.py")

    if not Path(EDGE_DRIVER_PATH).is_file():
        raise RuntimeError(f"msedgedriver introuvable à : {EDGE_DRIVER_PATH}")

    # Désactiver selenium-manager
    os.environ["SE_DISABLE_DRIVER_MANAGEMENT"] = "1"

    options = EdgeOptions()
    options.add_argument("--start-maximized")

    service = EdgeService(executable_path=EDGE_DRIVER_PATH)
    driver = webdriver.Edge(service=service, options=options)
    driver.implicitly_wait(10)

    yield driver

    driver.quit()


@pytest.fixture(scope="session")
def base_url() -> str:
    return "https://www.data.gov.tn/"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Si un test échoue, on prend une capture d'écran dans reports/screenshots/.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("browser")
        if driver is None:
            return

        screenshots_dir = Path("reports") / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        safe_nodeid = report.nodeid.replace("::", "__").replace("/", "_").replace("\\", "_")
        filename = f"{safe_nodeid}_{timestamp}.png"
        filepath = screenshots_dir / filename

        driver.save_screenshot(str(filepath))
        print(f"\n[pytest] Screenshot saved to: {filepath}")
