from collections.abc import Collection

import plotly.graph_objects as go


def compose_collection_of_figures_with_slider(figures: Collection[go.Figure]) -> go.Figure:
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
    final_fig.add_traces(next(iter(figures)).data)

    # Configure the layout with slider and play/pause buttons
    final_fig.update_layout(
        updatemenus=[
            {
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": 0, "redraw": True}, "fromcurrent": False}],
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
                        "args": [[str(i)], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
                        "label": f"Figure {i + 1}",
                        "method": "animate",
                    }
                    for i in range(len(figures))
                ],
            }
        ],
    )

    return final_fig
