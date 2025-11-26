"""
UI State Monitoring Utility
Captures and documents UI state changes, especially elements appearing/disappearing
"""

import time
import logging
from contextlib import contextmanager
from datetime import datetime
from typing import List, Tuple, Dict, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import Config


class UIStateMonitor:
    """
    Monitors and documents UI state changes including elements appearing/disappearing
    """

    def __init__(self, driver: WebDriver, log_file: str = None):
        self.driver = driver
        self.log_file = log_file or f"ui_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        # Store the current implicit wait value
        self.original_implicit_wait = 0  # Since we've already set it to 0 in conftest.py
        self.setup_logging()
        
    @contextmanager
    def _no_implicit_wait(self):
        """Temporarily disable implicit wait for instant checks"""
        # Get the current implicit wait time
        original_wait = self.driver.timeouts.implicit_wait
        self.driver.implicitly_wait(0)
        try:
            yield
        finally:
            # Restore original wait time
            self.driver.implicitly_wait(original_wait)

    def _get_implicit_wait(self):
        """Get current implicit wait time"""
        return self.driver.timeouts.implicit_wait

    def setup_logging(self):
        """Setup logging configuration for UI state changes"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()  # Also print to console
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def capture_element_state(self, locator: Tuple[By, str]) -> Dict:
        """Capture the current state of an element with zero implicit wait for performance"""
        # Use context manager to temporarily disable implicit wait for instant checks
        with self._no_implicit_wait():
            elements = self.driver.find_elements(*locator)
            if elements:
                element = elements[0]
                return {
                    'exists': True,
                    'is_displayed': element.is_displayed(),
                    'is_enabled': element.is_enabled(),
                    'text': element.text[:100],  # Limit text length
                    'tag_name': element.tag_name,
                    'class': element.get_attribute('class') or '',
                    'id': element.get_attribute('id') or '',
                    'timestamp': datetime.now().isoformat(),
                    'screenshot': None  # Will be added if needed
                }
        # If we exit the context manager, it means elements is empty
        return {
            'exists': False,
            'is_displayed': False,
            'is_enabled': False,
            'text': '',
            'tag_name': None,
            'class': '',
            'id': '',
            'timestamp': datetime.now().isoformat(),
            'screenshot': None
        }
    
    def monitor_element_disappearance(self, locator: Tuple[By, str], timeout: int = 10) -> Dict:
        """Monitor an element's disappearance and document the state change"""
        initial_state = self.capture_element_state(locator)
        
        self.logger.info(f"Monitoring element disappearance: {locator}")
        self.logger.info(f"Initial state - Exists: {initial_state['exists']}, Displayed: {initial_state['is_displayed']}")
        
        try:
            # Wait for element to become invisible
            result = WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(locator)
            )
            
            final_state = self.capture_element_state(locator)
            duration = (datetime.fromisoformat(final_state['timestamp']) - 
                       datetime.fromisoformat(initial_state['timestamp'])).total_seconds()
            
            self.logger.info(f"Element disappeared successfully after {duration:.2f}s")
            
            return {
                'success': True,
                'initial_state': initial_state,
                'final_state': final_state,
                'duration_seconds': duration,
                'disappeared': True,
                'reason': 'Element became invisible as expected'
            }
        except TimeoutException:
            final_state = self.capture_element_state(locator)
            self.logger.warning(f"Element did not disappear within {timeout}s timeout")
            
            return {
                'success': False,
                'initial_state': initial_state,
                'final_state': final_state,
                'duration_seconds': timeout,
                'disappeared': False,
                'reason': f'Element did not disappear within {timeout}s'
            }
    
    def monitor_element_appearance(self, locator: Tuple[By, str], timeout: int = 10) -> Dict:
        """Monitor an element's appearance and document the state change"""
        initial_state = self.capture_element_state(locator)
        
        self.logger.info(f"Monitoring element appearance: {locator}")
        self.logger.info(f"Initial state - Exists: {initial_state['exists']}, Displayed: {initial_state['is_displayed']}")
        
        try:
            # Wait for element to become visible
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            
            final_state = self.capture_element_state(locator)
            duration = (datetime.fromisoformat(final_state['timestamp']) - 
                       datetime.fromisoformat(initial_state['timestamp'])).total_seconds()
            
            self.logger.info(f"Element appeared successfully after {duration:.2f}s")
            
            return {
                'success': True,
                'initial_state': initial_state,
                'final_state': final_state,
                'duration_seconds': duration,
                'appeared': True,
                'reason': 'Element became visible as expected'
            }
        except TimeoutException:
            final_state = self.capture_element_state(locator)
            self.logger.warning(f"Element did not appear within {timeout}s timeout")
            
            return {
                'success': False,
                'initial_state': initial_state,
                'final_state': final_state,
                'duration_seconds': timeout,
                'appeared': False,
                'reason': f'Element did not appear within {timeout}s'
            }
    
    def monitor_loading_states(self, loading_indicators: List[Tuple[By, str]] = None) -> Dict:
        """Monitor common loading indicators and document their behavior"""
        if loading_indicators is None:
            # Common loading indicators across websites
            loading_indicators = [
                (By.CSS_SELECTOR, ".loading"),
                (By.CSS_SELECTOR, ".spinner"),
                (By.CSS_SELECTOR, ".loading-spinner"),
                (By.CSS_SELECTOR, ".progress"),
                (By.CSS_SELECTOR, "[data-loading='true']"),
                (By.CSS_SELECTOR, ".wait"),
                (By.CSS_SELECTOR, ".in-progress"),
                (By.CSS_SELECTOR, ".processing")
            ]

        monitor_results = {}

        for locator in loading_indicators:
            try:
                # Use the context manager to avoid the "zombie loop" - check with zero implicit wait
                initial_state = self.capture_element_state(locator)

                if initial_state['exists'] and initial_state['is_displayed']:
                    # Element is initially visible, monitor its disappearance
                    result = self.monitor_element_disappearance(locator)
                    monitor_results[str(locator)] = result
                else:
                    # Element is not initially visible, monitor for appearance then disappearance
                    # (in case it appears during monitoring)
                    result = self.monitor_element_appearance(locator)
                    if result['appeared']:
                        disappear_result = self.monitor_element_disappearance(locator)
                        monitor_results[str(locator)] = {
                            'appearance': result,
                            'disappearance': disappear_result
                        }
                    else:
                        monitor_results[str(locator)] = result
            except Exception as e:
                self.logger.error(f"Error monitoring {locator}: {str(e)}")
                monitor_results[str(locator)] = {
                    'error': str(e),
                    'locator': str(locator)
                }

        return monitor_results

    def monitor_image_loading(self, locator: Tuple[By, str], timeout: int = 10):
        """
        Monitors if an image is visible AND actually rendered (naturalWidth > 0).
        """
        initial_state = self.capture_element_state(locator)

        try:
            # 1. Wait for standard visibility
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )

            # 2. Wait for JS confirmation of image data
            is_loaded = WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script(
                    "return arguments[0].complete && " +
                    "typeof arguments[0].naturalWidth != 'undefined' && " +
                    "arguments[0].naturalWidth > 0", element)
            )

            final_state = self.capture_element_state(locator)

            return {
                'success': True,
                'initial_state': initial_state,
                'final_state': final_state,
                'image_loaded': True
            }
        except TimeoutException:
            return {
                'success': False,
                'initial_state': initial_state,
                'reason': "Image visible but failed to render (broken link)"
            }

    def _take_screenshot(self, name_prefix: str) -> str:
        """Helper to take a screenshot and return the path"""
        import os
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
        filename = f"reports/screenshots/{name_prefix}_{timestamp}.png"

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        self.driver.save_screenshot(filename)
        return filename

    def document_ui_changes(self, action_description: str, before_screenshot: str = None, after_screenshot: str = None):
        """Document a UI change with before/after state, automatically taking screenshots if needed"""
        if before_screenshot is True:  # User passed True to request a before screenshot
            before_screenshot = self._take_screenshot("before_ui_change")

        if after_screenshot is True:  # User passed True to request an after screenshot
            after_screenshot = self._take_screenshot("after_ui_change")

        self.logger.info(f"--- UI Change Documentation: {action_description} ---")
        if before_screenshot:
            self.logger.info(f"Before screenshot: {before_screenshot}")
        if after_screenshot:
            self.logger.info(f"After screenshot: {after_screenshot}")
        self.logger.info("--- End UI Change Documentation ---")


# Example usage
if __name__ == "__main__":
    # This would be used in your tests
    print("UI Monitor utility created successfully")
    print("To use in tests, import UIStateMonitor and use it like:")
    print("monitor = UIStateMonitor(driver)")
    print("result = monitor.monitor_element_disappearance((By.CSS_SELECTOR, '.loading-spinner'))")
    print("print(f'Element disappeared: {result[\"disappeared\"]}')")