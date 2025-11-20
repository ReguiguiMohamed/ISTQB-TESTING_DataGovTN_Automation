from __future__ import annotations

from typing import List, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class DatasetPage:
    """
    Page de détail d’un jeu de données CKAN.
    Exemple d’URL (AR) :
    https://catalog.data.gov.tn/ar/dataset/subventions-accordees-aux-associations-culturelles-de-manouba-pour-l-annee-2024
    """

    def __init__(self, driver: WebDriver, timeout: int = 10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # ---------- Synchronisation ----------

    def wait_loaded(self) -> "DatasetPage":
        """
        Attend que le titre principal <h1> soit visible.
        """
        self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "h1"))
        )
        return self

    # ---------- Titre & description ----------

    def get_title(self) -> str:
        h1 = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "h1"))
        )
        return h1.text.strip()

    def get_description(self) -> str:
        """
        Description fonctionnelle du jeu de données :
        <p id="descriptionId" class="description">...</p>
        """
        try:
            p = self.driver.find_element(
                By.CSS_SELECTOR, "p#descriptionId.description"
            )
            return p.text.strip()
        except Exception:
            return ""

    # ---------- Ressources ----------

    def _resource_items(self):
        """
        Chaque ressource est un <li class="resource-item"> dans
        <section id="dataset-resources"> <ul class="resource-list">.
        """
        return self.driver.find_elements(
            By.CSS_SELECTOR,
            "section#dataset-resources ul.resource-list li.resource-item",
        )

    def get_resources_count(self) -> int:
        return len(self._resource_items())

    def get_resources_formats(self) -> List[str]:
        """
        Récupère les formats via <span class="format-label" data-format="...">.
        """
        formats: List[str] = []
        for li in self._resource_items():
            try:
                span = li.find_element(By.CSS_SELECTOR, "span.format-label")
                fmt = span.get_attribute("data-format") or span.text
                if fmt:
                    formats.append(fmt.strip())
            except Exception:
                continue
        return formats

    def get_first_resource_download_url(self) -> Optional[str]:
        """
        Essaie de récupérer l’URL de téléchargement de la première ressource.
        On privilégie <a class="resource-url-analytics"> puis, à défaut,
        le lien principal de la ressource (<a.heading.file-name>).
        """
        items = self._resource_items()
        if not items:
            return None

        first = items[0]

        links = first.find_elements(By.CSS_SELECTOR, "a.resource-url-analytics")
        if not links:
            links = first.find_elements(By.CSS_SELECTOR, "a.heading.file-name")

        if not links:
            return None

        return links[0].get_attribute("href")

    def download_first_resource(self) -> None:
        """
        Clique sur la première ressource pour initier le téléchargement.
        """
        items = self._resource_items()
        if not items:
            raise AssertionError("Aucune ressource disponible pour le téléchargement.")

        first = items[0]

        links = first.find_elements(By.CSS_SELECTOR, "a.resource-url-analytics")
        if not links:
            links = first.find_elements(By.CSS_SELECTOR, "a.heading.file-name")

        if not links:
            raise AssertionError("Aucun lien de téléchargement trouvé pour la première ressource.")

        links[0].click()