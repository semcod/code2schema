#!/bin/bash
# Semcod project analysis examples

# 1. Analyze semcod frontend (www)
code2schema /home/tom/github/semcod/www \
  --out /tmp/semcod-schema.json \
  --md /tmp/semcod-report.md \
  --graphml /tmp/semcod-graph.graphml \
  --events \
  --cycles \
  --graph-summary

# 2. Quiet run for CI-like use
code2schema /home/tom/github/semcod/www -o /tmp/semcod-ci.json -q

# 3. Generate proto + html visualization
code2schema /home/tom/github/semcod/www \
  --proto /tmp/semcod-api.proto \
  --html /tmp/semcod-viz.html \
  -q
