from Indicators.abstract.base_parser import BaseParser
import ast, json
import networkx as nx


class CallGraphVisitor(ast.NodeVisitor):
    def __init__(self):
        self.graph = nx.DiGraph()
        self.current_function = None

    def visit_FunctionDef(self, node):
        self.current_function = node.name
        self.graph.add_node(self.current_function)
        self.generic_visit(node)
        self.current_function = None

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and self.current_function:
            caller = self.current_function
            callee = node.func.id
            self.graph.add_edge(caller, callee)

        self.generic_visit(node)


class AstParser(BaseParser):
    supported_languages = ["py"]

    def parse(self, file_path):
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

        tree = ast.parse(source_code)
        visitor = CallGraphVisitor()
        visitor.visit(tree)
        call_graph = visitor.graph
        call_graph_dict = nx.readwrite.json_graph.node_link_data(call_graph)
        call_graph_json = json.dumps(call_graph_dict, indent=2)

        return call_graph_json
