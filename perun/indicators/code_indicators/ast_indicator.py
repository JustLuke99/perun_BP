from perun.indicators.abstract.base_indicator import BaseIndicator
import ast, json
import networkx as nx
from typing import TypedDict, List, Dict, Tuple, Union


class Node(TypedDict):
    id: str


class Link(TypedDict):
    source: str
    target: str


class Data(TypedDict):
    directed: bool
    multigraph: bool
    graph: dict
    nodes: List[Node]
    links: List[Link]


class CallGraphVisitor(ast.NodeVisitor):
    def __init__(self):
        self.graph = nx.DiGraph()


class AstIndicator(BaseIndicator):
    supported_languages = ["py"]

    def parse(self, file_path) -> Data:
        try:
            f = open(
                file_path,
                "r",
                encoding="utf-8",
                errors="replace",
            )
        except UnicodeDecodeError as e:
            print(e)
            return

        source_code = f.read()

        visitor = CallGraphVisitor()
        visitor.visit(ast.parse(source_code))
        call_graph_dict: Data = nx.readwrite.json_graph.node_link_data(visitor.graph)

        return call_graph_dict
