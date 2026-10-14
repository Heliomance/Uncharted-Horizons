// The long search for one version, run here when a version is published; writes the order the page loads with.
// Local search to an optimum, then iterated local search — kick the best order with a few random band moves,
// re-optimise, keep it only if it is better — until the time budget runs out. Seeded, so a version's result repeats.
const P = require('./parse.js'), S = require('./solver.js'), fs = require('fs');
const [file, out, budget] = [process.argv[2], process.argv[3], +(process.argv[4] || 240) * 1000];
const G = { NODE_W: 176, NODE_H: 40, GX: 24, GY: 10, BAND_T: 30, BAND_B: 14, MAX_ROWS: 6, ERA_GAP: 56, LEFT: 210, TOP: 20 };
const doc = P.parseDocument(fs.readFileSync(file, 'utf8'));
const R = S.solve(doc, P.ERAS, G); const M = R.model; const t0 = Date.now();
let seed = 109; const rnd = () => (seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648;
let best = { order: R.solved.order, crossings: R.solved.crossings }, evals = 0, kicks = 0, kept = 0;
const save = finished => fs.writeFileSync(out, JSON.stringify({ version: doc.version, crossings: best.crossings, documentCrossings: R.document.crossings, quickCrossings: R.solved.crossings, evaluations: evals, kicks, kept, finished, ...S.serialise(best.order) }));
function descend(order, known) {
  const it = S.improve(M, order, known); let step = it.next(), last = step.value;
  while (!step.done && Date.now() - t0 < budget) { last = step.value; step = it.next(); }
  const v = step.done ? step.value : last; evals += v.evals; return v;
}
let v = descend(best.order, best.crossings); best = { order: v.order, crossings: v.crossings }; save(false);
const firstOptimum = best.crossings;
while (Date.now() - t0 < budget) {
  const b = [...best.order.bands];
  for (let n = 0; n < 3; n++) { const i = Math.floor(rnd() * b.length), j = Math.floor(rnd() * b.length); const [f] = b.splice(i, 1); b.splice(j, 0, f); }
  kicks++; const w = descend({ bands: b, cells: best.order.cells });
  if (w.crossings < best.crossings) { best = { order: w.order, crossings: w.crossings }; kept++; save(false); }
}
save(true);
console.log(`${doc.version}: document order ${R.document.crossings}, quick ${R.solved.crossings}, first optimum ${firstOptimum}, best ${best.crossings} (${(100 * (1 - best.crossings / R.document.crossings)).toFixed(0)}% fewer) — ${kicks} kicks, ${kept} kept, ${evals} evaluations in ${Math.round((Date.now() - t0) / 1000)} s; ${(fs.statSync(out).size / 1024).toFixed(1)} KB`);
const back = S.deserialise(M, JSON.parse(fs.readFileSync(out, 'utf8')));
console.log('round trip:', back ? `recovered, ${S.crossings(M, S.place(M, back).pos)} crossings` : 'REFUSED');
