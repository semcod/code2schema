# code2schema


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.1-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$0.15-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-1.0h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $0.1500 (1 commits)
- 👤 **Human dev:** ~$100 (1.0h @ $100/h, 30min dedup)

Generated on 2026-05-04 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---



**Semantic Compiler for Software Systems**

Przekształca kod Python w model semantyczny CQRS → kontrakty API → graf architektury.

```
CODE (.py)
  ⬇  AST extraction (built-in ast)
  ⬇  CQRS inference (Query / Command / Orchestrator)
  ⬇  Call Graph (NetworkX)
  ⬇  Event Model (DDD / Event Sourcing)
  ⬇  Workflow DAG
  ⬇  Quality Rules
  ↓
JSON schema · .proto · Markdown · GraphML · DOT
```

## Instalacja

```bash
pip install code2schema
```

Opcjonalne backendy:

```bash
pip install "code2schema[proto]"   # grpcio-tools → kompilacja .proto
pip install "code2schema[neo4j]"   # eksport do bazy grafowej
pip install "code2schema[viz]"     # pyvis → wizualizacja HTML
pip install "code2schema[dev]"     # pytest + ruff + black
```

## Szybki start

```bash
# Pełna analiza projektu
code2schema ./moj_projekt \
  --out schema.json \
  --proto api.proto \
  --md report.md \
  --graphml graph.graphml \
  --dot graph.dot \
  --graph-summary \
  --events \
  --cycles
```

Przykładowy output:

```
✅ Gotowe (1.2s)
   Modules  : 87
   Functions: 883
   Queries  : 612
   Commands : 184
   Orchest. : 87
   Workflows: 87
   Rules    : 43
   Graph    : 883N / 1204E
   → schema.json
```

## Użycie w kodzie

```python
from code2schema import extract_project, analyze
from code2schema.analyzer.graph import build_rich_graph, graph_summary
from code2schema.analyzer.events import infer_event_model
from code2schema.codegen import to_proto, to_markdown
from pathlib import Path

# Ekstrakcja + analiza
modules = extract_project(Path("./backend"))
schema  = analyze(modules)

# CQRS
print(f"Queries:      {len(schema.queries())}")
print(f"Commands:     {len(schema.commands())}")
print(f"Orchestrators:{len(schema.orchestrators())}")

# Graf
G = build_rich_graph(schema)
print(graph_summary(G, schema))

# Event Model (DDD)
em = infer_event_model(modules)
print(em.summary())

# Eksport
print(to_proto(schema))
print(to_markdown(schema))
```

## Architektura paczki

```
code2schema/
├── core/
│   ├── models.py       # IR: FunctionIR, ModuleIR, SchemaIR (Pydantic)
│   └── extractor.py    # AST parser (stdlib ast, bez zależności)
├── analyzer/
│   ├── cqrs.py         # CQRS inference + WorkflowDAG + Rules
│   ├── graph.py        # NetworkX: centrality, hubs, cycles, GraphML/DOT
│   └── events.py       # DDD / Event Sourcing inference
├── codegen/
│   └── __init__.py     # JSON, .proto, Markdown generators
└── cli.py              # entry point: code2schema <path> [flags]
```

## Klasy CQRS

| Rola | Kryterium |
|------|-----------|
| `query` | brak side-effectów, fan-out = 0 |
| `command` | side-effects (IO, network, DB) |
| `orchestrator` | fan-out ≥ 5 (wywołuje wiele funkcji) |

## Reguły jakości

Automatycznie generowane:

| ID | Warunek | Akcja |
|----|---------|-------|
| `HIGH_FAN_OUT` | fan-out ≥ 10 | refactor_to_service |
| `LONG_FUNCTION` | lines > 100 | split_function |
| `QUERY_WITH_SIDE_EFFECTS` | query + IO | separate_command_from_query |

## Graph export

GraphML można otworzyć w **Gephi**, **yEd** lub zaimportować do **Neo4j**.  
DOT renderuje **Graphviz**: `dot -Tsvg graph.dot -o graph.svg`

## Biblioteki

| Kategoria | Biblioteka | Po co |
|-----------|-----------|-------|
| Parsing | `ast` (stdlib) | Parsowanie Python bez zależności |
| Parsing | `libcst` | Modyfikacja kodu z zachowaniem formatowania |
| Parsing | `tree-sitter` | Multi-language (Go, TS, Rust) — v4 |
| Graf | `networkx` | Call graph, centrality, cykle |
| Graf | `neo4j` | Eksport do bazy grafowej |
| Wizualizacja | `pyvis` | Interaktywny HTML |
| Schema | `pydantic` | IR models + walidacja |
| Proto | `grpcio-tools` | Kompilacja `.proto` → kod |

## Roadmap

- [x] v0.1 — AST extraction, CQRS inference, JSON/Proto/MD output
- [x] v0.1 — NetworkX call graph, GraphML/DOT export, PageRank
- [x] v0.1 — Event Model (DDD), layer violation detection
- [ ] v0.2 — `libcst` extractor (zachowanie formatowania, transformacje)
- [ ] v0.2 — `tree-sitter` multi-language (Go, TypeScript, Rust)
- [ ] v0.3 — Neo4j export, pyvis HTML visualization
- [ ] v0.3 — Cross-language code generator (proto → Go/TS stubs)
- [ ] v0.4 — Data Flow Graph (DFG), State model extraction

## Licencja

MIT


## License

Licensed under Apache-2.0.
