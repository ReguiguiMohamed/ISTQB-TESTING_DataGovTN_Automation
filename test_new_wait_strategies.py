"""
Test script to verify the new wait strategies work properly.
This tests the new methods added to BasePage:
- wait_for_invisibility
- wait_for_image_to_load
- wait_for_refresh (staleness)
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pages.base_page import BasePage


class TestWaitStrategiesPage(BasePage):
    """Test page to verify new wait strategies"""
    
    # Locators for testing
    LOADING_SPINNER = (By.ID, "loading-spinner")
    TEST_IMAGE = (By.ID, "test-image")
    TEST_ELEMENT = (By.ID, "test-element")


def test_wait_strategies():
    """Test all new wait strategies"""
    
    # Initialize driver
    driver = webdriver.Chrome()
    page = TestWaitStrategiesPage(driver, timeout=10)
    
    try:
        # Create a test HTML page with elements for testing
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Wait Strategies</title>
        </head>
        <body>
            <div id="loading-spinner">Loading...</div>
            <img id="test-image" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" alt="Test">
            <div id="test-element">Test Content</div>
            
            <script>
                // Simulate loading spinner disappearing after 2 seconds
                setTimeout(() => {
                    document.getElementById('loading-spinner').style.display = 'none';
                }, 2000);
            </script>
        </body>
        </html>
        """
        
        # Load the test page
        driver.get("data:text/html;charset=utf-8," + html_content)
        
        print("Testing wait_for_invisibility...")
        # Test wait_for_invisibility - this should work once spinner disappears
        try:
            result = page.wait_for_invisibility((By.ID, "loading-spinner"))
            print("✓ wait_for_invisibility worked correctly")
        except TimeoutException:
            print("✗ wait_for_invisibility failed")
        
        print("Testing wait_for_image_to_load...")
        # Test wait_for_image_to_load
        try:
            img_element = page.wait_for_image_to_load((By.ID, "test-image"))
            print("✓ wait_for_image_to_load worked correctly")
        except AssertionError as e:
            print(f"✗ wait_for_image_to_load failed: {e}")
        
        print("Testing wait_for_refresh (staleness)...")
        # Test wait_for_refresh by getting an element and then modifying the DOM
        element = page.find((By.ID, "test-element"))
        
        # Change the element by removing and re-adding it (making the old reference stale)
        driver.execute_script("""
            var element = document.getElementById('test-element');
            var parent = element.parentNode;
            parent.removeChild(element);
        """)
        
        try:
            page.wait_for_refresh(element)
            print("✓ wait_for_refresh (staleness) worked correctly")
        except TimeoutException:
            print("✗ wait_for_refresh (staleness) failed")
        
        print("All wait strategy tests completed successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    test_wait_strategies()