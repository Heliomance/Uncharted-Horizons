/* The human API, played by scripts: every world and both economies, to victory.
   Usage: node test/test_human.js [games_per_cell=3]

   Player "steady": each turn it funds the focus with the most revealed work (the revealed ideas under study there), as a
   player reading the research screen would; once the FTL screen opens it follows the screen's hints instead (open
   questions first, then the build of the method it believes in). It uses an occasional Grand Endeavour: on a revealed
   step of the true method's build that has not occurred (never more than one at a time). It commits the prototype of the
   true method once that method's build is complete (with or without certainty: it knows the answer), and plays on to the
   launch. Player "patient": the same, but commits only once the FTL screen shows certainty (what a real player can do).
   Player "gambler": picks a wrong hypothesis that still stands, funds and Endeavours its build, and commits its
   prototype as soon as it can; the prototype must fail and rule that method out, and the game must still reach victory.
   Also checked: serialize() and UHEngine.restore() reproduce the game exactly; snapshot() has the SPEC's keys. Victory turns
   are reported against base Civ V's science victory on the same income: 305 (good economy) and 380 (average). */
'use strict';
const path = require('path');
const UHEngine = require(path.join(__dirname, '..', 'engine.js'));
const bundle = require(path.join(__dirname, '..', 'bundle.json'));
const N = parseInt(process.argv[2] || '3', 10);
let failures = 0;
const check = (cond, msg) => { if (!cond) { failures++; console.log('FAIL: ' + msg); } };

function mostRevealedWork(e) {
  const S = e.S, w = new Map();
  for (const k of S.live) {
    if (S.have.has(k) || !e.isRevealed(k)) continue;
    const f = e.ROWS[k].focus; w.set(f, (w.get(f) || 0) + 1);
  }
  let best = null;
  for (const [f, n] of w) if (best === null || n > w.get(best) || (n === w.get(best) && f < best)) best = f;
  return best;
}

function play(e, style) {
  const log = { endeavours: 0, wrong: null, wrongResult: null, committed: null, firstFtl: null, gamble: null };
  const F = e.F;
  while (!e.over) {
    const st = e.S.have.has(e.OPENS) ? e.status(e.S.have, e.turn) : null;
    if (st && log.firstFtl === null) log.firstFtl = e.turn;
    const fx = st ? e.ftl({ hints: false }) : null;
    if (style === 'gambler' && fx && !log.wrong && !log.gamble) {      // a wrong horse: a proposed hypothesis that still stands
      const h = fx.hypotheses.find((x) => x.method !== e.method && x.proposed && x.alive);
      if (h) log.gamble = h.method;
    }
    if (log.gamble && !log.wrong && !st.alive.includes(log.gamble)) log.gamble = null;   // ruled out before it could be built
    const target = log.gamble && !log.wrong ? log.gamble : e.method;  // the method whose build it chases
    let focus = null;
    if (log.gamble && !log.wrong) { const g = F.BUILD[target].find((x) => !x.some((y) => e.S.have.has(y))); focus = g ? e.hintFocus(g) : null; }
    const advice = st ? e.advise() : null;
    e.setFocus(focus || (advice && advice.focus) || mostRevealedWork(e) || null);
    if (st && !e.S.proto && !e.S.protoWorked) {
      if (log.gamble && !log.wrong && !e.prototypeCheck(log.gamble)) {
        const r = e.commitPrototype(log.gamble); check(r.ok, 'wrong commit refused: ' + r.reason); log.wrong = log.gamble;
      }
      if (!e.S.proto && !e.prototypeCheck(e.method) && (style !== 'patient' || st.certain) && (style !== 'gambler' || !log.gamble || log.wrongResult !== null)) {
        const r = e.commitPrototype(e.method); check(r.ok, 'true commit refused'); log.committed = e.turn;
      }
      if (!e.S.proto && e.S.end_k === null && !e.S.endRequest) {        // an occasional Endeavour on a stuck build step
        for (const g of F.BUILD[target]) {
          if (g.some((x) => e.S.have.has(x))) continue;
          const k = g.find((x) => e.ROWS[x] && !e.S.occurred.has(x) && !e.endeavourCheck(x));
          if (k) { const r = e.requestEndeavour(k); check(r.ok, 'Endeavour refused: ' + r.reason); log.endeavours++; break; }
        }
      }
    }
    const ev = e.step();
    for (const x of ev) if (x.type === 'prototype_result' && x.method === log.wrong) log.wrongResult = x.works;
  }
  return log;
}

const results = {};
for (const style of ['steady', 'patient']) for (const world of ['familiar', 'Process', 'Substance']) for (const econ of [1.0, 0.8]) {
  const key = `${style} ${world} ${econ}`, vt = [];
  for (let g = 0; g < N; g++) {
    const e = new UHEngine(bundle, { world, econ, game: 100 + g * 7 + (econ === 1 ? 0 : 3), player: 'human' });
    const log = play(e, style);
    check(e.victory, `${key} game ${e.game} (${e.method}): no victory by turn ${e.turn}`);
    if (e.victory) vt.push(e.victory.turn);
    // serialize and restore: the same game, turn for turn
    const saved = JSON.parse(JSON.stringify(e.serialize()));
    const r = UHEngine.restore(bundle, saved);
    check(r.turn === e.turn && JSON.stringify(r.snapshot({ ftl: false }).have) === JSON.stringify(e.snapshot({ ftl: false }).have) &&
      JSON.stringify(r.victory) === JSON.stringify(e.victory), `${key} game ${e.game}: restore differs`);
    console.log(`${key.padEnd(21)} game ${String(e.game).padStart(3)} ${e.method.padEnd(10)} victory turn ${e.victory ? e.victory.turn : '-'}` +
      ` (vs ${UHEngine.REFERENCE[e.econ]}: ${e.victory ? (e.victory.delta >= 0 ? '+' : '') + e.victory.delta : '-'}); FTL screen from ${log.firstFtl},` +
      ` certain ${e.S.cert}, prototype committed ${log.committed}, ${log.endeavours} Endeavour(s); ${saved.actions.length} choices saved, restored identically`);
  }
  results[key] = vt;
}

// the gambler: a wrong prototype first
let gambled = 0;
for (let g = 0; g < 90 && gambled < 4; g++) {
  const world = ['familiar', 'Process', 'Substance'][g % 3];
  const e = new UHEngine(bundle, { world, econ: 1.0, game: 200 + g, player: 'human' });
  const log = play(e, 'gambler');
  if (!log.wrong) continue;
  gambled++;
  check(log.wrongResult === false, `gambler: the wrong prototype (${log.wrong}) did not fail`);
  check(e.S.protoFailed.has(log.wrong), 'gambler: the failed method is not ruled out');
  const h = e.ftl().hypotheses.find((x) => x.method === log.wrong);
  check(h && !h.alive && h.prototypeFailed, 'gambler: the FTL screen does not show the failed prototype');
  check(e.commitPrototype(log.wrong).ok === false, 'gambler: a failed method can be committed again');
  check(e.victory, 'gambler: no victory after the failed prototype');
  const res = e.S.protoResults.map((x) => `${x.method} ${x.works ? 'works' : 'fails'} (turn ${x.turn})`).join(', ');
  console.log(`gambler ${world.padEnd(9)} 1.0 game ${e.game} (${e.method}): committed ${log.wrong} first; results: ${res}; victory turn ${e.victory ? e.victory.turn : '-'}`);
}
check(gambled > 0, 'gambler: no game offered a wrong prototype');

// save and restore after random choices: focus (or automatic), Endeavours started, replaced and stopped, prototypes
for (let g = 0; g < 6; g++) {
  const world = ['familiar', 'Process', 'Substance'][g % 3], econ = g < 3 ? 1.0 : 0.8;
  const e = new UHEngine(bundle, { world, econ, game: 40 + g, player: 'human' });
  const r = new UHEngine.PyRandom(900 + g), foci = bundle.foci.map((f) => f.name);
  let acts = 0;
  while (!e.over && e.turn < 520) {
    const x = r.random();
    if (x < 0.15) { e.setFocus(r.random() < 0.3 ? null : r.choice(foci)); acts++; }
    else if (x < 0.22) {
      const cands = e.IDS.filter((k) => !e.endeavourCheck(k));
      if (cands.length && e.requestEndeavour(r.choice(cands)).ok) acts++;
    } else if (x < 0.24 && e.S.end_k !== null) { e.stopEndeavour(); acts++; }
    const ok = e.METHODS.filter((o) => !e.prototypeCheck(o));
    if (ok.length && r.random() < 0.5) { e.commitPrototype(r.choice(ok)); acts++; }
    e.step();
  }
  const saved = JSON.parse(JSON.stringify(e.serialize()));
  const back = UHEngine.restore(bundle, saved);
  const a = JSON.stringify(e.snapshot()), b = JSON.stringify(back.snapshot());
  check(a === b && JSON.stringify(e.S.log) === JSON.stringify(back.S.log), `random choices ${world} ${econ}: restore differs`);
  console.log(`random  ${world.padEnd(9)} ${econ} game ${e.game}: ${acts} choices to turn ${e.turn}` +
    `${e.victory ? ', victory turn ' + e.victory.turn : ''}; prototypes ${e.S.protoResults.map((p) => p.method + (p.works ? ' works' : ' fails')).join(', ') || 'none'}; ` +
    `restored: ${a === b ? 'identical snapshot and event log' : 'DIFFERENT'}`);
}

// the snapshot's shape (SPEC.md)
const e = new UHEngine(bundle, { world: 'familiar', econ: 1.0, game: 3, player: 'human' });
for (let i = 0; i < 260; i++) e.step();
const s = e.snapshot();
for (const k of ['turn', 'world', 'ontology', 'econ', 'd', 'inc', 'share', 'funded', 'endeavour', 'prototype', 'drive', 'victory', 'have', 'occurred',
  'glimpsed', 'seen', 'lost', 'locked', 'prog', 'flow', 'events', 'ftl']) check(k in s, 'snapshot lacks ' + k);
check(JSON.stringify(s).length > 1000, 'snapshot is empty');
const q = e.endeavourQuote(Object.keys(e.ROWS).find((k) => !e.S.have.has(k) && e.S.met.has(k)));
check(q && q.cost > 0 && q.turns >= 1, 'endeavourQuote');

const med = (a) => { const b = a.slice().sort((x, y) => x - y); return b.length ? (b.length % 2 ? b[(b.length - 1) / 2] : (b[b.length / 2 - 1] + b[b.length / 2]) / 2) : null; };
console.log('\nvictory turns (median; base Civ V reference on the same income):');
for (const [k, v] of Object.entries(results)) console.log(`  ${k.padEnd(21)} ${v.join(', ').padEnd(24)} median ${med(v)} (reference ${k.endsWith('0.8') ? 380 : 305})`);
console.log(failures ? `\n${failures} FAILURES` : '\nall human API checks passed');
process.exit(failures ? 1 : 0);
