from abc import ABC
from dataclasses import dataclass
from enum import IntEnum, unique
from typing import Generic, NewType, TypeVar

from ugraph._abc._node import NodeId

EndNodeIdPair = NewType("EndNodeIdPair", tuple[NodeId, NodeId])


@unique
class BaseLinkType(IntEnum):
    pass


LinkTypeT = TypeVar("LinkTypeT", bound=BaseLinkType)


@dataclass(frozen=True, slots=True)
class LinkABC(Generic[LinkTypeT], ABC):
    link_type: LinkTypeT
