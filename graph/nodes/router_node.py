from typing import Any

from graph.state import IPLState
from utils import metadata_extractor
from utils.debug import debug_state


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

        # Domain-specific keywords
        batting_keywords = [
            "run",
            "runs",
            "average",
            "strike rate",
            "strike-rate",
            "fifty",
            "hundred",
            "fifties",
            "hundreds",
            "batting",
            "score",
        ]

        bowling_keywords = [
            "wicket",
            "wickets",
            "economy",
            "economy rate",
            "bowling average",
            "bowling",
            "figures",
            "best bowling",
            "strike rate",
            "strike-rate",
            "overs",
            "maiden",
        ]

        venue_keywords = [
            "stadium",
            "venue",
            "ground",
            "pitch",
            "home ground",
            "capacity",
            "surface",
        ]

        # Classification precedence: explicit compare/aggregation/reasoning, then domain
        if any(w in q for w in self.AGGREGATION_WORDS):
            qtype = "aggregation"
        elif " vs " in q or "compare" in q:
            # Comparison may be batting, bowling, or venue depending on keywords
            if any(w in q for w in batting_keywords):
                qtype = "batting_comparison"
            elif any(w in q for w in bowling_keywords):
                qtype = "bowling_comparison"
            elif any(w in q for w in venue_keywords):
                qtype = "venue_comparison"
            else:
                qtype = "comparison"
        elif any(w in q for w in ["why", "explain", "reason", "better", "stronger"]):
            qtype = "reasoning"
        elif any(w in q for w in batting_keywords):
            qtype = "batting"
        elif any(w in q for w in bowling_keywords):
            qtype = "bowling"
        elif any(w in q for w in venue_keywords):
            qtype = "venue"
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
