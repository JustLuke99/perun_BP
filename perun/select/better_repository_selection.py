# Standard Imports
from typing import Iterator

# Third-Party Imports

# Perun Imports
from perun import vcs
from perun.profile import helpers as profile_helpers
from perun.profile.factory import Profile
from perun.profile.helpers import ProfileInfo
from perun.select.abstract_base_selection import AbstractBaseSelection
from perun.utils.structs import MinorVersion
from perun.logic.stats import get_stats_of


class BetterRepositorySelection(AbstractBaseSelection):
    # nastavení soubor/složka(rek)/projekt -checkby file/folder/project
    # nastevní thresholdu - hodnota/hodnoty/dynamicky podle průměru (musí být celý prjekt/posledních x commitů) -treshhold num/nums/dynamic
    def should_check_version(self, _: MinorVersion) -> tuple[bool, float]:
        """We check all versions always when checking by whole repository selector

        :param _: analysed target version
        :return: always true with 100% confidence
        """
        # TODO update MinorVersion.HASH
        indicator_head_data = get_stats_of("indicator_data", [MinorVersion.HASH])

        parents = vcs.walk_minor_versions(MinorVersion.HASH)

        # NOTE this should be checked in func get_stats_of()
        # # TODO update to better if
        # if indicator_data is None:
        #     raise Exception(f"No data (stats) available for version {MinorVersion.HASH}")

        # TODO udělat hledání a počítání souborů ve složkách podle parserů - udělat parsery v configu nebo tak nějak :)

        return True, 1

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


from typing import List


def _find_all_paths(data_list: List[dict]) -> List[str]:
    paths = []
    for data in data_list:
        if not (new_path := data["file_path"].rsplit("/", 1)[0]) in paths:
            paths.append(new_path)

    return paths
