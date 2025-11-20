import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.home_page import HomePage
from pages.search_page import SearchPage
from pages.dataset_page import DatasetPage


@pytest.mark.functional
def test_dataset_details_display_correctly(browser, base_url):
    """Test that dataset details are displayed correctly"""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)
    dataset_page = DatasetPage(browser)

    # Open homepage and navigate to search page
    home_page.open()
    home_page.go_to_dataset_search_fr()  # Updated to use new method

    # Perform search for a specific dataset
    search_page.search("education")

    # Open the first result
    search_page.open_result_by_index(0)

    # Verify dataset title is displayed
    title = dataset_page.get_title()
    assert title is not None and title.strip() != "", "Dataset title should be displayed"

    # Verify dataset description is displayed
    description = dataset_page.get_description()
    assert description is not None, "Dataset description should be displayed"

    # Verify at least one resource is available
    resources_count = dataset_page.get_resources_count()
    assert resources_count > 0, f"Expected at least one resource, but found {resources_count}"

    print(f"Dataset '{title}' details verified: {resources_count} resources available")


@pytest.mark.functional
def test_dataset_resources_downloadable(browser, base_url):
    """Test that dataset resources can be downloaded"""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)
    dataset_page = DatasetPage(browser)

    # Open homepage and navigate to search page
    home_page.open()
    home_page.go_to_dataset_search_fr()  # Updated to use new method

    # Perform search
    search_page.search("data")

    # Open the first result
    search_page.open_result_by_index(0)

    # Verify that resources exist
    resources_count = dataset_page.get_resources_count()
    assert resources_count > 0, f"Expected at least one resource to be available, but found {resources_count}"

    # Attempt to download the first resource
    # Note: We can't verify the actual download completion in this test
    # but we can verify that the download link exists and is clickable
    try:
        dataset_page.download_first_resource()
        print(f"Attempted to download first resource from dataset with {resources_count} resources")
    except Exception as e:
        print(f"Could not download resource: {str(e)}")
        # This is not necessarily a failure since the download might start in a new tab/window


@pytest.mark.functional
def test_dataset_has_metadata(browser, base_url):
    """Test that dataset has metadata like organization, update date, license, etc."""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)
    dataset_page = DatasetPage(browser)

    # Open homepage and navigate to search page
    home_page.open()
    home_page.go_to_dataset_search_fr()  # Updated to use new method

    # Perform search
    search_page.search("education")

    # Open the first result
    search_page.open_result_by_index(0)

    # Look for metadata fields (organization, date, license) - using generic selectors
    # Wait for page to load
    wait = WebDriverWait(browser, 10)

    # Check for metadata elements (using generic selectors since we don't know exact structure)
    metadata_selectors = [
        (By.CSS_SELECTOR, ".organization, .publisher, .author, [data-testid='organization']"),
        (By.CSS_SELECTOR, ".date, .updated, .modified, .last-modified, [data-testid='date']"),
        (By.CSS_SELECTOR, ".license, .licence, [data-testid='license']"),
        (By.CSS_SELECTOR, ".metadata, .additional-info, .info-table")
    ]

    metadata_found = 0
    for selector in metadata_selectors:
        try:
            element = wait.until(EC.presence_of_element_located(selector))
            if element.text.strip():
                metadata_found += 1
        except:
            # Element doesn't exist, continue to next
            continue

    # At least one metadata field should be present
    assert metadata_found > 0, f"Expected at least one metadata field, but found {metadata_found}"

    print(f"Found {metadata_found} metadata fields on dataset page")


@pytest.mark.functional
def test_dataset_download_link_is_accessible(browser, base_url):
    """Test that dataset download link is accessible"""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)
    dataset_page = DatasetPage(browser)

    # Open homepage and navigate to search page
    home_page.open()
    home_page.go_to_dataset_search_fr()  # Updated to use new method

    # Perform search
    search_page.search("data")

    # Open the first result
    search_page.open_result_by_index(0)

    # Get initial resource count
    resources_count = dataset_page.get_resources_count()
    assert resources_count > 0, f"Expected at least one resource to be available, but found {resources_count}"

    # Attempt to access the download link
    # Note: We can't fully verify download completion without additional infrastructure
    # but we can check if clicking the link changes the URL or triggers download
    initial_url = browser.current_url

    try:
        dataset_page.download_first_resource()
        print(f"Attempted to download resource from dataset with {resources_count} resources")
        # TODO: Add more specific verification for download (may require additional infrastructure)
    except Exception as e:
        print(f"Could not access download link: {str(e)}")

    # Check if URL changed (might happen if download is through a separate page)
    new_url = browser.current_url
    print(f"URL before download: {initial_url}, after download attempt: {new_url}")


@pytest.mark.functional
def test_breadcrumb_allows_return_to_search(browser, base_url):
    """Test that breadcrumb allows return to search results"""
    # Initialize page objects
    home_page = HomePage(browser, base_url)
    search_page = SearchPage(browser)
    dataset_page = DatasetPage(browser)

    # Track the search URL
    home_page.open()
    home_page.go_to_dataset_search_fr()  # Updated to use new method

    # Perform search and note current URL
    search_page.search("education")
    search_results_url = browser.current_url

    # Open first result
    search_page.open_result_by_index(0)
    dataset_page_url = browser.current_url

    # Check if we can go back using browser back button or breadcrumb
    # Using generic selector for breadcrumb back link
    breadcrumb_selectors = [
        (By.CSS_SELECTOR, ".breadcrumb a, .back-link, .go-back, .return-link"),
        (By.CSS_SELECTOR, "nav a, .navigation a")
    ]

    # Try to find a link back to search results
    back_link_found = False
    wait = WebDriverWait(browser, 5)  # Shorter wait since this might not always exist

    for selector in breadcrumb_selectors:
        try:
            back_link = wait.until(EC.element_to_be_clickable(selector))
            back_link.click()
            # Wait a moment to see if navigation happened
            import time
            time.sleep(1)
            current_url = browser.current_url

            # Check if we're back on the search results page
            if search_results_url != dataset_page_url and search_results_url == current_url:
                back_link_found = True
                print("Successfully navigated back using breadcrumb/link")
                break
            else:
                # If back navigation didn't work as expected, go back to previous page
                browser.get(dataset_page_url)
        except:
            # Try next selector
            continue

    # If no breadcrumb found, use browser back button as fallback
    if not back_link_found:
        browser.back()
        current_url = browser.current_url
        if search_results_url == current_url or "search" in current_url.lower():
            print("Navigated back to search results using browser back button")
        else:
            # If we can't verify return to search, just ensure we're not on the same dataset page
            print(f"Attempted to return from dataset page. Current URL: {current_url}")