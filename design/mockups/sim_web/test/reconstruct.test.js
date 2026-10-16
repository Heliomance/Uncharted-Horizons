// Node test of the replay's reconstruction against the logs themselves: node test/reconstruct.test.js
// Checks, for every sample log: owned rows at the last turn = rows found; the FTL screen's standing hypotheses = the
// harness's alive list every turn (w7f.py's status, per turn, in the log); the first certain turn = the log's cert; the
// rebuilt rivals explain every arrival from abroad; snapshots and events build for every turn without error.
const fs = require('fs'), path = require('path');
const HERE = path.join(__dirname, '..');
global.UHView = require(path.join(HERE, 'view.js'));
const UHReplay = require(path.join(HERE, 'replay.js'));
const bundle = JSON.parse(fs.readFileSync(path.join(HERE, 'bundle.json'), 'utf8'));
let fail = 0;
const ok = (c, msg) => { if (!c) { fail++; console.log('  FAIL', msg); } };
for (const f of fs.readdirSync(path.join(HERE, 'traces')).filter(f => f.endsWith('.json'))) {
  const t = JSON.parse(fs.readFileSync(path.join(HERE, 'traces', f), 'utf8'));
  const t0 = Date.now();
  const g = UHReplay.reconstruct(bundle, t);
  const found = t.records.reduce((n, r) => n + r.found.length, 0);
  const last = g.snapshot(g.last);
  ok(Object.keys(last.have).length === found, f + ': owned at the last turn ' + Object.keys(last.have).length + ' != found ' + found);
  let aliveBad = 0, firstCert = null, nEvents = 0, hiddenEv = 0, ftlEv = 0;
  for (let T = g.first; T <= g.last; T++) {
    const s = g.snapshot(T);
    nEvents += s.events.length; hiddenEv += s.events.filter(e => e.hidden).length; ftlEv += s.events.filter(e => e.kind === 'ftl').length;
    const vm = UHView.researchModel(bundle, s, { engine: T % 2 === 0 });
    if (!vm.detailOf('insight')) aliveBad += 1000;
    const fv = g.ftlAt(T, true);
    const alive = fv.engineInfo.alive.slice().sort().join(',');
    const want = t.alive[String(T)].alive.slice().sort().join(',');
    if (alive !== want) { if (aliveBad < 3) console.log('   alive differs at', T, alive, 'vs', want); aliveBad++; }
    const pv = g.ftlAt(T, false);
    if (pv.certain && firstCert === null) firstCert = T;
    if (t.alive[String(T)].certain !== !!pv.certain) { if (aliveBad < 3) console.log('   certain differs at', T); aliveBad++; }
  }
  ok(aliveBad === 0, f + ': FTL standing differs from the log on ' + aliveBad + ' turns');
  ok(firstCert === (t.cert && t.cert[0]), f + ': first certain turn ' + firstCert + ' != log cert ' + (t.cert && t.cert[0]));
  ok(!g.seenRebuilt || g.seenCheck.explained === g.seenCheck.arrivals, f + ': rivals explain ' + g.seenCheck.explained + ' of ' + g.seenCheck.arrivals + ' arrivals');
  const P = g.projection;
  console.log(f + ': ' + g.turns + ' turns, ' + found + ' found (own ' + g.counts.own + ', abroad ' + g.counts.diffusion + ', Endeavour ' + g.counts.endeavour + '), ' +
    'seen rebuilt ' + g.seenRebuilt + ' (' + g.seenCheck.explained + '/' + g.seenCheck.arrivals + ' arrivals explained), certain ' + firstCert + ', built ' + g.built +
    ', victory ' + (P && P.launch) + ' (proto ' + (P && P.protoTurns) + ', drive ' + (P && P.driveTurns) + '), events ' + nEvents + ' (' + hiddenEv + ' hidden, ' + ftlEv + ' FTL changes), ' + (Date.now() - t0) + ' ms');
}
console.log(fail ? fail + ' FAILED' : 'all passed');
process.exit(fail ? 1 : 0);
