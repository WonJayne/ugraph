from dataclasses import dataclass
from enum import unique
from pathlib import Path

from ugraph import (
    BaseLinkType,
    BaseNodeType,
    EndNodeIdPair,
    LinkABC,
    MutableNetworkABC,
    NodeABC,
    NodeId,
    ThreeDCoordinates,
)
from ugraph.plot import ColorMap, add_3d_ugraph_to_figure


@unique
class ExampleNodeType(BaseNodeType):
    # Specify your own node types here (BaseNodeType is an IntEnum, that does not have any values)
    EXAMPLE_NODE = 0


@unique
class ExampleLinkType(BaseLinkType):
    # Specify your own link types here (BaseLinkType is an IntEnum, that does not have any values)
    EXAMPLE_LINK = 0


@dataclass(frozen=True, slots=True)
class ExampleNode(NodeABC[ExampleNodeType]):
    node_type: ExampleNodeType  # This is required to be able to use the node in the network
    # Define your own attributes here (apart from the ones defined in NodeABC)
    example_value: int


@dataclass(frozen=True, slots=True)
class ExampleLink(LinkABC[ExampleLinkType]):
    link_type: ExampleLinkType  # This is required to be able to use the link in the network
    # Define your own attributes here (apart from the ones defined in LinkABC)
    example_value: float


class ExampleNetwork(MutableNetworkABC[ExampleNode, ExampleLink, ExampleNodeType, ExampleLinkType]):
    # Define your own methods here (apart from the ones defined in MutableNetworkABC / ImmutableNetworkABC)
    pass


# Example usage
def create_example_network() -> ExampleNetwork:
    # Create two nodes and a link to show how to use the network
    node_a = ExampleNode(
        node_id=NodeId("A"),
        coordinates=ThreeDCoordinates(x=0, y=0, z=0),
        node_type=ExampleNodeType.EXAMPLE_NODE,
        example_value=1,
    )
    node_b = ExampleNode(
        node_id=NodeId("B"),
        coordinates=ThreeDCoordinates(x=100, y=-100, z=100),
        node_type=ExampleNodeType.EXAMPLE_NODE,
        example_value=2,
    )

    link = ExampleLink(link_type=ExampleLinkType.EXAMPLE_LINK, example_value=0.5)

    # Create an empty network and add the nodes and the link (with the end nodes specified)
    network = ExampleNetwork.create_empty()
    network.add_nodes([node_a, node_b])
    link_with_end_nodes = (EndNodeIdPair((node_a.id, node_b.id)), link)
    network.add_links([link_with_end_nodes])

    return network


if __name__ == "__main__":
    example_network = create_example_network()
    print(example_network.all_nodes, example_network.all_links)
    # if you want to debug your plot, you can use the following line to save the plot to a file
    example_network.debug_plot("example_network.png")
    # You can also store and load the network to/from a file
    example_network.write_json(Path("example.ExampleNetwork.json"))
    example_network = ExampleNetwork.read_json(Path("example.ExampleNetwork.json"))
    print(example_network.all_nodes, example_network.all_links)

    # Bonus, if you want to plot the network in 3D
    color_map = ColorMap({ExampleNodeType.EXAMPLE_NODE: "red", ExampleLinkType.EXAMPLE_LINK: "blue"})
    add_3d_ugraph_to_figure(example_network, color_map).show()
