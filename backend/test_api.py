"""Quick test of all API endpoints."""
import json
import urllib.request

BASE = "http://localhost:8000"


def post(endpoint, data):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE}{endpoint}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())


def main():
    print("=== Health ===")
    with urllib.request.urlopen(f"{BASE}/api/health") as r:
        print(json.loads(r.read()))

    print("\n=== Tokenize ===")
    r = post("/api/tokenize", {"text": "Natural language processing is amazing."})
    print(json.dumps(r, indent=2)[:500])

    print("\n=== Word Meaning ===")
    r = post("/api/word-meaning", {
        "sentence": "I went to the bank to deposit money.",
        "target_word": "bank",
    })
    print(json.dumps(r, indent=2)[:500])

    print("\n=== Grammar ===")
    r = post("/api/grammar", {"text": "The boys is playing football."})
    print(json.dumps(r, indent=2)[:500])

    print("\n=== Predict ===")
    r = post("/api/predict", {"text": "I want to learn", "top_k": 5})
    print(json.dumps(r, indent=2)[:600])

    print("\n=== Statistics ===")
    r = post("/api/statistics", {"text": "AI is amazing. Machine learning works well. Deep learning is great."})
    print(json.dumps(r, indent=2)[:500])

    print("\n✓ All endpoints working!")


if __name__ == "__main__":
    main()
