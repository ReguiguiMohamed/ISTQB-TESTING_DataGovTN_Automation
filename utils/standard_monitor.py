"""
Standardized UI Monitoring System
Provides automatic monitoring for all UI interactions without repeated code
"""

import functools
from typing import Callable, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.ui_monitor import UIStateMonitor
from utils.ui_documentation import UIStateChange, UIDocumentationSystem


class MonitoringDecorator:
    """
    Standardized decorator that automatically monitors UI state changes
    and integrates with the documentation system without repeated code
    """
    
    def __init__(self, ui_monitor: UIStateMonitor, doc_system: UIDocumentationSystem):
        self.ui_monitor = ui_monitor
        self.doc_system = doc_system

    def auto_monitor_interactions(self, element_locator: tuple = None):
        """
        Decorator that automatically monitors before and after UI interactions
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Get the driver from the first argument (self.driver of page object)
                driver = args[0].driver if hasattr(args[0], 'driver') else None
                
                if not driver:
                    return func(*args, **kwargs)  # No monitoring if no driver
                
                # Capture before state if element_locator is provided
                before_state = None
                if element_locator:
                    before_state = self.ui_monitor.capture_element_state(element_locator)
                
                # Execute the original function
                result = func(*args, **kwargs)
                
                # Capture after state if element_locator is provided
                after_state = None
                if element_locator:
                    try:
                        # Wait a bit for changes to occur
                        import time
                        time.sleep(0.5)
                        after_state = self.ui_monitor.capture_element_state(element_locator)
                    except:
                        pass  # It's ok if we can't capture after state
                
                # Create documentation record
                if element_locator and before_state and after_state:
                    change = UIStateChange(
                        timestamp=after_state['timestamp'],
                        element_locator=str(element_locator),
                        event_type="interaction",
                        duration=0.5,  # Approximate
                        initial_state=before_state,
                        final_state=after_state,
                        success=True,
                        test_name=func.__name__,
                        page_url=driver.current_url
                    )
                    self.doc_system.record_change(change)
                
                return result
            return wrapper
        return decorator
    
    def auto_monitor_loading_states(self):
        """
        Decorator that automatically monitors loading indicators disappearing after an action
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                
                # Monitor loading indicators after the action
                if hasattr(args[0], 'driver'):
                    all_disappeared, details = self.ui_monitor.wait_for_loading_indicators_to_disappear()
                    
                    # Record loading state change
                    change = UIStateChange(
                        timestamp=details.get('timestamp', str(func.__name__)),
                        element_locator="Loading Indicators",
                        event_type="loading_disappearance",
                        duration=1.0,  # Approximate
                        initial_state={"loading_visible": not all_disappeared},
                        final_state={"loading_disappeared": all_disappeared},
                        success=all_disappeared,
                        test_name=func.__name__,
                        page_url=args[0].driver.current_url,
                        notes=f"Loading indicators monitoring: {details}"
                    )
                    self.doc_system.record_change(change)
                
                return result
            return wrapper
        return decorator

    def auto_monitor_images(self):
        """
        Decorator that automatically monitors image loading states
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                
                # Look for images that might have loaded after the action
                if hasattr(args[0], 'driver'):
                    driver = args[0].driver
                    img_elements = driver.find_elements(By.TAG_NAME, 'img')
                    
                    for i, img in enumerate(img_elements[:5]):  # Check first 5 images to avoid too many checks
                        try:
                            # Create a locator for the specific image
                            img_locator = (By.XPATH, f"//img[{i+1}]")
                            img_result = self.ui_monitor.monitor_image_loading(img_locator, timeout=2)
                            
                            # Record image loading result
                            change = UIStateChange(
                                timestamp=img_result.get('final_state', {}).get('timestamp', str(func.__name__)),
                                element_locator=str(img_locator),
                                event_type="image_load",
                                duration=2.0,  # Approximate
                                initial_state=img_result.get('initial_state', {}),
                                final_state=img_result.get('final_state', {}),
                                success=img_result.get('image_loaded', False),
                                test_name=func.__name__,
                                page_url=driver.current_url,
                                notes="Real image load verification"
                            )
                            self.doc_system.record_change(change)
                        except Exception:
                            continue  # Skip if image check fails
                
                return result
            return wrapper
        return decorator


def create_standard_monitor(ui_monitor: UIStateMonitor, doc_system: UIDocumentationSystem):
    """
    Create a standardized monitoring instance for use across all page objects
    """
    return MonitoringDecorator(ui_monitor, doc_system)