"""
Page Object for the Dataset Catalog page.
"""
from pages.base_page import BasePage
from selenium.webdriver.common.by import By


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
        """Clicks the API link in the footer description."""
        self.click(self.API_LINK)

    def get_api_page_content(self):
        """Gets the content of the API page."""
        return self.find(self.API_PAGE_CONTENT).text
