RULE_CONFIG = {
    "RadonParser": {
        "active": True,
        "rules": {
            "lines_of_code": [{"threshold_type": "from", "from": 5}],
            "blank": [{"threshold_type": "to", "to": 10}],
            "cyclomatic_complexity": [{"threshold_type": "between", "from": 3, "to": 6}],
        },
    },
    "LizardParser": {
        "active": False,
        "rules": {
            "token_count": [{"threshold_type": "from", "from": 2}],
        },
    },
}


class Rule:
    def check_rule(self, key, value, parser_name) -> bool:
        ...
