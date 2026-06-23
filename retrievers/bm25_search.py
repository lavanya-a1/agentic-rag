import json
from rank_bm25 import BM25Okapi

# ===========================
# Load Dataset
# ===========================

DATASET_PATH = "json/master_dataset_enriched.json"

with open(DATASET_PATH, "r", encoding="utf-8") as f:
    dataset = json.load(f)

# ===========================
# Tokenize
# ===========================

corpus = []

for record in dataset:

    corpus.append(
        record["document_text"].lower().split()
    )

bm25 = BM25Okapi(corpus)

# ===========================
# Search Function
# ===========================

def bm25_search(query, top_k=5):

    tokens = query.lower().split()

    scores = bm25.get_scores(tokens)

    ranked = sorted(
        zip(scores, dataset),
        key=lambda x: x[0],
        reverse=True
    )

    results = []

    for score, doc in ranked[:top_k]:

        results.append({

            "id": str(doc["id"]),

            "document": doc["document_text"],

            "metadata": {

                "section": doc["section"],

                "team": doc["team"],

                "player": doc["player"],

                "venue": doc["venue"]

            },

            "score": float(score)

        })

    return results


# ===========================
# Test
# ===========================

