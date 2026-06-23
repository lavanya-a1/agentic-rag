
from graph.state import make_initial_state
from graph.nodes.router_node import RouterNode
from graph.nodes.batting_node import BattingStatsNode
from graph.nodes.bowling_node import BowlingStatsNode
from graph.nodes.synthesis_node import SynthesisNode


def run(query: str) -> str:

    state = make_initial_state(query)

    # Run router first to populate query_type and entities
    router = RouterNode()
    state = router.run(state)

    qtype = state.get("query_type", "") or ""

    # Conditional routing: run the appropriate stats node
    if "bat" in qtype:
        state = BattingStatsNode(top_k=5).run(state)
    elif "bowl" in qtype:
        state = BowlingStatsNode(top_k=5).run(state)
    else:
        # If not explicitly classified, attempt both (batting first)
        state = BattingStatsNode(top_k=5).run(state)
        if not state.get("batting_context"):
            state = BowlingStatsNode(top_k=5).run(state)

    # Synthesize from whichever context was populated
    synth = SynthesisNode()
    state = synth.run(state)

    return state.get("final_answer", "")


if __name__ == "__main__":
    q = input("Query: ")
    ans = run(q)
    print("\nFinal Answer:\n")
    print(ans)
