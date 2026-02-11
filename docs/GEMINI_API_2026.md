# Configuration Gemini API (2026)

## Changements API en 2026

Le package `google-generativeai` est **déprécié** depuis 2026.

**Migration effectuée:**
- ❌ `google-generativeai` (0.8.6) → ✅ `google-genai` (1.62.0)
- ❌ `gemini-1.5-flash` → ✅ `gemini-2.0-flash-exp`

## Configuration

### 1. Obtenir une clé API

Visite: https://aistudio.google.com/app/apikey

- Clique sur "Create API Key"
- Copie la clé

### 2. Configurer la variable d'environnement

```bash
# Option 1: Session actuelle
export GEMINI_API_KEY="ta-clé-ici"

# Option 2: Persistant (ajoute à ~/.bashrc ou ~/.zshrc)
echo 'export GEMINI_API_KEY="ta-clé-ici"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Vérifier la configuration

```bash
# Test simple
python -c "from google import genai; import os; client = genai.Client(api_key=os.getenv('GEMINI_API_KEY')); print('✅ API key configured')"

# Test complet
skillops oncall
```

## Utilisation du nouveau package

### Ancien code (déprécié)

```python
import google.generativeai as genai

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content(prompt)
```

### Nouveau code (2026)

```python
from google import genai

client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents=prompt
)
```

## Modèles disponibles (2026)

- **gemini-2.0-flash-exp** ⭐ (recommandé pour SkillOps)
  - Plus rapide
  - Moins cher
  - Parfait pour génération d'incidents

- **gemini-2.0-pro-exp**
  - Plus puissant
  - Plus lent
  - Pour tâches complexes

## Dépendances

```txt
google-genai==1.62.0
google-auth==2.47.0
```

## Troubleshooting

### Erreur: "Missing key inputs argument"

**Cause:** Variable `GEMINI_API_KEY` non définie

**Solution:**
```bash
export GEMINI_API_KEY="ta-clé"
```

### Erreur: "404 model not found"

**Cause:** Utilisation d'un ancien nom de modèle

**Solution:** Le code utilise maintenant `gemini-2.0-flash-exp` automatiquement

### Warning: "google.generativeai package has ended"

**Status:** ✅ Résolu - migration vers `google-genai` effectuée

## Tests

Tous les tests utilisent des mocks pour éviter les appels API réels:

```bash
# Tests oncall AI
pytest tests/lms/oncall_ai_test.py -v

# Tous les tests
pytest tests/ -q
# Résultat: 457 passed ✅
```

## Documentation officielle

- Nouveau package: https://ai.google.dev/gemini-api/docs/quickstart?lang=python
- Migration guide: https://github.com/google-gemini/deprecated-generative-ai-python

## Résumé

✅ **Configuration complète**
- Package mis à jour: `google-genai 1.62.0`
- Modèle moderne: `gemini-2.0-flash-exp`
- API 2026 compatible
- Tous les tests passent (457/457)
- Code plus propre avec la nouvelle API
