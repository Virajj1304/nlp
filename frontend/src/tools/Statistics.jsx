import { useState } from "react";
import { api } from "../api";

const SAMPLE = `Artificial intelligence is transforming the world of technology. Machine learning algorithms can learn from data and make predictions. Natural language processing helps computers understand human language. Deep learning uses neural networks to solve complex problems. Python is a popular programming language for data science and machine learning.`;

export default function Statistics() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleCompute() {
    if (!text.trim()) { setError("Please enter some text."); return; }
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const data = await api.statistics(text.trim());
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
        <h1 className="tool-title">Text Statistics</h1>
        <p className="tool-description">
          Compute word counts, sentence counts, unique words, average word length,
          most frequent words, and common bigrams from any text.
        </p>
      </div>

      <div className="card">
        <div className="card-title">Input</div>
        <div className="input-group">
          <label>Enter or paste text</label>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste a paragraph or more…"
            rows={6}
          />
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <button className="btn btn-primary" onClick={handleCompute} disabled={loading}>
            {loading ? "Computing…" : "Compute Statistics"}
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
      {loading && <div className="loading"><div className="spinner" /> Computing…</div>}

      {result && (
        <div className="results-section">
          {/* Core stats */}
          <div className="card">
            <div className="card-title">Overview</div>
            <div className="stat-grid">
              <div className="stat-item">
                <div className="stat-value">{result.word_count}</div>
                <div className="stat-label">Words</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{result.sentence_count}</div>
                <div className="stat-label">Sentences</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{result.unique_words}</div>
                <div className="stat-label">Unique Words</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{result.average_word_length}</div>
                <div className="stat-label">Avg Word Length</div>
              </div>
            </div>
          </div>

          {/* Frequent words */}
          {result.most_frequent_words?.length > 0 && (
            <div className="card">
              <div className="card-title">Most Frequent Words</div>
              <table className="data-table">
                <thead>
                  <tr><th>#</th><th>Word</th><th>Count</th></tr>
                </thead>
                <tbody>
                  {result.most_frequent_words.map((w, i) => (
                    <tr key={i}>
                      <td style={{ color: "var(--text-muted)" }}>{i + 1}</td>
                      <td style={{ fontWeight: 600 }}>{w.word}</td>
                      <td>
                        <span className="tag tag-accent">{w.count}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Common bigrams */}
          {result.common_bigrams?.length > 0 && (
            <div className="card">
              <div className="card-title">Common Bigrams</div>
              <table className="data-table">
                <thead>
                  <tr><th>#</th><th>Bigram</th><th>Count</th></tr>
                </thead>
                <tbody>
                  {result.common_bigrams.map((b, i) => (
                    <tr key={i}>
                      <td style={{ color: "var(--text-muted)" }}>{i + 1}</td>
                      <td style={{ fontFamily: "var(--font-mono)" }}>{b.bigram}</td>
                      <td>
                        <span className="tag tag-accent">{b.count}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      <div className="how-it-works">
        <h4>How it works</h4>
        <ul>
          <li><strong>Tokenization</strong> — NLTK splits the input into words and sentences.</li>
          <li><strong>Word Frequency</strong> — A Counter tallies how often each word appears.</li>
          <li><strong>Bigrams</strong> — Consecutive word pairs are counted to reveal common two-word patterns.</li>
          <li><strong>Average Word Length</strong> — Sum of all word lengths divided by total word count.</li>
        </ul>
      </div>
    </div>
  );
}
