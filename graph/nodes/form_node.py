from typing import List

from graph.state import IPLState
from retrievers.hybrid_search import hybrid_search

from utils.debug import debug_state


class FormNode:
    """Fetch form-related documents using the existing hybrid retriever.

    Requirements:
    - Use the user's original query (no rewrite)
    - Filter results where metadata['section'] == 'form'
    - Save results to state['form_context']
    - Do not hardcode any player names, team names, or match information
    """

    def __init__(self, top_k: int = 5):
        self.top_k = top_k

    def run(self, state: IPLState) -> IPLState:

        query = state.get("user_query", "")

        # Widen the candidate pool so that form-section docs are not missed
        # due to low overall RRF rank (mirrors the fix already in TrendNode).
        fetch_k = max(50, self.top_k * 10)
        results = hybrid_search(query, top_k=fetch_k)

        # ── DEBUG: raw retrieval ─────────────────────────────────────────────
        print(f"[FormNode] raw hybrid_search returned {len(results)} docs")
        sections_seen = [r.get('metadata', {}).get('section', '<none>') for r in results]
        print(f"[FormNode] sections in raw results: {sections_seen}")
        # ────────────────────────────────────────────────────────────────────

        form_docs: List[dict] = []

        for r in results:
            meta = r.get("metadata") or {}
            if str(meta.get("section", "")).lower() == "form":
                form_docs.append(r)

        print(f"[FormNode] form_docs after section filter: {len(form_docs)}")

        state["form_context"] = form_docs[: self.top_k]

        return state


if __name__ == "__main__":
    s = IPLState()
    s["user_query"] = "What is the recent form of CSK?"
    n = FormNode()
    print(n.run(s))
