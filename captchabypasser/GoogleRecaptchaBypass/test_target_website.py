from DrissionPage import ChromiumPage, ChromiumOptions
from RecaptchaSolver import RecaptchaSolver
import time
import os

# Specify the path to Microsoft Edge
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# Check if Edge exists at the default path, otherwise try alternatives
if not os.path.exists(EDGE_PATH):
    # Alternative path might be:
    EDGE_PATH = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(EDGE_PATH):
        # If Edge isn't found, we'll let DrissionPage try to find Chrome instead
        print("Microsoft Edge not found at standard locations. Will try to use Chrome instead.")
        EDGE_PATH = None

# Configure Chrome options
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

# Set the browser path if Edge is found
if EDGE_PATH and os.path.exists(EDGE_PATH):
    options.set_browser_path(EDGE_PATH)
    print(f"Using Microsoft Edge at: {EDGE_PATH}")
else:
    print("Using default Chromium/Chrome browser")

# Create the browser instance
driver = ChromiumPage(addr_or_opts=options)
recaptchaSolver = RecaptchaSolver(driver)

# Note: You may need to install ffmpeg for audio processing
# On Windows, you can download it from https://ffmpeg.org/download.html
# Or install via conda: conda install ffmpeg
# Or via chocolatey: choco install ffmpeg

print("Navigating to the target website...")
driver.get("https://data.gov.tn/fr/auth/login/")

print("Waiting for the reCAPTCHA element to appear...")
try:
    # Wait for the reCAPTCHA iframe to load
    driver.wait.ele_displayed('xpath://iframe[@title="reCAPTCHA"]', timeout=10)
    print("Found reCAPTCHA iframe, attempting to solve...")
    
    # Solve the reCAPTCHA
    t0 = time.time()
    recaptchaSolver.solveCaptcha()
    print(f"Time to solve the captcha: {time.time()-t0:.2f} seconds")
    
    # Wait a bit more to see if it was successful
    time.sleep(2)
    
    # Check if the reCAPTCHA is solved (checkbox has the checked style)
    if recaptchaSolver.is_solved():
        print("reCAPTCHA solved successfully!")
        
        # Find and fill the login form
        try:
            # Wait for form elements to be available
            username_field = driver.wait.ele_displayed('xpath://input[@id="username" or @name="username" or contains(@placeholder, "Identifiant") or contains(@id, "login")]', timeout=5)
            password_field = driver.wait.ele_displayed('xpath://input[@id="password" or @name="password" or contains(@placeholder, "Mot de passe")]', timeout=5)
            
            # Fill in dummy credentials (since we have permission to test)
            username_field.clear()
            username_field.input("test@example.com")  # Using dummy credentials
            
            password_field.clear()
            password_field.input("testpassword")  # Using dummy password
            
            print("Credentials entered. Ready for login.")
            
        except Exception as e:
            print(f"Could not find or fill form fields: {e}")
            
    else:
        print("reCAPTCHA solving failed.")
        
except Exception as e:
    print(f"Error finding reCAPTCHA element: {e}")

print("\nTest completed. Browser remains open for inspection.")

# Keep browser open for a few seconds so user can see the result
import time
time.sleep(10)
print("Closing browser in 10 seconds...")
driver.quit()