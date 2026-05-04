# Code2Schema Report

**Modules:** 607  **Functions:** 3142  **Workflows:** 1118

## CQRS Distribution

| Role | Count |
|------|-------|
| Query | 1518 |
| Command | 505 |
| Orchestrator | 1119 |

## Quality Rules

- 🔴 **HIGH_FAN_OUT** `app.main.lifespan` — fan_out=18 >= 10
- 🟡 **LONG_FUNCTION** `migrations.run_migration` — lines=143 > 100
- 🔴 **QUERY_WITH_SIDE_EFFECTS** `app.handlers.get_data` — query with IO

## Workflows (Orchestrators)

- **workflow_lifespan**: `app.main.lifespan` → init_db → get_logger → setup_cqrs → init_config
- **workflow_process**: `app.services.process` → validate → transform → save → emit_event

## Event Model

Commands        : 517
Domain Events   : 145
Aggregates      : 76

## Graph Summary

Nodes     : 2922
Edges     : 5612
Cycles    : 2
Hubs      : 15
Violations: 0

Top-5 PageRank:
  0.0891  main
  0.0452  process_scenario
  0.0418  get_logger
  0.0387  init_db
  0.0321  handle_command
