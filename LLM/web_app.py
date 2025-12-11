from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import jira_automation_enhanced
sys.path.append(str(Path(__file__).resolve().parent.parent))
from jira_automation_enhanced import JiraTicketCreator

# Available models - update this list to match free models in Nov 2025
# These are the models as of your requirement
AVAILABLE_MODELS = [
    {"name": "Gemini 2.5 Flash", "id": "gemini-2.5-flash", "provider": "gemini"},
    {"name": "Gemini 2.5 Pro", "id": "gemini-2.5-pro", "provider": "gemini"},
]

app = Flask(__name__)

def load_prompt_template():
    """Load the prompt template from a file, create default if missing"""
    try:
        with open("prompt_template.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # Create default prompt template
        default_template = """ROLE: You are a senior ISTQB-certified test analyst.
TASK: Generate black-box test cases from the following user story and acceptance criteria.

CONSTRAINTS:
- Focus ONLY on functional, black-box behavior (no implementation).
- Use clear, concise French.
- Structure the test cases as a JSON array with these fields:
  - id: Test case identifier
  - title: Title of the test case
  - type: Type of test case (positif / négatif / limite)
  - preconditions: Array of preconditions
  - input_data: Array of input data
  - steps: Array of steps to execute
  - expected_result: Expected result of the test
- Output only valid JSON with no additional text.

INPUT:
User Story:
[USER_STORY]

Critères d'acceptation:
[ACCEPTANCE_CRITERIA]

OUTPUT:
- JSON array of test cases covering the acceptance criteria, with positive, negative and boundary cases if applicable."""

        with open("prompt_template.txt", "w", encoding="utf-8") as f:
            f.write(default_template)
        return default_template

import json
import re

def generate_test_cases(user_story, acceptance_criteria, api_key, model_id):
    """Generate test cases using specified model and API key"""
    try:
        # Configure the API key
        genai.configure(api_key=api_key)

        # Select the model
        model = genai.GenerativeModel(model_id)

        # Load the prompt template
        prompt_template = load_prompt_template()

        # Replace placeholders in the template
        prompt = prompt_template.replace("[USER_STORY]", user_story)
        prompt = prompt_template.replace("[ACCEPTANCE_CRITERIA]", acceptance_criteria)

        # Generate content
        response = model.generate_content(prompt)

        # Extract JSON from response (in case model adds extra text)
        response_text = response.text.strip()

        # Try to find JSON in the response
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            # If no JSON array found, try to extract what looks like JSON
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            if json_start != -1 and json_end != 0:
                json_str = response_text[json_start:json_end]
            else:
                raise ValueError("Could not extract JSON from response")

        # Parse the JSON to validate it
        try:
            test_cases = json.loads(json_str)
            # Convert to markdown table format for display
            markdown_table = convert_json_to_markdown_table(test_cases)
            return {
                'json_result': test_cases,
                'markdown_result': markdown_table
            }
        except json.JSONDecodeError:
            # If parsing fails, return the original text
            return {
                'json_result': [],
                'markdown_result': response_text
            }

    except Exception as e:
        raise e

def convert_json_to_markdown_table(test_cases):
    """Convert JSON test cases to markdown table format"""
    if not test_cases:
        return "Aucun cas de test généré."

    # Create markdown table header
    markdown = "| ID | Titre | Type | Préconditions | Données d'entrée | Étapes | Résultat attendu |\n"
    markdown += "|----|-------|------|---------------|------------------|--------|------------------|\n"

    # Add each test case as a row
    for case in test_cases:
        id_val = case.get('id', 'N/A')
        title = case.get('title', 'N/A')
        test_type = case.get('type', 'N/A')

        # Convert arrays to string format for display
        preconditions = '<br>'.join(case.get('preconditions', ['N/A']))
        input_data = '<br>'.join(case.get('input_data', ['N/A']))
        steps = '<br>'.join([f"{i+1}. {step}" for i, step in enumerate(case.get('steps', ['N/A']))])
        expected_result = case.get('expected_result', 'N/A')

        markdown += f"| {id_val} | {title} | {test_type} | {preconditions} | {input_data} | {steps} | {expected_result} |\n"

    return markdown

@app.route('/')
def index():
    return render_template('index.html', models=AVAILABLE_MODELS)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        user_story = data.get('user_story', '')
        acceptance_criteria = data.get('acceptance_criteria', '')
        api_key = data.get('api_key', '')
        model_id = data.get('model_id', '')

        if not user_story or not acceptance_criteria or not api_key or not model_id:
            return jsonify({'error': 'Missing required fields'}), 400

        result = generate_test_cases(user_story, acceptance_criteria, api_key, model_id)

        return jsonify({
            'result': result['markdown_result'],
            'json_result': result['json_result']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/create-jira-tickets', methods=['POST'])
def create_jira_tickets():
    try:
        data = request.json
        test_cases = data.get('test_cases', [])

        if not test_cases:
            return jsonify({'error': 'No test cases provided'}), 400

        # Configuration from environment variables
        jira_url = os.getenv("JIRA_URL")
        jira_username = os.getenv("JIRA_USERNAME")
        jira_api_token = os.getenv("JIRA_API_TOKEN")
        jira_project_key = os.getenv("JIRA_PROJECT_KEY")

        if not all([jira_url, jira_username, jira_api_token, jira_project_key]):
            return jsonify({'error': 'Jira configuration not found in environment variables.'}), 500

        # Initialize the ticket creator
        jira_creator = JiraTicketCreator(jira_url, jira_username, jira_api_token, jira_project_key)
        
        # Discover custom fields from environment variables
        jira_creator.custom_fields['custom_priority'] = os.getenv("JIRA_CUSTOM_FIELD_PRIORITY")
        jira_creator.custom_fields['severity'] = os.getenv("JIRA_CUSTOM_FIELD_SEVERITY")

        created_tickets = jira_creator.bulk_create_tickets_from_json(test_cases)

        return jsonify({'created_tickets': created_tickets})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)