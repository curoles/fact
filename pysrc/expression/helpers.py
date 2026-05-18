import yaml
from fact import Fact


PRIMITIVES = {"str", "num", "list"}


def load_fact_info(kg, path):
    if path in PRIMITIVES:
        return None
    if kg.load(path) != 0:
        return None
    fact = Fact(kg, path)
    if fact.construct() != 0:
        return None
    return kg.get_fact(path).get("info", {})


def extract_expression(info, name=None):
    has = info.get("has", {})
    for attr, val in has.items():
        if val.get("type") == "math/expression":
            if name is None or attr == name:
                val_as = val.get("val_as", {}).get("math/expression", {})
                expr_str = val_as.get("expression_str", "")
                expr_yaml = val_as.get("expression_yaml", "")
                tree = yaml.safe_load(expr_yaml) if expr_yaml else None
                return {
                    "name": attr,
                    "str": expr_str,
                    "yaml": expr_yaml,
                    "tree": tree,
                }
    return None


def extract_all_expressions(info):
    expressions = {}
    has = info.get("has", {})
    for attr, val in has.items():
        if val.get("type") == "math/expression":
            val_as = val.get("val_as", {}).get("math/expression", {})
            expr_str = val_as.get("expression_str", "")
            expr_yaml = val_as.get("expression_yaml", "")
            if expr_yaml:
                expressions[attr] = {
                    "str": expr_str,
                    "yaml": expr_yaml,
                    "tree": yaml.safe_load(expr_yaml),
                }
    return expressions
