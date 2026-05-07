"""
code2schema.core.extractor
~~~~~~~~~~~~~~~~~~~~~~~~~~
Ekstrakcja funkcji i importów z plików .py przy użyciu wbudowanego modułu `ast`.
Bez zewnętrznych zależności — czyste stdlib.
"""

from __future__ import annotations

import ast
from pathlib import Path

from code2schema.core.models import FunctionIR, ModuleIR


# ── Wzorce side-effectów ─────────────────────────────────────────────────────

_FILESYSTEM_CALLS: set[str] = {
    "open",
    "write",
    "read",
    "unlink",
    "mkdir",
    "rmdir",
    "rename",
}
_NETWORK_CALLS: set[str] = {
    "get",
    "post",
    "put",
    "delete",
    "patch",
    "request",
    "fetch",
    "connect",
}
_SYSTEM_CALLS: set[str] = {
    "system",
    "popen",
    "subprocess",
    "Popen",
    "run",
    "call",
    "check_output",
}
_DB_CALLS: set[str] = {
    "execute",
    "commit",
    "rollback",
    "query",
    "insert",
    "update",
    "delete",
}

_NETWORK_MODULES: set[str] = {"requests", "httpx", "aiohttp", "urllib", "http"}
_SYSTEM_MODULES: set[str] = {"os", "subprocess", "shutil", "sys"}


class _FunctionVisitor(ast.NodeVisitor):
    """Odwiedza węzły AST i buduje FunctionIR."""

    def __init__(self, module_name: str) -> None:
        self.module_name = module_name
        self.functions: list[FunctionIR] = []
        self._imports: set[str] = set()

    # ── imports ───────────────────────────────────────────────────────────────

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._imports.add(alias.name.split(".")[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self._imports.add(node.module.split(".")[0])
        self.generic_visit(node)

    # ── functions ─────────────────────────────────────────────────────────────

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._process_func(node, is_async=False)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._process_func(node, is_async=True)
        self.generic_visit(node)

    def _process_func(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool
    ) -> None:
        calls = self._collect_calls(node)
        side_effects = self._detect_side_effects(node, calls)
        docstring = ast.get_docstring(node)

        func = FunctionIR(
            name=node.name,
            module=self.module_name,
            calls=list(dict.fromkeys(calls)),  # deduplicate, preserve order
            fan_out=len(set(calls)),
            side_effects=side_effects,
            lines=(
                node.end_lineno - node.lineno + 1 if hasattr(node, "end_lineno") else 0
            ),
            is_async=is_async,
            docstring=docstring,
        )
        self.functions.append(func)

    def _collect_calls(self, node: ast.AST) -> list[str]:
        """Zbiera nazwy wszystkich wywołań funkcji wewnątrz węzła."""
        calls: list[str] = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                name = self._resolve_call_name(child.func)
                if name:
                    calls.append(name)
        return calls

    @staticmethod
    def _resolve_call_name(func_node: ast.expr) -> str | None:
        if isinstance(func_node, ast.Name):
            return func_node.id
        if isinstance(func_node, ast.Attribute):
            return func_node.attr
        return None

    def _detect_side_effects(self, node: ast.AST, calls: list[str]) -> list[str]:
        from code2schema.core.models import SideEffect

        effects: list[SideEffect] = []
        call_set = set(calls)

        if call_set & _FILESYSTEM_CALLS:
            effects.append(SideEffect.FILESYSTEM)
        if call_set & _NETWORK_CALLS:
            effects.append(SideEffect.NETWORK)
        if call_set & _SYSTEM_CALLS:
            effects.append(SideEffect.SYSTEM)
        if call_set & _DB_CALLS:
            effects.append(SideEffect.DATABASE)

        return effects or [SideEffect.NONE]


# ── Public API ────────────────────────────────────────────────────────────────


def extract_module(path: Path) -> ModuleIR | None:
    """Parsuje jeden plik .py i zwraca ModuleIR."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return None

    module_name = _path_to_module(path)
    visitor = _FunctionVisitor(module_name)
    visitor.visit(tree)

    imports = [
        alias.name
        for node in ast.walk(tree)
        for alias in (
            node.names if isinstance(node, (ast.Import, ast.ImportFrom)) else []
        )
    ]

    return ModuleIR(
        name=module_name,
        path=str(path),
        functions=visitor.functions,
        imports=list(dict.fromkeys(imports)),
        lines=len(source.splitlines()),
    )


def extract_project(root: Path, exclude: list[str] | None = None) -> list[ModuleIR]:
    """Rekurencyjnie przetwarza katalog i zwraca listę ModuleIR."""
    exclude = set(exclude or ["__pycache__", ".venv", "venv", "node_modules", ".git"])
    modules: list[ModuleIR] = []

    for py_file in root.rglob("*.py"):
        if any(part in exclude for part in py_file.parts):
            continue
        mod = extract_module(py_file)
        if mod is not None:
            modules.append(mod)

    return modules


def _path_to_module(path: Path) -> str:
    """Konwertuje ścieżkę pliku na notację modułu (dots)."""
    parts = list(path.with_suffix("").parts)
    return ".".join(parts)
