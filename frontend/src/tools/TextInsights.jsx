import { useState } from "react";
import { api } from "../api";

const SAMPLE_TEXT = `Rahul, finish the backend by Wednesday and check the documentation before Thursday.
Hey Priya, submit the assignment before 5 PM tomorrow, it's urgent!
Also team, please deploy the release build on Friday morning ASAP.`;

export default function TextInsights() {
  const [text, setText] = useState(SAMPLE_TEXT);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleCompute(input = text) {
    if (!input.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.statistics(input.trim());
      setStats(data);
    } catch (err) {
      setError(err.message || "Failed to compute text statistics.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="tool-view">
      <div className="view-header">
        <div>
          <h1 className="view-title">Text Insights</h1>
          <p className="view-subtitle">
            Lightweight lexical statistics, word distributions, and common bigrams calculated from tokenized sentences.
          </p>
        </div>
      </div>

      {/* Input Card */}
      <div className="card input-card">
        <div className="input-toolbar">
          <span className="input-label">Text to Analyze</span>
          <button
            type="button"
            className="preset-btn"
            onClick={() => {
              setText(SAMPLE_TEXT);
              handleCompute(SAMPLE_TEXT);
            }}
          >
            Load Sample Text
          </button>
        </div>

        <textarea
          className="textarea font-mono"
          rows={4}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste or write text here to analyze statistics..."
        />

        <div className="card-actions">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => {
              setText("");
              setStats(null);
            }}
          >
            Clear
          </button>
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => handleCompute()}
            disabled={loading || !text.trim()}
          >
            {loading ? (
              <>
                <span className="spinner-sm" />
                Computing Stats...
              </>
            ) : (
              "Compute Insights"
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <span className="alert-icon">!</span>
          <div className="alert-content">
            <strong>Error:</strong> {error}
          </div>
        </div>
      )}

      {/* Stats Display */}
      {stats && (
        <div className="stats-results">
          {/* Top Metric Cards */}
          <div className="metric-cards-grid">
            <div className="metric-card">
              <span className="metric-number font-mono">{stats.word_count}</span>
              <span className="metric-label">Word Count</span>
            </div>
            <div className="metric-card">
              <span className="metric-number font-mono">{stats.sentence_count}</span>
              <span className="metric-label">Sentence Count</span>
            </div>
            <div className="metric-card">
              <span className="metric-number font-mono">{stats.unique_words}</span>
              <span className="metric-label">Unique Words</span>
            </div>
            <div className="metric-card">
              <span className="metric-number font-mono">{stats.lexical_diversity}%</span>
              <span className="metric-label">Lexical Diversity (TTR)</span>
            </div>
            <div className="metric-card">
              <span className="metric-number font-mono">{stats.average_word_length}</span>
              <span className="metric-label">Avg Word Length</span>
            </div>
          </div>

          <div className="stats-dual-grid">
            {/* Frequent Words Table */}
            <div className="card table-card">
              <h3 className="section-title">Most Frequent Words</h3>
              {stats.most_frequent_words.length === 0 ? (
                <p className="text-muted">No words available</p>
              ) : (
                <table className="stats-table">
                  <thead>
                    <tr>
                      <th>Word</th>
                      <th>Occurrences</th>
                      <th>Share</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.most_frequent_words.map((item, idx) => (
                      <tr key={idx}>
                        <td className="font-mono font-bold">{item.word}</td>
                        <td className="font-mono">{item.count}</td>
                        <td className="prob-bar-cell">
                          <div className="prob-bar-bg">
                            <div
                              className="prob-bar-fill"
                              style={{ width: `${item.percentage * 2}%` }}
                            />
                          </div>
                          <span className="prob-bar-label font-mono">
                            {item.percentage}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>

            {/* Common Bigrams */}
            <div className="card table-card">
              <h3 className="section-title">Common Bigrams</h3>
              {stats.common_bigrams.length === 0 ? (
                <p className="text-muted">No bigrams found (need at least 2 words)</p>
              ) : (
                <table className="stats-table">
                  <thead>
                    <tr>
                      <th>Bigram Phrase</th>
                      <th>Frequency</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.common_bigrams.map((item, idx) => (
                      <tr key={idx}>
                        <td className="font-mono text-highlight">{item.bigram}</td>
                        <td className="font-mono">{item.count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
