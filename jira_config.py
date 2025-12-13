# Jira Configuration
# To use the Jira automation, set these environment variables:

# JIRA_URL=https://yourcompany.atlassian.net
# JIRA_USERNAME=your-email@example.com
# JIRA_API_TOKEN=your-api-token
# JIRA_PROJECT_KEY=PROJ

# Example configuration file (rename to .env or set as environment variables)
import os

# Configuration from environment variables (primary) or config file (fallback)
JIRA_URL = os.getenv("JIRA_URL", "https://yourcompany.atlassian.net")
JIRA_USERNAME = os.getenv("JIRA_USERNAME", "your-email@example.com")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "your-api-token")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "PROJ")