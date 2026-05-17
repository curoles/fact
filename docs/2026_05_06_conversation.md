# Session Notes — May 6, 2026

## Work Done

### 1. Newton's Second Law as a physics equation

Created `physics/classical/mechanics/dynamics/law/newton_second.yaml` — the first
physics law expressed as both a `physics/equation` and a `math/expression`.

**Taxonomy decision:** `physics/classical/mechanics/dynamics/law/` — separating
dynamics from statics and kinematics. Getting taxonomy right upfront prevents
chaos when multiple contributors add facts.

**Physics equation concept:** Created `physics/equation.yaml` with `lhs` and `rhs`
(both type `list`). For Newton's second law:
- `lhs: [force]` — the quantity being defined
- `rhs: [mass, acceleration]` — the defining quantities

The names (`force`, `mass`, `acceleration`) are shared between the physics
equation (`lhs`/`rhs`) and the math expression (`expression_yaml`). A checker
can verify they match.

### 2. GitHub organization

Created `fact-kg` org on GitHub (`github.com/fact-kg`). Transferred all repos:
`fact`, `fact_physics`, `fact_math`, `fact_computer`.

Created `facts` repo as top-level container with git submodules:
```
facts/
  fact/           ← submodule: app code, kg, kg2
  fact_physics/   ← submodule
  fact_math/      ← submodule
  fact_computer/  ← submodule
```

Working directory moved from `prj/fact/fact` to `prj/fact/facts/fact`.

### 3. Deployed to Render fact-kg.onrender.com

https://fact-kg.onrender.com
https://fact-kg.onrender.com/fact/physics/atom/element/chromium

Deployed the web app to Render (free tier). Files added to `facts/` repo:

- `requirements.txt` — Python dependencies
- `render.yaml` — Render service config

Start command: `cd fact && uvicorn pysrc.web.server:app --host 0.0.0.0 --port $PORT`

Submodules work correctly — Render pulls them for public repos. Paths resolve
because `fact-server.yaml` uses `../fact_physics` etc., and submodules are siblings.

**Free tier behavior:** First requests after inactivity are slow (cold start ~30s).
Once facts are cached in memory, responses are fast. Single worker can get
overwhelmed with concurrent requests during initial loading.

---

## Design Decisions

### Physics equation structure

**Decision:** `physics/equation` has `lhs` (left-hand side) and `rhs` (right-hand
side), both type `list`. The equation declares physical participants as `has`
entries typed with MKS dimensions. `lhs`/`rhs` reference these participant names.

**Rationale:** Separates physics meaning (which quantities participate, what's input
vs output) from math computation (the expression tree). The same names bridge both
layers. `lhs`/`rhs` also enables future equation rearrangement — `F = ma` can become
`a = F/m` by swapping lhs/rhs and changing the expression tree.

### Taxonomy for physics laws

**Decision:** `physics/classical/mechanics/dynamics/law/` rather than flat
`physics/law/`.

**Rationale:** Anticipates growth. An authority should create proper structure
upfront rather than letting contributors scatter files. The hierarchy reflects
how physics is actually organized: classical vs quantum, mechanics vs thermodynamics,
dynamics vs statics.

### Deployment architecture

**Decision:** `facts` repo as a container with submodules, deployed to Render.
No code changes needed for deployment — existing `fact-server.yaml` paths work
because submodules are siblings.

**Alternatives considered:** Railway (less generous free tier), Fly.io (needs
Dockerfile). Render chosen for simplicity and truly free tier.

---

## Observations

### Using open source data

Wikidata/Wikipedia data (values, properties, URLs) can be imported automatically.
But the ontology — taxonomy, expression structure, type relationships — requires
human judgment and is the competitive advantage.

### Agent-assisted KG growth

A realistic future workflow:
1. Human builds ontology skeleton (taxonomy, types, expression patterns)
2. LLM agent crawls sources, generates YAML facts matching the patterns
3. Checker verifies every generated fact
4. Human reviews and approves

The skeleton built over these sessions is already enough to demonstrate this.

---

## Session continued — May 6, 2026

### Work Done

#### Multiple expressions per fact

Refactored all expression facts to use `as` pattern on `math/expression` type.
Before: `expression_str` and `expression_yaml` as separate top-level `has` entries.
After: wrapped in a named `has` entry typed `math/expression` with `as`:

```yaml
- has:
    expression_geometric:
      type: math/expression
      as:
        - math/expression:
            expression_str:
              value: "sin(x) = opposite / hypotenuse"
            expression_yaml:
              value: |
                math/algebra/operation/divide:
                  - opposite
                  - hypotenuse
```

Updated ~10 fact files (quadratic, linear, cubic, n_degree, root_plus, root_minus,
linear/root, pi, e, newton_second) and the evaluator/LaTeX renderer in routes.py.

#### Mathematical constants — e and pi

Created `math/analysis/constant/e.yaml` — dual identity as `math/constant`
(value 2.718281828459045) and `math/expression` (limit definition). Introduced
`math/analysis/real/calculus/expression/limit.yaml` concept.

Created `math/analysis/constant/pi.yaml` — dual identity with geometric expression
(circumference / diameter). Created supporting geometry facts:
`math/geometry/euclidean/shape/circle.yaml` with `circle/circumference.yaml` and
`circle/diameter.yaml`.

#### sin(x) with five expressions

Created `math/analysis/real/function/trigonometric/sin.yaml` with `python_impl`
and five expression representations:
1. Geometric — opposite / hypotenuse (working)
2. Taylor series — FIXME: needs factorial
3. Euler's formula — FIXME: needs complex numbers, exp
4. Unit circle — FIXME: needs geometry concepts
5. Differential equation — FIXME: needs ODE concept

Each FIXME marks a gap in the expression system — a roadmap.

#### Newton's second law — two expressions

Added differential form `F(t) = m * d²x/dt²` alongside algebraic `F = ma`.
FIXME for derivative operation.

### Design Decisions

#### Multiple expressions use `as` pattern

**Decision:** Each expression is a `has` entry typed `math/expression`, with
`expression_str` and `expression_yaml` set via `as`. Multiple expressions per
fact get descriptive names (`expression_geometric`, `expression_taylor`, etc.).

**Rationale:** Reality has multiple simultaneously correct descriptions. A KG
should capture all of them, not force one canonical form. The `as` pattern
is consistent with how other typed properties work.

#### Constants are both value and expression

**Decision:** `e` and `pi` have `is: math/constant` (with numeric value via `as`)
AND `is: math/expression` (with defining formula). Dual identity.

**Rationale:** A constant's value is a fact. How it's defined is also a fact.
Both matter — the value for computation, the definition for understanding.

#### Function vs expression distinction

**Decision:** Expressions with no free variables → constants (e, pi).
Expressions with free variables → functions (sin, quadratic).
Both use `math/expression` for their expression trees.

#### Geometry taxonomy

**Decision:** `math/geometry/euclidean/shape/circle/` with properties
(circumference, diameter) nested under the shape, not abstracted as general
properties.

**Rationale:** Circumference is circle-specific. No practical value in
abstracting it away from the shape it belongs to.

---

## Session — May 11, 2026

### Work Done

#### Expression module extracted

Moved expression evaluator, LaTeX renderer, and helpers from the polynomial
plot app into a shared library at `pysrc/expression/`:
- `evaluator.py` — `ExpressionEvaluator` class with operation resolution
- `latex.py` — `ExpressionLatex` class with LaTeX rendering
- `helpers.py` — `load_fact_info`, `extract_expression`, `extract_all_expressions`

Both the polynomial plot and expression diagram apps now use the shared module.

#### Algorithm system

Created algorithm step types as facts:
- `computer/algorithm.yaml` — base type
- `computer/algorithm/step.yaml` — base step with `next`
- `computer/algorithm/assign.yaml` — set variable
- `computer/algorithm/if.yaml` — conditional branch
- `computer/algorithm/indexed/for_each.yaml` — iteration
- `computer/algorithm/return.yaml` — produce output
- `computer/algorithm/evaluate_expression.yaml` — evaluate a math expression

Created `computer/algorithm/array/find_max.yaml` — first algorithm, uses 4 step
types with reusable, parameterized steps. Variables passed by name, comparison
operation pluggable via `python_impl`.

Created `computer/algorithm/evaluate_expression_and_return.yaml` — generic
two-step algorithm that evaluates any expression fact and returns the result.

#### Algorithm executor

`pysrc/algo_executor.py` — `AlgorithmExecutor` class that reads algorithm
steps from fact `has`/`as` structure, walks the `next` chain, dispatches to
step executors by type. Uses the shared expression evaluator for
`evaluate_expression` steps and comparison operations.

#### Test framework

Created `computer/test/case.yaml` — test case type with `description`,
`subject`, `expected_result`.

Created `pysrc/test/runner.py` — discovers test facts by scanning for
`/test/` in paths, loads subject (algorithm), executes with test inputs,
compares result to expected. Supports both algorithm tests and expression
tests (via `evaluate_expression_and_return` algorithm).

Test cases created:
- `computer/algorithm/array/find_max/test/` — 4 tests (basic, single
  element, negative numbers, duplicates)
- `math/algebra/real/singlevar/polynomial/quadratic/test/` — 3 tests
  (basic, zeros, negative coefficients)

All 7 tests pass.

#### Algorithm viewer app

Created `/apps/computer/algorithm_viewer/` — search for algorithm facts,
visualize as flowchart with D3.

FlowLayout in `pysrc/diagram/flow_layout.py` — positions steps in
columns (main flow left, branches right), different shapes per step type:
- Rectangle (blue) — assign, evaluate
- Diamond (orange) — if condition
- Hexagon (purple) — for_each loop
- Rounded rectangle (green) — return

Loop-back edges rendered as dashed polylines routed around body steps.

#### Diagram library improvements

Separated `FlowLayout` into its own file `pysrc/diagram/flow_layout.py`.
Studied pyflowchart library — it does zero layout (delegates to flowchart.js).
Useful patterns: `NodesGroup` for composable subgraphs, `TransparentNode`
for edge routing. For professional layout, Sugiyama/layered algorithm is
the standard — future improvement.

### Design Decisions

#### Algorithms are the testable unit

**Decision:** Expressions are tested by wrapping them in the
`evaluate_expression_and_return` algorithm. The test runner only executes
algorithms. Every testable computation is an algorithm.

**Rationale:** An algorithm takes inputs and returns an output — naturally
testable. Evaluating an expression is just a two-step algorithm (evaluate →
return). This unified the test framework: one runner, one test case format.

#### Step types are reusable

**Decision:** Algorithm steps (`assign`, `if`, `for_each`, `return`) are
generic fact types. Each algorithm assembles them with specific parameters
via `as`. Steps receive variable names, not hardcoded values.

**Rationale:** `find_min` reuses the same steps as `find_max` with a
different comparison operation. The steps don't know what algorithm they're
in — they're pluggable components.

#### Fact-code boundary for algorithms

**Decision:** Facts describe algorithm structure (steps, connections, variable
names, operation references). Code provides step semantics (what "assign" does).
The dispatch table in `algo_executor.py` is the irreducible code layer.

**Rationale:** Same pattern as expression operations — `python_impl` resolves
to a symbol, the symbol maps to a function. Facts say "what," code says "how."

#### pyflowchart study

pyflowchart generates text for flowchart.js, does no layout computation.
For our use case (full control, D3 rendering), the useful takeaways are:
- `NodesGroup` for composable subgraphs
- `TransparentNode` for edge routing
- Sugiyama algorithm for professional layered layout

### What's Still Rough

- FlowLayout has magic numbers and simple column/row positioning
- Algorithm executor has hardcoded bracket parsing for array access
  (should use expression evaluator)
- No interactive algorithm execution app (only flowchart viewing)

---

## Session — May 14, 2026

### Work Done

#### Declarative and constraint layers on algorithms

Added to find_max and bubble_sort:
- `precondition` — input constraints (e.g., "len(array) > 0")
- `postcondition` — output guarantees (e.g., "result >= all elements")
- `loop_invariant` — what's true each iteration
- `description` on every step — natural language intent
- `description` on variables — what each variable represents

Created fact types: `computer/algorithm/precondition.yaml`,
`postcondition.yaml`, `invariant.yaml`. Updated `math/variable.yaml` and
`computer/algorithm/step.yaml` with description property.

#### Bubble sort algorithm

Created `computer/algorithm/array/bubble_sort.yaml` — proper version with
inner bound `len(array) - i - 2`. Features:
- Nested for_each loops (outer and inner)
- Inline expression evaluation for computed values (j+1, inner bound)
- Indexed assignment (`assign_indexed`) for array element writes
- All variables declared (i, j, inner_bound, j_next, temp)
- 4 test cases, all passing

#### New step types and facts

- `computer/algorithm/assign_indexed.yaml` — write to array at index
- `computer/algorithm/evaluate_expression_fact.yaml` — evaluate external
  expression fact (separated from inline evaluation)
- `computer/algorithm/evaluate_expression.yaml` — updated for inline
  expression_yaml
- `math/algebra/operation/length.yaml` + Python `len` binding
- `computer/algorithm/rationale.yaml` — design rationale type

#### Algorithm executor updates

- `_exec_assign_indexed` — indexed container assignment
- `_exec_evaluate_expression_inline` — parse and evaluate inline YAML
- `_exec_evaluate_expression_fact` — load and evaluate external fact
- `for_each` now supports `to` (variable reference) alongside `to_length`
- FlowLayout updated with new step shapes and labels

#### Algorithm viewer — text view

Added view toggle (Flowchart / Text) to the algorithm viewer app. Text view
shows constraints table, variables table, and expandable step details with
all properties and descriptions.

#### Design rationale on algorithms

Added structured rationale to find_max and bubble_sort using YAML-in-YAML:

```yaml
rationale_yaml:
  understanding:
    problem: "sort elements in ascending order"
    constraints: ["can compare", "can swap"]
  planning:
    observation: "comparing adjacent and swapping is simplest"
    insight: "one pass bubbles largest to end"
    question: "does one pass suffice?"
    conclusion: "no, repeat n times"
  alternatives:
    - name: "merge sort"
      tradeoff: "O(n log n) but needs extra memory"
```

Research confirmed this is novel — no existing framework combines reasoning
chains with machine-readable format. DRL, QOC, and Polya's framework are
closest but none are structured data.

### Design Decisions

#### assign vs assign_indexed — separate types

**Decision:** `assign_indexed` is a separate step type, not `assign` with
optional `index`. Cannot reliably check "is optional field set" in `as` syntax.

#### evaluate_expression vs evaluate_expression_fact

**Decision:** Two types. Inline expressions use `expression_yaml` (YAML-in-YAML
on the step). External expressions use `expression_fact` (path to a fact).
No ambiguity about which is which.

#### All variables must be declared

**Decision:** Every variable an algorithm uses (loop indices, temporaries,
bounds) must be declared as a `has` entry with description. Like Fortran.

**Rationale:** Undeclared variables work in the executor but are invisible
as knowledge. Declaration adds documentation, enables verification, and
makes the algorithm self-describing.

#### Five layers of algorithm knowledge

An algorithm fact now supports five simultaneous layers:
1. **Procedural** — steps with next links
2. **Declarative** — descriptions on steps and variables
3. **Constraints** — pre/postconditions, loop invariants
4. **Computational** — inline expressions, operation references
5. **Epistemic** — design rationale (understanding, planning, alternatives)

### Research Notes

#### Knowledge quality metrics

Zaveri et al. (2016) framework, OQuaRE ontology metrics, SHACL constraint
satisfaction rate. No standard for multi-representation quality — open gap.

#### Algorithm design rationale frameworks

DRL (Decision Representation Language), QOC (Questions Options Criteria),
Polya's How to Solve It, Dijkstra's Calculational Method. None combine
reasoning chains with machine-readable format. Our YAML rationale structure
(understanding → planning → alternatives) appears novel.

### Observations

#### LLM reasoning with multiple layers

With all five layers, LLM reasoning about algorithms is qualitatively
different: steps for execution, descriptions for intent, constraints for
correctness verification, rationale for analogical reasoning across domains.
Each layer serves a different cognitive function.

#### Writing algorithms as facts is laborious but valuable

Bubble sort: 5 lines in Python, ~120 lines in YAML. But the YAML version
is executable, testable, visualizable, has constraints, rationale, and
descriptions. The Python version is dead code — it does one thing in one
language with no explanation.

---

## Session — May 16, 2026

### Work Done

#### Code generation from algorithm facts

Created `pysrc/algorithm/codegen/` with two generators:

**`python_gen.py`** — generates Python functions from algorithm facts.
Functional design: dispatch table mapping step types to generator functions,
chain walker following `next` links, expression-to-Python converter resolving
operations through `python_impl` facts. Generated code looks human-written.

**`cpp_gen.py`** — generates C++ template functions. Reuses `resolve_op_symbol`
from `python_gen`. Handles C++-specific syntax: `auto` declarations (tracks
first-use vs reassignment), C-style for loops, `.size()` instead of `len()`,
curly braces, `template<typename T>`.

Both generators produce clean, idiomatic code. Generated Python passes the
same test facts that verify the YAML algorithm directly.

Algorithm viewer app updated with three main tabs: Flowchart, Text, Code.
Code tab has language subtabs (Python, C++).

#### Flowchart fix for nested loops

`_place_body_chain` now follows `next` links within the body, enabling
nested loops (bubble sort's inner loop inside outer loop) to render fully
in the flowchart.

#### Rule engine and query system

Created `pysrc/rule/` with three modules:

**`pattern.py`** — parses rule patterns into structured conditions. Syntax:
`?X part ?Y`, `?X is ?Y`, `?X has ?prop`, `?X has ?prop ?val`. Variables
start with `?`. `AND` joins conditions.

**`matcher.py`** — matches conditions against the KG with variable binding
and unification. Each condition takes current bindings, returns extended
bindings. AND is sequential filtering. Dispatch table for condition types.
`MAX_BINDING_VARS = 20` safety limit.

**`engine.py`** — `RuleEngine` class loads all `knowledge/rule` facts at
init, parses their `when`/`then` patterns. Provides `query()` for pattern
matching with rule inference, and `find_transitive()` for following chains.
Handles primitives (`str`, `num`, `list`) as terminal types.

#### Rule facts

Created `kg/knowledge/rule.yaml` — base type with `when` and `then`
properties.

Created `kg/knowledge/rule/transitive_part.yaml` — first rule:
`?X part ?Y AND ?Y part ?Z => ?X part ?Z`. Derives that luna is part of
the universe through the chain luna → earth → solar_system → milky_way →
universe.

#### Query tool

**`pysrc/rule/query.py`** — interactive and single-shot query tool.
Commands: pattern queries, `find` (substring search), `transitive`,
`rules`, `help`. `query.bat` with absolute paths for running from any
location.

#### Query API endpoint

Added `/query` endpoint to the FastAPI web server. Same capabilities as
the CLI tool but via HTTP/JSON. No startup cost — uses the already-loaded
KG and rule engine.

LLM agents (including Claude) can query the live KG via:
`https://fact-kg.onrender.com/query?q=find+bubble`

Successfully tested: an LLM grounding itself against a verified knowledge
graph via a live REST API, using facts instead of training data.

### Design Decisions

#### Code generation — functional style

**Decision:** Pure functions with dispatch table, not a class with methods.
Each step type has a generator function. `ctx` dict carries state.

**Rationale:** Easier to extend (one function + one table entry per step
type), easier to read, no hidden state. C++ generator reuses Python
generator's `resolve_op_symbol` directly.

#### Rules live in domain paths

**Decision:** Rules are mixed with domain facts, not in a separate
`knowledge/rule/` hierarchy. The base type is at `kg/knowledge/rule.yaml`
but individual rules live near the domain they reason about.

**Rationale:** Rules about elements should live near elements. Rules about
algorithms near algorithms. The `is: type: knowledge/rule` tag identifies
them regardless of location.

#### Pattern language mirrors KG tags

**Decision:** Three pattern types (`is`, `part`, `has`) matching three tags.
No extra abstractions.

**Rationale:** The query language should be as simple as the knowledge
representation. If the KG has three tags, the query language needs three
patterns.

#### Type chains terminate at primitives

**Decision:** `str`, `num`, `list` are terminal types. `find_transitive`
stops at them without error.

**Rationale:** Every concept eventually reduces to a word (str). This is
both practical (no infinite chains) and philosophically honest (at the
bottom, every concept is a name).

#### Query API on existing web server

**Decision:** `/query` endpoint on FastAPI, not a separate daemon or gRPC
service.

**Rationale:** The web server already has the KG loaded. Adding an endpoint
is 30 lines. No new process, no new protocol, no new deployment. LLM
agents can use WebFetch to query it.

### Observations

#### LLM grounded by KG via live API

Successfully demonstrated: Claude querying the Fact KG at
`fact-kg.onrender.com/query` to get verified facts instead of relying on
training data. This is the "infrastructure for AI that reasons" promise
working in practice.

#### The system keeps emerging naturally

Query tool → rule engine → API endpoint. Each piece emerged from need:
rules needed queries, queries needed an API for LLM access. The `is`/`has`/
`part` foundation held through code generation, rule inference, and live
API querying without any changes to the core.

---

## Chemistry domain and quantum mechanics connection

### Chemistry ontology (from research)

Molecule and substance are distinct concepts (per ChEBI ontology):

- **Molecule** — abstract chemical entity: formula, molecular mass, bond types,
  geometry. E.g., H₂O is a molecule.
- **Substance** — bulk material: boiling point, density, melting point. E.g.,
  water is a substance composed of H₂O molecules.
- **Compound** — a substance composed of two or more different elements.
  H₂O is a compound. O₂ is a substance but not a compound.
- **States of matter** — ice, liquid water, steam are the SAME substance in
  different phases. Phase is a property of the substance, not a separate fact.

Proposed KG structure:
```
chemistry/molecule.yaml              — type: formula, molecular_mass, geometry
chemistry/molecule/h2o.yaml          — the molecule
chemistry/substance.yaml             — type: melting_point, boiling_point, density
chemistry/substance/water.yaml       — composed_of: chemistry/molecule/h2o
chemistry/compound.yaml              — subtype of substance
chemistry/classification/organic.yaml
chemistry/classification/inorganic.yaml
```

Property assignment rule: if the property requires temperature/pressure
conditions, it belongs to the substance. Molecule-level: formula, mass,
bonds. Substance-level: melting/boiling point, density, color.

### Chemistry drives quantum mechanics facts

Chemistry IS applied quantum mechanics. Adding molecule facts naturally
pulls in physics laws:

**Physics laws needed by chemistry:**
- **Coulomb's law** — `F = kq₁q₂/r²` — electrostatic force, fundamental
  to bonding
- **Schrödinger equation** — foundational quantum mechanics
- **Pauli exclusion principle** — explains electron configurations (we
  already have subshell facts!)
- **Bond energy expressions** — energy of molecular bonds

**The connection chain:**
`physics/quantum/` → explains → `chemistry/molecule/` → composes →
`chemistry/substance/`

We already have electron configurations and subshell quantum numbers for
all 118 elements. Adding `physics/quantum/` laws would connect this existing
data to chemistry bonding theory.

### App idea: Molecular Bond Viewer

Select two elements → show their electron configurations → predict bond
type and geometry based on quantum mechanics facts → display the molecule.

The physics laws compute (expression evaluator), the chemistry facts
display (web app). Cross-domain knowledge in action.

This would drive both chemistry facts AND physics law facts simultaneously,
solving the "what app drives physics laws?" question.
