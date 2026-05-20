"""Generate C++ function from algorithm fact.

Uses the same operation symbol resolution as python_gen
since basic operator symbols (+, -, >, <) are identical
in C++ and Python. Syntactic differences handled here:
  for loops   → C-style for(int i = from; i <= to; i++)
  len()       → .size()
  blocks      → curly braces
  statements  → semicolons
"""

import yaml
from expression import load_fact_info
from algorithm.codegen.python_gen import resolve_op_symbol


# --- expression tree to C++ string ---

def expr_to_cpp(kg, node):
    """Convert expression tree node to C++ expression string."""
    if isinstance(node, str):
        return node
    if isinstance(node, (int, float)):
        return str(node)
    if not isinstance(node, dict):
        return str(node)

    op_path = next(iter(node))
    operands = node[op_path]
    symbol = resolve_op_symbol(kg, op_path)
    parts = [expr_to_cpp(kg, o) for o in operands]

    if len(parts) == 1:
        if symbol == "len":
            return f"{parts[0]}.size()"
        if symbol == "neg":
            return f"-{parts[0]}"
        return f"{symbol}({parts[0]})"

    return f"({parts[0]} {symbol} {parts[1]})"


# --- indentation helper ---

def indent(lines):
    """Add one level of indentation to each line."""
    return ["    " + line for line in lines]


# --- step generators ---
# Each takes (step_as, ctx) and returns list of C++ code lines.

def gen_assign(step_as, ctx):
    var = step_as.get("variable", "")
    frm = step_as.get("from", "")
    declared = ctx.setdefault("declared", set())
    if var in declared:
        return [f"{var} = {frm};"]
    declared.add(var)
    return [f"auto {var} = {frm};"]


def gen_assign_indexed(step_as, ctx):
    container = step_as.get("container", "")
    index = step_as.get("index", "")
    frm = step_as.get("from", "")
    return [f"{container}[{index}] = {frm};"]


def gen_append(step_as, ctx):
    lst = step_as.get("list", "")
    val = step_as.get("value", "")
    return [f"{lst}.push_back({val});"]


def condition_to_cpp(step_as, ctx):
    """Convert condition_yaml to C++ expression string."""
    condition_yaml = step_as.get("condition_yaml", "")
    if condition_yaml:
        tree = yaml.safe_load(condition_yaml)
        return expr_to_cpp(ctx["kg"], tree)
    return "true"


def gen_if(step_as, ctx):
    cond_str = condition_to_cpp(step_as, ctx)

    lines = [f"if ({cond_str}) {{"]
    then_step = step_as.get("then", "")
    if then_step:
        body = generate_chain(then_step, ctx)
        lines.extend(indent(body))
    else_step = step_as.get("else", "")
    if else_step:
        lines.append("} else {")
        body = generate_chain(else_step, ctx)
        lines.extend(indent(body))
    lines.append("}")
    return lines


def gen_while(step_as, ctx):
    cond_str = condition_to_cpp(step_as, ctx)
    lines = [f"while ({cond_str}) {{"]
    body_step = step_as.get("body", "")
    if body_step:
        body = generate_chain(body_step, ctx)
        lines.extend(indent(body))
    lines.append("}")
    return lines


def gen_for_each(step_as, ctx):
    index = step_as.get("index", "i")
    from_val = step_as.get("from", 0)
    to_length = step_as.get("to_length", "")
    to_var = step_as.get("to", "")

    if to_length:
        condition = f"{index} < {to_length}.size()"
    elif to_var:
        condition = f"{index} < static_cast<int>({to_var})"
    else:
        condition = f"{index} < 0"

    lines = [f"for (int {index} = {from_val}; {condition}; {index}++) {{"]
    body_step = step_as.get("body", "")
    if body_step:
        body = generate_chain(body_step, ctx)
        lines.extend(indent(body))
    lines.append("}")
    return lines


def gen_evaluate_expression(step_as, ctx):
    result_var = step_as.get("result_variable", "result")
    expr_yaml = step_as.get("expression_yaml", "")
    if expr_yaml:
        tree = yaml.safe_load(expr_yaml)
        expr_str = expr_to_cpp(ctx["kg"], tree)
    else:
        expr_str = "0"
    declared = ctx.setdefault("declared", set())
    if result_var in declared:
        return [f"{result_var} = {expr_str};"]
    declared.add(result_var)
    return [f"auto {result_var} = {expr_str};"]


def gen_evaluate_expression_fact(step_as, ctx):
    result_var = step_as.get("result_variable", "result")
    expr_fact = step_as.get("expression_fact", "")
    return [f"// TODO: evaluate expression fact '{expr_fact}'",
            f"auto {result_var} = 0;"]


def _format_arg_cpp(arg_val):
    """Format a call argument as C++ code."""
    if isinstance(arg_val, dict):
        fields = ", ".join(f".{k} = {v}" for k, v in arg_val.items())
        return "{" + fields + "}"
    return str(arg_val)


def gen_call(step_as, ctx):
    algo_path = step_as.get("algorithm", "")
    result_var = step_as.get("result_variable", "")
    func_name = algo_path.rsplit("/", 1)[-1]

    step = ctx.get("_current_step", {})
    args = []
    for as_key, as_vals in step.get("val_as", {}).items():
        if as_key == "computer/algorithm/call":
            continue
        for arg_name, arg_val in as_vals.items():
            args.append(_format_arg_cpp(arg_val))

    call_str = f"{func_name}({', '.join(args)})"
    declared = ctx.setdefault("declared", set())
    if result_var in declared:
        return [f"{result_var} = {call_str};"]
    declared.add(result_var)
    return [f"auto {result_var} = {call_str};"]


def gen_return(step_as, ctx):
    var = step_as.get("variable", "")
    if ctx.get("return_type") == "void":
        return []
    return [f"return {var};"]


# --- dispatch table ---

STEP_GENERATORS = {
    "computer/algorithm/assign": gen_assign,
    "computer/algorithm/append": gen_append,
    "computer/algorithm/assign_indexed": gen_assign_indexed,
    "computer/algorithm/if": gen_if,
    "computer/algorithm/call": gen_call,
    "computer/algorithm/while": gen_while,
    "computer/algorithm/indexed/for_each": gen_for_each,
    "computer/algorithm/evaluate_expression": gen_evaluate_expression,
    "computer/algorithm/evaluate_expression_fact": gen_evaluate_expression_fact,
    "computer/algorithm/return": gen_return,
}


# --- chain walking ---

def generate_chain(step_name, ctx):
    """Generate C++ code for a step and follow its 'next' link."""
    steps = ctx["steps"]
    if step_name not in steps:
        return []

    step = steps[step_name]
    step_type = step["type"]
    step_as = step.get("val_as", {}).get(step_type, {})

    generator = STEP_GENERATORS.get(step_type)
    if generator is None:
        return [f"// unknown step type: {step_type}"]

    ctx["_current_step"] = step
    lines = generator(step_as, ctx)

    next_step = step_as.get("next", "")
    if next_step and next_step in steps:
        lines.extend(generate_chain(next_step, ctx))

    return lines


# --- main entry point ---

def generate_cpp(kg, algo_path):
    """Generate a C++ template function from an algorithm fact."""
    info = load_fact_info(kg, algo_path)
    if info is None:
        raise ValueError(f"Cannot load algorithm: {algo_path}")

    has = info.get("has", {})

    description = has.get("description", {}).get("val", "")
    func_name = algo_path.rsplit("/", 1)[-1]

    # input parameters — math/variable with data_type list
    params = []
    for attr, val in has.items():
        data_type = val.get("val_as", {}).get("math/variable", {}).get("data_type", "")
        if data_type == "list":
            params.append(f"std::vector<T>& {attr}")

    # collect steps
    steps = {attr: val for attr, val in has.items() if attr.startswith("step_")}

    # find first step
    first_step = None
    for name in ["step_init", "step_start", "step_outer_loop"]:
        if name in steps:
            first_step = name
            break
    if first_step is None and steps:
        first_step = next(iter(steps))

    # collect loop index names to exclude from pre-declarations
    loop_indices = set()
    for attr, val in has.items():
        if not attr.startswith("step_"):
            continue
        step_type = val.get("type", "")
        if step_type in ("computer/algorithm/indexed/for_each",):
            step_as = val.get("val_as", {}).get(step_type, {})
            idx = step_as.get("index", "")
            if idx:
                loop_indices.add(idx)

    # collect declared variables, determine type (T vs int) from description
    INDEX_HINTS = {"index", "bound", "position", "next"}
    variables = []
    var_types = {}
    for attr, val in has.items():
        if val.get("type") != "math/variable" or attr in loop_indices:
            continue
        variables.append(attr)
        desc = val.get("val_as", {}).get("math/variable", {}).get("description", "").lower()
        if any(hint in desc for hint in INDEX_HINTS):
            var_types[attr] = "int"
        else:
            var_types[attr] = "T"
    declared = set(variables) | loop_indices

    # determine return type
    return_type = "T"
    for attr, val in steps.items():
        step_type = val.get("type", "")
        if step_type == "computer/algorithm/return":
            ret_var = val.get("val_as", {}).get(step_type, {}).get("variable", "")
            if ret_var in var_types:
                return_type = var_types[ret_var]
            elif ret_var in [a for a, v in has.items()
                            if v.get("val_as", {}).get("math/variable", {}).get("data_type") == "list"]:
                return_type = "void"

    ctx = {"kg": kg, "steps": steps, "declared": declared, "return_type": return_type}

    # generate function
    lines = []
    if description:
        lines.append(f"// {description}")

    lines.append("template<typename T>")
    lines.append(f"{return_type} {func_name}({', '.join(params)}) {{")

    # declare all variables at function scope with correct types
    for var in variables:
        vtype = var_types.get(var, "T")
        lines.extend(indent([f"{vtype} {var} = {{}};"]))

    body = generate_chain(first_step, ctx)
    lines.extend(indent(body))

    lines.append("}")
    return "\n".join(lines) + "\n"
