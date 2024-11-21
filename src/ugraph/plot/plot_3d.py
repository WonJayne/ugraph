from collections import defaultdict
from typing import Hashable, NewType

from plotly.graph_objs import Scatter3d

try:
    import plotly.graph_objects as go
except ImportError as exc:
    raise ImportError(
        "The 'plot' functions require the 'plotly' library. \n Install it using: pip install ugraph[plotting]"
    ) from exc

from ugraph import BaseLinkType, BaseNodeType, ImmutableNetworkABC, NodeABC, NodeId

ColorMap = NewType("ColorMap", dict[Hashable, str])


def add_3d_ugraph_to_figure(
    network: ImmutableNetworkABC, color_map: ColorMap, figure: go.Figure | None = None
) -> go.Figure:
    figure = figure if figure is not None else go.Figure()
    figure.add_traces(data=_compute_graph_traces(network, color_map))
    figure.update_layout(
        scene={"xaxis_title": "X [Coordinates]", "yaxis_title": "Y [Coordinates]", "zaxis_title": "Z [Coordinates]"},
        font={"family": "Helvetica", "size": 12, "color": "black"},
    )
    return figure


def _compute_graph_traces(network: ImmutableNetworkABC, color_map: ColorMap) -> list[go.Scatter3d]:
    nodes_by_id = {node.id: node for node in network.all_nodes}
    return (
        _create_edge_traces(color_map, network, nodes_by_id)
        + _create_node_traces(color_map, network)
        + _create_arrow_traces(color_map, network, nodes_by_id)
    )


def _create_arrow_traces(
    color_map: ColorMap, network: ImmutableNetworkABC, nodes_by_id: dict[NodeId, NodeABC]
) -> list[go.Cone]:
    arrow_traces = []
    for end_node_pair, link in network.link_by_end_node_iterator():
        s_node = nodes_by_id[end_node_pair[0]]
        t_node = nodes_by_id[end_node_pair[1]]

        # Vector components for the arrow direction
        arrow_vector = [
            t_node.coordinates.x - s_node.coordinates.x,
            t_node.coordinates.y - s_node.coordinates.y,
            t_node.coordinates.z - s_node.coordinates.z,
        ]

        # Arrow starting point (at the mid-point of the edge for better clarity)
        mid_point = [
            (s_node.coordinates.x + t_node.coordinates.x) / 2,
            (s_node.coordinates.y + t_node.coordinates.y) / 2,
            (s_node.coordinates.z + t_node.coordinates.z) / 2,
        ]

        arrow_traces.append(
            go.Cone(
                x=[mid_point[0]],
                y=[mid_point[1]],
                z=[mid_point[2]],
                u=[arrow_vector[0]],
                v=[arrow_vector[1]],
                w=[arrow_vector[2]],
                sizemode="absolute",
                sizeref=4,  # Adjust the size of the arrows
                anchor="tail",
                colorscale=[[0, color_map[link.link_type]], [1, color_map[link.link_type]]],
                showscale=False,
                name=f"Arrow: {link.link_type.name}",
                legendgroup=link.link_type.name,
            )
        )
    return arrow_traces


def _create_node_traces(color_map: ColorMap, network: ImmutableNetworkABC) -> list[Scatter3d]:
    nodes_by_type: dict[BaseNodeType, dict[str, list[float | str | None]]] = defaultdict(
        lambda: {_key: [] for _key in ["node_x", "node_y", "node_z", "node_name"]}
    )
    for node in network.all_nodes:
        _type = node.node_type
        nodes_by_type[_type]["node_z"].append(node.coordinates.z)
        nodes_by_type[_type]["node_x"].append(node.coordinates.x)
        nodes_by_type[_type]["node_y"].append(node.coordinates.y)
        nodes_by_type[_type]["node_name"].append(f"{node.id} {node.node_type.name}")
    return [
        go.Scatter3d(
            x=nodes["node_x"],
            y=nodes["node_y"],
            z=nodes["node_z"],
            text=nodes["node_name"],
            name=node_type.name,
            mode="markers",
            hoverinfo="x+y+z+text",
            legendgroup=node_type.name,
            marker={"size": 25, "line_width": 0, "color": color_map[node_type]},
        )
        for node_type, nodes in nodes_by_type.items()
    ]


def _create_edge_traces(
    color_map: ColorMap, network: ImmutableNetworkABC, nodes_by_id: dict[NodeId, NodeABC]
) -> list[Scatter3d]:
    edges_by_type: dict[BaseLinkType, dict[str, list[float | str | None]]] = defaultdict(
        lambda: {_key: [] for _key in ["edge_x", "edge_y", "edge_z", "edge_line_name", "info"]}
    )
    for end_node_pair, link in network.link_by_end_node_iterator():
        s_node = nodes_by_id[end_node_pair[0]]
        t_node = nodes_by_id[end_node_pair[1]]
        _type = link.link_type
        edges_by_type[_type]["edge_x"].extend(
            (s_node.coordinates.x, (t_node.coordinates.x + s_node.coordinates.x) / 2, t_node.coordinates.x, None)
        )
        edges_by_type[_type]["edge_y"].extend(
            (s_node.coordinates.y, (t_node.coordinates.y + s_node.coordinates.y) / 2, t_node.coordinates.y, None)
        )
        edges_by_type[_type]["edge_z"].extend(
            (s_node.coordinates.z, (t_node.coordinates.z + s_node.coordinates.z) / 2, t_node.coordinates.z, None)
        )
        text = f"S:{s_node.id} T:{t_node.id},<br>link_type:{link.link_type}"
        edges_by_type[_type]["info"].extend((text, text, text, None))
    return [
        go.Scatter3d(
            x=edges["edge_x"],
            y=edges["edge_y"],
            z=edges["edge_z"],
            line={"width": 6, "color": color_map[edge_type]},
            mode="lines",
            name=edge_type.name,
            legendgroup=edge_type.name,
            opacity=1,
            hoverinfo="text",
            text=edges["info"],
        )
        for edge_type, edges in edges_by_type.items()
    ]
