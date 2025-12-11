import pytest
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pages.auth_page import AuthPage
from pages.dataset_catalog_page import DatasetCatalogPage


@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
@pytest.mark.usefixtures("jira_reporter")
def test_modify_email_page_language_bug(logged_in_browser):
    """
    Tests Bug #2: The 'Modifier mon E-mail' page incorrectly switches to English.
    Uses the logged_in_browser fixture to start from a logged-in state.
    """
    # Scroll to top at the very beginning
    logged_in_browser.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.5)

    auth_page = AuthPage(logged_in_browser)
    print("Clicking user profile menu...")
    auth_page.click(auth_page.USER_PROFILE_MENU)
    auth_page.wait.until(EC.visibility_of_element_located(auth_page.MODIFY_EMAIL_LINK))

    print("Clicking 'Modifier mon E-mail' link...")
    auth_page.click(auth_page.MODIFY_EMAIL_LINK)
    auth_page.wait.until(EC.visibility_of_element_located(auth_page.EMAIL_PAGE_HEADER))

    header_element = auth_page.find(auth_page.EMAIL_PAGE_HEADER)
    header_text = header_element.text
    print(f"Header text on email page: '{header_text}'")

    expected_english_text = "Change E-mail"
    assert header_text.strip() == expected_english_text, (
        f"BUG CONFIRMED: Page switched to English. "
        f"Expected '{expected_english_text}', but got '{header_text}'."
    )


@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
def test_mes_taches_link_appears_and_is_broken(logged_in_browser):
    """
    Tests Bug #4: 'Mes tâches' link appears after visiting the API page and is broken.

    This test uses the logged_in_browser fixture which should already have
    authentication cookies loaded from the DrissionPage captcha solving session.
    """
    # CRITICAL: Scroll to the top at the VERY START as requested
    print("Scrolling to top of page...")
    logged_in_browser.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.5)  # Brief pause to ensure scroll completes

    auth_page = AuthPage(logged_in_browser)
    dataset_page = DatasetCatalogPage(logged_in_browser)

    print("Navigating to dataset catalog page...")
    dataset_page.open()

    # Wait for page to load completely
    dataset_page.wait.until(EC.visibility_of_element_located(dataset_page.API_LINK))
    time.sleep(1)

    print("Clicking API link...")
    dataset_page.click_api_link()

    # Wait for API page to load
    dataset_page.wait.until(EC.visibility_of_element_located(dataset_page.API_PAGE_CONTENT))
    print("API page loaded, waiting a moment...")
    time.sleep(2)  # Give the page time to fully render

    print("Navigating back to previous page...")
    logged_in_browser.back()

    # Wait for page to load after going back
    time.sleep(2)

    # Scroll to top again after going back (ensures user menu is visible)
    print("Scrolling to top after returning from API page...")
    logged_in_browser.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.5)

    print("Opening user menu to check for 'Mes tâches' link...")
    auth_page.wait.until(EC.visibility_of_element_located(auth_page.USER_PROFILE_MENU))

    # Wait a moment before clicking to ensure menu is ready
    time.sleep(1)

    auth_page.click(auth_page.USER_PROFILE_MENU)

    # Allow dropdown animation/rendering time
    print("Waiting for user menu dropdown to fully render...")
    time.sleep(1.5)

    # Look for the 'Mes tâches' link
    print("Checking for 'Mes tâches' link in dropdown...")
    try:
        tasks_link = auth_page.wait.until(
            EC.visibility_of_element_located(auth_page.TASKS_LINK),
            message="'Mes tâches' link not found in dropdown"
        )
        assert tasks_link is not None, "BUG NOT REPRODUCED: 'Mes tâches' link did not appear."
        print("✓ Bug confirmed: 'Mes tâches' link is visible in dropdown")
    except Exception as e:
        print(f"Could not find 'Mes tâches' link: {e}")
        pytest.fail("BUG NOT REPRODUCED: 'Mes tâches' link did not appear after visiting API page.")

    # Click the tasks link
    print("Clicking 'Mes tâches' link...")
    tasks_link.click()

    # Wait for navigation
    time.sleep(2)

    print("Checking for error on 'Mes tâches' page...")
    try:
        error_header = WebDriverWait(logged_in_browser, 10).until(
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
        assert error_header is not None, "Error message should be present on broken page."
        print(f"✓ Bug confirmed: 'Mes tâches' page shows error: '{error_header.text}'")
    except Exception as e:
        print(f"No error message found: {e}")
        # Take screenshot for debugging
        try:
            logged_in_browser.save_screenshot("mes_taches_no_error.png")
            print("Screenshot saved: mes_taches_no_error.png")
        except:
            pass
        pytest.fail(
            "BUG NOT REPRODUCED: 'Mes tâches' page did not show an expected error message. "
            "The link may have been fixed or the error condition was not triggered."
        )

