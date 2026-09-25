# NLP Studio

**Interactive Natural Language Processing Toolkit**

A college mini-project that demonstrates classical NLP concepts through an
interactive web application. Built with React + Vite (frontend) and
FastAPI + NLTK (backend).

---

## Features

| Tool | NLP Concepts |
|------|-------------|
| **Tokenizer & Lemmatizer** | Sentence segmentation, word tokenization, WordNet lemmatization |
| **Word Meaning Detector** | WordNet, word senses, Lesk algorithm (WSD) |
| **Grammar Analyzer** | POS tagging, rule-based grammar checks |
| **Sentence Predictor** | N-gram language model (unigram/bigram/trigram), Laplace smoothing |
| **Text Statistics** | Word frequency, bigrams, corpus statistics |

All results are computed in real time — nothing is hardcoded.

---

## Tech Stack

- **Frontend:** React.js, Vite, vanilla CSS
- **Backend:** Python, FastAPI
- **NLP:** NLTK, WordNet, Lesk Algorithm

---

## Project Structure

```
nlp/
├── backend/
│   ├── main.py                 # FastAPI app with all endpoints
│   ├── requirements.txt        # Python dependencies
│   ├── download_nltk.py        # One-time NLTK data downloader
│   └── services/
│       ├── tokenizer.py        # Tokenization & Lemmatization
│       ├── word_meaning.py     # Word Sense Disambiguation (Lesk)
│       ├── grammar.py          # POS tagging & grammar rules
│       ├── predictor.py        # N-Gram language model
│       └── statistics.py       # Text statistics
│
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.jsx
        ├── index.css           # Global dark-theme styles
        ├── api.js              # API client
        ├── App.jsx             # Root layout with sidebar
        └── tools/
            ├── Tokenizer.jsx
            ├── WordMeaning.jsx
            ├── Grammar.jsx
            ├── Predictor.jsx
            └── Statistics.jsx
```

---

## Setup & Run

### 1. Backend

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Download NLTK data (run once)
python download_nltk.py

# Start the server
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The app will open at `http://localhost:5173`.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tokenize` | Tokenization & lemmatization |
| POST | `/api/word-meaning` | Word sense disambiguation |
| POST | `/api/grammar` | POS tagging & grammar check |
| POST | `/api/predict` | N-gram next-word prediction |
| POST | `/api/statistics` | Text statistics |
| GET  | `/api/health` | Health check |

---

## NLP Concepts Covered

### Word-Level Analysis
- Tokenization (sentence & word)
- Lemmatization (WordNet Lemmatizer)
- N-Grams (unigram, bigram, trigram)
- Corpus & Language Models
- Frequency distributions

### Syntax Analysis
- Part-of-Speech (POS) Tagging
- Basic rule-based grammar checking

### Semantic Analysis
- WordNet (synsets, definitions, synonyms)
- Semantic ambiguity
- Word senses
- Word Sense Disambiguation
- Lesk Algorithm

---

## Notes

- This is an educational mini-project, not a production system.
- The grammar checker uses simple heuristic rules — it is not comprehensive.
- The sentence predictor uses a small built-in corpus; predictions are limited to the vocabulary in that corpus.
- No external LLM APIs are used — all processing is done locally with NLTK.
