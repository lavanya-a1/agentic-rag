
from graph.state import make_initial_state
from graph.nodes.router_node import RouterNode
from graph.nodes.batting_node import BattingStatsNode
from graph.nodes.bowling_node import BowlingStatsNode
from graph.nodes.synthesis_node import SynthesisNode
from graph.nodes.venue_node import VenueNode
from graph.nodes.h2h_node import H2HNode
from graph.nodes.trend_node import TrendNode


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
    elif "venue" in qtype:
        state = VenueNode(top_k=5).run(state)
    elif "h2h" in qtype:
        state = H2HNode(top_k=5).run(state)
    elif "trend" in qtype:
        state = TrendNode(top_k=5).run(state)
    else:
        # If not explicitly classified, attempt both (batting first)
        state = BattingStatsNode(top_k=5).run(state)
        if not state.get("batting_context"):
            state = BowlingStatsNode(top_k=5).run(state)

    # Synthesize from whichever context was populated
    synth = SynthesisNode()
    state = synth.run(state)

    return state.get("final_answer", "")
def debug_state(stage, state):
    print(f"\n===== {stage} =====")
    print("USER_QUERY:", state.get("user_query"))
    print("QUERY_TYPE:", state.get("query_type"))
    print("ENTITIES:", state.get("entities"))
    for key in ["batting_context", "bowling_context", "venue_context", "h2h_context", "trend_context"]:
        docs = state.get(key, []) or []
        print(f"{key}: count={len(docs)} ids={[d.get('id') for d in docs]}")

if __name__ == "__main__":
    print("Welcome to the IPL LangGraph Assistant! (Type 'exit', 'quit', or 'q' to quit)\n")
    print("=" * 60)
    try:
        while True:
            try:
                q = input("You: ").strip()
            except EOFError:
                break
            
            if not q:
                continue
                
            if q.lower() in ["exit", "quit", "q"]:
                break
            
            # Run pipeline here so we have access to the final state for debugging
            state = make_initial_state(q)

            # Router
            router = RouterNode()
            state = router.run(state)

            qtype = state.get("query_type", "") or ""

            # Conditional routing: run the appropriate stats node
            if "bat" in qtype:
                state = BattingStatsNode(top_k=5).run(state)
            elif "bowl" in qtype:
                state = BowlingStatsNode(top_k=5).run(state)
            elif "venue" in qtype:
                state = VenueNode(top_k=5).run(state)
            elif "h2h" in qtype:
                state = H2HNode(top_k=5).run(state)
            elif "trend" in qtype:
                state = TrendNode(top_k=5).run(state)
            else:
                state = BattingStatsNode(top_k=5).run(state)
                if not state.get("batting_context"):
                    state = BowlingStatsNode(top_k=5).run(state)

            # Synthesize
            synth = SynthesisNode()
            state = synth.run(state)

            debug_state("FINAL", state)

            print("\nFinal Answer:\n")
            print(state.get("final_answer", ""))
            print("\n" + "=" * 60 + "\n")
    except KeyboardInterrupt:
        pass
    print("\nExiting..")
