"""
Authentication Page Object - Robust implementation with rate limiting and monitoring
"""
from pages.base_page import BasePage
from config import Config


class AuthPage(BasePage):
    """Page object for Authentication (Login/Signup) pages with robust navigation and monitoring."""
    
    # Locators
    LOGIN_FORM = ("css selector", ".login-form, form[action*='login'], #login-form")
    LOGIN_INPUT = ("css selector", "input[name='login'], input[name='username'], input[name='email'], #login, #email")
    PASSWORD_INPUT = ("css selector", "input[name='password'], #password, input[type='password']")
    LOGIN_BUTTON = ("css selector", "button[type='submit'], input[type='submit'], .login-btn, .submit-btn")
    ERROR_MESSAGE = ("css selector", ".error-message, .alert-error, .login-error, .auth-error")
    SUCCESS_MESSAGE = ("css selector", ".success-message, .alert-success, .login-success")
    
    # Additional auth elements
    FORGOT_PASSWORD = ("css selector", ".forgot-password, a[href*='password-reset'], a[href*='reset']")
    REGISTER_LINK = ("css selector", ".register-link, a[href*='register'], a[href*='signup']")
    
    def __init__(self, driver, timeout: int = 10):
        super().__init__(driver, timeout)

    def open_login_page(self):
        """Open the login page with safe navigation."""
        return self.safe_open_url(f"{Config.BASE_URL}/fr/auth/login/")
    
    def login(self, username: str, password: str):
        """Perform login with robust error handling."""
        try:
            # Find and fill login field
            if self.find_all(self.LOGIN_INPUT):
                self.input_text(self.LOGIN_INPUT, username)
            
            # Find and fill password field
            if self.find_all(self.PASSWORD_INPUT):
                self.input_text(self.PASSWORD_INPUT, password)
            
            # Submit the form
            if self.find_all(self.LOGIN_BUTTON):
                self.click(self.LOGIN_BUTTON)
                
        except Exception as e:
            # Record login error
            if self._standard_monitor:
                self._record_ui_change(self.LOGIN_FORM, "login_error", 
                                     {"action": "login", "username": username, "error": str(e)}, 
                                     {"action": "login_error"})
    
    def get_error_message(self):
        """Get any error message with error handling."""
        try:
            if self.find_all(self.ERROR_MESSAGE):
                return self.find(self.ERROR_MESSAGE).text
            return None
        except:
            return None
    
    def get_success_message(self):
        """Get any success message with error handling."""
        try:
            if self.find_all(self.SUCCESS_MESSAGE):
                return self.find(self.SUCCESS_MESSAGE).text
            return None
        except:
            return None
    
    def is_logged_in(self):
        """Check if user appears to be logged in with error handling."""
        current_url = self.get_current_url()
        # Check if URL changed to a dashboard/user area or if logout button appears
        return any(s in current_url for s in ['dashboard', 'account', 'profil', 'user']) or \
               len(self.driver.find_elements(*self.LOGIN_BUTTON)) == 0