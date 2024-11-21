import unittest

from usage.create_example_network import create_example_state_railway_network


class TestIntegration(unittest.TestCase):
    def test_integration(self) -> None:
        # Create a new graph
        graph = create_example_state_railway_network()

        self.assertEqual(graph.l_count, 32)
        self.assertEqual(graph.n_count, 24)

        reduced = graph.reduce_to_agent_network()
        self.assertEqual(reduced.l_count, 0)
        self.assertEqual(reduced.n_count, 0)

        reduced = graph.reduce_to_resource_network()
        self.assertEqual(reduced.l_count, 0)
        self.assertEqual(reduced.n_count, 8)

        reduced = graph.reduce_to_transition_network()
        self.assertEqual(reduced.l_count, 16)
        self.assertEqual(reduced.n_count, 16)
