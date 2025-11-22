import pytest
from pages.home_page import HomePage
from pages.search_page import SearchPage


@pytest.mark.cross_browser
def test_homepage_loads(browser, base_url):
    """Test that the homepage loads without error and contains 'data' or 'données' in title"""
    # Initialize page object
    home_page = HomePage(browser, base_url)

    # Open homepage
    home_page.go_to_dataset_search_fr()

    # Verify page loaded correctly
    assert browser.title is not None and browser.title.strip() != "", "Page should have a title"

    # Check if title contains 'data' or 'données'
    title_lower = browser.title.lower()
    assert "data" in title_lower or "données" in title_lower, f"Title '{browser.title}' should contain 'data' or 'données'"

    print(f"Homepage loaded successfully in {browser.name}, title: {browser.title}")


@pytest.mark.cross_browser
@pytest.mark.parametrize("search_keyword", ["data", "education", "health"])
def test_basic_search_works_on_all_browsers(browser, base_url, search_keyword):
    """Test that basic search functionality works across browsers"""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)

    # Open homepage and navigate to search page
    home_page.go_to_dataset_search_fr()  # Updated to use new method

    # Perform a basic search
    search_page.search(search_keyword)

    # Verify results are returned
    results = search_page.get_results_titles()
    assert len(results) > 0, f"Search for '{search_keyword}' should return results in {browser.name}"

    print(f"Search for '{search_keyword}' returned {len(results)} results in {browser.name}")


# Commands to run these tests:
# pytest tests/cross_browser/test_smoke_cross_browser.py --browser=chrome
# pytest tests/cross_browser/test_smoke_cross_browser.py --browser=firefox
# pytest tests/cross_browser/test_smoke_cross_browser.py --browser=edge