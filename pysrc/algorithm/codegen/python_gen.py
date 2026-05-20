"""Generate Python function from algorithm fact.

Each step type has a generator function that takes step data
and returns a list of code lines. A dispatch table maps step
types to generators. Expression trees are converted to Python
expression strings by walking the tree and resolving operation
symbols through python_impl facts.
"""

import yaml
from expression import load_fact_info


# --- operation symbol resolution ---

def resolve_op_symbol(kg, op_path):
    """Resolve operation fact path to Python symbol via python_impl chain."""
    info = load_fact_info(kg, op_path)
    if info is None:
        return op_path.rsplit("/", 1)[-1]
    impl_type = info.get("has", {}).get("python_impl", {}).get("type", "")
    if not impl_type:
        return op_path.rsplit("/", 1)[-1]
    impl_info = load_fact_info(kg, impl_type)
    if impl_info is None:
        return op_path.rsplit("/", 1)[-1]
    val_as = impl_info.get("val_as", {})
    symbol = val_as.get("computer/sw/lang/python/operator", {}).get("symbol", "")
    if not symbol:
        symbol = val_as.get("computer/sw/lang/python/function", {}).get("name", "")
    return symbol or op_path.rsplit("/", 1)[-1]


# --- expression tree to Python string ---

UNARY_FUNCTIONS = {"len", "math.sqrt", "math.sin"}

PYTHON_KEYWORDS = {"from": "from_", "in": "in_", "class": "class_", "type": "type_"}


def _translate_python(s):
    """Translate dot notation field names that are Python keywords.

    input.from → input.from_
    input.array[j] → input.array[j] (no keyword)
    """
    s = str(s)
    if "." not in s:
        return s
    bracket_part = ""
    base = s
    if "[" in s:
        base, bracket_part = s.split("[", 1)
        bracket_part = "[" + bracket_part
    parts = base.split(".")
    translated = [PYTHON_KEYWORDS.get(p, p) for p in parts]
    return ".".join(translated) + bracket_part


def expr_to_python(kg, node):
    """Convert expression tree node to Python expression string."""
    if isinstance(node, str):
        return _translate_python(node)
    if isinstance(node, (int, float)):
        return str(node)
    if not isinstance(node, dict):
        return str(node)

    op_path = next(iter(node))
    operands = node[op_path]
    symbol = resolve_op_symbol(kg, op_path)
    parts = [expr_to_python(kg, o) for o in operands]

    if len(parts) == 1:
        if symbol in UNARY_FUNCTIONS:
            return f"{symbol}({parts[0]})"
        if symbol == "neg":
            return f"-{parts[0]}"
        return f"{symbol}({parts[0]})"

    return f"({parts[0]} {symbol} {parts[1]})"


# --- indentation helper ---

def indent(lines):
    """Add one level of indentation to each line."""
    return ["    " + line for line in lines]


# --- step generators ---
# Each takes (step_as, ctx) and returns list of code lines.
# ctx = {"kg": kg, "steps": steps}

def gen_assign(step_as, ctx):
    var = step_as.get("variable", "")
    frm = _translate_python(step_as.get("from", ""))
    return [f"{var} = {frm}"]


def gen_append(step_as, ctx):
    lst = step_as.get("list", "")
    val = _translate_python(step_as.get("value", ""))
    return [f"{lst}.append({val})"]


def gen_assign_indexed(step_as, ctx):
    container = _translate_python(step_as.get("container", ""))
    index = _translate_python(step_as.get("index", ""))
    frm = _translate_python(step_as.get("from", ""))
    return [f"{container}[{index}] = {frm}"]


def condition_to_python(step_as, ctx):
    """Convert condition_yaml to Python expression string."""
    condition_yaml = step_as.get("condition_yaml", "")
    if condition_yaml:
        tree = yaml.safe_load(condition_yaml)
        return expr_to_python(ctx["kg"], tree)
    return "True"


def gen_if(step_as, ctx):
    cond_str = condition_to_python(step_as, ctx)

    lines = [f"if {cond_str}:"]

    then_step = step_as.get("then", "")
    if then_step:
        body = generate_chain(then_step, ctx)
        lines.extend(indent(body))

    else_step = step_as.get("else", "")
    if else_step:
        lines.append("else:")
        body = generate_chain(else_step, ctx)
        lines.extend(indent(body))

    return lines


def gen_for_each(step_as, ctx):
    index = step_as.get("index", "i")
    from_val = step_as.get("from", 0)
    to_length = step_as.get("to_length", "")
    to_var = step_as.get("to", "")

    if to_length:
        range_end = f"len({to_length})"
    elif to_var:
        range_end = f"int({to_var})"
    else:
        range_end = "0"

    lines = [f"for {index} in range({from_val}, {range_end}):"]

    body_step = step_as.get("body", "")
    if body_step:
        body = generate_chain(body_step, ctx)
        lines.extend(indent(body))

    return lines


def gen_while(step_as, ctx):
    cond_str = condition_to_python(step_as, ctx)
    lines = [f"while {cond_str}:"]
    body_step = step_as.get("body", "")
    if body_step:
        body = generate_chain(body_step, ctx)
        lines.extend(indent(body))
    return lines


def _format_arg_python(arg_val):
    """Format a call argument as Python SimpleNamespace."""
    if isinstance(arg_val, dict):
        fields = ", ".join(
            f"{PYTHON_KEYWORDS.get(k, k)}={v}" for k, v in arg_val.items())
        return f"SimpleNamespace({fields})"
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
            args.append(f"{arg_name}={_format_arg_python(arg_val)}")

    call_str = f"{func_name}({', '.join(args)})"
    if result_var:
        return [f"{result_var} = {call_str}"]
    return [call_str]


def gen_evaluate_expression(step_as, ctx):
    result_var = step_as.get("result_variable", "result")
    expr_yaml = step_as.get("expression_yaml", "")
    if expr_yaml:
        tree = yaml.safe_load(expr_yaml)
        expr_str = expr_to_python(ctx["kg"], tree)
    else:
        expr_str = "None"
    return [f"{result_var} = {expr_str}"]


def gen_evaluate_expression_fact(step_as, ctx):
    result_var = step_as.get("result_variable", "result")
    expr_fact = step_as.get("expression_fact", "")
    return [f"# TODO: evaluate expression fact '{expr_fact}'",
            f"{result_var} = None"]


def gen_return(step_as, ctx):
    var = step_as.get("variable", "")
    return [f"return {var}"]


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
    """Generate code for a step and follow its 'next' link.

    Returns a list of code lines (without indentation prefix).
    """
    steps = ctx["steps"]
    if step_name not in steps:
        return []

    step = steps[step_name]
    step_type = step["type"]
    step_as = step.get("val_as", {}).get(step_type, {})

    generator = STEP_GENERATORS.get(step_type)
    if generator is None:
        return [f"# unknown step type: {step_type}"]

    ctx["_current_step"] = step
    lines = generator(step_as, ctx)

    # follow the next link
    next_step = step_as.get("next", "")
    if next_step and next_step in steps:
        lines.extend(generate_chain(next_step, ctx))

    return lines


# --- main entry point ---

def generate_python(kg, algo_path):
    """Generate a Python function from an algorithm fact.

    Returns a string containing a complete Python function definition.
    """
    info = load_fact_info(kg, algo_path)
    if info is None:
        raise ValueError(f"Cannot load algorithm: {algo_path}")

    has = info.get("has", {})

    # metadata
    description = has.get("description", {}).get("val", "")
    func_name = algo_path.rsplit("/", 1)[-1]

    # input parameters — math/variable with data_type list, or ADT types
    params = []
    for attr, val in has.items():
        if "val" in val or attr.startswith("step_"):
            continue
        vtype = val.get("type", "")
        data_type = val.get("val_as", {}).get("math/variable", {}).get("data_type", "")
        if data_type == "list":
            params.append(f"{attr}: list")
        elif vtype and vtype not in ("str", "num", "math/variable", "math/constant") \
                and not vtype.startswith("computer/algorithm/"):
            params.append(attr)

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

    # build context
    ctx = {"kg": kg, "steps": steps}

    # generate function
    lines = [f"def {func_name}({', '.join(params)}):"]
    if description:
        lines.extend(indent([f'"""{description}"""']))

    body = generate_chain(first_step, ctx)
    lines.extend(indent(body))

    return "\n".join(lines) + "\n"
