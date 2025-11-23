from typing import List, Optional
from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class DatasetPage(BasePage):
    """
    Page de détail d’un jeu de données CKAN.
    """

    # Locators
    TITLE = (By.CSS_SELECTOR, "h1")
    DESCRIPTION = (By.CSS_SELECTOR, "p#descriptionId.description, .notes")
    RESOURCE_LIST_ITEMS = (By.CSS_SELECTOR, "section#dataset-resources ul.resource-list li.resource-item")
    RESOURCE_FORMAT_LABEL = (By.CSS_SELECTOR, "span.format-label")
    RESOURCE_DOWNLOAD_LINK = (By.CSS_SELECTOR, "a.resource-url-analytics, a.heading.file-name")

    def wait_loaded(self) -> "DatasetPage":
        """Waits for the main title to be visible."""
        self.find(self.TITLE)
        return self

    def get_title(self) -> str:
        """Returns the dataset title."""
        return self.find(self.TITLE).text.strip()

    def get_description(self) -> str:
        """Returns the dataset description if present."""
        try:
            return self.find(self.DESCRIPTION).text.strip()
        except Exception:
            return ""

    def get_resources_count(self) -> int:
        """Returns the number of resources listed."""
        try:
            return len(self.find_all(self.RESOURCE_LIST_ITEMS))
        except Exception:
            return 0

    def get_resources_formats(self) -> List[str]:
        """Returns a list of format labels (e.g., 'CSV', 'PDF')."""
        formats = []
        try:
            items = self.find_all(self.RESOURCE_LIST_ITEMS)
            for item in items:
                try:
                    span = item.find_element(*self.RESOURCE_FORMAT_LABEL)
                    fmt = span.get_attribute("data-format") or span.text
                    if fmt:
                        formats.append(fmt.strip())
                except Exception:
                    continue
        except Exception:
            pass
        return formats

    def download_first_resource(self) -> None:
        """Clicks the download link of the first resource."""
        items = self.find_all(self.RESOURCE_LIST_ITEMS)
        if not items:
            raise AssertionError("Aucune ressource disponible pour le téléchargement.")

        first_item = items[0]
        # Find the link within the first list item
        links = first_item.find_elements(*self.RESOURCE_DOWNLOAD_LINK)
        
        if not links:
            raise AssertionError("Aucun lien de téléchargement trouvé pour la première ressource.")
            
        links[0].click()