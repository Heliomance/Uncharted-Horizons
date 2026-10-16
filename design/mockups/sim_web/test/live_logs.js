/* The live game's logs in the replay viewer. Games are played through the engine's human API, as play.html plays them; each
   game's log (UHEngine.traceLog, what the live game's Copy log gives) is replayed by replay.js and compared, turn by turn,
   with the engine's own state, replayed from the log's choices.
     node test/live_logs.js [out_dir]      (with out_dir, the logs are also written there, for test_replay.py)

   Games: a delayed commit (the certain method committed 12 turns after it could be; an Endeavour begun and replaced first),
   a failed prototype (a wrong hypothesis committed as soon as it can be, then the true one), a Hail Mary (the true method
   committed as soon as its build is complete, before certainty, on the average economy), and the failed-prototype game's log
   and the Hail Mary's logs in the format the live game wrote before 16 October (no per-turn prototype record, no Drive,
   `seen` empty, so rebuilt from the rivals).
   Checked every turn: what is owned (turn and how), occurred, glimpsed, lost, locked out and seen abroad; the funded share's
   use (focus, Endeavour or prototype); the prototype and its progress; the Drive; the victory; every row's status in the
   player's view (the replay's against the live game's own); the FTL screen's standing hypotheses and certainty against the
   log's own; a failed prototype rules its method out from its turn on; no results line says a ruled-out hypothesis can be
   committed. And the replay reports the log's own victory, not a projection. */
'use strict';
const fs = require('fs'), path = require('path');
const WEB = path.join(__dirname, '..');
global.UHView = require(path.join(WEB, 'view.js'));
const V = global.UHView, RP = require(path.join(WEB, 'replay.js')), UHEngine = require(path.join(WEB, 'engine.js'));
const bundle = JSON.parse(fs.readFileSync(path.join(WEB, 'bundle.json'), 'utf8'));
const out = process.argv[2] || null;
let fail = 0;
const ok = (c, msg) => { if (!c) { fail++; console.log('  FAIL ' + msg); } };

function certainMethod(e) {
  const st = e.status(e.S.have, e.turn);
  if (!st.certain) return null;
  return st.alive.length === 1 ? st.alive[0] : e.METHODS.find((o) => e.F.COND[o].every((c) => st.kn[c]));
}

/** a game played as a player would, through the API; style: 'delayed' | 'gamble' | 'hailmary' */
function play(opts, style) {
  const e = new UHEngine(bundle, Object.assign({ player: 'human', trace: true }, opts));
  let can = null, endTried = 0, gambled = null;
  while (!e.over) {
    const a = e.advise();
    e.setFocus(a.focus || null);
    if (style === 'delayed' && ((endTried === 0 && e.turn >= 40) || (endTried === 1 && e.S.end_k !== null))) {   // begin one, then replace it
      const k = e.IDS.find((x) => !e.endeavourCheck(x) && x !== e.S.end_k);
      if (k && e.requestEndeavour(k).ok) endTried++;
    }
    if (!e.S.proto && !e.S.protoWorked && e.S.have.has(e.OPENS)) {
      if (style === 'gamble' && !gambled) {
        const wrong = e.METHODS.find((m) => m !== e.method && !e.prototypeCheck(m));
        if (wrong && e.commitPrototype(wrong).ok) gambled = wrong;
      }
      const m = style === 'hailmary' ? (!e.prototypeCheck(e.method) ? e.method : null) : certainMethod(e);
      if (!e.S.proto && m && !e.prototypeCheck(m)) {
        if (can === null) can = e.turn;
        if (style !== 'delayed' || e.turn >= can + 12) e.commitPrototype(m);
      }
    }
    e.step();
  }
  return e;
}

/** the log as the live game wrote it before 16 October: no per-turn prototype record, the prototype funded as nothing, no
    Drive, and `seen` measured after diffusion (always empty) */
function oldFormat(log) {
  const o = JSON.parse(JSON.stringify(log));
  for (const r of o.records) { delete r.proto; if (r.fund[0] === 'PROTO') r.fund = ['FOCUS', null]; r.seen = []; }
  delete o.drive; delete o.maxTurns; o.settings = Object.assign({}, o.settings); delete o.settings.DIFF;
  return o;
}

function compare(label, log) {
  // the engine's state each turn, replayed from the log's choices
  const e = new UHEngine(bundle, { world: log.world, econ: log.econ, game: log.game, seed: log.seed, rivals: log.diffusion !== false, player: 'human', maxTurns: log.maxTurns });
  const acts = log.choices, SN = {};
  let ai = 0;
  const last = log.records[log.records.length - 1].turn;
  while (!e.over && e.turn < last) {
    while (ai < acts.length && acts[ai].t === e.turn) { const x = acts[ai++]; if (x.a === 'focus') e.setFocus(x.v); else if (x.a === 'end') e.requestEndeavour(x.v); else if (x.a === 'stop') e.stopEndeavour(); else if (x.a === 'proto') e.commitPrototype(x.v); }
    e.step();
    SN[e.turn] = e.snapshot({ ftl: false });
  }
  const g = RP.reconstruct(bundle, log), W = V.world(bundle, log.world), R = bundle.rows;
  const tally = {}, ex = {};
  const bump = (k, s) => { tally[k] = (tally[k] || 0) + 1; (ex[k] = ex[k] || []).length < 3 && ex[k].push(s); };
  const sameSet = (k, a, b, T) => { const A = new Set(a), B = new Set(b); const x = [...A].filter((q) => !B.has(q)), y = [...B].filter((q) => !A.has(q)); if (x.length || y.length) bump(k, 'T' + T + ' replay-only ' + x.slice(0, 3) + ' / engine-only ' + y.slice(0, 3)); };
  let protoTurns = 0, driveTurns = 0;
  for (let T = g.first; T <= g.last; T++) {
    const S = SN[T], s = g.snapshot(T);
    if (!S) { bump('no engine state', T); continue; }
    sameSet('owned', Object.keys(s.have), Object.keys(S.have), T);
    for (const k in S.have) if (s.have[k] && (s.have[k].turn !== S.have[k].turn || s.have[k].via !== S.have[k].via)) bump('owned turn or way', 'T' + T + ' ' + k);
    for (const f of ['occurred', 'glimpsed', 'lost', 'locked', 'seen']) sameSet(f, s[f], S[f], T);
    if (s.inc !== S.inc) bump('Insight', T);
    const vm = V.researchModel(bundle, s, {}), f = vm.header.funded;
    const fundR = f.kind === 'focus' ? 'FOCUS ' + f.focus : f.kind === 'endeavour' ? 'END ' + f.id : f.kind === 'prototype' ? 'PROTO ' + f.method : 'FOCUS null';
    if (fundR !== S.fund[0] + ' ' + S.fund[1]) bump('funded', 'T' + T + ' replay ' + fundR + ' / engine ' + S.fund.join(' '));
    if (!!s.prototype !== !!S.prototype || (S.prototype && (s.prototype.method !== S.prototype.method || Math.abs(s.prototype.progress - S.prototype.progress) > 1e-12))) bump('prototype', 'T' + T + ' ' + JSON.stringify(s.prototype) + ' / ' + JSON.stringify(S.prototype));
    if (S.prototype) protoTurns++;
    if (JSON.stringify(s.drive) !== JSON.stringify(S.drive)) bump('Drive', 'T' + T + ' ' + JSON.stringify(s.drive) + ' / ' + JSON.stringify(S.drive));
    if (S.drive) driveTurns++;
    if (JSON.stringify(s.victory) !== JSON.stringify(S.victory)) bump('victory', T);
    const vmE = V.researchModel(bundle, Object.assign({}, S, { events: [] }), {});
    for (const k of W.ids) { const a = vm.rows[k], b = vmE.rows[k]; if ((a ? a.status : null) !== (b ? b.status : null)) bump('row status', 'T' + T + ' ' + R[k].name + ' ' + (a && a.status) + ' / ' + (b && b.status)); }
    const fv = g.ftlAt(T, false), AL = log.alive[String(T)];
    for (const h of fv.hypotheses) if (h.proposed && ((h.standing !== 'ruled_out') !== AL.alive.includes(h.method))) bump('FTL standing', 'T' + T + ' ' + h.method + ' ' + h.standing);
    if (!!fv.certain !== AL.certain) bump('FTL certainty', T);
    for (const r of fv.results) {
      const m = /^Every build need of (\w+) is met/.exec(r.text);
      if (m) { const h = fv.hypotheses.find((x) => x.method === m[1]); if (h.ruledTurn != null && h.ruledTurn <= r.turn) bump('committable after ruled out', 'T' + T + ' ' + r.text); }
    }
  }
  for (const k of Object.keys(tally).sort()) { ok(false, label + ': ' + k + ' differs on ' + tally[k] + ' turns, e.g. ' + ex[k].join(' | ')); }
  // the endgame as the replay tells it
  const v = log.victory;
  ok(g.live && !g.projection, label + ': a live log is not projected');
  ok(v && g.actual && g.actual.turn === v.turn, label + ': the replay reports the log\'s victory, turn ' + (v && v.turn));
  ok(v && g.events(v.turn).some((x) => x.kind === 'finish' && x.text.includes('turn ' + v.turn)), label + ': the victory is an event on its turn');
  ok(!g.events(g.last).some((x) => /The prototype and the Drive follow/.test(x.text)), label + ': no projection in the last turn\'s events');
  for (const r of log.prototypes) {
    const evs = g.events(r.turn).map((x) => x.text).join(' ');
    ok(evs.includes('The ' + r.method + ' prototype ' + (r.works ? 'works' : 'failed')), label + ': the ' + r.method + ' prototype\'s result is an event on turn ' + r.turn);
    if (!r.works) {
      const before = g.ftlAt(r.turn - 1, false).hypotheses.find((h) => h.method === r.method), after = g.ftlAt(r.turn, false).hypotheses.find((h) => h.method === r.method);
      // (a test result may have ruled it out already while its prototype was being built)
      ok(before.prototype.state === 'running' && after.standing === 'ruled_out' && after.prototype.state === 'failed' && after.ruledTurn <= r.turn,
        label + ': the ' + r.method + ' prototype is under way until turn ' + r.turn + ', then failed, and ' + r.method + ' ruled out' + (before.standing === 'ruled_out' ? ' (already, on turn ' + before.ruledTurn + ')' : ''));
    }
  }
  ok(g.marks.some((m) => m.kind === 'launch' && m.turn === v.turn), label + ': the chart marks the launch on turn ' + v.turn);
  const fl = g.ftlAt(g.last, false);
  ok(fl.prototypeResults.length === log.prototypes.length, label + ': the FTL screen has the prototypes\' results');
  console.log(label + ': ' + log.world + ', econ ' + log.econ + ', diffusion ' + log.diffusion + ', ' + log.m + '; ' + g.turns + ' turns; certain ' + (log.cert && log.cert[0]) + ', built ' + log.built +
    '; prototypes ' + log.prototypes.map((r) => r.method + (r.works ? ' works' : ' fails') + ' (turn ' + r.turn + ')').join(', ') + '; victory ' + v.turn + ' (' + (v.delta >= 0 ? '+' : '') + v.delta + ' against ' + v.reference + ')' +
    '; ' + protoTurns + ' prototype turns, ' + driveTurns + ' Drive turns; rows seen abroad ' + (g.seenRebuilt ? 'rebuilt (' + g.seenCheck.explained + '/' + g.seenCheck.arrivals + ' arrivals explained)' : 'from the log') +
    '; ' + (Object.keys(tally).length ? Object.keys(tally).length + ' kinds of difference' : 'every turn matches'));
}

const games = [
  ['delayed', play({ world: 'familiar', econ: 1.0, seed: 17003, rivals: true }, 'delayed')],
  ['failed', play({ world: 'Process', econ: 1.0, seed: 17046, rivals: false }, 'gamble')],
  ['hailmary', play({ world: 'Process', econ: 0.8, seed: 17110, rivals: true }, 'hailmary')],
];
const logs = {};
for (const [label, e] of games) {
  ok(!!e.victory, label + ': the game reaches victory');
  logs['live_' + label] = e.traceLog('live game (test/live_logs.js)');
}
ok(logs.live_delayed.choices.some((a) => a.a === 'end') && logs.live_delayed.ends.some((x) => x[2] === 'dropped'), 'delayed: an Endeavour was begun and replaced');
ok(logs.live_failed.prototypes.some((r) => !r.works), 'failed: a prototype failed');
ok(logs.live_failed.diffusion === false && logs.live_failed.settings.DIFF === '0', 'failed: played without diffusion, and the log says so');
const hm = logs.live_hailmary, hmCommit = hm.choices.find((a) => a.a === 'proto');
console.log('hailmary: committed on turn ' + hmCommit.t + ', certain on turn ' + (hm.cert && hm.cert[0]) + (hm.cert && hmCommit.t < hm.cert[0] ? ' (before certainty)' : ''));
logs.live_failed_oldformat = oldFormat(logs.live_failed);
logs.live_hailmary_oldformat = oldFormat(logs.live_hailmary);   // with diffusion: the rows seen abroad rebuilt from the rivals
for (const [k, log] of Object.entries(logs)) compare(k.replace('live_', ''), log);
// no rivals in the engine view of a game without diffusion
const gNoDiff = RP.reconstruct(bundle, logs.live_failed), vmE = V.researchModel(bundle, gNoDiff.snapshot(200), { engine: true });
ok(gNoDiff.rivals === 0 && vmE.engineInfo.rivalsAhead === null, 'a game without diffusion shows no rivals in the engine view');
// an economy the bundle lacks: a plain message
let msg = '';
try { RP.reconstruct(bundle, Object.assign({}, logs.live_failed, { econ: 0.9 })); } catch (err) { msg = err.message; }
ok(/×0.9 economy; the bundle has only ×1.0 and ×0.8/.test(msg), 'a log on another economy is refused in plain words: ' + msg);
if (out) {
  fs.mkdirSync(out, { recursive: true });
  for (const [k, log] of Object.entries(logs)) fs.writeFileSync(path.join(out, k + '.json'), JSON.stringify(log));
  console.log('logs written to ' + out);
}
console.log(fail ? fail + ' FAILED' : 'all passed');
process.exit(fail ? 1 : 0);
