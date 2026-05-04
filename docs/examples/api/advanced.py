"""
Advanced Python API usage for code2schema
"""
from pathlib import Path
from code2schema import extract_project, analyze
from code2schema.analyzer.cqrs import CQRSRole
from code2schema.analyzer.graph import build_rich_graph, hub_nodes, centrality_report, layer_violations

# 1. Extract with exclusions
modules = extract_project(
    Path("./backend"),
    exclude=["tests/**", "migrations/**", "venv/**", ".venv/**"]
)

schema = analyze(modules)

# 2. Filter functions by role
queries = [f for f in schema.all_functions() if f.role == CQRSRole.QUERY]
commands = [f for f in schema.all_functions() if f.role == CQRSRole.COMMAND]
orchestrators = [f for f in schema.all_functions() if f.role == CQRSRole.ORCHESTRATOR]

# 3. Find high fan-out functions (potential refactoring targets)
high_fan_out = [f for f in schema.all_functions() if f.fan_out >= 10]
print(f"Functions with fan-out >= 10: {len(high_fan_out)}")
for func in high_fan_out[:10]:
    print(f"  - {func.name} (fan_out={func.fan_out})")

# 4. Find long functions
long_functions = [f for f in schema.all_functions() if f.lines > 100]
print(f"\nFunctions with > 100 lines: {len(long_functions)}")

# 5. Graph analysis
G = build_rich_graph(schema)

# Get hub nodes (architectural centers)
hubs = hub_nodes(G, top_n=10)
print("\nTop 10 hub nodes:")
for node, score in hubs:
    print(f"  - {node}: {score:.4f}")

# PageRank centrality
centrality = centrality_report(G, top_n=5)
print("\nTop 5 by PageRank:")
print(centrality)

# 6. Access workflow DAGs
print(f"\nWorkflows: {len(schema.workflows)}")
for wf in schema.workflows[:5]:
    print(f"  - {wf.name}: {len(wf.steps)} steps")

# 7. Access quality rules
print(f"\nQuality rules: {len(schema.rules)}")
for rule in schema.rules[:5]:
    print(f"  - [{rule.severity}] {rule.id}: {rule.condition}")

# 8. Inspect specific function
if schema.modules:
    mod = schema.modules[0]
    if mod.functions:
        func = mod.functions[0]
        print(f"\nExample function: {func.name}")
        print(f"  Module: {func.module}")
        print(f"  Role: {func.role.value}")
        print(f"  Lines: {func.lines}")
        print(f"  Fan-out: {func.fan_out}")
        print(f"  Calls: {func.calls}")
        print(f"  Side effects: {[s.value for s in func.side_effects]}")
