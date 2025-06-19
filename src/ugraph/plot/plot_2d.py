from ugraph import ImmutableNetworkABC
from ugraph.plot._base import add_2d_ugraph_to_figure as _add, go
from ugraph.plot._options import ColorMap, PlotOptions

def add_2d_ugraph_to_figure(
    network: ImmutableNetworkABC,
    color_map: ColorMap,
    options: PlotOptions | None = None,
    figure: go.Figure | None = None,
) -> go.Figure:
    return _add(network, color_map, options, figure)
