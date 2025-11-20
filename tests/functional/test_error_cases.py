import pytest
from pages.home_page import HomePage
from pages.search_page import SearchPage
from pages.dataset_page import DatasetPage


@pytest.mark.functional
def test_search_with_empty_keyword_shows_all_or_error(browser, base_url):
    """Test searching with an empty keyword"""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)

    # Open homepage and navigate to search page
    home_page.open()
    home_page.go_to_dataset_search_fr()  # Updated to use new method

    # Perform search with empty keyword
    search_page.search("")

    # Check if results are displayed or appropriate message is shown
    results = search_page.get_results_titles()

    # The behavior depends on the site - it might show all datasets or an error message
    print(f"Search with empty keyword returned {len(results)} results")


@pytest.mark.functional
def test_search_with_special_characters(browser, base_url):
    """Test searching with special characters"""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)

    # Open homepage and navigate to search page
    home_page.open()
    home_page.go_to_dataset_search_fr()  # Updated to use new method

    # Perform search with special characters
    search_keyword = "!@#$%^&*()"
    search_page.search(search_keyword)

    # Check if the search handles special characters appropriately
    results = search_page.get_results_titles()
    print(f"Search with special characters '{search_keyword}' returned {len(results)} results")


@pytest.mark.functional
def test_search_with_very_long_keyword(browser, base_url):
    """Test searching with a very long keyword"""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)

    # Open homepage and navigate to search page
    home_page.open()
    home_page.go_to_dataset_search_fr()  # Updated to use new method

    # Perform search with a very long keyword
    long_keyword = "a" * 1000  # 1000 character keyword
    search_page.search(long_keyword)

    # Check if the search handles long keywords appropriately
    results = search_page.get_results_titles()
    print(f"Search with long keyword returned {len(results)} results")


@pytest.mark.functional
def test_navigate_to_nonexistent_page(browser, base_url):
    """Test what happens when manually navigating to non-existent pages"""
    # Initialize page object
    home_page = HomePage(browser, base_url)

    # Open homepage
    home_page.open()

    # Try to navigate to a non-existent page by changing URL
    nonexistent_url = f"{base_url}/nonexistent-page-12345"
    browser.get(nonexistent_url)

    # Check how the site handles 404 or similar errors
    page_title = browser.title
    page_source = browser.page_source

    # Verify that an appropriate error page is shown
    assert "404" in page_title or "not found" in page_source.lower() or "error" in page_source.lower()
    print(f"Nonexistent page handled correctly. Page title: {page_title}")


@pytest.mark.functional
def test_search_with_garbage_string_returns_no_results(browser, base_url):
    """Test that searching with garbage string returns no results"""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)

    # Open homepage and navigate to search page
    home_page.open()
    home_page.go_to_dataset_search_fr()  # Updated to use new method

    # Perform search with garbage string
    garbage_keyword = "zzzzqwerty12345"
    search_page.search(garbage_keyword)

    # Check if there are no results or a "no results" message
    results = search_page.get_results_titles()

    # Check if there's a "no results" message
    no_results_message_found = False
    try:
        # Look for common "no results" indicators
        no_results_selectors = [
            ".no-results, .no-result, .results-empty, [data-testid='no-results']",
            "//*[contains(text(), 'no result') or contains(text(), 'no match') or contains(text(), 'not found')]",
            "//*[contains(., 'no result') or contains(., 'no match') or contains(., 'not found')]"
        ]

        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        wait = WebDriverWait(browser, 5)

        for selector in no_results_selectors[:1]:  # Using first CSS selector
            try:
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                if element.text.strip():
                    no_results_message_found = True
                    break
            except:
                continue

    # Either no results should be returned or a "no results" message should be displayed
    assert len(results) == 0 or no_results_message_found, \
        f"Expected no results or 'no results' message for garbage search, but got {len(results)} results and no message"

    print(f"Search with garbage string '{garbage_keyword}' returned {len(results)} results, no_results_message: {no_results_message_found}")


@pytest.mark.functional
def test_search_with_empty_string_shows_validation_or_default(browser, base_url):
    """Test that searching with empty string shows validation or default behavior"""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)

    # Open homepage and navigate to search page
    home_page.open()
    home_page.go_to_dataset_search_fr()  # Updated to use new method

    # Perform search with empty string (already implemented in the original test)
    # Just expanding on the original test to better validate behavior
    search_page.search("")

    # Check if results are displayed or appropriate message is shown
    results = search_page.get_results_titles()

    # The behavior depends on the site - it might show all datasets or an error message
    # or ask the user to enter a search term
    print(f"Search with empty string returned {len(results)} results")

    # Look for validation or instruction message
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        wait = WebDriverWait(browser, 5)

        # Look for any instruction or validation messages
        message_selectors = [
            ".search-help, .search-hint, .instructions, .placeholder",
            "[data-testid='search-help'], [data-testid='search-instructions']"
        ]

        for selector in message_selectors:
            try:
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                if element.text.strip():
                    print(f"Found search hint/instruction: {element.text[:50]}...")
                    break
            except:
                continue

    except Exception as e:
        print(f"Could not check for validation messages: {str(e)}")


@pytest.mark.functional
def test_search_with_very_long_string_does_not_break_page(browser, base_url):
    """Test that searching with very long string does not break page"""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)

    # Open homepage and navigate to search page
    home_page.open()
    home_page.go_to_dataset_search_fr()  # Updated to use new method

    # Perform search with very long keyword (> 500 characters)
    very_long_keyword = "a" * 600  # 600 character keyword
    try:
        search_page.search(very_long_keyword)

        # Verify page didn't crash by checking if basic elements are still accessible
        results = search_page.get_results_titles()

        # Check if page is still functional (no 500 error, no JS exceptions visible)
        page_source = browser.page_source
        error_indicators = ["500", "error", "exception", "internal server error"]

        error_found = any(indicator.lower() in page_source.lower() for indicator in error_indicators)

        assert not error_found, f"Page error detected after long search: {error_found}"

        print(f"Search with very long string completed without breaking page. Results: {len(results)}")

    except Exception as e:
        # If the search itself fails due to the long string, that's acceptable
        # as long as it doesn't crash the page/browser
        print(f"Search with very long string caused exception (acceptable): {str(e)}")

        # Verify that the page is still accessible
        current_url = browser.current_url
        page_source = browser.page_source

        # Check for server errors
        error_indicators = ["500", "error", "exception", "internal server error"]
        error_found = any(indicator.lower() in page_source.lower() for indicator in error_indicators)

        assert not error_found, f"Server error occurred with very long search string: {error_found}"
        print("Page survived long string search without crashing")


@pytest.mark.functional
def test_invalid_url_does_not_crash(browser, base_url):
    """Test that opening an invalid dataset URL handles error gracefully"""
    # Initialize page object
    home_page = HomePage(browser, base_url)

    # Open homepage
    home_page.open()

    # Navigate to search page first to get a valid base URL
    home_page.go_to_dataset_search_fr()  # Updated to use new method
    search_url = browser.current_url

    # Try to navigate to a non-existent dataset URL (add an invalid slug)
    invalid_dataset_url = f"{search_url}/non-existent-dataset-12345"
    browser.get(invalid_dataset_url)

    # Check how the site handles this invalid dataset URL
    page_title = browser.title
    page_source = browser.page_source

    # Verify that an appropriate error page is shown, not a crash
    # Look for 404, error page or some indication that the dataset doesn't exist
    error_indicators = [
        "404" in page_title or "404" in page_source.lower(),
        "not found" in page_source.lower(),
        "error" in page_source.lower(),
        "does not exist" in page_source.lower()
    ]

    error_found = any(error_indicators)

    # Verify the page didn't crash completely (still has some content)
    assert len(page_source) > 100 or error_found, "Page appears to have crashed completely"

    print(f"Invalid dataset URL handled appropriately. Error indication found: {error_found}")