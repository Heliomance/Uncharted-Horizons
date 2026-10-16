/* pyrandom.js's glibc ports (PyRandom.math: exp, log, pow with Python's special cases, fma) against Python, to the bit.
   Usage: python3 -I test/pymath_ref.py <dir> [millions] && node test/test_pymath.js <dir>
   Also reports how often JavaScript's own Math.exp, Math.log and Math.pow would have differed. */
'use strict';
const path = require('path'), fs = require('fs');
const PyRandom = require(path.join(__dirname, '..', 'pyrandom.js'));
const M = PyRandom.math, dir = path.resolve(process.argv[2]);
const same = (a, b) => (Number.isNaN(a) && Number.isNaN(b)) || (a === b && (a !== 0 || 1 / a === 1 / b));
let bad = 0;
function run(name, arity, mine, native) {
  const buf = fs.readFileSync(path.join(dir, name + '.bin'));
  const v = new Float64Array(buf.buffer, buf.byteOffset, buf.length / 8), w = arity + 1;
  let n = 0, wrong = 0, nat = 0;
  for (let i = 0; i + w <= v.length; i += w) {
    n++;
    const args = Array.from(v.subarray(i, i + arity)), want = v[i + arity];
    const got = mine(...args);
    if (!same(got, want)) { wrong++; if (wrong <= 5) console.log(`  ${name}(${args.join(', ')}): Python ${want}, port ${got}`); }
    if (native && !same(native(...args), want)) nat++;
  }
  bad += wrong;
  console.log(`${name.padEnd(4)} ${n} cases: ${n - wrong} identical to Python` + (native ? `; JavaScript's own would differ in ${nat} (${(100 * nat / n).toFixed(2)}%)` : ''));
}
run('exp', 1, M.exp, Math.exp);
run('log', 1, M.log, Math.log);
run('pow', 2, M.pow, Math.pow);
run('fma', 3, M.fma, null);
console.log(bad ? `${bad} MISMATCHES` : 'every result identical to Python\'s');
process.exit(bad ? 1 : 0);
