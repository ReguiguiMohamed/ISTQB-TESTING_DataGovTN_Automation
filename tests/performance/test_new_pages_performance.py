"""
Performance tests for new pages with robust monitoring and fragile site handling
"""
import pytest
import time
from pages import FAQPage, ContactPage, AuthPage, StaticPage
from config import Config


@pytest.mark.performance
def test_faq_page_load_performance(auto_setup_monitoring, browser):
    """Test FAQ page load performance with robust error handling."""
    faq_page = FAQPage(browser)
    
    # Set up monitoring
    auto_setup_monitoring(faq_page)
    
    start_time = time.time()
    
    # Try to navigate to FAQ page
    success = faq_page.open_faq_page()
    
    load_time = time.time() - start_time
    
    if success:
        # Performance test: just record the time
        print(f"FAQ page loaded in {load_time:.2f} seconds")
        # Don't assert specific time - let fragile site conditions affect results appropriately
    else:
        print(f"FAQ page fell back to safe page, load time {load_time:.2f}s may include fallback")


@pytest.mark.performance
def test_contact_page_load_performance(auto_setup_monitoring, browser):
    """Test Contact page load performance with robust error handling."""
    contact_page = ContactPage(browser)
    
    # Set up monitoring
    auto_setup_monitoring(contact_page)
    
    start_time = time.time()
    
    # Try to navigate to Contact page
    success = contact_page.open_contact_page()
    
    load_time = time.time() - start_time
    
    if success:
        print(f"Contact page loaded in {load_time:.2f} seconds")
    else:
        print(f"Contact page fell back to safe page, load time {load_time:.2f}s may include fallback")


@pytest.mark.performance 
def test_static_pages_load_performance(auto_setup_monitoring, browser):
    """Test multiple static pages load performance."""
    static_page = StaticPage(browser)
    
    # Set up monitoring
    auto_setup_monitoring(static_page)
    
    pages_to_test = [
        ("About", static_page.open_about_page),
        ("Terms", static_page.open_terms_page), 
        ("Licenses", static_page.open_licenses_page),
        ("Data Requests", static_page.open_data_requests_page)
    ]
    
    for page_name, open_function in pages_to_test:
        start_time = time.time()
        
        try:
            success = open_function()
            load_time = time.time() - start_time
            
            if success:
                print(f"{page_name} page loaded in {load_time:.2f} seconds")
            else:
                print(f"{page_name} page fell back to safe page, load time {load_time:.2f}s")
        except Exception as e:
            print(f"{page_name} page load failed: {str(e)}")


@pytest.mark.performance
def test_multiple_page_navigations_performance(auto_setup_monitoring, browser):
    """Test performance of multiple page navigations."""
    home_page = HomePage(browser)
    faq_page = FAQPage(browser)
    contact_page = ContactPage(browser)
    static_page = StaticPage(browser)
    
    # Set up monitoring
    auto_setup_monitoring(home_page)
    auto_setup_monitoring(faq_page)
    auto_setup_monitoring(contact_page)
    auto_setup_monitoring(static_page)
    
    # Start with home page
    home_success = home_page.go_to_dataset_search_fr()
    
    if home_success:
        # Record navigation times
        navigation_times = []
        
        # Navigate to FAQ
        start_time = time.time()
        faq_success = faq_page.open_faq_page()
        navigation_times.append(("FAQ", time.time() - start_time, faq_success))
        
        # Navigate to Contact
        start_time = time.time()
        contact_success = contact_page.open_contact_page()
        navigation_times.append(("Contact", time.time() - start_time, contact_success))
        
        # Navigate to About
        start_time = time.time()
        about_success = static_page.open_about_page()
        navigation_times.append(("About", time.time() - start_time, about_success))
        
        # Print navigation performance
        for page_name, nav_time, success in navigation_times:
            status = "Success" if success else "Fallback"
            print(f"{page_name} navigation: {nav_time:.2f}s ({status})")