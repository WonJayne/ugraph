from ._compose_sequence import compose_collection_of_figures_with_slider, compose_with_dropdown
from ._options import ColorMap, PlotOptions
from ._plot_2d import add_2d_ugraph_to_figure
from ._plot_3d import add_3d_ugraph_to_figure

__all__ = [
    "PlotOptions",
    "add_2d_ugraph_to_figure",
    "add_3d_ugraph_to_figure",
    "ColorMap",
    "compose_collection_of_figures_with_slider",
    "compose_with_dropdown",
]

try:
    import plotly.graph_objects as go
except ImportError as exc:
    raise ImportError(
        "The 'plot' functions require the 'plotly' library. \n Install it using: pip install ugraph[plotting]"
    ) from exc
