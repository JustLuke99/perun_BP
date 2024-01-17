import importlib
import os
from datetime import datetime
import sys


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
    ]

    def __init__(self, load_parsers: bool = False):
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
        self.loaded_parsers = False
        # maybe change to True?
        if load_parsers:
            self.load_indicators()

    def load_indicators(self) -> None:
        """
        Loads code parsers from the specified directory and updates supported_languages.

        Parameters:
        - None

        Returns:
        - None
        """
        self.loaded_parsers = True

        parser_files = [
            f for f in os.listdir(self.parsers_directory) if f.endswith(".py")
        ]

        for parser_file in parser_files:
            module_name = os.path.splitext(parser_file)[0]
            module_path = f"{self.parsers_directory}.{module_name}"

            try:
                module = importlib.import_module(module_path)
            except Exception as e:
                raise AttributeError(f"Cant import module from file {parser_file}. {e}")

            classes = [
                cls for cls in dir(module) if isinstance(getattr(module, cls), type)
            ]

            if not classes:
                raise AttributeError(f"File {parser_file} doesnt have class.")

            parse_class = [classX for classX in classes if classX != "BaseParser" and "parser" in classX.lower()]

            parser_class = getattr(module, parse_class[0])
            try:
                supported_languages = parser_class().get_languages()
            except Exception as e:
                raise NotImplementedError(
                    f"In {parser_file} is missing get_languages()"
                )

            for language in supported_languages:
                if language not in self.supported_languages:
                    self.supported_languages.append(language)

            self.parsers.append(
                {
                    "class": parser_class(),
                    "supported_languages": parser_class().get_languages(),
                    "parser_name": parse_class[0]
                }
            )

    def parse(self, root_directory: str, ignore_files: list=[], ignore_folders: list=[]) -> None:
        """
        Parses code files in the specified root directory using loaded parsers.

        Parameters:
        - root_directory (str): The root directory to start parsing from.
        - ignore_files (list): A list of file names to ignore during parsing.
        - ignore_folders (list): A list of folder names to ignore during parsing.

        Returns:
        - None
        """
        if not self.loaded_parsers:
            self.load_indicators()

        for directory_name, _, files in os.walk(root_directory):
            if any(x in directory_name for x in ignore_folders):
                continue

            for file in files:
                if "." not in file:
                    file += ".bin"

                if not (
                    any(file.endswith(ext) for ext in self.supported_languages)
                    or any(x in file for x in ignore_files)
                ):
                    continue

                for code_parser in self.parsers:
                    if not any(
                        file.endswith(ext) for ext in code_parser["supported_languages"]
                    ):
                        continue

                    try:
                        _ = file.rsplit(".")[1]
                        data = code_parser["class"].parse(
                            file_path=os.path.join(directory_name, file)
                        )
                    except Exception as e:
                        print(f"File: {os.path.join(directory_name, file)}: {e}")
                        continue

                    self.data.append(
                        {
                            "file_path": os.path.join(directory_name, file),
                            "file_type": file.rsplit(".")[-1],
                            "parser_name": code_parser["parser_name"],
                            "data": data,
                        }
                    )


if __name__ == "__main__":
    start_time = datetime.now()
    IGNORE_FOLDERS = ["venv", "idea"]
    IGNORE_FILES = []
    # FOLDER = "test_files"
    FOLDER = "./test_files/"
    parser = IndicatorsManager(load_parsers=False)
    parser.load_indicators()
    fiLES = parser.parse(
        FOLDER, ignore_files=IGNORE_FILES, ignore_folders=IGNORE_FOLDERS
    )
    print("Size of data: ", sys.getsizeof(parser.data))
    print("Time taken: ", datetime.now() - start_time)
    print(fiLES)


