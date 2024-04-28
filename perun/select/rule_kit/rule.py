# if not weight, it will be default (1)
RULE_CONFIG = {
    "RadonParser": {
        "active": True,
        "rules": {
            "lines_of_code": [{"threshold_type": "value_from", "from":-1, "weight": 1}],
            #"blank": [{"threshold_type": "value_from", "from": -1, "weight": 2}],
            # "cyclomatic_complexity": [{"threshold_type": "value_between", "from": 1, "to": 2}],
            # "number_of_functions": [{"threshold_type": "value_between", "from": 1, "to": 7}],
        },
    },
    "LizardParser": {
        "active": True,
        "rules": {
            # "token_count": [{"threshold_type": "value_from", "from": 2, "weight": 1}],
            # "average_length_of_code": [{"threshold_type": "value_from", "from": -1, "weight": 1}],
            "number_of_functions": [{"threshold_type": "value_from", "from": -1, "weight": 1}],
        },
    },
}

threshold_functions = {
    "value_from": lambda value, rule: value > rule["from"],
    "value_to": lambda value, rule: value < rule["to"],
    "value_between": lambda value, rule: rule["from"] < value < rule["to"],
    # "list_len_from": lambda value, rule: len(value) > rule["from"],
    # "list_len_to": lambda value, rule: len(value) < rule["to"],
    # "list_len_between": lambda value, rule: rule["from"] < len(value) < rule["to"],
}

# validations = {
#     "list_len_from": lambda value: all(isinstance(item, str) for item in value),
#     "list_len_to": lambda value: all(isinstance(item, str) for item in value),
#     "list_len_between": lambda value: all(isinstance(item, str) for item in value),
# }


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
