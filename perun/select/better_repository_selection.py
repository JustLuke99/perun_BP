# Standard Imports
import os
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
from perun.vcs.git_repository import GitRepository
from perun.select.rule_kit.rule import RULE_CONFIG, Rule

CONFIG = {
    "compare_data_filter_parsers": True,
    "compare_data_filter_parser_names": ["RadonParser", "LizardParser"],
    "check_version_type": "last",
}


# class BetterRepositorySelection(AbstractBaseSelection):
class BetterRepositorySelection:
    __slots__ = ("git_repo", "rule_class")

    def __init__(self):
        self.git_repo = GitRepository("/home/luke/PycharmProjects/perun_BP")
        self.rule_class = Rule()

    # def should_check_version(self, head_version: MinorVersion) -> tuple[bool, float]:
    def should_check_version(self, target_version: MinorVersion) -> tuple[bool, float]:
        """We check all versions always when checking by whole repository selector

        :param target_version: analysed target version
        :return: always true with 100% confidence
        """

        git_repo = GitRepository(os.getcwd())

        # minor_versions = [x for x in git_repo.walk_minor_versions(target_version.checksum)]
        minor_versions = [x for x in git_repo.walk_minor_versions("7acd059b05c984afea70692d4c25c29825d8d12c")]


        # version_one, version_two = [b
        #     x
        #     for x in git_repo.walk_minor_versions(head_hash)
        #     if x.checksum == "7acd059b05c984afea70692d4c25c29825d8d12c"
        #     or x.checksum == "1168e8e02858ae1ec389ff3e37df7fceed54bdff"
        # ]
        if len(minor_versions) < 2:
            exit()

        version_one, version_two = minor_versions[:2]

        return self.should_check_versions(version_one, version_two)

    def should_check_versions(
        self, first_version: MinorVersion, second_version: MinorVersion
    ) -> tuple[bool, float]:
        """We check all pairs of versions always when checking by whole repository selector

        :param first_version: analysed target version
        :param second_version: corresponding baseline version (compared against)
        :return: always true with 100% confidence
        """
        diff = self._get_version_diff(first_version, second_version)

        should_check = self._check_diff_thresholds(diff_data=diff)
        print("Hehe: ", should_check)

        return should_check

    def _check_diff_thresholds(self, diff_data):
        """
        Check if the differences in the given data exceed the thresholds defined in the configuration.

        :param diff_data: List of dictionaries containing file differences.
        :return: Tuple (should_check, confidence) where should_check is a boolean indicating whether to check the version,
                 and confidence is a float indicating the confidence level.
        """
        for file_diff in diff_data:
            if file_diff["parser_name"] not in RULE_CONFIG.keys():
                continue

            if self._check_diff(file_diff["data"], file_diff["parser_name"]):
                return True

        return False

    def _check_diff(self, file_data, parser_name):
        """
        Check if the differences in the given file data exceed the thresholds defined in the configuration for a specific parser.

        :param file_data: Dictionary containing data about a file.
        :param parser_name: Name of the parser for which the thresholds are checked.
        :return: Boolean indicating whether the thresholds are exceeded.
        """
        for key, value in file_data.items():
            if isinstance(value, list):
                for item in value:
                    if self._check_diff(item, parser_name):
                        return True


            # if key not in CONFIG["parsers"][parser_name]:
            #     continue
            # 
            # rule = CONFIG["parsers"][parser_name][key]
            # range_type, num = rule.split(" ")
            # num2 = None
            #
            # if range_type == "to":
            #     if float(num) > float(value):
            #         return True
            # elif range_type == "from":
            #     if float(num) < float(value):
            #         return True
            # elif range_type == "between":
            #     if float(num) < float(value) < float(num2):
            #         return True

        return False

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


def _find_all_paths(data_list: List[dict]):
    paths = []
    for data in data_list:
        if not (new_path := data["file_path"].rsplit("/", 1)[0]) in paths:
            paths.append(new_path)

    return [{"path": path, "data": []} for path in paths]


def select_test(minor_version):
    x = BetterRepositorySelection()
    x.should_check_version(minor_version)
