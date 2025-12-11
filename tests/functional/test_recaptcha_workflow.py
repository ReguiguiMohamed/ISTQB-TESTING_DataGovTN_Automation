"""
Alternative login approach using the working captchabypasser
This test file shows how to integrate the working DrissionPage-based reCAPTCHA solver
with the existing test framework.
"""
import pytest
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pages.auth_page import AuthPage
from pages.dataset_catalog_page import DatasetCatalogPage
from DrissionPage import ChromiumPage, ChromiumOptions
from captchabypasser.GoogleRecaptchaBypass.RecaptchaSolver import RecaptchaSolver


@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
def test_mes_taches_link_appears_and_is_broken_with_pre_solved_captcha(browser):
    """
    Tests Bug #4: 'Mes tâches' link appears after visiting the API page and is broken.
    This version expects that reCAPTCHA has been solved separately using captchabypasser.
    """
    # Scroll to the top at the start as requested
    browser.execute_script("window.scrollTo(0, 0);")
    
    auth_page = AuthPage(browser)
    dataset_page = DatasetCatalogPage(browser)

    print("Navigating to dataset catalog page...")
    dataset_page.open()
    dataset_page.wait.until(EC.visibility_of_element_located(dataset_page.API_LINK))

    print("Clicking API link and navigating back...")
    dataset_page.click_api_link()
    dataset_page.wait.until(EC.visibility_of_element_located(dataset_page.API_PAGE_CONTENT))
    # Give the API page a moment before going back
    time.sleep(1)
    browser.back()

    # Scroll back to the top before opening the user menu (already done at start)

    print("Opening user menu to check for 'Mes tâches' link after returning from API...")
    auth_page.wait.until(EC.visibility_of_element_located(auth_page.USER_PROFILE_MENU))
    auth_page.click(auth_page.USER_PROFILE_MENU)
    # Allow dropdown animation/rendering
    time.sleep(1)

    tasks_link = auth_page.wait.until(EC.visibility_of_element_located(auth_page.TASKS_LINK))
    assert tasks_link is not None, "BUG NOT REPRODUCED: 'Mes tâches' link did not appear."
    print("Bug confirmed: 'Mes tâches' link is visible.")

    tasks_link.click()

    print("Checking for error on 'Mes tâches' page...")
    try:
        error_header = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//*[contains(text(), 'Une erreur est survenue') "
                    "or contains(text(), 'Error') or contains(text(), 'error') "
                    "or contains(text(), 'Erreur') or contains(text(), 'ERREUR') "
                    "or contains(text(), '404') or contains(text(), 'Page non trouv')]",
                )
            )
        )
        assert error_header is not None, "Error message should be present."
        print(f"Bug confirmed: Page shows an error message: '{error_header.text}'")
    except Exception:
        pytest.fail(
            "BUG NOT REPRODUCED: 'Mes tâches' page did not show an expected error message."
        )


def run_captcha_solving_first():
    """
    Function that demonstrates how to solve captcha first using the working captchabypasser,
    then run selenium tests - this is the recommended approach
    """
    # Set up DrissionPage with proper options
    options = ChromiumOptions()
    # You might need to specify the browser path from your original working implementation
    # If you want the sessions to potentially share cookies, you'd need to use the same user data directory
    
    driver = ChromiumPage(addr_or_opts=options)
    recaptcha_solver = RecaptchaSolver(driver)
    
    print("Navigating to the target website...")
    driver.get("https://data.gov.tn/fr/auth/login/")
    
    print("Attempting to solve reCAPTCHA...")
    recaptcha_solver.solveCaptcha()
    
    if recaptcha_solver.is_solved():
        print("reCAPTCHA solved successfully! You can now run Selenium tests.")
        # Keep the browser open for a while to allow for Selenium tests to potentially connect
        # though session sharing between DrissionPage and Selenium is complex
        return True
    else:
        print("reCAPTCHA solving failed.")
        return False


# If you want to manually run the captcha solver first before tests:
# run_captcha_solving_first()