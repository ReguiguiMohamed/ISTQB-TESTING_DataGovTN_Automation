import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.auth_page import AuthPage

@pytest.mark.functional
def test_modify_email_page_language_bug(logged_in_browser):
    """
    Tests Bug #2: The 'Modifier mon E-mail' page incorrectly switches to English.
    Uses the logged_in_browser fixture to start from a logged-in state.
    """
    # The logged_in_browser fixture has already handled the login.
    auth_page = AuthPage(logged_in_browser)

    # --- Navigation and Test Step ---
    print("Clicking user profile menu...")
    auth_page.click(auth_page.USER_PROFILE_MENU)
    auth_page.wait.until(EC.visibility_of_element_located(auth_page.MODIFY_EMAIL_LINK))

    print("Clicking 'Modifier mon E-mail' link...")
    auth_page.click(auth_page.MODIFY_EMAIL_LINK)
    auth_page.wait.until(EC.visibility_of_element_located(auth_page.EMAIL_PAGE_HEADER))

    # --- Assertion Step ---
    header_element = auth_page.find(auth_page.EMAIL_PAGE_HEADER)
    header_text = header_element.text
    print(f"Header text on email page: '{header_text}'")

    # The bug is that the page switches to English
    expected_english_text = "Change E-mail"
    assert header_text.strip() == expected_english_text, \
        f"BUG CONFIRMED: Page switched to English. Expected '{expected_english_text}', but got '{header_text}'."
