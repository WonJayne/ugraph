from collections import defaultdict
from collections.abc import Collection
from typing import Hashable, NewType

import plotly.graph_objects as go

from usage.state_network import StateNetwork

ColorMap = NewType("ColorMap", dict[Hashable, str])


def add_state_network_in_3d_to_figure(
    network: StateNetwork, color_map: ColorMap, figure: go.Figure | None = None
) -> go.Figure:
    figure = figure if figure is not None else go.Figure()
    figure.add_traces(data=_compute_graph_traces(network, color_map))
    figure.update_layout(
        scene={
            "xaxis_title": "X [Arbitrary Coordinates]",
            "yaxis_title": "Y [Arbitrary Coordinates]",
            "zaxis_title": "Z [Arbitrary Coordinates]",
        },
        font={"family": "Helvetica", "size": 12, "color": "black"},
    )
    return figure


def compose_with_slider(figures: Collection[go.Figure]) -> go.Figure:
    """
    Combine multiple 3D figures into one figure with a slider for navigation.

    Args:
        figures (Collection[go.Figure]): A collection of Plotly figures to combine.

    Returns:
        go.Figure: A combined figure with slider and animation frames.
    """
    if not figures:
        raise ValueError("The `figures` collection cannot be empty.")

    # Initialize the final figure and frames
    final_fig = go.Figure(frames=[go.Frame(data=fig.data, name=str(i)) for i, fig in enumerate(figures)])

    # Add the initial data (first figure's data)
    final_fig.add_traces(figures[0].data)

    # Configure the layout with slider and play/pause buttons
    final_fig.update_layout(
        updatemenus=[
            {
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}],
                        "label": "Play",
                        "method": "animate",
                    },
                    {
                        "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
                        "label": "Pause",
                        "method": "animate",
                    },
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top",
            }
        ],
        sliders=[
            {
                "active": 0,
                "yanchor": "top",
                "xanchor": "left",
                "currentvalue": {"font": {"size": 20}, "prefix": "Figure: ", "visible": True, "xanchor": "right"},
                "transition": {"duration": 300, "easing": "cubic-in-out"},
                "pad": {"b": 10, "t": 50},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": [
                    {
                        "args": [[str(i)], {"frame": {"duration": 300, "redraw": True}, "mode": "immediate"}],
                        "label": f"Figure {i + 1}",
                        "method": "animate",
                    }
                    for i in range(len(figures))
                ],
            }
        ],
    )

    return final_fig


def _compute_graph_traces(network: StateNetwork, color_map: ColorMap) -> list[go.Scatter3d]:
    edges_by_type = defaultdict(lambda: {_key: [] for _key in ["edge_x", "edge_y", "edge_z", "edge_line_name", "info"]})
    nodes_by_id = {node.id: node for node in network.all_nodes}
    for end_node_pair, link in network.link_by_end_node_iterator():
        s_node = nodes_by_id[end_node_pair[0]]
        t_node = nodes_by_id[end_node_pair[1]]
        s_id = link.link_type.name
        edges_by_type[s_id]["edge_x"].extend(
            (s_node.coordinates.x, (t_node.coordinates.x + s_node.coordinates.x) / 2, t_node.coordinates.x, None)
        )
        edges_by_type[s_id]["edge_y"].extend(
            (s_node.coordinates.y, (t_node.coordinates.y + s_node.coordinates.y) / 2, t_node.coordinates.y, None)
        )
        edges_by_type[s_id]["edge_z"].extend(
            (s_node.coordinates.z, (t_node.coordinates.z + s_node.coordinates.z) / 2, t_node.coordinates.z, None)
        )
        text = f"S:{s_node.id} T:{t_node.id},<br>link_type:{link.link_type}"
        edges_by_type[s_id]["info"].extend((text, text, text, None))

    nodes_by_type = defaultdict(lambda: {_key: [] for _key in ["node_x", "node_y", "node_z", "node_name"]})

    for node in network.all_nodes:
        s_id = node.node_type.name
        nodes_by_type[s_id]["node_z"].append(node.coordinates.z)
        nodes_by_type[s_id]["node_x"].append(node.coordinates.x)
        nodes_by_type[s_id]["node_y"].append(node.coordinates.y)
        nodes_by_type[s_id]["node_name"].append(f"{node.id} {node.node_type.name}")

    edge_traces = [
        go.Scatter3d(
            x=edges["edge_x"],
            y=edges["edge_y"],
            z=edges["edge_z"],
            line={"width": 6, "color": color_map[edge_type]},
            mode="lines",
            name=edge_type,
            legendgroup=edge_type,
            opacity=1,
            hoverinfo="text",
            text=edges["info"],
        )
        for edge_type, edges in edges_by_type.items()
    ]

    node_traces = [
        go.Scatter3d(
            x=nodes["node_x"],
            y=nodes["node_y"],
            z=nodes["node_z"],
            text=nodes["node_name"],
            name=node_type,
            mode="markers",
            hoverinfo="x+y+z+text",
            legendgroup=node_type,
            marker={"size": 25, "line_width": 0, "color": color_map[node_type]},
        )
        for node_type, nodes in nodes_by_type.items()
    ]

    # Add arrows (cones) for each edge
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

        # Add a cone to represent the arrow
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
                colorscale=[[0, color_map[link.link_type.name]], [1, color_map[link.link_type.name]]],
                showscale=False,
                name=f"Arrow: {link.link_type.name}",
                legendgroup=link.link_type.name,
            )
        )

    return edge_traces + node_traces + arrow_traces
