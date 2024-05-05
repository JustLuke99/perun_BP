"""
Author: Kraus Lukáš
Date: 5.5.2024
"""


class BaseIndicator:
    """
    Abstract class for indicators.

    Attributes:
    - supported_languages (list): The list of supported languages.

    Methods:
    - get_languages: Returns the supported languages.
    - parse: Parses the source code.
    """

    supported_languages: list

    def get_languages(self):
        """
        Returns the supported languages.

        Returns:
        - list: The supported languages.
        """
        return self.supported_languages

    def parse(self, **kwargs):
        """
        Parses the source code.

        Parameters:
        - **kwargs: The keyword arguments.

        Returns:
        - Any: The parsed data.
        """
        raise NotImplementedError
