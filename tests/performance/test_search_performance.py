import pytest
import time
from pages.home_page import HomePage
from pages.search_page import SearchPage


@pytest.mark.performance
def test_search_response_time_under_threshold(browser, base_url):
    """Test that search returns results within a time threshold"""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)

    # Open homepage and navigate to search page
    home_page.go_to_dataset_search_fr()  # Updated to use new method

    # Measure search response time
    start_time = time.time()
    search_page.search("education")
    end_time = time.time()

    response_time = end_time - start_time

    # Verify that search completes within threshold (TODO: Adjust actual threshold based on performance requirements)
    max_response_time = 15.0  # seconds - TODO: Adjust based on actual performance requirements
    assert response_time <= max_response_time, f"Search took {response_time:.2f}s, which exceeds maximum of {max_response_time}s"

    results = search_page.get_results_titles()
    assert len(results) > 0, "Search should return results"

    print(f"Search completed in {response_time:.2f} seconds with {len(results)} results")


@pytest.mark.performance
def test_page_load_time(browser, base_url):
    """Test that pages load within acceptable time limits"""
    # Initialize page object
    home_page = HomePage(browser, base_url)

    # Navigate to search page and measure load time
    start_time = time.time()
    home_page.go_to_dataset_search_fr()  # Updated to use new method
    end_time = time.time()

    search_page_load_time = end_time - start_time
    max_load_time = 15.0  # seconds
    assert search_page_load_time <= max_load_time, f"Search page load took {search_page_load_time:.2f}s, which exceeds maximum of {max_load_time}s"

    print(f"Search page loaded in {search_page_load_time:.2f} seconds")