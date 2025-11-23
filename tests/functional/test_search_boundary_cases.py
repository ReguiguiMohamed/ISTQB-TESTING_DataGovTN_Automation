import pytest
from pages.home_page import HomePage
from pages.search_page import SearchPage

@pytest.mark.functional
@pytest.mark.boundary
class TestSearchBoundaryCases:
    """
    Test suite for handling boundary values in search.
    """

    @pytest.fixture(autouse=True)
    def setup_pages(self, browser):
        self.home_page = HomePage(browser)
        self.search_page = SearchPage(browser)
        self.home_page.go_to_dataset_search_fr()

    def test_search_with_minimum_length_string(self):
        """Single character search."""
        min_char = "a"
        self.search_page.search(min_char)
        assert self.search_page.is_search_result_visible(), "Should handle single char input"
        print(f"Search with '{min_char}' executed successfully.")

    def test_search_with_long_string(self):
        """Very long string (255 chars)."""
        long_string = "a" * 255
        self.search_page.search(long_string)
        # Should not crash (Internal Server Error 500)
        assert self.search_page.is_search_result_visible(), "Should handle 255 chars without crash"
        print("Search with a 255-character string executed successfully.")

    def test_search_with_numeric_string(self):
        """Numeric input."""
        numeric = "1234567890"
        self.search_page.search(numeric)
        assert self.search_page.is_search_result_visible()
        print(f"Search with numeric string '{numeric}' executed successfully.")

