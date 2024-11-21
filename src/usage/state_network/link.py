from enum import unique

from ugraph import BaseLinkType, LinkABC


@unique
class StateLinkType(BaseLinkType):
    OCCUPATION = 0
    RESERVATION = 1
    ALLOCATION = 2
    TRANSITION = 3


class StateLink(LinkABC):
    link_type: StateLinkType
