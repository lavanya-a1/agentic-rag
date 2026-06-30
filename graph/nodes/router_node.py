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

    def _is_h2h_query(self, q: str) -> bool:
        """Return True when the query expresses a head-to-head / team-comparison intent.

        Detection is purely linguistic — no team names are hardcoded.
        Three independent signals are checked; any one is sufficient.
        """
        import re

        # ── Signal 1: strong standalone h2h phrases ──────────────────────────
        # These phrases are unambiguous on their own, regardless of context.
        strong_phrases = [
            "head-to-head",
            "head to head",
            r"\bh2h\b",
            "win-loss record",
            "win loss record",
            r"\brivalry\b",
            "faced each other",
            "record between",
            "history between",
            "history of matches",
            "comparison between",
            "won more matches",
            "better record",
            r"\bdominates\b",
            r"\bdominate\b",
            r"\bbeaten\b",
        ]
        for pattern in strong_phrases:
            if re.search(pattern, q):
                return True

        # ── Signal 2: comparison operators between two tokens ────────────────
        # Matches: "X vs Y", "X versus Y", "X against Y"
        # The surrounding tokens must be non-empty (i.e. actual entities).
        comparison_ops = r"(?:\bvs\.?\b|\bversus\b|\bagainst\b)"
        if re.search(r"\S+\s+" + comparison_ops + r"\s+\S+", q):
            return True

        # ── Signal 3: question frames about inter-team history ───────────────
        # Patterns like:
        #   "between <X> and <Y>"
        #   "which team has (the) better/more … between"
        #   "how many … (won|beat|defeated) … between"
        #   "who has won more (matches|games|times)"
        inter_team_frames = [
            r"between\s+\S+\s+and\s+\S+",          # between X and Y
            r"which team.{0,30}\bbetween\b",         # which team … between
            r"which team.{0,30}\brecord\b",          # which team … record
            r"who has (won|beaten|beat).{0,30}more", # who has won/beaten more
            r"how many.{0,30}(won|beat|defeated)",   # how many times … won
            r"(match|game|meeting)s?.{0,20}between", # matches between
        ]
        for frame in inter_team_frames:
            if re.search(frame, q):
                return True

        return False

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

        # Classification precedence: h2h > venue > aggregation > comparison > reasoning > domain
        is_venue_query = (
            self._contains_any(q, venue_keywords)
            or any(name in q for name in stadium_names)
            or (
                "friendly" in q
                and any(term in q for term in ["batting", "bowling", "spin", "pace"])
            )
        )

        # Head-to-head: delegate to the dedicated linguistic detector.
        # Venue queries are excluded so that "Which ground is better for MI vs CSK?"
        # stays classified as venue, not h2h.
        is_h2h_query = (
            not is_venue_query
            and self._is_h2h_query(q)
        )

        if is_h2h_query:
            qtype = "h2h"
        elif is_venue_query:
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
