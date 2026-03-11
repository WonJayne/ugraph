import warnings
from collections.abc import Hashable, Sequence
from pathlib import Path
from typing import Any

import igraph as ig
import plotly.graph_objects as go


def _get_layout(graph: ig.Graph, weights: Sequence[float] | None = None) -> ig.Layout:
    """Return an appropriate layout for ``graph`` based on ``weights``."""
    if weights is not None:
        return graph.layout_auto(weights=weights)
    return graph.layout_sugiyama() if graph.is_dag() else graph.layout_auto()


def debug_plot(
    graph: ig.Graph,
    with_labels: bool = True,
    file_name: str | Path | None = None,
    weights: Sequence[float] | None = None,
    show_direction: bool = True,
    arrow_scale: float = 0.18,
    **kwargs: dict[Hashable, Any],
) -> None:
    if with_labels:
        graph.vs["label"] = graph.vs["name"]
    layout = _get_layout(graph, weights)

    try:
        ig.plot(graph, layout=layout, bbox=(4000, 4000), vertex_size=3, **kwargs).save(
            file_name if file_name is not None else "debug.jpg"
        )
    except AttributeError:
        # fallback to a simple plotly based plot if cairo is unavailable
        warnings.warn("pycairo is missing; falling back to plotly for debug plot output")

        coords = layout.coords
        edge_list = graph.get_edgelist()
        edge_x = [
            coord
            for src_idx, tgt_idx in edge_list
            for coord in (coords[src_idx][0], coords[tgt_idx][0], None)
        ]
        edge_y = [
            coord
            for src_idx, tgt_idx in edge_list
            for coord in (coords[src_idx][1], coords[tgt_idx][1], None)
        ]

        node_x, node_y = zip(*coords)
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=edge_x,
                y=edge_y,
                mode="lines",
                name="edges",
                line={"color": "black", "width": 1},
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text" if with_labels else "markers",
                text=graph.vs["name"] if with_labels else None,
                textposition="top center",
                name="nodes",
                marker={"size": 8},
            )
        )

        if show_direction:
            annotations = []
            for src_idx, tgt_idx in edge_list:
                x0, y0 = coords[src_idx]
                x1, y1 = coords[tgt_idx]

                dx = x1 - x0
                dy = y1 - y0
                length = (dx**2 + dy**2) ** 0.5
                if length == 0:
                    continue

                frac = max(0.0, 1.0 - arrow_scale / length)
                xa = x0 + frac * dx
                ya = y0 + frac * dy

                annotations.append(
                    dict(
                        ax=x0,
                        ay=y0,
                        x=xa,
                        y=ya,
                        xref="x",
                        yref="y",
                        axref="x",
                        ayref="y",
                        showarrow=True,
                        arrowhead=3,
                        arrowsize=1.2,
                        arrowwidth=1.2,
                        arrowcolor="black",
                        standoff=2,
                    )
                )

            fig.update_layout(annotations=annotations)

        fig.update_layout(
            showlegend=False,
            xaxis={"visible": False},
            yaxis={"visible": False, "scaleanchor": "x", "scaleratio": 1},
            margin={"l": 20, "r": 20, "t": 20, "b": 20},
        )

        output = Path(file_name) if file_name is not None else Path("debug.html")
        # Avoid image export if kaleido is not installed; always write html
        fig.write_html(str(output.with_suffix(".html")))
