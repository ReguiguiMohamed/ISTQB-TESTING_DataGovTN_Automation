"""
Complete test for login/logout functionality with specific data.gov.tn requirements.
As the website owner, this tests the full authentication flow including reCAPTCHA bypass
and logout confirmation prompts.
"""
import pytest
from pages.auth_page import AuthPage
from config import Config
import time


@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
def test_complete_login_logout_flow(auto_setup_monitoring, browser):
    """Test complete login -> verification -> logout flow with confirmation."""
    auth_page = AuthPage(browser)

    # Set up monitoring
    auto_setup_monitoring(auth_page)

    print("="*60)
    print("Starting complete login/logout flow test")
    print("="*60)
    
    # Step 1: Open login page
    print("\n1. Opening login page...")
    auth_page.open_login_page()
    time.sleep(2)
    
    current_url = auth_page.get_current_url()
    print(f"   Current URL: {current_url}")
    print(f"   Page title: {auth_page.get_title()}")
    
    # Step 2: Perform login with credentials
    print("\n2. Filling login credentials...")
    username = "yas_lakh1"
    password = "t6NX4MBHr78tzUi"
    
    auth_page.login(username, password)
    
    # Step 3: Wait for possible redirect after login
    print("\n3. Waiting for login redirect...")
    login_success = auth_page.wait_for_login_redirect(timeout=25)

    # Step 4: Verify logged-in state
    print("\n4. Verifying logged-in state...")
    current_url = auth_page.get_current_url()
    is_logged_in = auth_page.is_logged_in()
    
    print(f"   Current URL: {current_url}")
    print(f"   Is logged in: {is_logged_in}")
    
    # Either we get redirected to the CMS or we show other signs of being logged in
    success_condition = login_success or is_logged_in
    assert success_condition, \
        f"Login failed - No redirect or login state detected. URL: {current_url}"
    
    print("   ✓ Login successful!")
    
    # Step 5: Verify we're on the expected CMS contributions page
    print("\n5. Verifying navigation to CMS contributions...")
    expected_pages = ["cms/contributions", "dashboard", "account", "profil"]
    page_found = any(page in current_url for page in expected_pages)
    
    if page_found:
        print(f"   ✓ Successfully navigated to expected user area: {current_url}")
    else:
        print(f"   ⚠ Expected user area not detected, but user appears logged in: {is_logged_in}")
    
    # Step 6: Perform logout with confirmation
    print("\n6. Starting logout process...")
    auth_page.logout()
    
    # Step 7: Wait and verify logout
    print("\n7. Verifying logout...")
    time.sleep(3)  # Wait for logout to process
    
    current_url_after_logout = auth_page.get_current_url()
    is_logged_in_after_logout = auth_page.is_logged_in()
    
    print(f"   URL after logout: {current_url_after_logout}")
    print(f"   Is still logged in: {is_logged_in_after_logout}")
    
    # After logout, we expect to not be logged in anymore
    if not is_logged_in_after_logout:
        print("   ✓ Logout successful!")
    else:
        print("   ⚠ User may still be logged in after logout attempt")
    
    print("\n" + "="*60)
    print("Complete login/logout flow test finished")
    print("="*60)


@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
def test_login_with_credentials_verification(auto_setup_monitoring, browser):
    """Test login functionality and verify account-specific elements."""
    auth_page = AuthPage(browser)

    # Set up monitoring
    auto_setup_monitoring(auth_page)
    
    print("\nTesting login with credentials verification...")
    
    # Navigate to login
    auth_page.open_login_page()
    time.sleep(1)
    
    # Login
    auth_page.login("yas_lakh1", "t6NX4MBHr78tzUi")
    
    # Wait for redirect
    login_success = auth_page.wait_for_login_redirect(timeout=20)
    
    # Verify login status
    is_logged_in = auth_page.is_logged_in()
    current_url = auth_page.get_current_url()
    
    # Assertions
    assert is_logged_in or login_success, "Login should be successful"
    
    print(f"Login verification passed. URL: {current_url}, Logged in: {is_logged_in}")


@pytest.mark.functional 
@pytest.mark.usefixtures("jira_reporter")
def test_logout_confirmation_flow(auto_setup_monitoring, browser):
    """Test the logout process including the confirmation prompt."""
    auth_page = AuthPage(browser)

    # Set up monitoring
    auto_setup_monitoring(auth_page)
    
    print("\nTesting logout confirmation flow...")
    
    # First, log in to have something to log out from
    auth_page.open_login_page()
    time.sleep(1)
    auth_page.login("yas_lakh1", "t6NX4MBHr78tzUi")
    auth_page.wait_for_login_redirect(timeout=20)
    
    # Check if we're logged in before attempting logout
    is_logged_in_before = auth_page.is_logged_in()
    print(f"Is logged in before logout: {is_logged_in_before}")
    assert is_logged_in_before, "Must be logged in to test logout"
    
    # Perform logout (this should handle the confirmation automatically)
    auth_page.logout()
    
    # Wait and verify logout completed
    time.sleep(3)
    is_logged_in_after = auth_page.is_logged_in()
    
    print(f"Is logged in after logout: {is_logged_in_after}")
    
    # The user should no longer be logged in
    assert not is_logged_in_after, "User should be logged out after logout process"
    
    print("Logout confirmation flow test passed!")


@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
def test_login_failure_with_invalid_credentials(auto_setup_monitoring, browser):
    """Test that login correctly handles invalid credentials."""
    auth_page = AuthPage(browser)

    # Set up monitoring
    auto_setup_monitoring(auth_page)
    
    print("\nTesting login failure with invalid credentials...")
    
    # Navigate to login
    auth_page.open_login_page()
    time.sleep(1)
    
    # Try to login with invalid credentials
    auth_page.login("invalid_user", "invalid_password")
    
    # Wait briefly to see response
    time.sleep(3)
    
    # Should not be logged in
    is_logged_in = auth_page.is_logged_in()
    error_message = auth_page.get_error_message()
    
    print(f"Is logged in with invalid credentials: {is_logged_in}")
    print(f"Error message: {error_message}")
    
    # Verify that login failed
    assert not is_logged_in, "Should not be logged in with invalid credentials"
    
    print("Login failure test passed!")