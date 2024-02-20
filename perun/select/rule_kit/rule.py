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

threshold_functions = {
    "from": lambda value, threshold: value > threshold,
    "to": lambda value, threshold: value < threshold,
    "between": lambda value, from_threshold, to_threshold: from_threshold < value < to_threshold
}

class Rule:
    def check_rule(self, key, value, parser_name) -> bool:
        if parser_name not in RULE_CONFIG.keys():
            return

        if not RULE_CONFIG[parser_name]["active"]:
            return

        if key not in RULE_CONFIG[parser_name]["rules"].keys():
            return

        for rule in RULE_CONFIG[parser_name]["rules"][key]:
            threshold_functions[rule["threshold_type"]](value, rule["from"])
