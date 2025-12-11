"""
Enhanced Jira ticket automation for test failures and LLM-generated test cases
Works with both pytest reports and JSON test case data
"""
import json
import re
import os
import requests
from datetime import datetime
from typing import Dict, List, Optional, Union
from pathlib import Path
import sys
from jira import JIRA

class JiraTicketCreator:
    def __init__(self, jira_url: str, username: str, api_token: str, project_key: str):
        """
        Initialize Jira ticket creator

        Args:
            jira_url: Base URL of your Jira instance (e.g., https://yourcompany.atlassian.net)
            username: Your Jira username or email
            api_token: Jira API token
            project_key: Project key where tickets should be created (e.g., 'PROJ')
        """
        self.jira_url = jira_url
        self.auth = (username, api_token)
        self.project_key = project_key

        # Connect to Jira using the official client
        self.jira = JIRA(server=jira_url, basic_auth=self.auth)

        # Discover custom fields
        self.custom_fields = self._discover_custom_fields()

    def _discover_custom_fields(self):
        """Discover custom fields in the project"""
        try:
            # Get all fields first to identify custom ones
            all_jira_fields = self.jira.fields()
            custom_fields = {}

            # Look for custom fields that match our requirements
            for field in all_jira_fields:
                field_id = field['id']
                field_name = field['name'].lower()

                if 'severity' in field_name:
                    custom_fields['severity'] = field_id
                elif 'priority' in field_name and 'custom' in field_name:
                    custom_fields['custom_priority'] = field_id

            # If the project has existing issues, we can double-check the actual field IDs
            try:
                issues = self.jira.search_issues(f"project={self.project_key}", maxResults=1)
                if issues:
                    sample_issue = issues[0]
                    all_fields = sample_issue.raw['fields']
                    for field_id in all_fields.keys():
                        if field_id.startswith('customfield_'):
                            # Get field name via field metadata
                            try:
                                field_meta = self.jira.field(field_id)
                                field_name = field_meta['name'].lower()
                                if 'severity' in field_name:
                                    custom_fields['severity'] = field_id
                                elif 'priority' in field_name and 'custom' in field_name:
                                    custom_fields['custom_priority'] = field_id
                            except:
                                # If the field info can't be retrieved, skip it
                                pass
            except:
                pass

            return custom_fields
        except Exception as e:
            print(f"Error discovering custom fields: {e}")
            return {}

    def parse_test_report(self, report_path: str) -> List[Dict]:
        """
        Parse pytest HTML report to extract failed tests
        
        Args:
            report_path: Path to the HTML test report
            
        Returns:
            List of failure dictionaries
        """
        failures = []
        
        if not os.path.exists(report_path):
            print(f"Report file not found: {report_path}")
            return failures
            
        # Read the HTML report
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple regex pattern to extract failure information
        # This pattern looks for failed test entries in the HTML report
        failure_pattern = r'<tr class="failed".*?</tr>'
        failure_blocks = re.findall(failure_pattern, content, re.DOTALL)
        
        for block in failure_blocks:
            # Extract test name
            name_match = re.search(r'<td class="col-result">(.*?)</td>', block)
            if name_match:
                test_name = name_match.group(1).strip()
                
                # Extract error message
                error_match = re.search(r'<div class="log".*?>(.*?)</div>', block, re.DOTALL)
                error_msg = error_match.group(1).strip() if error_match else "No error details"
                
                failures.append({
                    'test_name': test_name,
                    'error': error_msg,
                    'timestamp': datetime.now().isoformat()
                })
        
        return failures

    def create_jira_ticket(self, summary: str, description: str, issue_type: str = "Bug",
                          labels: List[str] = None, priority: str = "Moyenne", severity: str = "Majeure") -> Optional[Dict]:
        """
        Create a Jira ticket for a test failure or test case

        Args:
            summary: Brief summary of the issue
            description: Detailed description with error information
            issue_type: Type of issue (Bug, Task, Story, etc.)
            labels: List of labels to apply to the ticket
            priority: Priority level (Basse, Moyenne, Haute) - defaults to Moyenne
            severity: Severity level (Triviale, Mineure, Majeure, Critique) - defaults to Majeure

        Returns:
            Created issue data or None if creation failed
        """
        if labels is None:
            labels = ['automated-test', 'qa']

        # Build the fields dictionary
        fields = {
            "project": {"key": self.project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issue_type},
            "labels": labels,
        }

        # Add standard priority for compatibility
        if priority in ["Basse", "Moyenne", "Haute"]:
            # Map French priority terms to standard Jira values
            priority_mapping = {
                "Basse": "Low",
                "Moyenne": "Medium",
                "Haute": "High"
            }
            jira_priority = priority_mapping.get(priority, "Medium")
            fields["priority"] = {"name": jira_priority}
        elif priority:
            fields["priority"] = {"name": priority}

        # Add custom fields if they exist
        if issue_type.lower() == "bug":
            if "custom_priority" in self.custom_fields and priority:
                fields[self.custom_fields["custom_priority"]] = {"value": priority}
            if "severity" in self.custom_fields and severity:
                fields[self.custom_fields["severity"]] = {"value": severity}
        else:
            print(f"Note: Custom Priority/Severity fields not available for issue type '{issue_type}'. Using standard fields only.")

        try:
            # Create the issue using the JIRA client
            new_issue = self.jira.create_issue(fields=fields)
            return {
                'key': new_issue.key,
                'id': new_issue.id,
                'url': f"{self.jira_url}/browse/{new_issue.key}"
            }
        except Exception as e:
            print(f"Error creating Jira ticket: {e}")
            print(f"Fields tried: {list(fields.keys())}")

            # Print the specific error response
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_response = e.response.json()
                    print(f"Jira error details: {error_response}")
                except:
                    print(f"Could not parse Jira error response: {e.response.text}")
            return None

    def _determine_priority_and_severity(self, error_message: str) -> (str, str):
        """
        Determines the priority and severity of a bug based on keywords in the error message.

        Args:
            error_message: The error message from the test failure.

        Returns:
            A tuple containing the priority and severity.
        """
        error_message = error_message.lower()
        
        # Keywords for critical issues
        critical_keywords = ["critical", "crash", "blocker", "fatal", "unhandled exception"]
        if any(keyword in error_message for keyword in critical_keywords):
            return "Haute", "Critique"

        # Keywords for major issues
        major_keywords = ["error", "exception", "fail", "traceback", "assertionerror"]
        if any(keyword in error_message for keyword in major_keywords):
            return "Moyenne", "Majeure"

        # Keywords for minor issues
        minor_keywords = ["warning", "ui", "layout", "element not found", "timeout"]
        if any(keyword in error_message for keyword in minor_keywords):
            return "Basse", "Mineure"

        # Default to medium priority and major severity
        return "Moyenne", "Majeure"

    def create_tickets_for_failures(self, report_path: str) -> List[Dict]:
        """
        Parse test report and create Jira tickets for all failures

        Args:
            report_path: Path to the test report

        Returns:
            List of created ticket information
        """
        failures = self.parse_test_report(report_path)
        created_tickets = []

        for failure in failures:
            summary = f"Test Failure: {failure['test_name']}"
            description = f"""
h2. Automated Test Failure Report

h3. Test Details
*Test Case:* {failure['test_name']}
*Time of Failure:* {failure['timestamp']}

h3. Error Message
{{code:python}}
{failure['error']}
{{code}}

h3. Environment
*Browser:* {os.getenv("BROWSER", "N/A")}
*Platform:* {os.getenv("PLATFORM", "N/A")}

h3. Automation Info
This ticket was automatically generated by the test automation pipeline.
            """.strip()

            # Determine priority and severity based on the failure
            priority, severity = self._determine_priority_and_severity(failure['error'])

            ticket = self.create_jira_ticket(
                summary=summary,
                description=description,
                issue_type="Bug",
                labels=['automated-test-failure', 'qa', 'selenium', 'regression'],
                priority=priority,
                severity=severity
            )

            if ticket:
                created_tickets.append({
                    'test_name': failure['test_name'],
                    'jira_key': ticket['key'],
                    'jira_url': f"{self.jira_url}/browse/{ticket['key']}",
                    'timestamp': failure['timestamp']
                })
                print(f"Created Jira ticket {ticket['key']} for test: {failure['test_name']}")
            else:
                print(f"Failed to create Jira ticket for test: {failure['test_name']}")

        return created_tickets

    def bulk_create_tickets_from_json(self, json_data: Union[List[Dict], str, Path]) -> List[Dict]:
        """
        Create Jira tickets from structured JSON data (for LLM-generated test cases)

        Args:
            json_data: Path to JSON file or list of test case dictionaries

        Returns:
            List of created ticket information
        """
        # Handle both file path and direct data
        if isinstance(json_data, (str, Path)):
            with open(json_data, 'r', encoding='utf-8') as f:
                test_cases = json.load(f)
        else:
            test_cases = json_data

        created_tickets = []

        for test_case in test_cases:
            title = test_case.get('title', 'Unnamed Test Case')
            steps = test_case.get('steps', [])
            expected_result = test_case.get('expected_result', 'Expected result not specified')
            preconditions = test_case.get('preconditions', [])
            input_data = test_case.get('input_data', [])
            test_type = test_case.get('type', 'functional')
            test_id = test_case.get('id', 'N/A')

            summary = f"Test Case: {title}"
            description = f"""
h2. LLM-Generated Test Case

h3. Test Information
*Test ID:* {test_id}
*Test Type:* {test_type.capitalize()}

h3. Preconditions
{chr(10).join([f'* {pc}' for pc in preconditions]) if preconditions else 'None'}

h3. Input Data
{chr(10).join([f'* {inp}' for inp in input_data]) if input_data else 'None'}

h3. Test Steps
#_Test Steps_
{chr(10).join([f'# {step}' for step in steps]) if steps else 'No steps specified'}

h3. Expected Result
{{panel:title=Expected Result|borderColor=#008000|titleBGColor=#D9EAD3}}
{expected_result}
{{panel}}

h3. Automation Info
This ticket was automatically generated from an LLM-based test case.
            """.strip()

            # For test cases, use Task issue type and appropriate priority/severity
            ticket = self.create_jira_ticket(
                summary=summary,
                description=description,
                issue_type="Task",  # Use Task for test cases
                labels=['automated-test-case', 'qa', 'llm-generated', test_type.lower(), 'test-automation'],
                priority="Medium",
                severity="Majeure" 
            )

            if ticket:
                created_tickets.append({
                    'test_title': title,
                    'jira_key': ticket['key'],
                    'jira_url': f"{self.jira_url}/browse/{ticket['key']}",
                    'type': test_type
                })
                print(f"Created Jira ticket {ticket['key']} for test case: {title}")

        return created_tickets

    def process_llm_test_cases_from_web_app(self, json_file_path: str, create_tickets: bool = True) -> List[Dict]:
        """
        Process LLM-generated test cases saved from the web app
        
        Args:
            json_file_path: Path to JSON file with LLM-generated test cases
            create_tickets: Whether to actually create Jira tickets or just parse
            
        Returns:
            List of test case information
        """
        with open(json_file_path, 'r', encoding='utf-8') as f:
            test_cases = json.load(f)
        
        if create_tickets:
            return self.bulk_create_tickets_from_json(test_cases)
        else:
            return [{
                'id': tc.get('id', 'N/A'),
                'title': tc.get('title', 'Unnamed'),
                'type': tc.get('type', 'functional'),
                'steps_count': len(tc.get('steps', []))
            } for tc in test_cases]


def main():
    """Main function to run the Jira ticket creator from the command line."""
    import argparse

    parser = argparse.ArgumentParser(description="Create Jira tickets from test reports or JSON files.")
    parser.add_argument("--report-path", help="Path to the pytest HTML report.", default="reports/report.html")
    parser.add_argument("--json-path", help="Path to a JSON file with LLM-generated test cases.")
    parser.add_argument("--all", action="store_true", help="Process both the report and JSON file if they exist.")

    args = parser.parse_args()

    # Configuration from environment variables
    jira_url = os.getenv("JIRA_URL")
    jira_username = os.getenv("JIRA_USERNAME")
    jira_api_token = os.getenv("JIRA_API_TOKEN")
    jira_project_key = os.getenv("JIRA_PROJECT_KEY")

    if not all([jira_url, jira_username, jira_api_token, jira_project_key]):
        print("Error: Missing Jira configuration. Please set JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN, and JIRA_PROJECT_KEY environment variables.")
        sys.exit(1)

    # Initialize the ticket creator
    jira_creator = JiraTicketCreator(jira_url, jira_username, jira_api_token, jira_project_key)

    # Discover custom fields from environment variables
    jira_creator.custom_fields['custom_priority'] = os.getenv("JIRA_CUSTOM_FIELD_PRIORITY")
    jira_creator.custom_fields['severity'] = os.getenv("JIRA_CUSTOM_FIELD_SEVERITY")


    if args.all or args.report_path:
        if os.path.exists(args.report_path):
            print(f"Processing test report: {args.report_path}")
            created_tickets = jira_creator.create_tickets_for_failures(args.report_path)
            print(f"Created {len(created_tickets)} Jira tickets from test failures.")
        else:
            print(f"Test report not found at {args.report_path}")

    if args.all or args.json_path:
        if args.json_path and os.path.exists(args.json_path):
            print(f"Processing LLM-generated test cases: {args.json_path}")
            created_tickets = jira_creator.bulk_create_tickets_from_json(args.json_path)
            print(f"Created {len(created_tickets)} Jira tickets from LLM-generated test cases.")
        elif args.json_path:
            print(f"JSON file not found at {args.json_path}")


if __name__ == "__main__":
    main()