# Configuration Gemini API (Février 2026)

## Modèles Gratuits Disponibles

| Modèle             | Capacités                  | Contexte Max | Multimodal  |
|--------------------|----------------------------|--------------|-------------|
| Gemini 2.5 Pro    | Raisonnement avancé, code  | 1M tokens    | Texte/Image |
| **Gemini 2.5 Flash** ⭐ | Rapide, généraliste    | 1M tokens    | Texte/Image |
| Gemini 2.5 Flash-Lite | Ultra-rapide, low-latency | 1M tokens  | Texte only  |

**SkillOps utilise:** `gemini-2.5-flash` (meilleur rapport rapidité/limites)

## Limites Free Tier (par projet, reset minuit PT)

| Modèle            | RPM (req/min) | TPM (tokens/min) | RPD (req/jour) | Images/min |
|-------------------|---------------|------------------|----------------|------------|
| Gemini 2.5 Pro   | 5             | 250K             | 100            | 1          |
| **Gemini 2.5 Flash** | **15**    | **250K**         | **1000**       | **2**      |
| Flash-Lite       | 15            | 250K             | 1000           | N/A        |

**Avantages Flash pour SkillOps:**
- 3x plus de requêtes/minute que Pro (15 vs 5)
- 10x plus de requêtes/jour (1000 vs 100)
- Latence plus faible
- Suffisant pour génération d'incidents

## Configuration

### 1. Obtenir une clé API

Visite: https://aistudio.google.com/app/apikey

- Clique sur "Create API Key"
- Copie la clé (gratuit, pas de carte de crédit requise)

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

## Implémentation Python (SDK google-genai)

### Installation

```bash
pip install -q -U google-genai
```

### Chat Basique (utilisé dans SkillOps)

```python
from google import genai

client = genai.Client(api_key="YOUR_API_KEY")
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents="Ton prompt ici"
)
print(response.text)
```

### Streaming

```python
client = genai.Client(api_key="YOUR_API_KEY")
for chunk in client.models.generate_content_stream(
    model='gemini-2.5-flash',
    contents="Prompt streaming"
):
    print(chunk.text, end="")
```

### Multimodal (Image)

```python
client = genai.Client(api_key="YOUR_API_KEY")
img = client.files.upload(file_path="image.jpg")
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=["Analyse cette image", img]
)
print(response.text)
```

## Architecture SkillOps

```python
# src/lms/oncall_ai.py
from google import genai

def generate_incident_with_ai(api_key, storage_path, difficulty):
    client = genai.Client(api_key=api_key)

    context = get_incident_context(storage_path)
    prompt = build_prompt(context, difficulty)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return parse_incident(response.text)
```

## Dépendances

```txt
google-genai
google-auth==2.47.0
```

## Troubleshooting

### Erreur: "Missing key inputs argument"

**Cause:** Variable `GEMINI_API_KEY` non définie

**Solution:**
```bash
export GEMINI_API_KEY="ta-clé"
```

### Erreur: "429 Rate Limit"

**Cause:** Trop de requêtes (15 req/min dépassés)

**Solution:**
```python
import time
time.sleep(60)  # Attendre reset
```

### Erreur: "404 model not found"

**Cause:** Nom de modèle incorrect

**Solution:** Le code utilise maintenant `gemini-2.5-flash` (correct pour 2026)

### Warning: "google.generativeai package has ended"

**Status:** ✅ Résolu - migration vers `google-genai` effectuée
- Package: `google-genai` (nouveau, maintenu)
- Plus de warning de dépréciation
- API moderne et stable

## Tests

Tous les tests utilisent des mocks pour éviter les appels API réels:

```bash
# Tests oncall AI
pytest tests/lms/oncall_ai_test.py -v

# Tous les tests
pytest tests/ -q
# Résultat: 457 passed ✅
```

## Comparaison des Modèles pour SkillOps

| Critère         | Gemini 2.5 Pro | Gemini 2.5 Flash ⭐ | Flash-Lite |
|----------------|----------------|---------------------|------------|
| Qualité        | Excellent      | Très bon            | Bon        |
| Vitesse        | Moyen          | **Rapide**          | Ultra      |
| RPM Free       | 5              | **15**              | 15         |
| RPD Free       | 100            | **1000**            | 1000       |
| Use case       | Raisonnement   | **Génération**      | Simple     |

**Pourquoi Flash ?**
- ✅ Suffisant pour générer des incidents réalistes
- ✅ 3x plus de requêtes/minute que Pro
- ✅ Génère hints et validation questions rapidement
- ✅ Coût gratuit avec limites généreuses

## Documentation officielle

- Pricing & Limits: https://ai.google.dev/gemini-api/docs/pricing
- Python SDK: https://ai.google.dev/gemini-api/docs/quickstart?lang=python
- Models: https://ai.google.dev/gemini-api/docs/models

## Résumé

✅ **Configuration complète**
- Package: `google-genai` (nouveau SDK maintenu)
- Modèle: `gemini-2.5-flash` (15 RPM, 1000 RPD)
- API: `client = genai.Client()` + `client.models.generate_content()`
- Tous les tests passent (457/457)
- Free tier suffisant pour usage SkillOps
- Plus de warnings de dépréciation
