from collections.abc import Hashable, Sequence
from pathlib import Path
from typing import Any

import igraph as ig


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
    ig.plot(graph, **visual_style, **kwargs).save(file_name if file_name is not None else "debug.jpg")
