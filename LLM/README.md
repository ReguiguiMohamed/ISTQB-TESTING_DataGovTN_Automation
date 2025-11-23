# Générateur de Cas de Test avec Gemini AI

Cet outil permet de générer automatiquement des cas de test à partir d'une user story et de critères d'acceptation en utilisant l'IA Gemini.

## 🧩 Étapes de configuration

### Étape 1 – Obtenir une clé API Gemini (gratuite)

1. Vous avez besoin d'un compte Google
2. Allez sur Google AI Studio (Gemini) et créez une clé API (gratuite)
3. Copiez la clé API
4. Ne la collez pas ici; vous l'utiliserez localement sur votre machine

### Étape 2 – Installer les dépendances

Installez les dépendances Python nécessaires :

```bash
pip install -r ../requirements.txt
```

Ou installez spécifiquement la bibliothèque Google Generative AI :

```bash
pip install google-generativeai
```

### Étape 3 – Configurer la variable d'environnement

Sur Windows, exécutez cette commande dans une invite de commandes avec élévation de privilèges :

```cmd
setx GEMINI_API_KEY "VOTRE_CLÉ_API_ICI"
```

**Important :** Après avoir exécuté la commande `setx`, vous devez ouvrir une NOUVELLE invite de commandes pour que la variable d'environnement soit disponible. La variable n'est pas accessible dans la même session où vous avez exécuté `setx`.

## 🛠 Utilisation de l'outil

### Méthode 1: Interface Web (Recommandée)

L'interface web offre une expérience utilisateur plus conviviale avec sortie JSON structurée.

1. Installez les dépendances :
   ```bash
   pip install -r ../requirements.txt
   ```

2. Lancez l'application web :
   ```bash
   cd LLM
   python web_app.py
   ```

3. Ouvrez votre navigateur à l'adresse : http://localhost:5000

4. Dans l'interface :
   - Étape 1: Choisissez un modèle (ex: "Gemini 2.5 Flash")
   - Étape 2: Collez votre clé API Gemini dans le champ
   - Étape 3: Collez votre User Story + Critères d'acceptation, cliquez sur "Générer les cas de test"
   - Étape 4: Visualisez les résultats en format Markdown ou JSON
   - Étape 5: Téléchargez les résultats ou créez des tickets Jira automatiquement

#### Nouvelles Fonctionnalités Web:
- **Format Double**: Sortie à la fois en tableau Markdown et en JSON structuré
- **Téléchargement**: Boutons pour télécharger les formats JSON et Markdown
- **Jira Integration**: Bouton pour créer des tickets Jira directement depuis les résultats
- **Conversion Automatique**: Conversion fluide entre formats pour différentes utilisations

### Méthode 2: Script Python en ligne de commande

```bash
cd LLM
python generate_test_cases.py
```

### Méthode 3: Utiliser le script batch Windows

Double-cliquez sur `generate_test_cases.bat` ou exécutez-le dans un terminal :

```cmd
generate_test_cases.bat
```

## 🎫 Intégration Jira (Nouveau!)

Le système inclut maintenant une automatisation complète pour Jira:

### Gestion des échecs de test:
- Analyse automatique des rapports de test pytest (HTML)
- Création de tickets "Bug" pour chaque test échoué
- Intégration avec Jira via API REST

### Gestion des cas de test générés par LLM:
- Prise en charge du format JSON pour l'intégration Jira
- Création de tickets "Task" pour les nouveaux cas de test
- Étiquetage automatique et catégorisation

### Configuration:
Voir `README_JIRA_JSON.md` pour les détails complets sur la configuration Jira.

## 📝 Prompt utilisé

Le script utilise un template de prompt situé dans `prompt_template.txt` qui définit les rôles et contraintes pour la génération de cas de test.

## 🎯 Format de sortie

L'outil génère un tableau markdown avec les colonnes suivantes :
- ID
- Titre
- Type (positif / négatif / limite)
- Préconditions
- Données d'entrée
- Étapes
- Résultat attendu

## 🧪 Exemple d'utilisation

Exemple de user story :
> En tant qu'utilisateur, je veux rechercher un jeu de données par mot-clé afin de trouver rapidement les données pertinentes.

Exemple de critères d'acceptation :
> - Lorsque je saisis un mot-clé valide et que je lance la recherche, au moins un résultat pertinent s'affiche.
> - Si aucun jeu de données ne correspond au mot-clé, un message 'Aucun jeu de données trouvé' est affiché.
> - Si le champ de recherche est vide, aucun appel n'est fait et un message de validation est affiché.