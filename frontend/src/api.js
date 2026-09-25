const API_BASE = "http://localhost:8000";

async function request(endpoint, body) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

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
  tokenize:     (text)                   => request("/api/tokenize",      { text }),
  wordMeaning:  (sentence, target_word)  => request("/api/word-meaning",  { sentence, target_word }),
  grammar:      (text)                   => request("/api/grammar",       { text }),
  predict:      (text, top_k = 5)        => request("/api/predict",       { text, top_k }),
  statistics:   (text)                   => request("/api/statistics",     { text }),
};
