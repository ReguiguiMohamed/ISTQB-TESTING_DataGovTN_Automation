import pytest
import time
from selenium.webdriver.common.by import By
from pages.home_page import HomePage
from pages.search_page import SearchPage
from config import Config

@pytest.mark.stress
@pytest.mark.usefixtures("jira_reporter")
def test_concurrent_search_load(auto_setup_monitoring, browser):
    """Test how the system handles repeated searches in a short time."""
    home_page = HomePage(browser)
    search_page = SearchPage(browser)

    # Set up automatic monitoring
    auto_setup_monitoring(home_page)
    auto_setup_monitoring(search_page)

    home_page.go_to_dataset_search_fr()

    keywords = ["data", "education", "santé", "transport", "economie"]

    for i, keyword in enumerate(keywords):
        start_time = time.time()
        search_page.search(keyword)

        results = search_page.get_results_titles()
        duration = time.time() - start_time

        print(f"Search {i+1} ('{keyword}') took {duration:.2f}s. Results: {len(results)}")

        # Assertion: Search should not fail (return results or explicit no-result)
        assert search_page.is_search_result_visible(), f"Search {i+1} failed UI check"

@pytest.mark.stress
@pytest.mark.usefixtures("jira_reporter")
def test_repeated_search_does_not_crash(browser):
    """Test stability under repetition (20 iterations)."""
    home_page = HomePage(browser)
    search_page = SearchPage(browser)

    home_page.go_to_dataset_search_fr()

    keyword = "data"
    iterations = 20

    for i in range(iterations):
        search_page.search(keyword)

        # Verify browser is still alive and on correct page
        current_url = search_page.get_current_url()
        assert "dataset" in current_url, f"Navigation lost on iteration {i}"
        assert search_page.is_search_result_visible(), f"UI broken on iteration {i}"