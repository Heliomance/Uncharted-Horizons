(() => {
  'use strict';
  const LOG = m => { try { window.__uhLog && window.__uhLog(m); } catch {} };
  const FAIL = m => { try { window.__uhFail && window.__uhFail(m); } catch {} };
  LOG('app start; parser ' + (typeof PARSER));
  const NODE_W = 176, NODE_H = 40, GX = 24, GY = 10, BAND_T = 30, BAND_B = 14, MAX_ROWS = 6, ERA_GAP = 56, LEFT = 210, TOP = 20;
  const ERA_COLOURS = { Primitive: '#a8742f', Ancient: '#b38b35', Classical: '#8c8b3a', Medieval: '#4d8758', 'Early Modern': '#2e8280', Modern: '#2f6d9e', Atomic: '#4a59ad', Space: '#6b4aa5', Interstellar: '#8a3f8d' };
  const WORLD_ABBR = { Atomic: 'At', Elemental: 'El', Substance: 'Su', Process: 'Pr', Germ: 'Ge', Miasma: 'Mi', Humoral: 'Hu', Caloric: 'Ca', Vitalist: 'Vi', Gravitic: 'Gr' };
  const TIER_RANK = { CORE: 0, STANDARD: 1, UNCOMMON: 2, RARE: 3, UNIQUE: 4 };
  const POS_KEY = 'uh-techtree:positions';
  const SVGNS = 'http://www.w3.org/2000/svg';
  const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = s => document.querySelector(s);
  const el = (tag, attrs = {}, parent) => { const n = document.createElementNS(SVGNS, tag); for (const k in attrs) n.setAttribute(k, attrs[k]); if (parent) parent.appendChild(n); return n; };

  const svg = $('#graph'), world = $('#world'), stage = $('#stage');
  const layers = { eras: $('#layer-eras'), bands: $('#layer-bands'), edges: $('#layer-edges'), nodes: $('#layer-nodes') };
  const ribbon = $('#ribbon'), lanes = $('#lanes');
  const state = {
    doc: null, source: null, view: { x: 0, y: 0, k: 0.5 }, pos: new Map(), home: new Map(), nodeEls: new Map(), edgeEls: [], byNode: new Map(), echoes: [],
    selected: null, hover: null, latest: null, lineage: false, edgeMode: 'all', world: 'all', tiers: new Set(Object.keys(TIER_RANK)), layout: null,
  };

  // ---------- storage (a per-viewer convenience: moved nodes) ----------
  function loadSaved() { try { return JSON.parse(localStorage.getItem(POS_KEY) || '{}') || {}; } catch { return {}; } }
  function saveMoved() {
    const out = {};
    for (const [id, p] of state.pos) { const h = state.home.get(id); if (h && (Math.abs(h.x - p.x) > 0.5 || Math.abs(h.y - p.y) > 0.5)) out[id] = [Math.round(p.x), Math.round(p.y)]; }
    try { localStorage.setItem(POS_KEY, JSON.stringify(out)); } catch { /* storage unavailable: positions last for this visit */ }
    $('#reset').disabled = !Object.keys(out).length;
  }

  // ---------- layout: focus bands × era columns, in an order the solver chose ----------
  const G = { NODE_W, NODE_H, GX, GY, BAND_T, BAND_B, MAX_ROWS, ERA_GAP, LEFT, TOP };
  const ORDER_KEY = 'uh-techtree:order';
  function layoutFor(order) {
    const M = state.model, L = SOLVER.place(M, order); const echoes = [];
    for (const gs of order.cells.values()) for (const g of gs) for (const en of g) if (en.echo) echoes.push(en);
    return { eras: M.eras, eraX: L.eraX, eraW: L.eraW, bandY: L.bandY, bandH: L.bandH, width: L.width, height: L.height, home: L.pos, echoes, bands: order.bands };
  }
  function currentOrder() { return state.orderMode === 'document' ? state.orders.document : state.orders.opening; }
  function applyOrder(keepView) {
    const order = currentOrder(); state.order = order; state.layout = layoutFor(order); state.home = state.layout.home;
    const saved = loadSaved(); state.pos = new Map();
    for (const [id, h] of state.home) state.pos.set(id, saved[id] ? { x: saved[id][0], y: saved[id][1] } : { ...h });
    $('#reset').disabled = !Object.keys(saved).some(id => state.home.has(id));
    render(); if (!keepView) fit();
    if (state.selected) showPanel(state.selected);
  }


  // ---------- rendering ----------
  function edgePath(a, b) {
    const sx = a.x + NODE_W, sy = a.y + NODE_H / 2, tx = b.x, ty = b.y + NODE_H / 2;
    const dx = tx - sx;
    const c = dx > 0 ? Math.max(28, dx * 0.5) : 70 + Math.min(240, -dx * 0.25);
    return `M${sx},${sy} C${sx + c},${sy} ${tx - c},${ty} ${tx},${ty}`;
  }
  function echoPath(a, b) {
    const ay = a.y + NODE_H / 2, by = b.y + NODE_H / 2;
    if (Math.abs(a.x - b.x) < NODE_W) { const sx = a.x + NODE_W, tx = b.x + NODE_W, c = 50 + Math.abs(ay - by) * 0.08; return `M${sx},${ay} C${sx + c},${ay} ${tx + c},${by} ${tx},${by}`; }
    const [l, r, ly, ry] = a.x < b.x ? [a, b, ay, by] : [b, a, by, ay];
    const sx = l.x + NODE_W, tx = r.x, c = Math.max(40, (tx - sx) / 2);
    return `M${sx},${ly} C${sx + c},${ly} ${tx - c},${ry} ${tx},${ry}`;
  }
  function render() {
    const doc = state.doc, L = state.layout;
    Object.values(layers).forEach(g => g.replaceChildren());
    state.nodeEls.clear(); state.edgeEls = []; state.byNode.clear();
    for (const e of L.eras) {
      el('rect', { x: L.eraX[e] - ERA_GAP / 2, y: 0, width: L.eraW[e] + ERA_GAP, height: L.height, fill: ERA_COLOURS[e] || '#777', class: 'era-tint' }, layers.eras);
    }
    L.bands.forEach((name, i) => {
      el('rect', { x: 0, y: L.bandY[name], width: L.width, height: L.bandH[name], class: 'band' + (i % 2 ? ' band-alt' : '') }, layers.bands);
      el('line', { x1: 0, x2: L.width, y1: L.bandY[name], y2: L.bandY[name], class: 'band-rule' }, layers.bands);
    });
    doc.edges.forEach((e, i) => {
      if (!doc.rows.has(e.from) || !doc.rows.has(e.to)) return;
      const p = el('path', { class: 'edge' + (e.alt ? ' alt' : ''), d: edgePath(state.pos.get(e.from), state.pos.get(e.to)), 'marker-end': 'url(#arrow)' }, layers.edges);
      const rec = { ...e, el: p, i }; state.edgeEls.push(rec);
      for (const n of [e.from, e.to]) (state.byNode.get(n) || state.byNode.set(n, []).get(n)).push(rec);
    });
    state.echoes = [];
    for (const en of L.echoes) {
      const r = en.row, p = state.pos.get(en.key), h = state.pos.get(r.id);
      const link = el('path', { class: 'echo', d: echoPath(p, h) }, layers.edges);
      const g = el('g', { class: 'node echo-node', transform: `translate(${p.x},${p.y})`, 'data-id': r.id, 'data-key': en.key }, layers.nodes);
      el('title', {}, g).textContent = `${r.id} ${r.name}: also reachable through ${en.focus}; its home is ${r.focus}`;
      el('rect', { class: 'body', width: NODE_W, height: NODE_H, rx: 7 }, g);
      el('text', { class: 'nid', x: 10, y: 15 }, g).textContent = '↗ ' + r.id;
      el('text', { class: 'nfrom', x: NODE_W - 9, y: 15, 'text-anchor': 'end' }, g).textContent = 'home: ' + (r.focus.length > 16 ? r.focus.slice(0, 15) + '…' : r.focus);
      el('text', { class: 'nname', x: 10, y: 31 }, g).textContent = r.name.length > 25 ? r.name.slice(0, 24).trimEnd() + '…' : r.name;
      state.echoes.push({ key: en.key, id: r.id, focus: en.focus, g, link });
    }
    for (const r of doc.rows.values()) {
      const p = state.pos.get(r.id);
      const g = el('g', { class: `node tier-${r.tier}`, transform: `translate(${p.x},${p.y})`, 'data-id': r.id, 'data-key': r.id }, layers.nodes);
      el('title', {}, g).textContent = `${r.id} ${r.name} (${r.tier.toLowerCase()}, ${r.era})`;
      el('rect', { class: 'body', width: NODE_W, height: NODE_H, rx: 7 }, g);
      if (r.tier === 'RARE') el('rect', { class: 'inner', x: 3, y: 3, width: NODE_W - 6, height: NODE_H - 6, rx: 5 }, g);
      if (r.tier === 'UNIQUE') el('circle', { class: 'seal', cx: NODE_W - 10, cy: 10, r: 4 }, g);
      el('text', { class: 'nid', x: 10, y: 15 }, g).textContent = r.id;
      const name = r.name.length > 25 ? r.name.slice(0, 24).trimEnd() + '…' : r.name;
      el('text', { class: 'nname', x: 10, y: 31 }, g).textContent = name;
      if (r.world) el('text', { class: 'nworld', x: NODE_W - (r.tier === 'UNIQUE' ? 20 : 9), y: 15, 'text-anchor': 'end' }, g).textContent = WORLD_ABBR[r.world] || r.world.slice(0, 2);
      if (r.alsoIn && r.alsoIn.length) { const b = el('text', { class: 'nalso', x: NODE_W - 9, y: 32, 'text-anchor': 'end' }, g); b.textContent = '+' + r.alsoIn.length; el('title', {}, b).textContent = 'Also reachable through ' + r.alsoIn.join(' and '); }
      if (r.dualIssues && r.dualIssues.length) g.classList.add('dual-issue');
      state.nodeEls.set(r.id, g);
    }
    buildOverlays(); applyView(); restyle();
  }
  function buildOverlays() {
    const L = state.layout;
    ribbon.replaceChildren(); lanes.replaceChildren();
    for (const e of L.eras) {
      const d = document.createElement('div'); d.className = 'era'; d.style.background = ERA_COLOURS[e] || '#777';
      d.dataset.era = e; d.innerHTML = `<span>${e}</span>`; ribbon.appendChild(d);
    }
    const byName = new Map(state.doc.foci.map(f => [f.name, f]));
    for (const name of L.bands) {
      const f = byName.get(name);
      const d = document.createElement('div'); d.className = 'lane'; d.dataset.focus = f.name;
      d.innerHTML = `<span class="icon" aria-hidden="true">${f.icon}</span><span class="lname">${esc(f.name)}</span>`;
      lanes.appendChild(d);
    }
  }
  function applyView() {
    const v = state.view, L = state.layout; if (!L) return;
    world.setAttribute('transform', `translate(${v.x},${v.y}) scale(${v.k})`);
    for (const d of ribbon.children) {
      const e = d.dataset.era, x = (L.eraX[e] - ERA_GAP / 2) * v.k + v.x, w = (L.eraW[e] + ERA_GAP) * v.k;
      d.style.transform = `translateX(${x}px)`; d.style.width = w + 'px'; d.classList.toggle('narrow', w < 90);
    }
    const RIB = 30;
    for (const d of lanes.children) {
      const f = d.dataset.focus, top = L.bandY[f] * v.k + v.y, h = L.bandH[f] * v.k;
      const fs = Math.max(9.5, Math.min(13, 9 + v.k * 6)), lh = fs * 1.35 + 6;
      d.style.fontSize = fs + 'px';
      const w = d.offsetWidth || 150;
      const x = Math.max(4, v.x + LEFT * v.k - w - 6);
      const y = Math.min(Math.max(top + 4, RIB + 4), top + h - lh - 2);
      d.style.transform = `translate(${x}px, ${y}px)`;
      d.classList.toggle('gone', h < lh - 2 || top + h < RIB || top > svg.clientHeight);
    }
    $('#zoom-level').textContent = Math.round(v.k * 100) + '%';
  }

  // ---------- highlighting ----------
  function walk(start, dir) {
    const seen = new Set(); const stack = [start];
    while (stack.length) { const n = stack.pop(); for (const e of state.byNode.get(n) || []) { const m = dir === 'up' ? (e.to === n ? e.from : null) : (e.from === n ? e.to : null); if (m && !seen.has(m)) { seen.add(m); stack.push(m); } } }
    return seen;
  }
  function visible(r) { return PARSER.inWorld(r, state.world) && state.tiers.has(r.tier); }
  function restyle() {
    const doc = state.doc; if (!doc) return;
    const focus = state.selected || state.hover;
    let up = new Set(), down = new Set();
    if (focus && state.selected && state.lineage) { up = walk(focus, 'up'); down = walk(focus, 'down'); }
    for (const [id, g] of state.nodeEls) {
      const r = doc.rows.get(id); const shown = visible(r);
      g.classList.toggle('absent', !shown);
      g.classList.toggle('selected', id === state.selected);
      const near = focus && (state.byNode.get(focus) || []).some(e => (e.from === id && e.to === focus) || (e.to === id && e.from === focus));
      g.classList.toggle('related', !!(focus && (near || up.has(id) || down.has(id) || id === focus)));
      g.classList.toggle('faded', !!(state.selected && !(near || up.has(id) || down.has(id) || id === focus)));
    }
    for (const ec of state.echoes) {
      const home = state.nodeEls.get(ec.id), shown = visible(doc.rows.get(ec.id));
      for (const c of ['absent', 'faded', 'related']) ec.g.classList.toggle(c, home.classList.contains(c));
      ec.g.classList.toggle('selected', ec.id === state.selected);
      const on = shown && focus === ec.id;
      ec.link.setAttribute('class', 'echo' + (!shown ? ' hidden' : on ? ' on' : (state.selected || state.edgeMode === 'selected') ? ' quiet' : ''));
    }
    for (const e of state.edgeEls) {
      const a = doc.rows.get(e.from), b = doc.rows.get(e.to);
      const shown = visible(a) && visible(b);
      let cls = 'edge' + (e.alt ? ' alt' : '');
      let mark = 'arrow';
      if (!shown) cls += ' hidden';
      else if (focus && e.to === focus) { cls += ' in'; mark = 'arrow-in'; }
      else if (focus && e.from === focus) { cls += ' out'; mark = 'arrow-out'; }
      else if (state.selected && state.lineage && up.has(e.to) && up.has(e.from)) { cls += ' in far'; mark = 'arrow-in'; }
      else if (state.selected && state.lineage && down.has(e.from) && down.has(e.to)) { cls += ' out far'; mark = 'arrow-out'; }
      else if (state.selected || state.edgeMode === 'selected') cls += ' quiet';
      e.el.setAttribute('class', cls); e.el.setAttribute('marker-end', `url(#${mark})`);
    }
  }

  // ---------- details panel ----------
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  function fmt(s) {
    return esc(s).replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>').replace(/(^|[^*])\*([^*]+)\*/g, '$1<em>$2</em>').replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/⟨([^⟩]*)⟩/g, '<span class="uq">⟨$1⟩</span>');
  }
  function chip(id) {
    const r = state.doc.rows.get(id);
    if (!r) return `<span class="chip missing" title="Not a row in this version">${esc(id)}</span>`;
    return `<button class="chip t-${r.tier}${PARSER.inWorld(r, state.world) ? '' : ' off'}" data-go="${esc(id)}" title="${esc(r.name)}">${esc(id)} <span>${esc(r.name)}</span></button>`;
  }
  function showPanel(id) {
    const r = state.doc.rows.get(id); const panel = $('#panel');
    if (!r) { panel.hidden = true; return; }
    const deps = state.edgeEls.filter(e => e.from === id).map(e => e.to).filter((v, i, a) => a.indexOf(v) === i);
    const pre = r.pre.length ? r.pre.map(g => `<li>${g.map(o => o.map(chip).join(' <i>and</i> ')).join(' <i>or</i> ')}</li>`).join('') : '<li class="none">None</li>';
    $('#p-id').textContent = r.id;
    $('#p-name').textContent = r.name;
    $('#p-meta').innerHTML = `<span class="tierbadge t-${r.tier}">${r.tier.charAt(0) + r.tier.slice(1).toLowerCase()}</span><span>${esc(r.era)}</span><span>${esc(r.focus)}</span>${r.world ? `<span class="wtag">${esc(r.world)} worlds</span>` : ''}`;
    const also = r.alsoIn || [];
    $('#p-also').innerHTML = also.length ? `Reachable through ${[r.focus, ...also].map((f, i) => `<b>${esc(f)}</b>${i ? '' : ' (its home)'}`).join(also.length > 1 ? ', ' : ' and ').replace(/, ([^,]*)$/, ' and $1')}.` : '';
    $('#p-also').hidden = !also.length;
    $('#p-issues').innerHTML = (r.dualIssues || []).map(t => `<li>${esc(t.charAt(0).toUpperCase() + t.slice(1))}.</li>`).join('');
    $('#p-issues-wrap').hidden = !(r.dualIssues && r.dualIssues.length);
    $('#p-pre').innerHTML = pre;
    $('#p-pretext').textContent = r.preText;
    $('#p-deps').innerHTML = deps.length ? deps.map(chip).join(' ') : '<span class="none">Nothing yet</span>';
    $('#p-unlocks').innerHTML = fmt(r.unlocks);
    $('#p-notes').innerHTML = r.notes ? fmt(r.notes) : '';
    $('#p-notes-wrap').hidden = !r.notes;
    panel.hidden = false;
  }
  function select(id, centre) {
    state.selected = id; state.hover = null;
    if (id) { showPanel(id); if (centre) centreOn(id); } else $('#panel').hidden = true;
    restyle();
  }

  // ---------- view: pan, zoom, fit ----------
  function clampK(k) { return Math.min(2.5, Math.max(0.05, k)); }
  function zoomAt(px, py, factor) {
    const v = state.view, k = clampK(v.k * factor), f = k / v.k;
    v.x = px - (px - v.x) * f; v.y = py - (py - v.y) * f; v.k = k; state.moved = true; applyView();
  }
  function fit() {
    const L = state.layout; if (!L) return;
    const r = svg.getBoundingClientRect(), top = 38, bottom = 56;
    const k = clampK(Math.min((r.width - 24) / L.width, (r.height - top - bottom) / L.height));
    state.view = { k, x: (r.width - L.width * k) / 2, y: top + (r.height - top - bottom - L.height * k) / 2 }; applyView();
  }
  function centreOn(id) {
    const p = state.pos.get(id), r = svg.getBoundingClientRect(); const v = state.view; state.moved = true;
    const panel = $('#panel'); let w = r.width, h = r.height;
    if (!panel.hidden) { const pr = panel.getBoundingClientRect(); if (pr.width < r.width * 0.9) w = pr.left - r.left; else h = pr.top - r.top; }
    const k = Math.max(v.k, 0.7); const target = { k, x: w / 2 - (p.x + NODE_W / 2) * k, y: 30 + (h - 30) / 2 - (p.y + NODE_H / 2) * k };
    if (reduceMotion) { state.view = target; applyView(); return; }
    const from = { ...v }, t0 = performance.now();
    const step = t => { const a = Math.min(1, (t - t0) / 350), e = a * (2 - a); state.view = { k: from.k + (target.k - from.k) * e, x: from.x + (target.x - from.x) * e, y: from.y + (target.y - from.y) * e }; applyView(); if (a < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  }
  const pointers = new Map(); let drag = null;
  function toGraph(cx, cy) { const r = svg.getBoundingClientRect(), v = state.view; return { x: (cx - r.left - v.x) / v.k, y: (cy - r.top - v.y) / v.k }; }
  svg.addEventListener('pointerdown', ev => {
    if (!state.doc) return;
    try { svg.setPointerCapture(ev.pointerId); } catch { /* not an active pointer: carry on without capture */ }
    pointers.set(ev.pointerId, { x: ev.clientX, y: ev.clientY });
    const node = ev.target.closest('.node');
    if (pointers.size === 2) { drag = { kind: 'pinch', d: dist(), k: state.view.k }; return; }
    if (node) { const id = node.dataset.id, key = node.dataset.key || id, g = toGraph(ev.clientX, ev.clientY), p = state.pos.get(key); drag = { kind: 'node', id, key, el: node, ox: g.x - p.x, oy: g.y - p.y, sx: ev.clientX, sy: ev.clientY, moved: false }; }
    else drag = { kind: 'pan', sx: ev.clientX, sy: ev.clientY, vx: state.view.x, vy: state.view.y, moved: false };
  });
  function dist() { const [a, b] = [...pointers.values()]; return Math.hypot(a.x - b.x, a.y - b.y) || 1; }
  function mid() { const [a, b] = [...pointers.values()]; const r = svg.getBoundingClientRect(); return { x: (a.x + b.x) / 2 - r.left, y: (a.y + b.y) / 2 - r.top }; }
  svg.addEventListener('pointermove', ev => {
    if (pointers.has(ev.pointerId)) pointers.set(ev.pointerId, { x: ev.clientX, y: ev.clientY });
    if (!drag) {
      const node = ev.target.closest && ev.target.closest('.node'); const id = node ? node.dataset.id : null;
      if (!state.selected && id !== state.hover) { state.hover = id; restyle(); }
      return;
    }
    if (drag.kind === 'pinch' && pointers.size === 2) { const m = mid(); zoomAt(m.x, m.y, (drag.k * dist() / drag.d) / state.view.k); return; }
    const far = Math.hypot(ev.clientX - drag.sx, ev.clientY - drag.sy) > 4;
    if (drag.kind === 'pan') { if (far) { drag.moved = true; state.moved = true; } state.view.x = drag.vx + ev.clientX - drag.sx; state.view.y = drag.vy + ev.clientY - drag.sy; applyView(); }
    if (drag.kind === 'node' && (drag.moved || far)) {
      drag.moved = true; svg.classList.add('dragging');
      const g = toGraph(ev.clientX, ev.clientY), p = { x: g.x - drag.ox, y: g.y - drag.oy };
      state.pos.set(drag.key, p); drag.el.setAttribute('transform', `translate(${p.x},${p.y})`);
      if (drag.key === drag.id) for (const e of state.byNode.get(drag.id) || []) e.el.setAttribute('d', edgePath(state.pos.get(e.from), state.pos.get(e.to)));
      for (const ec of state.echoes) if (ec.key === drag.key || (drag.key === drag.id && ec.id === drag.id)) ec.link.setAttribute('d', echoPath(state.pos.get(ec.key), state.pos.get(ec.id)));
    }
  });
  const endPointer = ev => {
    pointers.delete(ev.pointerId);
    if (!drag) return;
    if (drag.kind === 'node') { if (drag.moved) saveMoved(); else select(drag.id === state.selected ? null : drag.id); }
    if (drag.kind === 'pan' && !drag.moved) select(null);
    svg.classList.remove('dragging');
    drag = pointers.size ? drag : null; if (drag && drag.kind === 'pinch') drag = null;
  };
  svg.addEventListener('pointerup', endPointer); svg.addEventListener('pointercancel', endPointer);
  svg.addEventListener('pointerleave', () => { if (!drag && state.hover && !state.selected) { state.hover = null; restyle(); } });
  svg.addEventListener('wheel', ev => {
    if (!state.doc) return; ev.preventDefault();
    const r = svg.getBoundingClientRect();
    if (ev.ctrlKey || ev.metaKey) zoomAt(ev.clientX - r.left, ev.clientY - r.top, Math.exp(-ev.deltaY * (ev.deltaMode ? 0.05 : 0.0025)));
    else { state.view.x -= ev.shiftKey && !ev.deltaX ? ev.deltaY : ev.deltaX; state.view.y -= ev.shiftKey && !ev.deltaX ? 0 : ev.deltaY; applyView(); }
  }, { passive: false });
  const centreZoom = f => { const r = svg.getBoundingClientRect(); zoomAt(r.width / 2, r.height / 2, f); };
  $('#zin').onclick = () => centreZoom(1.25); $('#zout').onclick = () => centreZoom(0.8); $('#fit').onclick = fit;
  window.addEventListener('keydown', ev => {
    if (ev.target.closest('input, select, textarea')) { if (ev.key === 'Escape') ev.target.blur(); return; }
    if (ev.key === '/') { ev.preventDefault(); $('#search').focus(); }
    else if (ev.key === '+' || ev.key === '=') centreZoom(1.25);
    else if (ev.key === '-') centreZoom(0.8);
    else if (ev.key === '0') fit();
    else if (ev.key === 'Escape') select(null);
    else if (ev.key.startsWith('Arrow')) { const s = 80; state.view.x += ev.key === 'ArrowLeft' ? s : ev.key === 'ArrowRight' ? -s : 0; state.view.y += ev.key === 'ArrowUp' ? s : ev.key === 'ArrowDown' ? -s : 0; applyView(); }
  });
  window.addEventListener('resize', () => applyView());

  // ---------- controls ----------
  $('#panel').addEventListener('click', ev => { const b = ev.target.closest('[data-go]'); if (b) select(b.dataset.go, true); });
  $('#p-close').onclick = () => select(null);
  $('#lineage').onchange = ev => { state.lineage = ev.target.checked; restyle(); };
  $('#edge-mode').onchange = ev => { state.edgeMode = ev.target.value; restyle(); };
  $('#world-sel').onchange = ev => { state.world = ev.target.value; restyle(); if (state.selected) showPanel(state.selected); };
  document.querySelectorAll('#tiers input').forEach(cb => cb.onchange = () => { cb.checked ? state.tiers.add(cb.value) : state.tiers.delete(cb.value); restyle(); });
  $('#reset').onclick = () => { try { localStorage.removeItem(POS_KEY); } catch {} if (state.doc) applyOrder(true); $('#reset').disabled = true; };
  $('#tools-toggle').onclick = () => { const open = document.body.classList.toggle('tools-open'); $('#tools-toggle').setAttribute('aria-expanded', String(open)); };
  $('#legend-toggle').onclick = () => { const l = $('#legend'); const open = l.hidden; l.hidden = !open; $('#legend-toggle').setAttribute('aria-expanded', String(open)); };
  // search
  const search = $('#search'), results = $('#results'); let hits = [], hi = 0;
  function runSearch() {
    const q = search.value.trim().toLowerCase(); results.replaceChildren(); hits = [];
    if (!q || !state.doc) { results.hidden = true; return; }
    for (const r of state.doc.rows.values()) { const s = r.id.toLowerCase().startsWith(q) ? 0 : r.name.toLowerCase().startsWith(q) ? 1 : r.name.toLowerCase().includes(q) ? 2 : -1; if (s >= 0) hits.push([s, r]); }
    hits.sort((a, b) => a[0] - b[0] || a[1].id.localeCompare(b[1].id, undefined, { numeric: true })); hits = hits.slice(0, 12).map(h => h[1]); hi = 0;
    if (!hits.length) { results.innerHTML = '<li class="none">No breakthrough matches</li>'; results.hidden = false; return; }
    hits.forEach((r, i) => { const li = document.createElement('li'); li.setAttribute('role', 'option'); li.dataset.id = r.id; li.innerHTML = `<b>${esc(r.id)}</b> ${esc(r.name)} <small>${esc(r.focus)}${r.alsoIn && r.alsoIn.length ? ' (also ' + r.alsoIn.map(esc).join(', ') + ')' : ''}, ${esc(r.era)}</small>`; if (i === hi) li.classList.add('hi'); results.appendChild(li); });
    results.hidden = false;
  }
  function pick(id) { results.hidden = true; search.value = ''; select(id, true); }
  search.addEventListener('input', runSearch);
  search.addEventListener('keydown', ev => {
    if (ev.key === 'ArrowDown' || ev.key === 'ArrowUp') { ev.preventDefault(); hi = (hi + (ev.key === 'ArrowDown' ? 1 : hits.length - 1)) % Math.max(1, hits.length); [...results.children].forEach((li, i) => li.classList.toggle('hi', i === hi)); }
    else if (ev.key === 'Enter' && hits[hi]) pick(hits[hi].id);
  });
  results.addEventListener('pointerdown', ev => { const li = ev.target.closest('li[data-id]'); if (li) { ev.preventDefault(); pick(li.dataset.id); } });
  search.addEventListener('blur', () => setTimeout(() => results.hidden = true, 120));

  // ---------- loading ----------
  function status(msg, kind) { const s = $('#status'); s.textContent = msg; s.dataset.kind = kind || ''; }
  function toast(msg) { const t = $('#toast'); t.textContent = msg; t.hidden = false; clearTimeout(toast.t); toast.t = setTimeout(() => t.hidden = true, 3200); }
  async function load(text, source) {
    let doc;
    try { doc = PARSER.parseDocument(text); } catch (err) { status('That file could not be read as the design document.', 'error'); showEmpty(true); return; }
    if (!doc.rows.size) { status('No breakthrough tables were found in that file. Open the tech tree design document.', 'error'); showEmpty(true); return; }
    const first = !state.doc; const prevVersion = state.doc && state.doc.version;
    // bands in the order their foci open; nodes within a cell in the document's order, CORE first
    state.model = SOLVER.model(doc, PARSER.ERAS, G);
    const D = SOLVER.documentOrder(state.model);
    state.orders = { document: D, opening: { bands: PARSER.openingOrder(doc).map(f => f.name), cells: D.cells } };
    state.doc = doc; state.source = source;
    if (state.selected && !doc.rows.has(state.selected)) state.selected = null;
    applyOrder(true); showEmpty(false);
    if (first || prevVersion !== doc.version) { requestAnimationFrame(() => { fit(); if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { if (!state.moved) fit(); }); }); }
    LOG(`loaded ${doc.version} from ${source.kind}: ${doc.rows.size} rows, ${doc.edges.length} links`);
    const where = source.kind === 'latest' ? 'the latest saved version' : `from ${source.name}`;
    $('#latest-btn').hidden = !(source.kind === 'file' && state.latest);
    $('#version').textContent = doc.version || 'version unknown';
    const multi = [...doc.rows.values()].filter(r => r.alsoIn && r.alsoIn.length).length;
    state.where = where; state.multi = multi; showSummary();
    if (!first && prevVersion !== doc.version) toast(`Now showing ${doc.version || 'the new version'}`);
  }
  function showSummary() {
    const d = state.doc; status(`${d.rows.size} breakthroughs in ${d.foci.length} focus areas, ${state.multi} reachable through more than one, ${state.edgeEls.length} links, ${state.where}`, '');
  }
  try { state.orderMode = localStorage.getItem(ORDER_KEY) === 'document' ? 'document' : 'opening'; } catch { state.orderMode = 'opening'; }
  $('#order-sel').value = state.orderMode;
  $('#order-sel').onchange = ev => { state.orderMode = ev.target.value; try { localStorage.setItem(ORDER_KEY, state.orderMode); } catch {} if (state.doc) { applyOrder(true); showSummary(); } };
  function showEmpty(on) { $('#empty').hidden = !on; }
  async function readFile(file) {
    if (!file) return;
    try { const text = await file.text(); load(text, { kind: 'file', name: file.name }); }
    catch { status(`Couldn't read ${file.name}.`, 'error'); }
  }
  $('#file').addEventListener('change', ev => readFile(ev.target.files[0]));
  $('#file2').addEventListener('change', ev => readFile(ev.target.files[0]));
  ['dragenter', 'dragover'].forEach(t => stage.addEventListener(t, ev => { ev.preventDefault(); stage.classList.add('drop'); }));
  ['dragleave', 'drop'].forEach(t => stage.addEventListener(t, ev => { ev.preventDefault(); stage.classList.remove('drop'); }));
  stage.addEventListener('drop', ev => readFile(ev.dataTransfer.files[0]));

  async function loadLatest() {
    const d = state.latest; if (!d) return;
    try {
      status(`Loading ${d.version || 'the latest version'}…`);
      const res = await fetch('/_blob/' + d.assetId);
      LOG(`fetch /_blob/${d.assetId}: HTTP ${res.status}, ${res.headers.get('content-type')}`);
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const text = await res.text(); LOG(`fetched ${text.length} characters`);
      load(text, { kind: 'latest', version: d.version });
    } catch (err) { FAIL(`fetch failed: ${err && err.message}`); status(`Couldn't load the latest version (${err.message}). Open a file instead.`, 'error'); if (!state.doc) showEmpty(true); }
  }
  async function connect() {
    status('Looking for the latest saved version…');
    setTimeout(() => { if (!state.doc) { LOG('timeout: nothing loaded after 12 s'); status('The latest saved version has not arrived. Open a file instead.', 'error'); showEmpty(true); } }, 12000);
    let db = null;
    try { db = window.claude && window.claude.use ? await window.claude.use('db') : null; } catch (err) { LOG('use(db) rejected: ' + (err && (err.code || err.message))); db = null; }
    LOG('db ' + (db ? 'available: ' + Object.keys(db).join(',') : 'null'));
    state.db = db;
    if (!db) { status('Open the design document to see its tree.'); showEmpty(true); return; }
    let lastAsset = null;
    $('#latest-btn').onclick = () => loadLatest();
    try {
      db.doc('meta/latest').onSnapshot(async snap => {
        LOG('snapshot: exists ' + (snap && snap.exists) + (snap && snap.exists ? ', fields ' + Object.keys(snap.data() || {}).join(',') : ''));
        if (!snap.exists) { if (!state.doc) { status('No version has been saved to this viewer yet. Open a file to see one.'); showEmpty(true); } return; }
        const d = snap.data() || {};
        if (!d.assetId || d.assetId === lastAsset) return;
        lastAsset = d.assetId; state.latest = d;
        if (state.source && state.source.kind === 'file') { $('#latest-btn').hidden = false; toast(`${d.version || 'A new version'} has been saved. Use Show latest to see it.`); return; }
        loadLatest();
      }, err => { LOG('snapshot error: ' + (err && (err.code || err.message))); if (!state.doc) { status('The saved versions are unavailable here. Open a file instead.'); showEmpty(true); } });
    } catch (err) { FAIL('subscribe failed: ' + (err && err.message)); status('Open the design document to see its tree.'); showEmpty(true); }
  }
  connect();
})();
