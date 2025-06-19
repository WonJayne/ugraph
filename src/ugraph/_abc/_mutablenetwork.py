from abc import ABC
from collections.abc import Collection, Iterable, Mapping
from dataclasses import dataclass
from typing import AbstractSet, TypeVar

import igraph

from ugraph._abc._immutablenetwork import (
    LINK_ATTRIBUTE_KEY,
    NODE_ATTRIBUTE_KEY,
    VERTEX_NAME_KEY,
    ImmutableNetworkABC,
    LinkIndex,
    LinkT,
    LinkTypeT,
    NodeT,
    NodeTypeT,
)
from ugraph._abc._link import EndNodeIdPair
from ugraph._abc._node import BaseNodeType, NodeId, NodeIndex

Self = TypeVar("Self", bound="MutableNetworkABC")


@dataclass(init=False, frozen=True)
class MutableNetworkABC(ImmutableNetworkABC[NodeT, LinkT, NodeTypeT, LinkTypeT], ABC):
    @property
    def underlying_digraph(self) -> igraph.Graph:
        return self._underlying_digraph

    def isomorphic(self, other: Self) -> bool:
        return self._underlying_digraph.isomorphic(other.underlying_digraph)

    def add_nodes(self, nodes_to_add: Mapping[NodeId, NodeT] | Collection[NodeT]) -> None:
        _add_nodes(self, nodes_to_add)

    def add_links(self, links_to_add: Collection[tuple[EndNodeIdPair, LinkT]] | Mapping[EndNodeIdPair, LinkT]) -> None:
        if isinstance(links_to_add, dict):
            return _add_links(self, links_to_add.items())  # type: ignore
        return _add_links(self, links_to_add)  # type: ignore

    def append_(self, network_to_append: ImmutableNetworkABC[NodeT, LinkT, NodeTypeT, LinkTypeT]) -> None:
        _append_to_network(self, network_to_append)

    def replace_node(self, index: NodeIndex, updated: NodeT, renamed: bool = False) -> None:
        _replace_node(self, index, updated, renamed)

    def replace_link(self, index: LinkIndex, new_link: LinkT) -> None:
        self._underlying_digraph.es[index][LINK_ATTRIBUTE_KEY] = new_link

    def remove_isolated_nodes(self) -> None:
        self._underlying_digraph.delete_vertices(self._underlying_digraph.vs.select(_degree=0))

    def __add__(self: Self, other: Self) -> Self:
        return self.__class__(self._underlying_digraph.union(other.underlying_digraph, byname=True))

    def sub_network(self: Self, selected: Collection[NodeIndex] | Collection[NodeId]) -> Self:
        return self.__class__(self._underlying_digraph.subgraph(selected))

    def delete_nodes_with_type(self, types: AbstractSet[NodeTypeT]) -> None:
        self._underlying_digraph.delete_vertices([i for i, n in enumerate(self.all_nodes) if n.node_type in types])

    def delete_nodes_without_type(self, types: AbstractSet[NodeTypeT]) -> None:
        self._underlying_digraph.delete_vertices([i for i, n in enumerate(self.all_nodes) if n.node_type not in types])

    def delete_links_without_type(self, types: AbstractSet[LinkTypeT]) -> None:
        self.delete_links([LinkIndex(i) for i, link in enumerate(self.all_links) if link.link_type not in types])

    def delete_links_with_type(self, types: AbstractSet[LinkTypeT]) -> None:
        self.delete_links([LinkIndex(i) for i, link in enumerate(self.all_links) if link.link_type in types])

    def delete_nodes(self, to_remove: Collection[NodeIndex] | Collection[NodeId]) -> None:
        self._underlying_digraph.delete_vertices(to_remove)

    def delete_links(self, to_remove: Collection[LinkIndex]) -> None:
        self._underlying_digraph.delete_edges(to_remove)

    @classmethod
    def create_new(cls: type[Self], nodes: Collection[NodeT], links: Collection[tuple[EndNodeIdPair, LinkT]]) -> Self:
        new = cls.create_empty()
        new.add_nodes(nodes)
        new.add_links(links)
        return new


def _add_nodes(network: MutableNetworkABC, nodes: Mapping[NodeId, NodeT] | Collection[NodeT]) -> None:
    v_count_before = network.underlying_digraph.vcount()
    network.underlying_digraph.add_vertices(len(nodes))
    node_pairs = ((node.node_id, node) for node in nodes)  # type: ignore
    iterator_ = nodes.items() if isinstance(nodes, Mapping) else node_pairs  # type: ignore
    for i, (node_id, node) in enumerate(iterator_, start=v_count_before):
        network.underlying_digraph.vs[i][NODE_ATTRIBUTE_KEY] = node
        network.underlying_digraph.vs[i][VERTEX_NAME_KEY] = node_id


def _add_links(mutable_network: MutableNetworkABC, links_to_add: Collection[tuple[EndNodeIdPair, LinkT]]) -> None:
    if len(links_to_add) == 0:
        return
    end_nodes, links = zip(*links_to_add)
    e_count_before = mutable_network.underlying_digraph.ecount()
    mutable_network.underlying_digraph.add_edges(end_nodes)
    for i, link in enumerate(links, start=e_count_before):
        mutable_network.underlying_digraph.es[i][LINK_ATTRIBUTE_KEY] = link


def _append_to_network(
    network_to_extend: MutableNetworkABC, network_to_append: ImmutableNetworkABC, skip_duplicate_nodes: bool = True
) -> None:
    if skip_duplicate_nodes:
        existing_node_ids = set(network_to_extend.node_ids)
        nodes_to_add = {
            node.node_id: node for node in network_to_append.all_nodes if node.node_id not in existing_node_ids
        }
        network_to_extend.add_nodes(nodes_to_add)
    else:
        assert not (overlap := set(network_to_extend.node_ids).intersection(network_to_append.node_ids)), f"{overlap=}"

        network_to_extend.add_nodes({node.node_id: node for node in network_to_append.all_nodes})
    links_to_add = tuple(network_to_append.iter_links_with_end_nodes())
    if len(links_to_add) > 0:
        network_to_extend.add_links(links_to_add)


def _replace_node(network: MutableNetworkABC, index: NodeIndex, new_node: NodeT, renamed: bool) -> None:
    if network.underlying_digraph.vs[index][VERTEX_NAME_KEY] != new_node.node_id:
        if not renamed:
            raise ValueError(
                f"Node id mismatch: {network.underlying_digraph.vs[index][VERTEX_NAME_KEY]} != {new_node.node_id}"
            )
        assert new_node.node_id not in set(
            network.underlying_digraph.vs[VERTEX_NAME_KEY]
        ), f"{new_node.node_id=} not unique"
        network.underlying_digraph.vs[index][VERTEX_NAME_KEY] = new_node.node_id
    network.underlying_digraph.vs[index][NODE_ATTRIBUTE_KEY] = new_node


def _delete_nodes_without_event_type(self: MutableNetworkABC, types: Iterable[BaseNodeType]) -> None:
    if not isinstance(types, (set, frozenset)):
        types = frozenset(types)
    self.delete_nodes([i for i, n in enumerate(self.all_nodes) if n.node_type not in types])  # type: ignore


def _delete_nodes_with_event_type(self: MutableNetworkABC, types: Iterable[BaseNodeType]) -> None:
    if not isinstance(types, (set, frozenset)):
        types = frozenset(types)
    self.delete_nodes([i for i, n in enumerate(self.all_nodes) if n.node_type in types])  # type: ignore
