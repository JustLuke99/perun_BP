import importlib
import os

import magic

from perun.logic.stats import add_stats, get_stats_of
from perun.utils.exceptions import VersionControlSystemException, StatsFileNotFoundException

CONFIG = {
    "indicator_files": [
        "lizard_indicator.py",
        "radon_indicator.py",
        "ast_indicator.py",
        "angr_indicator.py",
    ],  #  "ast_indicator.py", "angr_indicator.py"
    "IGNORE_FOLDERS": ["venv", "idea"],
    "IGNORE_FILES": ["meson.build", "__init__.py"],
    "ROOT_FOLDER": os.getcwd(),  # + "/dash_cytoscape",
}


class IndicatorsManager:
    """
    Manages a collection of code indicators and facilitates parsing of code files in a directory.

    Attributes:
    - indicators (list): A list of dictionaries, each containing a indicator class and its supported languages.
    - supported_languages (list): A list of all supported programming languages by the loaded indicators.
    """

    __slots__ = [
        "indicators",
        "supported_languages",
        "data",
        "vcs_version",
    ]

    def __init__(self, vsc_version: str):
        """
        Initializes a new instance of the CodeIndicatorManager class.

        Parameters:
        - None
        """
        self.indicators = []
        self.supported_languages = []
        self.data = []
        self.vcs_version = vsc_version

        self._load_indicators()

    def _check_if_file_exists(self) -> None:
        """
        Checks if the file exists in the version control system and raises appropriate exceptions IF found.

        """
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

    def get_data_from_indicators(
        self,
    ) -> None:
        """
        Parses code files in the specified root directory using loaded indicators.

        Parameters:
        - None
        Returns:
        - None
        """
        self._check_if_file_exists()

        for directory_name, _, files in os.walk(CONFIG["ROOT_FOLDER"]):
            if any(x in directory_name for x in CONFIG["IGNORE_FOLDERS"]):
                continue

            for file in files:
                if not self._has_extension(file):
                    if not self._is_executable(os.path.join(directory_name, file)):
                        continue
                    file += ".bin"

                if not (
                    any(file.endswith(ext) for ext in self.supported_languages)
                    and not any(x in file for x in CONFIG["IGNORE_FILES"])
                ):
                    continue

                indicator_data = []
                for code_indicator in self.indicators:
                    if not any(file.endswith(ext) for ext in code_indicator["supported_languages"]):
                        continue

                    file = file.replace(".bin", "")
                    try:
                        data = code_indicator["class"].parse(
                            file_path=os.path.join(directory_name, file)
                        )
                    except Exception as e:
                        print(f"File: {os.path.join(directory_name, file)}: {e}")
                        continue

                    indicator_data.append(
                        {
                            "parser_name": code_indicator["indicator_name"].replace(
                                "Indicator", "Parser"
                            ),
                            "data": data,
                        }
                    )

                self.data.append(
                    {
                        "file_path": os.path.join(
                            directory_name.replace(CONFIG["ROOT_FOLDER"], ""), file
                        ),
                        "file_type": file.rsplit(".")[-1],
                        "data": indicator_data,
                    }
                )

        self._save_data()

    def _load_indicators(self) -> None:
        """
        Loads code indicators from the specified directory and updates supported_languages.

        Parameters:
        - None

        Returns:
        - None
        """
        for indicator_file in CONFIG["indicator_files"]:
            module_name = os.path.splitext(indicator_file)[0]
            if "__init__" in module_name:
                continue

            module_path = f"perun.indicators.code_indicators.{module_name}"

            try:
                module = importlib.import_module(module_path)
            except Exception as e:
                raise AttributeError(f"Cant import module from file {indicator_file}. {e}")

            classes = [cls for cls in dir(module) if isinstance(getattr(module, cls), type)]

            if not classes:
                raise AttributeError(f"File {indicator_file} doesnt have class.")

            file_classes = [
                _class
                for _class in classes
                if _class != "BaseIndicator" and "indicator" in _class.lower()
            ]

            indicator_class = getattr(module, file_classes[0])
            try:
                supported_languages = indicator_class().get_languages()
            except Exception as e:
                raise NotImplementedError(f"In {indicator_file} is missing get_languages()")

            for language in supported_languages:
                if language not in self.supported_languages:
                    self.supported_languages.append(language)

            self.indicators.append(
                {
                    "class": indicator_class(),
                    "supported_languages": indicator_class().get_languages(),
                    "indicator_name": file_classes[0],
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
    IndicatorsManager(vsc_version=hash).get_data_from_indicators()
