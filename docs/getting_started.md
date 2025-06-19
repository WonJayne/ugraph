# Getting Started with `ugraph`

`ugraph` extends [`igraph`](https://igraph.org/) to let you store meaning alongside your graph structure. This short guide introduces the main pieces of the library and shows how to begin creating your own networks.

## Installation

```bash
pip install ugraph
# for plotting support
pip install ugraph[plotting]
```

## Repository Layout

```
ugraph/
├── src/
│   ├── ugraph/       # core library
│   ├── usage/        # examples
│   └── test_ugraph/  # unit tests
```
- **`src/ugraph`** contains the abstract base classes for nodes, links and networks.
- **`src/usage`** offers minimal and domain-specific examples such as the `StateNetwork` demo.
- **`src/test_ugraph`** holds the test suite which also doubles as usage samples.

## Defining Custom Nodes and Links

Graph elements are defined as dataclasses that derive from the abstract base classes. A minimal example:

```python
from dataclasses import dataclass
from enum import Enum, unique
from ugraph import NodeABC, LinkABC, MutableNetworkABC

@unique
class ExampleNodeType(Enum):
    EXAMPLE = 0

@dataclass(frozen=True, slots=True)
class ExampleNode(NodeABC[ExampleNodeType]):
    node_type: ExampleNodeType
    value: int

@unique
class ExampleLinkType(Enum):
    EXAMPLE = 0

@dataclass(frozen=True, slots=True)
class ExampleLink(LinkABC[ExampleLinkType]):
    link_type: ExampleLinkType

class ExampleNetwork(MutableNetworkABC[ExampleNode, ExampleLink, ExampleNodeType, ExampleLinkType]):
    pass
```

You can then create nodes, add them to a network, and serialize the result:

```python
n = ExampleNetwork()
node_a = ExampleNode(id=0, coordinates=(0, 0, 0), node_type=ExampleNodeType.EXAMPLE, value=42)
node_b = ExampleNode(id=1, coordinates=(1, 0, 0), node_type=ExampleNodeType.EXAMPLE, value=7)
link = ExampleLink(link_type=ExampleLinkType.EXAMPLE)

n.add_nodes([node_a, node_b])
n.add_links([((node_a.id, node_b.id), link)])

n.write_json("ExampleNetwork.json")
```

## Visualization

With the optional `plotting` extra you can display your graphs in 3‑D using Plotly:

```python
from ugraph.plot import add_3d_ugraph_to_figure
import plotly.graph_objects as go

fig = go.Figure()
add_3d_ugraph_to_figure(fig, n)
fig.show()
```

## Learning More

- Browse the [`src/usage`](https://github.com/WonJayne/ugraph/tree/main/src/usage) examples for ready-to-run scripts.
- Inspect the test suite under [`src/test_ugraph`](https://github.com/WonJayne/ugraph/tree/main/src/test_ugraph) for more advanced scenarios.

`ugraph` is designed to grow with your needs—extend the base classes, validate custom topologies and serialize your data for easy sharing.
