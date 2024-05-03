from typing import TypedDict, List, Dict
from typing import TypedDict, List, Dict

import radon.complexity as radon_complexity
import radon.raw as radon_raw
from radon.metrics import (
    mi_visit,
)
from typing_extensions import Union

from perun.indicators.abstract.base_indicator import BaseIndicator


class Data(TypedDict):
    lines_of_code: int
    logical_lines_of_code: int
    source_lines_of_code: int
    comment_lines: int
    multiline_strings: int
    comments_without_code: int
    blank: int
    maintainability_index: float
    number_of_functions: int
    function_names: List[str]
    functions: List[Dict[str, Union[int, str]]]


class RadonIndicator(BaseIndicator):
    supported_languages = ["py"]

    def parse(self, file_path: str) -> Data:
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
        raw_metrics = radon_raw.analyze(source_code)
        results = radon_complexity.cc_visit(source_code)
        # visit_h = h_visit(source_code)
        visit_mi = mi_visit(source_code, 2)
        # visit_ast = h_visit_ast(visit_h)
        # parameters = mi_parameters(source_code)
        # mi_computed = mi_compute(parameters[0], parameters[1], parameters[2], parameters[3])

        return_data: Data = {
            "lines_of_code": raw_metrics.loc,
            "logical_lines_of_code": raw_metrics.lloc,
            "source_lines_of_code": raw_metrics.sloc,
            "comment_lines": raw_metrics.comments,
            "multiline_strings": raw_metrics.multi,
            "comments_without_code": raw_metrics.single_comments,
            "blank": raw_metrics.blank,
            "maintainability_index": visit_mi,
            # "mi_parameters": parameters,
            # "mi_compute": mi_computed,
            "number_of_functions": len(results),
            "function_names": [func.fullname for func in results],
            "functions": [
                {"func_name": func.fullname, "cyclomatic_complexity": func.complexity}
                for func in results
            ],
        }

        return return_data
