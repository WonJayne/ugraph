# ugraph

[![PyPI version](https://badge.fury.io/py/ugraph.svg)](https://pypi.org/project/ugraph/)
[![Downloads](https://pepy.tech/badge/ugraph)](https://pepy.tech/project/ugraph)
[![Python](https://img.shields.io/pypi/pyversions/ugraph.svg)](https://pypi.org/project/ugraph/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

`ugraph` is a small typed domain-model layer on top of
[python-igraph](https://python.igraph.org/). It stores immutable Python objects as nodes and links,
while keeping igraph's graph structure and algorithms available underneath.

Use it when a graph is part of your domain model—not merely an intermediate data structure—and raw
vertex and edge attribute dictionaries would hide too much meaning.

In OpenBus, for example, a timetable network represents railway events as nodes and operational
activities or constraints as directed links. Its network subclass then adds timetable-specific
validation and transformations; `ugraph` supplies the reusable typed graph machinery.

## What it provides

- typed node, link, and network base classes;
- directed graph construction, mutation, filtering, and component operations;
- direct access to the underlying `igraph.Graph` for graph algorithms;
- JSON round-tripping for dataclass-based networks;
- basic debugging plots and Plotly-based 3D visualization.

## Installation

```bash
pip install ugraph
```

Use `pip install ugraph[cairo]` if you need igraph's Cairo-based plotting support.

## Quick start

This small event-activity network follows the same pattern as OpenBus's `TimeTableNetwork`, but
leaves out the railway-specific detail:

```python
from dataclasses import dataclass

from ugraph import (
    BaseLinkType,
    BaseNodeType,
    EndNodeIdPair,
    LinkABC,
    MutableNetworkABC,
    NodeABC,
    NodeId,
    ThreeDCoordinates,
)


class EventType(BaseNodeType):
    ARRIVAL = 0
    DEPARTURE = 1


class ActivityType(BaseLinkType):
    DWELL = 0


@dataclass(frozen=True, slots=True)
class Event(NodeABC[EventType]):
    node_type: EventType
    station: str


@dataclass(frozen=True, slots=True)
class Activity(LinkABC[ActivityType]):
    link_type: ActivityType
    duration_minutes: int


class EventActivityNetwork(
    MutableNetworkABC[Event, Activity, EventType, ActivityType]
):
    def is_acyclic(self) -> bool:
        return self.underlying_digraph.is_dag()


arrival = Event(
    node_id=NodeId("arrival:central"),
    coordinates=ThreeDCoordinates(0, 0, 0),
    node_type=EventType.ARRIVAL,
    station="Central",
)
departure = Event(
    node_id=NodeId("departure:central"),
    coordinates=ThreeDCoordinates(1, 0, 0),
    node_type=EventType.DEPARTURE,
    station="Central",
)

network = EventActivityNetwork.create_new(
    nodes=(arrival, departure),
    links=((
        EndNodeIdPair((arrival.node_id, departure.node_id)),
        Activity(ActivityType.DWELL, duration_minutes=2),
    ),),
)

assert network.is_acyclic()
assert network.n_count == 2
assert network.l_count == 1
```

The important pattern is the separation of responsibilities: dataclasses describe domain objects,
the network subclass holds domain operations and validation, and igraph handles generic graph
algorithms.

For serialization, mutation, visualization, and further examples, see the
[getting-started guide](docs/getting_started.md) and the
[example sources](https://github.com/WonJayne/ugraph/tree/main/src/usage).

## Scope

`ugraph` supports directed graphs with typed domain objects. It is not a general charting library or
a replacement for igraph; it deliberately builds on igraph.

## License

MIT; see [LICENSE](LICENSE).
