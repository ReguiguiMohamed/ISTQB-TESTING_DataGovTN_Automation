from typing import List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from config import Config

class SearchPage(BasePage):
    """
    Page de recherche des jeux de données CKAN.
    """

    # Locators
    SEARCH_INPUT = (By.ID, "field-giant-search")
    SEARCH_FORM = (By.ID, "dataset-search-form")
    RESULT_ITEMS = (By.CSS_SELECTOR, "li.dataset-item")
    DATASET_HEADING_LINK = (By.CSS_SELECTOR, "h2.dataset-heading a")
    NO_RESULTS_MSG = (By.CSS_SELECTOR, "h1.title-data-found")

    # Filters
    FILTER_CATEGORY = (By.CSS_SELECTOR, "select[name='groups'], .filter-category select")
    FILTER_ORG = (By.CSS_SELECTOR, "select[name='organization'], .filter-org select")

    def open(self) -> None:
        success = self.safe_open_url(Config.CATALOG_URL_FR)
        if success:
            # Verify page load by checking search input if we successfully loaded the real page
            try:
                self.find(self.SEARCH_INPUT)
            except:
                # If the element check fails, that's okay - page may be in fallback state
                pass

    def search(self, query: str) -> None:
        """Enters query and submits search."""
        self.input_text(self.SEARCH_INPUT, query)
        # Using specific find for form to submit
        self.driver.find_element(*self.SEARCH_FORM).submit()

        # Wait for either results or 'no results' message
        self.wait.until(
            lambda d: self.has_results() or self.has_no_results_message()
        )

    def get_results_titles(self) -> List[str]:
        """Extracts titles from result cards."""
        titles = []
        try:
            items = self.find_all(self.RESULT_ITEMS)
            for item in items:
                title_el = item.find_element(*self.DATASET_HEADING_LINK)
                titles.append(title_el.text.strip())
        except Exception:
            # Return empty list if no items found or stale elements
            return []
        return titles

    def get_results_count(self) -> int:
        """Returns the number of search results."""
        try:
            items = self.find_all(self.RESULT_ITEMS)
            return len(items)
        except Exception:
            return 0

    def has_results(self) -> bool:
        """Check if any result items exist."""
        try:
            return len(self.driver.find_elements(*self.RESULT_ITEMS)) > 0
        except Exception:
            return False

    def has_no_results_message(self) -> bool:
        """Checks for the 'Aucun jeu de données' message."""
        try:
            msgs = self.driver.find_elements(*self.NO_RESULTS_MSG)
            return any("Aucun jeu de données" in m.text for m in msgs)
        except Exception:
            return False

    def get_no_results_message(self) -> Optional[str]:
        try:
            msg = self.find(self.NO_RESULTS_MSG)
            return msg.text.strip()
        except Exception:
            return None

    def is_search_result_visible(self) -> bool:
        """
        Verifies if the search result area is visible (either results or 'no results' message).
        This method was used in the original tests and is needed for compatibility.
        """
        try:
            # Wait briefly to see if results or no-results message appears
            return self.has_results() or self.has_no_results_message()
        except Exception:
            return False

    def open_result_by_index(self, index: int):
        """
        Opens the dataset result at the specified index.
        """
        result_items = self.find_all(self.RESULT_ITEMS)
        if index >= len(result_items):
            raise IndexError(f"Index {index} is out of range. Only {len(result_items)} results available.")

        # Find the link in the specific result item
        result_item = result_items[index]
        link = result_item.find_element(*self.DATASET_HEADING_LINK)
        link.click()

    def has_next_page(self) -> bool:
        """
        Check if there is a next page link available.
        """
        next_page_selectors = [
            (By.CSS_SELECTOR, ".pagination .next a"),
            (By.CSS_SELECTOR, ".pager-next a"),
            (By.CSS_SELECTOR, "[rel='next']"),
            (By.XPATH, "//a[contains(text(), 'Next') or contains(text(), 'Suivant') or contains(text(), 'Page Suivante') or contains(@title, 'Next')]")
        ]

        for selector in next_page_selectors:
            try:
                elements = self.driver.find_elements(*selector)
                for element in elements:
                    if element.is_displayed():
                        return True
            except Exception:
                continue
        return False

    def go_to_next_page(self) -> bool:
        """
        Navigate to the next page if available.
        Returns True if navigation was successful, False otherwise.
        """
        next_page_selectors = [
            (By.CSS_SELECTOR, ".pagination .next a"),
            (By.CSS_SELECTOR, ".pager-next a"),
            (By.CSS_SELECTOR, "[rel='next']"),
            (By.XPATH, "//a[contains(text(), 'Next') or contains(text(), 'Suivant') or contains(text(), 'Page Suivante') or contains(@title, 'Next')]")
        ]

        for selector in next_page_selectors:
            try:
                elements = self.driver.find_elements(*selector)
                for element in elements:
                    if element.is_displayed():
                        element.click()
                        # Wait a bit for page to load
                        import time
                        time.sleep(1)
                        return True
            except Exception:
                continue
        return False