"""
Page Object for the "Mes contributions" page and its sub-pages.
"""
from pages.base_page import BasePage
from selenium.webdriver.common.by import By


class ContributionsPage(BasePage):
    """
    Page object for the user's contributions dashboard (/fr/cms/contributions/).
    """
    # Links on the main contributions dashboard
    PROPOSITIONS_LINK = (By.CSS_SELECTOR, "a[href*='/fr/cms/contributions/mes-reutilisations/']")
    DEMANDES_LINK = (By.CSS_SELECTOR, "a[href*='/fr/cms/contributions/mes-demandes/']")
    SIGNALEMENTS_LINK = (By.CSS_SELECTOR, "a[href*='/fr/cms/contributions/mes-anomalies/']")
    COMMENTAIRES_LINK = (By.CSS_SELECTOR, "a[href*='/fr/cms/contributions/mes-commentaires/']")

    # Elements on the sub-pages (e.g., after clicking "Propositions")
    ADD_NEW_BUTTON = (By.CSS_SELECTOR, ".btn-success, .add-new, a[href*='/add/']")

    def __init__(self, driver, timeout: int = 10):
        super().__init__(driver, timeout)

    def go_to_propositions(self):
        """Navigates to the 'Propositions' (reuses) section."""
        self.click(self.PROPOSITIONS_LINK)

    def click_add_new_button(self):
        """Clicks the 'add new' button on a contribution list page."""
        if self.find_all(self.ADD_NEW_BUTTON):
            self.click(self.ADD_NEW_BUTTON)
            return True
        return False
