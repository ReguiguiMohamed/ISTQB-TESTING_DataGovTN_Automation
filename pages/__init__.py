"""
Page Object models for the Data.gov.tn UI tests.

This package exposes all page classes so they can be imported as:

    from pages import HomePage, SearchPage, DatasetPage, FAQPage, ContactPage, AuthPage, StaticPage
"""

from .base_page import BasePage
from .home_page import HomePage
from .search_page import SearchPage
from .dataset_page import DatasetPage
from .faq_page import FAQPage
from .contact_page import ContactPage
from .auth_page import AuthPage
from .static_page import StaticPage

__all__ = ["BasePage", "HomePage", "SearchPage", "DatasetPage", "FAQPage", "ContactPage", "AuthPage", "StaticPage"]
