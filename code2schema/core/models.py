"""
code2schema.core.models
~~~~~~~~~~~~~~~~~~~~~~~
Intermediate Representation (IR) — język-most między kodem a schematem.
"""
from __future__ import annotations

from enum import Enum
from typing import List, Optional, Set

from pydantic import BaseModel, Field


class CQRSRole(str, Enum):
    QUERY = "query"
    COMMAND = "command"
    ORCHESTRATOR = "orchestrator"
    UNKNOWN = "unknown"


class SideEffect(str, Enum):
    FILESYSTEM = "filesystem"
    NETWORK = "network"
    SYSTEM = "system"
    DATABASE = "database"
    NONE = "none"


class FunctionIR(BaseModel):
    """Pojedyncza funkcja w modelu semantycznym."""
    name: str
    module: str
    calls: List[str] = Field(default_factory=list)
    role: CQRSRole = CQRSRole.UNKNOWN
    side_effects: List[SideEffect] = Field(default_factory=list)
    fan_out: int = 0
    lines: int = 0
    is_async: bool = False
    docstring: Optional[str] = None

    @property
    def qualified_name(self) -> str:
        return f"{self.module}.{self.name}"


class ModuleIR(BaseModel):
    """Moduł (plik .py) z wyekstrahowanymi funkcjami."""
    name: str          # np. "backend.services.analyzer"
    path: str
    functions: List[FunctionIR] = Field(default_factory=list)
    imports: List[str] = Field(default_factory=list)
    lines: int = 0


class WorkflowStep(BaseModel):
    callee: str
    is_async: bool = False


class WorkflowIR(BaseModel):
    """Graf wykonania (DAG) dla jednej funkcji-orkiestratora."""
    name: str
    entry: str
    steps: List[WorkflowStep] = Field(default_factory=list)


class RuleIR(BaseModel):
    """Heurystyczna reguła jakości wygenerowana z analizy."""
    id: str
    target: str
    condition: str
    action: str
    severity: str = "warning"


class SchemaIR(BaseModel):
    """Korzeń modelu semantycznego całego projektu."""
    system: dict = Field(default_factory=lambda: {"type": "code2schema", "version": "0.1"})
    modules: List[ModuleIR] = Field(default_factory=list)
    workflows: List[WorkflowIR] = Field(default_factory=list)
    rules: List[RuleIR] = Field(default_factory=list)

    # ── helpers ──────────────────────────────────────────────────────────────

    def all_functions(self) -> List[FunctionIR]:
        return [f for m in self.modules for f in m.functions]

    def orchestrators(self) -> List[FunctionIR]:
        return [f for f in self.all_functions() if f.role == CQRSRole.ORCHESTRATOR]

    def commands(self) -> List[FunctionIR]:
        return [f for f in self.all_functions() if f.role == CQRSRole.COMMAND]

    def queries(self) -> List[FunctionIR]:
        return [f for f in self.all_functions() if f.role == CQRSRole.QUERY]
