"""
Simple runner for the existing captchabypasser functionality
This file calls the existing working captchabypasser modules directly
"""
from DrissionPage import ChromiumPage, ChromiumOptions
from captchabypasser.GoogleRecaptchaBypass.RecaptchaSolver import RecaptchaSolver
import time
import os


def solve_captcha_on_target_site():
    """
    Solve captcha on the target website using the existing working captchabypasser
    """
    # Configure Chrome options similar to the working implementation
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
        print(f"Using Microsoft Edge at: {EDGE_PATH}")
    else:
        print("Using default Chromium/Chrome browser")

    # Create the browser instance
    driver = ChromiumPage(addr_or_opts=options)
    recaptcha_solver = RecaptchaSolver(driver)

    print("Navigating to the target website...")
    driver.get("https://data.gov.tn/fr/auth/login/")

    print("Waiting for the reCAPTCHA element to appear...")
    try:
        # Wait for the reCAPTCHA iframe to load
        driver.wait.ele_displayed('xpath://iframe[@title="reCAPTCHA"]', timeout=10)
        print("Found reCAPTCHA iframe, attempting to solve...")

        # Solve the reCAPTCHA
        t0 = time.time()
        recaptcha_solver.solveCaptcha()
        print(f"Time to solve the captcha: {time.time()-t0:.2f} seconds")

        # Wait a bit more to see if it was successful
        time.sleep(2)

        # Check if the reCAPTCHA is solved (checkbox has the checked style)
        if recaptcha_solver.is_solved():
            print("reCAPTCHA solved successfully!")
            return driver  # Return the driver so it stays open for manual testing
        else:
            print("reCAPTCHA solving failed.")
            return None

    except Exception as e:
        print(f"Error finding reCAPTCHA element: {e}")
        return None


def solve_captcha_and_login(username=None, password=None):
    """
    Solve captcha and optionally fill in login credentials
    """
    driver = solve_captcha_on_target_site()
    
    if driver is None:
        return False

    try:
        if username and password:
            # Find and fill the login form
            try:
                # Wait for form elements to be available
                username_field = driver.wait.ele_displayed(
                    'xpath://input[@id="username" or @name="username" or contains(@placeholder, "Identifiant") or contains(@id, "login")]', 
                    timeout=5
                )
                password_field = driver.wait.ele_displayed(
                    'xpath://input[@id="password" or @name="password" or contains(@placeholder, "Mot de passe")]', 
                    timeout=5
                )

                # Fill in credentials
                username_field.clear()
                username_field.input(username)

                password_field.clear()
                password_field.input(password)

                print("Credentials entered. Ready for login.")

                # Find and click the login button
                login_button = driver.wait.ele_displayed(
                    'xpath://button[@type="submit" or contains(@class, "bt-dark") or contains(text(), "Se connecter")]',
                    timeout=5
                )
                login_button.click()
                print("Login button clicked.")
                
                # Wait for potential redirect after login
                time.sleep(5)
                print(f"Current URL after login attempt: {driver.url}")
                
            except Exception as e:
                print(f"Could not find or fill form fields: {e}")
        
        return True
    except Exception as e:
        print(f"Error during login: {e}")
        return False


if __name__ == "__main__":
    print("Running captcha solver directly...")
    solve_captcha_on_target_site()