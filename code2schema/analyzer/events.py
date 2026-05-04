"""
code2schema.analyzer.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Inferencja modelu zdarzeń (DDD / Event Sourcing):
  - wykrywa funkcje, które "emitują" zdarzenia
  - klasyfikuje: Command Handler → Event → Event Handler
  - buduje Event Flow Map
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

from code2schema.core.models import CQRSRole, FunctionIR, ModuleIR


# ── Heurystyki nazw ───────────────────────────────────────────────────────────

_EVENT_EMIT_PATTERNS = re.compile(
    r"(emit|publish|dispatch|fire|send|enqueue|produce|notify|trigger|broadcast)",
    re.I,
)
_EVENT_HANDLER_PATTERNS = re.compile(
    r"(on_|handle_|listener|subscriber|consumer|process_|receive_)",
    re.I,
)
_AGGREGATE_PATTERNS = re.compile(
    r"(create|update|delete|save|store|persist|commit|apply)",
    re.I,
)


@dataclass
class DomainEvent:
    name: str              # np. "UserCreated"
    emitted_by: str        # qualified_name funkcji emitującej
    handled_by: List[str] = field(default_factory=list)


@dataclass
class CommandHandler:
    name: str
    command: str           # nazwa wywołania, które traktujemy jako "command"
    emits: List[str] = field(default_factory=list)


@dataclass
class EventModel:
    commands: List[CommandHandler] = field(default_factory=list)
    events: List[DomainEvent] = field(default_factory=list)
    aggregates: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"Commands        : {len(self.commands)}",
            f"Domain Events   : {len(self.events)}",
            f"Aggregates      : {len(self.aggregates)}",
        ]
        if self.events:
            lines.append("\nDomain Events:")
            for ev in self.events[:15]:
                handlers = ", ".join(ev.handled_by[:3]) or "—"
                lines.append(f"  {ev.name:30s} ← {ev.emitted_by.split('.')[-1]:25s} → [{handlers}]")
        if self.commands:
            lines.append("\nCommand Handlers (top 10):")
            for cmd in self.commands[:10]:
                emits = ", ".join(cmd.emits[:3]) or "—"
                lines.append(f"  {cmd.name:30s} emits=[{emits}]")
        return "\n".join(lines)


# ── Inference ─────────────────────────────────────────────────────────────────

def infer_event_model(modules: List[ModuleIR]) -> EventModel:
    """Przechodzi po IR i buduje model zdarzeń."""
    model = EventModel()

    all_funcs: dict[str, FunctionIR] = {}
    for mod in modules:
        for f in mod.functions:
            all_funcs[f.qualified_name] = f
            all_funcs[f.name] = f  # short alias

    # Krok 1: znajdź emiterów
    emitters: dict[str, DomainEvent] = {}
    for mod in modules:
        for f in mod.functions:
            if _EVENT_EMIT_PATTERNS.search(f.name) or any(
                _EVENT_EMIT_PATTERNS.search(c) for c in f.calls
            ):
                event_name = _derive_event_name(f.name)
                ev = DomainEvent(name=event_name, emitted_by=f.qualified_name)
                emitters[f.name] = ev
                model.events.append(ev)

    # Krok 2: znajdź handlerów
    for mod in modules:
        for f in mod.functions:
            if _EVENT_HANDLER_PATTERNS.search(f.name):
                # sprawdź, czy handler pasuje do jakiegoś zdarzenia
                for ev in model.events:
                    keyword = ev.name.lower().replace("event", "").strip()
                    if keyword and keyword in f.name.lower():
                        ev.handled_by.append(f.qualified_name)

    # Krok 3: command handlers
    for mod in modules:
        for f in mod.functions:
            if f.role == CQRSRole.COMMAND or _AGGREGATE_PATTERNS.search(f.name):
                emits = [
                    _derive_event_name(c)
                    for c in f.calls
                    if _EVENT_EMIT_PATTERNS.search(c)
                ]
                if emits or f.role == CQRSRole.COMMAND:
                    model.commands.append(
                        CommandHandler(
                            name=f.qualified_name,
                            command=f.name,
                            emits=emits,
                        )
                    )

    # Krok 4: agregaty — moduły z operacjami CRUD
    for mod in modules:
        crud_score = sum(
            1 for f in mod.functions
            if _AGGREGATE_PATTERNS.search(f.name)
        )
        if crud_score >= 2:
            model.aggregates.append(mod.name)

    return model


def _derive_event_name(func_name: str) -> str:
    """save_user → UserSaved, create_order → OrderCreated."""
    # Usuń prefiks czasownikowy
    for prefix in ("on_", "handle_", "emit_", "publish_", "dispatch_", "fire_"):
        if func_name.startswith(prefix):
            func_name = func_name[len(prefix):]
            break

    parts = func_name.split("_")
    if len(parts) >= 2:
        verb = parts[-1]  # ostatni segment = czasownik → past tense
        subject = "".join(p.capitalize() for p in parts[:-1])
        past = _past_tense(verb)
        return f"{subject}{past}"

    return func_name.capitalize() + "Event"


def _past_tense(verb: str) -> str:
    _map = {
        "create": "Created", "update": "Updated", "delete": "Deleted",
        "save": "Saved", "send": "Sent", "emit": "Emitted",
        "publish": "Published", "register": "Registered",
        "process": "Processed", "notify": "Notified",
    }
    return _map.get(verb.lower(), verb.capitalize() + "d")
