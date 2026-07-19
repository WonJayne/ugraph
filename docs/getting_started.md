# Getting started with `ugraph`

`ugraph` combines domain-specific Python dataclasses with a directed `igraph.Graph`. The
[README](../README.md) contains a complete minimal example; this guide shows the operations that
usually come next.

## The model

A `ugraph` model has three parts:

1. a `NodeABC` subclass containing a stable `NodeId`, 3D coordinates, a node type, and domain data;
2. a `LinkABC` subclass containing a link type and domain data;
3. an `ImmutableNetworkABC` or `MutableNetworkABC` subclass containing domain-level operations and
   validation.

The network stores the typed objects on an underlying `igraph.Graph`. Use the `ugraph` API for typed
access and `network.underlying_digraph` when an igraph algorithm is the clearest tool.

## Constructing and inspecting a network

Create a mutable network in one step:

```python
network = EventActivityNetwork.create_new(
    nodes=(arrival, departure),
    links=((EndNodeIdPair((arrival.node_id, departure.node_id)), dwell),),
)
```

The main read APIs are:

```python
network.all_nodes
network.all_links
network.node_ids
network.iter_links_with_end_nodes()
network.neighbors(arrival.node_id, mode="out")
network.weak_components()
```

For a subset, use node IDs or indices:

```python
station_view = network.sub_network((arrival.node_id, departure.node_id))
```

`MutableNetworkABC` additionally supports `add_nodes`, `add_links`, replacement, deletion, and
type-based filtering. `copy()` returns an independent graph structure containing the same immutable
node and link objects.

## Adding domain behavior

Keep domain rules on the network subclass. This is the central pattern used by OpenBus's timetable
networks:

```python
class EventActivityNetwork(
    MutableNetworkABC[Event, Activity, EventType, ActivityType]
):
    def validate_consistency(self) -> bool:
        if not self.underlying_digraph.is_dag():
            raise ValueError("Event-activity network must be acyclic")
        return True
```

This keeps generic graph mechanics in `ugraph` and domain semantics in the consuming package.

## JSON round-tripping

Dataclass-based networks can be written and reconstructed with their concrete node, link, and
network types:

```python
from pathlib import Path

path = Path("example.EventActivityNetwork.json")
network.write_json(path)
loaded = EventActivityNetwork.read_json(path)
```

The file name must end in `<NetworkClass>.json`. The involved classes must remain importable under
the module names stored in the JSON document.

## Visualization

For a quick structural debugging image:

```python
network.debug_plot("network.png")
```

For interactive 3D output, use the helpers under `ugraph.plot`. Node coordinates determine their
positions; a `ColorMap` maps node and link types to colors. See
[`src/usage/minimal_example.py`](../src/usage/minimal_example.py) for a complete plotting example.

## Further examples

- [`src/usage/minimal_example.py`](../src/usage/minimal_example.py) demonstrates construction,
  serialization, debugging, and 3D plotting.
- [`src/usage/state_network/`](../src/usage/state_network/) demonstrates domain-specific network
  reductions and topology validation.
- [`src/test_ugraph/`](../src/test_ugraph/) contains executable integration and serialization
  examples.
