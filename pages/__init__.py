"""
Page Object models for the Data.gov.tn UI tests.

This package exposes the main page classes so they can be imported as:

    from pages import HomePage, SearchPage, DatasetPage
"""

from .home_page import HomePage
from .search_page import SearchPage
from .dataset_page import DatasetPage

__all__ = ["HomePage", "SearchPage", "DatasetPage"]
