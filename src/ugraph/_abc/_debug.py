import warnings
from collections.abc import Hashable, Sequence
from pathlib import Path
from typing import Any

import igraph as ig
import plotly.graph_objects as go


def debug_plot(
    graph: ig.Graph,
    with_labels: bool = True,
    file_name: str | Path | None = None,
    weights: Sequence[float] | None = None,
    **kwargs: dict[Hashable, Any],
) -> None:
    if with_labels:
        graph.vs["label"] = graph.vs["name"]
    if weights is not None:
        k = graph.layout_auto(weights=weights)
    else:
        k = graph.layout_sugiyama() if graph.is_dag() else graph.layout_auto()

    visual_style = {"layout": k, "bbox": (4000, 4000), "vertex_size": 3}
    try:
        ig.plot(graph, **visual_style, **kwargs).save(file_name if file_name is not None else "debug.jpg")
    except AttributeError:
        # fallback to a simple plotly based plot if cairo is unavailable
        warnings.warn("pycairo is missing; falling back to plotly for debug plot output")
        coords = k.coords
        edge_x: list[float | None] = []
        edge_y: list[float | None] = []
        for s, t in graph.get_edgelist():
            edge_x.extend((coords[s][0], coords[t][0], None))
            edge_y.extend((coords[s][1], coords[t][1], None))

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
