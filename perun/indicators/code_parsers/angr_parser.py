from perun.indicators.abstract.base_parser import BaseParser
from perun.collect.trace.optimizations.resources.manager import extract, Resources
from typing import TypedDict, Dict


class Data(TypedDict):
    data: Dict[str, dict]


class AngrParser(BaseParser):
    supported_languages = ["bin"]

    def parse(self, file_path) -> Data:
        data: Data = extract(Resources.CALL_GRAPH_ANGR, binary=file_path, stats_name="", cache=None)
        return data
