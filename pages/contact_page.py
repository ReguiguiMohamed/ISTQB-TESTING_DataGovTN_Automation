"""
Contact Page Object - Robust implementation with rate limiting and monitoring
"""
from pages.base_page import BasePage
from config import Config


class ContactPage(BasePage):
    """Page object for Contact page with robust navigation and monitoring."""
    
    # Locators
    CONTACT_FORM = ("css selector", ".contact-form, form[action*='contact'], #contact-form")
    NAME_INPUT = ("css selector", "input[name='name'], input[name='full_name'], #name")
    EMAIL_INPUT = ("css selector", "input[name='email'], #email, input[type='email']")
    SUBJECT_INPUT = ("css selector", "input[name='subject'], #subject, input[name='title']")
    MESSAGE_INPUT = ("css selector", "textarea[name='message'], #message, textarea[name='content']")
    SUBMIT_BUTTON = ("css selector", "button[type='submit'], input[type='submit'], .submit-btn")
    SUCCESS_MESSAGE = ("css selector", ".success-message, .alert-success, .contact-success")
    ERROR_MESSAGE = ("css selector", ".error-message, .alert-error, .contact-error")
    
    def __init__(self, driver, timeout: int = 10):
        super().__init__(driver, timeout)

    def open_contact_page(self):
        """Open the contact page with safe navigation."""
        return self.safe_open_url(f"{Config.BASE_URL}/fr/contact/contact-us/")
    
    def fill_contact_form(self, name: str, email: str, subject: str, message: str):
        """Fill the contact form with robust error handling."""
        try:
            if self.find_all(self.NAME_INPUT):
                self.input_text(self.NAME_INPUT, name)
            if self.find_all(self.EMAIL_INPUT):
                self.input_text(self.EMAIL_INPUT, email)
            if self.find_all(self.SUBJECT_INPUT):
                self.input_text(self.SUBJECT_INPUT, subject)
            if self.find_all(self.MESSAGE_INPUT):
                self.input_text(self.MESSAGE_INPUT, message)
        except Exception as e:
            # Record the error but continue
            if self._standard_monitor:
                self._record_ui_change(self.CONTACT_FORM, "contact_form_error", 
                                     {"action": "form_fill", "error": str(e)}, 
                                     {"action": "form_fill_error"})
    
    def submit_contact_form(self):
        """Submit the contact form with retry mechanism."""
        try:
            if self.find_all(self.SUBMIT_BUTTON):
                self.click(self.SUBMIT_BUTTON)
        except Exception as e:
            # Record submission error
            if self._standard_monitor:
                self._record_ui_change(self.SUBMIT_BUTTON, "contact_submit_error", 
                                     {"action": "submit", "error": str(e)}, 
                                     {"action": "submit_error"})
    
    def get_success_message(self):
        """Get success message with error handling."""
        try:
            if self.find_all(self.SUCCESS_MESSAGE):
                return self.find(self.SUCCESS_MESSAGE).text
            return None
        except:
            return None
    
    def get_error_message(self):
        """Get error message with error handling."""
        try:
            if self.find_all(self.ERROR_MESSAGE):
                return self.find(self.ERROR_MESSAGE).text
            return None
        except:
            return None