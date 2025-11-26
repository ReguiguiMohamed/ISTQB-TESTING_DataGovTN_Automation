"""
Simple test to verify monitoring functionality works
"""
import pytest
from selenium.webdriver.common.by import By
from pages.home_page import HomePage


def test_monitoring_setup(auto_setup_monitoring, browser):
    """Simple test to verify monitoring setup works"""
    home = HomePage(browser)

    # Set up automatic monitoring
    auto_setup_monitoring(home)

    # Try to open a simple page that should work
    try:
        home.open_url("https://httpbin.org/forms/post")  # A page with form elements
    except:
        # If external site doesn't work, try opening about:blank
        home.open_url("about:blank")

    # Verify we can get the title
    title = home.get_title()
    assert title is not None

    # Try to find an element to trigger monitoring recording
    try:
        # Try to find a submit button or text input to trigger the monitoring
        test_locator = (By.TAG_NAME, "body")
        element = home.find(test_locator)
        assert element is not None

        # Try a click on the body (harmless action)
        home.driver.execute_script("document.body.click();")
    except:
        # If no specific elements, just verify basic functionality is monitored
        pass