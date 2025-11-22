# Bug Reports

This document follows a standard template for reporting bugs found during the testing of the [data.gov.tn](https://www.data.gov.tn/) portal.

---

## Template de Rapport de Bug

```
### ID du Bug: [Numéro Unique, ex: BUG-001]

**Titre:** [Titre concis et descriptif du bug]

**Sévérité:** [Critique / Majeure / Mineure / Triviale]
**Priorité:** [Haute / Moyenne / Basse]

**Environnement:**
- **URL:** [URL où le bug a été trouvé]
- **Navigateur:** [Chrome / Firefox / Edge, Version]
- **Résolution d'écran:** [ex: 1920x1080]

**Description (Résumé):**
[Bref résumé du problème.]

**Étapes pour Reproduire:**
1. [Première étape, ex: Naviguer vers la page d'accueil]
2. [Deuxième étape, ex: Cliquer sur le bouton 'Rechercher']
3. [Troisième étape, ex: Entrer le texte '...' dans le champ de recherche]
4. [...]

**Résultat Attendu:**
[Ce qui aurait dû se passer si le bug n'existait pas.]

**Résultat Obtenu (Actuel):**
[Ce qui s'est réellement passé.]

**Pièces Jointes (Screenshots, Logs):**
- [Lien vers le screenshot, ex: ../reports/screenshots/screenshot_name.png]

```

---

## Exemple de Rapport de Bug

### ID du Bug: BUG-001

**Titre:** La recherche avec des caractères spéciaux retourne une page vide au lieu de résultats ou d'un message d'erreur

**Sévérité:** Majeure
**Priorité:** Haute

**Environnement:**
- **URL:** https://catalog.data.gov.tn/fr/dataset/
- **Navigateur:** Chrome 129.0
- **Résolution d'écran:** 1920x1080

**Description (Résumé):**
Lorsqu'un utilisateur effectue une recherche en utilisant une chaîne de caractères contenant uniquement des caractères spéciaux (par exemple, `!@#$%^&*()`), le site ne renvoie aucun résultat et n'affiche pas le message "Aucun jeu de données trouvé". La zone de résultats est simplement vide, ce qui peut prêter à confusion pour l'utilisateur.

**Étapes pour Reproduire:**
1. Naviguer vers la page de recherche des jeux de données : `https://catalog.data.gov.tn/fr/dataset/`.
2. Attendre que la page se charge complètement.
3. Dans le champ de recherche "Rechercher des jeux de données...", entrer la chaîne de caractères : `!@#$%`.
4. Appuyer sur la touche "Entrée" ou cliquer sur le bouton de recherche.

**Résultat Attendu:**
Le système devrait soit :
- Afficher un message clair indiquant "Aucun jeu de données trouvé pour '!@#$%'".
- OU ignorer les caractères spéciaux et afficher les résultats pour une recherche vide (si c'est le comportement attendu).
- OU afficher un message d'erreur de validation indiquant que les caractères spéciaux ne sont pas autorisés.

**Résultat Obtenu (Actuel):**
La page se recharge, mais la zone où les résultats devraient s'afficher est complètement vide. Il n'y a ni résultats, ni message d'erreur, ni message "Aucun jeu de données trouvé".

**Pièces Jointes (Screenshots, Logs):**
- *Hypothétique:* `../reports/screenshots/tests_functional_test_error_cases.py__test_search_with_special_characters_20251122-143000.png`

---
