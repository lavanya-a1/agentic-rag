from typing import Any

from graph.state import IPLState
from utils import metadata_extractor


class RouterNode:
    """Classifies query type and extracts entities, updating state in-place."""

    AGGREGATION_WORDS = [
        "highest",
        "lowest",
        "maximum",
        "minimum",
        "most",
        "least",
        "top",
        "best",
    ]

    def run(self, state: IPLState) -> IPLState:
        q = state.get("user_query", "").lower()

        # Basic heuristic classification (keeps previous behaviour)
        if any(w in q for w in self.AGGREGATION_WORDS):
            qtype = "aggregation"
        elif " vs " in q or "compare" in q:
            qtype = "comparison"
        elif any(w in q for w in ["why", "explain", "reason", "better", "stronger"]):
            qtype = "reasoning"
        else:
            qtype = "retrieval"

        # Extract entities via existing metadata extractor (LLM-backed)
        entities = {}

        try:
            entities = metadata_extractor.extract_metadata(state.get("user_query", ""))
        except Exception:
            entities = {}

        state["query_type"] = qtype
        state["entities"] = entities

        return state


if __name__ == "__main__":
    s = IPLState()
    s["user_query"] = "Who scored most runs for MI in 2024?"
    r = RouterNode()
    print(r.run(s))
