from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

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
- Structure the test cases in a markdown table with the columns:
  - ID
  - Titre
  - Type (positif / négatif / limite)
  - Préconditions
  - Données d'entrée
  - Étapes
  - Résultat attendu

INPUT:
User Story:
[USER_STORY]

Critères d'acceptation:
[ACCEPTANCE_CRITERIA]

OUTPUT:
- Une liste de cas de test couvrant les critères d'acceptation, avec des cas positifs, négatifs et aux limites si applicable.
- Format : un tableau markdown, sans explication autour."""
        
        with open("prompt_template.txt", "w", encoding="utf-8") as f:
            f.write(default_template)
        return default_template

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
        
        return response.text
    except Exception as e:
        raise e

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
        
        return jsonify({'result': result})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)