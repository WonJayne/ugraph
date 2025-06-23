from dataclasses import dataclass
from enum import unique

from ugraph import BaseLinkType, LinkABC


@unique
class StateLinkType(BaseLinkType):
    OCCUPATION = 0
    RESERVATION = 1
    ALLOCATION = 2
    TRANSITION = 3


@dataclass(frozen=True)
class StateLink(LinkABC[StateLinkType]):
    link_type: StateLinkType
