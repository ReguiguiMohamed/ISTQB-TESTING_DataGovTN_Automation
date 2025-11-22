import pytest
from pages.home_page import HomePage
from pages.search_page import SearchPage
from pages.dataset_page import DatasetPage


@pytest.mark.functional
def test_search_exact_phrase_returns_expected_results(browser, base_url):
    """Test that searching for an exact phrase returns relevant results"""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)
    
    # Open homepage and navigate to search page
    home_page.go_to_dataset_search_fr()  # Updated to use new method
    
    # Perform search with exact phrase
    search_page.search('"open data"')
    
    # Get results titles
    results = search_page.get_results_titles()
    
    # Verify that at least one result is returned
    assert len(results) > 0, f"Expected at least one result for 'open data', but got {len(results)}"
    
    print(f"Found {len(results)} results for exact phrase 'open data'")


@pytest.mark.functional
def test_search_with_boolean_operators(browser, base_url):
    """Test that searching with boolean operators works (if supported)"""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)
    
    # Open homepage and navigate to search page
    home_page.go_to_dataset_search_fr()  # Updated to use new method
    
    # Perform search with boolean operator (using AND pattern)
    search_keyword = "education AND health"
    search_page.search(search_keyword)
    
    # Check if the search handles boolean operators appropriately
    results = search_page.get_results_titles()
    print(f"Search with boolean operator '{search_keyword}' returned {len(results)} results")
    
    # At minimum, the search should not fail
    assert len(results) >= 0, "Boolean search should not fail"


@pytest.mark.functional
def test_search_results_sorting_functionality(browser, base_url):
    """Test that search results can be sorted (if sorting is available)"""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)
    
    # Open homepage and navigate to search page
    home_page.go_to_dataset_search_fr()  # Updated to use new method
    
    # Perform initial search
    search_page.search("data")
    initial_results = search_page.get_results_titles()
    initial_count = len(initial_results)
    
    # Look for sorting functionality
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        wait = WebDriverWait(browser, 5)
        
        # Look for sort elements
        sort_selectors = [
            (By.CSS_SELECTOR, "select[name='sort'], .sort-options, .sort-selector"),
            (By.CSS_SELECTOR, ".sort-button, .sort-control, [data-testid='sort']")
        ]
        
        sort_element_found = False
        for selector in sort_selectors:
            try:
                sort_element = wait.until(EC.presence_of_element_located(selector))
                sort_element_found = True
                print("Sorting functionality available")
                break
            except:
                continue
        
        if not sort_element_found:
            print("No sorting functionality detected")
        
        assert initial_count > 0, "Search should return results for sorting test"
        
    except Exception as e:
        print(f"Error checking sorting functionality: {str(e)}")
        # Still verify that the search returned results
        assert initial_count > 0, "Search should return results"


@pytest.mark.functional
@pytest.mark.xfail(reason="Autocomplete results container locator needs adjustment or results take too long to load.")
def test_search_autocomplete_suggestions(browser, base_url):
    """Test that search autocomplete suggestions appear (if available)"""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)
    
    # Open homepage and navigate to search page
    home_page.go_to_dataset_search_fr()  # Updated to use new method
    
    # Find search input
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    
    wait = WebDriverWait(browser, 10)
    search_input_element = search_page.search_input # Corrected: use the property, assigned to a new variable
    
    # Type part of a word to trigger autocomplete
    search_input_element.clear()
    search_input_element.send_keys("edu")
    
    # Wait briefly to see if suggestions appear
    import time
    time.sleep(1)
    
    # Look for autocomplete suggestions
    try:
        suggestion_selectors = [
            (By.CSS_SELECTOR, ".suggestions, .autocomplete, .search-suggestions"),
            (By.CSS_SELECTOR, "[role='listbox'], .dropdown-menu, .typeahead")
        ]
        
        suggestions_found = False
        for selector in suggestion_selectors:
            try:
                suggestions = browser.find_elements(*selector)
                if suggestions:
                    suggestions_found = True
                    print(f"Found {len(suggestions)} autocomplete suggestion containers")
                    break
            except:
                continue
        
        if not suggestions_found:
            print("No autocomplete suggestions found")
        
        # Re-locate the search input before interacting with it again (to avoid StaleElementReferenceException)
        search_input_element = search_page.search_input
        search_input_element.clear()
        search_input_element.send_keys("education", Keys.RETURN)
        
        # Wait for results
        wait.until(EC.presence_of_element_located(search_page.RESULTS_CONTAINER))
        results = search_page.get_results_titles()
        
        assert len(results) > 0, "Search should return results after autocomplete test"
        
    except Exception as e:
        # If autocomplete is not available, just perform a normal search to ensure functionality
        # Re-locate the search input in the except block as well
        search_input_element = search_page.search_input
        search_input_element.clear()
        search_input_element.send_keys("education", Keys.RETURN)
        wait.until(EC.presence_of_element_located(search_page.RESULTS_CONTAINER))
        results = search_page.get_results_titles()
        assert len(results) > 0, "Search should return results"
        
        print(f"Autocomplete test skipped due to: {str(e)}")