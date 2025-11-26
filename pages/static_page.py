"""
Static Content Page Object - Robust implementation for various static pages
"""
from pages.base_page import BasePage
from config import Config


class StaticPage(BasePage):
    """Generic page object for static content pages with robust navigation and monitoring."""
    
    # Common locators for static pages
    PAGE_TITLE = ("css selector", "h1, .page-title, .title")
    PAGE_CONTENT = ("css selector", ".page-content, .content, .main-content, article")
    BACK_BUTTON = ("css selector", ".back-btn, .back-button, [data-back], a[href^='/']")
    
    def __init__(self, driver, timeout: int = 10):
        super().__init__(driver, timeout)

    def open_about_page(self):
        """Open the about us page with safe navigation."""
        return self.safe_open_url(f"{Config.BASE_URL}/fr/qui-sommes-nous/")
    
    def open_terms_page(self):
        """Open the terms of use page with safe navigation."""
        return self.safe_open_url(f"{Config.BASE_URL}/fr/conditions-générales-dutilisation/")
    
    def open_licenses_page(self):
        """Open the licenses page with safe navigation."""
        return self.safe_open_url(f"{Config.BASE_URL}/fr/licences-de-réutilisation-des-données-publiques-ouvertes/")
    
    def open_useful_links_page(self):
        """Open the useful links page with safe navigation."""
        return self.safe_open_url(f"{Config.BASE_URL}/fr/liens-utiles/")
    
    def open_data_requests_page(self):
        """Open the data requests page with safe navigation."""
        return self.safe_open_url(f"{Config.BASE_URL}/fr/demandes-de-donnees/")
    
    def get_page_title(self):
        """Get page title with error handling."""
        try:
            if self.find_all(self.PAGE_TITLE):
                return self.find(self.PAGE_TITLE).text
            return self.get_title()
        except:
            return self.get_title()
    
    def get_page_content(self):
        """Get page content with error handling."""
        try:
            if self.find_all(self.PAGE_CONTENT):
                content_element = self.find(self.PAGE_CONTENT)
                return content_element.text
            # If no specific content container, get main content
            body_text = self.driver.find_element("tag name", "body").text
            return body_text[:1000]  # Return first 1000 chars to avoid huge content
        except:
            return ""
    
    def has_content(self, text: str):
        """Check if page contains specific text with error handling."""
        try:
            page_content = self.get_page_content()
            return text.lower() in page_content.lower()
        except:
            return False
    
    def navigate_back(self):
        """Navigate back with error handling."""
        try:
            if self.find_all(self.BACK_BUTTON):
                self.click(self.BACK_BUTTON)
            else:
                # Use browser back if no specific back button
                self.driver.back()
        except Exception as e:
            # If browser back also fails, try to load a safe fallback
            if self._standard_monitor:
                self._record_ui_change(("tag name", "body"), "navigation_back_error", 
                                     {"action": "navigate_back", "error": str(e)}, 
                                     {"action": "navigate_back_error"})
            self.safe_open_url("about:blank")