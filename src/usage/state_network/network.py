from collections import defaultdict

from ugraph import MutableNetworkABC, NodeIndex
from usage.state_network.link import StateLink, StateLinkType
from usage.state_network.node import StateNode, StateNodeType
from usage.utils.result import Result


class StateNetwork(MutableNetworkABC[StateNode, StateLink, StateNodeType, StateLinkType]):

    def reduce_to_agent_network(self) -> "StateNetwork":
        copied = self.shallow_copy
        copied.delete_nodes_without_type(frozenset((StateNodeType.AGENT,)))
        return copied

    def reduce_to_resource_network(self) -> "StateNetwork":
        copied = self.shallow_copy
        copied.delete_nodes_without_type(frozenset((StateNodeType.RESOURCE,)))
        return copied

    def reduce_to_transition_network(self) -> "StateNetwork":
        copied = self.shallow_copy
        copied.delete_nodes_without_type(frozenset((StateNodeType.INFRASTRUCTURE,)))
        return copied

    def reduce_to_resource_and_infrastructure_network(self) -> "StateNetwork":
        copied = self.shallow_copy
        copied.delete_nodes_without_type(frozenset((StateNodeType.RESOURCE, StateNodeType.INFRASTRUCTURE)))
        return copied

    def reduce_to_infrastructure_and_agent_network(self) -> "StateNetwork":
        copied = self.shallow_copy
        copied.delete_nodes_without_type(frozenset((StateNodeType.INFRASTRUCTURE, StateNodeType.AGENT)))
        return copied

    def validate_topology(self) -> Result[bool, str]:
        return _validate_topology(self)


def _validate_topology(state_network: StateNetwork) -> Result[bool, str]:
    node_result = _validate_node_incidence(state_network)
    if not node_result:
        return node_result
    return _validate_network_incidence(state_network)


def _validate_network_incidence(state_network):
    infra_only = state_network.reduce_to_transition_network()
    for component in infra_only.weak_components():
        if not component.underlying_digraph.is_dag():
            component.debug_plot(file_name=f"inconsistent_infra.png")
            return Result.from_failure(f"Infrastructure component {component} is not a DAG")
        if not component.underlying_digraph.is_simple():
            component.debug_plot(file_name=f"inconsistent_infra.png")
            return Result.from_failure(f"Infrastructure component {component} has more than one node")
    except_transitions = state_network.shallow_copy
    for component in except_transitions.weak_components():
        if not component.underlying_digraph.is_dag():
            component.debug_plot(file_name=f"inconsistent_transitions.png")
            return Result.from_failure(f"Component {component} is not a DAG")
        if not component.underlying_digraph.is_simple():
            component.debug_plot(file_name=f"inconsistent_transitions.png")
            return Result.from_failure(f"Component {component} has more than one node")
    return Result.from_success(True)


def _validate_node_incidence(state_network):
    outgoing_links = defaultdict(list)
    incoming_links = defaultdict(list)
    for (s, t), link in state_network.link_by_tuple_iterator():
        outgoing_links[s].append(link)
        incoming_links[t].append(link)
    for i, node in enumerate(state_network.all_nodes):
        i: NodeIndex
        if node.node_type == StateNodeType.AGENT:
            if len(incoming_links[i]) > 0:
                return Result.from_failure(f"Agent node {i} has incoming links")
            for link in outgoing_links[i]:
                if link.link_type not in {StateLinkType.OCCUPATION, StateLinkType.RESERVATION}:
                    return Result.from_failure(f"Agent node {i} has non-occupation link")
            continue
        if node.node_type == StateNodeType.RESOURCE:
            if len(outgoing_links[i]) > 0:
                return Result.from_failure(f"Resource node {i} has outgoing links")
            for link in incoming_links[i]:
                if link.link_type != StateLinkType.ALLOCATION:
                    return Result.from_failure(f"Resource node {i} has non-occupation link")
            continue
        if node.node_type == StateNodeType.INFRASTRUCTURE:
            for link in incoming_links[i]:
                if link.link_type not in {
                    StateLinkType.RESERVATION,
                    StateLinkType.OCCUPATION,
                    StateLinkType.TRANSITION,
                }:
                    return Result.from_failure(
                        f"Infrastructure node {i} has a non allowed incoming link {link.link_type}"
                    )
            for link in outgoing_links[i]:
                if link.link_type not in {StateLinkType.ALLOCATION, StateLinkType.TRANSITION}:
                    return Result.from_failure(
                        f"Infrastructure node {i} has a non allowed outgoing link {link.link_type}"
                    )
            continue
        return Result.from_failure(f"Node {i} has an unknown type {node.node_type}")
    return Result.from_success(True)
