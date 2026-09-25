"""
TaskLens — Backend Test Suite
===============================
Directly tests all FastAPI endpoint handlers and services:
  1. Health check
  2. Task Extractor (/api/extract-tasks)
  3. Word Meaning Disambiguation (/api/word-meaning)
  4. Next-Word Prediction (/api/predict)
  5. Text Insights Statistics (/api/statistics)
"""

from main import (
    health,
    extract_tasks_endpoint,
    word_meaning_endpoint,
    predict_endpoint,
    statistics_endpoint,
    TextInput,
    WordMeaningInput,
    PredictInput,
)


def test_health():
    res = health()
    assert res["status"] == "ok"
    assert res["app"] == "TaskLens"
    print("[PASS] Health endpoint OK")


def test_task_extractor():
    sample = "Rahul, finish the backend by Wednesday and check the documentation before Thursday."
    res = extract_tasks_endpoint(TextInput(text=sample))
    assert res["count"] == 2
    tasks = res["tasks"]
    assert tasks[0]["action"] == "Finish"
    assert tasks[0]["assignee"] == "Rahul"
    assert tasks[0]["deadline"] == "Wednesday"
    assert tasks[1]["action"] == "Check"
    assert tasks[1]["assignee"] == "Rahul"
    assert tasks[1]["deadline"] == "Thursday"
    print(f"[PASS] Task Extractor OK ({len(tasks)} tasks extracted: {[t['title'] for t in tasks]})")


def test_word_meaning():
    res = word_meaning_endpoint(WordMeaningInput(
        sentence="I went to the bank to deposit money.",
        target_word="bank"
    ))
    assert res["found"] is True
    assert "financial" in res["definition"].lower() or "depository" in res["detected_sense"]
    assert len(res["alternative_senses"]) > 0
    print(f"[PASS] Word Meaning OK (Detected: {res['detected_sense']})")


def test_predict():
    res = predict_endpoint(PredictInput(
        text="Please send the",
        top_k=5
    ))
    assert res["model"] == "Trigram Model"
    words = [p["word"] for p in res["predictions"]]
    assert "report" in words or "document" in words or "presentation" in words or "file" in words
    print(f"[PASS] Smart Completion Predictor OK (Top suggestions: {words})")


def test_statistics():
    res = statistics_endpoint(TextInput(
        text="Rahul will finish the project. The project is critical for the college submission."
    ))
    assert res["word_count"] > 0
    assert res["sentence_count"] == 2
    print(f"[PASS] Text Insights OK (Words: {res['word_count']}, Sentences: {res['sentence_count']})")


if __name__ == "__main__":
    print("Testing TaskLens Backend Endpoints...")
    test_health()
    test_task_extractor()
    test_word_meaning()
    test_predict()
    test_statistics()
    print("\nAll TaskLens backend tests passed successfully!")
