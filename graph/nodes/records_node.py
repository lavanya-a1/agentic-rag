from typing import List

from graph.state import IPLState
from retrievers.hybrid_search import hybrid_search

from utils.debug import debug_state


class RecordsNode:
    """Fetch record-related documents using the existing hybrid retriever.

    Requirements:
    - Use the user's original query (no rewrite)
    - Filter results where metadata['section'] == 'records'
    - Save results to state['records_context']
    - Do not hardcode any player names, team names, or record types
    """

    def __init__(self, top_k: int = 5):
        self.top_k = top_k

    def run(self, state: IPLState) -> IPLState:

        query = state.get("user_query", "")

        results = hybrid_search(query, top_k=self.top_k)

        records_docs: List[dict] = []

        for r in results:
            meta = r.get("metadata") or {}
            if str(meta.get("section", "")).lower() == "records":
                records_docs.append(r)

        state["records_context"] = records_docs

        return state


if __name__ == "__main__":
    s = IPLState()
    s["user_query"] = "Who has scored the most runs in IPL history?"
    n = RecordsNode()
    print(n.run(s))
