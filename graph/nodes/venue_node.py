from typing import List

from graph.state import IPLState
from retrievers.hybrid_search import hybrid_search

from utils.debug import debug_state

class VenueNode:
    """Fetch venue-related documents using the existing hybrid retriever.

    Requirements:
    - Use the user's original query (no rewrite)
    - Filter results where metadata['section'] == 'venue'
    - Save results to state['venue_context']
    - Do not hardcode any venue names
    """

    def __init__(self, top_k: int = 5):
        self.top_k = top_k

    def run(self, state: IPLState) -> IPLState:

        query = state.get("user_query", "")

        # Use existing hybrid search directly with the user's query
        results = hybrid_search(query, top_k=self.top_k)

        venue_docs: List[dict] = []

        for r in results:
            meta = r.get("metadata") or {}
            if str(meta.get("section", "")).lower() == "venue":
                venue_docs.append(r)

        state["venue_context"] = venue_docs

        return state


if __name__ == "__main__":
    s = IPLState()
    s["user_query"] = "What is the pitch like at Wankhede Stadium?"
    n = VenueNode()
    print(n.run(s))
