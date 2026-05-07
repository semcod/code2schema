# code2schema

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Dependencies](#dependencies)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `code2schema`
- **version**: `0.1.2`
- **python_requires**: `>=3.10`
- **license**: {'text': 'Apache-2.0'}
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(1), app.doql.less, goal.yaml, .env.example, src(1 mod), project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: code2schema;
  version: 0.1.2;
}

dependencies {
  runtime: "libcst>=1.1.0, networkx>=3.2, pydantic>=2.5";
  dev: "pytest>=8, pytest-cov, black, ruff, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60";
}

entity[name="FunctionIR"] {
  name: string!;
  module: string!;
  calls: List[str]!;
  role: CQRSRole!;
  side_effects: List[SideEffect]!;
  fan_out: int!;
  lines: int!;
  is_async: bool!;
  docstring: string;
}

entity[name="ModuleIR"] {
  name: string!;
  path: string!;
  functions: List[FunctionIR]!;
  imports: List[str]!;
  lines: int!;
}

entity[name="WorkflowStep"] {
  callee: string!;
  is_async: bool!;
}

entity[name="WorkflowIR"] {
  name: string!;
  entry: string!;
  steps: List[WorkflowStep]!;
}

entity[name="RuleIR"] {
  id: string!;
  target: string!;
  condition: string!;
  action: string!;
  severity: string!;
}

entity[name="SchemaIR"] {
  system: json!;
  modules: List[ModuleIR]!;
  workflows: List[WorkflowIR]!;
  rules: List[RuleIR]!;
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="code2schema"] {

}

deploy {
  target: pip;
}

environment[name="local"] {
  runtime: python;
  env_file: .env;
  python_version: >=3.10;
}
```

### Source Modules

- `code2schema.cli`

## Dependencies

### Runtime

```text markpact:deps python
libcst>=1.1.0
networkx>=3.2
pydantic>=2.5
```

### Development

```text markpact:deps python scope=dev
pytest>=8
pytest-cov
black
ruff
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
```

## Source Map

*Top 1 modules by symbol density — signatures for LLM orientation.*

### `code2schema.cli` (`code2schema/cli.py`)

```python
def _project_name_from_path(path)  # CC=6, fan=3
def main(argv)  # CC=30, fan=32 ⚠
```

## Call Graph

*26 nodes · 18 edges · 6 modules · CC̄=2.1*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `_build_graph_data` *(in code2schema.codegen.visualizer)* | 9 | 1 | 22 | **23** |
| `infer_event_model` *(in code2schema.analyzer.events)* | 26 ⚠ | 1 | 21 | **22** |
| `graph_summary` *(in code2schema.analyzer.graph)* | 8 | 1 | 21 | **22** |
| `to_markdown` *(in code2schema.codegen)* | 7 | 1 | 16 | **17** |
| `extract_module` *(in code2schema.core.extractor)* | 5 | 1 | 14 | **15** |
| `to_proto` *(in code2schema.codegen)* | 3 | 1 | 10 | **11** |
| `_derive_event_name` *(in code2schema.analyzer.events)* | 5 | 2 | 8 | **10** |
| `analyze` *(in code2schema.analyzer.cqrs)* | 6 | 1 | 9 | **10** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/code2schema
# nodes: 26 | edges: 18 | modules: 6
# CC̄=2.1

HUBS[20]:
  code2schema.codegen.visualizer._build_graph_data
    CC=9  in:1  out:22  total:23
  code2schema.analyzer.events.infer_event_model
    CC=26  in:1  out:21  total:22
  code2schema.analyzer.graph.graph_summary
    CC=8  in:1  out:21  total:22
  code2schema.codegen.to_markdown
    CC=7  in:1  out:16  total:17
  code2schema.core.extractor.extract_module
    CC=5  in:1  out:14  total:15
  code2schema.codegen.to_proto
    CC=3  in:1  out:10  total:11
  code2schema.analyzer.events._derive_event_name
    CC=5  in:2  out:8  total:10
  code2schema.analyzer.cqrs.analyze
    CC=6  in:1  out:9  total:10
  code2schema.analyzer.cqrs.generate_rules
    CC=7  in:1  out:6  total:7
  code2schema.core.extractor.extract_project
    CC=6  in:1  out:5  total:6
  code2schema.analyzer.cqrs.build_call_graph
    CC=7  in:1  out:5  total:6
  code2schema.analyzer.graph.centrality_report
    CC=2  in:1  out:4  total:5
  code2schema.analyzer.cqrs.build_workflows
    CC=6  in:1  out:3  total:4
  code2schema.codegen._safe_proto_name
    CC=2  in:1  out:3  total:4
  code2schema.core.extractor._path_to_module
    CC=1  in:1  out:3  total:4
  code2schema.codegen.visualizer.to_html
    CC=1  in:1  out:3  total:4
  code2schema.analyzer.events._past_tense
    CC=1  in:1  out:3  total:4
  code2schema.codegen.write_json
    CC=1  in:1  out:2  total:3
  code2schema.codegen.write_markdown
    CC=1  in:1  out:2  total:3
  code2schema.analyzer.graph.layer_violations
    CC=8  in:1  out:2  total:3

MODULES:
  code2schema.analyzer.cqrs  [5 funcs]
    _infer_role  CC=4  out:0
    analyze  CC=6  out:9
    build_call_graph  CC=7  out:5
    build_workflows  CC=6  out:3
    generate_rules  CC=7  out:6
  code2schema.analyzer.events  [3 funcs]
    _derive_event_name  CC=5  out:8
    _past_tense  CC=1  out:3
    infer_event_model  CC=26  out:21
  code2schema.analyzer.graph  [5 funcs]
    centrality_report  CC=2  out:4
    detect_cycles  CC=1  out:2
    graph_summary  CC=8  out:21
    hub_nodes  CC=3  out:1
    layer_violations  CC=8  out:2
  code2schema.codegen  [7 funcs]
    _safe_proto_name  CC=2  out:3
    to_json  CC=1  out:2
    to_markdown  CC=7  out:16
    to_proto  CC=3  out:10
    write_json  CC=1  out:2
    write_markdown  CC=1  out:2
    write_proto  CC=1  out:2
  code2schema.codegen.visualizer  [3 funcs]
    _build_graph_data  CC=9  out:22
    to_html  CC=1  out:3
    write_html  CC=1  out:2
  code2schema.core.extractor  [3 funcs]
    _path_to_module  CC=1  out:3
    extract_module  CC=5  out:14
    extract_project  CC=6  out:5

EDGES:
  code2schema.analyzer.events.infer_event_model → code2schema.analyzer.events._derive_event_name
  code2schema.analyzer.events._derive_event_name → code2schema.analyzer.events._past_tense
  code2schema.analyzer.cqrs.analyze → code2schema.analyzer.cqrs.build_call_graph
  code2schema.analyzer.cqrs.analyze → code2schema.analyzer.cqrs.build_workflows
  code2schema.analyzer.cqrs.analyze → code2schema.analyzer.cqrs.generate_rules
  code2schema.analyzer.cqrs.analyze → code2schema.analyzer.cqrs._infer_role
  code2schema.analyzer.graph.graph_summary → code2schema.analyzer.graph.detect_cycles
  code2schema.analyzer.graph.graph_summary → code2schema.analyzer.graph.hub_nodes
  code2schema.analyzer.graph.graph_summary → code2schema.analyzer.graph.centrality_report
  code2schema.analyzer.graph.graph_summary → code2schema.analyzer.graph.layer_violations
  code2schema.core.extractor.extract_module → code2schema.core.extractor._path_to_module
  code2schema.core.extractor.extract_project → code2schema.core.extractor.extract_module
  code2schema.codegen.write_json → code2schema.codegen.to_json
  code2schema.codegen.to_proto → code2schema.codegen._safe_proto_name
  code2schema.codegen.write_proto → code2schema.codegen.to_proto
  code2schema.codegen.write_markdown → code2schema.codegen.to_markdown
  code2schema.codegen.visualizer.to_html → code2schema.codegen.visualizer._build_graph_data
  code2schema.codegen.visualizer.write_html → code2schema.codegen.visualizer.to_html
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (1)

**`CLI Command Tests`**

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/code2schema
# nodes: 26 | edges: 18 | modules: 6
# CC̄=2.1

HUBS[20]:
  code2schema.codegen.visualizer._build_graph_data
    CC=9  in:1  out:22  total:23
  code2schema.analyzer.events.infer_event_model
    CC=26  in:1  out:21  total:22
  code2schema.analyzer.graph.graph_summary
    CC=8  in:1  out:21  total:22
  code2schema.codegen.to_markdown
    CC=7  in:1  out:16  total:17
  code2schema.core.extractor.extract_module
    CC=5  in:1  out:14  total:15
  code2schema.codegen.to_proto
    CC=3  in:1  out:10  total:11
  code2schema.analyzer.events._derive_event_name
    CC=5  in:2  out:8  total:10
  code2schema.analyzer.cqrs.analyze
    CC=6  in:1  out:9  total:10
  code2schema.analyzer.cqrs.generate_rules
    CC=7  in:1  out:6  total:7
  code2schema.core.extractor.extract_project
    CC=6  in:1  out:5  total:6
  code2schema.analyzer.cqrs.build_call_graph
    CC=7  in:1  out:5  total:6
  code2schema.analyzer.graph.centrality_report
    CC=2  in:1  out:4  total:5
  code2schema.analyzer.cqrs.build_workflows
    CC=6  in:1  out:3  total:4
  code2schema.codegen._safe_proto_name
    CC=2  in:1  out:3  total:4
  code2schema.core.extractor._path_to_module
    CC=1  in:1  out:3  total:4
  code2schema.codegen.visualizer.to_html
    CC=1  in:1  out:3  total:4
  code2schema.analyzer.events._past_tense
    CC=1  in:1  out:3  total:4
  code2schema.codegen.write_json
    CC=1  in:1  out:2  total:3
  code2schema.codegen.write_markdown
    CC=1  in:1  out:2  total:3
  code2schema.analyzer.graph.layer_violations
    CC=8  in:1  out:2  total:3

MODULES:
  code2schema.analyzer.cqrs  [5 funcs]
    _infer_role  CC=4  out:0
    analyze  CC=6  out:9
    build_call_graph  CC=7  out:5
    build_workflows  CC=6  out:3
    generate_rules  CC=7  out:6
  code2schema.analyzer.events  [3 funcs]
    _derive_event_name  CC=5  out:8
    _past_tense  CC=1  out:3
    infer_event_model  CC=26  out:21
  code2schema.analyzer.graph  [5 funcs]
    centrality_report  CC=2  out:4
    detect_cycles  CC=1  out:2
    graph_summary  CC=8  out:21
    hub_nodes  CC=3  out:1
    layer_violations  CC=8  out:2
  code2schema.codegen  [7 funcs]
    _safe_proto_name  CC=2  out:3
    to_json  CC=1  out:2
    to_markdown  CC=7  out:16
    to_proto  CC=3  out:10
    write_json  CC=1  out:2
    write_markdown  CC=1  out:2
    write_proto  CC=1  out:2
  code2schema.codegen.visualizer  [3 funcs]
    _build_graph_data  CC=9  out:22
    to_html  CC=1  out:3
    write_html  CC=1  out:2
  code2schema.core.extractor  [3 funcs]
    _path_to_module  CC=1  out:3
    extract_module  CC=5  out:14
    extract_project  CC=6  out:5

EDGES:
  code2schema.analyzer.events.infer_event_model → code2schema.analyzer.events._derive_event_name
  code2schema.analyzer.events._derive_event_name → code2schema.analyzer.events._past_tense
  code2schema.analyzer.cqrs.analyze → code2schema.analyzer.cqrs.build_call_graph
  code2schema.analyzer.cqrs.analyze → code2schema.analyzer.cqrs.build_workflows
  code2schema.analyzer.cqrs.analyze → code2schema.analyzer.cqrs.generate_rules
  code2schema.analyzer.cqrs.analyze → code2schema.analyzer.cqrs._infer_role
  code2schema.analyzer.graph.graph_summary → code2schema.analyzer.graph.detect_cycles
  code2schema.analyzer.graph.graph_summary → code2schema.analyzer.graph.hub_nodes
  code2schema.analyzer.graph.graph_summary → code2schema.analyzer.graph.centrality_report
  code2schema.analyzer.graph.graph_summary → code2schema.analyzer.graph.layer_violations
  code2schema.core.extractor.extract_module → code2schema.core.extractor._path_to_module
  code2schema.core.extractor.extract_project → code2schema.core.extractor.extract_module
  code2schema.codegen.write_json → code2schema.codegen.to_json
  code2schema.codegen.to_proto → code2schema.codegen._safe_proto_name
  code2schema.codegen.write_proto → code2schema.codegen.to_proto
  code2schema.codegen.write_markdown → code2schema.codegen.to_markdown
  code2schema.codegen.visualizer.to_html → code2schema.codegen.visualizer._build_graph_data
  code2schema.codegen.visualizer.write_html → code2schema.codegen.visualizer.to_html
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 28f 114236L | python:13,yaml:9,json:2,shell:2,toml:1,txt:1 | 2026-05-04
# CC̄=2.1 | critical:2/103 | dups:0 | cycles:0

HEALTH[2]:
  🟡 CC    main CC=30 (limit:15)
  🟡 CC    infer_event_model CC=26 (limit:15)

REFACTOR[1]:
  1. split 2 high-CC methods  (CC>15)

PIPELINES[15]:
  [1] Src [main]: main → _project_name_from_path
      PURITY: 100% pure
  [2] Src [summary]: summary
      PURITY: 100% pure
  [3] Src [centrality]: centrality
      PURITY: 100% pure
  [4] Src [__init__]: __init__
      PURITY: 100% pure
  [5] Src [visit_Import]: visit_Import
      PURITY: 100% pure

LAYERS:
  code2schema/                    CC̄=4.6    ←in:0  →out:9  !! split
  │ visualizer                 317L  0C    3m  CC=9      ←1
  │ cqrs                       166L  0C    7m  CC=7      ←1
  │ !! events                     162L  3C    4m  CC=26     ←1
  │ extractor                  160L  1C   12m  CC=6      ←1
  │ !! cli                        147L  0C    2m  CC=30     ←0
  │ graph                      146L  0C    8m  CC=8      ←1
  │ __init__                   117L  0C    7m  CC=7      ←1
  │ models                      95L  8C    4m  CC=3      ←0
  │ __init__                    10L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  project/                        CC̄=0.0    ←in:0  →out:0
  │ calls.yaml                 349L  0C    0m  CC=0.0    ←0
  │ map.toon.yaml              114L  0C   56m  CC=0.0    ←0
  │ calls.toon.yaml             99L  0C    0m  CC=0.0    ←0
  │ analysis.toon.yaml          69L  0C    0m  CC=0.0    ←0
  │ project.toon.yaml           49L  0C    0m  CC=0.0    ←0
  │ prompt.txt                  47L  0C    0m  CC=0.0    ←0
  │ evolution.toon.yaml         47L  0C    0m  CC=0.0    ←0
  │ duplication.toon.yaml        9L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! schema.json              111256L  0C    0m  CC=0.0    ←0
  │ !! goal.yaml                  510L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              77L  0C    0m  CC=0.0    ←0
  │ project.sh                  48L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-cli-tests.testql.toon.yaml    20L  0C    0m  CC=0.0    ←0
  │
  docs/                           CC̄=0.0    ←in:0  →out:0
  │ advanced                    67L  0C    0m  CC=0.0    ←0
  │ schema-sample.json          56L  0C    0m  CC=0.0    ←0
  │ basic                       52L  0C    0m  CC=0.0    ←0
  │ basic.sh                    45L  0C    0m  CC=0.0    ←0
  │

COUPLING:
                                 code2schema  code2schema.analyzer   code2schema.codegen      code2schema.core
           code2schema                    ──                     7                     1                     1  !! fan-out
  code2schema.analyzer                    ←7                    ──                                              hub
   code2schema.codegen                    ←1                                          ──                      
      code2schema.core                    ←1                                                                ──
  CYCLES: none
  HUB: code2schema.analyzer/ (fan-in=7)
  SMELL: code2schema/ fan-out=9 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 0 groups | 13f 1441L | 2026-05-04

SUMMARY:
  files_scanned: 13
  total_lines:   1441
  dup_groups:    0
  dup_fragments: 0
  saved_lines:   0
  scan_ms:       4577
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 103 func | 9f | 2026-05-04

NEXT[2] (ranked by impact):
  [1] !! SPLIT-FUNC      main  CC=30  fan=32
      WHY: CC=30 exceeds 15
      EFFORT: ~1h  IMPACT: 960

  [2] !! SPLIT-FUNC      infer_event_model  CC=26  fan=17
      WHY: CC=26 exceeds 15
      EFFORT: ~1h  IMPACT: 442


RISKS[0]: none

METRICS-TARGET:
  CC̄:          2.1 → ≤1.5
  max-CC:      30 → ≤15
  god-modules: 0 → 0
  high-CC(≥15): 2 → ≤1
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  prev CC̄=2.1 → now CC̄=2.1
```

## Intent

Semantic compiler: Code → AST → CQRS Model → Workflow DAG → Proto/Schema
