# Standard Imports
import os
from typing import Iterator, List
from itertools import chain

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
from perun.vcs.git_repository import GitRepository
from perun.select.rule_kit.rule import RULE_CONFIG, Rule

CONFIG = {
    "compare_data_filter_parsers": True,
    "compare_data_filter_parser_names": ["RadonParser", "LizardParser"],
    "check_version_type": "last",
    "check_diff_thresholds": {
        "find_diff_in": "folders",  # "files", "folders", "project", "folders_rec"
        "immersion": {  # this can be active only for "folders" and "folders_rec"
            "active": True,
            "folder_immersion_level": 2,
            "from": "root",  # "root", "end"
        },
    },
    "evaluate_rules": "average", # "any", "average", "average_weighted"
}
# imersion level - from: root/end


# class BetterRepositorySelection(AbstractBaseSelection):
class BetterRepositorySelection:
    __slots__ = ("git_repo", "rule_class")

    def __init__(self, repository_path: str = os.getcwd()) -> None:
        # self.git_repo = GitRepository("/home/luke/PycharmProjects/perun_BP")
        self.git_repo = GitRepository(repository_path)
        self.rule_class = Rule()

    def should_check_version(
        self, target_version: MinorVersion | None = None
    ) -> tuple[bool, float]:
        """We check all versions always when checking by whole repository selector

        :param target_version: analysed target version
        :return: always true with 100% confidence
        """
        minor_versions = [
            x
            for x in self.git_repo.walk_minor_versions(
                target_version.checksum if target_version else self.git_repo.get_minor_head()
            )
        ]

        # FIXME delete it later
        # version_one, version_two = [
        #     x
        #     for x in minor_versions
        #     if x.checksum == "3a1d0413e29a0bef723a4b8eea44ddd2caf53ec5"
        #     or x.checksum == "b38d03ed9a114eb800497b61ebbb5157e9768ce4"
        # ]

        if len(minor_versions) < 2:
            exit()

        # FIXME remove comment
        version_one, version_two = minor_versions[:2]

        return self.should_check_versions(version_one, version_two)

    def should_check_versions(
        self, target_version: MinorVersion, version_to_compare: MinorVersion
    ) -> tuple[bool, float]:
        # FIXME fix return
        """We check all pairs of versions always when checking by whole repository selector

        :param target_version: analysed target version
        :param version_to_compare: corresponding baseline version (compared against)
        :return: always true with 100% confidence
        """
        diff = self._get_version_diff(target_version, version_to_compare)
        print(diff)
        # TODO add confidence
        should_check = self._check_diff_thresholds(diff_data=diff)
        # TODO add confidence
        return should_check

    def _check_diff_thresholds(self, diff_data):
        """
        Check if the differences in the given data exceed the thresholds defined in the configuration.

        :param diff_data: List of dictionaries containing file differences.
        :return: Tuple (should_check, confidence) where should_check is a boolean indicating whether to check the version,
                 and confidence is a float indicating the confidence level.
        """

        def calculate_immersion_level(folder, max_slashes):
            """
            Calculate the immersion level of a folder based on the number of slashes in its path.

            :param folder: The folder path.
            :param max_slashes: The maximum number of slashes in any folder path.
            :return: True if the folder's immersion level meets the threshold, False otherwise.
            """
            immersion_config = CONFIG["check_diff_thresholds"]["immersion"]

            if not immersion_config["active"]:
                return True

            if immersion_config["from"] == "root":
                return (
                    True
                    if folder.count("/") <= immersion_config["folder_immersion_level"]
                    else False
                )
            elif immersion_config["from"] == "end":
                return (
                    True
                    if folder.count("/") >= max_slashes - immersion_config["folder_immersion_level"]
                    else False
                )
            else:
                raise Exception("Field 'from̈́' is not defined.")

        diff_result = []

        if CONFIG["check_diff_thresholds"]["find_diff_in"] == "files":
            for file_diff in diff_data:
                diff_result.append(self._check_diff(file_diff["data"], file_diff["parser_name"]))
        elif CONFIG["check_diff_thresholds"]["find_diff_in"] == "project":
            folder_rec_diff = self._calculate_diff_of_folders_recursively(diff_data)
            for parser_name, data in folder_rec_diff[""].items():
                diff_result.append(self._check_diff(data, parser_name))
        elif CONFIG["check_diff_thresholds"]["find_diff_in"] in ("folders", "folders_rec"):
            folder_diff = (
                self._calculate_diff_of_folders_recursively(diff_data)
                if CONFIG["check_diff_thresholds"]["find_diff_in"] == "folders_rec"
                else self._calculate_diff_of_folders(diff_data)
            )
            max_slashes = max(path.count("/") for path in folder_diff.keys())
            for folder, parsers in folder_diff.items():
                if calculate_immersion_level(folder, max_slashes):
                    for parser_name, data in parsers.items():
                        diff_result.append(self._check_diff(data, parser_name))
        else:
            raise Exception("find_diff_in is not defined.")

        return self._evaluate_rules(diff_result)

    def _evaluate_rules(self, diff_result):
        """
        Evaluate the rules based on the differences result.

        This method calculates the total number of rules and the sum of weights for the rules with a True result.

        :param diff_result: The differences result containing nested dictionaries/lists.
        :type diff_result: list
        """

        def get_dicts(lst):
            """
            Extract dictionaries from a nested list of dictionaries/lists.

            This function recursively extracts dictionaries from a nested structure of dictionaries/lists.

            :param lst: The input nested list of dictionaries/lists.
            :type lst: list
            :return: A list of dictionaries extracted from the nested structure.
            :rtype: list
            """
            dicts = []
            for item in lst:
                if isinstance(item, dict):
                    dicts.append(item)
                elif isinstance(item, list):
                    dicts.extend(get_dicts(item))
            return dicts

        count = 0
        true_rules = 0
        for diff in diff_result:
            diff_dict = get_dicts(diff)
            for rule in diff_dict:
                count += 1
                if rule["result"]:
                    true_rules += rule["weight"]

        # TODO improve this
        if CONFIG["evaluate_rules"] == "any":
            return (True, 1, diff_result) if true_rules > 0 else (False, 0, diff_result)
        elif CONFIG["evaluate_rules"] == "average":
            return (True, true_rules / count, diff_result) if true_rules / count > 0.5 else (False, true_rules / count, diff_result)
        elif CONFIG["evaluate_rules"] == "average_weighted":
            return (True, true_rules / count, diff_result) if true_rules / count > 0.7 else (False, true_rules / count, diff_result)

    def _calculate_diff_of_folders_recursively(self, diff_data):
        diff_data = self._calculate_diff_of_folders(diff_data)

        diff_rec = {}
        folders_sorted = sorted(diff_data.keys(), key=lambda x: x.count("/"), reverse=True)
        for folder in folders_sorted:
            if folder not in diff_rec.keys():
                diff_rec[folder] = diff_data[folder]

            under_folders = [
                s
                for s in diff_rec.keys()
                if folder in s and s != folder and folder.count("/") + 1 == s.count("/")
            ]
            if not under_folders:
                continue

            for parser_name in diff_data[folder].keys():
                for key in diff_data[folder][parser_name].keys():
                    if isinstance(diff_data[folder][parser_name][key], list):
                        diff_rec[folder][parser_name][key].extend(
                            diff_data[folder][parser_name][key]
                        )
                    else:
                        diff_rec[folder][parser_name][key] += diff_data[folder][parser_name][key]

        return diff_rec

    def _calculate_diff_of_folders(self, diff_data):
        """
        Calculate the differences for each folder based on the given data.

        :param diff_data: List of dictionaries containing file differences.
        :type diff_data: list[dict]
        :return: Dictionary containing the differences for each folder.
        :rtype: dict
        """

        def reset_values_to_zero(d):
            for key, value in d.items():
                if isinstance(value, dict):
                    reset_values_to_zero(value)
                elif isinstance(value, list):
                    for item in value:
                        reset_values_to_zero(item)
                else:
                    d[key] = 0

        diff_folders = {}

        if not any(x["file_name"].count("/") == 1 for x in diff_data):
            item_to_add = diff_data[0].copy()
            item_to_add["file_name"] = "/" + item_to_add["file_name"].split("/")[-1]
            reset_values_to_zero(item_to_add["data"])
            diff_data.append(item_to_add)

        for file_diff in diff_data:
            folder = file_diff["file_name"].rsplit("/", 1)[0]

            if folder not in diff_folders.keys():
                diff_folders[folder] = {}

            if not file_diff["parser_name"] in diff_folders[folder]:
                diff_folders[folder][file_diff["parser_name"]] = file_diff["data"]
            else:
                for key in diff_folders[folder][file_diff["parser_name"]].keys():
                    if isinstance(diff_folders[folder][file_diff["parser_name"]][key], list):
                        diff_folders[folder][file_diff["parser_name"]][key].extend(
                            file_diff["data"][key]
                        )
                    else:
                        diff_folders[folder][file_diff["parser_name"]][key] += file_diff["data"][
                            key
                        ]

        return diff_folders

    def _check_diff(self, file_data, parser_name):
        """
        Check if the differences in the given file data exceed the thresholds defined in the configuration for a specific parser.

        :param file_data: Dictionary containing data about a file.
        :param parser_name: Name of the parser for which the thresholds are checked.
        :return: Boolean indicating whether the thresholds are exceeded.
        """
        file_diff = []
        for key, value in file_data.items():
            if isinstance(value, list):
                for item in value:
                    if diff := self._check_diff(item, parser_name):
                        file_diff.append(diff)

            if diff := self.rule_class.evaluate_rule(key, value, parser_name):
                file_diff.append(diff)

        return file_diff

    def _get_version_diff(
        self, first_version: MinorVersion, second_version: MinorVersion
    ) -> List[dict]:
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
                    pass
            return compared_data

        first_version_data = self._get_data(first_version.checksum)
        second_version_data = self._get_data(second_version.checksum)

        file_diff = []
        for file in first_version_data[first_version.checksum]:
            second_version_file = self._get_data_from_file(
                file_path=file["file_path"], data=second_version_data[second_version.checksum]
            )

            for parser in file["data"]:
                if (
                    CONFIG["compare_data_filter_parsers"]
                    and parser["parser_name"] not in CONFIG["compare_data_filter_parser_names"]
                ):
                    continue

                if parser["parser_name"] not in RULE_CONFIG.keys():
                    continue

                if not RULE_CONFIG[parser["parser_name"]]["active"]:
                    continue

                second_version_parser_data = self._get_parser_data(
                    parser["parser_name"], second_version_file["data"]
                )
                diff = compare_dicts(parser["data"], second_version_parser_data)
                file_diff.append(
                    {
                        "parser_name": parser["parser_name"],
                        "file_name": file["file_path"],
                        "data": diff,
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
        return get_stats_of("indicator_data", stats_ids=[git_hash], minor_version=git_hash)

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

    def should_check_profiles(self, _: Profile, __: Profile) -> tuple[bool, float]:
        """We check all pairs of profiles always when checking by whole repository selector

        :param _: analysed target profile
        :param __: corresponding baseline profile (compared against)
        :return: always true with 100% confidence
        """
        return True, 1

    def _find_all_by_file_path(data_list, file_path_to_find):
        return [item for item in data_list if file_path_to_find in item.get("file_path")]


# def _find_all_paths(data_list: List[dict]):
#     paths = []
#     for data in data_list:
#         if not (new_path := data["file_path"].rsplit("/", 1)[0]) in paths:
#             paths.append(new_path)
#
#     return [{"path": path, "data": []} for path in paths]
#


def select_test(minor_version):
    x = BetterRepositorySelection()
    x.should_check_version(minor_version)
