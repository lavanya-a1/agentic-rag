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

    def _is_form_query(self, q: str) -> bool:
        """Return True when the query expresses a recent/current form intent.

        Detection is purely linguistic — no player or team names are hardcoded.
        Two independent signal groups are checked; any match is sufficient.
        """
        import re

        # ── Signal 1: unambiguous form phrases (literal substring match) ────────
        # Sorted from most-specific to least-specific to avoid false positives.
        literal_phrases = [
            # multi-word – most specific first
            "recent form",
            "current form",
            "best form",
            "great form",
            "good form",
            "poor form",
            "out of form",
            "in form",
            "in-form",
            "recent performance",
            "recent performances",
            "recent matches",
            "recent games",
            "recent batting",
            "recent bowling",
            "performing lately",
            "performing recently",
            "performing well",
            "performing best",
            "current performance",
            "form of",
            "form for",
            "hottest streak",
            "best performer",
            "top performer",
            "on a roll",
            "lately",
        ]
        # Avoid classifying explicit career-statistic requests as form.
        # These should still route to batting/bowling or retrieval instead.
        career_stat_patterns = [
            r"\b(?:career|total)\s+(?:runs|wickets)\b",
            r"\b(?:batting|bowling)\s+average\b",
            r"\bstrike\s+rate\b",
            r"\beconomy\b",
        ]
        for pattern in career_stat_patterns:
            if re.search(pattern, q):
                return False

        if self._contains_any(q, literal_phrases):
            return True

        # ── Signal 2: regex patterns for looser phrasings ───────────────────────
        regex_patterns = [
            # "most in-form" / "most in form"
            r"\bmost\s+in[- ]?form\b",
            # "performing (well|best|great|brilliantly) recently/lately"
            r"\bperforming\b.{0,25}\b(recently|lately|of\s+late)\b",
            # "(best|good|great|poor|bad) form" even with words in between
            r"\b(best|great|good|poor|bad)\b.{0,10}\bform\b",
            # "in (the) (best|great|good|top) form"
            r"\bin\b.{0,15}\bform\b",
            # "who is performing best / who has been in form"
            r"\b(who|which\s+player|which\s+batter|which\s+bowler)\b.{0,30}\bform\b",
            # "(current|recent|latest) (batting|bowling) form"
            r"\b(current|recent|latest)\s+(batting|bowling)\s+form\b",
            # Recent / last N performance queries
            r"\blast\s+(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+(matches|innings)\b",
            r"\blast\s+(?:few|several|couple)\s+(matches|innings)\b",
            r"\brecent\s+(matches|innings|form|performance|performances)\b",
            r"\bform\s+in\s+the\s+last\b",
            r"\b(?:performed|performing)\s+(?:recently|lately|of\s+late)\b",
        ]
        for pattern in regex_patterns:
            if re.search(pattern, q):
                return True

        return False

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

        # Head-to-head: delegate to the dedicated linguistic detector.
        # Venue queries are excluded so that "Which ground is better for MI vs CSK?"
        # stays classified as venue, not h2h.
        is_h2h_query = self._is_h2h_query(q)

        # Form queries should override every other type (except h2h) when a
        # recent/current-performance intent is detected.
        is_form_query = (
            not is_h2h_query
            and self._is_form_query(q)
            and not self._contains_any(q, ["career runs", "total wickets", "batting average", "bowling average", "strike rate", "economy"])
        )

        # Classification precedence: h2h > form > venue > aggregation > comparison > reasoning > domain
        is_venue_query = (
            not is_form_query
            and (
                self._contains_any(q, venue_keywords)
                or any(name in q for name in stadium_names)
                or (
                    "friendly" in q
                    and any(term in q for term in ["batting", "bowling", "spin", "pace"])
                )
            )
        )

        # Trend keywords: performance over time, season-on-season
        trend_keywords = [
            "trend",
            "trends",
            "over the seasons",
            "across seasons",
            "season trend",
            "year on year",
            "over the years",
            "improvement",
            "decline",
            "consistency",
            "consistent",
            "inconsistent",
            "how has",
            "how have",
            "evolved",
            "last season",
            "this season",
        ]

        is_trend_query = (
            not is_venue_query
            and not is_h2h_query
            and not is_form_query
            and self._contains_any(q, trend_keywords)
        )

        # Classification precedence: h2h > form > trend > venue > aggregation > comparison > reasoning > domain
        if is_h2h_query:
            qtype = "h2h"
        elif is_form_query:
            qtype = "form"
        elif is_trend_query:
            qtype = "trend"
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
                qtype = "batting"
            elif self._contains_any(q, bowling_keywords):
                qtype = "bowling"
            elif is_venue_query:
                qtype = "venue_comparison"
            else:
                qtype = "batting"
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
