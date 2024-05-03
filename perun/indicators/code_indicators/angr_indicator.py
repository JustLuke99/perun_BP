from typing import TypedDict, Dict

from perun.collect.trace.optimizations.resources.manager import extract, Resources
from perun.indicators.abstract.base_indicator import BaseIndicator


class Data(TypedDict):
    data: Dict[str, dict]


class AngrIndicator(BaseIndicator):
    supported_languages = ["bin"]

    def parse(self, file_path) -> Data:
        data: Data = extract(Resources.CALL_GRAPH_ANGR, binary=file_path, stats_name="", cache=None)
        return data
