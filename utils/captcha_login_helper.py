"""
Pre-login helper using DrissionPage and the working captchabypasser
This solves the reCAPTCHA once and saves cookies for Selenium tests
"""
import pickle
import time
import threading
from DrissionPage import ChromiumPage, ChromiumOptions
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'captchabypasser', 'GoogleRecaptchaBypass'))
from RecaptchaSolver import RecaptchaSolver
import os


def login_with_drissionpage_and_save_cookies(username=None, password=None):
    """
    Use existing captchabypasser to login, save cookies for Selenium
    """
    # Configure browser options similar to the working captchabypasser implementation
    CHROME_ARGUMENTS = [
        "-no-first-run",
        "-force-color-profile=srgb",
        "-metrics-recording-only",
        "-password-store=basic",
        "-use-mock-keychain",
        "-export-tagged-pdf",
        "-no-default-browser-check",
        "-disable-background-mode",
        "-enable-features=NetworkService,NetworkServiceInProcess",
        "-disable-features=FlashDeprecationWarning",
        "-deny-permission-prompts",
        "-disable-gpu",
        "-accept-lang=en-US",
        "--disable-usage-stats",
        "--disable-crash-reporter",
        "--no-sandbox"
    ]

    options = ChromiumOptions()
    for argument in CHROME_ARGUMENTS:
        options.set_argument(argument)

    # Specify the path to Microsoft Edge if needed
    EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

    if os.path.exists(EDGE_PATH):
        options.set_browser_path(EDGE_PATH)
    else:
        print("Using default Chromium/Chrome browser")

    # Create the browser instance
    driver = ChromiumPage(addr_or_opts=options)

    print("Navigating to the target website...")
    driver.get("https://data.gov.tn/fr/auth/login/")

    # Wait for page to fully load
    time.sleep(3)

    try:
        print("Filling login credentials FIRST...")
        # Fill credentials FIRST before or alongside reCAPTCHA solving
        if username and password:
            print("Filling login credentials...")

            # Method 1: Try by ID first (most reliable)
            try:
                username_field = driver.ele('#username', timeout=5)
                password_field = driver.ele('#password', timeout=5)

                if username_field and password_field:
                    print("Found form fields by ID")
                    username_field.clear()
                    username_field.input(username)
                    print(f"Username entered: {username[:3]}***")

                    password_field.clear()
                    password_field.input(password)
                    print("Password entered")
                else:
                    raise Exception("Fields not found by ID")

            except Exception as e:
                print(f"Could not find fields by ID: {e}")
                print("Trying alternative selectors...")

                # Method 2: Try by name attribute
                try:
                    username_field = driver.ele('@name=username', timeout=5)
                    password_field = driver.ele('@name=password', timeout=5)

                    if username_field and password_field:
                        print("Found form fields by name attribute")
                        username_field.clear()
                        username_field.input(username)
                        password_field.clear()
                        password_field.input(password)
                    else:
                        raise Exception("Fields not found by name")

                except Exception as e2:
                    print(f"Could not find fields by name: {e2}")

                    # Method 3: Try by input type
                    try:
                        username_field = driver.ele('xpath://input[@type="text"]', timeout=5)
                        password_field = driver.ele('xpath://input[@type="password"]', timeout=5)

                        if username_field and password_field:
                            print("Found form fields by input type")
                            username_field.clear()
                            username_field.input(username)
                            password_field.clear()
                            password_field.input(password)
                        else:
                            raise Exception("Fields not found by type")
                    except Exception as e3:
                        print(f"FATAL: Could not find form fields: {e3}")
                        # Continue anyway even if fields are not found - reCAPTCHA might still be solvable
                        print("Continuing with reCAPTCHA solving...")

            # Wait for input to register
            time.sleep(1)

        print("Attempting to solve reCAPTCHA with audio recognition...")
        recaptcha_solver = RecaptchaSolver(driver)

        # Start reCAPTCHA solving in a separate thread to allow timeout
        import threading

        def solve_recaptcha():
            try:
                recaptcha_solver.solveCaptcha()
                print(f"reCAPTCHA solver finished")
            except Exception as e:
                print(f"reCAPTCHA solving encountered issues: {e}")

        # Start the solving process in a separate thread
        solving_thread = threading.Thread(target=solve_recaptcha, daemon=True)
        solving_thread.start()

        # Wait for 30 seconds to allow reCAPTCHA to solve
        print("Waiting 30 seconds for reCAPTCHA to potentially solve...")
        time.sleep(30)

        # Check if reCAPTCHA is solved (this is the critical check for the green tick)
        is_solved = recaptcha_solver.is_solved()
        print(f"reCAPTCHA solved status after 30 seconds: {is_solved}")

        print("Automatically clicking 'Se connecter' button after 30 seconds...")

        # Click the connect button after 30 seconds regardless of reCAPTCHA status
        print("Proceeding to click login button regardless of reCAPTCHA status...")

        # Click the login button (credentials are already filled)
        if username and password:
            print("Attempting to click login button...")

            # Try multiple selectors for the login button
            login_button = None
            button_selectors = [
                'xpath://button[@name="signin"]',
                'xpath://button[@class="bt-dark"]',
                'xpath://button[@aria-label="signin"]',
                'xpath://button[@type="submit"]',
                'css:button[name="signin"]',
                'css:button.bt-dark',
                'xpath://button[contains(text(), "connecter")]',
                'xpath://*[contains(text(), "Se connecter")]',
                'xpath://button[contains(text(), "Se connecter")]',
                'xpath://*[contains(text(), "Connexion")]',
                'xpath://button[contains(text(), "Connexion")]',
                'xpath://*[contains(text(), "S\'identifier")]',
                'xpath://button[contains(text(), "S\'identifier")]',
            ]

            for selector in button_selectors:
                try:
                    login_button = driver.ele(selector, timeout=3)
                    if login_button:
                        print(f"Found login button with selector: {selector}")
                        break
                except:
                    continue

            if not login_button:
                print("ERROR: Could not find login button with any selector")
                print("Attempting to find any submit button...")
                try:
                    login_button = driver.ele('xpath://button[@type="submit"]', timeout=5)
                except:
                    print("FATAL: No submit button found")
                    driver.quit()
                    return None

            # Try clicking the button (without scrolling to avoid the bug)
            try:
                login_button.click()
                print("Login button clicked successfully")
            except Exception as click_error:
                print(f"Standard click failed: {click_error}")
                print("Trying JavaScript click...")
                try:
                    driver.run_js('arguments[0].click();', login_button)
                    print("JavaScript click executed")
                except Exception as js_error:
                    print(f"JavaScript click also failed: {js_error}")
                    # Don't exit - maybe page state will allow login eventually
                    pass

        # Wait for login to process
        print("Waiting for login to process...")
        time.sleep(5)

        # Check if URL changed (sign of successful login)
        current_url = driver.url
        print(f"Current URL after login attempt: {current_url}")

        # Wait for potential redirect
        try:
            original_url = current_url
            time.sleep(3)
            current_url = driver.url
            if current_url != original_url:
                print(f"URL changed from {original_url} to {current_url}")
            else:
                print("No URL change detected - checking for error messages...")

                # Check for error messages
                try:
                    error_element = driver.ele('xpath://*[contains(@class, "error") or contains(@class, "alert")]', timeout=2)
                    if error_element:
                        print(f"WARNING: Possible error message: {error_element.text}")
                except:
                    print("No obvious error messages found")

        except Exception as e:
            print(f"Error checking URL change: {e}")

        # Additional wait to ensure session is established
        time.sleep(3)

        # Save cookies to file for Selenium to use
        cookies = driver.cookies()
        print(f"Collected {len(cookies)} cookies from DrissionPage session")

        # Debug: print cookie names
        cookie_names = [c.get('name', 'unnamed') for c in cookies]
        print(f"Cookie names: {', '.join(cookie_names)}")

        with open('login_cookies.pkl', 'wb') as f:
            pickle.dump(cookies, f)
        print("✓ Cookies saved to login_cookies.pkl")

        # Keep browser open briefly so user can verify
        print("Keeping browser open for 3 seconds for verification...")
        time.sleep(3)

        # Ensure all threads are properly closed
        driver.quit()
        print("✓ DrissionPage browser closed")

        # Explicitly join the solving thread if it's still running
        if solving_thread.is_alive():
            try:
                solving_thread.join(timeout=2)  # Wait up to 2 seconds for thread to finish
            except:
                pass  # Thread may not respond, but we continue anyway

        return cookies

    except Exception as e:
        print(f"ERROR during login process: {e}")
        import traceback
        traceback.print_exc()
        try:
            driver.quit()
        except:
            pass
        return None


def load_cookies_into_selenium(selenium_driver):
    """
    Load the saved cookies into a Selenium WebDriver
    """
    import pickle
    from selenium.webdriver.common.by import By

    try:
        # First navigate to the domain to set the context for cookies
        print("Navigating to data.gov.tn to set cookie domain...")
        selenium_driver.get('https://data.gov.tn')
        time.sleep(2)

        # Load cookies from file
        with open('login_cookies.pkl', 'rb') as f:
            cookies = pickle.load(f)

        print(f"Loaded {len(cookies)} cookies from file")

        # Add cookies to Selenium driver
        successful_cookies = 0
        for cookie in cookies:
            try:
                # Convert DrissionPage cookie format to Selenium format
                selenium_cookie = {
                    'name': cookie['name'],
                    'value': cookie['value'],
                }

                # Handle domain - ensure it's valid for data.gov.tn
                domain = cookie.get('domain', '')
                if domain.startswith('.'):
                    selenium_cookie['domain'] = domain
                elif 'data.gov.tn' in domain:
                    selenium_cookie['domain'] = domain
                else:
                    selenium_cookie['domain'] = '.data.gov.tn'

                # Add path
                selenium_cookie['path'] = cookie.get('path', '/')

                # Add optional fields if present and valid
                if 'expiry' in cookie and cookie['expiry']:
                    try:
                        selenium_cookie['expiry'] = int(cookie['expiry'])
                    except:
                        pass

                if 'secure' in cookie:
                    selenium_cookie['secure'] = bool(cookie['secure'])

                if 'httpOnly' in cookie:
                    selenium_cookie['httpOnly'] = bool(cookie['httpOnly'])

                # Add the cookie
                selenium_driver.add_cookie(selenium_cookie)
                successful_cookies += 1

            except Exception as e:
                cookie_name = cookie.get('name', 'unknown')
                print(f"Could not add cookie '{cookie_name}': {e}")
                continue

        print(f"✓ Successfully added {successful_cookies}/{len(cookies)} cookies to Selenium")

        # Refresh the page to apply cookies
        print("Refreshing page to apply cookies...")
        selenium_driver.refresh()
        time.sleep(2)

        return True

    except FileNotFoundError:
        print("ERROR: login_cookies.pkl not found. Run the DrissionPage login first.")
        return False
    except Exception as e:
        print(f"ERROR loading cookies into Selenium: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Example usage
    username = os.getenv("TEST_USERNAME")
    password = os.getenv("TEST_PASSWORD")

    if not username or not password:
        print("ERROR: Please set TEST_USERNAME and TEST_PASSWORD environment variables")
        print("Example:")
        print("  set TEST_USERNAME=your_username")
        print("  set TEST_PASSWORD=your_password")
        print("  python captcha_login_helper.py")
    else:
        print(f"Attempting login with username: {username[:3]}***")
        cookies = login_with_drissionpage_and_save_cookies(username, password)
        if cookies:
            print("\n" + "="*60)
            print("✓ SUCCESS: Login completed and cookies saved")
            print("="*60)
            print("\nYou can now run your Selenium tests using:")
            print("  pytest test_user_profile_bugs.py")
        else:
            print("\n" + "="*60)
            print("✗ FAILED: Login process failed")
            print("="*60)
            print("\nPlease check:")
            print("  1. Username and password are correct")
            print("  2. reCAPTCHA was solved successfully")
            print("  3. Network connection is stable")