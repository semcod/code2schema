"""
Basic Python API usage for code2schema
"""
from pathlib import Path
from code2schema import extract_project, analyze
from code2schema.analyzer.graph import build_rich_graph, graph_summary, detect_cycles
from code2schema.analyzer.events import infer_event_model
from code2schema.codegen import to_json, to_proto, to_markdown
from code2schema.codegen.visualizer import write_html

# 1. Basic extraction and analysis
modules = extract_project(Path("/home/tom/github/maskservice/c2004/backend"))
schema = analyze(modules)

# 2. Access CQRS statistics
print(f"Modules:       {len(schema.modules)}")
print(f"Functions:     {len(schema.all_functions())}")
print(f"Queries:       {len(schema.queries())}")
print(f"Commands:      {len(schema.commands())}")
print(f"Orchestrators: {len(schema.orchestrators())}")

# 3. Export to JSON
json_output = to_json(schema, indent=2)
Path("schema.json").write_text(json_output)

# 4. Export to Protocol Buffers
proto_output = to_proto(schema)
Path("api.proto").write_text(proto_output)

# 5. Export to Markdown report
md_output = to_markdown(schema)
Path("report.md").write_text(md_output)

# 6. Generate interactive HTML visualization
write_html(schema, Path("viz.html"))

# 7. Graph analysis
G = build_rich_graph(schema)

# Print graph summary
print(graph_summary(G, schema))

# Detect cycles
cycles = detect_cycles(G)
if cycles:
    print(f"\n⚠️  Found {len(cycles)} cycles:")
    for cycle in cycles[:5]:
        print(f"  {' → '.join(cycle)}")

# 8. Event model (DDD/Event Sourcing)
em = infer_event_model(modules)
print(em.summary())
