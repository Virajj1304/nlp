import { useState } from "react";
import { api } from "../api";

const SAMPLES = [
  "I want to learn",
  "Machine learning is",
  "Natural language",
  "Students should",
  "The development of",
];

export default function Predictor() {
  const [text, setText] = useState("");
  const [topK, setTopK] = useState(5);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handlePredict() {
    if (!text.trim()) { setError("Please enter some words."); return; }
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const data = await api.predict(text.trim(), topK);
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const maxProb = result?.predictions?.length
    ? Math.max(...result.predictions.map((p) => p.probability))
    : 1;

  return (
    <div>
      <div className="tool-header">
        <h1 className="tool-title">Smart Sentence Predictor</h1>
        <p className="tool-description">
          Predict the next word using a statistical N-gram language model built
          from a curated corpus. No LLM — just trigram → bigram → unigram
          fallback with Laplace smoothing.
        </p>
      </div>

      <div className="card">
        <div className="card-title">Input</div>
        <div className="input-group">
          <label>Enter the beginning of a sentence</label>
          <input
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="e.g., I want to learn"
            onKeyDown={(e) => e.key === "Enter" && handlePredict()}
          />
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap", marginBottom: 14 }}>
          <label style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>
            Top predictions:
          </label>
          <select value={topK} onChange={(e) => setTopK(Number(e.target.value))}>
            <option value={3}>Top 3</option>
            <option value={5}>Top 5</option>
            <option value={10}>Top 10</option>
          </select>
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
          <button className="btn btn-primary" onClick={handlePredict} disabled={loading}>
            {loading ? "Predicting…" : "Predict Next Word"}
          </button>
          <span style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>Samples →</span>
          {SAMPLES.map((s, i) => (
            <button
              key={i}
              className="btn"
              style={{ color: "var(--text-muted)", background: "var(--bg-secondary)", border: "1px solid var(--border)", padding: "6px 12px", fontSize: "0.78rem" }}
              onClick={() => { setText(s); setResult(null); }}
            >
              "{s}"
            </button>
          ))}
        </div>
      </div>

      {error && <div className="error-msg">{error}</div>}
      {loading && <div className="loading"><div className="spinner" /> Predicting…</div>}

      {result && (
        <div className="results-section">
          {/* Model info */}
          <div className="card">
            <div className="card-title">Prediction Info</div>
            <div className="stat-grid">
              <div className="stat-item">
                <div className="stat-value" style={{ fontSize: "1rem", textTransform: "capitalize" }}>{result.model || "—"}</div>
                <div className="stat-label">Model Used</div>
              </div>
              <div className="stat-item">
                <div className="stat-value" style={{ fontSize: "0.9rem" }}>{result.context_used || "—"}</div>
                <div className="stat-label">Context</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{result.predictions?.length || 0}</div>
                <div className="stat-label">Predictions</div>
              </div>
            </div>
          </div>

          {/* Predictions */}
          {result.predictions?.length > 0 ? (
            <div className="card">
              <div className="card-title">Predicted Next Words</div>
              {result.predictions.map((p, i) => (
                <div key={i} className="prediction-item">
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.78rem", color: "var(--text-muted)", width: 20 }}>
                    {i + 1}.
                  </span>
                  <span className="prediction-word">{p.word}</span>
                  <div className="prediction-bar-wrapper">
                    <div
                      className="prediction-bar"
                      style={{ width: `${(p.probability / maxProb) * 100}%` }}
                    />
                  </div>
                  <span className="prediction-prob">
                    {(p.probability * 100).toFixed(2)}%
                  </span>
                  <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.72rem", color: "var(--text-muted)" }}>
                    (×{p.count})
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="card">
              <p style={{ color: "var(--text-secondary)" }}>{result.message || "No predictions available for this context."}</p>
            </div>
          )}

          {/* Corpus stats */}
          {result.corpus_stats && (
            <div className="card">
              <div className="card-title">Corpus Statistics</div>
              <div className="stat-grid">
                <div className="stat-item">
                  <div className="stat-value">{result.corpus_stats.total_sentences}</div>
                  <div className="stat-label">Sentences</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{result.corpus_stats.vocabulary_size}</div>
                  <div className="stat-label">Vocabulary</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{result.corpus_stats.total_tokens}</div>
                  <div className="stat-label">Total Tokens</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{result.corpus_stats.unique_bigrams}</div>
                  <div className="stat-label">Bigrams</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{result.corpus_stats.unique_trigrams}</div>
                  <div className="stat-label">Trigrams</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="how-it-works">
        <h4>How it works</h4>
        <ul>
          <li><strong>N-Gram Model</strong> — Counts sequences of 1 (unigram), 2 (bigram), and 3 (trigram) consecutive words from the training corpus.</li>
          <li><strong>Prediction</strong> — Given the last 1–2 words, the model looks up which words most frequently follow that context.</li>
          <li><strong>Laplace Smoothing</strong> — Adds 1 to every count so unseen words get a small probability instead of zero.</li>
          <li><strong>Fallback</strong> — If trigram context isn't found, falls back to bigram, then unigram.</li>
        </ul>
      </div>
    </div>
  );
}
