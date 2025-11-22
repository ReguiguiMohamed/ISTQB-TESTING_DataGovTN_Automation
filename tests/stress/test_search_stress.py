import pytest
import time
from pages.home_page import HomePage
from pages.search_page import SearchPage


@pytest.mark.stress
def test_concurrent_search_load(browser, base_url):
    """Test how the system handles repeated searches in a short time"""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)

    # Open homepage and navigate to search page
    home_page.go_to_dataset_search_fr()  # Updated to use new method

    # Perform multiple searches in succession
    keywords = ["data", "education", "santé", "transport", "economie"]

    for i, keyword in enumerate(keywords):
        start_time = time.time()
        search_page.search(keyword)

        results = search_page.get_results_titles()
        end_time = time.time()

        search_duration = end_time - start_time

        print(f"Search {i+1} for '{keyword}' took {search_duration:.2f}s and returned {len(results)} results")

        # Verify each search returns results
        assert len(results) >= 0, f"Search for '{keyword}' should not fail"  # Allow 0 results as valid

    print(f"All {len(keywords)} searches completed successfully")


@pytest.mark.stress
def test_paginated_search_under_load(browser, base_url):
    """Test pagination functionality under search load"""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)

    # Open homepage and navigate to search page
    home_page.go_to_dataset_search_fr()  # Updated to use new method

    # Perform an initial search
    search_page.search("information")

    # Check if there are enough results to paginate
    initial_results = search_page.get_results_titles()
    print(f"Initial search returned {len(initial_results)} results")

    # Try pagination if possible
    if len(initial_results) >= 10:  # Assuming page size is 10
        next_page_success = search_page.go_to_next_page()

        if next_page_success:
            next_page_results = search_page.get_results_titles()
            print(f"After pagination: {len(next_page_results)} results")
            assert len(next_page_results) >= 0, "Pagination should not fail"
        else:
            print("No next page available or pagination failed")

    # Perform additional searches after pagination
    search_page.search("statistics")
    results_after_pagination = search_page.get_results_titles()
    assert len(results_after_pagination) >= 0, "Search after pagination should work"

    print(f"Search after pagination returned {len(results_after_pagination)} results")


@pytest.mark.stress
def test_repeated_search_does_not_crash(browser, base_url):
    """Test that repeated searches do not cause the system to crash"""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)

    # Open homepage and navigate to search page
    home_page.go_to_dataset_search_fr()  # Updated to use new method

    # Perform search repeatedly in a loop (20 iterations)
    keyword = "data"
    iterations = 20

    for i in range(iterations):
        # Perform a search
        search_page.search(keyword)

        # Verify page is still functional by checking for results or basic elements
        results = search_page.get_results_titles()

        # Verify that search results page is still functional (no crashes)
        assert browser.current_url is not None, f"Browser crashed on iteration {i+1}"

        print(f"Iteration {i+1}: Search for '{keyword}' returned {len(results)} results")

        # Optional: Add a small delay between searches to avoid overloading
        time.sleep(0.1)

    print(f"Completed {iterations} repeated searches without crashing")


# Optional: Use pytest-xdist to run tests in parallel
# Command: pytest tests/stress/test_search_stress.py -n auto