"""
code2schema.cli
~~~~~~~~~~~~~~~
CLI v3 — pełny pipeline.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from code2schema.analyzer.cqrs import analyze
from code2schema.analyzer.events import infer_event_model
from code2schema.analyzer.graph import (
    build_rich_graph, detect_cycles, graph_summary, write_dot, write_graphml,
)
from code2schema.codegen import write_json, write_markdown, write_proto
from code2schema.core.extractor import extract_project


def main(argv=None):
    parser = argparse.ArgumentParser(prog="code2schema",
        description="Semantic Compiler: Code → CQRS → Schema / Proto / Graph")
    parser.add_argument("path")
    parser.add_argument("-o", "--out", default="schema.json")
    parser.add_argument("--proto", metavar="FILE")
    parser.add_argument("--md", metavar="FILE")
    parser.add_argument("--graphml", metavar="FILE")
    parser.add_argument("--dot", metavar="FILE")
    parser.add_argument("--events", action="store_true")
    parser.add_argument("--cycles", action="store_true")
    parser.add_argument("--graph-summary", action="store_true")
    parser.add_argument("--no-rules", action="store_true")
    parser.add_argument("--exclude", nargs="*", default=[])
    parser.add_argument("-q", "--quiet", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.path)
    if not root.exists():
        print(f"ERROR: {root}", file=sys.stderr)
        return 1

    t0 = time.perf_counter()
    if not args.quiet:
        print(f"⏳ Parsing: {root}")

    modules = extract_project(root, exclude=args.exclude or None)
    if not modules:
        print("ERROR: Brak plików .py.", file=sys.stderr)
        return 1

    schema = analyze(modules)
    if args.no_rules:
        schema.rules = []

    G = build_rich_graph(schema)

    if args.cycles:
        cycles = detect_cycles(G)
        if cycles:
            print(f"\n⚠️  Cykle ({len(cycles)}):")
            for c in cycles[:5]:
                print(f"  {' → '.join(c[:5])}")
        else:
            print("✅ Brak cykli.")

    if args.graph_summary:
        print("\n── Graph Summary ──────────────────────")
        print(graph_summary(G, schema))

    if args.events:
        em = infer_event_model(modules)
        print("\n── Event Model ────────────────────────")
        print(em.summary())

    write_json(schema, Path(args.out))
    if args.proto:
        write_proto(schema, Path(args.proto))
    if args.md:
        write_markdown(schema, Path(args.md))
    if args.graphml:
        write_graphml(G, Path(args.graphml))
    if args.dot:
        write_dot(G, Path(args.dot))

    if not args.quiet:
        funcs = schema.all_functions()
        print(
            f"\n✅ Gotowe ({time.perf_counter()-t0:.2f}s)\n"
            f"   Modules  : {len(modules)}\n"
            f"   Functions: {len(funcs)}\n"
            f"   Queries  : {len(schema.queries())}\n"
            f"   Commands : {len(schema.commands())}\n"
            f"   Orchest. : {len(schema.orchestrators())}\n"
            f"   Workflows: {len(schema.workflows)}\n"
            f"   Rules    : {len(schema.rules)}\n"
            f"   Graph    : {G.number_of_nodes()}N / {G.number_of_edges()}E\n"
            f"   → {args.out}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
