# if not weight, it will be default (1)
RULE_CONFIG = {
    "RadonParser": {
        "active": True,
        "rules": {
            "lines_of_code": [{"threshold_type": "from", "from": 5, "weight": 1}],
            "blank": [{"threshold_type": "to", "to": 10, "weight": 2}],
            "cyclomatic_complexity": [
                {"threshold_type": "between", "from": 3, "to": 6}
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
    "from": lambda value, rule: value > rule["from"],
    "to": lambda value, rule: value < rule["to"],
    "between": lambda value, rule: rule["from"] < value < rule["to"],
}


class Rule:
    @staticmethod
    def _check_if_should_be_checked(key, value, parser_name):
        if parser_name not in RULE_CONFIG.keys():
            return True

        if not RULE_CONFIG[parser_name]["active"]:
            return True

        if key not in RULE_CONFIG[parser_name]["rules"].keys():
            return True

        return False

    def evaluate_rule(self, key, value, parser_name) -> None | bool:
        if self._check_if_should_be_checked(key, value, parser_name):
            return

        results = []
        for rule in RULE_CONFIG[parser_name]["rules"][key]:
            results.append(
                {
                    "weight": rule.get("weight", 1),
                    "result": threshold_functions[rule["threshold_type"]](value, rule),
                    "rule": rule,
                    "parser_name": parser_name,
                    "key": key,
                    "value": value,
                }
            )

        return results
