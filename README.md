# ugraph

[![PyPI version](https://badge.fury.io/py/ugraph.svg)](https://badge.fury.io/py/ugraph)
[![Downloads](https://pepy.tech/badge/ugraph)](https://pepy.tech/project/ugraph)
![black](https://img.shields.io/badge/code%20style-black-000000.svg)
![isort](https://img.shields.io/badge/%20imports-isort-%231674b1.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![mypyc](https://img.shields.io/badge/mypy%20checked-100%25-brightgreen)
![flake8](https://img.shields.io/badge/flake8%20checked-100%25-brightgreen)
![pylint](https://img.shields.io/badge/pylint%20checked-100%25-brightgreen)


Extending [igraph](https://igraph.org/) to support defining custom classes for links and nodes in a graph.

_Because your graphs aren't just for you_  
*(igraph → ugraph)*


Enhance the **understandability** and **maintainability** of your graphs by defining custom classes for nodes and links. `ugraph` is a wrapper around `igraph`.

#### Installation

Install `ugraph` via pip:

```bash
pip install ugraph
```

#### Usage
Generally, `ugraph` can be used as a replacement for `igraph`. The main difference is that `ugraph` allows you to define custom classes for nodes and links in a graph.
This is useful when you want to store additional information about nodes and links in a graph. Since you are using custom classes (dataclasses) you can benefit from type hints and IDE autocompletion, as well as type checking.


#### Credits

This project builds upon the excellent [igraph](https://igraph.org/) library. We acknowledge and thank the igraph community for their foundational work.

#### License
See the [LICENSE](LICENSE) file for license rights and limitations (MIT).