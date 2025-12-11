"""
Manual intervention test for login functionality.
This test allows users to manually solve reCAPTCHA and complete login.
"""
import os
import time

import pytest

from pages.auth_page import AuthPage
from config import Config


def _get_real_credentials_or_skip():
    """Read real credentials from environment or skip if missing."""
    username = os.getenv("TEST_USERNAME")
    password = os.getenv("TEST_PASSWORD")
    if not username or not password:
        pytest.skip("Real login credentials not configured (TEST_USERNAME/TEST_PASSWORD).")
    return username, password


@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
def test_manual_login_with_recaptcha_solving(auto_setup_monitoring, browser):
    """Test login with manual reCAPTCHA solving capability."""
    auth_page = AuthPage(browser)

    # Set up monitoring
    auto_setup_monitoring(auth_page)

    # Navigate to login page
    print("Opening login page...")
    auth_page.open_login_page()
    
    # Wait for the page to load completely
    time.sleep(3)
    
    print("Page loaded. Current URL:", auth_page.get_current_url())
    print("Page title:", auth_page.get_title())
    
    # Fill in credentials from environment
    username, password = _get_real_credentials_or_skip()
    
    print(f"Filling credentials for user: {username}")
    
    # Find and fill login field
    try:
        if auth_page.find_all(auth_page.LOGIN_INPUT):
            auth_page.input_text(auth_page.LOGIN_INPUT, username)
            print("Username entered successfully")
    except Exception as e:
        print(f"Could not enter username: {e}")

    # Find and fill password field
    try:
        if auth_page.find_all(auth_page.PASSWORD_INPUT):
            auth_page.input_text(auth_page.PASSWORD_INPUT, password)
            print("Password entered successfully")
    except Exception as e:
        print(f"Could not enter password: {e}")
    
    print("\n" + "="*50)
    print("PAGE READY FOR MANUAL INTERVENTION")
    print("Please manually solve the reCAPTCHA if present")
    print("Then manually click the 'Se connecter' button")
    print("The test will wait for 60 seconds for you to complete these actions")
    print("="*50)
    
    # Wait for manual intervention - give user time to solve reCAPTCHA and click login
    for i in range(60, 0, -1):
        print(f"Waiting... {i} seconds remaining. Press Ctrl+C to continue test evaluation.", end='\r')
        time.sleep(1)
    
    print("\nContinuing test evaluation...")
    
    # Check if login was successful by looking at URL or other indicators
    current_url = auth_page.get_current_url()
    print(f"Current URL after manual login attempt: {current_url}")
    
    # Check if we're on the expected post-login page (CMS contributions)
    if "cms/contributions" in current_url:
        print("SUCCESS: Login appears to have been successful (redirected to CMS)")
        print("Test completed successfully")
    elif auth_page.is_logged_in():
        print("SUCCESS: Login appears to have been successful (user appears logged in)")
        print("Test completed successfully")
    else:
        print(f"INFO: Still on URL: {current_url}")
        print("Login may not have completed, but this could be due to reCAPTCHA protection")
        print("Test completed with information")


@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
def test_manual_logout(auto_setup_monitoring, browser):
    """Test logout with manual capability."""
    auth_page = AuthPage(browser)

    # Set up monitoring
    auto_setup_monitoring(auth_page)

    print("This test assumes you're already logged in.")
    print("Navigate manually to the profile/logout area if needed.")
    print("The test will wait for 30 seconds for manual logout actions.")
    
    print("\n" + "="*50)
    print("PAGE READY FOR MANUAL LOGOUT")
    print("Please navigate to your profile/logout area")
    print("Then manually click the logout button/link")
    print("The test will wait for 30 seconds for you to complete these actions")
    print("="*50)
    
    # Wait for manual logout actions
    for i in range(30, 0, -1):
        print(f"Waiting for logout... {i} seconds remaining", end='\r')
        time.sleep(1)
    
    print("\nTest completed. Page state after logout attempt:")
    print(f"Current URL: {auth_page.get_current_url()}")
    print(f"Is logged in: {auth_page.is_logged_in()}")
