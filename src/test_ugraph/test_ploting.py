import unittest
from pathlib import Path

from ugraph.plot import ColorMap, add_3d_ugraph_to_figure
from usage.create_state_network_example import create_example_state_railway_network
from usage.state_network import StateLinkType, StateNodeType


class TestUgraphPlot(unittest.TestCase):

    def setUp(self) -> None:
        # delete the file if it exists
        for path in (Path("test_plot.html"), Path("test_plot.png")):
            if path.exists():
                path.unlink()

    def tearDown(self) -> None:
        self.setUp()

    def test_plot(self):
        network = create_example_state_railway_network()

        color_map = ColorMap(
            {
                StateNodeType.RESOURCE: "green",
                StateNodeType.INFRASTRUCTURE: "blue",
                StateLinkType.ALLOCATION: "green",
                StateLinkType.TRANSITION: "blue",
                StateLinkType.OCCUPATION: "purple",
            }
        )

        figure = add_3d_ugraph_to_figure(network, color_map=color_map)
        figure = add_3d_ugraph_to_figure(network, color_map=color_map, figure=figure)
        figure.write_html("test_plot.html")

        # test the file is created
        self.assertTrue(Path("test_plot.html").exists())

        self.assertRaises(ValueError, lambda: figure.write_image("test_plot.png"))

    def test_debug_plot(self):
        network = create_example_state_railway_network()

        network.debug_plot(with_labels=True, file_name="test_plot.png")
