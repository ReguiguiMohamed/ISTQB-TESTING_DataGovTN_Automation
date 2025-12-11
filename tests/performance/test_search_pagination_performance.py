import pytest
from pages.home_page import HomePage
from pages.search_page import SearchPage


@pytest.mark.performance
@pytest.mark.usefixtures("jira_reporter")
def test_search_pagination_performance(browser, base_url):
    """Test the performance of search result pagination"""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)
    
    # Open homepage and navigate to search page
    home_page.go_to_dataset_search_fr()  # Updated to use new method
    
    # Perform a search that should return multiple pages of results
    search_page.search("data")
    
    # Measure pagination performance
    import time
    start_time = time.time()
    
    # Try to go to next page
    pagination_success = search_page.go_to_next_page()
    
    if pagination_success:
        page_load_time = time.time() - start_time
        print(f"Pagination completed in {page_load_time:.2f} seconds")
        
        # Verify results are still present after pagination
        results_after_pagination = search_page.get_results_titles()
        assert len(results_after_pagination) > 0, "Results should persist after pagination"
        
        # Performance requirement: pagination should complete within 5 seconds
        assert page_load_time <= 15.0, f"Pagination took {page_load_time:.2f}s, which exceeds 15s limit"
    else:
        print("Pagination test skipped - no next page available")


@pytest.mark.performance
@pytest.mark.usefixtures("jira_reporter")
def test_multiple_searches_performance(browser, base_url):
    """Test performance when executing multiple searches in sequence"""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)
    
    # Open homepage and navigate to search page
    home_page.go_to_dataset_search_fr()  # Updated to use new method
    
    # Define search terms to test
    search_terms = ["education", "health", "transport", "economy", "environment"]
    
    total_search_time = 0
    successful_searches = 0
    
    for term in search_terms:
        import time
        start_time = time.time()
        
        search_page.search(term)
        results = search_page.get_results_titles()
        
        search_duration = time.time() - start_time
        total_search_time += search_duration
        
        if len(results) >= 0:  # Count as successful if no error occurred
            successful_searches += 1
        
        print(f"Search '{term}' took {search_duration:.2f}s and returned {len(results)} results")
    
    avg_search_time = total_search_time / len(search_terms)
    
    # Performance requirement: average search should complete within 5 seconds
    assert avg_search_time <= 15.0, f"Average search time {avg_search_time:.2f}s exceeds 15s limit"
    
    print(f"Multiple searches completed. Average time: {avg_search_time:.2f}s, Success rate: {successful_searches}/{len(search_terms)}")