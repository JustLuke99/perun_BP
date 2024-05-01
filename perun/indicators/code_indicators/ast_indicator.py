from perun.indicators.abstract.base_indicator import BaseIndicator
import ast, json
import networkx as nx
from typing import TypedDict, List, Dict, Tuple, Union


# class Data(TypedDict):
#     body: List
#     type_ignores: List


class AstIndicator(BaseIndicator):
    supported_languages = ["py"]

    def parse(self, file_path) -> str:
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
        data: str = ast.dump(ast.parse(source_code))

        return data
