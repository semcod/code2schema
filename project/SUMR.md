# Code2Schema Report

**Modules:** 15  **Functions:** 93  **Workflows:** 21

## CQRS Distribution

| Role | Count |
|------|-------|
| Query | 67 |
| Command | 5 |
| Orchestrator | 21 |

## Quality Rules

- 🔴 **HIGH_FAN_OUT** `code2schema.cli._print_summary` — fan_out=11 >= 10
- 🔴 **HIGH_FAN_OUT** `code2schema.cli.main` — fan_out=10 >= 10
- 🔴 **HIGH_FAN_OUT** `code2schema.analyzer.graph.graph_summary` — fan_out=11 >= 10
- 🔴 **HIGH_FAN_OUT** `code2schema.core.extractor._process_func` — fan_out=10 >= 10
- 🔴 **HIGH_FAN_OUT** `code2schema.core.extractor.extract_module` — fan_out=13 >= 10

## Workflows (Orchestrators)

- **workflow_test_graphml_export**: `tests.test_code2schema.test_graphml_export` → analyze → build_rich_graph → write_graphml → exists → stat
- **workflow_test_resolve_paths_for_file_input_with_custom_outputs**: `tests.test_code2schema.test_resolve_paths_for_file_input_with_custom_outputs` → mkdir → write_text → Namespace → _resolve_paths → str
- **workflow__run_reports**: `code2schema.cli._run_reports` → detect_cycles → print → infer_event_model → graph_summary → summary → len → join
- **workflow__write_outputs**: `code2schema.cli._write_outputs` → write_json → write_proto → write_markdown → write_html → write_graphml → write_dot → Path
- **workflow__print_summary**: `code2schema.cli._print_summary` → all_functions → print → append → join → len → number_of_nodes → number_of_edges → perf_counter
- **workflow_main**: `code2schema.cli.main` → _build_parser → parse_args → _resolve_paths → perf_counter → _run_extraction → _run_reports → _write_outputs → exists
- **workflow__find_emitters**: `code2schema.analyzer.events._find_emitters` → search → any → _derive_event_name → append → DomainEvent
- **workflow__find_handlers**: `code2schema.analyzer.events._find_handlers` → search → strip → append → replace → lower
- **workflow_infer_event_model**: `code2schema.analyzer.events.infer_event_model` → _find_emitters → _find_handlers → _find_command_handlers → _find_aggregates → EventModel
- **workflow__derive_event_name**: `code2schema.analyzer.events._derive_event_name` → split → startswith → len → join → _past_tense → capitalize
- **workflow_build_call_graph**: `code2schema.analyzer.cqrs.build_call_graph` → DiGraph → set → add → add_node → add_edge
- **workflow_analyze**: `code2schema.analyzer.cqrs.analyze` → build_call_graph → dict → build_workflows → generate_rules → SchemaIR → out_degree → _infer_role → max
- **workflow_build_rich_graph**: `code2schema.analyzer.graph.build_rich_graph` → DiGraph → add_node → get → int → add_edge
- **workflow_write_dot**: `code2schema.analyzer.graph.write_dot` → nodes → append → edges → write_text → get → join → split
- **workflow_graph_summary**: `code2schema.analyzer.graph.graph_summary` → detect_cycles → hub_nodes → centrality_report → layer_violations → join → append → number_of_nodes → number_of_edges
- **workflow__process_func**: `code2schema.core.extractor._process_func` → _collect_calls → _detect_side_effects → get_docstring → FunctionIR → append → list → len → fromkeys
- **workflow_extract_module**: `code2schema.core.extractor.extract_module` → _path_to_module → _FunctionVisitor → visit → ModuleIR → read_text → parse → walk → str
- **workflow_extract_project**: `code2schema.core.extractor.extract_project` → set → rglob → any → extract_module → append
- **workflow_to_proto**: `code2schema.codegen.__init__.to_proto` → all_functions → join → capitalize → _safe_proto_name → append → len → commands → queries
- **workflow_to_markdown**: `code2schema.codegen.__init__.to_markdown` → all_functions → len → join → commands → queries → orchestrators → append
