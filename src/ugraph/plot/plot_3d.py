from collections import defaultdict

from plotly.graph_objs import Scatter3d

from ugraph import BaseLinkType, BaseNodeType, ImmutableNetworkABC, NodeABC, NodeId
from ugraph.plot._options import ColorMap, PlotOptions

try:
    import plotly.graph_objects as go
except ImportError as exc:
    raise ImportError(
        "The 'plot' functions require the 'plotly' library. \n Install it using: pip install ugraph[plotting]"
    ) from exc


def add_3d_ugraph_to_figure(
    network: ImmutableNetworkABC,
    color_map: ColorMap,
    options: PlotOptions | None = None,
    figure: go.Figure | None = None,
) -> go.Figure:
    figure = figure if figure is not None else go.Figure()
    options = options if options is not None else PlotOptions()
    figure.add_traces(data=_compute_graph_traces(network, color_map, options))
    figure.update_layout(
        scene={"xaxis_title": "X [Coordinates]", "yaxis_title": "Y [Coordinates]", "zaxis_title": "Z [Coordinates]"},
        font={"family": "Helvetica", "size": 12, "color": "black"},
    )
    return figure


def _compute_graph_traces(
    network: ImmutableNetworkABC, color_map: ColorMap, options: PlotOptions
) -> list[go.Scatter3d]:
    nodes_by_id = {node.id: node for node in network.all_nodes}
    base_traces = _create_edge_traces(color_map, network, nodes_by_id, options) + _create_node_traces(
        color_map, network, options
    )
    if not options.add_arrow:
        return base_traces
    return base_traces + _create_arrow_traces(color_map, network, nodes_by_id, options)


def _create_arrow_traces(
    color_map: ColorMap, network: ImmutableNetworkABC, nodes_by_id: dict[NodeId, NodeABC], options: PlotOptions
) -> list[go.Cone]:
    arrow_traces = []
    for (s_idx, t_idx), link in network.link_by_end_node_iterator():
        s_cords, t_cords = nodes_by_id[s_idx].coordinates, nodes_by_id[t_idx].coordinates
        arrow_vector = [t_cords.x - s_cords.x, t_cords.y - s_cords.y, t_cords.z - s_cords.z]
        mid_point = [(s_cords.x + t_cords.x) * 0.5, (s_cords.y + t_cords.y) * 0.5, (s_cords.z + t_cords.z) * 0.5]

        arrow_traces.append(
            go.Cone(
                x=[mid_point[0]],
                y=[mid_point[1]],
                z=[mid_point[2]],
                u=[arrow_vector[0]],
                v=[arrow_vector[1]],
                w=[arrow_vector[2]],
                sizemode="absolute",
                sizeref=options.arrow_width,
                anchor="tail",
                colorscale=[[0, color_map[link.link_type]], [1, color_map[link.link_type]]],
                showscale=False,
                name=f"Arrow: {link.link_type.name}",
                legendgroup=link.link_type.name,
            )
        )
    return arrow_traces


def _create_node_traces(color_map: ColorMap, network: ImmutableNetworkABC, options: PlotOptions) -> list[Scatter3d]:
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
            marker={
                "size": options.node_size,
                "line_width": options.node_size * 0.1,
                "color": color_map[node_type],
                "symbol": options.node_shape,
            },
        )
        for node_type, nodes in nodes_by_type.items()
    ]


def _create_edge_traces(
    color_map: ColorMap, network: ImmutableNetworkABC, nodes_by_id: dict[NodeId, NodeABC], options: PlotOptions
) -> list[Scatter3d]:
    edges_by_type: dict[BaseLinkType, dict[str, list[float | str | None]]] = defaultdict(
        lambda: {_key: [] for _key in ["edge_x", "edge_y", "edge_z", "edge_line_name", "info"]}
    )
    for end_node_pair, link in network.link_by_end_node_iterator():
        s_node = nodes_by_id[end_node_pair[0]]
        t_node = nodes_by_id[end_node_pair[1]]
        s_cords, t_cords = s_node.coordinates, t_node.coordinates
        _type = link.link_type
        edges_by_type[_type]["edge_x"].extend((s_cords.x, (t_cords.x + s_cords.x) * 0.5, t_cords.x, None))
        edges_by_type[_type]["edge_y"].extend((s_cords.y, (t_cords.y + s_cords.y) * 0.5, t_cords.y, None))
        edges_by_type[_type]["edge_z"].extend((s_cords.z, (t_cords.z + s_cords.z) * 0.5, t_cords.z, None))
        text = f"S:{s_node.id} T:{t_node.id},<br>link_type:{link.link_type}"
        edges_by_type[_type]["info"].extend((text, text, text, None))
    return [
        go.Scatter3d(
            x=edges["edge_x"],
            y=edges["edge_y"],
            z=edges["edge_z"],
            line={"width": options.edge_width, "color": color_map[edge_type], "dash": options.edge_dash},
            mode="lines",
            name=edge_type.name,
            legendgroup=edge_type.name,
            opacity=options.edge_opacity,
            hoverinfo="text",
            text=edges["info"],
        )
        for edge_type, edges in edges_by_type.items()
    ]
