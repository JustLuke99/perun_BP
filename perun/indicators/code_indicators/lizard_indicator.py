from perun.indicators.abstract.base_indicator import BaseIndicator
import lizard
import os
from typing import TypedDict, List, Dict, Tuple
from typing_extensions import Union


class Data(TypedDict):
    average_code_complexity: int
    average_cyclomatic_complexity: float
    average_length_of_code: float
    average_token_count: float
    number_of_functions: int
    token_count: int
    functions: List[Dict[str, Union[int, str]]]


class LizardIndicator(BaseIndicator):
    supported_languages = ["py", "cpp", "c"]

    def parse(self, file_path: str) -> Data:
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
