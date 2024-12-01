import json
import unittest
from pathlib import Path

from ugraph import UGraphDecoder, UGraphEncoder
from usage.create_state_network_example import create_example_state_railway_network
from usage.state_network import StateNetwork


class TestUgraphSerializer(unittest.TestCase):

    def setUp(self) -> None:
        # delete the file if it exists
        for path in (Path("test_serialisation.json"), Path(f"{StateNetwork.__name__}.json")):
            if path.exists():
                path.unlink()

    def tearDown(self) -> None:
        self.setUp()

    def test_full_cycle(self) -> None:
        graph = create_example_state_railway_network()

        with open("test_serialisation.json", "w") as f:
            json.dump(graph, f, cls=UGraphEncoder)

        with open("test_serialisation.json", "r") as f:
            loaded = json.load(f, cls=UGraphDecoder)

        self.assertEqual(graph.l_count, loaded.l_count)
        self.assertEqual(graph.n_count, loaded.n_count)
        self.assertEqual(graph.all_nodes, loaded.all_nodes)
        self.assertEqual(graph.all_links, loaded.all_links)

    def test_full_cycle_with_classmethods(self):
        graph = create_example_state_railway_network()

        graph.write_json(Path(f"{graph.__class__.__name__}.json"))

        loaded = graph.read_json(Path(f"{graph.__class__.__name__}.json"))

        self.assertEqual(graph.l_count, loaded.l_count)
        self.assertEqual(graph.n_count, loaded.n_count)
        self.assertEqual(graph.all_nodes, loaded.all_nodes)
        self.assertEqual(graph.all_links, loaded.all_links)
