from graph.state import make_initial_state
from graph.nodes.router_node import RouterNode
from graph.nodes.batting_node import BattingStatsNode
from graph.nodes.synthesis_node import SynthesisNode
from graph.engine import GraphEngine


def run(query: str) -> str:

    state = make_initial_state(query)

    nodes = [
        RouterNode(),
        BattingStatsNode(top_k=5),
        SynthesisNode(),
    ]

    engine = GraphEngine(nodes)

    final = engine.run(state)

    return final.get("final_answer", "")


if __name__ == "__main__":
    q = input("Query: ")
    ans = run(q)
    print("\nFinal Answer:\n")
    print(ans)
