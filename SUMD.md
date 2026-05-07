# code2schema

Semantic compiler: Code → AST → CQRS Model → Workflow DAG → Proto/Schema

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Code Analysis](#code-analysis)
- [Source Map](#source-map)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `code2schema`
- **version**: `0.1.1`
- **python_requires**: `>=3.10`
- **license**: {'text': 'Apache-2.0'}
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(1), app.doql.less, goal.yaml, .env.example, src(1 mod), project/(2 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: code2schema;
  version: 0.1.1;
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

## Interfaces

### CLI Entry Points

- `code2schema`

### testql Scenarios

#### `testql-scenarios/generated-cli-tests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -m code2schema
  timeout_ms, 10000

# Test 1: CLI help command
SHELL "python -m code2schema --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "usage"

# Test 2: CLI version command
SHELL "python -m code2schema --version" 5000
ASSERT_EXIT_CODE 0

# Test 3: CLI main workflow (dry-run)
SHELL "python -m code2schema --help" 10000
ASSERT_EXIT_CODE 0
```

## Configuration

```yaml
project:
  name: code2schema
  version: 0.1.1
  env: local
```

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

## Deployment

```bash markpact:run
pip install code2schema

# development install
pip install -e .[dev]
```

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | `*(not set)*` | Required: OpenRouter API key (https://openrouter.ai/keys) |
| `LLM_MODEL` | `openrouter/qwen/qwen3-coder-next` | Model (default: openrouter/qwen/qwen3-coder-next) |
| `PFIX_AUTO_APPLY` | `true` | true = apply fixes without asking |
| `PFIX_AUTO_INSTALL_DEPS` | `true` | true = auto pip/uv install |
| `PFIX_AUTO_RESTART` | `false` | true = os.execv restart after fix |
| `PFIX_MAX_RETRIES` | `3` |  |
| `PFIX_DRY_RUN` | `false` |  |
| `PFIX_ENABLED` | `true` |  |
| `PFIX_GIT_COMMIT` | `false` | true = auto-commit fixes |
| `PFIX_GIT_PREFIX` | `pfix:` | commit message prefix |
| `PFIX_CREATE_BACKUPS` | `false` | false = disable .pfix_backups/ directory |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`code2schema`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `code2schema/__init__.py:__version__`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# code2schema | 18f 1843L | python:15,shell:2,less:1 | 2026-05-04
# stats: 57 func | 12 cls | 18 mod | CC̄=4.3 | critical:2 | cycles:0
# alerts[5]: CC main=30; CC infer_event_model=26; CC _build_graph_data=9; CC build_rich_graph=8; CC layer_violations=8
# hotspots[5]: main fan=32; extract_module fan=13; infer_event_model fan=11; graph_summary fan=11; _build_graph_data fan=9
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[18]:
  app.doql.less,75
  code2schema/__init__.py,11
  code2schema/analyzer/__init__.py,2
  code2schema/analyzer/cqrs.py,167
  code2schema/analyzer/events.py,163
  code2schema/analyzer/graph.py,147
  code2schema/cli.py,148
  code2schema/codegen/__init__.py,118
  code2schema/codegen/visualizer.py,318
  code2schema/core/__init__.py,2
  code2schema/core/extractor.py,161
  code2schema/core/models.py,96
  docs/examples/api/advanced.py,68
  docs/examples/api/basic.py,53
  docs/examples/cli/basic.sh,46
  project.sh,48
  tests/__init__.py,1
  tests/test_code2schema.py,219
D:
  code2schema/__init__.py:
  code2schema/analyzer/__init__.py:
  code2schema/analyzer/cqrs.py:
    e: _infer_role,build_call_graph,detect_cycles,centrality,build_workflows,generate_rules,analyze
    _infer_role(func)
    build_call_graph(modules)
    detect_cycles(G)
    centrality(G)
    build_workflows(modules)
    generate_rules(modules)
    analyze(modules)
  code2schema/analyzer/events.py:
    e: infer_event_model,_derive_event_name,_past_tense,DomainEvent,CommandHandler,EventModel
    DomainEvent:
    CommandHandler:
    EventModel: summary(0)
    infer_event_model(modules)
    _derive_event_name(func_name)
    _past_tense(verb)
  code2schema/analyzer/graph.py:
    e: build_rich_graph,centrality_report,hub_nodes,detect_cycles,layer_violations,write_graphml,write_dot,graph_summary
    build_rich_graph(schema)
    centrality_report(G;top_n)
    hub_nodes(G;threshold)
    detect_cycles(G)
    layer_violations(schema)
    write_graphml(G;path)
    write_dot(G;path)
    graph_summary(G;schema)
  code2schema/cli.py:
    e: _project_name_from_path,main
    _project_name_from_path(path)
    main(argv)
  code2schema/codegen/__init__.py:
    e: to_json,write_json,to_proto,write_proto,to_markdown,write_markdown,_safe_proto_name
    to_json(schema;indent)
    write_json(schema;path)
    to_proto(schema)
    write_proto(schema;path)
    to_markdown(schema)
    write_markdown(schema;path)
    _safe_proto_name(name)
  code2schema/codegen/visualizer.py:
    e: _build_graph_data,to_html,write_html
    _build_graph_data(schema)
    to_html(schema)
    write_html(schema;path)
  code2schema/core/__init__.py:
  code2schema/core/extractor.py:
    e: extract_module,extract_project,_path_to_module,_FunctionVisitor
    _FunctionVisitor: __init__(1),visit_Import(1),visit_ImportFrom(1),visit_FunctionDef(1),visit_AsyncFunctionDef(1),_process_func(2),_collect_calls(1),_resolve_call_name(1),_detect_side_effects(2)  # Odwiedza węzły AST i buduje FunctionIR.
    extract_module(path)
    extract_project(root;exclude)
    _path_to_module(path)
  code2schema/core/models.py:
    e: CQRSRole,SideEffect,FunctionIR,ModuleIR,WorkflowStep,WorkflowIR,RuleIR,SchemaIR
    CQRSRole:
    SideEffect:
    FunctionIR: qualified_name(0)  # Pojedyncza funkcja w modelu semantycznym.
    ModuleIR:  # Moduł (plik .py) z wyekstrahowanymi funkcjami.
    WorkflowStep:
    WorkflowIR:  # Graf wykonania (DAG) dla jednej funkcji-orkiestratora.
    RuleIR:  # Heurystyczna reguła jakości wygenerowana z analizy.
    SchemaIR: all_functions(0),orchestrators(0),commands(0),queries(0)  # Korzeń modelu semantycznego całego projektu.
  docs/examples/api/advanced.py:
  docs/examples/api/basic.py:
  tests/__init__.py:
  tests/test_code2schema.py:
    e: sample_file,sample_module,test_extract_module_returns_module,test_function_names,test_side_effects_detected,test_query_no_side_effects,test_role_query,test_role_command,test_role_orchestrator,test_analyze_schema,test_analyze_generates_rules,test_call_graph_has_edges,test_to_json,test_to_proto,test_to_markdown,test_empty_project,test_invalid_syntax_file,test_build_rich_graph,test_no_cycles_in_sample,test_graphml_export,test_dot_export,test_layer_violations,test_event_model_runs,test_event_model_summary
    sample_file(tmp_path)
    sample_module(sample_file)
    test_extract_module_returns_module(sample_module)
    test_function_names(sample_module)
    test_side_effects_detected(sample_module)
    test_query_no_side_effects(sample_module)
    test_role_query(sample_module)
    test_role_command(sample_module)
    test_role_orchestrator(sample_module)
    test_analyze_schema(sample_module)
    test_analyze_generates_rules(sample_module)
    test_call_graph_has_edges(sample_module)
    test_to_json(sample_module)
    test_to_proto(sample_module)
    test_to_markdown(sample_module)
    test_empty_project(tmp_path)
    test_invalid_syntax_file(tmp_path)
    test_build_rich_graph(sample_module)
    test_no_cycles_in_sample(sample_module)
    test_graphml_export(sample_module;tmp_path)
    test_dot_export(sample_module;tmp_path)
    test_layer_violations(sample_module)
    test_event_model_runs(sample_module)
    test_event_model_summary(sample_module)
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

## Intent

Semantic compiler: Code → AST → CQRS Model → Workflow DAG → Proto/Schema
