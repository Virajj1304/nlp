# TaskLens

> **Productivity Web App Powered by Classical Natural Language Processing**  
> Converts messy everyday messages, emails, meeting notes, and college/project messages into clear actionable tasks using traditional rule-based & statistical NLP.

---

## 📌 Project Overview

**TaskLens** is an NLP mini-project that demonstrates how classical computational linguistics (tokenization, POS tagging, lemmatization, rule-based information extraction, WordNet Word Sense Disambiguation via the Lesk algorithm, and N-gram statistical language modeling) can solve real-world productivity workflows.

> **Zero LLM Policy**: This project strictly uses **classical NLP** (NLTK + WordNet). There are **no** OpenAI, Gemini, Claude, or third-party generative LLM APIs, and **no** chatbots. All extractions and probabilities are computed deterministically and statistically from local algorithms and corpora.

---

## 🚀 Core Features

### 1. Task Extractor (Main Feature)
Converts unstructured chat messages and notes into structured task cards.
- **Example Input:**  
  `"Rahul, finish the backend by Wednesday and check the documentation before Thursday."`
- **Extracted Fields:**
  - **Action:** Base action verb (e.g., `Finish`, `Check`)
  - **Task / Object:** Direct object noun phrase (e.g., `the backend`, `the documentation`)
  - **Assignee:** Vocative / addressed individual or group (e.g., `Rahul`)
  - **Deadline:** Temporal prepositional phrase (e.g., `Wednesday`, `Thursday`)
  - **Priority:** Linguistic urgency classification (`High`, `Normal`, `Low`)
  - **Context:** Domain categorization (`Tech / Engineering`, `Academic / College`, `Operations / Admin`, etc.)
- **Classical NLP Pipeline:**
  - **Sentence Segmentation:** NLTK Punkt segmenter
  - **Word Tokenization:** Penn Treebank word tokenizer
  - **POS Tagging:** Averaged Perceptron Tagger (`NNP`, `VB`, `DT`, `NN`, `IN`)
  - **Lemmatization:** WordNet Lemmatizer (`pos='v'`)
  - **Information Extraction:** Rule-based grammar chunking and vocative addressing heuristics.
- **NLP Inspection:** Each task card includes an expandable *"How was this extracted?"* section displaying tokens, POS tags, lemmatization steps, and rule breakdowns.

### 2. Context-Aware Word Meaning
Disambiguates polysemous words based on sentence context using WordNet and the **Simplified Lesk Algorithm**.
- **Example Input:** `"I went to the bank to deposit money."` with target `"bank"`
- **Result:** Identifies `depository_financial_institution.n.01` with definition, synonyms, examples, and Lesk overlap score (`['deposit', 'money']`).
- **Contrast:** When passed `"The fisherman sat on the river bank..."`, it selects `bank.n.01` (slope beside a body of water).
- **Shows:** Detected meaning, full definition, WordNet synonyms, overlap keywords, and all alternative ranked senses.

### 3. Smart Sentence & Task Completion
Suggests candidate next words as the user types task prefixes.
- **Example Input:** `"Please send the"`
- **Suggestions:** `report`, `document`, `presentation`, `file`
- **NLP Model:** Statistical **Trigram Language Model** with **Laplace (Add-One) Smoothing**:
  $$P(w_3 \mid w_1, w_2) = \frac{\text{Count}(w_1, w_2, w_3) + 1}{\text{Count}(w_1, w_2) + |V|}$$
  with graceful fallback to **Bigram** and **Unigram** models when context is unseen.
- **Interactive UI:** Click any suggestion chip to append the word and instantly compute the next candidates.

### 4. Text Insights
Computes lightweight lexical metrics from raw text:
- Total word count & sentence count
- Unique words & Lexical Diversity (Type-Token Ratio)
- Average word length
- Top frequent words (frequency bars)
- Common bigram phrases

---

## 🛠 Tech Stack

- **Frontend:** React 19, Vite, Vanilla CSS (Modern Minimalist Linear/Notion dark aesthetic)
- **Backend:** Python 3.10+, FastAPI, Uvicorn, Pydantic
- **NLP Engine:** NLTK (Natural Language Toolkit), Princeton WordNet

---

## 📁 Repository Structure

```
nlp/
├── backend/
│   ├── main.py                     # FastAPI REST API routes
│   ├── requirements.txt            # Python dependencies (fastapi, uvicorn, nltk, pydantic)
│   ├── download_nltk.py            # One-time NLTK corpora downloader
│   ├── test_api.py                 # Automated backend test suite
│   └── services/
│       ├── task_extractor.py       # Task extraction via POS tags & IE rules
│       ├── word_meaning.py         # Word Sense Disambiguation (Lesk + WordNet)
│       ├── predictor.py            # Statistical N-Gram Language Model
│       └── statistics.py           # Text insights & lexical statistics
│
└── frontend/
    ├── index.html                  # HTML5 entry point with Inter & JetBrains Mono
    ├── package.json                # React + Vite dependencies
    ├── vite.config.js              # Vite bundler configuration
    └── src/
        ├── main.jsx                # React root mount
        ├── App.jsx                 # Main layout & navigation
        ├── index.css               # Notion/Linear dark theme stylesheet
        ├── api.js                  # Frontend API client
        └── tools/
            ├── TaskExtractor.jsx   # Task Extractor tool (default view)
            ├── WordMeaning.jsx     # Word Sense Disambiguation tool
            ├── SmartCompletion.jsx # Smart autocomplete tool
            └── TextInsights.jsx    # Text metrics & bigrams tool
```

---

## ⚡ Setup & Run Instructions

### 1. Prerequisites
- Python 3.10+ installed
- Node.js 18+ and npm installed

---

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Download required NLTK datasets (punkt, averaged_perceptron_tagger, wordnet, stopwords)
python download_nltk.py

# Run automated tests to verify NLP services
python test_api.py

# Start the FastAPI server
uvicorn main:app --reload --port 8000
```

The backend server will run at `http://localhost:8000`.  
Interactive Swagger API documentation is available at `http://localhost:8000/docs`.

---

### 3. Frontend Setup

In a new terminal window:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the Vite development server
npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 📡 API Specification

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| `POST` | `/api/extract-tasks` | Extracts structured task cards from text | `{"text": "Rahul, finish backend..."}` |
| `POST` | `/api/word-meaning` | Performs Lesk WSD on target word | `{"sentence": "...", "target_word": "..."}` |
| `POST` | `/api/predict` | Computes statistical N-gram predictions | `{"text": "Please send the", "top_k": 5}` |
| `POST` | `/api/statistics` | Computes word counts, TTR, and bigrams | `{"text": "..."}` |
| `GET`  | `/api/health` | Backend status & metadata check | _None_ |

---

## 🎨 UI Design Philosophy

- **Linear / Notion Minimalist Aesthetic:** Deep charcoal background (`#0c0d0e`), subtle borders (`#202428`), and crisp typography.
- **No AI Tropes:** Zero chatbots, zero pulsing neon gradients, zero robot illustrations.
- **Diagnostic Transparency:** NLP metrics and POS tags are accessible inside clean, collapsible diagnostics.
- **Responsive:** Optimized for desktop and mobile screens.

---

## 📄 License
MIT License. Created for college NLP mini-project demonstration.
