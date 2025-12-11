"""
Script to run tests and automatically create Jira tickets for failures
"""
import subprocess
import sys
import os
from pathlib import Path
import argparse

def run_tests_and_create_jira_tickets():
    """Run pytest and automatically create Jira tickets for failures"""
    
    parser = argparse.ArgumentParser(description="Run tests and create Jira tickets for failures.")
    parser.add_argument("test_path", nargs='?', default="tests/", help="Path to the test file or directory to run.")
    args = parser.parse_args()

    print(f"Running tests in: {args.test_path}")
    
    # Run pytest with HTML report
    result = subprocess.run([
        sys.executable, "-m", "pytest", args.test_path,
        "--html=reports/report.html", 
        "--self-contained-html",
        "-v"
    ], capture_output=True, text=True)
    
    print("Test execution completed.")
    print(f"Return code: {result.returncode}")
    
    # Check if there are any failures before proceeding
    if "failed" in result.stdout or result.returncode != 0:
        print("Test failures detected. Creating Jira tickets...")
        
        # Import and run the Jira automation
        try:
            from jira_automation_enhanced import JiraTicketCreator
            import os
            
            # Get Jira configuration
            jira_url = os.getenv("JIRA_URL")
            jira_username = os.getenv("JIRA_USERNAME") 
            jira_api_token = os.getenv("JIRA_API_TOKEN")
            jira_project_key = os.getenv("JIRA_PROJECT_KEY")
            
            if not all([jira_url, jira_username, jira_api_token, jira_project_key]):
                print("Jira configuration not found. Please set environment variables.")
                print("Set: JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN, JIRA_PROJECT_KEY")
                return
            
            # Initialize Jira ticket creator
            jira_creator = JiraTicketCreator(jira_url, jira_username, jira_api_token, jira_project_key)
            
            # Create tickets for failures
            report_path = "reports/report.html"
            if os.path.exists(report_path):
                created_tickets = jira_creator.create_tickets_for_failures(report_path)
                print(f"Created {len(created_tickets)} Jira tickets for test failures")
            else:
                print(f"Report not found at {report_path}")
                
        except ImportError as e:
            print(f"Error importing Jira automation: {e}")
        except Exception as e:
            print(f"Error creating Jira tickets: {e}")
    else:
        print("No test failures detected. No Jira tickets created.")

if __name__ == "__main__":
    run_tests_and_create_jira_tickets()