# Ideas to Think About

## What executable algorithms in KG open up

Having precise, executable algorithms as facts is a huge feature. Here are
the doors it opens.

### Automatic code generation — real, not hallucinated

Algorithm facts have typed inputs, typed operations, explicit control flow,
and tests. Generating Python/Rust/JavaScript is mechanical translation. The
generated code is provably correct because it matches the tested algorithm
fact. Not "LLM generates code from a prompt" — structured, verifiable
translation.

### Algorithm comparison

Store bubble sort, merge sort, quicksort as facts. They all solve the same
problem with different steps. Compare structurally — "merge sort uses
recursion, bubble sort uses nested loops." Compare empirically — run the
same tests, measure performance. Comparison is fact-based, not opinion.

### Algorithm evolution

Version algorithms by creating variants. `find_max_v2` handles empty arrays.
The diff between v1 and v2 is visible in the fact structure — which steps
changed, which constraints were added. Git tracks file changes; our system
tracks knowledge changes.

### Proving theorems about algorithms

With constraints (preconditions, postconditions, loop invariants), a theorem
prover could verify them. "Given precondition 'array is non-empty', does the
algorithm guarantee postcondition 'result is maximum'?" Formal verification
from human-readable YAML.

### Teaching

An algorithm fact with steps + constraints + descriptions + flowchart + tests
+ expression trees is a complete lesson. A student sees the flowchart, reads
the constraints, runs the tests, modifies a parameter, sees what breaks. The
knowledge IS the textbook.

### Algorithm discovery

"Find all algorithms that use `greater_than` operation."
"Find all algorithms that iterate over arrays."
"Which algorithm handles empty arrays?"
Graph queries on the KG — algorithm structure is searchable knowledge.

### Composable computation

An algorithm that calls another algorithm. A physics simulation calls
`evaluate_expression` for `F=ma`, calls numerical integration for position
update, calls `find_max` for collision detection. The entire simulation is
facts — auditable, testable, modifiable without coding.

### Algorithm regression

Given observed input-output pairs, match them against algorithms in the KG.
An agent observes a system producing outputs and runs each algorithm against
those inputs. When outputs match, conclude which algorithm the system
implements.

Enables:
- **Reverse engineering** — observe a black box, identify the algorithm
- **Validation** — "does this system implement the algorithm we think?"
- **Scientific discovery** — observe natural phenomena, match against known
  mathematical models. "This data fits F = ma" is algorithm regression
  against physics equations
- **Paper verification** — a paper claims "we use algorithm X." Run
  algorithm X against the paper's reported data and check if results match.

This is automated hypothesis testing — the KG has the hypotheses as
executable facts, the regression tests them against observed reality.

### The unusual territory

This system sits between a programming language and a knowledge base. It's
not a language — you can't write arbitrary programs. It's not just a
database — it executes. It's a **knowledge machine** — structured knowledge
that does work.

### Related research: LaSR — Symbolic Regression with a Learned Concept Library

NeurIPS 2024 paper (Grayeli, Sehgal, Costilla Reyes, Cranmer, Chaudhuri).
Uses LLMs to discover mathematical formulas from data — symbolic regression
enhanced with learned concept abstractions.

Reference: https://neurips.cc/virtual/2024/poster/96212

Connection to our system:
- **Their output is our input.** LaSR discovers equations like `F = ma`.
  Our system stores them as executable, testable expression trees.
- **Algorithm regression is the reverse.** They: data → find equation.
  Us: observed data → match against known equations in KG.
- **Their "concept library" ≈ our operation taxonomy.** They learn that
  "multiplication of two variables" is reusable. We have
  `math/algebra/operation/multiply` as a fact.
- **Combined workflow:** LaSR discovers formula from data → our system
  stores it as a fact with expression tree + tests + constraints + LaTeX →
  future LaSR runs benefit from stored knowledge.

Validates direction: research community is moving toward structured symbolic
knowledge + LLM reasoning. We're building the knowledge infrastructure.

### Next design step

Layer declarative descriptions and constraints onto algorithm facts:
- Preconditions and postconditions on algorithms
- Constraints on variables (invariants)
- Natural language descriptions on steps

Same fact = procedural (steps) + declarative (constraints) + descriptive
(natural language). Multiple valid representations of the same knowledge.

**Status (May 11, 2026):** Implemented on find_max algorithm. Precondition,
postcondition, loop invariant, and step descriptions added alongside
procedural steps. All tests still pass.

## Knowledge quality metrics

### Existing research

**Zaveri et al. (2016) — "Quality Assessment for Linked Data"**
Canonical framework with 18 quality dimensions:
- **Property completeness** — does each fact have all properties its type declares?
- **Schema completeness** — are all class properties present?
- **Semantic accuracy** — correct real-world mapping
- **Consistency** — adherence to structural definitions

**OQuaRE — Ontology Quality Metrics (Duque-Ramos et al., 2011)**
Structural metrics adapted from software engineering:
- **ANOnto** — annotation richness (annotations per class)
- **DITOnto** — depth of inheritance tree
- **AROnto** — attribute richness (restrictions per class)
- **NOMOnto** — number of methods (properties per class)

**SHACL constraint satisfaction rate** — fraction of entities passing declared
shape constraints. Measures how well data conforms to its own rules.

**Depth vs breadth proxies** — breadth = number of distinct types/paths.
Depth = average properties per fact. Density = edges/nodes ratio.

**Information-theoretic** — description entropy (Shannon entropy over property
distributions per class). Low entropy = uniform descriptions. Anomalies
indicate errors. (Paulheim & Bizer, 2014)

### Gap: no metric for multi-representation quality

No established standard for measuring quality across declarative + procedural
+ constraint representations simultaneously. This is novel territory.

### Possible metric for our system

Property completeness as base, with richness bonuses:

```
Quality(fact) = (properties filled / properties declared by type)
             × (1 + has_description × 0.2)
             × (1 + has_constraints × 0.3)
             × (1 + has_tests × 0.3)
             × (1 + multiple_representations × 0.2)
```

The checker could report quality scores alongside pass/fail. Example output:
"325 facts: avg quality 0.4, 200 at base level, 50 with descriptions,
10 with constraints, 7 tested."

More objective alternative: **number of answerable questions** — how many
distinct questions can be answered using this fact? A fact with only `is`
answers "does X exist?" A fact with tests answers "what does X return for
input Y?" A fact with constraints answers "is X correct for all inputs?"

### Key insight

Knowledge quality is not about counting layers we added. It's about
measuring the actual information content and verifiability of the fact.
Property completeness (Zaveri) is the most directly applicable existing
metric. Constraint satisfaction rate (SHACL-inspired) captures our unique
multi-layer approach.

## EARS (Easy Approach to Requirements Syntax)

Structured natural language templates for requirements: ubiquitous, event-driven,
state-driven, unwanted behavior, optional. Each template has trigger/condition +
subject + action.

Current assessment: not directly useful yet. Our facts are already more precise
than EARS templates. But the condition/trigger concept is missing from our tags —
we describe what things *are* and *have*, not *when* or *under what conditions*.

The `function` concept (inputs → outputs) may be a more natural way to express
behavior than borrowing EARS patterns. A condition is just another input.

Revisit when we start expressing behavioral requirements as facts.

Reference: https://alistairmavin.com/ears/

## JSON output for check and verify tools

Add `--output-json` flag to `check.py` and `verify.py` so that LLM agents and
scripts can consume structured output instead of parsing human-readable text.

Current assessment: not needed yet. Claude handles the text output fine.
Revisit when we build automation that chains tool outputs or when the output
gets complex enough that text parsing becomes unreliable.

## Rust verifier — multi-language fact-driven development

Rust has proc macros and custom attributes that mirror Python's `@fact` decorator:

```rust
#[fact("app/org/igorlesik/fact/pysrc/kg_module")]
struct Kg { ... }
```

The `syn` crate can parse Rust AST to find `#[fact(...)]`, struct fields,
method signatures, and trait implementations. Same verification logic,
different language frontend.

Key difference from Python: Rust uses traits (interfaces) not inheritance,
so we'd need `implements_trait` instead of `parent_class` — reinforcing
that fact vocabulary should be language-specific (`computer/sw/lang/rust/`).

This is potentially the real value of the project: write facts once as
language-agnostic specifications, verify against any language with AST tooling.

Revisit after the Python verifier is mature and the `src/` Rust code is revived.

## YAML block scalars as embedded structured data

YAML `|` block scalars can contain YAML-formatted content as plain text:

```yaml
- has:
    config_template: |
      - host: localhost
        port: 8080
        options:
          timeout: 30
          retries: 3
```

The content is a string to the fact system but parseable on demand. This creates
a middle tier in the epistemology:

1. **Strong tags** (`is`, `has`) — fully structured, verified by checker
2. **`|` block with structured content** — carried but opaque to the checker,
   parseable by programs or LLM agents when needed
3. **LLM-inferred** — not in the fact at all

This avoids extending the type system beyond `str`, `num`, `list` while
allowing arbitrarily complex data structures inside facts. Could be used for
examples, templates, complex configurations, or data that doesn't fit the
current tag model.

## Web UI design decisions

Stack: FastAPI + Jinja2 + HTMX + vis.js + classless CSS (Pico or Simple.css).

- **HTMX** for navigation and dynamic content — server renders HTML, minimal JS
- **vis.js** for interactive graph visualization — self-contained, no framework needed
- **Classless CSS** for styling — write semantic HTML, looks professional automatically
- **No build tools** — no npm, no webpack, just `<script>` tags
- **Zero lock-in** — each piece is replaceable independently

Design principles: minimal, professionally elegant, fast. Good typography and
spacing matter more than animations or effects. The graph visualization is the
key interactive element.

Dual output: HTML for humans, JSON for bots/agents. Same endpoints, content
negotiation via Accept header.

### Deployment options

For running the web service publicly:

1. **Railway / Render / Fly.io** — push git, auto-deploys. Free tier. Easiest.
2. **DigitalOcean App Platform** — similar, ~$5/month.
3. **Small VPS** (DigitalOcean, Linode, Hetzner) — $4-6/month, more control.
4. **AWS** — overkill for this size. Only if already in AWS ecosystem.

Recommended starting point: Render or Railway. Need a `requirements.txt` with:
fastapi, uvicorn, pyyaml, jsonschema, rich, jinja2.

### Roots as separate repos

Each fact root will eventually be its own git repo. The server needs a config
file listing roots and their sources:

```yaml
# fact-server.yaml
roots:
  - path: kg
    repo: https://github.com/igorlesik/fact-kg
  - path: kg2
    repo: https://github.com/igorlesik/fact-kg2
```

For local dev: paths point to local directories.
For deployment: server clones repos on startup.

Design the server with this in mind from the start — roots should be
configurable, not hardcoded. Implement when refactoring to Jinja2 templates.

## Rationale as knowledge — reasoning patterns in KGs

### The idea

Most KGs store conclusions. Ours can store the reasoning that led to
conclusions — via `knowledge/rationale`. Example: Euler's 1770 intuitive
argument for why positive × negative = negative, alongside the modern
formal derivation from the distributive property.

With enough rationales, an AI could learn reasoning *patterns* — not just
facts, but how to think. The same pattern ("reducing input reduces output")
appears in algebra, thermodynamics, economics. Recognizing and transferring
these patterns is analogical reasoning.

### Existing systems (from research)

**OMDoc** (Kohlhase) — structured math with explicit proof steps and WHY.
XML-based with object/statement/theory layers. Closest to our approach.
Failed because authoring overhead was too high for working mathematicians.

**NEOMYCIN** (Clancey, 1987) — separated diagnostic strategy (HOW to
think) from domain knowledge (WHAT to know). Explicitly represented
meta-reasoning. Genuine rationale ontology. Didn't scale — hand-authored.

**Walton's Argumentation Schemes** — ~60 reusable reasoning patterns:
"argument from analogy," "argument from expert opinion," "argument from
cause to effect." Implemented in tools (Araucaria, OVA). The **AIF**
(Argument Interchange Format) standardized the graph schema. **AIFdb**
corpus has thousands of annotated arguments. Limitation: manual annotation.

**SME (Structure Mapping Engine)** (Gentner & Forbus, Northwestern) —
transfers reasoning between domains by matching relational structure.
Still active. Taught to solve AP physics by analogy to worked examples.

**ThoughtSource** (2023, Nature Scientific Data) — aggregated chain-of-
thought reasoning datasets for LLM training. Structured reasoning traces
with step labels.

**Mizar Mathematical Library** — 60,000 theorems with readable formal
proofs. Enabled automated premise selection (learning which lemmas help).
Genuine discovery from rationale structure.

### The capture problem

**Every rationale system failed because recording rationale costs more
than it benefits the recorder.** Systems that succeeded (Mizar, MYCIN)
had rationale as a byproduct of the primary task, not an add-on.

**For our system:** Rationale should emerge naturally. When we write
algorithm steps + descriptions + constraints, the rationale is partially
there. When we capture Euler's argument, it's because we're reading Euler,
not because a system demands it. YAML-in-YAML is low friction — add
what's useful, skip what's not.

### Possible direction: reasoning scheme types

Walton's argumentation schemes as fact types:

```
knowledge/reasoning/scheme.yaml                    — base type
knowledge/reasoning/scheme/argument_from_analogy.yaml
knowledge/reasoning/scheme/monotonic_argument.yaml
knowledge/reasoning/scheme/proof_by_contradiction.yaml
knowledge/reasoning/scheme/reduction_to_known.yaml
```

Then rationales reference which scheme they use. The sign rule's Euler
argument uses "monotonic_argument" scheme. This makes reasoning patterns
searchable: "find all rationales that use argument from analogy."

This is the bridge between storing rationales (easy, low friction) and
enabling analogical reasoning at scale (hard, research-level). The
schemes are the indexing layer that makes rationales machine-searchable.
