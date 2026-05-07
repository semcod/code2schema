"""Basic Python API quick-start for code2schema."""
from pathlib import Path

from code2schema import analyze, extract_project
from code2schema.codegen import to_json

modules = extract_project(Path("."))
schema = analyze(modules)
Path("schema.json").write_text(to_json(schema))
print(f"Modules={len(schema.modules)} Functions={len(schema.all_functions())}")
