from __future__ import annotations

from abc import ABC
from collections.abc import Collection
from dataclasses import dataclass
from enum import IntEnum, unique
from statistics import mean
from typing import Generic, NewType, Type, TypeVar

NodeId = NewType("NodeId", str)
ClusterId = NodeId
EndNodeIds = NewType("EndNodeIds", tuple[NodeId, ...])
NodeIndex = NewType("NodeIndex", int)


@unique
class BaseNodeType(IntEnum):
    pass


NodeT = TypeVar("NodeT", bound=BaseNodeType)


@dataclass(frozen=True, slots=True)
class NodeABC(ABC, Generic[NodeT]):
    id: NodeId
    coordinates: ThreeDCoordinates
    node_type: NodeT


T = TypeVar("T", bound="ThreeDCoordinates")


@dataclass(frozen=True, slots=True)
class ThreeDCoordinates:
    x: float  # pylint: disable=invalid-name
    y: float  # pylint: disable=invalid-name
    z: float  # pylint: disable=invalid-name

    def __add__(self, other: ThreeDCoordinates) -> ThreeDCoordinates:
        return ThreeDCoordinates(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: ThreeDCoordinates) -> ThreeDCoordinates:
        return ThreeDCoordinates(self.x - other.x, self.y - other.y, self.z - other.z)

    @classmethod
    def create_mean_location_coordinates(cls: Type[T], coordinates: Collection[ThreeDCoordinates]) -> T:
        return cls(mean(c.x for c in coordinates), mean(c.y for c in coordinates), mean(c.z for c in coordinates))


def node_distance(n_1: NodeABC, n_2: NodeABC) -> float:
    c_1, c_2 = n_1.coordinates, n_2.coordinates
    if c_1.z == 0 == c_2.z:
        return ((c_1.x - c_2.x) ** 2 + (c_1.y - c_2.y) ** 2) ** 0.5
    return ((c_1.x - c_2.x) ** 2 + (c_1.y - c_2.y) ** 2 + (c_1.z - c_2.z) ** 2) ** 0.5
