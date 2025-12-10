"""
Comprehensive test for login/logout functionality with real credentials.
Tests the complete login workflow including reCAPTCHA handling and logout verification.
"""
import os
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.auth_page import AuthPage
from config import Config


def _get_real_credentials_or_skip():
    """Read real credentials from environment or skip tests if missing."""
    username = os.getenv("TEST_USERNAME")
    password = os.getenv("TEST_PASSWORD")
    if not username or not password:
        pytest.skip("Real login credentials not configured (TEST_USERNAME/TEST_PASSWORD).")
    return username, password


@pytest.mark.functional
def test_successful_login_with_credentials(auto_setup_monitoring, browser):
    """Test successful login with real credentials and reCAPTCHA handling."""
    auth_page = AuthPage(browser)
    auto_setup_monitoring(auth_page)

    print("Opening login page...")
    auth_page.open_login_page()
    auth_page.wait.until(EC.visibility_of_element_located(auth_page.LOGIN_FORM))

    username, password = _get_real_credentials_or_skip()

    print("Attempting to log in...")
    auth_page.login(username, password)

    print("Waiting for possible redirect after login...")
    login_success = auth_page.wait_for_login_redirect(timeout=25)

    current_url = auth_page.get_current_url()
    print(f"Current URL after login attempt: {current_url}")

    is_redirected = "cms/contributions" in current_url or any(indicator in current_url for indicator in ['dashboard', 'account', 'profil'])
    is_logged_in = auth_page.is_logged_in()

    print(f"Is redirected to CMS: {is_redirected}")
    print(f"Is logged in (by indicators): {is_logged_in}")

    assert is_redirected or is_logged_in, \
        f"Expected to be either redirected to CMS contributions or logged in, but current URL is: {current_url}"


@pytest.mark.functional
def test_logout_functionality(logged_in_browser):
    """
    Test logout functionality starting from a logged-in state.
    Uses the logged_in_browser fixture.
    """
    auth_page = AuthPage(logged_in_browser)

    # We are already logged in thanks to the fixture.
    is_logged_in_before = auth_page.is_logged_in()
    print(f"Is logged in before logout attempt: {is_logged_in_before}")
    assert is_logged_in_before, "Should be logged in at the start of the test."

    print("Attempting to log out...")
    auth_page.logout()

    # Wait for logout to complete by checking for a logged-out state
    auth_page.wait.until(lambda d: not auth_page.is_logged_in())

    is_logged_out = not auth_page.is_logged_in()
    print(f"Is logged out: {is_logged_out}")

    assert is_logged_out, "User should be logged out."
    
    print("Logout action completed successfully.")


@pytest.mark.functional
def test_login_form_elements_accessibility(auto_setup_monitoring, browser):
    """Test that login form elements are accessible and can be filled."""
    auth_page = AuthPage(browser)
    auto_setup_monitoring(auth_page)

    print("Opening login page to test form elements...")
    auth_page.open_login_page()
    
    # Wait for the login form to be visible
    auth_page.wait.until(EC.visibility_of_element_located(auth_page.LOGIN_FORM))

    login_inputs = auth_page.find_all(auth_page.LOGIN_INPUT)
    password_inputs = auth_page.find_all(auth_page.PASSWORD_INPUT)

    print(f"Found {len(login_inputs)} login input(s), {len(password_inputs)} password input(s)")

    assert len(login_inputs) > 0 or len(password_inputs) > 0, "Should find at least one login or password input"

    print("Successfully verified form elements accessibility")


@pytest.mark.functional
def test_login_page_load_and_structure(auto_setup_monitoring, browser):
    """Test that login page loads and has expected structure."""
    auth_page = AuthPage(browser)
    auto_setup_monitoring(auth_page)

    print("Opening login page to check structure...")
    auth_page.open_login_page()
    auth_page.wait.until(EC.visibility_of_element_located(auth_page.LOGIN_FORM))

    title = auth_page.get_title()
    current_url = auth_page.get_current_url()

    print(f"Page title: {title}")
    print(f"Current URL: {current_url}")

    has_login_indicators = any(indicator in current_url.lower() for indicator in ['login', 'auth', 'se-connecter']) or \
                          any(indicator in title.lower() for indicator in ['login', 'connexion', 'auth'])

    assert has_login_indicators, f"Should be on a login page, but title: {title}, URL: {current_url}"

    print("Login page structure verified successfully")
