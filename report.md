# Code2Schema Report

**Modules:** 10  **Functions:** 52  **Workflows:** 9

## CQRS Distribution

| Role | Count |
|------|-------|
| Query | 43 |
| Command | 0 |
| Orchestrator | 9 |

## Quality Rules

- 🔴 **HIGH_FAN_OUT** `code2schema.cli.main` — fan_out=21 >= 10
- 🔴 **HIGH_FAN_OUT** `code2schema.core.extractor._process_func` — fan_out=10 >= 10
- 🔴 **HIGH_FAN_OUT** `code2schema.core.extractor.extract_module` — fan_out=13 >= 10

## Workflows (Orchestrators)

- **workflow_main**: `code2schema.cli.main` → ArgumentParser → add_argument → parse_args → Path → perf_counter → extract_project → analyze → write_json
- **workflow_build_call_graph**: `code2schema.analyzer.cqrs.build_call_graph` → DiGraph → set → add → add_node → add_edge
- **workflow_analyze**: `code2schema.analyzer.cqrs.analyze` → build_call_graph → dict → build_workflows → generate_rules → SchemaIR → out_degree → _infer_role → max
- **workflow__build_graph_data**: `code2schema.codegen.visualizer._build_graph_data` → all_functions → len → append → get → setdefault → commands → queries → orchestrators
- **workflow_to_proto**: `code2schema.codegen.__init__.to_proto` → all_functions → join → capitalize → _safe_proto_name → append → len → commands → queries
- **workflow_to_markdown**: `code2schema.codegen.__init__.to_markdown` → all_functions → len → join → commands → queries → orchestrators → append
- **workflow__process_func**: `code2schema.core.extractor._process_func` → _collect_calls → _detect_side_effects → get_docstring → FunctionIR → append → list → len → fromkeys
- **workflow_extract_module**: `code2schema.core.extractor.extract_module` → _path_to_module → _FunctionVisitor → visit → ModuleIR → read_text → parse → walk → str
- **workflow_extract_project**: `code2schema.core.extractor.extract_project` → set → rglob → any → extract_module → append
