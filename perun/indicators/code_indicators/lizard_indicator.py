"""
Author: Kraus Lukáš
Date: 5.5.2024
"""

from typing import TypedDict, List, Dict

import lizard
from typing_extensions import Union

from perun.indicators.abstract.base_indicator import BaseIndicator


class Data(TypedDict):
    """
    The type of the parsed data.
    """

    average_code_complexity: int
    average_cyclomatic_complexity: float
    average_length_of_code: float
    average_token_count: float
    number_of_functions: int
    token_count: int
    functions: List[Dict[str, Union[int, str]]]


class LizardIndicator(BaseIndicator):
    """
    Class for parsing source code with Lizard.

    Attributes:
    - supported_languages (List[str]): The list of supported languages.

    Methods:
    - parse: Parses the source code.
    """

    supported_languages = ["py", "cpp", "c"]

    def parse(self, file_path: str) -> Data:
        """
        Parse the source code with Lizard.

        Parameters:
        - file_path (str): The path to the source code file.

        Returns:
        - Data: The parsed data.
        """
        data = lizard.analyze_file(file_path)
        return_data: Data = {
            "average_code_complexity": data.CCN,
            "average_cyclomatic_complexity": data.average_cyclomatic_complexity,
            "average_length_of_code": data.average_nloc,
            "average_token_count": data.average_token_count,
            "number_of_functions": data.nloc,
            "token_count": data.token_count,
            "functions": [
                {
                    "cyclomatic_complexity": func.cyclomatic_complexity,
                    "end_line": func.end_line,
                    "func_name": func.name,
                    "start_line": func.start_line,
                    "lines_of_code": func.nloc,
                    "token_count": func.token_count,
                    "parameters_count": func.parameter_count,
                    "length": func.length,
                }
                for func in data.function_list
            ],
        }

        return return_data
