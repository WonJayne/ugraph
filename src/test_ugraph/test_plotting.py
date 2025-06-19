import unittest
from pathlib import Path

from ugraph.plot import (
    ColorMap,
    add_3d_ugraph_to_figure,
    compose_collection_of_figures_with_slider,
    compose_with_dropdown,
)
from usage.create_state_network_example import create_example_state_railway_network
from usage.state_network import StateLinkType, StateNodeType


class TestUgraphPlot(unittest.TestCase):

    def setUp(self) -> None:
        # delete the file if it exists
        for path in (
            Path("test_plot.html"),
            Path("test_plot.png"),
            Path("test_plot_with_dropdown.html"),
            Path("test_plot_with_slider.html"),
            Path("test_debug_plot.png"),
            Path("test_debug_plot.html"),
        ):
            if path.exists():
                path.unlink()

    def tearDown(self) -> None:
        self.setUp()

    def test_plot(self):
        network = create_example_state_railway_network()

        # test that debug_plot works
        network.debug_plot(with_labels=True, file_name="test_debug_plot.png")
        self.assertTrue(Path("test_debug_plot.png").is_file() or Path("test_debug_plot.html").is_file())

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

        with self.assertRaises(ValueError):
            figure.write_image("test_plot.png")
        self.assertFalse(Path("test_plot.png").exists())

        compose_with_dropdown([figure], ["Test Plot"]).write_html("test_plot_with_dropdown.html")

        compose_collection_of_figures_with_slider([figure], ["Test Plot"]).write_html("test_plot_with_slider.html")

        self.assertTrue(Path("test_plot_with_dropdown.html").exists())
        self.assertTrue(Path("test_plot_with_slider.html").exists())

    def test_debug_plot(self):
        network = create_example_state_railway_network()

        network.debug_plot(with_labels=True, file_name="test_plot.png")
