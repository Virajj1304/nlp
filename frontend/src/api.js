/**
 * TaskLens — API Client
 * Connects React frontend directly to FastAPI backend
 */

// Use environment variable in production (e.g., Render URL) or fallback to local backend
export const API_BASE = (
  import.meta.env.VITE_API_URL || "http://localhost:8000"
).replace(/\/+$/, "");

async function request(endpoint, body = null, method = "POST") {
  const options = {
    method,
    headers: { "Content-Type": "application/json" },
  };

  if (body && method !== "GET") {
    options.body = JSON.stringify(body);
  }

  let res;
  try {
    res = await fetch(`${API_BASE}${endpoint}`, options);
  } catch (err) {
    throw new Error(
      `Network error connecting to backend (${API_BASE}). If on Render free tier, it may be waking up from sleep (~30-45s).`
    );
  }

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Server error (${res.status}): ${text}`);
  }

  const data = await res.json();

  if (data.error) {
    throw new Error(data.error);
  }

  return data;
}

export const api = {
  extractTasks: (text) => request("/api/extract-tasks", { text }),
  wordMeaning: (sentence, target_word) => request("/api/word-meaning", { sentence, target_word }),
  predict: (text, top_k = 5) => request("/api/predict", { text, top_k }),
  statistics: (text) => request("/api/statistics", { text }),
  checkHealth: async () => {
    try {
      const res = await fetch(`${API_BASE}/api/health`);
      return res.ok;
    } catch {
      return false;
    }
  },
};
