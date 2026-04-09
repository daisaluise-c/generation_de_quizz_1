import random
import math
from collections import defaultdict
from uuid import uuid4
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator

# 1. MODÈLES DE DONNÉES
class QuizConfig(BaseModel):
    """Configuration pour la génération d'un quiz"""
    n: int = Field(..., ge=1, le=50, description="Nombre de questions", example=5)
    filtres_tags: Optional[dict[str, float]] = Field(
        None, description="Répartition par tag (ex: {'performance': 0.4, 'tactique': 0.3})",
        example={"performance": 0.4, "tactique": 0.3}
    )
    difficulte: Optional[str] = Field(None, description="Filtrer par difficulté : facile, moyen, difficile", example="moyen")

    @validator('difficulte')
    def check_difficulte(cls, v):
        if v is not None and v not in ("facile", "moyen", "difficile"):
            raise ValueError("La difficulté doit être 'facile', 'moyen' ou 'difficile'")
        return v

    @validator('filtres_tags')
    def check_tags_sum(cls, v):
        if v and sum(v.values()) > 1.0:
            raise ValueError("La somme des pourcentages des tags ne peut pas dépasser 1.0 (100%)")
        return v

class Question(BaseModel):
    """Représente une question dans la banque"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    contenu: str
    tags: list[str]
    difficulte: str  # 'facile', 'moyen', 'difficile'

class Quiz(BaseModel):
    """Représente un quiz généré"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    questions: list[Question]
    score: int = 0
    cree_le: datetime = Field(default_factory=datetime.utcnow)

# 2. BANQUE DE QUESTIONS (élargie pour éviter les erreurs de quantité)
BANQUE = [
    # Performance
    Question(contenu="Qu'est-ce que le VO2max ?", tags=["performance"], difficulte="facile"),
    Question(contenu="Expliquez le seuil lactique.", tags=["performance"], difficulte="moyen"),
    Question(contenu="Facteurs de récupération post-effort.", tags=["performance"], difficulte="difficile"),
    Question(contenu="Méthodes d'entraînement en intervalles.", tags=["performance"], difficulte="moyen"),
    Question(contenu="La périodisation en sport.", tags=["performance"], difficulte="moyen"),
    # Tactique
    Question(contenu="Qu'est-ce que le pressing haut ?", tags=["tactique"], difficulte="facile"),
    Question(contenu="Différence bloc bas vs bloc médian.", tags=["tactique"], difficulte="moyen"),
    Question(contenu="La contre-attaque organisée.", tags=["tactique"], difficulte="moyen"),
    Question(contenu="Défense en zone vs homme à homme.", tags=["tactique"], difficulte="moyen"),
    # Mental
    Question(contenu="Définissez la cohérence cardiaque.", tags=["mental"], difficulte="facile"),
    Question(contenu="Comment développer la résilience ?", tags=["mental"], difficulte="difficile"),
    Question(contenu="Techniques de visualisation.", tags=["mental"], difficulte="moyen"),
    # Nutrition
    Question(contenu="Rôle des glucides avant l'effort.", tags=["nutrition"], difficulte="facile"),
    Question(contenu="Fenêtre anabolique : définition.", tags=["nutrition"], difficulte="moyen"),
    Question(contenu="Alimentation et performance cognitive.", tags=["nutrition", "mental"], difficulte="difficile"),
    Question(contenu="Hydratation pendant l'effort.", tags=["nutrition"], difficulte="moyen"),
]

# 3. LOGIQUE DE GÉNÉRATION
def generer_quiz(config: QuizConfig) -> list[Question]:
    """
    Génère une liste de questions selon la configuration.
    Lève ValueError si la banque est insuffisante.
    """
    # 1. Filtrage par difficulté
    pool = BANQUE
    if config.difficulte:
        pool = [q for q in BANQUE if q.difficulte == config.difficulte]

    selectionnees = []
    ids_pris = set()

    # 2. Sélection par quotas de tags
    if config.filtres_tags:
        # Normalisation des proportions pour que la somme = 1
        total = sum(config.filtres_tags.values())
        proportions_norm = {tag: pct / total for tag, pct in config.filtres_tags.items()}

        # Indexation des questions par tag (dans le pool filtré)
        index = defaultdict(list)
        for q in pool:
            for tag in q.tags:
                if tag in proportions_norm:
                    index[tag].append(q)

        # Tirage par tag
        for tag, pct in proportions_norm.items():
            quota = math.ceil(config.n * pct)   # nombre de questions visées pour ce tag
            dispo = [q for q in index[tag] if q.id not in ids_pris]
            tirees = random.sample(dispo, min(quota, len(dispo)))
            selectionnees.extend(tirees)
            ids_pris.update(q.id for q in tirees)

    # 3. Complétion aléatoire pour atteindre exactement N questions
    restant = config.n - len(selectionnees)
    if restant > 0:
        libres = [q for q in pool if q.id not in ids_pris]
        if len(libres) < restant:
            raise ValueError(f"Banque insuffisante : besoin de {restant} question(s) supplémentaire(s), mais seulement {len(libres)} disponible(s).")
        selectionnees.extend(random.sample(libres, restant))

    # 4. Mélange final
    random.shuffle(selectionnees)
    return selectionnees

# 4. ENDPOINT FASTAPI
app = FastAPI(title="Quiz Generator API", description="Génère des quiz aléatoires avec répartition par tag")

@app.post("/quiz/generer", response_model=Quiz, status_code=201)
def quiz_generer(config: QuizConfig):
    """
    Génère un quiz de N questions.

    Exemple de body JSON :
    {
      "n": 5,
      "filtres_tags": {"performance": 0.4, "tactique": 0.3},
      "difficulte": "moyen"
    }

    Exemple d'appel curl :
    curl -X POST http://127.0.0.1:8000/quiz/generer \\
         -H "Content-Type: application/json" \\
         -d '{"n": 5, "filtres_tags": {"performance": 0.4}}'
    """
    try:
        questions = generer_quiz(config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return Quiz(questions=questions)

# 5. LANCEMENT

if __name__ == "__main__":
    import uvicorn
    print("Serveur démarré sur http://127.0.0.1:8000")
    print("Documentation interactive : http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)