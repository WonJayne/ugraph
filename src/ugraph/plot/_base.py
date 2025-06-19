from __future__ import annotations

from collections import defaultdict

try:
    import plotly.graph_objects as go
except ImportError as exc:  # pragma: no cover - handled at runtime
    raise ImportError(
        "The 'plot' functions require the 'plotly' library.\nInstall it using: pip install ugraph[plotting]"
    ) from exc

from ugraph import BaseLinkType, BaseNodeType, ImmutableNetworkABC, NodeABC, NodeId
from ._options import ColorMap, PlotOptions


__all__ = [
    "add_ugraph_to_figure",
    "add_2d_ugraph_to_figure",
    "add_3d_ugraph_to_figure",
]


def add_ugraph_to_figure(
    network: ImmutableNetworkABC,
    color_map: ColorMap,
    options: PlotOptions | None = None,
    figure: go.Figure | None = None,
    *,
    dimension: int,
) -> go.Figure:
    """Create or extend a :class:`plotly.graph_objects.Figure` with graph traces."""
    figure = figure if figure is not None else go.Figure()
    options = options if options is not None else PlotOptions()
    figure.add_traces(
        data=_compute_graph_traces(network, color_map, options, dimension=dimension)
    )
    figure.update_layout(
        scene={"xaxis_title": "X [Coordinates]", "yaxis_title": "Y [Coordinates]", "zaxis_title": "Z [Coordinates]"},
        font={"family": "Helvetica", "size": 12, "color": "black"},
    )
    return figure


def add_2d_ugraph_to_figure(
    network: ImmutableNetworkABC,
    color_map: ColorMap,
    options: PlotOptions | None = None,
    figure: go.Figure | None = None,
) -> go.Figure:
    """Add a 2D representation of ``network`` to ``figure``."""
    return add_ugraph_to_figure(
        network,
        color_map,
        options=options,
        figure=figure,
        dimension=2,
    )


def add_3d_ugraph_to_figure(
    network: ImmutableNetworkABC,
    color_map: ColorMap,
    options: PlotOptions | None = None,
    figure: go.Figure | None = None,
) -> go.Figure:
    """Add a 3D representation of ``network`` to ``figure``."""
    return add_ugraph_to_figure(
        network,
        color_map,
        options=options,
        figure=figure,
        dimension=3,
    )


def _compute_graph_traces(
    network: ImmutableNetworkABC,
    color_map: ColorMap,
    options: PlotOptions,
    *,
    dimension: int,
) -> list[go.BaseTraceType]:
    """Compute graph traces for 2D or 3D plotting."""
    nodes_by_id = {node.node_id: node for node in network.all_nodes}
    base_traces = create_edge_traces(
        color_map, network, nodes_by_id, options, dimension
    ) + create_node_traces(color_map, network, options, dimension)
    if not options.add_arrow:
        return base_traces
    return base_traces + create_arrow_traces(
        color_map, network, nodes_by_id, options, dimension
    )


def create_arrow_traces(
    color_map: ColorMap,
    network: ImmutableNetworkABC,
    nodes_by_id: dict[NodeId, NodeABC],
    options: PlotOptions,
    dimension: int,
) -> list[go.Cone]:
    arrow_traces: list[go.Cone] = []
    for (s_idx, t_idx), link in network.iter_links_with_end_nodes():
        s_cords, t_cords = nodes_by_id[s_idx].coordinates, nodes_by_id[t_idx].coordinates
        arrow_vector = [
            t_cords.x - s_cords.x,
            t_cords.y - s_cords.y,
            t_cords.z - s_cords.z,
        ]
        mid_point = [
            (s_cords.x + t_cords.x) * 0.5,
            (s_cords.y + t_cords.y) * 0.5,
            (s_cords.z + t_cords.z) * 0.5,
        ]
        kwargs: dict[str, list[float]] = {
            "x": [mid_point[0]],
            "y": [mid_point[1]],
            "u": [arrow_vector[0]],
            "v": [arrow_vector[1]],
        }
        if dimension == 3:
            kwargs["z"] = [mid_point[2]]
            kwargs["w"] = [arrow_vector[2]]
        arrow_traces.append(
            go.Cone(
                **kwargs,
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


def create_node_traces(
    color_map: ColorMap,
    network: ImmutableNetworkABC,
    options: PlotOptions,
    dimension: int,
) -> list[go.Scatter | go.Scatter3d]:
    if dimension == 2:
        nodes_by_type: dict[BaseNodeType, dict[str, list[float | str | None]]] = defaultdict(
            lambda: {key: [] for key in ["node_x", "node_y", "node_name"]}
        )
    else:
        nodes_by_type = defaultdict(
            lambda: {key: [] for key in ["node_x", "node_y", "node_z", "node_name"]}
        )
    for node in network.all_nodes:
        _type = node.node_type
        if dimension == 3:
            nodes_by_type[_type]["node_z"].append(node.coordinates.z)
        nodes_by_type[_type]["node_x"].append(node.coordinates.x)
        nodes_by_type[_type]["node_y"].append(node.coordinates.y)
        nodes_by_type[_type]["node_name"].append(f"{node.node_id} {node.node_type.name}")
    traces: list[go.Scatter | go.Scatter3d] = []
    for node_type, nodes in nodes_by_type.items():
        marker = {
            "size": options.node_size,
            "line_width": options.node_size * 0.1,
            "color": color_map[node_type],
            "symbol": options.node_shape,
        }
        if dimension == 2:
            traces.append(
                go.Scatter(
                    x=nodes["node_x"],
                    y=nodes["node_y"],
                    text=nodes["node_name"],
                    name=node_type.name,
                    mode="markers",
                    hoverinfo="x+y+text",
                    legendgroup=node_type.name,
                    marker=marker,
                )
            )
        else:
            traces.append(
                go.Scatter3d(
                    x=nodes["node_x"],
                    y=nodes["node_y"],
                    z=nodes["node_z"],
                    text=nodes["node_name"],
                    name=node_type.name,
                    mode="markers",
                    hoverinfo="x+y+z+text",
                    legendgroup=node_type.name,
                    marker=marker,
                )
            )
    return traces


def create_edge_traces(  # pylint: disable=too-many-locals
    color_map: ColorMap,
    network: ImmutableNetworkABC,
    nodes_by_id: dict[NodeId, NodeABC],
    options: PlotOptions,
    dimension: int,
) -> list[go.Scatter | go.Scatter3d]:
    if dimension == 2:
        edges_by_type: dict[BaseLinkType, dict[str, list[float | str | None]]] = defaultdict(
            lambda: {key: [] for key in ["edge_x", "edge_y", "edge_line_name", "info"]}
        )
    else:
        edges_by_type = defaultdict(
            lambda: {key: [] for key in ["edge_x", "edge_y", "edge_z", "edge_line_name", "info"]}
        )
    for end_node_pair, link in network.iter_links_with_end_nodes():
        s_node = nodes_by_id[end_node_pair[0]]
        t_node = nodes_by_id[end_node_pair[1]]
        s_cords, t_cords = s_node.coordinates, t_node.coordinates
        _type = link.link_type
        edges_by_type[_type]["edge_x"].extend((s_cords.x, (t_cords.x + s_cords.x) * 0.5, t_cords.x, None))
        edges_by_type[_type]["edge_y"].extend((s_cords.y, (t_cords.y + s_cords.y) * 0.5, t_cords.y, None))
        if dimension == 3:
            edges_by_type[_type]["edge_z"].extend((s_cords.z, (t_cords.z + s_cords.z) * 0.5, t_cords.z, None))
        text = f"S:{s_node.node_id} T:{t_node.node_id},<br>link_type:{link.link_type}"
        edges_by_type[_type]["info"].extend((text, text, text, None))
    traces: list[go.Scatter | go.Scatter3d] = []
    for edge_type, edges in edges_by_type.items():
        line = {
            "width": options.edge_width,
            "color": color_map[edge_type],
            "dash": options.edge_dash,
        }
        if dimension == 2:
            traces.append(
                go.Scatter(
                    x=edges["edge_x"],
                    y=edges["edge_y"],
                    line=line,
                    mode="lines",
                    name=edge_type.name,
                    legendgroup=edge_type.name,
                    opacity=options.edge_opacity,
                    hoverinfo="text",
                    text=edges["info"],
                )
            )
        else:
            traces.append(
                go.Scatter3d(
                    x=edges["edge_x"],
                    y=edges["edge_y"],
                    z=edges["edge_z"],
                    line=line,
                    mode="lines",
                    name=edge_type.name,
                    legendgroup=edge_type.name,
                    opacity=options.edge_opacity,
                    hoverinfo="text",
                    text=edges["info"],
                )
            )
    return traces
