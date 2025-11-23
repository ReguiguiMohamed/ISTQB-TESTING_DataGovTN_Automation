import os
import sys
import google.generativeai as genai

def get_gemini_api_key():
    """Get Gemini API key from environment variable"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        print("If you used 'setx' command, please open a NEW command prompt and try again.")
        print("Alternatively, you can set it using 'setx GEMINI_API_KEY \"your_api_key_here\"'")
        return None
    return api_key

def load_prompt_template():
    """Load the prompt template from a file"""
    try:
        with open("prompt_template.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("Error: prompt_template.txt not found.")
        print("Creating a default prompt template...")
        create_default_prompt_template()
        return load_prompt_template()

def create_default_prompt_template():
    """Create a default prompt template file"""
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
    print("Default prompt template created as 'prompt_template.txt'")

def generate_test_cases(user_story, acceptance_criteria):
    """Generate test cases using Gemini API"""
    api_key = get_gemini_api_key()
    if not api_key:
        return None

    try:
        # Configure the API key
        genai.configure(api_key=api_key)

        # Select the model - using the correct model name
        model = genai.GenerativeModel('gemini-1.5-pro')

        # Load the prompt template
        prompt_template = load_prompt_template()

        # Replace placeholders in the template
        prompt = prompt_template.replace("[USER_STORY]", user_story)
        prompt = prompt.replace("[ACCEPTANCE_CRITERIA]", acceptance_criteria)

        # Generate content
        response = model.generate_content(prompt)

        return response.text
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def main():
    print("🎯 Test Case Generator using Gemini AI")
    print("="*50)
    
    # Get user input
    print("Entrez la user story:")
    user_story = input("> ")
    
    print("\nEntrez les critères d'acceptation:")
    acceptance_criteria = input("> ")
    
    print("\nGénération des cas de test en cours...")
    
    # Generate test cases
    result = generate_test_cases(user_story, acceptance_criteria)
    
    if result:
        print("\n" + "="*50)
        print("CAS DE TEST GÉNÉRÉS:")
        print("="*50)
        print(result)
        
        # Optionally save to file
        save_to_file = input("\nVoulez-vous sauvegarder les résultats dans un fichier? (y/n): ")
        if save_to_file.lower() == 'y':
            filename = input("Nom du fichier (sans extension): ") or "test_cases"
            with open(f"{filename}.md", "w", encoding="utf-8") as f:
                f.write("# Cas de test générés\n\n")
                f.write(result)
            print(f"Résultats sauvegardés dans {filename}.md")
    else:
        print("Échec de la génération des cas de test.")

if __name__ == "__main__":
    main()