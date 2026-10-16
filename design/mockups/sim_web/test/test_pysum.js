/* engine.js's pysum (CPython 3.12+'s compensated float sum) against Python's sum(), to the bit (signs of zero included).
   Usage: python3 -I test/pysum_ref.py <ref.json> && node test/test_pysum.js <ref.json> */
'use strict';
const path = require('path');
const { pysum } = require(path.join(__dirname, '..', 'engine.js'));
const { fromHex } = require('./pyfloat.js');
const cases = require(path.resolve(process.argv[2]));
let bad = 0, naive = 0;
const eq = (a, b) => (Number.isNaN(a) && Number.isNaN(b)) || (a === b && 1 / a === 1 / b);
for (const [xs, s] of cases) {   // (an empty list sums to the int 0, written here as 0.0)
  const v = xs.map(fromHex), want = fromHex(s), got = pysum(v);
  if (!eq(got, want)) { bad++; if (bad < 10) console.log('MISMATCH', xs.slice(0, 5), got, want); }
  if (!eq(v.reduce((a, b) => a + b, 0), want)) naive++;
}
console.log(`pysum: ${cases.length - bad} of ${cases.length} sums identical to Python's sum() (a plain left-to-right sum would differ in ${naive})`);
process.exit(bad ? 1 : 0);
