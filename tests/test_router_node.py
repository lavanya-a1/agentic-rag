import unittest

from graph.nodes.router_node import RouterNode
from graph.state import make_initial_state


class RouterNodeTests(unittest.TestCase):
    def setUp(self):
        self.router = RouterNode()

    def test_venue_queries_are_routed_to_venue(self):
        venue_queries = [
            "Is Chinnaswamy a batting-friendly pitch?",
            "What type of pitch is Wankhede?",
            "Tell me about Eden Gardens.",
            "Which stadium favors spinners?",
            "Which venue has the highest average first innings score?",
            "Is Hyderabad good for chasing?",
            "How is the wicket at Wankhede?",
            "Where do spinners become dangerous?",
            "Which ground has short boundaries?",
            "Which stadium is hardest for bowlers?",
            "Does Wankhede have dew?",
            "What is the strategy at Chennai?",
        ]

        for query in venue_queries:
            with self.subTest(query=query):
                state = self.router.run(make_initial_state(query))
                self.assertIn(state["query_type"], {"venue", "venue_comparison"})

    def test_player_stat_queries_still_classify_as_batting(self):
        batting_queries = [
            "Virat Kohli runs",
            "Rohit Sharma strike rate",
            "Compare Kohli and Gill",
            "Highest run scorer",
            "Batting average of KL Rahul",
        ]

        for query in batting_queries:
            with self.subTest(query=query):
                state = self.router.run(make_initial_state(query))
                self.assertEqual(state["query_type"], "batting")


if __name__ == "__main__":
    unittest.main()
