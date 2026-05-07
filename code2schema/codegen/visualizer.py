"""
code2schema.codegen.visualizer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Generuje interaktywny HTML z grafem CQRS (D3.js force layout).
Bez zewnętrznych zależności poza stdlib — D3 ładowany z CDN.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from code2schema.core.models import CQRSRole, SchemaIR

# ── Kolory ról ────────────────────────────────────────────────────────────────
ROLE_COLOR: dict[str, str] = {
    CQRSRole.QUERY: "#4ade80",  # zielony
    CQRSRole.COMMAND: "#fb923c",  # pomarańczowy
    CQRSRole.ORCHESTRATOR: "#a78bfa",  # fioletowy
    CQRSRole.UNKNOWN: "#94a3b8",  # szary
}

ROLE_EMOJI: dict[str, str] = {
    CQRSRole.QUERY: "🔍",
    CQRSRole.COMMAND: "✏️",
    CQRSRole.ORCHESTRATOR: "🔀",
    CQRSRole.UNKNOWN: "❓",
}


def _build_nodes(schema: SchemaIR) -> tuple[list[dict], dict[str, int]]:
    """Buduje listę node'ów i mapę nazwa → index dla D3."""
    nodes: list[dict] = []
    node_ids: dict[str, int] = {}
    for func in schema.all_functions():
        idx = len(nodes)
        node_ids[func.name] = idx
        nodes.append(
            {
                "id": idx,
                "name": func.name,
                "module": func.module,
                "role": func.role.value,
                "color": ROLE_COLOR.get(func.role, "#94a3b8"),
                "emoji": ROLE_EMOJI.get(func.role, "❓"),
                "fan_out": func.fan_out,
                "lines": func.lines,
                "side_effects": [s.value for s in func.side_effects],
                "is_async": func.is_async,
            }
        )
    return nodes, node_ids


def _build_links(schema: SchemaIR, node_ids: dict[str, int]) -> list[dict]:
    """Buduje listę krawędzi (caller → callee) dla D3."""
    links: list[dict] = []
    for func in schema.all_functions():
        src = node_ids.get(func.name)
        if src is None:
            continue
        for callee in func.calls:
            dst = node_ids.get(callee)
            if dst is not None and src != dst:
                links.append({"source": src, "target": dst})
    return links


def _group_rules_by_target(schema: SchemaIR) -> dict[str, list[str]]:
    """Grupuje rule.id po krótkiej nazwie targetu."""
    rules_by_target: dict[str, list[str]] = {}
    for r in schema.rules:
        rules_by_target.setdefault(r.target.split(".")[-1], []).append(r.id)
    return rules_by_target


def _build_stats(schema: SchemaIR, function_count: int) -> dict[str, int]:
    """Buduje sekcję 'stats' wyświetlaną w pasku górnym."""
    return {
        "modules": len(schema.modules),
        "functions": function_count,
        "commands": len(schema.commands()),
        "queries": len(schema.queries()),
        "orchestrators": len(schema.orchestrators()),
        "workflows": len(schema.workflows),
        "rules": len(schema.rules),
    }


def _build_graph_data(schema: SchemaIR) -> dict[str, Any]:
    """Buduje nodes/links/rules/stats dla D3 force graph."""
    nodes, node_ids = _build_nodes(schema)
    links = _build_links(schema, node_ids)
    return {
        "nodes": nodes,
        "links": links,
        "rules": _group_rules_by_target(schema),
        "stats": _build_stats(schema, len(nodes)),
    }


_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Code2Schema — CQRS Visualizer</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Segoe UI',system-ui,sans-serif;background:#0f172a;color:#e2e8f0;height:100vh;display:flex;flex-direction:column}
  header{padding:12px 20px;background:#1e293b;border-bottom:1px solid #334155;display:flex;align-items:center;gap:16px;flex-shrink:0}
  header h1{font-size:18px;font-weight:700;color:#f8fafc}
  header h1 span{color:#818cf8}
  .stats{display:flex;gap:10px;margin-left:auto;flex-wrap:wrap}
  .stat{background:#0f172a;border:1px solid #334155;border-radius:8px;padding:4px 12px;font-size:12px;display:flex;gap:6px;align-items:center}
  .stat b{color:#f8fafc}
  .main{display:flex;flex:1;overflow:hidden}
  #graph{flex:1;overflow:hidden;cursor:grab}
  #graph:active{cursor:grabbing}
  #sidebar{width:280px;background:#1e293b;border-left:1px solid #334155;overflow-y:auto;flex-shrink:0;padding:16px;display:flex;flex-direction:column;gap:12px}
  .legend h3,.panel h3{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:#94a3b8;margin-bottom:8px}
  .legend-row{display:flex;align-items:center;gap:8px;margin-bottom:6px;cursor:pointer;padding:4px 6px;border-radius:6px;transition:background .15s}
  .legend-row:hover{background:#0f172a}
  .legend-row input{cursor:pointer}
  .dot{width:14px;height:14px;border-radius:50%;flex-shrink:0}
  .legend-row span{font-size:13px}
  .panel{background:#0f172a;border-radius:8px;padding:12px}
  .panel p{font-size:12px;color:#94a3b8;margin-bottom:8px}
  #detail{min-height:120px}
  #detail .fname{font-size:15px;font-weight:600;color:#f8fafc;margin-bottom:4px}
  #detail .fmodule{font-size:11px;color:#64748b;margin-bottom:10px;word-break:break-all}
  #detail .badge{display:inline-block;border-radius:9999px;font-size:11px;padding:2px 10px;font-weight:600;margin-bottom:8px}
  .tag{display:inline-block;background:#1e293b;border:1px solid #334155;border-radius:4px;font-size:10px;padding:1px 6px;margin:2px}
  .rule-item{font-size:11px;color:#fbbf24;margin:2px 0}
  #search{width:100%;background:#0f172a;border:1px solid #334155;border-radius:6px;padding:6px 10px;color:#e2e8f0;font-size:13px;outline:none}
  #search:focus{border-color:#818cf8}
  #search::placeholder{color:#475569}
  .node circle{transition:r .2s,opacity .15s}
  .node text{pointer-events:none;user-select:none}
  .link{stroke:#334155;stroke-opacity:.7}
  .node.dimmed circle{opacity:.2}
  .node.dimmed text{opacity:.2}
  .link.dimmed{stroke-opacity:.08}
</style>
</head>
<body>
<header>
  <h1>Code2<span>Schema</span> — CQRS Visualizer</h1>
  <div class="stats" id="stats"></div>
</header>
<div class="main">
  <svg id="graph"></svg>
  <div id="sidebar">
    <div>
      <input id="search" type="text" placeholder="🔍 Szukaj funkcji...">
    </div>
    <div class="legend">
      <h3>Role CQRS</h3>
      <label class="legend-row"><input type="checkbox" checked data-role="query"><div class="dot" style="background:#4ade80"></div><span>🔍 Query</span></label>
      <label class="legend-row"><input type="checkbox" checked data-role="command"><div class="dot" style="background:#fb923c"></div><span>✏️ Command</span></label>
      <label class="legend-row"><input type="checkbox" checked data-role="orchestrator"><div class="dot" style="background:#a78bfa"></div><span>🔀 Orchestrator</span></label>
      <label class="legend-row"><input type="checkbox" checked data-role="unknown"><div class="dot" style="background:#94a3b8"></div><span>❓ Unknown</span></label>
    </div>
    <div class="panel">
      <h3>Szczegóły węzła</h3>
      <div id="detail"><p>Kliknij węzeł aby zobaczyć szczegóły</p></div>
    </div>
    <div class="panel">
      <h3>Reguły jakości</h3>
      <div id="rules-panel"><p>Brak naruszeń ✅</p></div>
    </div>
  </div>
</div>
<script>
const DATA = __GRAPH_DATA__;

// ── Stats bar ─────────────────────────────────────────────────────────────────
const s = DATA.stats;
document.getElementById('stats').innerHTML = [
  ['📦 Modules', s.modules],
  ['⚡ Functions', s.functions],
  ['🔍 Queries', s.queries],
  ['✏️ Commands', s.commands],
  ['🔀 Orchestrators', s.orchestrators],
  ['🔁 Workflows', s.workflows],
  ['⚠️ Rules', s.rules],
].map(([l,v])=>`<div class="stat">${l} <b>${v}</b></div>`).join('');

// ── Rules panel ───────────────────────────────────────────────────────────────
const rp = document.getElementById('rules-panel');
const rEntries = Object.entries(DATA.rules);
if(rEntries.length){
  rp.innerHTML = rEntries.map(([fn,ids])=>
    `<div class="rule-item">⚠️ <b>${fn}</b>: ${ids.join(', ')}</div>`
  ).join('');
}

// ── D3 Force Graph ────────────────────────────────────────────────────────────
const svg = d3.select('#graph');
const container = document.getElementById('graph');

let W = container.clientWidth, H = container.clientHeight;
svg.attr('width', W).attr('height', H);

const g = svg.append('g');

// Zoom
svg.call(d3.zoom().scaleExtent([0.1, 4]).on('zoom', e => g.attr('transform', e.transform)));

// Arrow marker
svg.append('defs').append('marker')
  .attr('id','arrow').attr('viewBox','0 -4 8 8').attr('refX',16).attr('refY',0)
  .attr('markerWidth',6).attr('markerHeight',6).attr('orient','auto')
  .append('path').attr('d','M0,-4L8,0L0,4').attr('fill','#475569');

const simulation = d3.forceSimulation(DATA.nodes)
  .force('link', d3.forceLink(DATA.links).id(d=>d.id).distance(80).strength(0.4))
  .force('charge', d3.forceManyBody().strength(-220))
  .force('center', d3.forceCenter(W/2, H/2))
  .force('collision', d3.forceCollide(d => nodeRadius(d) + 6));

function nodeRadius(d){
  if(d.role==='orchestrator') return 16 + Math.min(d.fan_out, 20);
  if(d.role==='command') return 10;
  return 8;
}

const link = g.append('g').selectAll('line')
  .data(DATA.links).join('line')
  .attr('class','link')
  .attr('stroke-width', 1.2)
  .attr('marker-end','url(#arrow)');

const node = g.append('g').selectAll('.node')
  .data(DATA.nodes).join('g')
  .attr('class','node')
  .call(d3.drag()
    .on('start',(e,d)=>{ if(!e.active) simulation.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; })
    .on('drag', (e,d)=>{ d.fx=e.x; d.fy=e.y; })
    .on('end',  (e,d)=>{ if(!e.active) simulation.alphaTarget(0); d.fx=null; d.fy=null; })
  )
  .on('click', onNodeClick)
  .on('mouseover', onNodeHover)
  .on('mouseout', onNodeOut);

node.append('circle')
  .attr('r', nodeRadius)
  .attr('fill', d=>d.color)
  .attr('stroke', '#0f172a')
  .attr('stroke-width', 2);

node.append('text')
  .attr('dy', d => nodeRadius(d) + 12)
  .attr('text-anchor','middle')
  .attr('font-size', 10)
  .attr('fill','#94a3b8')
  .text(d => d.name.length > 18 ? d.name.slice(0,17)+'…' : d.name);

simulation.on('tick', ()=>{
  link
    .attr('x1',d=>d.source.x).attr('y1',d=>d.source.y)
    .attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);
  node.attr('transform',d=>`translate(${d.x},${d.y})`);
});

// ── Hover ─────────────────────────────────────────────────────────────────────
function onNodeHover(e, d){
  const connected = new Set([d.id]);
  DATA.links.forEach(l=>{
    if(l.source.id===d.id||l.target.id===d.id){
      connected.add(l.source.id); connected.add(l.target.id);
    }
  });
  node.classed('dimmed', n => !connected.has(n.id));
  link.classed('dimmed', l => l.source.id!==d.id && l.target.id!==d.id);
}

function onNodeOut(){
  node.classed('dimmed', false);
  link.classed('dimmed', false);
}

// ── Click detail ──────────────────────────────────────────────────────────────
function onNodeClick(e, d){
  const roleColors={'query':'#4ade80','command':'#fb923c','orchestrator':'#a78bfa','unknown':'#94a3b8'};
  const rules = DATA.rules[d.name] || [];
  const sideEff = d.side_effects.filter(s=>s!=='none');
  document.getElementById('detail').innerHTML = `
    <div class="fname">${d.emoji} ${d.name}</div>
    <div class="fmodule">${d.module}</div>
    <span class="badge" style="background:${roleColors[d.role]}20;color:${roleColors[d.role]};border:1px solid ${roleColors[d.role]}40">${d.role.toUpperCase()}</span>
    ${d.is_async ? '<span class="badge" style="background:#0ea5e920;color:#38bdf8;border:1px solid #0ea5e940">async</span>' : ''}
    <div style="margin-top:8px;font-size:12px;color:#64748b">
      <div>Fan-out: <b style="color:#e2e8f0">${d.fan_out}</b></div>
      <div>Lines: <b style="color:#e2e8f0">${d.lines}</b></div>
      ${sideEff.length ? `<div style="margin-top:4px">Side effects:<br>${sideEff.map(s=>`<span class="tag">⚡${s}</span>`).join('')}</div>` : ''}
      ${rules.length ? `<div style="margin-top:6px;color:#fbbf24">${rules.map(r=>`⚠️ ${r}`).join('<br>')}</div>` : ''}
    </div>
  `;
}

// ── Search ────────────────────────────────────────────────────────────────────
const hidden = new Set();
document.getElementById('search').addEventListener('input', e=>{
  const q = e.target.value.trim().toLowerCase();
  if(!q){ node.classed('dimmed',false); link.classed('dimmed',false); return; }
  node.classed('dimmed', d => !d.name.toLowerCase().includes(q));
  link.classed('dimmed', l => !l.source.name.toLowerCase().includes(q) && !l.target.name.toLowerCase().includes(q));
});

// ── Legend filters ────────────────────────────────────────────────────────────
document.querySelectorAll('[data-role]').forEach(cb=>{
  cb.addEventListener('change', ()=>{
    const active = new Set([...document.querySelectorAll('[data-role]:checked')].map(c=>c.dataset.role));
    node.style('display', d => active.has(d.role) ? null : 'none');
    link.style('display', l => active.has(l.source.role) && active.has(l.target.role) ? null : 'none');
  });
});

// ── Resize ────────────────────────────────────────────────────────────────────
window.addEventListener('resize', ()=>{
  W = container.clientWidth; H = container.clientHeight;
  svg.attr('width',W).attr('height',H);
  simulation.force('center', d3.forceCenter(W/2,H/2)).alpha(0.3).restart();
});
</script>
</body>
</html>"""


def to_html(schema: SchemaIR) -> str:
    """Generuje interaktywny HTML z grafem CQRS."""
    data = _build_graph_data(schema)
    return _HTML_TEMPLATE.replace("__GRAPH_DATA__", json.dumps(data))


def write_html(schema: SchemaIR, path: Path) -> None:
    path.write_text(to_html(schema), encoding="utf-8")
