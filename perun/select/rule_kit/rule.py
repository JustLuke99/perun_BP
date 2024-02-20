RULE_CONFIG = {
    "RadonParser": {
        "active": True,
        "rules": {
            "lines_of_code": [{"threshold_type": "from", "from": 5, "weight": 1}],
            "blank": [{"threshold_type": "to", "to": 10, "weight": 2}],
            "cyclomatic_complexity": [
                {"threshold_type": "between", "from": 3, "to": 6, "weight": 1}
            ],
        },
    },
    "LizardParser": {
        "active": False,
        "rules": {
            "token_count": [{"threshold_type": "from", "from": 2, "weight": 1}],
        },
    },
}

threshold_functions = {
    "from": lambda value, threshold: value > threshold,
    "to": lambda value, threshold: value < threshold,
    "between": lambda value, from_threshold, to_threshold: from_threshold < value < to_threshold,
}


class Rule:
    @staticmethod
    def check_rule(key, value, parser_name) -> None | bool:
        if parser_name not in RULE_CONFIG.keys():
            return

        if not RULE_CONFIG[parser_name]["active"]:
            return

        if key not in RULE_CONFIG[parser_name]["rules"].keys():
            return

        results = []
        for rule in RULE_CONFIG[parser_name]["rules"][key]:
            results.append({"weight": rule["weight"], "result": threshold_functions[rule["threshold_type"]](value, rule["from"])})

        print("")