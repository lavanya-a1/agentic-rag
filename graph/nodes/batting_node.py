from typing import List

from graph.state import IPLState
from retrievers.hybrid_search import hybrid_search
from utils.debug import debug_state

class BattingStatsNode:
    """Uses existing retriever to fetch batting-related records and stores them in state.batting_context."""

    def __init__(self, top_k: int = 5):
        self.top_k = top_k

    def run(self, state: IPLState) -> IPLState:

        query = state.get("user_query", "")

        # Prefer a rewritten, retrieval-friendly query
        #try:
        #    rewritten = query_rewriter.rewrite_query(query)
        #except Exception:
        #    rewritten = query

        rewritten = query

        # Use existing hybrid search
        results = hybrid_search(rewritten, top_k=self.top_k)

        # Filter to batting-related records using metadata (no hardcoded data)
        batting_docs: List[dict] = []

        for r in results:
            meta = r.get("metadata") or {}
            # Accept records where `section` explicitly marks batting
            if str(meta.get("section", "")).lower() == "batting":
                batting_docs.append(r)

        # Save to state
        state["batting_context"] = batting_docs
        print("QUERY:", state["user_query"])

        for doc in batting_docs:
            print(doc)
        

        return state


if __name__ == "__main__":
    s = IPLState()
    s["user_query"] = "Who scored most runs last season?"
    n = BattingStatsNode()
    print(n.run(s))
