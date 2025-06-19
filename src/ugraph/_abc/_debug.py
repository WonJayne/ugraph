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
        edge_x = [
            coord
            for src_idx, tgt_idx in graph.get_edgelist()
            for coord in (coords[src_idx][0], coords[tgt_idx][0], None)
        ]
        edge_y = [
            coord
            for src_idx, tgt_idx in graph.get_edgelist()
            for coord in (coords[src_idx][1], coords[tgt_idx][1], None)
        ]

        node_x, node_y = zip(*coords)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line={"color": "black"}))
        fig.add_trace(
            go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text" if with_labels else "markers",
                text=graph.vs["name"] if with_labels else None,
            )
        )
        output = Path(file_name) if file_name is not None else Path("debug.html")
        # Avoid image export if kaleido is not installed; always write html
        fig.write_html(str(output.with_suffix(".html")))
