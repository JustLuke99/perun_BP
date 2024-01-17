from Indicators.abstract.base_parser import BaseParser
import lizard
import os
from typing import TypedDict, List, Dict, Tuple
from typing_extensions import Union

Data = TypedDict(
    "Data",
    {
        "ccn": int,
        "average_cyclomatic_complexity": float,
        "average_nloc": float,
        "average_token_count": float,
        "nloc": int,
        "token_count": int,
        "functions": List[Dict[str, Union[int, str]]],
    },
)


class LizardParser(BaseParser):
    supported_languages = ["py", "cpp"]  # TODO add "c"

    def parse(self, file_path: str) -> Data:
        data = lizard.analyze_file(file_path)
        return_data: Data = {
            "ccn": data.CCN,
            "average_cyclomatic_complexity": data.average_cyclomatic_complexity,
            "average_nloc": data.average_nloc,
            "average_token_count": data.average_token_count,
            "nloc": data.nloc,
            "token_count": data.token_count,
            "functions": [
                {
                    "cyclomatic_complexity": func.cyclomatic_complexity,
                    "end_line": func.end_line,
                    "func_name": func.name,
                    "start_line": func.start_line,
                    "nloc": func.nloc,
                    "token_count": func.token_count,
                    "parameters_count": func.parameter_count,
                    "length": func.length,
                }
                for func in data.function_list
            ],
        }

        return return_data
