# ISTQB-TESTING_DataGovTN_Automation

ISTQB Foundation Level software testing project using Python and Selenium to implement Black-Box, Non-Functional, and Load testing on the Tunisian National Open Data Portal (data.gov.tn).

## Docker Setup for Cross-Browser Testing

This project includes a Docker-based Selenium Grid setup for reliable cross-browser testing. This ensures consistent test execution across different browsers without requiring local browser driver installations.

**Note**: Safari testing is only available on macOS and is not supported in Docker containers.

### Quick Start with Docker

1. **Start the Selenium Grid:**
   ```bash
   docker-compose up -d
   ```

2. **Run cross-browser tests:**
   ```bash
   pytest tests/cross_browser/test_smoke_cross_browser.py --remote --browser=chrome
   pytest tests/cross_browser/test_smoke_cross_browser.py --remote --browser=firefox
   pytest tests/cross_browser/test_smoke_cross_browser.py --remote --browser=edge
   ```

3. **Stop the grid when done:**
   ```bash
   docker-compose down
   ```

For detailed instructions, see [docs/docker-setup.md](docs/docker-setup.md).

## Running Tests

### Local Execution (traditional method)
```bash
pytest tests/functional/test_search_basic.py --browser=chrome
```

### Cross-Browser Execution (with Docker)
```bash
# Run on Chrome via Docker
pytest tests/cross_browser/test_smoke_cross_browser.py --remote --browser=chrome

# Run on all supported browsers in parallel (Chrome, Firefox, Edge)
pytest tests/cross_browser/test_smoke_cross_browser.py --remote --browser=chrome --browser=firefox --browser=edge
```

### Safari Testing (macOS only)
```bash
# Safari testing is only possible on macOS with local execution
pytest tests/cross_browser/test_smoke_cross_browser.py --browser=safari
```

## Requirements

- Python 3.8+
- Docker Desktop
- Docker Compose
- Note: Safari requires macOS for local execution
