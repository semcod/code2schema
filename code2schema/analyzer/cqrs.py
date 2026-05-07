"""
code2schema.analyzer.cqrs
~~~~~~~~~~~~~~~~~~~~~~~~~
CQRS inference + call graph (NetworkX) + reguły jakości.
"""

from __future__ import annotations

from typing import List

import networkx as nx

from code2schema.core.models import (
    CQRSRole,
    FunctionIR,
    ModuleIR,
    RuleIR,
    SchemaIR,
    SideEffect,
    WorkflowIR,
    WorkflowStep,
)

# ── Progi heurystyczne ───────────────────────────────────────────────────────

FAN_OUT_ORCHESTRATOR = 5  # >= N wywołań → orchestrator
FAN_OUT_HIGH = 10  # alert reguły
CC_LIMIT = 15  # (placeholder, liczony zewnętrznie)


# ── CQRS Inference ───────────────────────────────────────────────────────────


def _infer_role(func: FunctionIR) -> CQRSRole:
    """Klasyfikuje funkcję na podstawie side-effectów i fan-outu."""
    has_side_effects = SideEffect.NONE not in func.side_effects

    if func.fan_out >= FAN_OUT_ORCHESTRATOR:
        return CQRSRole.ORCHESTRATOR

    if has_side_effects:
        return CQRSRole.COMMAND

    if func.fan_out == 0:
        return CQRSRole.QUERY

    # Małe funkcje bez side-effectów, ale z wywołaniami → query
    return CQRSRole.QUERY


# ── Call Graph ───────────────────────────────────────────────────────────────


def build_call_graph(modules: List[ModuleIR]) -> nx.DiGraph:
    """Buduje skierowany graf wywołań między funkcjami."""
    G = nx.DiGraph()

    all_names: set[str] = set()
    for mod in modules:
        for f in mod.functions:
            all_names.add(f.name)
            G.add_node(f.qualified_name, role=f.role, module=mod.name)

    for mod in modules:
        for f in mod.functions:
            for callee in f.calls:
                if callee in all_names:
                    G.add_edge(f.qualified_name, callee)

    return G


def detect_cycles(G: nx.DiGraph) -> List[List[str]]:
    """Zwraca listę cykli w grafie wywołań."""
    return list(nx.simple_cycles(G))


def centrality(G: nx.DiGraph) -> dict[str, float]:
    """PageRank — im wyższy, tym bardziej 'centralny' w architekturze."""
    return nx.pagerank(G) if G.number_of_edges() > 0 else {}


# ── Workflow DAG ──────────────────────────────────────────────────────────────


def build_workflows(modules: List[ModuleIR]) -> List[WorkflowIR]:
    """Buduje DAG wykonania dla każdego orkiestratora."""
    workflows: list[WorkflowIR] = []
    for mod in modules:
        for f in mod.functions:
            if f.role == CQRSRole.ORCHESTRATOR and f.calls:
                workflow = WorkflowIR(
                    name=f"workflow_{f.name}",
                    entry=f.qualified_name,
                    steps=[
                        WorkflowStep(callee=c, is_async=f.is_async) for c in f.calls
                    ],
                )
                workflows.append(workflow)
    return workflows


# ── Rules ────────────────────────────────────────────────────────────────────


def generate_rules(modules: List[ModuleIR]) -> List[RuleIR]:
    """Generuje heurystyczne reguły jakości na podstawie IR."""
    rules: list[RuleIR] = []

    for mod in modules:
        for f in mod.functions:
            if f.fan_out >= FAN_OUT_HIGH:
                rules.append(
                    RuleIR(
                        id="HIGH_FAN_OUT",
                        target=f.qualified_name,
                        condition=f"fan_out={f.fan_out} >= {FAN_OUT_HIGH}",
                        action="refactor_to_service",
                        severity="error",
                    )
                )
            if f.lines > 100:
                rules.append(
                    RuleIR(
                        id="LONG_FUNCTION",
                        target=f.qualified_name,
                        condition=f"lines={f.lines} > 100",
                        action="split_function",
                        severity="warning",
                    )
                )
            if f.role == CQRSRole.QUERY and SideEffect.NONE not in f.side_effects:
                rules.append(
                    RuleIR(
                        id="QUERY_WITH_SIDE_EFFECTS",
                        target=f.qualified_name,
                        condition="role=query but has side effects",
                        action="separate_command_from_query",
                        severity="warning",
                    )
                )

    return rules


# ── Main entry ────────────────────────────────────────────────────────────────


def analyze(modules: List[ModuleIR]) -> SchemaIR:
    """Pełna analiza: CQRS + graf + workflow + reguły → SchemaIR."""

    # 1. Ustaw rolę CQRS dla każdej funkcji
    for mod in modules:
        for f in mod.functions:
            f.role = _infer_role(f)

    # 2. Graf wywołań
    G = build_call_graph(modules)

    # 3. Wzbogać fan-out danymi z grafu
    out_degrees = dict(G.out_degree())
    for mod in modules:
        for f in mod.functions:
            qn = f.qualified_name
            if qn in out_degrees:
                f.fan_out = max(f.fan_out, out_degrees[qn])
            # Ponów rolę po uaktualnieniu fan-out
            f.role = _infer_role(f)

    # 4. Workflow DAG
    workflows = build_workflows(modules)

    # 5. Reguły
    rules = generate_rules(modules)

    return SchemaIR(modules=modules, workflows=workflows, rules=rules)
