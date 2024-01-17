from Indicators.abstract.base_parser import BaseParser
import magic


def _is_executable(file_path: str) -> bool:
    def get_file_type(file_path: str):
        mime = magic.Magic()
        file_type = mime.from_file(file_path)
        return file_type

    return (
        True if "executable" in get_file_type(file_path.replace(".bin", "")) else False
    )


class AngrParser(BaseParser):
    supported_languages = ["bin"]

    def parse(self, file_path):
        if not _is_executable(file_path):
            raise Exception("Not executable, skipping.")

        # TODO add angr
