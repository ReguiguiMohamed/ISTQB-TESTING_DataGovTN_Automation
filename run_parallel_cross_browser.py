import subprocess
import threading
from pathlib import Path
import sys

def run_browser_tests(browser_name, report_file):
    """Run tests for a specific browser"""
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/cross_browser/test_smoke_cross_browser.py",
        "-v", "--remote", f"--browser={browser_name}", 
        "--tb=short", 
        f"--html=tests/cross_browser/reports/{report_file}", 
        "--self-contained-html"
    ]
    
    print(f"Starting {browser_name} tests...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"{browser_name} tests completed successfully")
    else:
        print(f"{browser_name} tests failed:")
        print(result.stdout)
        print(result.stderr)
    
    return result.returncode

def main():
    # Create reports directory if it doesn't exist
    reports_dir = Path("tests/cross_browser/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Define test configurations
    browsers = [
        ("chrome", "chrome_report.html"),
        ("firefox", "firefox_report.html"), 
        ("edge", "edge_report.html")
    ]
    
    # Create threads for parallel execution
    threads = []
    results = {}
    
    for browser_name, report_file in browsers:
        thread = threading.Thread(
            target=lambda b=browser_name, r=report_file: results.update({b: run_browser_tests(b, r)})
        )
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print("\nAll parallel cross-browser tests completed!")
    print("Reports are available in the reports folder:")
    print("- chrome_report.html")
    print("- firefox_report.html") 
    print("- edge_report.html")
    
    # Return appropriate exit code
    return_codes = list(results.values())
    return max(return_codes) if return_codes else 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)