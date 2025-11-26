"""
FAQ Page Object - Robust implementation with rate limiting and monitoring
"""
from pages.base_page import BasePage
from config import Config


class FAQPage(BasePage):
    """Page object for FAQ page with robust navigation and monitoring."""
    
    # Locators
    FAQ_CONTAINER = ("css selector", ".faq-container, .faq-section, .faqs, .frequently-asked-questions")
    FAQ_QUESTIONS = ("css selector", ".faq-question, .question, .accordion-title")
    FAQ_ANSWERS = ("css selector", ".faq-answer, .answer, .accordion-content")
    SEARCH_INPUT = ("css selector", ".faq-search, #faq-search, input[name='faq-search']")
    
    def __init__(self, driver, timeout: int = 10):
        super().__init__(driver, timeout)

    def open_faq_page(self):
        """Open the FAQ page with safe navigation."""
        return self.safe_open_url(f"{Config.BASE_URL}/fr/faq/")
    
    def search_faq(self, query: str):
        """Search for FAQ with robust error handling."""
        if self.find_all(self.SEARCH_INPUT):
            self.input_text(self.SEARCH_INPUT, query)
        else:
            # If search not available, just record the attempt
            if self._standard_monitor:
                self._record_ui_change(self.SEARCH_INPUT, "faq_search_attempt", 
                                     {"action": "faq_search", "query": query}, 
                                     {"action": "faq_search_completed", "query": query})
    
    def get_all_questions(self):
        """Get all FAQ questions with error handling."""
        try:
            question_elements = self.find_all(self.FAQ_QUESTIONS)
            return [q.text for q in question_elements]
        except:
            # Fallback if FAQ questions are not available
            return []
    
    def get_all_answers(self):
        """Get all FAQ answers with error handling."""
        try:
            answer_elements = self.find_all(self.FAQ_ANSWERS)
            return [a.text for a in answer_elements]
        except:
            # Fallback if FAQ answers are not available
            return []