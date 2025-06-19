from enum import unique

from ugraph import BaseNodeType, NodeABC, NodeId, ThreeDCoordinates


@unique
class StateNodeType(BaseNodeType):
    RESOURCE = 0
    INFRASTRUCTURE = 1
    AGENT = 2


class StateNode(NodeABC):
    node_type: StateNodeType
    coordinates: ThreeDCoordinates
    node_id: NodeId
