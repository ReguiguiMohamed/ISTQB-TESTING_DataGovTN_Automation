"""
Centralized configuration for the test automation framework.
Reads from environment variables with sensible defaults.
"""
import os


class Config:
    # Base URLs
    BASE_URL = os.getenv("BASE_URL", "https://data.gov.tn")
    CATALOG_URL_FR = os.getenv("CATALOG_URL_FR", "https://catalog.data.gov.tn/fr/dataset/")
    CATALOG_URL_AR = os.getenv("CATALOG_URL_AR", "https://catalog.data.gov.tn/ar/dataset/")

    # Grid Configuration
    HUB_HOST = os.getenv("HUB_HOST", "localhost")
    HUB_PORT = os.getenv("HUB_PORT", "4444")
    REMOTE_URL = f"http://{HUB_HOST}:{HUB_PORT}/wd/hub"

    # Timeouts
    IMPLICIT_WAIT = int(os.getenv("IMPLICIT_WAIT", 10))
    EXPLICIT_WAIT = int(os.getenv("EXPLICIT_WAIT", 15))
    PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", 30))

    # Rate limiting and delays for government websites with anti-bot measures
    REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", 2.0))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 2))
    RETRY_DELAY = float(os.getenv("RETRY_DELAY", 1.0))

    # Performance threshold
    PERFORMANCE_THRESHOLD = float(os.getenv("PERFORMANCE_THRESHOLD", 10.0))

    # Browser Defaults
    DEFAULT_BROWSER = "chrome"
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    WINDOW_WIDTH = int(os.getenv("WINDOW_WIDTH", 1920))
    WINDOW_HEIGHT = int(os.getenv("WINDOW_HEIGHT", 1080))
