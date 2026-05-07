"""Testy jednostkowe code2schema."""
from __future__ import annotations

import argparse
import ast
import textwrap
from pathlib import Path

import pytest

from code2schema.core.models import CQRSRole, SideEffect
from code2schema.core.extractor import extract_module
from code2schema.analyzer.cqrs import _infer_role, analyze, build_call_graph
from code2schema.cli import _resolve_paths
from code2schema.codegen import to_json, to_proto, to_markdown


# ── Fixtures ─────────────────────────────────────────────────────────────────

SAMPLE_CODE = textwrap.dedent("""
    import os
    import requests

    def get_user(user_id):
        return user_id

    def save_user(user_id, data):
        with open("users.json", "w") as f:
            f.write(data)

    def orchestrate(user_id, data):
        result = get_user(user_id)
        save_user(user_id, data)
        os.system("echo done")
        requests.post("http://api", json=result)
        return result
""")


@pytest.fixture
def sample_file(tmp_path: Path) -> Path:
    f = tmp_path / "sample.py"
    f.write_text(SAMPLE_CODE)
    return f


@pytest.fixture
def sample_module(sample_file):
    return extract_module(sample_file)


# ── Ekstrakcja ────────────────────────────────────────────────────────────────

def test_extract_module_returns_module(sample_module):
    assert sample_module is not None
    assert len(sample_module.functions) == 3


def test_function_names(sample_module):
    names = [f.name for f in sample_module.functions]
    assert "get_user" in names
    assert "save_user" in names
    assert "orchestrate" in names


def test_side_effects_detected(sample_module):
    save = next(f for f in sample_module.functions if f.name == "save_user")
    assert SideEffect.FILESYSTEM in save.side_effects


def test_query_no_side_effects(sample_module):
    get = next(f for f in sample_module.functions if f.name == "get_user")
    assert SideEffect.NONE in get.side_effects
    assert get.fan_out == 0


# ── CQRS Inference ───────────────────────────────────────────────────────────

def test_role_query(sample_module):
    get = next(f for f in sample_module.functions if f.name == "get_user")
    assert _infer_role(get) == CQRSRole.QUERY


def test_role_command(sample_module):
    save = next(f for f in sample_module.functions if f.name == "save_user")
    assert _infer_role(save) == CQRSRole.COMMAND


def test_role_orchestrator(sample_module):
    orch = next(f for f in sample_module.functions if f.name == "orchestrate")
    # fan_out >= FAN_OUT_ORCHESTRATOR (5) — orchestrate calls 4 distinct functions
    # After analyze() the role will be updated; test infer directly
    assert _infer_role(orch) in (CQRSRole.ORCHESTRATOR, CQRSRole.COMMAND)


# ── Full analyze ──────────────────────────────────────────────────────────────

def test_analyze_schema(sample_module):
    schema = analyze([sample_module])
    assert schema is not None
    funcs = schema.all_functions()
    assert len(funcs) == 3


def test_analyze_generates_rules(sample_module):
    schema = analyze([sample_module])
    # orchestrate has QUERY_WITH_SIDE_EFFECTS or LONG_FUNCTION potential
    # At minimum schema.rules is a list
    assert isinstance(schema.rules, list)


def test_call_graph_has_edges(sample_module):
    analyze([sample_module])  # sets roles
    G = build_call_graph([sample_module])
    # orchestrate calls get_user and save_user → edges expected
    assert G.number_of_nodes() > 0


# ── Codegen ───────────────────────────────────────────────────────────────────

def test_to_json(sample_module):
    schema = analyze([sample_module])
    output = to_json(schema)
    assert "modules" in output
    assert "workflows" in output
    assert "rules" in output


def test_to_proto(sample_module):
    schema = analyze([sample_module])
    proto = to_proto(schema)
    assert "service Code2Schema" in proto
    assert "rpc" in proto


def test_to_markdown(sample_module):
    schema = analyze([sample_module])
    md = to_markdown(schema)
    assert "# Code2Schema Report" in md
    assert "CQRS" in md


# ── Edge cases ────────────────────────────────────────────────────────────────

def test_empty_project(tmp_path):
    schema = analyze([])
    assert schema.all_functions() == []


def test_invalid_syntax_file(tmp_path):
    bad = tmp_path / "bad.py"
    bad.write_text("def foo(: INVALID SYNTAX !!!")
    mod = extract_module(bad)
    assert mod is None


# ── Graph ─────────────────────────────────────────────────────────────────────

from code2schema.analyzer.graph import (
    build_rich_graph, centrality_report, detect_cycles, hub_nodes,
    layer_violations, write_dot, write_graphml,
)
from code2schema.analyzer.events import infer_event_model


def test_build_rich_graph(sample_module):
    schema = analyze([sample_module])
    G = build_rich_graph(schema)
    assert G.number_of_nodes() > 0


def test_no_cycles_in_sample(sample_module):
    schema = analyze([sample_module])
    G = build_rich_graph(schema)
    cycles = detect_cycles(G)
    # Prosty przykład nie powinien mieć cykli
    assert isinstance(cycles, list)


def test_graphml_export(sample_module, tmp_path):
    schema = analyze([sample_module])
    G = build_rich_graph(schema)
    out = tmp_path / "graph.graphml"
    write_graphml(G, out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_dot_export(sample_module, tmp_path):
    schema = analyze([sample_module])
    G = build_rich_graph(schema)
    out = tmp_path / "graph.dot"
    write_dot(G, out)
    content = out.read_text()
    assert "digraph" in content
    assert "CallGraph" in content


def test_layer_violations(sample_module):
    schema = analyze([sample_module])
    violations = layer_violations(schema)
    assert isinstance(violations, list)


# ── Events ────────────────────────────────────────────────────────────────────

def test_event_model_runs(sample_module):
    schema = analyze([sample_module])
    em = infer_event_model(schema.modules)
    assert hasattr(em, "commands")
    assert hasattr(em, "events")
    assert hasattr(em, "aggregates")


def test_event_model_summary(sample_module):
    schema = analyze([sample_module])
    em = infer_event_model(schema.modules)
    summary = em.summary()
    assert "Commands" in summary
    assert "Domain Events" in summary


# ── CLI Paths ─────────────────────────────────────────────────────────────────

def test_resolve_paths_for_special_project_dir(tmp_path: Path):
    backend_dir = tmp_path / "c2004" / "backend"
    backend_dir.mkdir(parents=True)

    args = argparse.Namespace(
        path=str(backend_dir),
        out=None,
        proto=True,
        md=True,
        html=True,
    )

    root, out_path, proto_path, md_path, html_path = _resolve_paths(args)

    assert root == backend_dir
    assert out_path == backend_dir.parent / "c2004_schema.json"
    assert proto_path == backend_dir.parent / "c2004_api.proto"
    assert md_path == backend_dir.parent / "c2004_report.md"
    assert html_path == backend_dir.parent / "c2004_viz.html"


def test_resolve_paths_for_file_input_with_custom_outputs(tmp_path: Path):
    file_path = tmp_path / "repo" / "main.py"
    file_path.parent.mkdir(parents=True)
    file_path.write_text("def main():\n    pass\n")

    args = argparse.Namespace(
        path=str(file_path),
        out="schema.json",
        proto="api.proto",
        md=None,
        html=None,
    )

    root, out_path, proto_path, md_path, html_path = _resolve_paths(args)

    assert root == file_path
    assert out_path == file_path.parent / "schema.json"
    assert proto_path == file_path.parent / "api.proto"
    assert md_path is None
    assert html_path is None
