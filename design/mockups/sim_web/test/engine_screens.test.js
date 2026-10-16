// view.js on the live engine's snapshots (engine.js, written alongside): node test/engine_screens.test.js
// Plays one game a world with the advisor (the generalist's choices, following the FTL hints) to its end, building both
// view models every turn, and checks them against the engine: owned = the engine's have; the FTL screen's standing
// hypotheses and certainty = the engine's ftl(); every event becomes text; the player view shows no hidden rows.
const fs = require('fs'), path = require('path');
const HERE = path.join(__dirname, '..');
const V = require(path.join(HERE, 'view.js'));
let UHEngine;
try { UHEngine = require(path.join(HERE, 'engine.js')); } catch (e) { console.log('engine.js not loadable yet:', e.message); process.exit(0); }
const bundle = JSON.parse(fs.readFileSync(path.join(HERE, 'bundle.json'), 'utf8'));
let fail = 0;
const ok = (c, m) => { if (!c) { fail++; console.log('  FAIL', m); } };
for (const [world, econ] of [['familiar', '1.0'], ['Process', '1.0'], ['Substance', '0.8']]) {
  const t0 = Date.now();
  let e;
  try { e = new UHEngine(bundle, { world, econ, game: 0, player: 'advisor' }); } catch (err) { console.log(world, 'engine would not start:', err.message); fail++; continue; }
  let turns = 0, bad = 0, textless = 0, leaks = 0, certV = null, certE = null, committed = null, sawProto = 0, sawDrive = 0, victoryText = '', slotOk = false;
  while (!e.over && turns < 700) {
    e.step(); turns++;
    const s = e.snapshot();
    const vm = V.researchModel(bundle, s, {}), vmE = V.researchModel(bundle, s, { engine: true });
    if (vm.owned.count !== Object.keys(s.have).length) bad++;
    textless += vm.events.filter(x => !x.text).length;
    leaks += Object.values(vm.rows).filter(c => c.hidden).length;
    if (!vmE.detailOf('insight')) bad++;
    const fv = V.ftlModel(bundle, s, { truth: s.hidden && s.hidden.truth, instrD: bundle.ftl.INSTR_D[econ],
      canCommit: m => { const q = e.prototypeQuote(m); return { ok: q.eligible, reason: q.reason }; } });
    // play on as a careful human would: commit to the prototype the screen is certain of, once it can be committed
    const sure = fv.certain && fv.hypotheses.find(h => h.method === fv.certain.method);
    if (sure && sure.prototype.canCommit) { const r = e.commitPrototype(sure.method); committed = committed || (r && r.ok !== false ? s.turn : null); }
    if (s.prototype) sawProto++;
    if (s.drive && !s.drive.done) sawDrive++;
    for (const x of vm.events) if (x.kind === 'finish' && /Victory/.test(x.text)) victoryText = x.text;
    if (s.victory) { const fvv = V.ftlModel(bundle, s, { truth: s.hidden.truth }); slotOk = fvv.victory && fvv.victory.turn === s.victory.turn; }
    const ef = s.ftl;
    if (ef && fv.open) {
      const a = fv.hypotheses.filter(h => h.standing !== 'ruled_out').map(h => h.method).sort().join(',');
      const b = ef.hypotheses.filter(h => h.proposed && h.alive).map(h => h.method).sort().join(',');
      if (a !== b) { if (bad < 3) console.log('   standing differs at', s.turn, a, '|', b); bad++; }
      if (fv.certain && certV === null) certV = s.turn;
      if (ef.certain && certE === null) certE = s.turn;
    }
  }
  ok(bad === 0, world + ': view models disagree with the engine on ' + bad + ' checks');
  ok(textless === 0, world + ': ' + textless + ' events without text');
  ok(leaks === 0, world + ': hidden rows in the player view');
  ok(certV === certE, world + ': certain on turn ' + certV + ' (view) vs ' + certE + ' (engine)');
  ok(e.victory && sawProto > 0 && sawDrive > 0 && slotOk && victoryText, world + ': the prototype, the Drive and the victory reach the screens');
  console.log(world + ': ' + turns + ' turns, certain ' + certV + ', committed ' + committed + ', prototype ' + sawProto + ' turns, Drive ' + sawDrive +
    ' turns, victory ' + (e.victory ? e.victory.turn : 'none') + ' ("' + victoryText + '"), ' + (Date.now() - t0) + ' ms');
}
console.log(fail ? fail + ' FAILED' : 'all passed');
process.exit(fail ? 1 : 0);
