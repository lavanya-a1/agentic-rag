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

    def test_form_queries_are_routed_to_form(self):
        form_queries = [
            "What is the recent form of CSK?",
            "How has Gujarat Titans been performing lately?",
            "Tell me about the current form of Virat Kohli",
            "Recent performances of Mumbai Indians",
        ]

        for query in form_queries:
            with self.subTest(query=query):
                state = self.router.run(make_initial_state(query))
                self.assertEqual(state["query_type"], "form")

    def test_records_queries_are_routed_to_records(self):
        records_queries = [
            "Who has scored the most runs in IPL history?",
            "Which player has taken the most wickets?",
            "Highest individual score in IPL.",
            "Best bowling figures in IPL.",
            "Which team has the highest total in IPL?",
            "Lowest team score in IPL history.",
            "Fastest century in IPL.",
            "Most sixes in IPL.",
            "Most catches in IPL.",
            "Highest successful run chase in IPL.",
            "Largest victory margin in IPL.",
            "Which player has the most Player of the Match awards?",
        ]

        for query in records_queries:
            with self.subTest(query=query):
                state = self.router.run(make_initial_state(query))
                self.assertEqual(state["query_type"], "records")

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
