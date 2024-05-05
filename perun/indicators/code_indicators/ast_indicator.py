"""
Author: Kraus Lukáš
Date: 5.5.2024
"""

import ast

from perun.indicators.abstract.base_indicator import BaseIndicator


class AstIndicator(BaseIndicator):
    """
    Class for parsing source code with AST.

    Attributes:
    - supported_languages (List[str]): The list of supported languages.

    Methods:
    - parse: Parses the source code.
    """

    supported_languages = ["py"]

    def parse(self, file_path) -> str:
        """
        Parse the source code with AST.

        Parameters:
        - file_path (str): The path to the source code file.

        Returns:
        - str: The parsed data.
        """
        f = open(
            file_path,
            "r",
            encoding="utf-8",
            errors="replace",
        )

        source_code = f.read()
        data: str = ast.dump(ast.parse(source_code))

        return data
