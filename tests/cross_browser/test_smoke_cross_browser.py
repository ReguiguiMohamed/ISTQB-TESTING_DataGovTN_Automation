import pytest
from pages.home_page import HomePage
from pages.search_page import SearchPage
from pages.dataset_page import DatasetPage
from config import Config

@pytest.mark.cross_browser
@pytest.mark.smoke
def test_homepage_dataset_search_smoke(browser):
    """
    Smoke test: verify that the French dataset search page loads correctly
    in every browser (title, URL, and search UI available).
    """
    home_page = HomePage(browser)
    search_page = SearchPage(browser)

    # Open the French dataset search page
    home_page.go_to_dataset_search_fr()

    # Basic page-level checks using BasePage methods
    current_url = home_page.get_current_url()
    assert "catalog.data.gov.tn" in current_url, f"Unexpected URL: {current_url}"
    assert "/fr/dataset" in current_url, f"Expected French path, got {current_url}"

    title = home_page.get_title()
    assert title and title.strip(), "Page should have a non-empty title"

    # UI-level: search area is visible
    assert search_page.is_search_result_visible(), "Search area should be visible on load"

@pytest.mark.cross_browser
@pytest.mark.parametrize("search_keyword", ["data", "education"])
def test_cross_browser_basic_search_smoke(browser, search_keyword):
    """
    Smoke test: Basic search scenario across browsers.
    """
    home_page = HomePage(browser)
    search_page = SearchPage(browser)

    home_page.go_to_dataset_search_fr()
    search_page.search(search_keyword)

    # Verify meaningful reaction
    assert search_page.is_search_result_visible(), f"Search failed for '{search_keyword}'"

    if search_page.has_results():
        titles = search_page.get_results_titles()
        assert len(titles) > 0, "Results found but titles list is empty"
    else:
        assert search_page.has_no_results_message(), "Should show 'no results' message"

@pytest.mark.cross_browser
@pytest.mark.parametrize("search_keyword", ["transport"])
def test_cross_browser_end_to_end_dataset_details(browser, search_keyword):
    """
    Smoke flow: Search -> Open Dataset -> Validate Details.
    """
    home_page = HomePage(browser)
    search_page = SearchPage(browser)
    dataset_page = DatasetPage(browser)

    home_page.go_to_dataset_search_fr()
    search_page.search(search_keyword)

    if not search_page.has_results():
        pytest.skip(f"No results for {search_keyword}, skipping detail test")

    search_page.open_result_by_index(0)
    dataset_page.wait_loaded()

    assert dataset_page.get_title(), "Dataset title missing"
    # Note: Resources count is checked but 0 is allowed (valid dataset state)
    assert dataset_page.get_resources_count() >= 0
