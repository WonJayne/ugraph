from abc import ABC
from dataclasses import dataclass
from enum import IntEnum, unique
from typing import Generic, NewType, TypeVar

from ugraph._abc._node import NodeId

EndNodeIdPair = NewType("EndNodeIdPair", tuple[NodeId, NodeId])


@unique
class BaseLinkType(IntEnum):
    pass


LinkT = TypeVar("LinkT", bound="LinkABC")


@dataclass(frozen=True, slots=True)
class LinkABC(Generic[LinkT], ABC):
    link_type: LinkT
