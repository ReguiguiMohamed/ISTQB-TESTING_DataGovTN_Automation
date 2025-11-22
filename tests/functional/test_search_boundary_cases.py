import pytest
from pages.home_page import HomePage
from pages.search_page import SearchPage

# These tests focus on boundary value analysis for the search input field.

@pytest.mark.functional
@pytest.mark.boundary
class TestSearchBoundaryCases:
    """
    Test suite for handling boundary values in the search functionality.
    """

    @pytest.fixture(autouse=True)
    def setup_pages(self, browser, base_url):
        """Setup page objects for each test in the class."""
        self.home_page = HomePage(browser, base_url)
        self.search_page = SearchPage(browser)
        self.home_page.go_to_dataset_search_fr()

    def test_search_with_minimum_length_string(self):
        """
        Tests how the application handles a search with a single character.
        Expected: The application should either return results or handle it gracefully
        without errors.
        """
        min_char = "a"
        self.search_page.search(min_char)
        # The primary assertion is that the search executes without crashing.
        # We can optionally check if results are returned or a message is shown.
        assert self.search_page.is_search_result_visible(), \
            "Search with minimum length string should execute without errors."
        print(f"Search with '{min_char}' executed successfully.")

    def test_search_with_long_string(self):
        """
        Tests the system's behavior with a very long search string.
        Expected: The application should not crash or produce an error. It should
        either truncate the string or handle it properly.
        """
        long_string = "a" * 255
        self.search_page.search(long_string)
        assert self.search_page.is_search_result_visible(), \
            "Search with a very long string should not break the search functionality."
        print("Search with a 255-character string executed successfully.")

    def test_search_with_leading_and_trailing_spaces(self):
        """
        Tests if the search trims whitespace from the search term.
        Expected: Searching for '  term  ' should yield the same results as 'term'.
        """
        search_term = "education"
        search_term_with_spaces = f"  {search_term}  "
        
        # Search with the term surrounded by spaces
        self.search_page.search(search_term_with_spaces)
        results_with_spaces = self.search_page.get_results_count()

        # Perform a new search with the clean term
        self.search_page.search(search_term)
        results_without_spaces = self.search_page.get_results_count()

        assert results_with_spaces == results_without_spaces, \
            "Search should trim leading/trailing whitespace from the query."
        print("Search correctly handles leading and trailing whitespace.")

    def test_search_with_numeric_string(self):
        """
        Tests searching with a string that consists only of numbers.
        Expected: The search should execute correctly, likely returning few or no results,
        but without application errors.
        """
        numeric_string = "1234567890"
        self.search_page.search(numeric_string)
        assert self.search_page.is_search_result_visible(), \
            "Search with a numeric string should execute without errors."
        print("Search with a numeric string executed successfully.")

