from abc import ABC
from collections.abc import Collection, Iterable, Mapping
from dataclasses import dataclass
from typing import AbstractSet, TypeVar

import igraph

from ugraph._abc._immutablenetwork import (
    VERTEX_NAME_IN_GRAPH,
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
        assert self.node_attribute_name == network_to_append.node_attribute_name
        assert self.link_attribute_name == network_to_append.link_attribute_name
        _append_to_network(self, network_to_append)

    def replace_node(self, index: NodeIndex, updated: NodeT, renamed: bool = False) -> None:
        _replace_node(self, index, updated, renamed)

    def replace_link(self, index: LinkIndex, new_link: LinkT) -> None:
        self._underlying_digraph.es[index][self.link_attribute_name] = new_link

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

    def delete_nodes(self, to_remove: Iterable[NodeIndex] | Iterable[NodeId]) -> None:
        self._underlying_digraph.delete_vertices(to_remove)

    def delete_links(self, to_remove: Iterable[LinkIndex]) -> None:
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
    node_attr_name = network.node_attribute_name
    iterator_ = nodes.items() if isinstance(nodes, Mapping) else ((node.id, node) for node in nodes)  # mypy: ignore
    for i, (node_id, node) in enumerate(iterator_, start=v_count_before):
        network.underlying_digraph.vs[i][node_attr_name] = node
        network.underlying_digraph.vs[i][VERTEX_NAME_IN_GRAPH] = node_id


def _add_links(mutable_network: MutableNetworkABC, links_to_add: Collection[tuple[EndNodeIdPair, LinkT]]) -> None:
    if len(links_to_add) == 0:
        return
    end_nodes, links = zip(*links_to_add)
    e_count_before = mutable_network.underlying_digraph.ecount()
    mutable_network.underlying_digraph.add_edges(end_nodes)
    link_name = mutable_network.link_attribute_name
    for i, link in enumerate(links, start=e_count_before):
        mutable_network.underlying_digraph.es[i][link_name] = link


def _append_to_network(
    network_to_extend: MutableNetworkABC, network_to_append: ImmutableNetworkABC, skip_duplicate_nodes: bool = True
) -> None:
    if skip_duplicate_nodes:
        existing_node_ids = set(network_to_extend.node_ids)
        nodes_to_add = {node.id: node for node in network_to_append.all_nodes if node.id not in existing_node_ids}
        network_to_extend.add_nodes(nodes_to_add)
    else:
        assert (
            set(network_to_extend.node_ids).difference(network_to_append.node_ids) == {}
        ), f"{set(network_to_extend.node_ids).difference(network_to_append.node_ids) == {} }"

        network_to_extend.add_nodes({node.id: node for node in network_to_append.all_nodes})
    links_to_add = tuple(network_to_append.link_by_end_node_iterator())
    if len(links_to_add) > 0:
        network_to_extend.add_links(links_to_add)


def _replace_node(network: MutableNetworkABC, index: NodeIndex, new_node: NodeT, renamed: bool) -> None:
    if network.underlying_digraph.vs[index][VERTEX_NAME_IN_GRAPH] != new_node.id:
        if not renamed:
            raise ValueError(
                f"Node id mismatch: {network.underlying_digraph.vs[index][VERTEX_NAME_IN_GRAPH]} != {new_node.id}"
            )
        assert new_node.id not in set(network.underlying_digraph.vs[VERTEX_NAME_IN_GRAPH]), f"{new_node.id=} not unique"
        network.underlying_digraph.vs[index][VERTEX_NAME_IN_GRAPH] = new_node.id
    network.underlying_digraph.vs[index][network.node_attribute_name] = new_node


def _delete_nodes_without_event_type(self: MutableNetworkABC, types: Iterable[BaseNodeType]) -> None:
    if not isinstance(types, (set, frozenset)):
        types = frozenset(types)
    self.delete_nodes([i for i, n in enumerate(self.all_nodes) if n.node_type not in types])  # type: ignore


def _delete_nodes_with_event_type(self: MutableNetworkABC, types: Iterable[BaseNodeType]) -> None:
    if not isinstance(types, (set, frozenset)):
        types = frozenset(types)
    self.delete_nodes([i for i, n in enumerate(self.all_nodes) if n.node_type in types])  # type: ignore