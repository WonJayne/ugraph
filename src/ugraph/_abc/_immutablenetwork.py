from __future__ import annotations

import json
import warnings
from abc import ABC
from collections.abc import Iterable
from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
from types import UnionType
from typing import Any, Generic, Iterator, Literal, NewType, Type, TypeVar, Union, get_args, get_origin, get_type_hints

import igraph

from ugraph._abc._debug import debug_plot
from ugraph._abc._link import BaseLinkType, EndNodeIdPair, LinkABC
from ugraph._abc._node import BaseNodeType, NodeABC, NodeId, NodeIndex

NodeT = TypeVar("NodeT", bound=NodeABC)
LinkT = TypeVar("LinkT", bound=LinkABC)
NodeTypeT = TypeVar("NodeTypeT", bound=BaseNodeType)
LinkTypeT = TypeVar("LinkTypeT", bound=BaseLinkType)
Self = TypeVar("Self", bound="ImmutableNetworkABC")
LinkIndex = NewType("LinkIndex", int)

VERTEX_NAME_KEY: Literal["name"] = "name"  # is given by igraph library
assert VERTEX_NAME_KEY == "name"  # is given by igraph library and cannot be changed

NODE_ATTRIBUTE_KEY: str = "node"
LINK_ATTRIBUTE_KEY: str = "link"
assert NODE_ATTRIBUTE_KEY != LINK_ATTRIBUTE_KEY  # must be different
assert NODE_ATTRIBUTE_KEY != VERTEX_NAME_KEY  # must be different
assert LINK_ATTRIBUTE_KEY != VERTEX_NAME_KEY  # must be different
assert NODE_ATTRIBUTE_KEY == "node"  # must be "node"
assert LINK_ATTRIBUTE_KEY == "link"  # must be "link"


@dataclass(init=False, frozen=True, eq=False)
class ImmutableNetworkABC(Generic[NodeT, LinkT, NodeTypeT, LinkTypeT], ABC):
    _underlying_digraph: igraph.Graph

    def __init__(self, _underlying_digraph: igraph.Graph) -> None:
        if not _underlying_digraph.is_directed():
            raise TypeError("Only directed graphs allowed")
        object.__setattr__(self, "_underlying_digraph", _underlying_digraph)

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ImmutableNetworkABC):
            return False
        if self is other:
            return True
        raise ValueError(
            f"Cannot compare two {self.__class__.__name__} instances\n"
            f"Since we would need to check the graph for isomorphism and then for this match "
            f"compare nodes and links"
        )

    @property
    def n_count(self) -> int:
        return self._underlying_digraph.vcount()

    @property
    def l_count(self) -> int:
        return self._underlying_digraph.ecount()

    @property
    def node_ids(self) -> list[NodeId]:
        if self._underlying_digraph.vcount() == 0:
            return []
        return self._underlying_digraph.vs[VERTEX_NAME_KEY]

    @property
    def all_edges(self) -> igraph.EdgeSeq:
        return self._underlying_digraph.es

    @property
    def end_node_id_pair_iterator(self) -> Iterator[EndNodeIdPair]:
        warnings.warn(
            "end_node_id_pair_iterator is deprecated, use iter_end_node_id_pairs() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.iter_end_node_id_pairs()

    def iter_end_node_id_pairs(self) -> Iterator[EndNodeIdPair]:
        return (
            EndNodeIdPair((es.source_vertex[VERTEX_NAME_KEY], es.target_vertex[VERTEX_NAME_KEY]))
            for es in self._underlying_digraph.es
        )  # noqa

    @property
    def edge_tuple_iterator(self) -> Iterator[tuple[NodeIndex, NodeIndex]]:
        warnings.warn(
            "edge_tuple_iterator is deprecated, use iter_edge_tuples() instead", DeprecationWarning, stacklevel=2
        )
        return self.iter_edge_tuples()

    def iter_edge_tuples(self) -> Iterator[tuple[NodeIndex, NodeIndex]]:
        return (es.tuple for es in self._underlying_digraph.es)

    @property
    def all_links(self) -> list[LinkT]:
        if self._underlying_digraph.vcount() == 0:
            return []
        return self._underlying_digraph.es[LINK_ATTRIBUTE_KEY]

    @property
    def all_nodes(self) -> list[NodeT]:
        if self._underlying_digraph.vcount() == 0:
            return []
        return self._underlying_digraph.vs[NODE_ATTRIBUTE_KEY]

    def node_index_by_id(self, node_id: NodeId) -> NodeIndex:
        """Return the index for the node with ``node_id``."""
        return self._underlying_digraph.vs.find(node_id).index

    def node_index_by_name(self, node_name: NodeId) -> NodeIndex:
        warnings.warn(
            "node_index_by_name is deprecated, use node_index_by_id() instead", DeprecationWarning, stacklevel=2
        )
        return self.node_index_by_id(node_name)

    def node_id_by_index(self, node_index: NodeIndex) -> NodeId:
        """Return the node id for ``node_index``."""
        return self._underlying_digraph.vs[VERTEX_NAME_KEY][node_index]

    def node_name_by_index(self, node_index: NodeIndex) -> NodeId:
        warnings.warn(
            "node_name_by_index is deprecated, use node_id_by_index() instead", DeprecationWarning, stacklevel=2
        )
        return self.node_id_by_index(node_index)

    def node_by_index(self, node_index: NodeIndex) -> NodeT:
        return self._underlying_digraph.vs[NODE_ATTRIBUTE_KEY][node_index]

    def node_by_id(self, n_id: NodeId) -> NodeT:
        return self.node_by_index(self.node_index_by_id(n_id))

    def link_index_by_source_target(self, source: NodeId | NodeIndex, target: NodeId | NodeIndex) -> LinkIndex:
        return self._underlying_digraph.get_eid(source, target)

    def link_source_target_by_index(self, idx: LinkIndex) -> tuple[NodeIndex, NodeIndex]:
        return self._underlying_digraph.es[idx].tuple

    def link_index_by_end_node_id_pair(self, end_nodes: EndNodeIdPair) -> LinkIndex:
        return self._underlying_digraph.get_eid(end_nodes[0], end_nodes[1])

    def edge_by_index(self, idx: LinkIndex) -> igraph.Edge:
        return self._underlying_digraph.es.find(idx)

    def edge_by_source_target(self, source: NodeId | NodeIndex, target: NodeId | NodeIndex) -> igraph.Edge:
        return self._underlying_digraph.es.find(_from=source, _to=target)

    def link_by_index(self, idx: LinkIndex) -> LinkT:
        return self._underlying_digraph.es[LINK_ATTRIBUTE_KEY][idx]

    def link_by_source_target(self, source_id: NodeId | NodeIndex, target_id: NodeId | NodeIndex) -> LinkT:
        return self.link_by_index(self.link_index_by_source_target(source_id, target_id))

    def link_by_end_node_id_pair(self, end_nodes: EndNodeIdPair) -> LinkT:
        return self.link_by_index(self.link_index_by_source_target(end_nodes[0], end_nodes[1]))

    def link_end_node_id_pair_by_index(self, index: LinkIndex) -> EndNodeIdPair:
        edge = self.edge_by_index(index)
        return EndNodeIdPair((edge.source_vertex[VERTEX_NAME_KEY], edge.target_vertex[VERTEX_NAME_KEY]))

    def link_by_end_node_iterator(self) -> Iterator[tuple[EndNodeIdPair, LinkT]]:
        warnings.warn(
            "link_by_end_node_iterator is deprecated, use iter_links_with_end_nodes() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.iter_links_with_end_nodes()

    def iter_links_with_end_nodes(self) -> Iterator[tuple[EndNodeIdPair, LinkT]]:
        return zip(self.iter_end_node_id_pairs(), self.all_links)

    def link_by_tuple_iterator(self) -> Iterator[tuple[tuple[NodeIndex, NodeIndex], LinkT]]:
        warnings.warn(
            "link_by_tuple_iterator is deprecated, use iter_links_with_indices() instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.iter_links_with_indices()

    def iter_links_with_indices(self) -> Iterator[tuple[tuple[NodeIndex, NodeIndex], LinkT]]:
        return zip((es.tuple for es in self._underlying_digraph.es), self.all_links)

    def in_degrees(self) -> list[int]:
        return self._underlying_digraph.indegree()

    def out_degrees(self) -> list[int]:
        return self._underlying_digraph.outdegree()

    def degrees(self) -> list[int]:
        return self._underlying_digraph.degree()

    def incident_links_per_node(
        self, idx: NodeId | NodeIndex, mode: Literal["in", "out", "all"] = "all"
    ) -> list[LinkT]:
        return [
            self._underlying_digraph.es[i][LINK_ATTRIBUTE_KEY] for i in self._underlying_digraph.incident(idx, mode)
        ]

    def incident_link_idx_per_node(
        self, idx: NodeId | NodeIndex, mode: Literal["in", "out", "all"] = "all"
    ) -> list[LinkIndex]:
        return self._underlying_digraph.incident(vertex=idx, mode=mode)

    def neighbors(self, idx: NodeId | NodeIndex, mode: Literal["in", "out", "all"] = "all") -> list[NodeT]:
        return self._underlying_digraph.vs[self._underlying_digraph.neighbors(vertex=idx, mode=mode)][
            NODE_ATTRIBUTE_KEY
        ]

    @classmethod
    def create_empty(cls: Type[Self]) -> Self:
        return cls(igraph.Graph(directed=True))

    def copy(self: Self) -> Self:
        """Return a shallow copy of this network."""
        return self.__class__(self._underlying_digraph.copy())

    @property
    def shallow_copy(self: Self) -> Self:
        """Return a shallow copy of this network (deprecated)."""
        warnings.warn("shallow_copy is deprecated, use copy() instead", DeprecationWarning, stacklevel=2)
        return self.copy()

    def nodes_by_indices(self, indices: Iterable[NodeIndex]) -> list[NodeT]:
        return self._underlying_digraph.vs.select(indices)[NODE_ATTRIBUTE_KEY]

    def nodes_by_indexes(self, indexes: Iterable[NodeIndex]) -> list[NodeT]:
        warnings.warn(
            "nodes_by_indexes is deprecated, use nodes_by_indices() instead", DeprecationWarning, stacklevel=2
        )
        return self.nodes_by_indices(indexes)

    def nodes_by_ids(self, ids: Iterable[NodeId]) -> list[NodeT]:
        """Return the nodes for the given ids."""
        return self._underlying_digraph.vs.select(name_in=ids)[NODE_ATTRIBUTE_KEY]

    def nodes_by_names(self, names: Iterable[NodeId]) -> list[NodeT]:
        warnings.warn("nodes_by_names is deprecated, use nodes_by_ids() instead", DeprecationWarning, stacklevel=2)
        return self.nodes_by_ids(names)

    def links_by_indices(self, indices: Iterable[LinkIndex]) -> list[LinkT]:
        return self._underlying_digraph.es.select(indices)[LINK_ATTRIBUTE_KEY]

    def links_by_indexes(self, indexes: Iterable[LinkIndex]) -> list[LinkT]:
        warnings.warn(
            "links_by_indexes is deprecated, use links_by_indices() instead", DeprecationWarning, stacklevel=2
        )
        return self.links_by_indices(indexes)

    def weak_components(self: Self) -> tuple[Self, ...]:
        return tuple(self.__class__(graph) for graph in self._underlying_digraph.components(mode="weak").subgraphs())

    def debug_plot(self, file_name: Path | str | None = None, with_labels: bool = True, **kwargs: Any) -> None:
        debug_plot(self._underlying_digraph, with_labels, file_name, **kwargs)

    def write_json(self, path: Path | str) -> None:
        assert str(path).endswith(
            f"{self.__class__.__name__}.json"
        ), f"File name must end with {self.__class__.__name__}.json"
        with open(path, "w") as file:
            json.dump(self, file, cls=ImmutableNetworkEncoder)

    @classmethod
    def read_json(cls: Type[Self], path: Path | str) -> Self:
        assert str(path).endswith(f"{cls.__name__}.json"), f"File name must end with {cls.__name__}.json"
        with open(path, "r") as file:
            return json.load(file, cls=ImmutableNetworkDecoder)


class ImmutableNetworkEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, igraph.Graph):
            igraph_dict = _serialize_igraph(o)
            igraph_dict["__class__"] = "igraph.Graph"
            return igraph_dict
        if isinstance(o, NodeABC | LinkABC):
            data = asdict(o)
            data["__class__"] = f"{o.__class__.__module__}.{o.__class__.__name__}"
            return data
        if isinstance(o, ImmutableNetworkABC):
            data = asdict(o)
            data["__class__"] = f"{o.__class__.__module__}.{o.__class__.__name__}"
            return data
        if isinstance(o, set | frozenset):
            return list(o)
        return super().default(o)


class ImmutableNetworkDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    @staticmethod
    def object_hook(dct: dict[str, Any]) -> Any:  # pylint: disable=method-hidden
        if "__class__" in dct:
            class_name: str = dct["__class__"]
            del dct["__class__"]

            if class_name == "igraph.Graph":
                return _deserialize_igraph(dct)

            module_name, class_name = class_name.rsplit(".", 1)
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            return _dataclass_from_dict(cls, dct)

        return dct


def _dataclass_from_dict(cls: type, data: dict[str, Any | None] | Any) -> Any:
    # handle type unions
    if get_origin(cls) is Union or get_origin(cls) is UnionType:
        for arg in get_args(cls):
            try:
                return _dataclass_from_dict(arg, data)
            except Exception as exception:  # pylint: disable=broad-except
                print(f"Failed to convert {data} to {arg}: {exception}", flush=True)
        raise ValueError(f"Could not convert {data} to any of {get_args(cls)}")

    # handle types defined with NewType
    if hasattr(cls, "__supertype__"):
        supertype = cls.__supertype__
        return cls(_dataclass_from_dict(supertype, data))

    # handle Literal types
    if get_origin(cls) is Literal:
        if data in get_args(cls):
            return data  # Valid literal value
        raise ValueError(f"Value {data} is not a valid Literal for {cls}")

    # handle non dataclass types
    if not is_dataclass(cls):
        if isinstance(data, igraph.Graph) or data is None:
            return data
        return cls(data)

    field_types = get_type_hints(cls)
    result = {}
    for _type in field_types:
        if _type not in data:
            continue
        # catch ellipsis type hints
        args = get_args(field_types[_type])
        if len(args) > 0 and args[-1] is Ellipsis:
            # This is a variadic tuple, convert each list item into the appropriate type
            elem_type = args[0]  # The type of the tuple's elements
            result[_type] = tuple(_dataclass_from_dict(elem_type, item) for item in data[_type])  # type: ignore
        else:
            # Handle non-ellipsis types normally
            result[_type] = (
                _dataclass_from_dict(field_types[_type], data[_type]) if _type in data else None  # type: ignore
            )
    return cls(**result)


def _serialize_igraph(graph: igraph.Graph) -> dict[str, Any]:
    return {
        "node_count": graph.vcount(),
        "edges": graph.get_edgelist(),
        "attributes": {key: graph[key] for key in graph.attributes()},
        "vertex_attrs": [v.attributes() for v in graph.vs],
        "edge_attrs": [e.attributes() for e in graph.es],
        "is_directed": graph.is_directed(),
    }


def _deserialize_igraph(data: dict[str, Any]) -> igraph.Graph:
    edge_attr_keys = next(iter(data["edge_attrs"])).keys() if data["edge_attrs"] else []
    vertex_attr_keys = next(iter(data["vertex_attrs"])).keys() if data["vertex_attrs"] else []
    return igraph.Graph(
        n=data["node_count"],
        edges=data["edges"],
        directed=data["is_directed"],
        graph_attrs=data["attributes"],
        edge_attrs={k: [d[k] for d in data["edge_attrs"]] for k in edge_attr_keys},
        vertex_attrs={k: [d[k] for d in data["vertex_attrs"]] for k in vertex_attr_keys},
    )
