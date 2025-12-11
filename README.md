# ISTQB-TESTING_DataGovTN_Automation

ISTQB Foundation Level software testing project using Python and Selenium to implement Black-Box, Non-Functional, and Load testing on the Tunisian National Open Data Portal (data.gov.tn).

## 🎯 LLM-Powered Test Case Generation

This project includes an innovative LLM-based test case generator that automatically creates black-box test cases from user stories and acceptance criteria.

### Quick Start with LLM Generator

1. **Get a Gemini API key** from Google AI Studio (free tier)

2. **Install the Gemini CLI:**
   ```bash
   npm install -g @google/generative-ai
   ```

3. **Set your API key:**
   ```bash
   setx GEMINI_API_KEY "your_api_key_here"  # Windows
   # or
   export GEMINI_API_KEY="your_api_key_here"  # Linux/macOS
   ```

   **Important (Windows):** After running `setx`, open a NEW command prompt for the environment variable to be available.

4. **Run the generator:**
   ```bash
   cd LLM
   python generate_test_cases.py
   # or double-click generate_test_cases.bat (Windows)
   ```

5. **Or use the web interface (recommended):**
   ```bash
   cd LLM
   python web_app.py
   ```
   Then open your browser at: http://localhost:5000

For detailed instructions, see [LLM/README.md](LLM/README.md).

## Docker Setup for Cross-Browser Testing

This project includes a Docker-based Selenium Grid setup for reliable cross-browser testing. This ensures consistent test execution across different browsers without requiring local browser driver installations.

For detailed instructions, see [docs/docker-setup.md](docs/docker-setup.md).
