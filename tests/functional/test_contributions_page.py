"""Tests for bugs on the "Mes contributions" page."""
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.contributions_page import ContributionsPage

@pytest.mark.functional
def test_add_new_proposition_button_is_broken(logged_in_browser):
    """
    Tests Bug #1: The 'Faire une proposition' button on the reuses page is broken.
    It has no onclick or href attribute.
    """
    contributions_page = ContributionsPage(logged_in_browser)
    contributions_page.go_to_propositions()
    WebDriverWait(logged_in_browser, 10).until(EC.url_contains("mes-reutilisations"))

    url_before_click = logged_in_browser.current_url
    print(f"URL before click: {url_before_click}")

    # Find and click the button
    button_found = contributions_page.click_add_new_button()
    assert button_found, "The 'add new' button was not found on the page."
    print("Clicked the 'Faire une proposition de réutilisation' button.")

    # Allow a moment for a potential navigation
    import time
    time.sleep(1)

    url_after_click = logged_in_browser.current_url
    print(f"URL after click: {url_after_click}")

    assert url_before_click == url_after_click, \
        f"BUG CONFIRMED: Clicking the 'add new proposition' button should not do anything, but the URL changed."

@pytest.mark.functional
def test_add_new_request_button_is_broken(logged_in_browser):
    """
    Tests Bug #1 variation: The 'Faire une demande' button is also broken.
    It has an onclick="location.href=''" which just reloads the page.
    """
    contributions_page = ContributionsPage(logged_in_browser)
    contributions_page.click(contributions_page.DEMANDES_LINK)
    WebDriverWait(logged_in_browser, 10).until(EC.url_contains("mes-demandes"))

    url_before_click = logged_in_browser.current_url
    print(f"URL before click: {url_before_click}")

    # Find and click the button
    button_found = contributions_page.click_add_new_button()
    assert button_found, "The 'add new' button was not found on the 'demandes' page."
    print("Clicked the 'Faire une demande d'ajout de données' button.")

    # Allow a moment for a potential navigation/reload
    import time
    time.sleep(2)

    url_after_click = logged_in_browser.current_url
    print(f"URL after click: {url_after_click}")

    # The URL might be exactly the same or have a '#' at the end if it reloads.
    assert url_after_click.startswith(url_before_click), \
        f"BUG CONFIRMED: Clicking the button should only reload the page, but it navigated to {url_after_click}."

