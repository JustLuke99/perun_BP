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


# class BetterRepositorySelection(AbstractBaseSelection):
class BetterRepositorySelection:
    # nastavení soubor/složka(rek)/projekt -checkby file/folder/project
    # nastevní thresholdu - hodnota/hodnoty/dynamicky podle průměru (musí být celý prjekt/posledních x commitů) -treshhold num/nums/dynamic

    # def should_check_version(self, head_version: MinorVersion) -> tuple[bool, float]:
    def should_check_version(self, git_hash) -> tuple[bool, float]:
        """We check all versions always when checking by whole repository selector

        :param _: analysed target version
        :return: always true with 100% confidence
        """

        def compare_values(compare_value, compare_second_value):
            if isinstance(compare_value, list):

                ...
            elif isinstance(compare_value, dict):
                ...
            else:
                # TODO změnit na !=
                if compare_value == compare_second_value:
                    file_diff[file["file_path"]][parser["parser_name"]][key] = value - second_data[key]

        head_data = self.get_data(get_minor_head())

        file_diff = defaultdict(lambda: defaultdict(dict))
        for file in head_data[get_minor_head()]:
            second_item = self.get_data_from_file(
                file_path=file["file_path"], data=head_data[get_minor_head()]
            )

            for parser in file["data"]:
                # TODO improve ["RadonParser"]
                if not parser["parser_name"] in ["RadonParser"]:
                    continue

                parser_data = parser["data"]
                second_data = self.get_parser_data(parser["parser_name"], second_item["data"])
                for key, value in parser_data.items():
                    compare_values(value, second_data[key])


        # print(head_data)
        print(file_diff)

        parents = vcs.walk_minor_versions(get_minor_head())
        x = WholeRepositorySelection.get_skeleton(self, target_version=get_minor_head())
        print(x)

        # print([x for x in parents])
        # print([x.checksum for x in parents])

        return True, 1

    def get_data(self, git_hash):
        return get_stats_of("indicator_data", [git_hash])

    def get_parser_data(self, parser_name, data):
        for parser in data:
            if parser["parser_name"] == parser_name:
                return parser["data"]

    def get_data_from_file(self, file_path, data):
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
