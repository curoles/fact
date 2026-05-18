import sys
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))

from expression import load_fact_info
from diagram import FlowLayout, to_json
from algorithm.codegen.python_gen import generate_python
from algorithm.codegen.cpp_gen import generate_cpp
from algorithm.codegen.rust_gen import generate_rust

router = APIRouter(prefix="/apps/computer/algorithm_viewer")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

CONSTRAINT_TYPES = {
    "computer/algorithm/precondition",
    "computer/algorithm/postcondition",
    "computer/algorithm/invariant",
}


def extract_algorithm(info):
    has = info.get("has", {})
    description = ""
    desc_info = has.get("description", {})
    if desc_info:
        description = desc_info.get("val", "")

    steps = {}
    constraints = {}
    variables = {}
    for attr, val in has.items():
        if attr.startswith("step_"):
            steps[attr] = val
        elif val.get("type") in CONSTRAINT_TYPES:
            constraint_as = val.get("val_as", {}).get(val["type"], {})
            constraints[attr] = {
                "kind": val["type"].rsplit("/", 1)[-1],
                "condition": constraint_as.get("condition", ""),
            }
        elif val.get("type") in ("math/variable", "list"):
            var_as = val.get("val_as", {}).get(val["type"], {})
            variables[attr] = {
                "type": val["type"],
                "description": var_as.get("description", ""),
            }

    first_step = None
    for name in ["step_init", "step_start", "step_evaluate"]:
        if name in steps:
            first_step = name
            break
    if first_step is None and steps:
        first_step = next(iter(steps))

    return description, steps, first_step, constraints, variables


@router.get("/")
def algorithm_viewer(request: Request):
    from pysrc.web.server import kg, ROOTS

    fact_path = request.query_params.get("fact", "")
    view = request.query_params.get("view", "flowchart")

    info = None
    description = ""
    steps = {}
    constraints = {}
    variables = {}
    diagram_data = None
    generated_code = ""
    error = ""

    if fact_path:
        info = load_fact_info(kg, fact_path)
        if info is None:
            error = f"Fact not found: {fact_path}"
        else:
            types = info.get("type", [])
            if "computer/algorithm" not in types:
                error = f"Not an algorithm: {fact_path}"
            else:
                description, steps, first_step, constraints, variables = extract_algorithm(info)
                if not steps:
                    error = f"No steps found in: {fact_path}"
                if first_step and view == "flowchart":
                    layout = FlowLayout()
                    diagram = layout.layout(steps, first_step)
                    diagram_data = to_json(diagram)
                elif view == "python":
                    try:
                        generated_code = generate_python(kg, fact_path)
                    except Exception as e:
                        error = f"Code generation error: {e}"
                elif view == "cpp":
                    try:
                        generated_code = generate_cpp(kg, fact_path)
                    except Exception as e:
                        error = f"Code generation error: {e}"
                elif view == "rust":
                    try:
                        generated_code = generate_rust(kg, fact_path)
                    except Exception as e:
                        error = f"Code generation error: {e}"

    if "application/json" in request.headers.get("accept", ""):
        return JSONResponse({
            "fact": fact_path,
            "description": description,
            "diagram": diagram_data,
            "error": error,
        })

    return templates.TemplateResponse(request, "algorithm_viewer.html", {
        "fact_path": fact_path,
        "view": view,
        "description": description,
        "steps": steps,
        "constraints": constraints,
        "variables": variables,
        "diagram_data": diagram_data,
        "generated_code": generated_code,
        "error": error,
    })
