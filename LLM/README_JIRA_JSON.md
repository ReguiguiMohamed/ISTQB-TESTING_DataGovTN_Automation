# Jira Ticket Automation & JSON Test Case Generation

This enhancement adds two major features to the LLM-powered test case generator:

## 1. JSON Output Format

The web application now generates test cases in structured JSON format in addition to the markdown table format. This provides:

- **Structured Data**: Easy to parse and integrate with other tools
- **Dual Format**: Both human-readable markdown table and machine-readable JSON
- **Improved Parsing**: Better extraction and validation of test case components

### JSON Structure:
```json
[
  {
    "id": "TC001",
    "title": "Verify search with valid keyword",
    "type": "positif",
    "preconditions": ["User is on homepage", "Search bar is visible"],
    "input_data": ["education"],
    "steps": [
      "Enter 'education' in search bar",
      "Click search button",
      "Verify results are displayed"
    ],
    "expected_result": "Search results page with education-related datasets is displayed"
  }
]
```

## 2. Jira Ticket Automation

Automatically create Jira tickets for:
- Test failures from pytest reports
- LLM-generated test cases from the web interface

### Features:
- Creates tickets for failed tests from HTML reports
- Bulk creates tickets from JSON test case data
- Supports both Bug (for failures) and Task (for test cases) issue types
- Proper formatting with Jira markup language
- Configurable via environment variables

## Setup

### Jira Configuration:
Set these environment variables:
```bash
export JIRA_URL=https://yourcompany.atlassian.net
export JIRA_USERNAME=your-email@example.com
export JIRA_API_TOKEN=your-api-token
export JIRA_PROJECT_KEY=PROJ
```

### Install Dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Web Interface:
1. Start the web app: `cd LLM && python web_app.py`
2. Open browser to `http://localhost:5000`
3. Select model, enter API key, add user story and acceptance criteria
4. Click "Générer les cas de test"
5. View results in both Markdown and JSON formats
6. Use "Télécharger JSON" to get structured test cases
7. Use "Créer Tickets Jira" to create tickets (requires configuration)

### Jira Automation Scripts:
```bash
# Process test failures from pytest report
python jira_automation_enhanced.py
# Then select option 1

# Process LLM-generated test cases
python jira_automation_enhanced.py
# Then select option 2
```

## Files Added/Modified:

- `jira_automation.py` - Basic Jira integration
- `jira_automation_enhanced.py` - Enhanced version with JSON support
- `jira_config.py` - Configuration template
- `LLM/web_app.py` - Updated to support JSON output
- `LLM/templates/index.html` - Updated UI with JSON functionality
- `LLM/prompt_template.txt` - Updated to generate JSON format
- `requirements.txt` - Added requests library

## Benefits:

1. **Better Integration**: JSON format enables easy integration with other tools
2. **Automated Tracking**: Failed tests are automatically tracked in Jira
3. **Efficient Management**: LLM-generated test cases can be directly imported into Jira
4. **Dual Format**: Maintains human-readable markdown for reporting while enabling automation
5. **Flexible Workflow**: Supports both manual and automated test case management

The system maintains backward compatibility while adding powerful automation capabilities for test case management and failure tracking.