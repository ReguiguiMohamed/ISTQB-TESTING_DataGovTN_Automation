"""
Corrected test_ui_monitoring_demo with proper method calls and imports
"""
import pytest
from selenium.webdriver.common.by import By

def test_ui_monitoring_direct_usage(browser, ui_monitor):
    """
    Test to verify the UI Monitor utility works in isolation.
    """
    # Navigate to a simple page that should always work to avoid timeouts
    browser.get("about:blank")

    # 1. Monitor a non-existent element (Should log a failure, not crash)
    # Note: Use a valid strategy like By.CSS_SELECTOR
    print("\n--- Testing Non-Existent Element ---")
    result = ui_monitor.monitor_element_disappearance((By.CSS_SELECTOR, ".non-existent-element"))
    print(f"Result (should be True/False based on timeout): {result['success']}")

    # 2. Monitor loading indicators directly via the UTILITY
    # (Use monitor_loading_states, NOT wait_for_loading_indicators_to_disappear)
    print("\n--- Testing Loading States ---")
    results = ui_monitor.monitor_loading_states()
    print(f"Monitor Report: {results}")

    # Verify we got a dictionary back
    assert isinstance(results, dict)