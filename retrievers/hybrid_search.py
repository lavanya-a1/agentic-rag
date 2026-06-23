from retrievers.semantic_search import semantic_search
from retrievers.bm25_search import bm25_search

# ==========================================
# Reciprocal Rank Fusion
# ==========================================

def rrf_fusion(semantic_results,
               bm25_results,
               k=60):

    fused_scores = {}

    docs = {}

    # Semantic ranking
    for rank, item in enumerate(semantic_results):

        doc_id = item["id"]

        fused_scores[doc_id] = fused_scores.get(doc_id, 0) + 1 / (k + rank + 1)

        docs[doc_id] = item

    # BM25 ranking
    for rank, item in enumerate(bm25_results):

        doc_id = item["id"]

        fused_scores[doc_id] = fused_scores.get(doc_id, 0) + 1 / (k + rank + 1)

        docs[doc_id] = item

    ranked = sorted(
        fused_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    final_results = []

    for doc_id, score in ranked:

        item = docs[doc_id]

        item["rrf_score"] = score

        final_results.append(item)

    return final_results


# ==========================================
# Hybrid Search
# ==========================================

def hybrid_search(query, top_k=5):

    semantic_results = semantic_search(
        query,
        top_k
    )

    bm25_results = bm25_search(
        query,
        top_k
    )

    results = rrf_fusion(
        semantic_results,
        bm25_results
    )

    return results[:top_k]


# ==========================================
# Test
# ==========================================

