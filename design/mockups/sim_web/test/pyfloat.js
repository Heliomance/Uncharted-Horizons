/* Test helpers for comparing JavaScript numbers with Python's: float.hex parsing, Python's round(x, n) (round half to even
   on the exact binary value, as CPython's correctly rounded dtoa does), and an exact float-to-decimal expansion. */
'use strict';

/** parse Python's float.hex() output exactly */
function fromHex(s) {
  if (s === 'inf') return Infinity;
  if (s === '-inf') return -Infinity;
  if (s === 'nan') return NaN;
  const m = /^(-?)0x([01])\.([0-9a-f]*)p([+-]\d+)$/.exec(s);
  if (!m) throw new Error('bad hex float ' + s);
  const sign = m[1] ? -1 : 1, frac = m[3];
  const mant = BigInt('0x' + m[2] + frac);
  const e = parseInt(m[4], 10) - 4 * frac.length;
  let v = Number(mant);                         // exact: at most 53 significant bits
  v = e >= 0 ? v * Math.pow(2, e) : v / Math.pow(2, -e);   // exact for normal results
  if (e < -1000) v = Number(mant) * Math.pow(2, e + 600) * Math.pow(2, -600);
  return sign * v;
}

/** the exact value of a finite double as a BigInt fraction {num, den} (den a power of two) */
function exact(x) {
  const buf = new DataView(new ArrayBuffer(8));
  buf.setFloat64(0, x);
  const hi = buf.getUint32(0), lo = buf.getUint32(4);
  const sign = hi >>> 31 ? -1n : 1n;
  const expBits = (hi >>> 20) & 0x7ff;
  let mant = (BigInt(hi & 0xfffff) << 32n) | BigInt(lo);
  let e;
  if (expBits === 0) e = -1074; else { mant |= 1n << 52n; e = expBits - 1075; }
  if (e >= 0) return { num: sign * (mant << BigInt(e)), den: 1n };
  return { num: sign * mant, den: 1n << BigInt(-e) };
}

/** Python's round(x, n) for a float x and an int n >= 0 */
function pyRound(x, n) {
  if (!Number.isFinite(x) || x === 0) return x;
  const { num, den } = exact(x);
  const scale = 10n ** BigInt(n);
  const neg = num < 0n;
  const a = (neg ? -num : num) * scale;
  let q = a / den; const r = a % den;
  if (2n * r > den || (2n * r === den && (q & 1n) === 1n)) q += 1n;
  if (q === 0n) return neg ? -0 : 0;
  let s = q.toString();
  if (n > 0) {
    s = s.padStart(n + 1, '0');
    s = s.slice(0, s.length - n) + '.' + s.slice(s.length - n);
  }
  return parseFloat((neg ? '-' : '') + s);
}

module.exports = { fromHex, exact, pyRound };
