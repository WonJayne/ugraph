from abc import ABC
from dataclasses import dataclass
from enum import IntEnum, unique
from typing import NewType

from ugraph._abc._node import NodeId

EndNodeIdPair = NewType("EndNodeIdPair", tuple[NodeId, NodeId])


@unique
class BaseLinkType(IntEnum):
    pass


@dataclass(frozen=True, slots=True)
class LinkABC(ABC):
    link_type: BaseLinkType


@unique
class SpeedCategory(IntEnum):
    pass
