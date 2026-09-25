"""
Download all required NLTK data packages.
Run this once before starting the backend server.
"""

import nltk

packages = [
    "punkt",
    "punkt_tab",
    "averaged_perceptron_tagger",
    "averaged_perceptron_tagger_eng",
    "wordnet",
    "omw-1.4",
    "stopwords",
    "tagsets",
    "tagsets_json",
]

for pkg in packages:
    print(f"Downloading {pkg}...")
    nltk.download(pkg, quiet=False)

print("\nAll NLTK data downloaded successfully.")
