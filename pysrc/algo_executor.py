import yaml
from expression import ExpressionEvaluator, load_fact_info, extract_expression


class AlgorithmExecutor:
    def __init__(self, kg):
        self.kg = kg
        self.evaluator = ExpressionEvaluator(kg)

    def execute(self, algo_path, inputs):
        info = load_fact_info(self.kg, algo_path)
        if info is None:
            raise ValueError(f"Cannot load algorithm: {algo_path}")

        has = info.get("has", {})

        steps = {}
        for attr, val in has.items():
            if attr.startswith("step_"):
                steps[attr] = val

        first_step = None
        for name in ["step_init", "step_start"]:
            if name in steps:
                first_step = name
                break
        if first_step is None and steps:
            first_step = next(iter(steps))

        variables = dict(inputs)
        return self._execute_step(first_step, steps, variables)

    def _execute_step(self, step_name, steps, variables):
        step = steps[step_name]
        step_type = step["type"]
        step_as = step.get("val_as", {}).get(step_type, {})

        result = None
        if step_type == "computer/algorithm/assign":
            result = self._exec_assign(step_as, variables)
        elif step_type == "computer/algorithm/if":
            result = self._exec_if(step_as, variables, steps)
        elif step_type == "computer/algorithm/while":
            result = self._exec_while(step_as, variables, steps)
        elif step_type == "computer/algorithm/indexed/for_each":
            result = self._exec_for_each(step_as, variables, steps)
        elif step_type == "computer/algorithm/assign_indexed":
            result = self._exec_assign_indexed(step_as, variables)
        elif step_type == "computer/algorithm/swap":
            result = self._exec_swap(step_as, variables)
        elif step_type == "computer/algorithm/call":
            result = self._exec_call(step, variables)
        elif step_type == "computer/algorithm/evaluate_expression":
            result = self._exec_evaluate_expression_inline(step_as, variables)
        elif step_type == "computer/algorithm/evaluate_expression_fact":
            result = self._exec_evaluate_expression_fact(step_as, variables)
        elif step_type == "computer/algorithm/return":
            return self._exec_return(step_as, variables)

        next_step = step_as.get("next", "")
        if next_step and next_step in steps:
            return self._execute_step(next_step, steps, variables)
        return result

    def _resolve_dot(self, name, variables):
        """Resolve dot notation: input.array → variables["input"]["array"]."""
        parts = name.split(".")
        val = variables[parts[0]]
        for part in parts[1:]:
            val = val[part]
        return val

    def _resolve_value(self, expr, variables):
        if isinstance(expr, (int, float)):
            return expr
        expr = str(expr)
        if "[" in expr:
            arr_part, idx_str = expr.rstrip("]").split("[")
            idx = int(self._resolve_value(idx_str, variables)) if idx_str in variables else int(idx_str)
            if "." in arr_part:
                arr = self._resolve_dot(arr_part, variables)
            else:
                arr = variables[arr_part]
            return arr[idx]
        if "." in expr:
            return self._resolve_dot(expr, variables)
        if expr in variables:
            return variables[expr]
        try:
            return float(expr)
        except ValueError:
            return expr

    def _resolve_arg(self, arg_val, variables):
        """Resolve an argument — handles dicts (compound types), lists, and scalars."""
        if isinstance(arg_val, dict):
            return {k: self._resolve_value(v, variables) for k, v in arg_val.items()}
        if isinstance(arg_val, list):
            return [self._resolve_value(v, variables) for v in arg_val]
        return self._resolve_value(arg_val, variables)

    def _exec_call(self, step, variables):
        """Execute a call step — invoke another algorithm with arguments."""
        step_type = step["type"]
        step_as = step.get("val_as", {}).get(step_type, {})
        algo_path = step_as.get("algorithm", "")
        result_var = step_as.get("result_variable", "")

        # collect arguments from the called algorithm's as block
        called_args = {}
        for as_key, as_vals in step.get("val_as", {}).items():
            if as_key == step_type:
                continue
            for arg_name, arg_val in as_vals.items():
                called_args[arg_name] = self._resolve_arg(arg_val, variables)

        result = self.execute(algo_path, called_args)
        if result_var:
            variables[result_var] = result

    def _exec_assign(self, step_as, variables):
        var_name = step_as.get("variable", "")
        from_expr = step_as.get("from", "")
        variables[var_name] = self._resolve_value(from_expr, variables)

    def _eval_condition(self, step_as, variables):
        condition_yaml = step_as.get("condition_yaml", "")
        if condition_yaml:
            import yaml
            tree = yaml.safe_load(condition_yaml)
            return self.evaluator.evaluate(tree, dict(variables))
        return False

    MAX_WHILE_ITERATIONS = 10000

    def _exec_while(self, step_as, variables, steps):
        body_step = step_as.get("body", "")
        iterations = 0
        while self._eval_condition(step_as, variables):
            if body_step and body_step in steps:
                self._execute_step(body_step, steps, variables)
            iterations += 1
            assert iterations < self.MAX_WHILE_ITERATIONS, "while loop exceeded max iterations"

    def _exec_if(self, step_as, variables, steps):
        if self._eval_condition(step_as, variables):
            then_step = step_as.get("then", "")
            if then_step and then_step in steps:
                return self._execute_step(then_step, steps, variables)

    def _exec_for_each(self, step_as, variables, steps):
        index_name = step_as.get("index", "i")
        from_val = int(self._resolve_value(step_as.get("from", 0), variables))
        to_length_key = step_as.get("to_length", "")
        if to_length_key:
            arr = self._resolve_value(to_length_key, variables)
            end = len(arr)
        else:
            end = int(self._resolve_value(step_as.get("to", 0), variables))
        body_step = step_as.get("body", "")

        for i in range(from_val, end):
            variables[index_name] = i
            if body_step and body_step in steps:
                self._execute_step(body_step, steps, variables)
        if index_name in variables:
            del variables[index_name]

    def _exec_assign_indexed(self, step_as, variables):
        container = step_as.get("container", "")
        idx = int(self._resolve_value(step_as.get("index", ""), variables))
        val = self._resolve_value(step_as.get("from", ""), variables)
        variables[container][idx] = val

    def _exec_swap(self, step_as, variables):
        arr_name = step_as.get("array", "")
        idx_a = self._resolve_value(step_as.get("index_a", ""), variables)
        idx_b = self._resolve_value(step_as.get("index_b", ""), variables)
        arr = variables[arr_name]
        a, b = int(idx_a), int(idx_b)
        arr[a], arr[b] = arr[b], arr[a]

    def _exec_evaluate_expression_inline(self, step_as, variables):
        expr_yaml = step_as.get("expression_yaml", "")
        result_var = step_as.get("result_variable", "result")
        import yaml
        tree = yaml.safe_load(expr_yaml)
        variables[result_var] = self.evaluator.evaluate(tree, dict(variables))

    def _exec_evaluate_expression_fact(self, step_as, variables):
        expr_path_key = step_as.get("expression_fact", "")
        expr_path = variables.get(expr_path_key, expr_path_key)
        result_var = step_as.get("result_variable", "result")
        info = load_fact_info(self.kg, expr_path)
        if info is None:
            raise ValueError(f"Cannot load expression: {expr_path}")
        expr = extract_expression(info)
        if expr is None or expr["tree"] is None:
            raise ValueError(f"No expression tree in: {expr_path}")
        variables[result_var] = self.evaluator.evaluate(expr["tree"], dict(variables))

    def _exec_return(self, step_as, variables):
        var_name = step_as.get("variable", "")
        return variables.get(var_name)
