# Quiz Generator API

API de generation de quiz intelligente et flexible. Permet de generer des quizz aleatoires avec filtrage par tags et difficulte.

## Table des matieres

- [Vue d'ensemble](#vue-densemble)
- [Fonctionnalites](#fonctionnalites)
- [Prerequis](#prerequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Lancement](#lancement)
- [Utilisation de l'API](#utilisation-de-lapi)
- [Exemples d'appels](#exemples-dappels)
- [Structure du projet](#structure-du-projet)
- [Architecture technique](#architecture-technique)

## Vue d'ensemble

Ce projet est une API REST construite avec FastAPI qui genere des quiz adaptes a vos besoins. L'API utilise une banque de questions stockee en memoire et propose des fonctionnalites de filtrage avancees.

### Cas d'usage

- Generer des quizz pour l'entrainement sportif
- Filtrer les questions par domaine (performance, tactique, mental, nutrition)
- Adapter le niveau de difficulte (facile, moyen, difficile)
- Obtenir une repartition equilibree des sujets

## Fonctionnalites

- Generation aleatoire: Cree des quiz avec un nombre de questions configurable
- Filtrage par tags: Repartit les questions selon vos proportions preferees
- Filtrage par difficulte: Selectionne uniquement les niveaux desires
- Documentation interactive: Swagger UI incluse (/docs)
- Validation robuste: Verification des parametres et erreurs explicites
- Identifiants uniques: Chaque quiz et question a un UUID
- Timestamps: Enregistrement de la date/heure de creation

## Prerequis

- Python 3.9+
- pip (gestionnaire de paquets Python)

## Installation

### 1. Acceder au projet

```
cd /home/daisa-luise-monteiro/Documents/akassa/backend
```

### 2. Creer un environnement virtuel (optionnel mais recommande)

```
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dependances

```
pip install fastapi uvicorn pydantic
```

Ou installer depuis un fichier requirements.txt (si disponible):

```
pip install -r requirements.txt
```

## Configuration

### Banque de questions

Les questions sont definies dans le dictionnaire BANQUE dans main.py. Vous pouvez:

- Ajouter des questions: Creer de nouvelles instances de Question
- Modifier les tags: Utiliser tags=["tag1", "tag2", ...]
- Ajuster la difficulte: Utiliser difficulte="facile", "moyen" ou "difficile"

### Exemple: Ajouter une question

```python
Question(
    contenu="Quelle est l'importance du repos ?",
    tags=["performance", "mental"],
    difficulte="moyen"
)
```

## Lancement

### Demarrer le serveur

```
python3 main.py
```

Vous verrez:

```
Serveur demarre sur http://127.0.0.1:8000
Documentation interactive: http://127.0.0.1:8000/docs
```

### Arreter le serveur

Appuyez sur Ctrl+C dans le terminal.

## Utilisation de l'API

### Endpoint disponible

POST /quiz/generer

Genere un nouveau quiz selon les parametres fournis.

#### Parametres (JSON)

| Parametre | Type | Obligatoire | Description | Exemple |
|-----------|------|-------------|-------------|---------|
| n | integer | Oui | Nombre de questions (1-50) | 5 |
| filtres_tags | object | Non | Repartition par tag (0-100%) | {"performance": 0.4, "tactique": 0.3} |
| difficulte | string | Non | Niveau de difficulte | "moyen" |

#### Reponse

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "questions": [
    {
      "id": "uuid...",
      "contenu": "Qu'est-ce que le VO2max ?",
      "tags": ["performance"],
      "difficulte": "facile"
    }
  ],
  "score": 0,
  "cree_le": "2026-04-09T10:30:00"
}
```

## Exemples d'appels

### 1. Quiz simple (5 questions aleatoires)

```
curl -X POST http://127.0.0.1:8000/quiz/generer \
  -H "Content-Type: application/json" \
  -d '{"n": 5}'
```

### 2. Quiz avec filtrage par tags

```
curl -X POST http://127.0.0.1:8000/quiz/generer \
  -H "Content-Type: application/json" \
  -d '{
    "n": 10,
    "filtres_tags": {
      "performance": 0.5,
      "tactique": 0.3,
      "mental": 0.2
    }
  }'
```

### 3. Quiz facile uniquement

```
curl -X POST http://127.0.0.1:8000/quiz/generer \
  -H "Content-Type: application/json" \
  -d '{
    "n": 8,
    "difficulte": "facile"
  }'
```

### 4. Quiz moyen avec repartition equilibree

```
curl -X POST http://127.0.0.1:8000/quiz/generer \
  -H "Content-Type: application/json" \
  -d '{
    "n": 6,
    "difficulte": "moyen",
    "filtres_tags": {
      "performance": 0.5,
      "tactique": 0.5
    }
  }'
```

### 5. Avec Python

```python
import requests

url = "http://127.0.0.1:8000/quiz/generer"
payload = {
    "n": 5,
    "filtres_tags": {"performance": 0.6, "nutrition": 0.4},
    "difficulte": "moyen"
}

response = requests.post(url, json=payload)
quiz = response.json()
print(f"Quiz cree avec {len(quiz['questions'])} questions")
```

## Structure du projet

```
backend/
- main.py               Application principale (API + logique)
- README.md             Documentation (ce fichier)
- requirements.txt      Dependances Python (optionnel)
- __pycache__/          Cache Python (auto-genere)
```

## Architecture technique

### Modeles de donnees

1. QuizConfig: Configuration de generation (nombre, tags, difficulte)
2. Question: Represente une question avec ID, contenu, tags et difficulte
3. Quiz: Quiz genere contenant des questions, un ID et un score

### Flux de generation

```
QuizConfig -> Filtrage par difficulte -> Selection par tags
          -> Completion aleatoire -> Melange -> Quiz
```

### Technologie

- Framework: FastAPI 0.100+
- Serveur: Uvicorn (serveur ASGI)
- Validation: Pydantic
- ID: UUID4
- Timestamps: datetime

## Tester l'API

### Via Swagger UI

Allez a: http://127.0.0.1:8000/docs

Cliquez sur "Try it out" pour tester directement dans le navigateur.

### Via ReDoc (alternative)

Allez a: http://127.0.0.1:8000/redoc

## Gestion des erreurs

| Code | Erreur | Cause |
|------|--------|-------|
| 400 | Bad Request | Banque insuffisante ou parametres invalides |
| 422 | Validation Error | JSON invalide ou parametres hors limites |

### Exemple d'erreur

```
curl -X POST http://127.0.0.1:8000/quiz/generer \
  -d '{"n": 100, "filtres_tags": {"performance": 1.5}}'

Reponse:
{"detail": "La somme des pourcentages des tags ne peut pas depasser 1.0"}
```

## Notes

- Les questions sont stockees en memoire (non-persistantes)
- Chaque redemarrage reinitialise la banque
- Les quotas de tags sont arrondis (ceil) pour garantir les proportions
- Les questions non classees par tag ne sont utilisees que pour la completion

## Support

Pour toute question ou amelioration, consultez le code source dans main.py.

Derniere mise a jour: 9 avril 2026# generation_de_quizz_1
