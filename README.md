# ugraph

[![PyPI version](https://badge.fury.io/py/ugraph.svg)](https://badge.fury.io/py/ugraph)
[![Downloads](https://pepy.tech/badge/ugraph)](https://pepy.tech/project/ugraph)
![black](https://img.shields.io/badge/code%20style-black-000000.svg)
![isort](https://img.shields.io/badge/%20imports-isort-%231674b1.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![mypyc](https://img.shields.io/badge/mypy%20checked-100%25-brightgreen)
![flake8](https://img.shields.io/badge/flake8%20checked-100%25-brightgreen)
![pylint](https://img.shields.io/badge/pylint%20checked-100%25-brightgreen)

**Extend your graphs beyond structure—add meaning with `ugraph`.**

`ugraph` builds on [igraph](https://igraph.org/) to provide a powerful way to define and work with custom node and link types in your graphs. This package is ideal for those who need more than just graph structure—it empowers you to combine graph data with rich information via Python dataclasses, and comes with built-in support for JSON storage and 3D visualizations.

_Because your graphs aren't just for you_  
*(igraph → ugraph)*

---

### Why ugraph?

Graphs often represent more than their edges and nodes—they carry data, behaviors, and relationships that need to be understood in context. `ugraph` bridges this gap by enabling:

- **Custom node and link classes**: Add type-safe attributes and behaviors to your graph elements.
- **Data serialization**: Easily save and load your graphs in JSON format for persistence and sharing.
- **3D visualization**: Render interactive, browser-based 3D visualizations in HTML using Plotly.

With `ugraph`, your graphs are as **understandable** and **maintainable** as the data they represent.

---

### Features at a Glance

- **Custom Classes**: Define your nodes and links as Python dataclasses, allowing for type hints, IDE autocompletion, and type checking.
- **Serialization**: Store and reload your networks seamlessly using JSON files.
- **Interactive Visualization**: Generate 3D plots of your graphs in HTML for better insights and presentation.

---

### Disclaimer

`ugraph` is not intended for creating graph figures or visualizations (e.g., bar charts, scatter plots). It is a tool for working with graph data structures (nodes and links) and enhancing their usability.

---

### Installation

Install `ugraph` using pip:

```bash
pip install ugraph
```

(if you need igraph's cairo-based plotting, use `pip install ugraph[cairo]`)

---

### Quick Start

`ugraph` works similarly to `igraph`, with the added flexibility of custom node and link types. You can define attributes like coordinates, IDs, or any other domain-specific data in a type-safe and Pythonic way.

Explore usage examples in the [examples directory](https://github.com/WonJayne/ugraph/tree/main/src/usage), or start with a [minimal example](https://github.com/WonJayne/ugraph/tree/main/src/usage/minimal_example.py).

### Documentation

For an extended introduction and code snippets, see [docs/getting_started.md](./docs/getting_started.md).

---

### Credits

This project builds upon the excellent [igraph](https://igraph.org/) library. We acknowledge and thank the igraph community for their foundational work.

---

### License

See the [LICENSE](LICENSE) file for rights and limitations (MIT).

