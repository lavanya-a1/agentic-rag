from typing import List

from graph.state import IPLState
from retrievers.hybrid_search import hybrid_search

from utils.debug import debug_state

class H2HNode:
    """Fetch head-to-head documents using the existing hybrid retriever.

    Requirements:
    - Use the user's original query (no rewrite)
    - Filter results where metadata['section'] == 'h2h'
    - Save results to state['h2h_context']
    - Do not hardcode any team names
    """

    def __init__(self, top_k: int = 5):
        self.top_k = top_k

    def run(self, state: IPLState) -> IPLState:

        query = state.get("user_query", "")

        # Use existing hybrid search directly with the user's query
        results = hybrid_search(query, top_k=self.top_k)

        h2h_docs: List[dict] = []

        for r in results:
            meta = r.get("metadata") or {}
            if str(meta.get("section", "")).lower() == "h2h":
                h2h_docs.append(r)

        state["h2h_context"] = h2h_docs

        return state


if __name__ == "__main__":
    s = IPLState()
    s["user_query"] = "MI vs CSK head-to-head"
    n = H2HNode()
    print(n.run(s))
