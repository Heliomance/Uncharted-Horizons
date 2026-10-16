/* Node's results for the games test_browser.py plays in Chromium (written to stdout as JSON). */
'use strict';
const path = require('path');
const UHEngine = require(path.join(__dirname, '..', 'engine.js'));
const bundle = require(path.join(__dirname, '..', 'bundle.json'));
const res = {};
for (const [label, o] of [['generalist', { world: 'Process', econ: 0.8, game: 7, player: 'generalist' }],
  ['advisor', { world: 'familiar', econ: 1.0, game: 12, player: 'advisor' }]]) {
  const e = new UHEngine(bundle, o);
  while (!e.over) { e.step(); const a = e.advise(); if (o.player === 'advisor' && a.prototype) e.commitPrototype(a.prototype); }
  res[label] = { t: Object.fromEntries([...e.S.have].map(([k, v]) => [k, v.turn])), victory: e.victory, turn: e.turn };
}
process.stdout.write(JSON.stringify(res));
