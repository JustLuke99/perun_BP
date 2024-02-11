# Standard Imports
from typing import Iterator, List

# Third-Party Imports

# Perun Imports
from perun import vcs
from perun.profile import helpers as profile_helpers
from perun.profile.factory import Profile
from perun.profile.helpers import ProfileInfo
from perun.select.abstract_base_selection import AbstractBaseSelection
from perun.utils.structs import MinorVersion
from perun.logic.stats import get_stats_of
from perun.select.whole_repository_selection import WholeRepositorySelection
from perun.vcs import get_minor_head
from collections import defaultdict
import tomlkit
from tomlkit import parse


# class BetterRepositorySelection(AbstractBaseSelection):
class BetterRepositorySelection:
    # nastavení soubor/složka(rek)/projekt -checkby file/folder/project
    # nastevní thresholdu - hodnota/hodnoty/dynamicky podle průměru (musí být celý prjekt/posledních x commitů) -treshhold num/nums/dynamic

    # def should_check_version(self, head_version: MinorVersion) -> tuple[bool, float]:
    def should_check_version(self, target_version: MinorVersion) -> tuple[bool, float]:
        """We check all versions always when checking by whole repository selector

        :param _: analysed target version
        :return: always true with 100% confidence
        """
        # head_hash = target_version.checksum
        head_hash = "1168e8e02858ae1ec389ff3e37df7fceed54bdff"
        first_parent_hash = [x for x in vcs.walk_minor_versions(head_hash)][1].checksum
        first_parent_hash = "7acd059b05c984afea70692d4c25c29825d8d12c"

        diff = self._get_version_diff(head_hash, first_parent_hash)

        should_check = self._check_diff(diff_data=diff)

        # return should_check
        exit()

        # NOTE for testing :^O
        x = WholeRepositorySelection.get_skeleton(self, target_version=get_minor_head())
        print(x)

        # print([x for x in parents])
        # print([x.checksum for x in parents])

        return True, 1

    @staticmethod
    def _check_diff(diff_data):
        """
        Check if the differences in the given data exceed the thresholds defined in pyproject.toml.

        :param diff_data: List of dictionaries containing file differences.
        :return: Tuple (check, confidence) where check is a boolean indicating whether to check the version,
                 and confidence is a float indicating the confidence level.
        """
        with open("pyproject.toml", "r") as file:
            config = tomlkit.parse(file.read())

        thresholds = config["tool"]["select"]["thresholds"]

        for file in diff_data:
            if not file["parser_name"] in thresholds.keys():
                continue

            for key, value in file["data"].items():
                if key not in thresholds[file["parser_name"]].keys():
                    continue

                # TODO create better rule parser
                # TODO ?move it to better place?
                rule = thresholds[file["parser_name"]][key]
                range_type, num = rule.split(" ")
                num2 = None

                # TODO improve this and add choices
                if range_type == "to":
                    if float(num) > float(value):
                        # return True, 1.0
                        print("returnuju se :)")
                elif range_type == "from":
                    if float(num) < float(value):
                        # return True, 1.0
                        print("returnuju se :)")
                elif range_type == "between":
                    if float(num) < float(value) < float(num2):
                        # return True, 1.0
                        print("returnuju se :)")

        return False, 0.0

    def _get_version_diff(self, first_hash: str, second_hash: str) -> List[dict]:
        """
        Get the differences between two versions based on their hashes.

        :param first_hash: Hash of the first version.
        :param second_hash: Hash of the second version.
        :return: List of dictionaries containing file differences.
        """

        def compare_dicts(dict1, dict2):
            compared_data = {}
            for key in dict1:
                try:
                    if isinstance(dict1[key], dict):
                        compared_data[key] = compare_dicts(dict1[key], dict2[key])
                    elif isinstance(dict1[key], list):
                        compared_data[key] = []
                        for i in range(min(len(dict1[key]), len(dict2[key]))):
                            compared_data[key].append(compare_dicts(dict1[key][i], dict2[key][i]))
                    else:
                        if isinstance(dict1[key], int) or isinstance(dict1[key], float):
                            compared_data[key] = abs(dict1[key] - dict2[key])
                except:
                    print("")
            return compared_data

        # TODO change this to first_hash
        head_data = self._get_data(second_hash)

        file_diff = []
        # TODO change this to first_hash
        for file in head_data[second_hash]:
            # TODO change this to first_hash
            second_item = self._get_data_from_file(
                file_path=file["file_path"], data=head_data[second_hash]
            )

            for parser in file["data"]:
                # TODO improve ["RadonParser"]
                if not parser["parser_name"] in ["RadonParser", "LizardParser"]:
                    continue

                second_data = self._get_parser_data(parser["parser_name"], second_item["data"])
                data = compare_dicts(parser["data"], second_data)
                file_diff.append(
                    {
                        "parser_name": parser["parser_name"],
                        "file_name": file["file_path"],
                        "data": data,
                    }
                )

        return file_diff

    @staticmethod
    def _get_data(git_hash):
        """
        Get the statistics data based on the given git hash.

        :param git_hash: Hash of the git commit.
        :return: Statistics data.
        """
        return get_stats_of("indicator_data", [git_hash])

    @staticmethod
    def _get_parser_data(parser_name, data):
        """
        Get the data for the specified parser from the given data.

        :param parser_name: Name of the parser.
        :param data: Data containing parsers.
        :return: Data for the specified parser.
        """
        for parser in data:
            if parser["parser_name"] == parser_name:
                return parser["data"]

    @staticmethod
    def _get_data_from_file(file_path, data):
        """
        Get the data for the specified file from the given data.

        :param file_path: Path of the file.
        :param data: Data containing files.
        :return: Data for the specified file.
        """
        for item in data:
            if item["file_path"] == file_path:
                return item

    def should_check_versions(self, _: MinorVersion, __: MinorVersion) -> tuple[bool, float]:
        """We check all pairs of versions always when checking by whole repository selector

        :param _: analysed target version
        :param __: corresponding baseline version (compared against)
        :return: always true with 100% confidence
        """
        return True, 1

    def should_check_profiles(self, _: Profile, __: Profile) -> tuple[bool, float]:
        """We check all pairs of profiles always when checking by whole repository selector

        :param _: analysed target profile
        :param __: corresponding baseline profile (compared against)
        :return: always true with 100% confidence
        """
        return True, 1

    def _find_all_by_file_path(data_list, file_path_to_find):
        return [item for item in data_list if file_path_to_find in item.get("file_path")]


def _find_all_paths(data_list: List[dict]):
    paths = []
    for data in data_list:
        if not (new_path := data["file_path"].rsplit("/", 1)[0]) in paths:
            paths.append(new_path)

    return [{"path": path, "data": []} for path in paths]


def select_test():
    x = BetterRepositorySelection()
    x.should_check_version("123ABC")
