import { useState } from "react";
import { api } from "../api";

const SAMPLES = [
  "The boys is playing football in the park.",
  "She have a apple in her bag.",
  "They was running very fast yesterday.",
  "The cat sat on the mat and purred softly.",
  "He do not knows the answer to the question.",
];

export default function Grammar() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAnalyze() {
    if (!text.trim()) { setError("Please enter a sentence."); return; }
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const data = await api.grammar(text.trim());
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
        <h1 className="tool-title">Grammar & Sentence Analyzer</h1>
        <p className="tool-description">
          Analyze sentence structure with POS tagging, lemmatization, and basic
          rule-based grammar checks. This is a simple educational analyzer, not a
          full grammar checker.
        </p>
      </div>

      <div className="card">
        <div className="card-title">Input</div>
        <div className="input-group">
          <label>Enter a sentence</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Type a sentence…"
            rows={3}
          />
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
          <button className="btn btn-primary" onClick={handleAnalyze} disabled={loading}>
            {loading ? "Analyzing…" : "Analyze Grammar"}
          </button>
          <span style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>Samples →</span>
          {SAMPLES.map((s, i) => (
            <button
              key={i}
              className="btn"
              style={{ color: "var(--text-muted)", background: "var(--bg-secondary)", border: "1px solid var(--border)", padding: "6px 12px", fontSize: "0.78rem" }}
              onClick={() => { setText(s); setResult(null); }}
            >
              #{i + 1}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="error-msg">{error}</div>}
      {loading && <div className="loading"><div className="spinner" /> Analyzing…</div>}

      {result && (
        <div className="results-section">
          {/* Suggestions */}
          {result.suggestions.length > 0 && (
            <div className="card">
              <div className="card-title">Grammar Suggestions</div>
              {result.suggestions.map((s, i) => (
                <div key={i} className="suggestion">
                  <div className="suggestion-type">{s.type}</div>
                  <div className="suggestion-msg">{s.message}</div>
                </div>
              ))}
            </div>
          )}

          {result.suggestions.length === 0 && (
            <div className="card" style={{ borderLeft: "3px solid var(--success)" }}>
              <p style={{ color: "var(--success)", fontSize: "0.9rem" }}>
                ✓ No basic grammar issues detected.
              </p>
            </div>
          )}

          {/* POS Table */}
          <div className="card">
            <div className="card-title">Word Analysis</div>
            <div style={{ overflowX: "auto" }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Word</th>
                    <th>POS Tag</th>
                    <th>Description</th>
                    <th>Lemma</th>
                  </tr>
                </thead>
                <tbody>
                  {result.word_analysis.map((w, i) => (
                    <tr key={i}>
                      <td style={{ fontWeight: 600 }}>{w.word}</td>
                      <td><span className="tag tag-accent">{w.pos_tag}</span></td>
                      <td style={{ color: "var(--text-secondary)", fontSize: "0.82rem" }}>{w.pos_description}</td>
                      <td style={{ fontFamily: "var(--font-mono)", color: w.word.toLowerCase() !== w.lemma ? "var(--accent)" : undefined }}>
                        {w.lemma}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Word categories */}
          <div className="card">
            <div className="card-title">Word Categories</div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 16 }}>
              <div>
                <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.04em", marginBottom: 6 }}>Nouns</p>
                <div className="word-list">
                  {result.nouns.length ? result.nouns.map((w, i) => <span key={i} className="tag">{w}</span>) : <span className="note">None found</span>}
                </div>
              </div>
              <div>
                <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.04em", marginBottom: 6 }}>Verbs</p>
                <div className="word-list">
                  {result.verbs.length ? result.verbs.map((w, i) => <span key={i} className="tag">{w}</span>) : <span className="note">None found</span>}
                </div>
              </div>
              <div>
                <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.04em", marginBottom: 6 }}>Adjectives</p>
                <div className="word-list">
                  {result.adjectives.length ? result.adjectives.map((w, i) => <span key={i} className="tag">{w}</span>) : <span className="note">None found</span>}
                </div>
              </div>
              <div>
                <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.04em", marginBottom: 6 }}>Adverbs</p>
                <div className="word-list">
                  {result.adverbs.length ? result.adverbs.map((w, i) => <span key={i} className="tag">{w}</span>) : <span className="note">None found</span>}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="how-it-works">
        <h4>How it works</h4>
        <ul>
          <li><strong>POS Tagging</strong> — NLTK's averaged perceptron tagger assigns a part-of-speech tag (noun, verb, adjective, etc.) to each word.</li>
          <li><strong>Lemmatization</strong> — WordNet Lemmatizer reduces each word to its base form, using the POS tag for accuracy.</li>
          <li><strong>Grammar Rules</strong> — Simple heuristics check for common errors: subject-verb agreement with "be" verbs, article usage (a/an), and double negatives.</li>
        </ul>
        <p style={{ marginTop: 8, fontStyle: "italic" }}>
          Note: This is a basic rule-based analyzer. It catches common patterns but is not a comprehensive grammar checker.
        </p>
      </div>
    </div>
  );
}
