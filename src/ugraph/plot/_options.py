from typing import Hashable, Literal, NewType

ColorMap = NewType("ColorMap", dict[Hashable, str])


class PlotOptions:
    add_arrow: bool = True
    arrow_width: int = 2
    node_size: int = 2
    node_shape: str = "circle"
    edge_width: int = 6
    edge_dash: Literal["solid", "dash", "dot", "longdash", "dashdot", "longdashdot"] = "solid"
    edge_opacity: float = 1.0
