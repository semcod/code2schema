#!/bin/bash
# Basic CLI usage examples for code2schema

# 1. Basic analysis - generates schema.json in project directory
code2schema /home/tom/github/maskservice/c2004/backend
# Output: /home/tom/github/maskservice/c2004/c2004_schema.json

# 2. Generate all formats
code2schema ./backend --proto --md --html
# Output:
#   - backend_schema.json
#   - backend_api.proto
#   - backend_report.md
#   - backend_viz.html

# 3. Full analysis with diagnostics
code2schema ./backend \
    --proto \
    --md \
    --html \
    --graph-summary \
    --events \
    --cycles

# 4. Custom output names
code2schema ./backend \
    --proto api.proto \
    --md report.md \
    --html viz.html

# 5. Exclude directories (e.g., tests, migrations)
code2schema ./backend \
    --proto --md \
    --exclude "tests/**" "migrations/**" "venv/**"

# 6. Quiet mode (no console output)
code2schema ./backend --proto --md -q

# 7. Disable quality rules
code2schema ./backend --md --no-rules

# 8. Graph export formats
code2schema ./backend \
    --graphml graph.graphml \
    --dot graph.dot
