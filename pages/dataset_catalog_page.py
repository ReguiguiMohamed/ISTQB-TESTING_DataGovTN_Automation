"""
Page Object for the Dataset Catalog page.
"""
from pages.base_page import BasePage
from selenium.webdriver.common.by import By
import time


class DatasetCatalogPage(BasePage):
    """
    Page object for https://catalog.data.gov.tn/fr/dataset
    """
    API_LINK = (By.PARTIAL_LINK_TEXT, "API")
    API_PAGE_CONTENT = (By.TAG_NAME, "pre")

    def __init__(self, driver, timeout: int = 10):
        super().__init__(driver, timeout)
        self.url = "https://catalog.data.gov.tn/fr/dataset"

    def open(self):
        """Navigates to the dataset catalog page."""
        self.open_url(self.url)

    def click_api_link(self):
        """
        Scrolls the API link into view and clicks it using JavaScript to
        avoid interception.
        """
        element = self.find(self.API_LINK)
        # Scroll the element into the middle of the screen to ensure it's not obscured
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        # Small pause to allow any lazy-loaded content/animations to settle
        time.sleep(1)
        # Click using JavaScript
        self.driver.execute_script("arguments[0].click();", element)

    def get_api_page_content(self):
        """Gets the content of the API page."""
        return self.find(self.API_PAGE_CONTENT).text
