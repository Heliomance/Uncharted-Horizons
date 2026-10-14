// Layout for the tech-tree viewer: focus bands as rows, eras as columns, every node in its own band and era. An order
// names the bands top to bottom and the nodes inside each focus-and-era cell; place() turns an order into positions.
const SOLVER = (() => {
  const TIER_RANK = { CORE: 0, STANDARD: 1, UNCOMMON: 2, RARE: 3, UNIQUE: 4 };
  function model(doc, ERAS, G) {
    const rows = [...doc.rows.values()];
    const eras = ERAS.filter(e => rows.some(r => r.era === e));
    const names = new Set(doc.foci.map(f => f.name));
    const entries = rows.map(r => ({ key: r.id, row: r, focus: r.focus, era: r.era, echo: false }));
    for (const r of rows) for (const f of r.alsoIn || []) if (names.has(f)) entries.push({ key: `echo:${r.id}:${f}`, row: r, focus: f, era: r.era, echo: true });
    const cells = new Map(); const ck = (f, e) => f + '|' + e;
    for (const en of entries) { const k = ck(en.focus, en.era); (cells.get(k) || cells.set(k, []).get(k)).push(en); }
    // depth columns inside each cell: a same-cell prerequisite sits to the left of its dependent
    const groups = new Map();          // cell key → [[entry…] per depth]
    for (const [k, list] of cells) {
      const ids = new Set(list.filter(e => !e.echo).map(e => e.row.id)); const depth = new Map();
      const d = (r, seen = new Set()) => {
        if (depth.has(r.id)) return depth.get(r.id); if (seen.has(r.id)) return 0; seen.add(r.id);
        let m = -1; for (const g of r.pre) for (const o of g) for (const p of o) if (ids.has(p)) m = Math.max(m, d(doc.rows.get(p), seen));
        depth.set(r.id, m + 1); return m + 1;
      };
      list.forEach(en => { if (!en.echo) d(en.row); });
      const byDepth = [];
      for (const en of list) (byDepth[en.echo ? 0 : depth.get(en.row.id)] ||= []).push(en);
      groups.set(k, byDepth.filter(Boolean));
    }
    const edges = [];
    for (const e of doc.edges) if (doc.rows.has(e.from) && doc.rows.has(e.to) && e.from !== e.to) edges.push([e.from, e.to]);
    return { eras, foci: doc.foci.map(f => f.name), groups, edges, ck, G };
  }
  /** document order: bands as in the document, cells by tier then ID (echoes last) */
  function documentOrder(M) {
    const cellOrder = new Map();
    for (const [k, gs] of M.groups) cellOrder.set(k, gs.map(g => [...g].sort((a, b) => (a.echo - b.echo) || TIER_RANK[a.row.tier] - TIER_RANK[b.row.tier] || a.row.id.localeCompare(b.row.id, undefined, { numeric: true }))));
    return { bands: [...M.foci], cells: cellOrder };
  }
  function place(M, O) {
    const { NODE_W, NODE_H, GX, GY, BAND_T, BAND_B, MAX_ROWS, ERA_GAP, LEFT, TOP } = M.G;
    const dims = new Map(); const slot = new Map();
    for (const [k, gs] of O.cells) {
      let col = 0, rows = 0;
      for (const g of gs) for (let i = 0; i < g.length; i += MAX_ROWS) { const ch = g.slice(i, i + MAX_ROWS); ch.forEach((en, j) => slot.set(en.key, { k, col, row: j })); rows = Math.max(rows, ch.length); col++; }
      dims.set(k, { cols: col, rows });
    }
    const eraX = {}, eraW = {}; let x = LEFT;
    for (const e of M.eras) { const cols = Math.max(1, ...M.foci.map(f => (dims.get(M.ck(f, e)) || { cols: 0 }).cols)); eraX[e] = x; eraW[e] = cols * (NODE_W + GX) - GX; x += eraW[e] + ERA_GAP; }
    const bandY = {}, bandH = {}; let y = TOP;
    for (const f of O.bands) { const r = Math.max(1, ...M.eras.map(e => (dims.get(M.ck(f, e)) || { rows: 0 }).rows)); bandY[f] = y; bandH[f] = BAND_T + r * (NODE_H + GY) - GY + BAND_B; y += bandH[f]; }
    const pos = new Map();
    for (const [key, s] of slot) { const [f, e] = s.k.split('|'); pos.set(key, { x: eraX[e] + s.col * (NODE_W + GX), y: bandY[f] + BAND_T + s.row * (NODE_H + GY) }); }
    return { pos, eraX, eraW, bandY, bandH, width: x - ERA_GAP + 40, height: y + 20 };
  }
  return { model, documentOrder, place };
})();
if (typeof module !== 'undefined') module.exports = SOLVER;
