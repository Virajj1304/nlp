"""
TaskLens — FastAPI Backend
============================
Clean REST API powered entirely by classical NLP (NLTK + WordNet).
No external LLMs or third-party generative APIs.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import nltk

# Ensure all required NLTK datasets are downloaded in production / fresh containers
def _ensure_nltk_data():
    required_packages = [
        "punkt",
        "punkt_tab",
        "averaged_perceptron_tagger",
        "averaged_perceptron_tagger_eng",
        "wordnet",
        "omw-1.4",
        "stopwords",
        "tagsets",
    ]
    for pkg in required_packages:
        try:
            nltk.data.find(pkg)
        except LookupError:
            try:
                nltk.download(pkg, quiet=True)
            except Exception:
                pass

_ensure_nltk_data()

from services import task_extractor, word_meaning, statistics
from services.predictor import ngram_model

# ── App Definition ───────────────────────────────────────────────────

app = FastAPI(
    title="TaskLens API",
    description="Productivity web app converting unstructured messages to actionable tasks via classical NLP",
    version="1.0.0",
)

# Robust CORS configuration for local development and deployed frontends (Render, Vercel, Netlify)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Schemas ──────────────────────────────────────────────────

class TextInput(BaseModel):
    text: str = Field(..., min_length=1, description="Raw input text")


class WordMeaningInput(BaseModel):
    sentence: str = Field(..., min_length=1, description="Context sentence")
    target_word: str = Field(..., min_length=1, description="Target word to disambiguate")


class PredictInput(BaseModel):
    text: str = Field(..., min_length=1, description="Prefix text for next-word suggestion")
    top_k: int = Field(5, ge=1, le=15, description="Number of suggestions to return")


# ── Endpoints ────────────────────────────────────────────────────────

@app.post("/api/extract-tasks")
def extract_tasks_endpoint(body: TextInput):
    """
    Main feature: Extract structured task cards (action, object, assignee,
    deadline, priority, domain context) from unstructured text.
    """
    try:
        return task_extractor.extract_tasks(body.text)
    except Exception as e:
        return {"error": str(e), "tasks": [], "count": 0}


@app.post("/api/word-meaning")
def word_meaning_endpoint(body: WordMeaningInput):
    """
    Feature 2: Word Sense Disambiguation using WordNet & Lesk algorithm.
    """
    try:
        return word_meaning.detect_meaning(body.sentence, body.target_word)
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/predict")
def predict_endpoint(body: PredictInput):
    """
    Feature 3: Next-word prediction using statistical Trigram/Bigram/Unigram model.
    """
    try:
        result = ngram_model.predict(body.text, top_k=body.top_k)
        result["corpus_stats"] = ngram_model.corpus_stats()
        return result
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/statistics")
def statistics_endpoint(body: TextInput):
    """
    Feature 4: Lightweight text insights, metrics, frequencies and bigrams.
    """
    try:
        return statistics.compute(body.text)
    except Exception as e:
        return {"error": str(e)}


@app.get("/")
def root():
    return {
        "app": "TaskLens API",
        "status": "online",
        "docs": "/docs",
        "health": "/api/health",
        "description": "Productivity web app powered by classical NLP (NLTK + WordNet)",
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "app": "TaskLens",
        "nlp_engine": "NLTK + WordNet",
        "version": "1.0.0"
    }
