from selenium.webdriver.remote.webdriver import WebDriver


class HomePage:
    """
    Représente la page d'accueil https://data.gov.tn.
    Cette page sert surtout de point d'entrée pour aller vers le catalogue CKAN.
    """

    def __init__(self, driver: WebDriver, base_url: str = "https://data.gov.tn"):
        self.driver = driver
        self.base_url = base_url.rstrip("/")

    def open(self) -> None:
        """Ouvre la page d'accueil principale."""
        self.driver.get(f"{self.base_url}/")

    def go_to_dataset_search_fr(self) -> None:
        """
        Ouvre directement la page de recherche des jeux de données en français.
        On passe par l’URL du catalogue CKAN.
        """
        self.driver.get("https://catalog.data.gov.tn/fr/dataset/")

    def go_to_dataset_search_ar(self) -> None:
        """
        Ouvre directement la page de recherche des jeux de données en arabe.
        """
        self.driver.get("https://catalog.data.gov.tn/ar/dataset/")