import pytest

from pages.home_page import HomePage
from pages.search_page import SearchPage
from pages.dataset_page import DatasetPage


@pytest.mark.cross_browser
def test_homepage_dataset_search_smoke(browser, base_url):
    """
    Smoke test: verify that the French dataset search page loads correctly
    in every browser (title, URL, and search UI available).
    """
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)

    # Open the French dataset search page
    home_page.go_to_dataset_search_fr()

    # Basic page-level checks
    assert browser.current_url.startswith(
        "https://catalog.data.gov.tn/"
    ), f"Unexpected catalog URL in {browser.name}: {browser.current_url}"
    assert "/fr/dataset" in browser.current_url, (
        f"Expected French dataset path in {browser.name}, got {browser.current_url}"
    )

    assert browser.title is not None and browser.title.strip(), (
        f"Page should have a non-empty title in {browser.name}"
    )

    # UI-level: search area is visible (either results or 'no results' message)
    assert search_page.is_search_result_visible(), (
        f"Search area should be visible on initial load in {browser.name}"
    )


@pytest.mark.cross_browser
@pytest.mark.parametrize("search_keyword", ["data", "education", "santé"])
def test_cross_browser_basic_search_smoke(browser, base_url, search_keyword):
    """
    Smoke test: the same basic search scenario should behave consistently
    across Chrome, Firefox and Edge.
    """
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)

    # Navigate directly to the dataset search page
    home_page.go_to_dataset_search_fr()

    # Perform a basic search
    search_page.search(search_keyword)

    # Verify that the page reacts in a meaningful way
    assert search_page.is_search_result_visible(), (
        f"Search area should show results or a 'no results' message "
        f"for '{search_keyword}' in {browser.name}"
    )

    # If there are results, they should be well-formed
    if search_page.has_results():
        titles = search_page.get_results_titles()
        assert titles, (
            f"Expected at least one non-empty result title for '{search_keyword}' "
            f"in {browser.name}"
        )
        assert all(t.strip() for t in titles), (
            f"All result titles should be non-empty strings in {browser.name}"
        )
    else:
        # Fallback: explicit "no results" message should be visible
        no_results_msg = search_page.get_no_results_message()
        assert no_results_msg, (
            f"Expected a 'no results' message when no datasets match '{search_keyword}' "
            f"in {browser.name}"
        )


@pytest.mark.cross_browser
@pytest.mark.parametrize("search_keyword", ["population", "transport"])
def test_cross_browser_end_to_end_dataset_details(browser, base_url, search_keyword):
    """
    More complex cross-browser smoke flow:
    - open catalog in FR
    - search for a keyword
    - open the first dataset
    - validate dataset title and resources section.
    """
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)
    dataset_page = DatasetPage(browser)

    # Step 1: navigate to the search page
    home_page.go_to_dataset_search_fr()
    assert search_page.is_search_result_visible(), (
        f"Initial search results area should be visible in {browser.name}"
    )

    # Step 2: execute the search
    search_page.search(search_keyword)
    assert search_page.is_search_result_visible(), (
        f"After searching '{search_keyword}', search results area "
        f"should be visible in {browser.name}"
    )

    # Guard: if no datasets are found for this keyword, we still consider
    # the behavior valid, but we stop the end-to-end journey.
    if not search_page.has_results():
        no_results_msg = search_page.get_no_results_message()
        assert no_results_msg, (
            f"Expected a 'no results' message when no datasets match '{search_keyword}' "
            f"in {browser.name}"
        )
        return

    # Step 3: open the first dataset in the list
    search_page.open_result_by_index(0)
    dataset_page.wait_loaded()

    # Step 4: validate dataset details
    title = dataset_page.get_title()
    assert title, f"Dataset page should have a non-empty <h1> title in {browser.name}"

    # Resources section is an important part of the dataset detail page;
    # we don't force a minimum number (some datasets may legitimately have 0),
    # but we do check that the structure is stable across browsers.
    resources_count = dataset_page.get_resources_count()
    assert resources_count >= 0, (
        f"Resources count should be a non-negative integer in {browser.name}"
    )
    formats = dataset_page.get_resources_formats()

    # If there are resources, they should expose at least one format label
    if resources_count > 0:
        assert formats, (
            f"Expected at least one resource format when there are resources "
            f"listed in {browser.name}"
        )


# Example commands to run these tests (locally, in CI or inside Docker):
#   pytest tests/cross_browser/test_smoke_cross_browser.py --browser=chrome
#   pytest tests/cross_browser/test_smoke_cross_browser.py --browser=firefox
#   pytest tests/cross_browser/test_smoke_cross_browser.py --browser=edge
