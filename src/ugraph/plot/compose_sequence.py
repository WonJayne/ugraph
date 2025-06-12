from collections.abc import Sequence

import plotly.graph_objects as go


def compose_collection_of_figures_with_slider(
    figures: Sequence[go.Figure], titles: Sequence[str] | None = None
) -> go.Figure:
    """
    Combine multiple figures, including those with subplots, into one figure with a slider for navigation.

    Args:
        figures (Collection[go.Figure]): A collection of Plotly figures to combine.
        titles (Collection[str] | None): Optional titles for the figures.

    Returns:
        go.Figure: A combined figure with a slider for navigation.
    """
    if not figures:
        raise ValueError("The `figures` collection cannot be empty.")

    if titles and len(titles) != len(figures):
        raise ValueError("The length of `titles` must match the length of `figures`.")

        # Initialize the list of frames
    frames = [go.Frame(data=fig.data, layout=fig.layout, name=f"{i}") for i, fig in enumerate(figures)]

    # Create the combined figure
    combined_figure = go.Figure(data=figures[0].data, layout=figures[0].layout)  # Start with the first figure's traces

    # Set frames via `update` instead of appending
    combined_figure.update(frames=frames)

    # Update layout with buttons and slider
    combined_figure.update_layout(
        updatemenus=[
            {
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": 723, "redraw": True}, "fromcurrent": True}],
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
                "transition": {"duration": 0},
                "pad": {"b": 10, "t": 50},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": [
                    {
                        "args": [[str(i)], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
                        "label": titles[i] if titles is not None else f"Figure {i + 1}",
                        "method": "animate",
                    }
                    for i in range(len(figures))
                ],
            }
        ],
    )

    return combined_figure


def compose_with_dropdown(figures: list[go.Figure], titles: list[str] | None = None) -> go.Figure:
    base_layout = figures[0].layout
    all_traces = []
    visibility_matrix = []

    for i, fig in enumerate(figures):
        vis = []
        for trace in fig.data:
            all_traces.append(trace)
            vis.append(True)
        visibility_matrix.append(vis)

    # pad so each step controls all traces
    max_len = max(len(v) for v in visibility_matrix)
    for vis in visibility_matrix:
        vis += [False] * (max_len - len(vis))

    steps = [
        {
            "label": titles[i] if titles else f"Figure {i + 1}",
            "method": "update",
            "args": [{"visible": [j == i for j in range(len(figures)) for _ in range(len(figures[j].data))]}],
        }
        for i in range(len(figures))
    ]

    fig = go.Figure(data=all_traces)
    fig.update_layout(
        updatemenus=[
            {
                "type": "dropdown",
                "showactive": True,
                "x": 0.1,
                "y": 1.15,
                "buttons": steps,
                "direction": "down",
                "pad": {"r": 10, "t": 10},
                "xanchor": "left",
                "yanchor": "top",
                "active": 0,
                "title": {"text": "Select Service: "},
            }
        ],
        **base_layout.to_plotly_json(),
    )
    return fig
