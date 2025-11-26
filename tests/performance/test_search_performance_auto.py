"""
Performance tests with automatic UI monitoring
"""
import pytest
from selenium.webdriver.common.by import By
from pages.home_page import HomePage
from pages.search_page import SearchPage
from pages.dataset_page import DatasetPage


@pytest.mark.performance  
def test_search_performance_with_monitoring(auto_setup_monitoring, browser):
    home = HomePage(browser)
    search = SearchPage(browser)
    
    # Automatically set up monitoring
    auto_setup_monitoring(home)
    auto_setup_monitoring(search)

    # Performance test with automatic monitoring
    home.go_to_dataset_search_fr()
    search.search("education")
    
    # Monitor performance metrics
    titles = search.get_results_titles()
    assert len(titles) > 0