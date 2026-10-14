// Design-document parser for the tech-tree viewer. A port of the shared prerequisite parser (power/prereq.py)
// and the generator's world tagging (power/gen_data.py), so the viewer reads the document exactly as the tools do.
const IDRX_SRC = String.raw`\b([A-Z]{1,3}-?[A-Z]?\d{1,2}[A-Z]?(?:-W|-V\d+)?|ME-B)\b`;
const idRx = () => new RegExp(IDRX_SRC, 'g');
const START_ID = new RegExp(String.raw`^\s*(?:` + IDRX_SRC + ')');
const ERAS = ['Primitive', 'Ancient', 'Classical', 'Medieval', 'Early Modern', 'Modern', 'Atomic', 'Space', 'Interstellar'];
const TIERS = ['CORE', 'STANDARD', 'UNCOMMON', 'RARE', 'UNIQUE'];

function findIds(s) { return [...s.matchAll(idRx())].map(m => m[1]); }

function stripDescriptions(s) {
  for (;;) {
    let changed = false;
    const rx = /\(([^()]*)\)/g; let m;
    while ((m = rx.exec(s))) {
      if (!START_ID.test(m[1])) { s = s.slice(0, m.index) + s.slice(m.index + m[0].length); changed = true; break; }
    }
    if (!changed) return s;
  }
}
function depthAt(s) { const d = []; let k = 0; for (let i = 0; i < s.length; i++) { if (s[i] === '(') k++; if (s[i] === ')') k--; d.push(k); } return d; }
function cutCommentary(s) {
  const d = depthAt(s);
  for (let i = 0; i < s.length; i++) if (d[i] === 0 && s.startsWith(' — ', i)) return s.slice(0, i);
  return s;
}
const isAlnum = c => !!c && /[A-Za-z0-9]/.test(c);
function split(s, seps) {
  const d = depthAt(s); const out = []; let last = 0;
  for (let i = 0; i < s.length; i++) {
    if (d[i] !== 0 || i < last) continue;
    for (const sep of seps) {
      if (s.startsWith(sep, i) && (sep === '+' || sep === ',' || (!isAlnum(s[i - 1]) && !isAlnum(s[i + sep.length])))) {
        out.push(s.slice(last, i)); last = i + sep.length; break;
      }
    }
  }
  out.push(s.slice(last)); return out;
}
function topGroups(s) {
  const out = []; let d = 0, st = null;
  for (let i = 0; i < s.length; i++) {
    if (s[i] === '(') { if (d === 0) st = i; d++; }
    else if (s[i] === ')') { d--; if (d === 0 && st !== null) out.push([st, i]); }
  }
  return out;
}
function termBody(term, known) {
  const t = term.trim();
  const all = findIds(t).filter(x => !known || known.has(x));
  for (const [a, b] of topGroups(t)) {
    const inner = t.slice(a + 1, b); const ids = findIds(inner).filter(x => !known || known.has(x));
    if (ids.length && ids.length === all.length) return termBody(inner, known);
  }
  return t;
}
/** [[[ids…], …], …]: AND-terms, each a list of OR-options, each a list of ANDed IDs */
function parsePrereq(pre, known) {
  const s = cutCommentary(stripDescriptions(pre)); const out = [];
  for (const term of split(s, ['+'])) {
    const body = termBody(term, known);
    const hasOr = /\bor\b/.test(body); const opts = [];
    for (const o of split(body, hasOr ? ['or', ','] : ['or'])) {
      const ids = findIds(o).filter(x => !known || known.has(x));
      if (ids.length) opts.push(ids);
    }
    if (opts.length) out.push(opts);
  }
  return out;
}

const AXIS = { Substance: 'Atomic', Process: 'Atomic', Miasma: 'Germ', Humoral: 'Germ', Caloric: null, Vitalist: null, Gravitic: null };
const ELEMENTAL = new Set(['Substance', 'Process']);
const WORLD_TEXT = /Only in ([A-Z][a-z]+) worlds|([A-Z][a-z]+) worlds only|\*([A-Z][a-z]+) only\.?\*|\*\*([A-Z][a-z]+)-exclusive/;
const VALIDATED = /\(([A-Z][a-z]+)(?:-Elemental| Theory)? validated\)/;

/** Parse the whole design document into {version, foci, rows, edges} */
function parseDocument(text) {
  const lines = text.replace(/\r\n?/g, '\n').split('\n');
  const vm = /Design Document \((v[\d.]+)\)/.exec(lines.slice(0, 5).join('\n'));
  const version = vm ? vm[1] : null;
  const end = lines.findIndex(l => /^## 4\./.test(l));
  const body = end > 0 ? lines.slice(0, end) : lines;
  const foci = []; const rows = new Map(); let cur = null;
  for (const l of body) {
    const fm = /^#{2,4} FOCUS: ([A-Z][A-Z &'-]+?)\s*(\S+)?\s*$/.exec(l);
    if (fm) { cur = { name: titleCase(fm[1].trim()), icon: fm[2] || '', available: '', dual: [] }; foci.push(cur); continue; }
    if (/^## /.test(l)) { cur = null; continue; }
    if (!cur) continue;
    const am = /^\*Available from: (.*)\*\s*$/.exec(l); if (am) { cur.available = am[1]; continue; }
    // every row ID a focus's dual-path line names, whatever its format; checked against the rows below
    if (/^\*Also reachable in this focus\b/.test(l)) { for (const id of findIds(l)) cur.dual.push({ id }); continue; }
    const rm = /^\| ([A-Z][A-Z0-9-]*) \| \*\*/.exec(l);
    if (!rm) continue;
    const cells = l.split(' | ').map(c => c.trim());
    cells[0] = cells[0].replace(/^\|\s*/, ''); cells[cells.length - 1] = cells[cells.length - 1].replace(/\s*\|$/, '');
    const [id, name, tier, era, pre, unlocks, notes] = cells;
    rows.set(id, { id, name: name.replace(/\*\*/g, ''), tier, era, preText: pre || '', unlocks: unlocks || '', notes: notes || '', focus: cur.name });
  }
  const known = new Set(rows.keys());
  for (const r of rows.values()) r.pre = parsePrereq(r.preText, known).map(g => g.map(o => o.filter(p => p !== r.id)).filter(o => o.length)).filter(g => g.length);
  const memo = new Map();
  const world = (k, seen) => {
    if (memo.has(k)) return memo.get(k);
    const r = rows.get(k); let w = null;
    if (k.startsWith('QM-E')) w = 'Elemental';
    else {
      const m = WORLD_TEXT.exec(r.unlocks);
      if (m) w = m[1] || m[2] || m[3] || m[4];
      else { const v = VALIDATED.exec(r.preText); if (v) w = v[1]; }
      if (!w) for (const g of r.pre) {
        if (g.length !== 1) continue;
        for (const p of g[0]) if (!seen.has(p)) { const pw = world(p, new Set([...seen, k])); if (pw) { w = pw; break; } }
        if (w) break;
      }
    }
    if (!seen.size) memo.set(k, w);
    return w;
  };
  for (const k of rows.keys()) rows.get(k).world = world(k, new Set());
  const edges = [];
  for (const r of rows.values()) r.pre.forEach((g, gi) => g.forEach(o => o.forEach(p => edges.push({ from: p, to: r.id, alt: g.length > 1, group: gi }))));
  // other foci a breakthrough is reachable through, from both records: the other focus's dual-path line,
  // and the row's own "Also discoverable through …" text. Either is taken; disagreements are kept as issues.
  const live = foci.filter(f => [...rows.values()].some(r => r.focus === f.name));
  const byName = new Map(live.map(f => [f.name.toLowerCase(), f.name]));
  const fromLines = new Map();
  for (const f of foci) for (const d of f.dual) if (rows.has(d.id)) (fromLines.get(d.id) || fromLines.set(d.id, new Set()).get(d.id)).add(f.name);
  for (const r of rows.values()) {
    const lines = fromLines.get(r.id) || new Set(), text = new Set(), unknown = [];
    const m = /(?:Also )?(?:discoverable|reachable) through ([^.*()]+)/i.exec(r.unlocks + ' ' + r.notes);
    if (m) for (let n of m[1].split(/,\s*|\s+or\s+|\s+and\s+/)) {
      n = n.trim().replace(/^the\s+/i, '').replace(/\s+focus$/i, '').trim(); if (!n) continue;
      const hit = byName.get(n.toLowerCase());
      if (hit) { if (hit !== r.focus) text.add(hit); } else unknown.push(n);
    }
    const all = [...new Set([...lines, ...text])].filter(f => f !== r.focus);
    if (!all.length && !unknown.length) continue;
    r.alsoIn = all; r.dualIssues = [];
    for (const f of all) {
      if (!lines.has(f)) r.dualIssues.push(`the row says it is also discoverable through ${f}, but ${f}'s dual-path line does not list it`);
      if (!text.has(f)) r.dualIssues.push(`${f}'s dual-path line lists it, but the row's own text does not mention ${f}`);
    }
    for (const n of unknown) r.dualIssues.push(`the row mentions "${n}", which is not a focus in this version`);
  }
  return { version, foci: live, rows, edges };
}
function titleCase(s) {
  const small = new Set(['and', 'the', 'of', 'in']);
  return s.toLowerCase().split(' ').map((w, i) => (i && small.has(w)) ? w : w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}
/** rows present in a world: the familiar world, or one with an axis branch in place of its familiar value */
function inWorld(row, alt) {
  if (!alt || alt === 'all') return true;
  const keep = new Set([null, 'Germ', 'Atomic']);
  if (alt !== 'familiar') { keep.add(alt); if (ELEMENTAL.has(alt)) keep.add('Elemental'); if (AXIS[alt]) keep.delete(AXIS[alt]); }
  return keep.has(row.world ?? null);
}
/** foci in the order they open: the era of the rows a focus's "Available from" line needs (the earliest route
 * where it offers alternatives), then how deep those rows sit in the prerequisite chain; a focus whose line names
 * no rows opens with its own earliest row. Ties keep the document's order. */
function openingOrder(doc) {
  const known = new Set(doc.rows.keys()); const era = id => ERAS.indexOf(doc.rows.get(id).era);
  const depthMemo = new Map();
  const depth = (id, seen = new Set()) => {
    if (depthMemo.has(id)) return depthMemo.get(id);
    if (seen.has(id)) return 0; seen.add(id);
    const r = doc.rows.get(id); let d = 0;
    for (const g of r.pre) { let best = Infinity; for (const o of g) best = Math.min(best, Math.max(0, ...o.map(p => doc.rows.has(p) ? 1 + depth(p, seen) : 0))); if (best < Infinity) d = Math.max(d, best); }
    depthMemo.set(id, d); return d;
  };
  const when = f => {
    const own = [...doc.rows.values()].filter(r => r.focus === f.name);
    const earliest = Math.min(...own.map(r => ERAS.indexOf(r.era)));
    const terms = parsePrereq(f.available || '', known);
    if (!terms.length) return [earliest, -1, f.name];
    let e = 0, d = 0;
    for (const g of terms) {
      let best = null;
      for (const o of g) { const oe = Math.max(...o.map(era)), od = Math.max(...o.map(id => depth(id))); if (!best || oe < best[0] || (oe === best[0] && od < best[1])) best = [oe, od]; }
      if (best[0] > e || (best[0] === e && best[1] > d)) { e = best[0]; d = best[1]; }
    }
    return [e, d, f.name];
  };
  const idx = new Map(doc.foci.map((f, i) => [f.name, i]));
  return doc.foci.map(f => [f, when(f)]).sort((a, b) => a[1][0] - b[1][0] || a[1][1] - b[1][1] || idx.get(a[0].name) - idx.get(b[0].name)).map(([f, w]) => ({ name: f.name, era: ERAS[w[0]], depth: w[1] }));
}
if (typeof module !== 'undefined') module.exports = { parseDocument, parsePrereq, inWorld, openingOrder, ERAS, TIERS };
