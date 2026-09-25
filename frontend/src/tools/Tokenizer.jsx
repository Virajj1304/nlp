import { useState } from "react";
import { api } from "../api";

const SAMPLE = "Natural language processing enables computers to understand human language. NLP techniques include tokenization, lemmatization, and part-of-speech tagging. These methods are fundamental to building intelligent text analysis systems.";

export default function Tokenizer() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAnalyze() {
    const input = text.trim();
    if (!input) { setError("Please enter some text."); return; }
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const data = await api.tokenize(input);
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="tool-header">
        <h1 className="tool-title">Tokenizer & Lemmatizer</h1>
        <p className="tool-description">
          Break text into sentences and words, then reduce each word to its base
          (lemma) form using NLTK's WordNet Lemmatizer.
        </p>
      </div>

      <div className="card">
        <div className="card-title">Input</div>
        <div className="input-group">
          <label>Enter text to analyze</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Type or paste text here…"
            rows={5}
          />
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <button className="btn btn-primary" onClick={handleAnalyze} disabled={loading}>
            {loading ? "Analyzing…" : "Analyze"}
          </button>
          <button
            className="btn"
            style={{ color: "var(--text-muted)", background: "var(--bg-secondary)", border: "1px solid var(--border)" }}
            onClick={() => setText(SAMPLE)}
          >
            Load Sample
          </button>
        </div>
      </div>

      {error && <div className="error-msg">{error}</div>}
      {loading && <div className="loading"><div className="spinner" /> Processing…</div>}

      {result && (
        <div className="results-section">
          {/* Stats */}
          <div className="card">
            <div className="card-title">Statistics</div>
            <div className="stat-grid">
              <div className="stat-item">
                <div className="stat-value">{result.sentence_count}</div>
                <div className="stat-label">Sentences</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{result.total_words}</div>
                <div className="stat-label">Total Words</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{result.unique_words}</div>
                <div className="stat-label">Unique Words</div>
              </div>
            </div>
          </div>

          {/* Sentences */}
          <div className="card">
            <div className="card-title">Sentences</div>
            {result.sentences.map((s, i) => (
              <p key={i} style={{ marginBottom: 6, fontSize: "0.88rem", color: "var(--text-secondary)" }}>
                <span style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)", marginRight: 8 }}>{i + 1}.</span>
                {s}
              </p>
            ))}
          </div>

          {/* Tokens */}
          <div className="card">
            <div className="card-title">Tokens</div>
            <div className="word-list">
              {result.tokens.map((t, i) => (
                <span key={i} className="tag">{t}</span>
              ))}
            </div>
          </div>

          {/* Lemmas */}
          <div className="card">
            <div className="card-title">Word → Lemma</div>
            <table className="data-table">
              <thead>
                <tr><th>Original</th><th>Lemma</th></tr>
              </thead>
              <tbody>
                {result.lemmas.map((l, i) => (
                  <tr key={i}>
                    <td>{l.original}</td>
                    <td style={{ color: l.original.toLowerCase() !== l.lemma ? "var(--accent)" : undefined }}>
                      {l.lemma}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="how-it-works">
        <h4>How it works</h4>
        <ul>
          <li><strong>Sentence segmentation</strong> — NLTK's <code>sent_tokenize</code> splits text at sentence boundaries.</li>
          <li><strong>Word tokenization</strong> — <code>word_tokenize</code> splits sentences into individual words and punctuation.</li>
          <li><strong>Lemmatization</strong> — WordNet Lemmatizer reduces inflected words (e.g., "running" → "running", "cats" → "cat") to their dictionary form.</li>
        </ul>
      </div>
    </div>
  );
}
