/* pyrandom.js against CPython's random.Random, draw by draw.
   Usage: python3 -I test/pyrandom_ref.py <ref.json> && node test/test_pyrandom.js <ref.json>
   Every random(), getrandbits(k), _randbelow(n), choice, choices, cum_weights choice and gammavariate must be identical
   to the bit (gammavariate through pyrandom.js's ports of glibc's log and exp, as Python computes them). With
   PyRandom.math.native (JavaScript's Math.log and Math.exp) about one gammavariate value in ten would differ in the
   last bit; the test reports that too, for comparison. */
'use strict';
const path = require('path');
const PyRandom = require(path.join(__dirname, '..', 'pyrandom.js'));
const { fromHex } = require('./pyfloat.js');
const ref = require(path.resolve(process.argv[2]));

let ops = 0, bad = 0, gammaUlp = 0, gammaN = 0, maxRel = 0;
const fail = (msg) => { bad++; if (bad <= 10) console.log('MISMATCH', msg); };
for (const rec of ref) {
  const seed = BigInt(rec.seed);
  const r = new PyRandom(seed >= -(2n ** 52n) && seed <= 2n ** 52n ? Number(seed) : seed);
  for (const op of rec.ops) {
    ops++;
    switch (op[0]) {
      case 'random': { const v = r.random(), w = fromHex(op[1]); if (v !== w) fail(`seed ${rec.seed} random ${v} != ${w}`); break; }
      case 'getrandbits': { const v = String(r.getrandbits(op[1])); if (v !== op[2]) fail(`seed ${rec.seed} getrandbits(${op[1]}) ${v} != ${op[2]}`); break; }
      case 'randbelow': {
        const n = BigInt(op[1]);
        const v = String(n <= 2n ** 53n ? r._randbelow(Number(n)) : r._randbelow(n));
        if (v !== op[2]) fail(`seed ${rec.seed} _randbelow(${op[1]}) ${v} != ${op[2]}`); break;
      }
      case 'choice': { const seq = Array.from({ length: op[1] }, (_, i) => i); const v = r.choice(seq); if (v !== op[2]) fail(`seed ${rec.seed} choice(len ${op[1]}) ${v} != ${op[2]}`); break; }
      case 'choices': {   // the reference drew its weights from the same generator first
        const w = op[1].map((_, j) => r.random() * (j + 1));
        if (w.some((x, j) => x !== fromHex(op[1][j]))) fail(`seed ${rec.seed} choices' weights differ`);
        const v = r.choices(w.map((_, i) => i), w)[0]; if (v !== op[2]) fail(`seed ${rec.seed} choices ${v} != ${op[2]}`); break;
      }
      case 'cum_choices': {
        const cw = op[1].map(fromHex); const v = r.choices(cw.map((_, i) => i), null, { cum_weights: cw, k: 3 });
        if (JSON.stringify(v) !== JSON.stringify(op[2])) fail(`seed ${rec.seed} cum choices ${v} != ${op[2]}`); break;
      }
      case 'gamma': {
        const st = r.getstate(), v = r.gammavariate(op[1], op[2]), w = fromHex(op[3]); gammaN++;
        if (v !== w) fail(`seed ${rec.seed} gammavariate(${op[1]}, ${op[2]}) ${v} != ${w}`);
        const r2 = new PyRandom(0); r2.setstate(st);                // the same draw with JavaScript's own log and exp
        const keep = PyRandom.math; PyRandom.math = Object.assign({}, keep, keep.native);
        const vn = r2.gammavariate(op[1], op[2]); PyRandom.math = keep;
        if (vn !== w) { gammaUlp++; maxRel = Math.max(maxRel, Math.abs(vn - w) / Math.abs(w)); }
        break;
      }
      default: throw new Error('unknown op ' + op[0]);
    }
  }
}
console.log(`pyrandom: ${ops} operations over ${ref.length} seeds; mismatches ${bad} (gammavariate: ${gammaN} values, all compared to the bit; ` +
  `with JavaScript's own log and exp ${gammaUlp} would differ, by up to ${maxRel.toExponential(2)} of their value)`);
process.exit(bad ? 1 : 0);
