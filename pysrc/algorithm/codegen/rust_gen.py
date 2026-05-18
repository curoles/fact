"""Generate Rust function from algorithm fact.

Uses the same operation symbol resolution as python_gen
since basic operator symbols (+, -, >, <) are identical
in Rust and Python. Rust-specific syntax:
  types       → generic T with Copy + PartialOrd
  for loops   → for i in from..to
  while       → while condition
  blocks      → curly braces
  variables   → let mut, reassignment without let
  arrays      → Vec<T>, .len()
"""

import yaml
from expression import load_fact_info
from algorithm.codegen.python_gen import resolve_op_symbol


# --- expression tree to Rust string ---

def expr_to_rust(kg, node):
    """Convert expression tree node to Rust expression string."""
    if isinstance(node, str):
        return node
    if isinstance(node, (int, float)):
        if isinstance(node, float):
            return f"{node}_f64"
        return str(node)
    if not isinstance(node, dict):
        return str(node)

    op_path = next(iter(node))
    operands = node[op_path]
    symbol = resolve_op_symbol(kg, op_path)
    parts = [expr_to_rust(kg, o) for o in operands]

    if len(parts) == 1:
        if symbol == "len":
            return f"{parts[0]}.len()"
        if symbol == "neg":
            return f"-{parts[0]}"
        return f"{symbol}({parts[0]})"

    return f"({parts[0]} {symbol} {parts[1]})"


# --- indentation helper ---

def indent(lines):
    """Add one level of indentation to each line."""
    return ["    " + line for line in lines]


# --- step generators ---

def condition_to_rust(step_as, ctx):
    """Convert condition_yaml to Rust expression string."""
    condition_yaml = step_as.get("condition_yaml", "")
    if condition_yaml:
        tree = yaml.safe_load(condition_yaml)
        return expr_to_rust(ctx["kg"], tree)
    return "true"


def gen_assign(step_as, ctx):
    var = step_as.get("variable", "")
    frm = step_as.get("from", "")
    declared = ctx.get("declared", set())
    if var in declared:
        return [f"{var} = {frm};"]
    declared.add(var)
    return [f"let mut {var} = {frm};"]


def gen_assign_indexed(step_as, ctx):
    container = step_as.get("container", "")
    index = step_as.get("index", "")
    frm = step_as.get("from", "")
    return [f"{container}[{index}] = {frm};"]


def gen_if(step_as, ctx):
    cond_str = condition_to_rust(step_as, ctx)
    lines = [f"if {cond_str} {{"]
    then_step = step_as.get("then", "")
    if then_step:
        body = generate_chain(then_step, ctx)
        lines.extend(indent(body))
    lines.append("}")
    return lines


def gen_while(step_as, ctx):
    cond_str = condition_to_rust(step_as, ctx)
    lines = [f"while {cond_str} {{"]
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
        range_end = f"{to_length}.len()"
    elif to_var:
        range_end = f"({to_var} as usize + 1)"
    else:
        range_end = "0"

    lines = [f"for {index} in {from_val}..{range_end} {{"]
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
        expr_str = expr_to_rust(ctx["kg"], tree)
    else:
        expr_str = "Default::default()"
    declared = ctx.get("declared", set())
    if result_var in declared:
        return [f"{result_var} = {expr_str};"]
    declared.add(result_var)
    return [f"let mut {result_var} = {expr_str};"]


def gen_evaluate_expression_fact(step_as, ctx):
    result_var = step_as.get("result_variable", "result")
    expr_fact = step_as.get("expression_fact", "")
    return [f"// TODO: evaluate expression fact '{expr_fact}'",
            f"let mut {result_var} = Default::default();"]


def gen_return(step_as, ctx):
    var = step_as.get("variable", "")
    return [f"{var}"]


# --- dispatch table ---

STEP_GENERATORS = {
    "computer/algorithm/assign": gen_assign,
    "computer/algorithm/assign_indexed": gen_assign_indexed,
    "computer/algorithm/if": gen_if,
    "computer/algorithm/while": gen_while,
    "computer/algorithm/indexed/for_each": gen_for_each,
    "computer/algorithm/evaluate_expression": gen_evaluate_expression,
    "computer/algorithm/evaluate_expression_fact": gen_evaluate_expression_fact,
    "computer/algorithm/return": gen_return,
}


# --- chain walking ---

def generate_chain(step_name, ctx):
    """Generate Rust code for a step and follow its 'next' link."""
    steps = ctx["steps"]
    if step_name not in steps:
        return []

    step = steps[step_name]
    step_type = step["type"]
    step_as = step.get("val_as", {}).get(step_type, {})

    generator = STEP_GENERATORS.get(step_type)
    if generator is None:
        return [f"// unknown step type: {step_type}"]

    lines = generator(step_as, ctx)

    next_step = step_as.get("next", "")
    if next_step and next_step in steps:
        lines.extend(generate_chain(next_step, ctx))

    return lines


# --- main entry point ---

def generate_rust(kg, algo_path):
    """Generate a Rust generic function from an algorithm fact."""
    info = load_fact_info(kg, algo_path)
    if info is None:
        raise ValueError(f"Cannot load algorithm: {algo_path}")

    has = info.get("has", {})

    description = has.get("description", {}).get("val", "")
    func_name = algo_path.rsplit("/", 1)[-1]

    # input parameters
    params = []
    for attr, val in has.items():
        if val.get("type") == "list" and "val" not in val:
            params.append(f"{attr}: &mut Vec<T>")

    # collect loop index names
    loop_indices = set()
    for attr, val in has.items():
        if not attr.startswith("step_"):
            continue
        step_type = val.get("type", "")
        if step_type == "computer/algorithm/indexed/for_each":
            step_as = val.get("val_as", {}).get(step_type, {})
            idx = step_as.get("index", "")
            if idx:
                loop_indices.add(idx)

    # collect declared variables, determine type (T vs i64) from description
    INDEX_HINTS = {"index", "bound", "position", "next"}
    variables = []
    var_types = {}
    for attr, val in has.items():
        if val.get("type") != "math/variable" or attr in loop_indices:
            continue
        variables.append(attr)
        desc = val.get("val_as", {}).get("math/variable", {}).get("description", "").lower()
        if any(hint in desc for hint in INDEX_HINTS):
            var_types[attr] = "i64"
        else:
            var_types[attr] = "T"
    declared = set(variables) | loop_indices

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

    ctx = {"kg": kg, "steps": steps, "declared": declared}

    # generate function
    lines = []
    if description:
        lines.append(f"/// {description}")
    lines.append(f"fn {func_name}<T: Copy + PartialOrd + Default + std::ops::Sub<Output=T> + std::ops::Add<Output=T> + From<i32>>({', '.join(params)}) -> T {{")

    # declare variables at function scope with correct types
    for var in variables:
        vtype = var_types.get(var, "T")
        lines.extend(indent([f"let mut {var}: {vtype} = Default::default();"]))

    body = generate_chain(first_step, ctx)
    lines.extend(indent(body))

    lines.append("}")
    return "\n".join(lines) + "\n"
