import { useState } from "react";
import { api } from "../api";

const PRESETS = [
  {
    label: "Backend & Docs",
    text: "Rahul, finish the backend by Wednesday and check the documentation before Thursday.",
  },
  {
    label: "Urgent College Submission",
    text: "Hey Priya, submit the assignment before 5 PM tomorrow, it's urgent! Also team, please deploy the release build on Friday morning ASAP.",
  },
  {
    label: "PR Review",
    text: "Can someone review the pull request by tonight? Priority: high",
  },
  {
    label: "Meeting Notes",
    text: "Meeting notes:\n1. Prepare the presentation slides for the client meeting by Monday.\n2. Schedule a sync with the design team.\n3. Send the weekly project report by EOD.",
  },
];

export default function TaskExtractor() {
  const [input, setInput] = useState(PRESETS[0].text);
  const [tasks, setTasks] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedNlp, setExpandedNlp] = useState({});
  const [copiedId, setCopiedId] = useState(null);

  async function handleExtract(textToAnalyze = input) {
    if (!textToAnalyze.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.extractTasks(textToAnalyze.trim());
      setTasks(data.tasks || []);
    } catch (err) {
      setError(err.message || "Failed to extract tasks. Check backend connection.");
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      handleExtract();
    }
  }

  function toggleNlp(idx) {
    setExpandedNlp((prev) => ({
      ...prev,
      [idx]: !prev[idx],
    }));
  }

  function copyTask(task, idx) {
    const text = `[ ] ${task.title}\nAssigned: ${task.assignee}\nDeadline: ${task.deadline}\nPriority: ${task.priority}`;
    navigator.clipboard.writeText(text);
    setCopiedId(idx);
    setTimeout(() => setCopiedId(null), 1800);
  }

  return (
    <div className="tool-view">
      <div className="view-header">
        <div>
          <h1 className="view-title">Task Extractor</h1>
          <p className="view-subtitle">
            Parse messy everyday messages and emails into clean, actionable tasks using classical NLP rules, POS tagging, and lemmatization.
          </p>
        </div>
      </div>

      {/* Input Surface */}
      <div className="card input-card">
        <div className="input-toolbar">
          <span className="input-label">Message / Notes Input</span>
          <div className="presets-group">
            <span className="presets-label">Examples:</span>
            {PRESETS.map((preset, i) => (
              <button
                key={i}
                type="button"
                className="preset-btn"
                onClick={() => {
                  setInput(preset.text);
                  handleExtract(preset.text);
                }}
              >
                {preset.label}
              </button>
            ))}
          </div>
        </div>

        <textarea
          className="textarea"
          rows={4}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Paste messy message (e.g., 'Rahul, finish the backend by Wednesday and check the documentation before Thursday.')"
        />

        <div className="card-actions">
          <div className="shortcut-hint">
            <span>Press</span> <kbd>Ctrl</kbd> + <kbd>Enter</kbd> <span>to analyze</span>
          </div>

          <div className="btn-group">
            {input && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => {
                  setInput("");
                  setTasks(null);
                }}
              >
                Clear
              </button>
            )}
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => handleExtract()}
              disabled={loading || !input.trim()}
            >
              {loading ? (
                <>
                  <span className="spinner-sm" />
                  Analyzing NLP...
                </>
              ) : (
                "Extract Tasks"
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="alert alert-error">
          <span className="alert-icon">!</span>
          <div className="alert-content">
            <strong>Error:</strong> {error}
          </div>
        </div>
      )}

      {/* Loading state skeleton */}
      {loading && (
        <div className="task-results">
          <div className="skeleton-header" />
          <div className="task-grid">
            <div className="task-card skeleton-card" />
            <div className="task-card skeleton-card" />
          </div>
        </div>
      )}

      {/* Empty state */}
      {!loading && tasks === null && !error && (
        <div className="empty-state">
          <div className="empty-icon">✓</div>
          <h3>Ready to extract tasks</h3>
          <p>
            Paste an unstructured chat message, email, or meeting note above and click <strong>Extract Tasks</strong>.
          </p>
        </div>
      )}

      {/* Zero tasks found state */}
      {!loading && tasks !== null && tasks.length === 0 && !error && (
        <div className="empty-state">
          <div className="empty-icon">∅</div>
          <h3>No actionable tasks detected</h3>
          <p>
            The message did not contain recognizable action verbs or task directives. Try phrasing with an imperative verb like <em>finish</em>, <em>submit</em>, <em>review</em>, or <em>prepare</em>.
          </p>
        </div>
      )}

      {/* Extracted Tasks Output */}
      {!loading && tasks && tasks.length > 0 && (
        <div className="task-results">
          <div className="results-header">
            <div className="results-count">
              <span className="badge count-badge">{tasks.length}</span>
              <span>Actionable {tasks.length === 1 ? "Task" : "Tasks"} Extracted</span>
            </div>
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={() => {
                const markdown = tasks
                  .map(
                    (t) =>
                      `## ${t.title}\n- **Assignee:** ${t.assignee}\n- **Deadline:** ${t.deadline}\n- **Priority:** ${t.priority}\n- **Context:** ${t.context}`
                  )
                  .join("\n\n");
                navigator.clipboard.writeText(markdown);
              }}
            >
              Copy All Markdown
            </button>
          </div>

          <div className="task-grid">
            {tasks.map((task, idx) => {
              const isNlpOpen = !!expandedNlp[idx];
              const priorityClass =
                task.priority === "High"
                  ? "priority-high"
                  : task.priority === "Low"
                  ? "priority-low"
                  : "priority-normal";

              return (
                <div key={idx} className="task-card">
                  <div className="task-card-header">
                    <div className="task-title-group">
                      <div className="task-checkbox" onClick={() => copyTask(task, idx)} title="Click to copy task">
                        {copiedId === idx ? "✓" : ""}
                      </div>
                      <h3 className="task-title">{task.title}</h3>
                    </div>
                    <div className="task-badges">
                      <span className={`badge ${priorityClass}`}>
                        {task.priority}
                      </span>
                      <span className="badge badge-context">
                        {task.context}
                      </span>
                    </div>
                  </div>

                  <div className="task-meta-grid">
                    <div className="task-meta-item">
                      <span className="meta-label">Assigned to</span>
                      <span className="meta-value">
                        <span className="avatar-initial">
                          {task.assignee.charAt(0).toUpperCase()}
                        </span>
                        {task.assignee}
                      </span>
                    </div>

                    <div className="task-meta-item">
                      <span className="meta-label">Deadline</span>
                      <span className="meta-value meta-deadline">
                        {task.deadline}
                      </span>
                    </div>

                    <div className="task-meta-item">
                      <span className="meta-label">Action</span>
                      <span className="meta-value font-mono">
                        {task.action}
                      </span>
                    </div>

                    <div className="task-meta-item">
                      <span className="meta-label">Target Object</span>
                      <span className="meta-value">
                        {task.task_object}
                      </span>
                    </div>
                  </div>

                  {/* Expandable "How was this extracted?" NLP details */}
                  <div className="nlp-accordion">
                    <button
                      type="button"
                      className="nlp-toggle-btn"
                      onClick={() => toggleNlp(idx)}
                    >
                      <span>{isNlpOpen ? "▾" : "▸"}</span>
                      <span>How was this extracted? (NLP Breakdown)</span>
                    </button>

                    {isNlpOpen && (
                      <div className="nlp-details">
                        <div className="nlp-detail-row">
                          <span className="nlp-label">Source Clause:</span>
                          <span className="nlp-code-inline font-mono">
                            "{task.nlp_breakdown.clause_text}"
                          </span>
                        </div>

                        <div className="nlp-detail-row">
                          <span className="nlp-label">POS Tagging:</span>
                          <div className="pos-tags-wrap">
                            {task.nlp_breakdown.tokens.map((tok, tIdx) => (
                              <span key={tIdx} className="pos-pill">
                                <span className="pos-word">{tok.token}</span>
                                <span className="pos-tag">{tok.tag}</span>
                              </span>
                            ))}
                          </div>
                        </div>

                        <div className="nlp-detail-row">
                          <span className="nlp-label">Lemmatization:</span>
                          <span className="nlp-code-inline font-mono">
                            {task.nlp_breakdown.action_verb} → {task.nlp_breakdown.action_lemma} (Verb, base form)
                          </span>
                        </div>

                        <div className="nlp-steps-list">
                          <span className="nlp-label">Pipeline Steps:</span>
                          <ul>
                            {task.nlp_breakdown.steps.map((st, sIdx) => (
                              <li key={sIdx}>{st}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
