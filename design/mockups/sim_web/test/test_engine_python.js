/* engine.js against the Python harness, game by game and turn by turn.
   Usage: bash test/make_python_ref.sh <dir> [games_per_method] && node test/test_engine_python.js <dir>

   For every reference game (w7f.py's generalist player; see make_python_ref.sh) the engine replays the same game: the
   game index s is the game's place in w7f.py's draws, which gives its method, World Truth, seed (17000 + s) and the five
   rivals from the pool. Checked: the method and truth drawn, and every row's discovery turn (rows never discovered
   included). For each traced game, every turn's record: what was found (in order), diffused, by Endeavour, which ideas
   occurred (and how), were glimpsed, lost, seen in rivals' hands, locked out, rediscovered; the funded focus; development
   (exactly); the turn's Insight, the funded share, each focus's Insight, every hidden meter and a running Endeavour's
   progress, rounded as the trace rounds them (Python's round: half to even on the exact binary value). */
'use strict';
const path = require('path'), fs = require('fs');
const UHEngine = require(path.join(__dirname, '..', 'engine.js'));
const bundle = require(path.join(__dirname, '..', 'bundle.json'));
const { pyRound } = require('./pyfloat.js');
const dir = path.resolve(process.argv[2] || '.');
const meta = JSON.parse(fs.readFileSync(path.join(dir, 'meta.json'), 'utf8'));

const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
let games = 0, matched = 0, rowsCompared = 0, rowsDiffer = 0;
const failures = [];
for (const m of meta) {
  const recs = JSON.parse(fs.readFileSync(path.join(dir, m.games), 'utf8'));
  const methods = Object.keys(bundle.ftl[bundle.worlds[m.world].ontology].COND);
  const draws = [];
  for (let s = 0; s < m.n * methods.length; s++) if (!m.methods || m.methods.includes(methods[s % methods.length])) draws.push(s);
  let ok = 0;
  recs.forEach((rec, i) => {
    const s = draws[i];
    const e = new UHEngine(bundle, { world: m.world, econ: m.econ, game: s, player: 'generalist', maxTurns: m.maxTurns, instrD: m.instrD });
    const problems = [];
    if (e.method !== rec.m) problems.push(`method ${e.method} != ${rec.m}`);
    if (!same(e.truth, rec.truth)) problems.push('truth differs');
    const t = e.runToEnd(), pt = rec.t;
    const keys = new Set([...Object.keys(t), ...Object.keys(pt)]);
    let diff = 0, firstRow = null;
    for (const k of keys) {
      rowsCompared++;
      if (t[k] !== pt[k]) { diff++; rowsDiffer++; if (!firstRow || Math.min(t[k] || 1e9, pt[k] || 1e9) < firstRow[1]) firstRow = [k, Math.min(t[k] || 1e9, pt[k] || 1e9), t[k], pt[k]]; }
    }
    if (diff) problems.push(`${diff} of ${keys.size} rows differ (earliest ${firstRow[0]}: engine ${firstRow[2]}, Python ${firstRow[3]})`);
    games++;
    if (!problems.length) { ok++; matched++; } else failures.push(`${m.world} econ ${m.econ} game ${s} (${rec.m}): ${problems.join('; ')}`);
  });
  console.log(`${m.world.padEnd(9)} econ ${m.econ}: ${ok} of ${recs.length} games identical (every row's discovery turn, ${m.maxTurns} turns)`);
}

// ---- the traced games: every turn's record ----
let traced = 0, tracedOk = 0, turnsCompared = 0;
const fieldDiffs = {};
for (const m of meta) {
  if (!m.trace) continue;
  const tr = JSON.parse(fs.readFileSync(path.join(dir, m.trace), 'utf8'));
  const e = new UHEngine(bundle, { world: m.world, econ: m.econ, game: tr.game, player: 'generalist', maxTurns: m.maxTurns, instrD: m.instrD, trace: true });
  e.runToEnd();
  traced++;
  let bad = 0;
  const note = (f, turn, a, b) => { fieldDiffs[f] = (fieldDiffs[f] || 0) + 1; if (bad++ < 5) console.log(`  ${m.world} ${m.econ} turn ${turn} ${f}: Python ${JSON.stringify(a)} engine ${JSON.stringify(b)}`); };
  if (tr.records.length !== e.traceRecords.length) note('length', 0, tr.records.length, e.traceRecords.length);
  for (let i = 0; i < Math.min(tr.records.length, e.traceRecords.length); i++) {
    const a = tr.records[i], b = e.traceRecords[i];
    turnsCompared++;
    for (const f of ['turn', 'd', 'found', 'diff', 'endv', 'occ', 'glim', 'fund', 'lost', 'locked', 'redisc', 'share']) if (!same(a[f], b[f])) note(f, a.turn, a[f], b[f]);
      // seen: the harness measures it after its diffusion step, so Python's is always empty; the engine records what was
      // first seen abroad that turn (compared exactly whenever Python's is not empty)
      if (a.seen.length && !same(a.seen, b.seen)) note('seen', a.turn, a.seen, b.seen);
    if (a.inc !== pyRound(b.inc, 3)) note('inc', a.turn, a.inc, b.inc);
    const fl = {}; for (const [f, v] of Object.entries(b.flow)) fl[f] = pyRound(v, 2);
    if (!same(a.flow, fl)) note('flow', a.turn, a.flow, fl);
    const pg = {}; for (const [k, v] of Object.entries(b.prog)) pg[k] = pyRound(v, 3);
    if (!same(a.prog, pg)) note('prog', a.turn, a.prog, pg);
    const en = b.end ? [b.end[0], pyRound(b.end[1], 3)] : null;
    if (!same(a.end, en)) note('end', a.turn, a.end, en);
  }
  // the FTL screen's knowledge each turn (w7f.py's status at the end of the turn: standing hypotheses, answers, certainty)
  const all = e.S.have;
  let ftlTurns = 0;
  for (const [T, st] of Object.entries(tr.alive)) {
    const hT = new Map([...all].filter(([, v]) => v.turn <= +T));
    const mine = e.status(hT, +T);
    ftlTurns++;
    if (!same(mine.alive, st.alive) || !same(Object.fromEntries(Object.entries(mine.kn).sort()), Object.fromEntries(Object.entries(st.known).sort())) || mine.certain !== st.certain)
      note('ftl status', +T, st, { alive: mine.alive, known: mine.kn, certain: mine.certain });
  }
  if (!bad) tracedOk++;
  console.log(`trace ${m.world.padEnd(9)} econ ${m.econ} game ${tr.game} (${tr.m}): ${tr.records.length} turns, ${bad ? bad + ' field differences' : 'every record identical'}` +
    `; FTL knowledge compared on ${ftlTurns} turns`);
}

console.log(`\nSUMMARY: ${matched} of ${games} games identical (${rowsCompared - rowsDiffer} of ${rowsCompared} row discovery turns); ` +
  `${tracedOk} of ${traced} traced games identical turn by turn (${turnsCompared} turns)` + (Object.keys(fieldDiffs).length ? `; field differences ${JSON.stringify(fieldDiffs)}` : ''));
for (const f of failures) console.log('DIFFERS: ' + f);
process.exit(matched === games && tracedOk === traced ? 0 : 1);
