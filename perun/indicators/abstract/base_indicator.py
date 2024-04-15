class BaseIndicator:
    supported_languages: list

    def get_languages(self):
        return self.supported_languages

    def parse(self, **kwargs):
        raise NotImplementedError
