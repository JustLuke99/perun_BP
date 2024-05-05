"""
Author: Kraus Lukáš
Date: 5.5.2024
"""

from typing import TypedDict, Dict

from perun.collect.trace.optimizations.resources.manager import extract, Resources
from perun.indicators.abstract.base_indicator import BaseIndicator


class Data(TypedDict):
    """
    The type of the parsed data.
    """

    data: Dict[str, dict]


class AngrIndicator(BaseIndicator):
    """
    Class for parsing source code with Angr.

    Attributes:
    - supported_languages (List[str]): The list of supported languages.

    Methods:
    - parse: Parses the source code.
    """

    supported_languages = ["bin"]

    def parse(self, file_path) -> Data:
        """
        Parse the binary file with Angr.

        Parameters:
        - file_path (str): The path to the binary file.

        Returns:
        - Data: The parsed data.
        """
        data: Data = extract(Resources.CALL_GRAPH_ANGR, binary=file_path, stats_name="", cache=None)
        return data
