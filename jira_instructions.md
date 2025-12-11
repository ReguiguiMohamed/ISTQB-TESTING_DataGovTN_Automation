# How to Use the Improved Jira Automation Script

The `jira_automation_enhanced.py` script has been improved to be more robust, secure, and easier to integrate into your CI/CD pipeline.

## Configuration

The script is now configured entirely through environment variables. This means you no longer need to edit any Python files to set it up.

### 1. Jira Credentials and Project Info

You must provide your Jira URL, username, API token, and project key using environment variables.

**On Windows (Command Prompt):**
```bash
setx JIRA_URL "https://yourcompany.atlassian.net"
setx JIRA_USERNAME "your-email@example.com"
setx JIRA_API_TOKEN "your-api-token"
setx JIRA_PROJECT_KEY "PROJ"
```

**On Linux/macOS:**
```bash
export JIRA_URL="https://yourcompany.atlassian.net"
export JIRA_USERNAME="your-email@example.com"
export JIRA_API_TOKEN="your-api-token"
export JIRA_PROJECT_KEY="PROJ"
```
*(Note: For a permanent setup on Linux/macOS, add these `export` commands to your `~/.bashrc` or `~/.zshrc` file and restart your shell.)*

### 2. Custom Fields for Priority and Severity

If your Jira project uses custom fields for "Priority" and "Severity," you can specify their IDs using environment variables.

**How to find your Custom Field IDs:**
1.  Go to your Jira instance.
2.  Navigate to `https://<your-domain>.atlassian.net/rest/api/2/field`.
3.  Search for the fields named "Severity" and "Priority" and note their `id` (e.g., `customfield_10037`).

**On Windows (Command Prompt):**
```bash
setx JIRA_CUSTOM_FIELD_PRIORITY "customfield_10038"
setx JIRA_CUSTOM_FIELD_SEVERITY "customfield_10037"
```

**On Linux/macOS:**
```bash
export JIRA_CUSTOM_FIELD_PRIORITY="customfield_10038"
export JIRA_CUSTOM_FIELD_SEVERITY="customfield_10037"
```

## How to Use the Script

The script is now non-interactive and can be run with command-line arguments, making it suitable for automation pipelines.

*   **To create tickets from a test report:**
    ```bash
    python jira_automation_enhanced.py --report-path "reports/report.html"
    ```

*   **To create tickets from a JSON file of LLM-generated test cases:**
    ```bash
    python jira_automation_enhanced.py --json-path "path/to/your/test-cases.json"
    ```

*   **To process both a report and a JSON file at the same time:**
    ```bash
    python jira_automation_enhanced.py --all --report-path "reports/report.html" --json-path "path/to/your/test-cases.json"
    ```

## Improved Jira Ticket Structure

The generated Jira tickets now have a more professional and readable structure:

*   **For Bug Reports:** The description includes clear sections for:
    *   Test Details
    *   Error Message (in a formatted code block)
    *   Environment (Browser, Platform)

*   **For Test Cases:** The description is organized with:
    *   Headings for different sections (Test Info, Preconditions, etc.)
    *   Numbered test steps
    *   A visually distinct panel for the expected result

These changes make the tickets easier to understand and act upon.
