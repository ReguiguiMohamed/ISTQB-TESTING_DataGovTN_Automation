from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
import logging
import time
from utils.standard_monitor import create_standard_monitor
from config import Config


class BasePage:
    """Base class for all Page Objects containing common methods."""

    def __init__(self, driver: WebDriver, timeout: int = 10):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout, ignored_exceptions=[StaleElementReferenceException])
        # Initialize monitoring if available (will be set up via pytest fixtures)
        self._ui_monitor = None
        self._doc_system = None
        self._standard_monitor = None
        # Rate limiting
        self._last_request_time = 0

    def _rate_limit(self):
        """Enforce rate limiting to avoid being blocked by government websites"""
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time

        if time_since_last_request < Config.REQUEST_DELAY:
            sleep_time = Config.REQUEST_DELAY - time_since_last_request
            time.sleep(sleep_time)

        self._last_request_time = time.time()

        # Additional delay to reduce bot detection - only for sensitive operations
        # Don't apply to every action to avoid excessive delays
        # This is handled separately in sensitive methods like login

    def _retry_with_backoff(self, func, *args, **kwargs):
        """Execute a function with retry logic for handling connection issues"""
        for attempt in range(Config.MAX_RETRIES):
            try:
                self._rate_limit()
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == Config.MAX_RETRIES - 1:  # Last attempt
                    raise e
                time.sleep(Config.RETRY_DELAY)
                # Log retry attempt
                logging.info(f"Retry attempt {attempt + 1}/{Config.MAX_RETRIES} for {func.__name__}")
        return None

    def open_url(self, url: str):
        """Navigates to the specified URL with rate limiting."""
        def _open():
            self.driver.get(url)
        self._retry_with_backoff(_open)

    def find(self, locator: tuple):
        """Finds a visible element with automatic monitoring."""
        def _find():
            element = self.wait.until(EC.visibility_of_element_located(locator))
            # Record the find attempt if monitoring is enabled
            if self._standard_monitor:
                self._record_ui_change(locator, "element_find", {"action": "find"}, {"action": "element_found"})
            return element
        return self._retry_with_backoff(_find)

    def find_all(self, locator: tuple):
        """Finds all present elements (visible or not) with rate limiting."""
        def _find_all():
            return self.wait.until(EC.presence_of_all_elements_located(locator))
        return self._retry_with_backoff(_find_all)

    def click(self, locator: tuple):
        """Clicks on a clickable element with rate limiting and retries."""
        def _click():
            element = self.wait.until(EC.element_to_be_clickable(locator))
            
            # Record the click action if monitoring is enabled
            if self._standard_monitor:
                self._record_ui_change(locator, "click", {"action": "click"}, {"action": "clicked"})
            
            element.click()
            return element
        
        return self._retry_with_backoff(_click)

    def input_text(self, locator: tuple, text: str):
        """Sends text to an element with rate limiting and retries."""
        def _input_text():
            element = self.find(locator)
            
            # Record the text input if monitoring is enabled
            if self._standard_monitor:
                self._record_ui_change(locator, "input_text", 
                                     {"action": "input_text", "text": text}, 
                                     {"action": "text_entered", "text": text})
            
            element.clear()
            element.send_keys(text)
            return element
        
        return self._retry_with_backoff(_input_text)

    def get_title(self) -> str:
        """Returns the page title."""
        return self.driver.title

    def get_current_url(self) -> str:
        """Returns the current URL."""
        return self.driver.current_url

    def safe_open_url(self, url: str, fallback_url: str = "about:blank"):
        """
        Safely opens a URL with retry mechanism and fallback for fragile websites.
        Returns True if successful, False if fallback was used.
        """
        try:
            def _open_url():
                self.driver.get(url)
            self._retry_with_backoff(_open_url)
            return True
        except Exception as e:
            # Log the error and try fallback
            logging.warning(f"Failed to open {url}: {str(e)}, trying fallback {fallback_url}")
            try:
                self.driver.get(fallback_url)
                return False  # Indicates fallback was used
            except:
                raise e  # If fallback also fails, raise original error
    
    def safe_navigate(self, navigation_func, fallback_url: str = "about:blank"):
        """
        Safely executes a navigation function with retry and fallback.
        navigation_func should be a callable that performs the navigation.
        """
        try:
            def _navigate():
                return navigation_func()
            result = self._retry_with_backoff(_navigate)
            return True, result
        except Exception as e:
            logging.warning(f"Navigation failed: {str(e)}, trying fallback {fallback_url}")
            try:
                self.driver.get(fallback_url)
                return False, None  # Indicates fallback was used
            except:
                raise e  # If fallback also fails, raise original error

    def setup_monitoring(self, ui_monitor=None, doc_system=None):
        """Set up automatic monitoring for this page object"""
        self._ui_monitor = ui_monitor
        self._doc_system = doc_system
        if ui_monitor and doc_system:
            self._standard_monitor = create_standard_monitor(ui_monitor, doc_system)

    def _record_ui_change(self, element_locator: tuple, event_type: str, initial_state: dict = None, final_state: dict = None):
        """Helper method to record UI state changes when monitoring is enabled"""
        if self._doc_system:
            from utils.ui_documentation import UIStateChange
            import datetime
            change = UIStateChange(
                timestamp=datetime.datetime.now().isoformat(),
                element_locator=str(element_locator),
                event_type=event_type,
                duration=0.0,  # Will be calculated properly in future enhancements
                initial_state=initial_state or {"action": event_type},
                final_state=final_state or {"action": f"completed_{event_type}"},
                success=True,
                test_name="unknown_test",  # This should be passed from test context in future
                page_url=self.driver.current_url
            )
            self._doc_system.record_change(change)

    def wait_for_invisibility(self, locator: tuple) -> bool:
        """
        Waits for an element to disappear from the DOM or become invisible.
        Returns True if successful, raises TimeoutException if it stays visible.
        """
        return self.wait.until(EC.invisibility_of_element_located(locator))

    def wait_for_image_to_load(self, locator: tuple):
        """
        Waits for an image to be visible AND fully loaded (naturalWidth > 0).
        """
        # 1. Wait for the element to be present and visible in the DOM
        element = self.wait.until(EC.visibility_of_element_located(locator))

        # 2. Use JavaScript to check if the image binary actually loaded
        is_loaded = self.driver.execute_script(
            "return arguments[0].complete && " +
            "typeof arguments[0].naturalWidth != 'undefined' && " +
            "arguments[0].naturalWidth > 0", element)

        if not is_loaded:
            raise AssertionError(f"Image located by {locator} is visible but failed to load (broken image).")
        
        return element

    def wait_for_refresh(self, element):
        """
        Waits for a specific element reference to become stale (detached from DOM).
        Useful when waiting for a page refresh or list update to start.
        """
        self.wait.until(EC.staleness_of(element))

    def find_and_monitor(self, locator: tuple, monitor_ui_changes: bool = True):
        """
        Finds a visible element and optionally monitors UI changes around it
        """
        if monitor_ui_changes:
            from utils.ui_monitor import UIStateMonitor
            monitor = UIStateMonitor(self.driver)
            # Monitor the element's appearance
            return monitor.monitor_element_appearance(locator)['final_state']
        else:
            return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_for_invisibility_with_monitoring(self, locator: tuple):
        """
        Waits for element to disappear with full UI change monitoring
        """
        from utils.ui_monitor import UIStateMonitor
        monitor = UIStateMonitor(self.driver)
        result = monitor.monitor_element_disappearance(locator)
        
        # Log the UI change for documentation
        if result['disappeared']:
            logging.info(f"Element {locator} successfully disappeared - {result['duration_seconds']:.2f}s")
        else:
            logging.warning(f"Element {locator} did not disappear - {result['reason']}")
        
        return result['success']

    def wait_for_loading_indicators_to_disappear(self):
        """
        Monitor and wait for common loading indicators to disappear
        """
        from utils.ui_monitor import UIStateMonitor
        monitor = UIStateMonitor(self.driver)
        results = monitor.monitor_loading_states()
        
        # Check if all loading indicators have disappeared
        all_disappeared = all(
            result.get('disappeared', result.get('appearance', {}).get('disappeared', True)) 
            for result in results.values() 
            if isinstance(result, dict) and 'error' not in result
        )
        
        return all_disappeared, results