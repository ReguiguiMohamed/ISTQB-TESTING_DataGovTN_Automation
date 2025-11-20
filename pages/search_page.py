from __future__ import annotations

from typing import List, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SearchPage:
    """
    Page de recherche des jeux de données CKAN.
    Exemple d’URL : https://catalog.data.gov.tn/fr/dataset/
    """

    DEFAULT_URL_FR = "https://catalog.data.gov.tn/fr/dataset/"

    # Filter locators (for compatibility with existing tests)
    FILTER_CATEGORY = (By.CSS_SELECTOR, "select[name='groups'], select[name='organization'], select[name='vocab_category'], .filter-category select")
    FILTER_ORGANIZATION = (By.CSS_SELECTOR, "select[name='organization'], select[name='owner_org'], .filter-org select")
    FILTER_FORMAT = (By.CSS_SELECTOR, "select[name='format'], .filter-format select, select[name*='res_format']")

    def __init__(self, driver: WebDriver, timeout: int = 10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # ---------- Navigation ----------

    def open(self, url: Optional[str] = None) -> None:
        """Ouvre la page de recherche (par défaut en français)."""
        target = url or self.DEFAULT_URL_FR
        self.driver.get(target)
        # on attend que le champ de recherche soit visible
        try:
            self.wait.until(
                EC.visibility_of_element_located((By.ID, "field-giant-search"))
            )
        except Exception:
            # Si le champ de recherche n'est pas trouvé immédiatement,
            # attendre un peu plus longtemps ou vérifier si la page a chargé
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # ---------- Eléments de la page ----------

    @property
    def search_input(self):
        return self.wait.until(
            EC.visibility_of_element_located((By.ID, "field-giant-search"))
        )

    @property
    def search_form(self):
        return self.driver.find_element(By.ID, "dataset-search-form")

    def _result_items(self):
        """
        Chaque résultat est un <li class="dataset-item"> dans la liste.
        """
        return self.driver.find_elements(By.CSS_SELECTOR, "li.dataset-item")

    # ---------- Actions ----------

    def search(self, query: str) -> None:
        """
        Effectue une recherche et attend soit des résultats,
        soit le message "Aucun jeu de données trouvé ...".
        """
        field = self.search_input
        field.clear()
        field.send_keys(query)

        self.search_form.submit()

        # Attendre soit des résultats, soit un message "Aucun jeu de données trouvé"
        self.wait.until(
            lambda d: self.has_results() or self.has_no_results_message()
        )

    # ---------- Infos sur les résultats ----------

    def has_results(self) -> bool:
        return len(self._result_items()) > 0

    def get_results_titles(self) -> List[str]:
        """
        Récupère les titres des jeux de données dans les cartes de résultat,
        en lisant <h2 class="dataset-heading"> <a>...</a> </h2>.
        """
        titles: List[str] = []
        for item in self._result_items():
            try:
                link = item.find_element(By.CSS_SELECTOR, "h2.dataset-heading a")
                titles.append(link.text.strip())
            except Exception:
                # On ignore les cartes mal formées
                continue
        return titles

    def open_result_by_index(self, index: int = 0) -> None:
        """
        Clique sur le résultat d’indice donné (0 par défaut).
        """
        items = self._result_items()
        if not items:
            raise AssertionError("Aucun résultat de recherche disponible.")

        if index < 0 or index >= len(items):
            raise IndexError(f"Index {index} hors limites pour {len(items)} résultats.")

        link = items[index].find_element(By.CSS_SELECTOR, "h2.dataset-heading a")
        link.click()

    # ---------- Message d'absence de résultat ----------

    def has_no_results_message(self) -> bool:
        """
        Vérifie la présence du message "Aucun jeu de données trouvé pour ...".
        Ce message est dans <h1 class="title-data-found">.
        """
        msgs = self.driver.find_elements(By.CSS_SELECTOR, "h1.title-data-found")
        return any("Aucun jeu de données trouvé" in m.text for m in msgs)

    def get_no_results_message(self) -> Optional[str]:
        msgs = self.driver.find_elements(By.CSS_SELECTOR, "h1.title-data-found")
        if not msgs:
            return None
        return msgs[0].text.strip()

    # ---------- Pagination ----------

    def has_next_page(self) -> bool:
        """
        Vérifie s'il y a une page suivante dans la pagination.
        """
        next_links = self.driver.find_elements(By.CSS_SELECTOR, "a[rel='next'], li.next a, .pagination-next a")
        return len(next_links) > 0

    def go_to_next_page(self) -> bool:
        """
        Navigue vers la page suivante si disponible.
        Returns True si successful, False otherwise.
        """
        if not self.has_next_page():
            return False

        try:
            next_link = self.driver.find_element(By.CSS_SELECTOR, "a[rel='next'], li.next a, .pagination-next a")
            next_link.click()

            # Attendre que la page se recharge
            self.wait.until(EC.staleness_of(next_link))

            # Attendre que le nouveau jeu de résultats soit chargé
            self.wait.until(
                lambda d: self.has_results() or self.has_no_results_message()
            )

            return True
        except Exception:
            return False

    # ---------- Filter support ----------

    def select_category(self, category: str) -> None:
        """
        Sélectionne une catégorie dans le filtre de catégorie.
        """
        from selenium.webdriver.support.ui import Select
        try:
            category_select = self.driver.find_element(*self.FILTER_CATEGORY)
            select = Select(category_select)
            select.select_by_visible_text(category)
        except Exception:
            # Si le filtre n'est pas disponible ou la catégorie n'existe pas
            pass

    def select_organization(self, organization: str) -> None:
        """
        Sélectionne une organisation dans le filtre d'organisation.
        """
        from selenium.webdriver.support.ui import Select
        try:
            org_select = self.driver.find_element(*self.FILTER_ORGANIZATION)
            select = Select(org_select)
            select.select_by_visible_text(organization)
        except Exception:
            # Si le filtre n'est pas disponible ou l'organisation n'existe pas
            pass

    def select_format(self, format: str) -> None:
        """
        Sélectionne un format dans le filtre de format.
        """
        from selenium.webdriver.support.ui import Select
        try:
            format_select = self.driver.find_element(*self.FILTER_FORMAT)
            select = Select(format_select)
            select.select_by_visible_text(format)
        except Exception:
            # Si le filtre n'est pas disponible ou le format n'existe pas
            pass

    def apply_filters(self) -> None:
        """
        Applique les filtres sélectionnés en soumettant le formulaire de recherche.
        """
        try:
            self.search_form.submit()
            # Attendre que les résultats avec filtres soient chargés
            self.wait.until(
                lambda d: self.has_results() or self.has_no_results_message()
            )
        except Exception:
            # Si la soumission échoue, on continue sans erreur critique
            pass