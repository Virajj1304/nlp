"""
NLP Studio — FastAPI Backend
==============================
Provides REST API endpoints for each NLP tool.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from services import tokenizer, word_meaning, grammar, statistics
from services.predictor import ngram_model

# ── App ──────────────────────────────────────────────────────────────

app = FastAPI(title="NLP Studio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response schemas ───────────────────────────────────────

class TextInput(BaseModel):
    text: str = Field(..., min_length=1, description="Input text")


class WordMeaningInput(BaseModel):
    sentence: str = Field(..., min_length=1)
    target_word: str = Field(..., min_length=1)


class PredictInput(BaseModel):
    text: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=20)


# ── Endpoints ────────────────────────────────────────────────────────

@app.post("/api/tokenize")
def tokenize_endpoint(body: TextInput):
    try:
        return tokenizer.analyze(body.text)
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/word-meaning")
def word_meaning_endpoint(body: WordMeaningInput):
    try:
        return word_meaning.detect_meaning(body.sentence, body.target_word)
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/grammar")
def grammar_endpoint(body: TextInput):
    try:
        return grammar.analyze(body.text)
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/predict")
def predict_endpoint(body: PredictInput):
    try:
        result = ngram_model.predict(body.text, top_k=body.top_k)
        result["corpus_stats"] = ngram_model.corpus_stats()
        return result
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/statistics")
def statistics_endpoint(body: TextInput):
    try:
        return statistics.compute(body.text)
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/health")
def health():
    return {"status": "ok"}
