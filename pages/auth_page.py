"""
Authentication Page Object - Robust implementation with rate limiting and monitoring
"""
from pages.base_page import BasePage
from config import Config
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class AuthPage(BasePage):
    """Page object for Authentication (Login/Logout) pages with robust navigation and monitoring."""

    # Locators for the actual data.gov.tn website
    LOGIN_FORM = ("css selector", ".login-form, form[action*='login'], #login-form")
    LOGIN_INPUT = ("css selector", "input[name='login'], input[name='username'], input[name='email'], #login, #email, input#email")
    PASSWORD_INPUT = ("css selector", "input[name='password'], #password, input[type='password'], input#password")

    # Updated selector for the "Se connecter" button - using only standard CSS selectors
    LOGIN_BUTTON = ("css selector", "button[type='submit'], input[type='submit'], .login-btn, .submit-btn, .se-connecter, [class*='connecter']")

    ERROR_MESSAGE = ("css selector", ".error-message, .alert-error, .login-error, .auth-error, .alert-danger")
    SUCCESS_MESSAGE = ("css selector", ".success-message, .alert-success, .login-success, .alert-info")

    # reCAPTCHA elements - More specific selectors
    RECAPTCHA_IFRAME = ("css selector", "iframe[src*='recaptcha'], iframe[title*='reCAPTCHA'], .g-recaptcha iframe")
    RECAPTCHA_CHECKBOX = ("css selector", "div.recaptcha-checkbox-checkmark, .recaptcha-checkbox-border, .recaptcha-checkbox")
    RECAPTCHA_VERIFY_FRAME = ("css selector", "iframe[src*='recaptcha/api2/frame']")

    # Specific selector for reCAPTCHA challenge (for testing environment)
    RECAPTCHA_BYPASS = ("css selector", "[data-captcha-bypass='true'], [data-recaptcha-bypass='true']")

    # Logout elements - updated for the confirmation prompt - using only standard CSS selectors
    LOGOUT_LINK = ("css selector", "a[href*='logout'], .logout-btn, #logout, [data-logout='true'], .logout-link, [href*='Deconnexion'], [href*='deconnecter']")
    USER_MENU = ("css selector", ".user-menu, .user-profile, .profile-dropdown, .user-account, .dropdown-menu")

    # Confirmation dialog elements for logout - using only standard CSS selectors
    LOGOUT_CONFIRMATION_BUTTON = ("xpath", "//button[contains(text(), 'Se déconnecter') or contains(text(), 'Déconnexion') or contains(@value, 'Se déconnecter') or contains(@value, 'Déconnexion')] | //input[contains(@value, 'Se déconnecter') or contains(@value, 'Déconnexion')] | //button[contains(@class, 'confirm') and contains(@class, 'logout')]")

    # Additional auth elements
    FORGOT_PASSWORD = ("css selector", ".forgot-password, a[href*='password-reset'], a[href*='reset']")
    REGISTER_LINK = ("css selector", ".register-link, a[href*='register'], a[href*='signup']")

    # Logged in state indicators
    CMS_CONTRIBUTIONS_LINK = ("css selector", "a[href*='cms/contributions'], .cms-link, .contributions-link")

    # For handling the post-login state
    USER_PROFILE_MENU = ("css selector", ".user-menu, .dropdown.user, .navbar-user, a.nav-link.fs-top.droped")
    MODIFY_EMAIL_LINK = (By.LINK_TEXT, "Modifier mon E-mail")
    EMAIL_PAGE_HEADER = (By.CSS_SELECTOR, "h1, h2") # To check the language


    def __init__(self, driver, timeout: int = 10):
        super().__init__(driver, timeout)

    def open_login_page(self):
        """Open the login page with safe navigation."""
        return self.safe_open_url(f"{Config.BASE_URL}/fr/auth/login/")

    def bypass_recaptcha_for_testing(self):
        """Bypass reCAPTCHA for testing environment if possible."""
        try:
            print("Attempting to bypass reCAPTCHA for testing...")

            # Look for testing bypass elements (if the site has them)
            bypass_elements = self.driver.find_elements(*self.RECAPTCHA_BYPASS)
            if bypass_elements:
                print("Found reCAPTCHA bypass element, clicking...")
                bypass_elements[0].click()
                return True

            # If you have a test environment where reCAPTCHA is disabled,
            # you might have special attributes or endpoints
            print("No automatic bypass found, continuing...")
            return True  # Return True to continue without reCAPTCHA
        except Exception as e:
            print(f"Error in reCAPTCHA bypass: {e}")
            return True  # Continue anyway

    def handle_recaptcha(self):
        """Handle or bypass reCAPTCHA as needed for testing."""
        try:
            print("Checking for reCAPTCHA bypass in testing environment...")

            # For testing purposes, especially as the site owner,
            # you might have environment variables or special configurations
            # to disable reCAPTCHA during tests
            import os
            if os.getenv("DISABLE_RECAPTCHA_FOR_TEST", "false").lower() == "true":
                print("reCAPTCHA disabled for testing via environment variable")
                return

            # First, try to bypass for testing environment
            if self.bypass_recaptcha_for_testing():
                print("reCAPTCHA handling completed (or bypassed for testing)")
                return

            # Wait a moment for the page to fully load
            time.sleep(1)

            # Since we're seeing iframe errors, let's handle them more carefully
            print("Looking for reCAPTCHA elements...")

            # Check if reCAPTCHA is present at all
            recaptcha_frames = self.driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha']")
            if not recaptcha_frames:
                print("No reCAPTCHA iframes found, continuing with login...")
                return

            print(f"Found {len(recaptcha_frames)} reCAPTCHA iframe(s), attempting to handle...")

            # For site owners doing testing, sometimes the best approach
            # is to continue and let the user manually handle if needed
            print("reCAPTCHA present but continuing login process...")

        except Exception as e:
            print(f"Non-critical error in reCAPTCHA handling (continuing): {e}")
            # Don't fail the login process due to reCAPTCHA handling errors
            pass

    def login(self, username: str, password: str):
        """Perform login with robust error handling and reCAPTCHA support."""
        try:
            print(f"Attempting to log in with username: {username}")

            # Find and fill login field
            if self.find_all(self.LOGIN_INPUT):
                print("Found login input field, filling with username")
                self.input_text(self.LOGIN_INPUT, username)
            else:
                print("Could not find login input field, trying alternative selectors")
                # Try more specific selectors
                email_selectors = [
                    (By.CSS_SELECTOR, "#email"),
                    (By.CSS_SELECTOR, "[name='email']"),
                    (By.CSS_SELECTOR, "[id*='email']"),
                    (By.CSS_SELECTOR, "input[type='email']")
                ]

                for selector in email_selectors:
                    elements = self.driver.find_elements(*selector)
                    if elements:
                        elements[0].send_keys(username)
                        print(f"Filled username using alternative selector: {selector}")
                        break
                else:
                    print("Could not find any email input field")

            # Find and fill password field
            if self.find_all(self.PASSWORD_INPUT):
                print("Found password input field, filling with password")
                self.input_text(self.PASSWORD_INPUT, password)
            else:
                print("Could not find password input field, trying alternative selectors")
                # Try more specific selectors
                pwd_selectors = [
                    (By.CSS_SELECTOR, "#password"),
                    (By.CSS_SELECTOR, "[name='password']"),
                    (By.CSS_SELECTOR, "[id*='password']")
                ]

                for selector in pwd_selectors:
                    elements = self.driver.find_elements(*selector)
                    if elements:
                        elements[0].send_keys(password)
                        print(f"Filled password using alternative selector: {selector}")
                        break
                else:
                    print("Could not find any password input field")

            # Handle reCAPTCHA if present
            self.handle_recaptcha()

            # Try to find and click the login button using multiple strategies
            login_clicked = False

            # Strategy 1: Using the class selector
            if not login_clicked and self.find_all(self.LOGIN_BUTTON):
                try:
                    self.click(self.LOGIN_BUTTON)
                    print("Successfully clicked login button with main selector")
                    login_clicked = True
                except:
                    print("Failed to click login button with main selector")

            # Strategy 2: Using XPath for "Se connecter" text
            if not login_clicked:
                try:
                    login_button_xpath = "//button[contains(text(), 'Se connecter') or contains(text(), 'Connexion') or contains(@value, 'Se connecter') or contains(@value, 'Connexion')]"
                    login_element = self.driver.find_element(By.XPATH, login_button_xpath)
                    login_element.click()
                    print("Successfully clicked login button with XPath")
                    login_clicked = True
                except:
                    print("Failed to find login button with XPath")

            # Strategy 3: Click any submit button in the form
            if not login_clicked:
                try:
                    submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                    if submit_buttons:
                        submit_buttons[0].click()
                        print("Clicked generic submit button")
                        login_clicked = True
                    else:
                        print("No submit button found")
                except:
                    print("Failed to click submit button")

            if not login_clicked:
                print("Could not find or click any login button")

        except Exception as e:
            print(f"Error during login: {e}")
            # Record login error
            if self._standard_monitor:
                self._record_ui_change(self.LOGIN_FORM, "login_error",
                                     {"action": "login", "username": username, "error": str(e)},
                                     {"action": "login_error"})

    def logout(self):
        """Perform logout with robust error handling including confirmation dialog."""
        try:
            print("Starting logout process...")

            # Look for logout link or button
            logout_elements = self.driver.find_elements(*self.LOGOUT_LINK)
            if logout_elements:
                print("Found logout link/button, attempting to click")
                self.click(self.LOGOUT_LINK)

                # Wait for confirmation dialog/prompt if it appears
                time.sleep(2)

                # Look for the confirmation button "Se déconnecter" that appears after clicking logout
                confirmation_elements = self.driver.find_elements(*self.LOGOUT_CONFIRMATION_BUTTON)
                if confirmation_elements:
                    print("Found logout confirmation button, clicking to confirm")
                    confirmation_elements[0].click()
                    print("Confirmed logout")
                else:
                    print("No confirmation dialog found, proceeding...")

            else:
                print("Could not find main logout link, checking user menu")
                # If direct logout link is not found, try to access through user menu
                user_menu_elements = self.driver.find_elements(*self.USER_MENU)
                if user_menu_elements:
                    print("Found user menu, opening to find logout")
                    # Click the user menu to expand it
                    user_menu_elements[0].click()
                    time.sleep(1)  # Wait for menu to open

                    # Look for logout in the dropdown menu
                    logout_elements_dropdown = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='logout'], .logout-option, a:contains('Déconnexion'), a:contains('Se déconnecter')")
                    if logout_elements_dropdown:
                        print("Found logout in user menu dropdown")
                        logout_elements_dropdown[0].click()

                        # Wait for confirmation dialog if it appears
                        time.sleep(2)

                        # Look for confirmation button again
                        confirmation_elements = self.driver.find_elements(*self.LOGOUT_CONFIRMATION_BUTTON)
                        if confirmation_elements:
                            print("Found logout confirmation button, clicking to confirm")
                            confirmation_elements[0].click()
                            print("Confirmed logout")
                        else:
                            print("No confirmation dialog found in dropdown logout")
                    else:
                        print("Could not find logout in user menu")
                else:
                    print("Could not find user menu either")

        except Exception as e:
            print(f"Error during logout: {e}")
            # Record logout error
            if self._standard_monitor:
                self._record_ui_change(self.LOGOUT_LINK, "logout_error",
                                     {"action": "logout", "error": str(e)},
                                     {"action": "logout_error"})

    def get_error_message(self):
        """Get any error message with error handling."""
        try:
            if self.find_all(self.ERROR_MESSAGE):
                return self.find(self.ERROR_MESSAGE).text
            return None
        except:
            return None

    def get_success_message(self):
        """Get any success message with error handling."""
        try:
            if self.find_all(self.SUCCESS_MESSAGE):
                return self.find(self.SUCCESS_MESSAGE).text
            return None
        except:
            return None

    def is_logged_in(self):
        """Check if user appears to be logged in with error handling."""
        current_url = self.get_current_url()
        print(f"Current URL: {current_url}")

        # Check if URL changed to CMS contributions page or if user-specific elements are present
        logged_in_indicators = [
            'cms/contributions' in current_url,
            'dashboard' in current_url,
            'account' in current_url,
            'profil' in current_url,
            'user' in current_url
        ]

        print(f"Logged-in URL indicators: {logged_in_indicators}")

        # Check if logout button exists (indicating logged-in state)
        logout_elements = self.driver.find_elements(*self.LOGOUT_LINK)
        user_menu_elements = self.driver.find_elements(*self.USER_MENU)

        # Check if specific logged-in elements exist (like CMS contributions link)
        cms_elements = self.driver.find_elements(*self.CMS_CONTRIBUTIONS_LINK)

        # Check for user profile elements
        profile_elements = self.driver.find_elements(*self.USER_PROFILE_MENU)

        is_logged_in = (any(logged_in_indicators) or
                       len(logout_elements) > 0 or
                       len(user_menu_elements) > 0 or
                       len(cms_elements) > 0 or
                       len(profile_elements) > 0)

        print(f"Is logged in: {is_logged_in} (based on {len(logout_elements)} logout elements, {len(user_menu_elements)} user menu elements)")

        return is_logged_in

    def wait_for_login_redirect(self, timeout: int = 20):
        """Wait for login redirect to complete."""
        from selenium.webdriver.support import expected_conditions as EC

        print(f"Waiting up to {timeout} seconds for login redirect...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            current_url = self.driver.current_url
            print(f"Current URL during wait: {current_url}")

            # Check for explicit error messages on the page
            error_text = self.get_error_message()
            if error_text:
                print(f"Login failed: Detected error message on page: {error_text}")
                return False

            if "cms/contributions" in current_url or any(indicator in current_url for indicator in ['dashboard', 'account', 'profil']):
                print(f"Login redirect successful. New URL: {current_url}")
                return True
            time.sleep(0.5)

        current_url = self.driver.current_url
        print(f"Login redirect timed out. Final URL: {current_url}")
        return False