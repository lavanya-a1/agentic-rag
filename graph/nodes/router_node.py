from typing import Any

from graph.state import IPLState

try:
    from utils import metadata_extractor
except Exception:  # pragma: no cover - optional dependency guard
    metadata_extractor = None


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

    def _contains_any(self, query: str, terms: list[str]) -> bool:
        return any(term in query for term in terms)

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
            "wicket",
            "conditions",
            "condition",
            "batting-friendly",
            "bowling-friendly",
            "spin-friendly",
            "pace-friendly",
            "dew",
            "strategy",
            "toss",
            "chasing",
            "defending",
            "boundary",
            "boundaries",
            "bounce",
            "spin",
            "pace",
            "fast",
            "slow",
            "flat",
            "assist",
            "spinners",
            "dangerous",
            "average score",
            "first innings",
        ]

        stadium_names = [
            "wankhede",
            "chinnaswamy",
            "eden gardens",
            "ma chidambaram",
            "sawai mansingh",
            "narendra modi",
            "rajiv gandhi",
            "mohali",
            "ekana",
            "hyderabad",
            "chennai",
            "delhi",
            "mumbai",
            "kolkata",
            "jaipur",
            "ahmedabad",
            "lucknow",
            "pune",
            "bengaluru",
            "bangalore",
            "rajiv gandhi stadium",
            "narendra modi stadium",
        ]

        # Classification precedence: venue cues first, then compare/aggregation/reasoning, then domain
        is_venue_query = (
            self._contains_any(q, venue_keywords)
            or any(name in q for name in stadium_names)
            or (
                "friendly" in q
                and any(term in q for term in ["batting", "bowling", "spin", "pace"])
            )
        )

        if is_venue_query:
            qtype = "venue"
        elif any(w in q for w in self.AGGREGATION_WORDS):
            if self._contains_any(q, batting_keywords):
                qtype = "batting"
            elif self._contains_any(q, bowling_keywords):
                qtype = "bowling"
            else:
                qtype = "aggregation"
        elif " vs " in q or "compare" in q:
            if self._contains_any(q, batting_keywords):
                qtype = "batting_comparison"
            elif self._contains_any(q, bowling_keywords):
                qtype = "bowling_comparison"
            elif is_venue_query:
                qtype = "venue_comparison"
            else:
                qtype = "batting_comparison"
        elif any(w in q for w in ["why", "explain", "reason", "better", "stronger"]):
            qtype = "reasoning"
        elif self._contains_any(q, batting_keywords):
            qtype = "batting"
        elif self._contains_any(q, bowling_keywords):
            qtype = "bowling"
        else:
            qtype = "retrieval"

        # Extract entities via existing metadata extractor (LLM-backed)
        entities = {}

        if metadata_extractor is not None:
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
