"""
Tests for bugs on the Dataset Catalog page.
"""
import pytest
from pages.dataset_catalog_page import DatasetCatalogPage

@pytest.mark.functional
def test_api_link_is_broken(browser):
    """
    Tests Bug #3: The API link on the dataset page leads to a non-functional page.
    1. Navigates to the dataset catalog page.
    2. Clicks the 'API' link.
    3. Asserts that the resulting page contains the incorrect plain text '{'version': 3}'.
    """
    dataset_page = DatasetCatalogPage(browser)
    dataset_page.open()

    dataset_page.click_api_link()

    content = dataset_page.get_api_page_content()
    
    expected_broken_text = '{"version": 3}'
    
    assert expected_broken_text in content, f"BUG CONFIRMED: API page shows incorrect content. Expected to find '{expected_broken_text}' but got '{content}'."
