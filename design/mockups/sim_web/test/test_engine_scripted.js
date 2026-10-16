/* The engine's human path against the Python harness: the scripted player of py_scripted.py, played through the API
   (setFocus, requestEndeavour, step), game by game and turn by turn.
   Usage: (make the references with py_scripted.py, one file per world and economy, named <world>_<econ>.json)
          node test/test_engine_scripted.js <dir>
   The policy, as py_scripted.py has it: before turn T, the focus is none (automatic) when T is divisible by 4, otherwise
   the T-th (modulo) of the sorted foci of the rows discovered; when T is divisible by 15 and no Endeavour is running (or
   the running one's breakthrough has just been found by study), an Endeavour on the first revealed, undiscovered
   breakthrough with its prerequisites met, preferring one whose idea has not occurred. */
'use strict';
const path = require('path'), fs = require('fs');
const UHEngine = require(path.join(__dirname, '..', 'engine.js'));
const bundle = require(path.join(__dirname, '..', 'bundle.json'));
const { pyRound, fromHex } = require('./pyfloat.js');
const dir = path.resolve(process.argv[2] || '.');
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const pysorted = (it) => Array.from(it).sort((a, b) => (a < b ? -1 : a > b ? 1 : 0));

let games = 0, ok = 0, turns = 0, endeavours = 0, recOk = 0, rawTurns = 0, rawValues = 0;
const fieldDiffs = {};
for (const f of fs.readdirSync(dir).filter((x) => /^(familiar|Process|Substance)_(1\.0|0\.8)\.json$/.test(x)).sort()) {
  const [, world, econ] = /^(\w+)_([\d.]+)\.json$/.exec(f);
  const recs = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
  let okHere = 0;
  recs.forEach((rec, s) => {
    const e = new UHEngine(bundle, { world, econ: parseFloat(econ), game: s, player: 'human', maxTurns: econ === '1.0' ? 450 : 600, trace: true });
    while (!e.over) {
      const T = e.turn + 1, S = e.S;
      const foci = pysorted(new Set([...S.have.keys()].map((k) => e.ROWS[k].focus)));
      e.setFocus(T % 4 === 0 || !foci.length ? null : foci[T % foci.length]);
      if (T % 15 === 0 && (S.end_k === null || S.have.has(S.end_k))) {
        const rev = e.IDS.filter((k) => !S.have.has(k) && e.prereqsMet(k, S.have) && e.isRevealed(k));
        const unocc = rev.filter((k) => !S.occurred.has(k));
        const pick = unocc.length ? unocc[0] : rev[0];
        if (pick) { const r = e.requestEndeavour(pick); if (!r.ok) throw new Error('request refused: ' + r.reason); }
      }
      for (const ev of e.step()) if (ev.type === 'endeavour_started') endeavours++;
    }
    games++;
    const t = {}; for (const [k, v] of e.S.have) t[k] = v.turn;
    let diff = 0; for (const k of new Set([...Object.keys(t), ...Object.keys(rec.t)])) if (t[k] !== rec.t[k]) diff++;
    let bad = 0;
    const note = (fld, turn, a, b) => { fieldDiffs[fld] = (fieldDiffs[fld] || 0) + 1; if (bad++ < 3) console.log(`  ${world} ${econ} game ${s} turn ${turn} ${fld}: Python ${JSON.stringify(a)} engine ${JSON.stringify(b)}`); };
    if (rec.records.length !== e.traceRecords.length) note('length', 0, rec.records.length, e.traceRecords.length);
    for (let i = 0; i < Math.min(rec.records.length, e.traceRecords.length); i++) {
      const a = rec.records[i], b = e.traceRecords[i];
      turns++;
      for (const fld of ['turn', 'd', 'found', 'diff', 'endv', 'occ', 'glim', 'fund', 'lost', 'seen', 'locked', 'redisc', 'share']) if (!same(a[fld], b[fld])) note(fld, a.turn, a[fld], b[fld]);
      if (a.inc !== pyRound(b.inc, 3)) note('inc', a.turn, a.inc, b.inc);
      const fl = {}; for (const [k, v] of Object.entries(b.flow)) fl[k] = pyRound(v, 2);
      if (!same(a.flow, fl)) note('flow', a.turn, a.flow, fl);
      const pg = {}; for (const [k, v] of Object.entries(b.prog)) pg[k] = pyRound(v, 3);
      if (!same(a.prog, pg)) note('prog', a.turn, a.prog, pg);
      const en = b.end ? [b.end[0], pyRound(b.end[1], 3)] : null;
      if (!same(a.end, en)) note('end', a.turn, a.end, en);
      if (a.raw) {                                   // the raw floats, to the bit
        rawTurns++;
        const bit = (h, v) => Object.is(fromHex(h), v);
        if (!bit(a.raw.inc, b.inc)) note('raw inc', a.turn, a.raw.inc, b.inc);
        for (const [f, h] of Object.entries(a.raw.flow)) { rawValues++; if (!bit(h, b.flow[f])) note('raw flow ' + f, a.turn, fromHex(h), b.flow[f]); }
        if (Object.keys(a.raw.flow).length !== Object.keys(b.flow).length) note('raw flow keys', a.turn, Object.keys(a.raw.flow), Object.keys(b.flow));
        for (const [k, h] of Object.entries(a.raw.progress)) { rawValues++; if (!bit(h, b.raw.progress[k])) note('raw progress ' + k, a.turn, fromHex(h), b.raw.progress[k]); }
        for (const [k, h] of Object.entries(a.raw.need)) { rawValues++; if (!bit(h, b.raw.need[k])) note('raw need ' + k, a.turn, fromHex(h), b.raw.need[k]); }
        // a running Endeavour's progress (once it ends the harness leaves the old value in a variable nothing reads; the engine clears it)
        if (a.end && !bit(a.raw.end_prog, b.raw.end_prog)) note('raw end_prog', a.turn, a.raw.end_prog, b.raw.end_prog);
      }
    }
    if (!diff && !bad) { ok++; okHere++; } else console.log(`DIFFERS ${world} ${econ} game ${s} (${rec.m}): ${diff} rows' discovery turns, ${bad} record fields`);
    if (!bad) recOk++;
  });
  console.log(`${world.padEnd(9)} econ ${econ}: ${okHere} of ${recs.length} scripted games identical (discovery turns and every turn's record)`);
}
console.log(`\nSUMMARY: ${ok} of ${games} scripted games identical, ${turns} turns compared (${rawTurns} with raw floats: ${rawValues} values to the bit), ${endeavours} Endeavours started` +
  (Object.keys(fieldDiffs).length ? `; field differences ${JSON.stringify(fieldDiffs)}` : ''));
process.exit(ok === games ? 0 : 1);
