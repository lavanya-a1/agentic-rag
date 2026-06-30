from typing import List

from graph.state import IPLState
from retrievers.hybrid_search import hybrid_search

from utils.debug import debug_state


class TrendNode:
    """Fetch trend-related documents using the existing hybrid retriever.

    Requirements:
    - Use the user's original query (no rewrite)
    - Filter results where metadata['section'] == 'trend'
    - Save results to state['trend_context']
    - Do not hardcode any team names, years, or seasons
    """

    def __init__(self, top_k: int = 5):
        self.top_k = top_k

    def run(self, state: IPLState) -> IPLState:

        query = state.get("user_query", "")

        # Fetch a wider candidate pool so that trend docs are not missed due
        # to low overall rank.  The section filter is applied after retrieval,
        # so we need enough candidates to guarantee trend-section hits.
        fetch_k = max(50, self.top_k * 10)
        results = hybrid_search(query, top_k=fetch_k)

        trend_docs: List[dict] = []

        for r in results:
            meta = r.get("metadata") or {}
            if str(meta.get("section", "")).lower() == "trend":
                trend_docs.append(r)

        # Return only the top_k best trend docs (already ranked by rrf_score)
        state["trend_context"] = trend_docs[: self.top_k]

        return state



if __name__ == "__main__":
    s = IPLState()
    s["user_query"] = "What is the recent batting trend for CSK in 2024?"
    n = TrendNode()
    print(n.run(s))
