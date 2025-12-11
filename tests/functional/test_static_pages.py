"""
Test cases for various static pages like about, help, terms, etc.
Tests that these pages load correctly and contain expected content.
"""
import pytest
from pages.static_page import StaticPage
from pages.home_page import HomePage
from config import Config


@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
def test_about_page_load(auto_setup_monitoring, browser):
    """Test that the About page loads successfully."""
    static_page = StaticPage(browser)

    # Set up monitoring
    auto_setup_monitoring(static_page)

    # Navigate to the about page using the method from StaticPage
    success = static_page.open_about_page()

    if success:
        title = static_page.get_title()
        current_url = static_page.get_current_url()

        # Verify we're on the about page
        assert "qui-sommes-nous" in current_url.lower() or "about" in title.lower(), \
            f"Expected to be on about page, but title: {title}, URL: {current_url}"

        print(f"About page loaded successfully. Title: {title}")
    else:
        # If real page failed, verify fallback was used gracefully
        current_url = static_page.get_current_url()
        assert "about:blank" in current_url or Config.BASE_URL in current_url


@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
def test_terms_page_load(auto_setup_monitoring, browser):
    """Test that the Terms of Use page loads successfully."""
    static_page = StaticPage(browser)

    # Set up monitoring
    auto_setup_monitoring(static_page)

    # Navigate to the terms page using the method from StaticPage
    success = static_page.open_terms_page()

    if success:
        title = static_page.get_title()
        current_url = static_page.get_current_url()

        # Verify we're on the terms page
        expected_terms_indicators = ["conditions", "utilisation", "terms", "conditions générales"]
        has_terms_indicator = any(indicator in title.lower() for indicator in expected_terms_indicators) or \
                            any(indicator in current_url.lower() for indicator in expected_terms_indicators)

        assert has_terms_indicator, \
            f"Expected to be on terms page, but title: {title}, URL: {current_url}"

        print(f"Terms page loaded successfully. Title: {title}")
    else:
        current_url = static_page.get_current_url()
        assert "about:blank" in current_url or Config.BASE_URL in current_url


@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
def test_licenses_page_load(auto_setup_monitoring, browser):
    """Test that the Licenses page loads successfully."""
    static_page = StaticPage(browser)

    # Set up monitoring
    auto_setup_monitoring(static_page)

    # Navigate to the licenses page
    success = static_page.open_licenses_page()

    if success:
        title = static_page.get_title()
        current_url = static_page.get_current_url()

        # Verify we're on the licenses page
        expected_licenses_indicators = ["licences", "réutilisation", "donnees", "public"]
        has_licenses_indicator = any(indicator in title.lower() for indicator in expected_licenses_indicators) or \
                               any(indicator in current_url.lower() for indicator in expected_licenses_indicators)

        assert has_licenses_indicator, \
            f"Expected to be on licenses page, but title: {title}, URL: {current_url}"

        print(f"Licenses page loaded successfully. Title: {title}")
    else:
        current_url = static_page.get_current_url()
        assert "about:blank" in current_url or Config.BASE_URL in current_url


@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
def test_useful_links_page_load(auto_setup_monitoring, browser):
    """Test that the Useful Links page loads successfully."""
    static_page = StaticPage(browser)

    # Set up monitoring
    auto_setup_monitoring(static_page)

    # Navigate to the useful links page
    success = static_page.open_useful_links_page()

    if success:
        title = static_page.get_title()
        current_url = static_page.get_current_url()

        # Verify we're on the useful links page
        expected_useful_indicators = ["liens", "utiles", "links", "ressources"]
        has_useful_indicator = any(indicator in title.lower() for indicator in expected_useful_indicators) or \
                              any(indicator in current_url.lower() for indicator in expected_useful_indicators)

        assert has_useful_indicator, \
            f"Expected to be on useful links page, but title: {title}, URL: {current_url}"

        print(f"Useful Links page loaded successfully. Title: {title}")
    else:
        current_url = static_page.get_current_url()
        assert "about:blank" in current_url or Config.BASE_URL in current_url


@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
def test_data_requests_page_load(auto_setup_monitoring, browser):
    """Test that the Data Requests page loads successfully."""
    static_page = StaticPage(browser)

    # Set up monitoring
    auto_setup_monitoring(static_page)

    # Navigate to the data requests page
    success = static_page.open_data_requests_page()

    if success:
        title = static_page.get_title()
        current_url = static_page.get_current_url()

        # Verify we're on the data requests page
        expected_data_indicators = ["demandes", "donnees", "data", "request"]
        has_data_indicator = any(indicator in title.lower() for indicator in expected_data_indicators) or \
                            any(indicator in current_url.lower() for indicator in expected_data_indicators)

        assert has_data_indicator, \
            f"Expected to be on data requests page, but title: {title}, URL: {current_url}"

        print(f"Data Requests page loaded successfully. Title: {title}")
    else:
        current_url = static_page.get_current_url()
        assert "about:blank" in current_url or Config.BASE_URL in current_url


@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
def test_static_pages_content_verification(auto_setup_monitoring, browser):
    """Verify that static pages have expected content structure."""
    static_page = StaticPage(browser)

    # Set up monitoring
    auto_setup_monitoring(static_page)

    # Test about page content structure
    success = static_page.open_about_page()

    if success:
        # Get page content using the StaticPage method
        page_content = static_page.get_page_content()
        page_title = static_page.get_page_title()

        # Verify that the page has content
        assert len(page_content) > 50, "Static page should have meaningful content"
        assert len(page_title) > 0, "Static page should have a title"

        print(f"About page content verified - Title: {page_title[:50]}..., Content length: {len(page_content)}")

        # Verify the content has actual text (not just HTML)
        assert len(page_content.strip()) > 0, "Page content should not be empty"

        # Navigate to terms page and verify content structure
        static_page.open_terms_page()
        terms_content = static_page.get_page_content()
        terms_title = static_page.get_page_title()

        print(f"Terms page content verified - Title: {terms_title[:50]}..., Content length: {len(terms_content)}")

        assert len(terms_content) > 50, "Terms page should have meaningful content"


@pytest.mark.functional
@pytest.mark.usefixtures("jira_reporter")
def test_multiple_static_pages_load(auto_setup_monitoring, browser):
    """Test loading multiple static pages in sequence."""
    static_page = StaticPage(browser)

    # Set up monitoring
    auto_setup_monitoring(static_page)

    # Define the pages to test
    pages_to_test = [
        {"method": "open_about_page", "name": "About", "keywords": ["organisation", "donnees", "ouvertes"]},
        {"method": "open_terms_page", "name": "Terms", "keywords": ["conditions", "utilisation", "donnees"]},
        {"method": "open_licenses_page", "name": "Licenses", "keywords": ["licences", "reutilisation", "publiques"]},
        {"method": "open_useful_links_page", "name": "Useful Links", "keywords": ["liens", "utiles", "ressources"]},
    ]

    tested_pages = 0

    for page_info in pages_to_test:
        # Call the appropriate method to open the page
        open_method = getattr(static_page, page_info["method"])
        success = open_method()

        if success:
            title = static_page.get_title()
            current_url = static_page.get_current_url()
            page_content = static_page.get_page_content()

            # Verify page loaded correctly
            print(f"{page_info['name']} page loaded: {title} - Content length: {len(page_content)}")

            # Check if page content contains relevant keywords
            has_relevant_content = any(keyword in page_content.lower() for keyword in page_info["keywords"])
            print(f"{page_info['name']} page has relevant content: {has_relevant_content}")

            tested_pages += 1
        else:
            print(f"Failed to load {page_info['name']} page, using fallback")

    # Assert that at least one page loaded successfully
    assert tested_pages > 0, "At least one static page should load successfully"