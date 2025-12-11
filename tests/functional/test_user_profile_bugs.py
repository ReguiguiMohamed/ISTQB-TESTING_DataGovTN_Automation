import pytest
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
    assert header_text.strip() == expected_english_text, \
        f"BUG CONFIRMED: Page switched to English. Expected '{expected_english_text}', but got '{header_text}'."

@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
def test_mes_taches_link_appears_and_is_broken(logged_in_browser):
    """
    Tests Bug #4: 'Mes tâches' link appears after visiting the API page and is broken.
    """
    auth_page = AuthPage(logged_in_browser)
    dataset_page = DatasetCatalogPage(logged_in_browser)

    print("Navigating to dataset catalog page...")
    dataset_page.open()
    dataset_page.wait.until(EC.visibility_of_element_located(dataset_page.API_LINK))

    print("Clicking API link and navigating back...")
    dataset_page.click_api_link()
    dataset_page.wait.until(EC.visibility_of_element_located(dataset_page.API_PAGE_CONTENT))
    logged_in_browser.back()

    print("Navigating to user dashboard...")
    logged_in_browser.get("https://data.gov.tn/fr/cms/contributions/")
    auth_page.wait.until(EC.visibility_of_element_located(auth_page.USER_PROFILE_MENU))
    
    print("Opening user menu to check for 'Mes tâches' link...")
    auth_page.click(auth_page.USER_PROFILE_MENU)
    
    tasks_link = auth_page.wait.until(EC.visibility_of_element_located(auth_page.TASKS_LINK))
    assert tasks_link is not None, "BUG NOT REPRODUCED: 'Mes tâches' link did not appear."
    print("Bug confirmed: 'Mes tâches' link is visible.")

    tasks_link.click()

    print("Checking for error on 'Mes tâches' page...")
    try:
        error_header = WebDriverWait(logged_in_browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Error') or contains(text(), '404') or contains(text(), 'Page non trouvée')]"))
        )
        assert error_header is not None, "Error message should be present."
        print(f"Bug confirmed: Page shows an error message: '{error_header.text}'")
    except:
        pytest.fail("BUG NOT REPRODUCED: 'Mes tâches' page did not show an expected error message.")