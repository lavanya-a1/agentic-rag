from typing import List

from graph.state import IPLState
from retrievers.hybrid_search import hybrid_search
from utils import query_rewriter


class BowlingStatsNode:
    """Uses existing retriever to fetch bowling-related records and stores them in state.bowling_context."""

    def __init__(self, top_k: int = 5):
        self.top_k = top_k

    def run(self, state: IPLState) -> IPLState:

        query = state.get("user_query", "")

        # Prefer a rewritten, retrieval-friendly query
        #try:
            #rewritten = query_rewriter.rewrite_query(query)
        #except Exception:
            #rewritten = query
        rewritten = query
        # Use existing hybrid search
        results = hybrid_search(rewritten, top_k=self.top_k)

        # Filter to bowling-related records using metadata (no hardcoded data)
        bowling_docs: List[dict] = []

        for r in results:
            meta = r.get("metadata") or {}
            # Accept records where `section` explicitly marks bowling
            if str(meta.get("section", "")).lower() == "bowling":
                bowling_docs.append(r)

        # Save to state
        state["bowling_context"] = bowling_docs

        return state


if __name__ == "__main__":
    s = IPLState()
    s["user_query"] = "Who took the most wickets in IPL 2024?"
    n = BowlingStatsNode()
    print(n.run(s))
