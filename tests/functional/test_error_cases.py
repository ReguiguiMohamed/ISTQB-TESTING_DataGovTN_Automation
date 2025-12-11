import pytest
from pages.home_page import HomePage
from pages.search_page import SearchPage

@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
def test_search_with_special_characters(browser):
    """Test searching with special characters."""
    home_page = HomePage(browser)
    search_page = SearchPage(browser)

    home_page.go_to_dataset_search_fr()

    # Bug Report Candidate: This often fails on legacy CKAN instances
    special_chars = "! @#$%^&*()"
    search_page.search(special_chars)

    # We expect either results (fuzzy match) or "No results found"
    # We DO NOT expect a raw 500 error page
    assert search_page.is_search_result_visible(), "Special chars caused crash/unexpected state"
    print(f"Search with special characters '{special_chars}' completed successfully.")


@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
def test_navigate_to_nonexistent_page(browser):
    """Test 404 handling."""
    home_page = HomePage(browser)
    home_page.go_to_dataset_search_fr()

    # Manually construct a bad URL
    current_url = home_page.get_current_url()
    bad_url = current_url.rstrip("/") + "/nonexistent-page-123"

    browser.get(bad_url)

    page_source = browser.page_source.lower()
    title = browser.title.lower()

    # Flexible assertion for 404
    is_404 = "404" in title or "not found" in page_source or "page non trouvée" in page_source
    assert is_404, "Application did not show a standard 404 page"
    print(f"404 page handled correctly. Title: {title}")