import importlib
import os
from perun.logic.stats import add_stats, get_stats_of
import magic
from perun.utils.exceptions import VersionControlSystemException, StatsFileNotFoundException

CONFIG = {
    "parser_files": ["lizard_parser.py", "radon_parser.py", "ast_parser.py", "angr_parser.py"],
    "IGNORE_FOLDERS": ["venv", "idea"],
    "IGNORE_FILES": ["meson.build"],
    "ROOT_FOLDER": os.getcwd(),
}


class IndicatorsManager:
    """
    Manages a collection of code parsers and facilitates parsing of code files in a directory.

    Attributes:
    - parsers_directory (str): The directory containing code parsers.
    - parsers (list): A list of dictionaries, each containing a parser class and its supported languages.
    - supported_languages (list): A list of all supported programming languages by the loaded parsers.
    """

    __slots__ = [
        "parsers_directory",
        "parsers",
        "supported_languages",
        "data",
        "loaded_parsers",
        "vcs_version",
    ]

    def __init__(self, vsc_version: str):
        """
        Initializes a new instance of the CodeParserManager class.

        Parameters:
        - None
        """
        # TODO change it to cfg
        self.parsers_directory = "code_parsers"
        self.parsers = []
        self.supported_languages = []
        self.data = []
        self.vcs_version = vsc_version

        self._load_indicators()

    def _check_if_file_exists(self) -> None:
        try:
            if get_stats_of(
                "indicator_data",
                minor_version=self.vcs_version,
                stats_ids=[self.vcs_version],
            ):
                return
        except VersionControlSystemException as e:
            if "missing" not in str(e):
                raise e
        except StatsFileNotFoundException as e:
            if "does not exist" not in str(e):
                raise e
        except Exception as e:
            raise e

    def parse(
        self,
    ) -> None:
        """
        Parses code files in the specified root directory using loaded parsers.

        Parameters:
        - None
        Returns:
        - None
        """
        self._check_if_file_exists()

        for directory_name, _, files in os.walk(CONFIG["ROOT_FOLDER"]):
            if any(x in directory_name for x in CONFIG["ignore_folders"]):
                continue

            for file in files:
                if not self._has_extension(file):
                    if not self._is_executable(os.path.join(directory_name, file)):
                        continue
                    file += ".bin"

                if not (
                    any(file.endswith(ext) for ext in self.supported_languages)
                    and not any(x in file for x in CONFIG["ignore_files"])
                ):
                    continue

                parser_data = []
                # # TODO REMOVE IT
                # self.parsers = self.parsers[:2]
                for code_parser in self.parsers:
                    if not any(file.endswith(ext) for ext in code_parser["supported_languages"]):
                        continue

                    file = file.replace(".bin", "")
                    try:
                        data = code_parser["class"].parse(
                            file_path=os.path.join(directory_name, file)
                        )
                    except Exception as e:
                        print(f"File: {os.path.join(directory_name, file)}: {e}")
                        continue

                    parser_data.append({"parser_name": code_parser["parser_name"], "data": data})

                self.data.append(
                    {
                        # "file_path": os.path.join(directory_name, file.replace(".bin", "")),
                        "file_path": os.path.join(
                            directory_name.replace(CONFIG["ROOT_FOLDER"], ""), file
                        ),
                        "file_type": file.rsplit(".")[-1],
                        "data": parser_data,
                    }
                )

        self._save_data()

    def _load_indicators(self) -> None:
        """
        Loads code parsers from the specified directory and updates supported_languages.

        Parameters:
        - None

        Returns:
        - None
        """
        for parser_file in CONFIG["parser_files"]:
            module_name = os.path.splitext(parser_file)[0]
            if "__init__" in module_name:
                continue

            module_path = f"perun.indicators.code_parsers.{module_name}"

            try:
                module = importlib.import_module(module_path)
            except Exception as e:
                raise AttributeError(f"Cant import module from file {parser_file}. {e}")

            classes = [cls for cls in dir(module) if isinstance(getattr(module, cls), type)]

            if not classes:
                raise AttributeError(f"File {parser_file} doesnt have class.")

            parse_class = [
                _class
                for _class in classes
                if _class != "BaseParser" and "parser" in _class.lower()
            ]

            parser_class = getattr(module, parse_class[0])
            try:
                supported_languages = parser_class().get_languages()
            except Exception as e:
                raise NotImplementedError(f"In {parser_file} is missing get_languages()")

            for language in supported_languages:
                if language not in self.supported_languages:
                    self.supported_languages.append(language)

            self.parsers.append(
                {
                    "class": parser_class(),
                    "supported_languages": parser_class().get_languages(),
                    "parser_name": parse_class[0],
                }
            )

    def _save_data(self):
        """
        Saves parsed indicator data using the add_stats function.

        The parsed indicator data is stored under the filename "indicator_data" with the specified VCS version.

        Parameters:
        - None

        Returns:
        - None
        """
        add_stats(
            "indicator_data",
            minor_version=self.vcs_version,
            stats_ids=[self.vcs_version],
            stats_contents=[self.data],
        )
        print(f"Data saved. {self.vcs_version}")

    def _has_extension(self, file_path):
        """
        Checks if the file at the given path has any extension.

        Parameters:
        - file_path (str): The path to the file.

        Returns:
        - bool: True if the file has any extension, False otherwise.
        """
        _, file_extension = os.path.splitext(file_path)
        return bool(file_extension)

    def _is_executable(self, file_path: str) -> bool:
        def get_file_type(file_path: str):
            mime = magic.Magic()
            file_type = mime.from_file(file_path)
            return file_type

        return True if "executable" in get_file_type(file_path.replace(".bin", "")) else False


def test_indicator_manager(hash, git_repo_path):
    IndicatorsManager(vsc_version=hash).parse()
