from selenium.webdriver.remote.webdriver import WebDriver
from pages.base_page import BasePage
from config import Config

class HomePage(BasePage):
    """
    Représente la page d'accueil (Landing Page).
    Point d'entrée principal vers le catalogue CKAN.
    """

    def __init__(self, driver: WebDriver, base_url: str = None):
        super().__init__(driver)
        self.base_url = base_url or Config.BASE_URL

    def open(self) -> None:
        """Ouvre la page d'accueil principale."""
        self.safe_open_url(f"{self.base_url}/")

    def go_to_dataset_search_fr(self) -> None:
        """
        Ouvre directement la page de recherche des jeux de données en français.
        """
        self.safe_open_url(Config.CATALOG_URL_FR)

    def go_to_dataset_search_ar(self) -> None:
        """
        Ouvre directement la page de recherche des jeux de données en arabe.
        """
        self.safe_open_url(Config.CATALOG_URL_AR)