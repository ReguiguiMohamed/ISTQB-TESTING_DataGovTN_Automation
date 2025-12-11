import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By

from pages.home_page import HomePage
from pages.search_page import SearchPage
from pages.dataset_page import DatasetPage


@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
def test_search_with_valid_keyword_returns_results(browser):
    home = HomePage(browser)
    search = SearchPage(browser)

    try:
        home.go_to_dataset_search_fr()
        search.search("budget")
    except WebDriverException as e:
        # Le site ou le réseau a fermé la connexion
        if "ERR_CONNECTION_CLOSED" in str(e):
            pytest.xfail("Site catalog.data.gov.tn a fermé la connexion (ERR_CONNECTION_CLOSED)")
        raise

    titles = search.get_results_titles()
    assert len(titles) > 0, "Aucun résultat trouvé pour le mot-clé 'budget'"


@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
def test_search_results_persist_after_pagination(browser, base_url):
    """Test that search results persist after navigating to next page"""
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)

    home_page.go_to_dataset_search_fr()

    # utilise un mot-clé qui renvoie vraiment des résultats
    search_page.search("budget")

    initial_results = search_page.get_results_titles()
    assert len(initial_results) > 0, "Initial search should return results"

    # TODO: ici seulement tu enchaînes avec la pagination
    # ex: search_page.go_to_next_page() si tu as implémenté la méthode
    # puis tu refais get_results_titles() et tu vérifies que ça ne revient pas à 0

    # Vérifier s'il y a une page suivante avant de naviguer
    if search_page.has_next_page():
        # Naviguer vers la page suivante
        pagination_success = search_page.go_to_next_page()

        assert pagination_success, "La navigation vers la page suivante devrait réussir"

        # Récupérer les résultats après la pagination
        results_after_pagination = search_page.get_results_titles()

        # Vérifier que les résultats persistent après la pagination
        assert len(results_after_pagination) > 0, "Les résultats devraient persister après la pagination"
        assert len(results_after_pagination) > 0, f"Il devrait y avoir des résultats après pagination, mais trouvé {len(results_after_pagination)}"

        print(f"Résultats initiaux: {len(initial_results)}, Résultats après pagination: {len(results_after_pagination)}")
    else:
        # Si aucune page suivante n'est disponible, vérifier qu'on a quand même des résultats initiaux
        print(f"Pas de page suivante disponible, mais {len(initial_results)} résultats initiaux trouvés")
        assert len(initial_results) > 0, "Il devrait y avoir des résultats initiaux même sans pagination"


@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
def test_open_first_dataset_has_title_and_resources(browser):
    home = HomePage(browser)
    search = SearchPage(browser)
    dataset_page = DatasetPage(browser)

    try:
        home.go_to_dataset_search_fr()
        search.search("budget")
    except WebDriverException as e:
        if "ERR_CONNECTION_CLOSED" in str(e):
            pytest.xfail("Site catalog.data.gov.tn a fermé la connexion (ERR_CONNECTION_CLOSED)")
        raise

    assert search.has_results(), "Aucun résultat pour 'budget', impossible de tester le dataset"

    search.open_result_by_index(0)
    dataset_page.wait_loaded()

    title = dataset_page.get_title()
    resources_count = dataset_page.get_resources_count()

    assert title.strip() != "", "Le titre du dataset est vide"
    assert resources_count > 0, "Le dataset ne contient aucune ressource"


@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
def test_search_with_auto_monitoring(auto_setup_monitoring, browser):
    home = HomePage(browser)
    search = SearchPage(browser)

    # Automatically set up monitoring for both page objects
    auto_setup_monitoring(home)
    auto_setup_monitoring(search)

    # 1. Go to the search page - all interactions are now automatically monitored
    home.go_to_dataset_search_fr()

    # 2. Search - all clicks, inputs, and loading states are monitored automatically
    search.search("education")

    # All UI state changes are automatically documented without additional code!
    titles = search.get_results_titles()
    assert len(titles) > 0