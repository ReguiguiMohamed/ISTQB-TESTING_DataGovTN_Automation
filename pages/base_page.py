from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

class BasePage:
    """Base class for all Page Objects containing common methods."""

    def __init__(self, driver: WebDriver, timeout: int = 10):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout, ignored_exceptions=[StaleElementReferenceException])

    def open_url(self, url: str):
        """Navigates to the specified URL."""
        self.driver.get(url)

    def find(self, locator: tuple):
        """Finds a visible element."""
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_all(self, locator: tuple):
        """Finds all present elements (visible or not)."""
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def click(self, locator: tuple):
        """Clicks on a clickable element."""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def input_text(self, locator: tuple, text: str):
        """Sends text to an element."""
        element = self.find(locator)
        element.clear()
        element.send_keys(text)

    def get_title(self) -> str:
        """Returns the page title."""
        return self.driver.title

    def get_current_url(self) -> str:
        """Returns the current URL."""
        return self.driver.current_url