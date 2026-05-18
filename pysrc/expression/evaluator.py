import math
import operator

from expression.helpers import load_fact_info

SYMBOL_TO_FN = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "**": operator.pow,
    "==": operator.eq,
    "<": operator.lt,
    ">": operator.gt,
    ">=": operator.ge,
    "&": operator.and_,
    "neg": operator.neg,
    "math.sqrt": math.sqrt,
    "math.sin": math.sin,
    "len": len,
}


class ExpressionEvaluator:
    def __init__(self, kg):
        self.kg = kg
        self._op_cache = {}

    def resolve_operation(self, op_path):
        if op_path in self._op_cache:
            return self._op_cache[op_path]
        info = load_fact_info(self.kg, op_path)
        if info is None:
            return None
        impl_type = info.get("has", {}).get("python_impl", {}).get("type", "")
        if not impl_type:
            return None
        impl_info = load_fact_info(self.kg, impl_type)
        if impl_info is None:
            return None
        val_as = impl_info.get("val_as", {})
        symbol = val_as.get("computer/sw/lang/python/operator", {}).get("symbol", "")
        if not symbol:
            symbol = val_as.get("computer/sw/lang/python/function", {}).get("name", "")
        fn = SYMBOL_TO_FN.get(symbol)
        self._op_cache[op_path] = fn
        return fn

    def _resolve_value(self, expr, variables):
        """Resolve a value string — handles variables and array[index] access."""
        if isinstance(expr, (int, float)):
            return expr
        expr = str(expr)
        if "[" in expr:
            arr_name, idx_str = expr.rstrip("]").split("[")
            idx = int(variables[idx_str]) if idx_str in variables else int(idx_str)
            return variables[arr_name][idx]
        if expr in variables:
            return variables[expr]
        return float(expr)

    def evaluate(self, node, variables):
        if isinstance(node, str):
            try:
                return self._resolve_value(node, variables)
            except (ValueError, KeyError, IndexError):
                return float(node)
            return float(node)
        if isinstance(node, (int, float)):
            return float(node)
        if isinstance(node, dict):
            op_path = next(iter(node))
            if op_path == "math/expression/conditional":
                branches = node[op_path]
                cond = self.evaluate(branches["condition"], variables)
                if cond:
                    return self.evaluate(branches["then"], variables)
                else:
                    return self.evaluate(branches["else"], variables)
            if op_path == "math/algebra/expression/indexed/sum":
                return self._eval_indexed_sum(node[op_path], variables)
            if op_path == "math/expression/indexed/element_at":
                node_data = node[op_path]
                collection = variables[node_data["collection"]]
                idx = int(variables[node_data["at"]])
                return collection[idx]
            operands = node[op_path]
            op_fn = self.resolve_operation(op_path)
            if op_fn is None:
                raise ValueError(f"Unknown operation: {op_path}")
            vals = [self.evaluate(o, variables) for o in operands]
            if len(vals) == 1:
                return op_fn(vals[0])
            return op_fn(vals[0], vals[1])
        raise ValueError(f"Cannot evaluate: {node}")

    def _eval_indexed_sum(self, node_data, variables):
        index_name = node_data["index"]
        from_val = int(node_data["from"])
        to_length_key = node_data.get("to_length")
        if to_length_key:
            to_val = len(variables[to_length_key]) - 1
        else:
            to_val = int(node_data["to"])
        body = node_data["body"]
        result = 0
        for i in range(from_val, to_val + 1):
            variables[index_name] = i
            result = result + self.evaluate(body, variables)
        del variables[index_name]
        return result
