from typing import TypedDict, Optional, List, Dict, Any


class IPLState(TypedDict, total=False):
    user_query: str
    query_type: str
    entities: Dict[str, Any]
    batting_context: List[Dict[str, Any]]
    bowling_context: List[Dict[str, Any]]
    venue_context: List[Dict[str, Any]]
    final_answer: str


def make_initial_state(query: str) -> IPLState:
    return IPLState(
        user_query=query,
        query_type="",
        entities={},
        batting_context=[],
        bowling_context=[],
        venue_context=[],
        final_answer="",
    )
