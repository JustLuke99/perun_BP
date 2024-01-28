class Selection:
    def __init__(self, head_hash):
        self.head_hash = head_hash
        self.head_data = None

    def should_compare_head(self, head_hash) -> bool:
        self.should_check_version(head_hash, is_head=True)
        pass

    def should_check_version(self, version_hash, is_head: bool = False) -> bool:
        # zde se bude kontrolovat HEAD/version, zda má smysl porovnávat se zbytkem

        # získát soubor (-> data) z .../stats (pokud to je head, ulož do self.head_data)

        # porovnat hodnoty, zda má verzi smysl porovnávat
        pass

    def should_check_versions(self, version_hash):
        # zde se bude porovnávat verze z argumentů s head verzí

        # získát version soubor (-> data) z .../stats

        # porovnat head s version
        pass