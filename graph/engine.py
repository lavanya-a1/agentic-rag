from typing import List

from graph.state import IPLState


class GraphEngine:
    def __init__(self, nodes: List):
        self.nodes = nodes

    def run(self, state: IPLState) -> IPLState:
        current = state
        for node in self.nodes:
            current = node.run(current)
        return current


__all__ = ["GraphEngine"]
