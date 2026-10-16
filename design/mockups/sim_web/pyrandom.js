/* Python's random.Random, bit for bit (CPython 3.13, Lib/random.py and Modules/_randommodule.c).

   MT19937 seeded as CPython seeds it from an int (its absolute value split into 32-bit words, least significant first,
   then init_by_array), random() from two 32-bit words (27 + 26 bits), getrandbits(k), _randbelow(n) by rejection on
   getrandbits(n.bit_length()), choice, choices (with weights or cumulative weights: accumulate, then bisect_right) and
   gammavariate (all three branches, the same arithmetic as Python's).

   gammavariate and expovariate call log and exp, which Python takes from the C library. PyRandom.math holds ports of
   glibc 2.39's exp, log and pow as Python calls them on x86-64 with FMA, to the bit ({log, exp, pow, fma}; pow with
   Python's own special cases first), so gammavariate's values match Python's exactly; the engine uses the same pow.
   (JavaScript's Math.exp, Math.log and Math.pow differ from glibc's in the last bit for 2-10% of arguments, and between
   browsers; they are kept as PyRandom.math.native.)

   Works in Node (module.exports) and the browser (window.PyRandom). No dependencies. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.PyRandom = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  const N = 624, M = 397, MATRIX_A = 0x9908b0df, UPPER_MASK = 0x80000000, LOWER_MASK = 0x7fffffff;
  // Python's module constants, as Python computes them (math.log(4.0), 1.0 + math.log(4.5), math.e)
  const LOG4 = 1.3862943611198906, SG_MAGICCONST = 2.504077396776274, E = 2.718281828459045;
  const RECIP53 = 1.0 / 9007199254740992.0;

  /** the 32-bit words of a non-negative integer, least significant first (CPython's random_seed) */
  function seedWords(seed) {
    let n;
    if (typeof seed === 'bigint') n = seed < 0n ? -seed : seed;
    else {
      if (!Number.isInteger(seed)) throw new TypeError('PyRandom: seed must be an integer (Python hashes other types)');
      n = BigInt(Math.abs(seed));
    }
    const words = [];
    if (n === 0n) return [0];
    while (n > 0n) { words.push(Number(n & 0xffffffffn)); n >>= 32n; }
    return words;
  }

  class PyRandom {
    constructor(seed) {
      this.mt = new Uint32Array(N);
      this.index = N + 1;
      if (seed !== undefined) this.seed(seed);
    }

    init_genrand(s) {
      const mt = this.mt;
      mt[0] = s >>> 0;
      for (let i = 1; i < N; i++) {
        const p = mt[i - 1] ^ (mt[i - 1] >>> 30);
        mt[i] = (Math.imul(1812433253, p) + i) >>> 0;
      }
      this.index = N;
    }

    init_by_array(key) {
      const mt = this.mt, klen = key.length;
      this.init_genrand(19650218);
      let i = 1, j = 0;
      for (let k = (N > klen ? N : klen); k; k--) {
        const p = mt[i - 1] ^ (mt[i - 1] >>> 30);
        mt[i] = ((mt[i] ^ Math.imul(p, 1664525)) >>> 0) + key[j] + j;   // Uint32Array keeps it modulo 2^32
        i++; j++;
        if (i >= N) { mt[0] = mt[N - 1]; i = 1; }
        if (j >= klen) j = 0;
      }
      for (let k = N - 1; k; k--) {
        const p = mt[i - 1] ^ (mt[i - 1] >>> 30);
        mt[i] = ((mt[i] ^ Math.imul(p, 1566083941)) >>> 0) - i;
        i++;
        if (i >= N) { mt[0] = mt[N - 1]; i = 1; }
      }
      mt[0] = 0x80000000;
    }

    /** Random.seed(a) for an int a (version 2 seeding of an int is the int itself) */
    seed(a) { this.init_by_array(seedWords(a)); }

    genrand_uint32() {
      const mt = this.mt;
      let y;
      if (this.index >= N) {
        let kk;
        for (kk = 0; kk < N - M; kk++) {
          y = (mt[kk] & UPPER_MASK) | (mt[kk + 1] & LOWER_MASK);
          mt[kk] = mt[kk + M] ^ (y >>> 1) ^ ((y & 1) ? MATRIX_A : 0);
        }
        for (; kk < N - 1; kk++) {
          y = (mt[kk] & UPPER_MASK) | (mt[kk + 1] & LOWER_MASK);
          mt[kk] = mt[kk + (M - N)] ^ (y >>> 1) ^ ((y & 1) ? MATRIX_A : 0);
        }
        y = (mt[N - 1] & UPPER_MASK) | (mt[0] & LOWER_MASK);
        mt[N - 1] = mt[M - 1] ^ (y >>> 1) ^ ((y & 1) ? MATRIX_A : 0);
        this.index = 0;
      }
      y = mt[this.index++];
      y ^= (y >>> 11);
      y ^= (y << 7) & 0x9d2c5680;
      y ^= (y << 15) & 0xefc60000;
      y ^= (y >>> 18);
      return y >>> 0;
    }

    /** [0, 1) with 53 random bits */
    random() {
      const a = this.genrand_uint32() >>> 5, b = this.genrand_uint32() >>> 6;
      return (a * 67108864.0 + b) * RECIP53;
    }

    /** an int with k random bits: a Number up to 53 bits, a BigInt beyond */
    getrandbits(k) {
      if (k < 0) throw new RangeError('number of bits must be non-negative');
      if (k === 0) return 0;
      if (k <= 32) return this.genrand_uint32() >>> (32 - k);
      if (k <= 53) {
        let v = 0, mult = 1;
        for (let left = k; left > 0; left -= 32) {
          let r = this.genrand_uint32();
          if (left < 32) r >>>= (32 - left);
          v += r * mult; mult *= 4294967296;
        }
        return v;
      }
      let v = 0n, sh = 0n;
      for (let left = k; left > 0; left -= 32) {
        let r = this.genrand_uint32();
        if (left < 32) r >>>= (32 - left);
        v |= BigInt(r) << sh; sh += 32n;
      }
      return v;
    }

    /** a random int in [0, n), n > 0 (Random._randbelow_with_getrandbits) */
    _randbelow(n) {
      if (typeof n === 'bigint') {
        const k = n.toString(2).length;
        let r = BigInt(this.getrandbits(k));
        while (r >= n) r = BigInt(this.getrandbits(k));
        return r;
      }
      const k = bitLength(n);
      let r = this.getrandbits(k);
      while (r >= n) r = this.getrandbits(k);
      return r;
    }

    randrange(start, stop) {
      if (stop === undefined) return this._randbelow(start);
      return start + this._randbelow(stop - start);
    }

    randint(a, b) { return this.randrange(a, b + 1); }

    choice(seq) {
      if (!seq.length) throw new RangeError('Cannot choose from an empty sequence');
      return seq[this._randbelow(seq.length)];
    }

    /** Random.choices(population, weights=None, *, cum_weights=None, k=1) */
    choices(population, weights, opts) {
      const o = opts || {};
      const k = o.k === undefined ? 1 : o.k;
      const n = population.length;
      let cum = o.cum_weights || null;
      if (!cum) {
        if (!weights) {
          const nf = n + 0.0, out = [];
          for (let i = 0; i < k; i++) out.push(population[Math.floor(this.random() * nf)]);
          return out;
        }
        cum = []; let acc;
        for (let i = 0; i < weights.length; i++) { acc = i === 0 ? weights[0] : acc + weights[i]; cum.push(acc); }
      } else if (weights) throw new TypeError('Cannot specify both weights and cumulative weights');
      if (cum.length !== n) throw new RangeError('The number of weights does not match the population');
      const total = cum[cum.length - 1] + 0.0;
      if (!(total > 0.0)) throw new RangeError('Total of weights must be greater than zero');
      if (!Number.isFinite(total)) throw new RangeError('Total of weights must be finite');
      const hi = n - 1, out = [];
      for (let i = 0; i < k; i++) out.push(population[bisectRight(cum, this.random() * total, 0, hi)]);
      return out;
    }

    uniform(a, b) { return a + (b - a) * this.random(); }

    shuffle(x) {
      for (let i = x.length - 1; i > 0; i--) {
        const j = this._randbelow(i + 1);
        const t = x[i]; x[i] = x[j]; x[j] = t;
      }
      return x;
    }

    expovariate(lambd) { return -PyRandom.math.log(1.0 - this.random()) / lambd; }

    gammavariate(alpha, beta) {
      if (alpha <= 0.0 || beta <= 0.0) throw new RangeError('gammavariate: alpha and beta must be > 0.0');
      const { log, exp, pow } = PyRandom.math;
      if (alpha > 1.0) {
        // R.C.H. Cheng, "The generation of Gamma variables with non-integral shape parameters", Applied Statistics (1977)
        const ainv = Math.sqrt(2.0 * alpha - 1.0);
        const bbb = alpha - LOG4;
        const ccc = alpha + ainv;
        for (;;) {
          const u1 = this.random();
          if (!(1e-7 < u1 && u1 < 0.9999999)) continue;
          const u2 = 1.0 - this.random();
          const v = log(u1 / (1.0 - u1)) / ainv;
          const x = alpha * exp(v);
          const z = u1 * u1 * u2;
          const r = bbb + ccc * v - x;
          if (r + SG_MAGICCONST - 4.5 * z >= 0.0 || r >= log(z)) return x * beta;
        }
      } else if (alpha === 1.0) {
        return -log(1.0 - this.random()) * beta;
      }
      // alpha between 0 and 1 (exclusive): ALGORITHM GS of Statistical Computing, Kennedy & Gentle
      let x;
      for (;;) {
        const u = this.random();
        const b = (E + alpha) / E;
        const p = b * u;
        if (p <= 1.0) x = pow(p, 1.0 / alpha);
        else x = -log((b - p) / alpha);
        const u1 = this.random();
        if (p > 1.0) {
          if (u1 <= pow(x, alpha - 1.0)) break;
        } else if (u1 <= exp(-x)) break;
      }
      return x * beta;
    }

    /** the generator's state, as Random.getstate()'s middle element: 624 words and the index */
    getstate() { return { mt: Array.from(this.mt), index: this.index }; }
    setstate(s) { this.mt = Uint32Array.from(s.mt); this.index = s.index; }
  }

  function bitLength(n) {
    if (n <= 0) return 0;
    if (n < 4294967296) return 32 - Math.clz32(n);
    return 64 - Math.clz32(Math.floor(n / 4294967296));   // exact for integers below 2^53
  }

  /** bisect.bisect_right(a, x, lo, hi) */
  function bisectRight(a, x, lo, hi) {
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (x < a[mid]) hi = mid; else lo = mid + 1;
    }
    return lo;
  }


  // ---- glibc's exp, log and pow, bit for bit ---------------------------------------------------------------------------
  // Python's math.log and math.exp and its float ** float call the C library. On x86-64 with FMA (where the simulator runs)
  // glibc 2.39 selects the FMA builds of exp, log and pow (sysdeps/ieee754/dbl-64/e_exp.c, e_log.c, e_pow.c, compiled
  // with -mfma, so the compiler fuses many multiply-adds). These are ports of those builds, operation by operation as
  // their machine code does them (read from libm.so.6), with the same tables and an exact fused multiply-add, so that
  // they return the same double as Python's for every argument (test/test_pymath.js checks millions). JavaScript's own
  // Math.exp, Math.log and Math.pow differ from glibc's in the last bit for 2-10% of arguments, and from one browser to
  // another.
  // glibc 2.39's tables (sysdeps/ieee754/dbl-64/e_exp_data.c, e_log_data.c, e_pow_log_data.c), as 64-bit words
  const EXP_DATA = [
    '40671547652b82fe', '4338000000000000', 'bf762e42fefa0000', 'bd0cf79abc9e3b3a', '3fdffffffffffdbd', '3fc555555555543c',
    '3fa55555cf172b91', '3f81111167a4d017'];   // invln2N, shift, negln2hiN, negln2loN, poly[4]
  const EXP_TAB = [
    '0000000000000000', '3ff0000000000000', '3c9b3b4f1a88bf6e', '3feff63da9fb3335', 'bc7160139cd8dc5d', '3fefec9a3e778061',
    'bc905e7a108766d1', '3fefe315e86e7f85', '3c8cd2523567f613', '3fefd9b0d3158574', 'bc8bce8023f98efa', '3fefd06b29ddf6de',
    '3c60f74e61e6c861', '3fefc74518759bc8', '3c90a3e45b33d399', '3fefbe3ecac6f383', '3c979aa65d837b6d', '3fefb5586cf9890f',
    '3c8eb51a92fdeffc', '3fefac922b7247f7', '3c3ebe3d702f9cd1', '3fefa3ec32d3d1a2', 'bc6a033489906e0b', '3fef9b66affed31b',
    'bc9556522a2fbd0e', '3fef9301d0125b51', 'bc5080ef8c4eea55', '3fef8abdc06c31cc', 'bc91c923b9d5f416', '3fef829aaea92de0',
    '3c80d3e3e95c55af', '3fef7a98c8a58e51', 'bc801b15eaa59348', '3fef72b83c7d517b', 'bc8f1ff055de323d', '3fef6af9388c8dea',
    '3c8b898c3f1353bf', '3fef635beb6fcb75', 'bc96d99c7611eb26', '3fef5be084045cd4', '3c9aecf73e3a2f60', '3fef54873168b9aa',
    'bc8fe782cb86389d', '3fef4d5022fcd91d', '3c8a6f4144a6c38d', '3fef463b88628cd6', '3c807a05b0e4047d', '3fef3f49917ddc96',
    '3c968efde3a8a894', '3fef387a6e756238', '3c875e18f274487d', '3fef31ce4fb2a63f', '3c80472b981fe7f2', '3fef2b4565e27cdd',
    'bc96b87b3f71085e', '3fef24dfe1f56381', '3c82f7e16d09ab31', '3fef1e9df51fdee1', 'bc3d219b1a6fbffa', '3fef187fd0dad990',
    '3c8b3782720c0ab4', '3fef1285a6e4030b', '3c6e149289cecb8f', '3fef0cafa93e2f56', '3c834d754db0abb6', '3fef06fe0a31b715',
    '3c864201e2ac744c', '3fef0170fc4cd831', '3c8fdd395dd3f84a', '3feefc08b26416ff', 'bc86a3803b8e5b04', '3feef6c55f929ff1',
    'bc924aedcc4b5068', '3feef1a7373aa9cb', 'bc9907f81b512d8e', '3feeecae6d05d866', 'bc71d1e83e9436d2', '3feee7db34e59ff7',
    'bc991919b3ce1b15', '3feee32dc313a8e5', '3c859f48a72a4c6d', '3feedea64c123422', 'bc9312607a28698a', '3feeda4504ac801c',
    'bc58a78f4817895b', '3feed60a21f72e2a', 'bc7c2c9b67499a1b', '3feed1f5d950a897', '3c4363ed60c2ac11', '3feece086061892d',
    '3c9666093b0664ef', '3feeca41ed1d0057', '3c6ecce1daa10379', '3feec6a2b5c13cd0', '3c93ff8e3f0f1230', '3feec32af0d7d3de',
    '3c7690cebb7aafb0', '3feebfdad5362a27', '3c931dbdeb54e077', '3feebcb299fddd0d', 'bc8f94340071a38e', '3feeb9b2769d2ca7',
    'bc87deccdc93a349', '3feeb6daa2cf6642', 'bc78dec6bd0f385f', '3feeb42b569d4f82', 'bc861246ec7b5cf6', '3feeb1a4ca5d920f',
    '3c93350518fdd78e', '3feeaf4736b527da', '3c7b98b72f8a9b05', '3feead12d497c7fd', '3c9063e1e21c5409', '3feeab07dd485429',
    '3c34c7855019c6ea', '3feea9268a5946b7', '3c9432e62b64c035', '3feea76f15ad2148', 'bc8ce44a6199769f', '3feea5e1b976dc09',
    'bc8c33c53bef4da8', '3feea47eb03a5585', 'bc845378892be9ae', '3feea34634ccc320', 'bc93cedd78565858', '3feea23882552225',
    '3c5710aa807e1964', '3feea155d44ca973', 'bc93b3efbf5e2228', '3feea09e667f3bcd', 'bc6a12ad8734b982', '3feea012750bdabf',
    'bc6367efb86da9ee', '3fee9fb23c651a2f', 'bc80dc3d54e08851', '3fee9f7df9519484', 'bc781f647e5a3ecf', '3fee9f75e8ec5f74',
    'bc86ee4ac08b7db0', '3fee9f9a48a58174', 'bc8619321e55e68a', '3fee9feb564267c9', '3c909ccb5e09d4d3', '3feea0694fde5d3f',
    'bc7b32dcb94da51d', '3feea11473eb0187', '3c94ecfd5467c06b', '3feea1ed0130c132', '3c65ebe1abd66c55', '3feea2f336cf4e62',
    'bc88a1c52fb3cf42', '3feea427543e1a12', 'bc9369b6f13b3734', '3feea589994cce13', 'bc805e843a19ff1e', '3feea71a4623c7ad',
    'bc94d450d872576e', '3feea8d99b4492ed', '3c90ad675b0e8a00', '3feeaac7d98a6699', '3c8db72fc1f0eab4', '3feeace5422aa0db',
    'bc65b6609cc5e7ff', '3feeaf3216b5448c', '3c7bf68359f35f44', '3feeb1ae99157736', 'bc93091fa71e3d83', '3feeb45b0b91ffc6',
    'bc5da9b88b6c1e29', '3feeb737b0cdc5e5', 'bc6c23f97c90b959', '3feeba44cbc8520f', 'bc92434322f4f9aa', '3feebd829fde4e50',
    'bc85ca6cd7668e4b', '3feec0f170ca07ba', '3c71affc2b91ce27', '3feec49182a3f090', '3c6dd235e10a73bb', '3feec86319e32323',
    'bc87c50422622263', '3feecc667b5de565', '3c8b1c86e3e231d5', '3feed09bec4a2d33', 'bc91bbd1d3bcbb15', '3feed503b23e255d',
    '3c90cc319cee31d2', '3feed99e1330b358', '3c8469846e735ab3', '3feede6b5579fdbf', 'bc82dfcd978e9db4', '3feee36bbfd3f37a',
    '3c8c1a7792cb3387', '3feee89f995ad3ad', 'bc907b8f4ad1d9fa', '3feeee07298db666', 'bc55c3d956dcaeba', '3feef3a2b84f15fb',
    'bc90a40e3da6f640', '3feef9728de5593a', 'bc68d6f438ad9334', '3feeff76f2fb5e47', 'bc91eee26b588a35', '3fef05b030a1064a',
    '3c74ffd70a5fddcd', '3fef0c1e904bc1d2', 'bc91bdfbfa9298ac', '3fef12c25bd71e09', '3c736eae30af0cb3', '3fef199bdd85529c',
    '3c8ee3325c9ffd94', '3fef20ab5fffd07a', '3c84e08fd10959ac', '3fef27f12e57d14b', '3c63cdaf384e1a67', '3fef2f6d9406e7b5',
    '3c676b2c6c921968', '3fef3720dcef9069', 'bc808a1883ccb5d2', '3fef3f0b555dc3fa', 'bc8fad5d3ffffa6f', '3fef472d4a07897c',
    'bc900dae3875a949', '3fef4f87080d89f2', '3c74a385a63d07a7', '3fef5818dcfba487', 'bc82919e2040220f', '3fef60e316c98398',
    '3c8e5a50d5c192ac', '3fef69e603db3285', '3c843a59ac016b4b', '3fef7321f301b460', 'bc82d52107b43e1f', '3fef7c97337b9b5f',
    'bc892ab93b470dc9', '3fef864614f5a129', '3c74b604603a88d3', '3fef902ee78b3ff6', '3c83c5ec519d7271', '3fef9a51fbc74c83',
    'bc8ff7128fd391f0', '3fefa4afa2a490da', 'bc8dae98e223747d', '3fefaf482d8e67f1', '3c8ec3bc41aa2008', '3fefba1bee615a27',
    '3c842b94c3a9eb32', '3fefc52b376bba97', '3c8a64a931d185ee', '3fefd0765b6e4540', 'bc8e37bae43be3ed', '3fefdbfdad9cbe14',
    '3c77893b4d91cd9d', '3fefe7c1819e90d8', '3c5305c14160cc89', '3feff3c22b8f71f1'];
  const LOG_DATA = [
    '3fe62e42fefa3800', '3d2ef35793c76730', 'bfe0000000000001', '3fd555555551305b', 'bfcfffffffeb4590', '3fc999b324f10111',
    'bfc55575e506c89f', 'bfe0000000000000', '3fd5555555555577', 'bfcffffffffffdcb', '3fc999999995dd0c', 'bfc55555556745a7',
    '3fc24924a344de30', 'bfbfffffa4423d65', '3fbc7184282ad6ca', 'bfb999eb43b068ff', '3fb78182f7afd085', 'bfb5521375d145cd'];   // ln2hi, ln2lo, poly[5], poly1[11]
  const LOG_TAB = [
    '3ff734f0c3e0de9f', 'bfd7cc7f79e69000', '3ff713786a2ce91f', 'bfd76feec20d0000', '3ff6f26008fab5a0', 'bfd713e31351e000',
    '3ff6d1a61f138c7d', 'bfd6b85b38287800', '3ff6b1490bc5b4d1', 'bfd65d5590807800', '3ff69147332f0cba', 'bfd602d076180000',
    '3ff6719f18224223', 'bfd5a8ca86909000', '3ff6524f99a51ed9', 'bfd54f4356035000', '3ff63356aa8f24c4', 'bfd4f637c36b4000',
    '3ff614b36b9ddc14', 'bfd49da7fda85000', '3ff5f66452c65c4c', 'bfd445923989a800', '3ff5d867b5912c4f', 'bfd3edf439b0b800',
    '3ff5babccb5b90de', 'bfd396ce448f7000', '3ff59d61f2d91a78', 'bfd3401e17bda000', '3ff5805612465687', 'bfd2e9e2ef468000',
    '3ff56397cee76bd3', 'bfd2941b3830e000', '3ff54725e2a77f93', 'bfd23ec58cda8800', '3ff52aff42064583', 'bfd1e9e129279000',
    '3ff50f22dbb2bddf', 'bfd1956d2b48f800', '3ff4f38f4734ded7', 'bfd141679ab9f800', '3ff4d843cfde2840', 'bfd0edd094ef9800',
    '3ff4bd3ec078a3c8', 'bfd09aa518db1000', '3ff4a27fc3e0258a', 'bfd047e65263b800', '3ff4880524d48434', 'bfcfeb224586f000',
    '3ff46dce1b192d0b', 'bfcf474a7517b000', '3ff453d9d3391854', 'bfcea4443d103000', '3ff43a2744b4845a', 'bfce020d44e9b000',
    '3ff420b54115f8fb', 'bfcd60a22977f000', '3ff40782da3ef4b1', 'bfccc00104959000', '3ff3ee8f5d57fe8f', 'bfcc202956891000',
    '3ff3d5d9a00b4ce9', 'bfcb81178d811000', '3ff3bd60c010c12b', 'bfcae2c9ccd3d000', '3ff3a5242b75dab8', 'bfca45402e129000',
    '3ff38d22cd9fd002', 'bfc9a877681df000', '3ff3755bc5847a1c', 'bfc90c6d69483000', '3ff35dce49ad36e2', 'bfc87120a645c000',
    '3ff34679984dd440', 'bfc7d68fb4143000', '3ff32f5cceffcb24', 'bfc73cb83c627000', '3ff3187775a10d49', 'bfc6a39a9b376000',
    '3ff301c8373e3990', 'bfc60b3154b7a000', '3ff2eb4ebb95f841', 'bfc5737d76243000', '3ff2d50a0219a9d1', 'bfc4dc7b8fc23000',
    '3ff2bef9a8b7fd2a', 'bfc4462c51d20000', '3ff2a91c7a0c1bab', 'bfc3b08abc830000', '3ff293726014b530', 'bfc31b996b490000',
    '3ff27dfa5757a1f5', 'bfc2875490a44000', '3ff268b39b1d3bbf', 'bfc1f3b9f879a000', '3ff2539d838ff5bd', 'bfc160c8252ca000',
    '3ff23eb7aac9083b', 'bfc0ce7f57f72000', '3ff22a012ba940b6', 'bfc03cdc49fea000', '3ff2157996cc4132', 'bfbf57bdbc4b8000',
    '3ff201201dd2fc9b', 'bfbe370896404000', '3ff1ecf4494d480b', 'bfbd17983ef94000', '3ff1d8f5528f6569', 'bfbbf9674ed8a000',
    '3ff1c52311577e7c', 'bfbadc79202f6000', '3ff1b17c74cb26e9', 'bfb9c0c3e7288000', '3ff19e010c2c1ab6', 'bfb8a646b372c000',
    '3ff18ab07bb670bd', 'bfb78d01b3ac0000', '3ff1778a25efbcb6', 'bfb674f145380000', '3ff1648d354c31da', 'bfb55e0e6d878000',
    '3ff151b990275fdd', 'bfb4485cdea1e000', '3ff13f0ea432d24c', 'bfb333d94d6aa000', '3ff12c8b7210f9da', 'bfb22079f8c56000',
    '3ff11a3028ecb531', 'bfb10e4698622000', '3ff107fbda8434af', 'bfaffa6c6ad20000', '3ff0f5ee0f4e6bb3', 'bfadda8d4a774000',
    '3ff0e4065d2a9fce', 'bfabbcece4850000', '3ff0d244632ca521', 'bfa9a1894012c000', '3ff0c0a77ce2981a', 'bfa788583302c000',
    '3ff0af2f83c636d1', 'bfa5715e67d68000', '3ff09ddb98a01339', 'bfa35c8a49658000', '3ff08cabaf52e7df', 'bfa149e364154000',
    '3ff07b9f2f4e28fb', 'bf9e72c082eb8000', '3ff06ab58c358f19', 'bf9a55f152528000', '3ff059eea5ecf92c', 'bf963d62cf818000',
    '3ff04949cdd12c90', 'bf9228fb8caa0000', '3ff038c6c6f0ada9', 'bf8c317b20f90000', '3ff02865137932a9', 'bf8419355daa0000',
    '3ff0182427ea7348', 'bf781203c2ec0000', '3ff008040614b195', 'bf60040979240000', '3fefe01ff726fa1a', '3f6feff384900000',
    '3fefa11cc261ea74', '3f87dc41353d0000', '3fef6310b081992e', '3f93cea3c4c28000', '3fef25f63ceeadcd', '3f9b9fc114890000',
    '3feee9c8039113e7', '3fa1b0d8ce110000', '3feeae8078cbb1ab', '3fa58a5bd001c000', '3fee741aa29d0c9b', '3fa95c8340d88000',
    '3fee3a91830a99b5', '3fad276aef578000', '3fee01e009609a56', '3fb07598e598c000', '3fedca01e577bb98', '3fb253f5e30d2000',
    '3fed92f20b7c9103', '3fb42edd8b380000', '3fed5cac66fb5cce', '3fb606598757c000', '3fed272caa5ede9d', '3fb7da76356a0000',
    '3fecf26e3e6b2ccd', '3fb9ab434e1c6000', '3fecbe6da2a77902', '3fbb78c7bb0d6000', '3fec8b266d37086d', '3fbd431332e72000',
    '3fec5894bd5d5804', '3fbf0a3171de6000', '3fec26b533bb9f8c', '3fc067152b914000', '3febf583eeece73f', '3fc147858292b000',
    '3febc4fd75db96c1', '3fc2266ecdca3000', '3feb951e0c864a28', '3fc303d7a6c55000', '3feb65e2c5ef3e2c', '3fc3dfc33c331000',
    '3feb374867c9888b', '3fc4ba366b7a8000', '3feb094b211d304a', '3fc5933928d1f000', '3feadbe885f2ef7e', '3fc66acd2418f000',
    '3feaaf1d31603da2', '3fc740f8ec669000', '3fea82e63fd358a7', '3fc815c0f51af000', '3fea5740ef09738b', '3fc8e92954f68000',
    '3fea2c2a90ab4b27', '3fc9bb3602f84000', '3fea01a01393f2d1', '3fca8bed1c2c0000', '3fe9d79f24db3c1b', '3fcb5b515c01d000',
    '3fe9ae2505c7b190', '3fcc2967ccbcc000', '3fe9852ef297ce2f', '3fccf635d5486000', '3fe95cbaeea44b75', '3fcdc1bd3446c000',
    '3fe934c69de74838', '3fce8c01b8cfe000', '3fe90d4f2f6752e6', '3fcf5509c0179000', '3fe8e6528effd79d', '3fd00e6c121fb800',
    '3fe8bfce9fcc007c', '3fd071b80e93d000', '3fe899c0dabec30e', '3fd0d46b9e867000', '3fe87427aa2317fb', '3fd13687334bd000',
    '3fe84f00acb39a08', '3fd1980d67234800', '3fe82a49e8653e55', '3fd1f8ffe0cc8000', '3fe8060195f40260', '3fd2595fd7636800',
    '3fe7e22563e0a329', '3fd2b9300914a800', '3fe7beb377dcb5ad', '3fd3187210436000', '3fe79baa679725c2', '3fd377266dec1800',
    '3fe77907f2170657', '3fd3d54ffbaf3000', '3fe756cadbd6130c', '3fd432eee32fe000'];   // {invc, logc} x 128
  const POW_DATA = [
    '3fe62e42fefa3800', '3d2ef35793c76730', 'bfe0000000000000', 'bfe5555555555560', '3fe0000000000006', '3fe999999959554e',
    'bfe555555529a47a', 'bff2495b9b4845e9', '3ff0002b8b263fc3'];   // ln2hi, ln2lo, poly[7]
  const POW_TAB = [
    '3ff6a00000000000', '0000000000000000', 'bfd62c82f2b9c800', '3cfab42428375680',
    '3ff6800000000000', '0000000000000000', 'bfd5d1bdbf580800', 'bd1ca508d8e0f720',
    '3ff6600000000000', '0000000000000000', 'bfd5767717455800', 'bd2362a4d5b6506d',
    '3ff6400000000000', '0000000000000000', 'bfd51aad872df800', 'bce684e49eb067d5',
    '3ff6200000000000', '0000000000000000', 'bfd4be5f95777800', 'bd041b6993293ee0',
    '3ff6000000000000', '0000000000000000', 'bfd4618bc21c6000', '3d13d82f484c84cc',
    '3ff5e00000000000', '0000000000000000', 'bfd404308686a800', '3cdc42f3ed820b3a',
    '3ff5c00000000000', '0000000000000000', 'bfd3a64c55694800', '3d20b1c686519460',
    '3ff5a00000000000', '0000000000000000', 'bfd347dd9a988000', '3d25594dd4c58092',
    '3ff5800000000000', '0000000000000000', 'bfd2e8e2bae12000', '3d267b1e99b72bd8',
    '3ff5600000000000', '0000000000000000', 'bfd2895a13de8800', '3d15ca14b6cfb03f',
    '3ff5600000000000', '0000000000000000', 'bfd2895a13de8800', '3d15ca14b6cfb03f',
    '3ff5400000000000', '0000000000000000', 'bfd22941fbcf7800', 'bd165a242853da76',
    '3ff5200000000000', '0000000000000000', 'bfd1c898c1699800', 'bd1fafbc68e75404',
    '3ff5000000000000', '0000000000000000', 'bfd1675cababa800', '3d1f1fc63382a8f0',
    '3ff4e00000000000', '0000000000000000', 'bfd1058bf9ae4800', 'bd26a8c4fd055a66',
    '3ff4c00000000000', '0000000000000000', 'bfd0a324e2739000', 'bd0c6bee7ef4030e',
    '3ff4a00000000000', '0000000000000000', 'bfd0402594b4d000', 'bcf036b89ef42d7f',
    '3ff4a00000000000', '0000000000000000', 'bfd0402594b4d000', 'bcf036b89ef42d7f',
    '3ff4800000000000', '0000000000000000', 'bfcfb9186d5e4000', '3d0d572aab993c87',
    '3ff4600000000000', '0000000000000000', 'bfcef0adcbdc6000', '3d2b26b79c86af24',
    '3ff4400000000000', '0000000000000000', 'bfce27076e2af000', 'bd172f4f543fff10',
    '3ff4200000000000', '0000000000000000', 'bfcd5c216b4fc000', '3d21ba91bbca681b',
    '3ff4000000000000', '0000000000000000', 'bfcc8ff7c79aa000', '3d27794f689f8434',
    '3ff4000000000000', '0000000000000000', 'bfcc8ff7c79aa000', '3d27794f689f8434',
    '3ff3e00000000000', '0000000000000000', 'bfcbc286742d9000', '3d194eb0318bb78f',
    '3ff3c00000000000', '0000000000000000', 'bfcaf3c94e80c000', '3cba4e633fcd9066',
    '3ff3a00000000000', '0000000000000000', 'bfca23bc1fe2b000', 'bd258c64dc46c1ea',
    '3ff3a00000000000', '0000000000000000', 'bfca23bc1fe2b000', 'bd258c64dc46c1ea',
    '3ff3800000000000', '0000000000000000', 'bfc9525a9cf45000', 'bd2ad1d904c1d4e3',
    '3ff3600000000000', '0000000000000000', 'bfc87fa06520d000', '3d2bbdbf7fdbfa09',
    '3ff3400000000000', '0000000000000000', 'bfc7ab890210e000', '3d2bdb9072534a58',
    '3ff3400000000000', '0000000000000000', 'bfc7ab890210e000', '3d2bdb9072534a58',
    '3ff3200000000000', '0000000000000000', 'bfc6d60fe719d000', 'bd10e46aa3b2e266',
    '3ff3000000000000', '0000000000000000', 'bfc5ff3070a79000', 'bd1e9e439f105039',
    '3ff3000000000000', '0000000000000000', 'bfc5ff3070a79000', 'bd1e9e439f105039',
    '3ff2e00000000000', '0000000000000000', 'bfc526e5e3a1b000', 'bd20de8b90075b8f',
    '3ff2c00000000000', '0000000000000000', 'bfc44d2b6ccb8000', '3d170cc16135783c',
    '3ff2c00000000000', '0000000000000000', 'bfc44d2b6ccb8000', '3d170cc16135783c',
    '3ff2a00000000000', '0000000000000000', 'bfc371fc201e9000', '3cf178864d27543a',
    '3ff2800000000000', '0000000000000000', 'bfc29552f81ff000', 'bd248d301771c408',
    '3ff2600000000000', '0000000000000000', 'bfc1b72ad52f6000', 'bd2e80a41811a396',
    '3ff2600000000000', '0000000000000000', 'bfc1b72ad52f6000', 'bd2e80a41811a396',
    '3ff2400000000000', '0000000000000000', 'bfc0d77e7cd09000', '3d0a699688e85bf4',
    '3ff2400000000000', '0000000000000000', 'bfc0d77e7cd09000', '3d0a699688e85bf4',
    '3ff2200000000000', '0000000000000000', 'bfbfec9131dbe000', 'bd2575545ca333f2',
    '3ff2000000000000', '0000000000000000', 'bfbe27076e2b0000', '3d2a342c2af0003c',
    '3ff2000000000000', '0000000000000000', 'bfbe27076e2b0000', '3d2a342c2af0003c',
    '3ff1e00000000000', '0000000000000000', 'bfbc5e548f5bc000', 'bd1d0c57585fbe06',
    '3ff1c00000000000', '0000000000000000', 'bfba926d3a4ae000', '3d253935e85baac8',
    '3ff1c00000000000', '0000000000000000', 'bfba926d3a4ae000', '3d253935e85baac8',
    '3ff1a00000000000', '0000000000000000', 'bfb8c345d631a000', '3d137c294d2f5668',
    '3ff1a00000000000', '0000000000000000', 'bfb8c345d631a000', '3d137c294d2f5668',
    '3ff1800000000000', '0000000000000000', 'bfb6f0d28ae56000', 'bd269737c93373da',
    '3ff1600000000000', '0000000000000000', 'bfb51b073f062000', '3d1f025b61c65e57',
    '3ff1600000000000', '0000000000000000', 'bfb51b073f062000', '3d1f025b61c65e57',
    '3ff1400000000000', '0000000000000000', 'bfb341d7961be000', '3d2c5edaccf913df',
    '3ff1400000000000', '0000000000000000', 'bfb341d7961be000', '3d2c5edaccf913df',
    '3ff1200000000000', '0000000000000000', 'bfb16536eea38000', '3d147c5e768fa309',
    '3ff1000000000000', '0000000000000000', 'bfaf0a30c0118000', '3d2d599e83368e91',
    '3ff1000000000000', '0000000000000000', 'bfaf0a30c0118000', '3d2d599e83368e91',
    '3ff0e00000000000', '0000000000000000', 'bfab42dd71198000', '3d1c827ae5d6704c',
    '3ff0e00000000000', '0000000000000000', 'bfab42dd71198000', '3d1c827ae5d6704c',
    '3ff0c00000000000', '0000000000000000', 'bfa77458f632c000', 'bd2cfc4634f2a1ee',
    '3ff0c00000000000', '0000000000000000', 'bfa77458f632c000', 'bd2cfc4634f2a1ee',
    '3ff0a00000000000', '0000000000000000', 'bfa39e87b9fec000', '3cf502b7f526feaa',
    '3ff0a00000000000', '0000000000000000', 'bfa39e87b9fec000', '3cf502b7f526feaa',
    '3ff0800000000000', '0000000000000000', 'bf9f829b0e780000', 'bd2980267c7e09e4',
    '3ff0800000000000', '0000000000000000', 'bf9f829b0e780000', 'bd2980267c7e09e4',
    '3ff0600000000000', '0000000000000000', 'bf97b91b07d58000', 'bd288d5493faa639',
    '3ff0400000000000', '0000000000000000', 'bf8fc0a8b0fc0000', 'bcdf1e7cf6d3a69c',
    '3ff0400000000000', '0000000000000000', 'bf8fc0a8b0fc0000', 'bcdf1e7cf6d3a69c',
    '3ff0200000000000', '0000000000000000', 'bf7fe02a6b100000', 'bd19e23f0dda40e4',
    '3ff0200000000000', '0000000000000000', 'bf7fe02a6b100000', 'bd19e23f0dda40e4',
    '3ff0000000000000', '0000000000000000', '0000000000000000', '0000000000000000',
    '3ff0000000000000', '0000000000000000', '0000000000000000', '0000000000000000',
    '3fefc00000000000', '0000000000000000', '3f80101575890000', 'bd10c76b999d2be8',
    '3fef800000000000', '0000000000000000', '3f90205658938000', 'bd23dc5b06e2f7d2',
    '3fef400000000000', '0000000000000000', '3f98492528c90000', 'bd2aa0ba325a0c34',
    '3fef000000000000', '0000000000000000', '3fa0415d89e74000', '3d0111c05cf1d753',
    '3feec00000000000', '0000000000000000', '3fa466aed42e0000', 'bd2c167375bdfd28',
    '3fee800000000000', '0000000000000000', '3fa894aa149fc000', 'bd197995d05a267d',
    '3fee400000000000', '0000000000000000', '3faccb73cdddc000', 'bd1a68f247d82807',
    '3fee200000000000', '0000000000000000', '3faeea31c006c000', 'bd0e113e4fc93b7b',
    '3fede00000000000', '0000000000000000', '3fb1973bd1466000', 'bd25325d560d9e9b',
    '3feda00000000000', '0000000000000000', '3fb3bdf5a7d1e000', '3d2cc85ea5db4ed7',
    '3fed600000000000', '0000000000000000', '3fb5e95a4d97a000', 'bd2c69063c5d1d1e',
    '3fed400000000000', '0000000000000000', '3fb700d30aeac000', '3cec1e8da99ded32',
    '3fed000000000000', '0000000000000000', '3fb9335e5d594000', '3d23115c3abd47da',
    '3fecc00000000000', '0000000000000000', '3fbb6ac88dad6000', 'bd1390802bf768e5',
    '3feca00000000000', '0000000000000000', '3fbc885801bc4000', '3d2646d1c65aacd3',
    '3fec600000000000', '0000000000000000', '3fbec739830a2000', 'bd2dc068afe645e0',
    '3fec400000000000', '0000000000000000', '3fbfe89139dbe000', 'bd2534d64fa10afd',
    '3fec000000000000', '0000000000000000', '3fc1178e8227e000', '3d21ef78ce2d07f2',
    '3febe00000000000', '0000000000000000', '3fc1aa2b7e23f000', '3d2ca78e44389934',
    '3feba00000000000', '0000000000000000', '3fc2d1610c868000', '3d039d6ccb81b4a1',
    '3feb800000000000', '0000000000000000', '3fc365fcb0159000', '3cc62fa8234b7289',
    '3feb400000000000', '0000000000000000', '3fc4913d8333b000', '3d25837954fdb678',
    '3feb200000000000', '0000000000000000', '3fc527e5e4a1b000', '3d2633e8e5697dc7',
    '3feae00000000000', '0000000000000000', '3fc6574ebe8c1000', '3d19cf8b2c3c2e78',
    '3feac00000000000', '0000000000000000', '3fc6f0128b757000', 'bd25118de59c21e1',
    '3feaa00000000000', '0000000000000000', '3fc7898d85445000', 'bd1c661070914305',
    '3fea600000000000', '0000000000000000', '3fc8beafeb390000', 'bd073d54aae92cd1',
    '3fea400000000000', '0000000000000000', '3fc95a5adcf70000', '3d07f22858a0ff6f',
    '3fea000000000000', '0000000000000000', '3fca93ed3c8ae000', 'bd28724350562169',
    '3fe9e00000000000', '0000000000000000', '3fcb31d8575bd000', 'bd0c358d4eace1aa',
    '3fe9c00000000000', '0000000000000000', '3fcbd087383be000', 'bd2d4bc4595412b6',
    '3fe9a00000000000', '0000000000000000', '3fcc6ffbc6f01000', 'bcf1ec72c5962bd2',
    '3fe9600000000000', '0000000000000000', '3fcdb13db0d49000', 'bd2aff2af715b035',
    '3fe9400000000000', '0000000000000000', '3fce530effe71000', '3cc212276041f430',
    '3fe9200000000000', '0000000000000000', '3fcef5ade4dd0000', 'bcca211565bb8e11',
    '3fe9000000000000', '0000000000000000', '3fcf991c6cb3b000', '3d1bcbecca0cdf30',
    '3fe8c00000000000', '0000000000000000', '3fd07138604d5800', '3cf89cdb16ed4e91',
    '3fe8a00000000000', '0000000000000000', '3fd0c42d67616000', '3d27188b163ceae9',
    '3fe8800000000000', '0000000000000000', '3fd1178e8227e800', 'bd2c210e63a5f01c',
    '3fe8600000000000', '0000000000000000', '3fd16b5ccbacf800', '3d2b9acdf7a51681',
    '3fe8400000000000', '0000000000000000', '3fd1bf99635a6800', '3d2ca6ed5147bdb7',
    '3fe8200000000000', '0000000000000000', '3fd214456d0eb800', '3d0a87deba46baea',
    '3fe7e00000000000', '0000000000000000', '3fd2bef07cdc9000', '3d2a9cfa4a5004f4',
    '3fe7c00000000000', '0000000000000000', '3fd314f1e1d36000', 'bd28e27ad3213cb8',
    '3fe7a00000000000', '0000000000000000', '3fd36b6776be1000', '3d116ecdb0f177c8',
    '3fe7800000000000', '0000000000000000', '3fd3c25277333000', '3d183b54b606bd5c',
    '3fe7600000000000', '0000000000000000', '3fd419b423d5e800', '3d08e436ec90e09d',
    '3fe7400000000000', '0000000000000000', '3fd4718dc271c800', 'bd2f27ce0967d675',
    '3fe7200000000000', '0000000000000000', '3fd4c9e09e173000', 'bd2e20891b0ad8a4',
    '3fe7000000000000', '0000000000000000', '3fd522ae0738a000', '3d2ebe708164c759',
    '3fe6e00000000000', '0000000000000000', '3fd57bf753c8d000', '3d1fadedee5d40ef',
    '3fe6c00000000000', '0000000000000000', '3fd5d5bddf596000', 'bd0a0b2a08a465dc'];   // {invc, pad, logc, logctail} x 128

  const LITTLE = new Uint8Array(new Uint32Array([1]).buffer)[0] === 1;
  const F64 = new Float64Array(1), U32 = new Uint32Array(F64.buffer), LOW = LITTLE ? 0 : 1, HIGH = LITTLE ? 1 : 0;
  const hiw = (x) => { F64[0] = x; return U32[HIGH]; };
  const dbl = (h, l) => { U32[HIGH] = h >>> 0; U32[LOW] = l >>> 0; return F64[0]; };
  const hex2d = (s) => dbl(parseInt(s.slice(0, 8), 16), parseInt(s.slice(8), 16));
  const TWO52 = 4503599627370496, TWO27 = 134217728, TINY = 2.2250738585072014e-308;   // 2^52, 2^27, 2^-1022
  const TWO1009 = dbl(0x7f000000, 0);

  /** the exact value of a finite double: {m: BigInt, e} with value m * 2^e */
  function decompose(x) {
    F64[0] = x; const h = U32[HIGH], l = U32[LOW];
    const ex = (h >>> 20) & 0x7ff;
    let m = (BigInt(h & 0xfffff) << 32n) | BigInt(l);
    let e;
    if (ex === 0) e = -1074; else { m |= 1n << 52n; e = ex - 1075; }
    return { m: h >>> 31 ? -m : m, e };
  }
  /** m * 2^e rounded to the nearest double, ties to even (subnormals and overflow included) */
  function roundBig(m, e) {
    if (m === 0n) return 0;
    const neg = m < 0n; let a = neg ? -m : m;
    const n = a.toString(2).length;
    let q = Math.max(e + n - 53, -1074);                  // the exponent of the result's last bit
    if (q > e) {
      const sh = BigInt(q - e), half = 1n << (sh - 1n), rem = a & ((1n << sh) - 1n);
      a >>= sh;
      if (rem > half || (rem === half && (a & 1n) === 1n)) a += 1n;
    } else { a <<= BigInt(e - q); }
    if (q > 971) return neg ? -Infinity : Infinity;
    let v = Number(a);                                      // exact: at most 2^53
    while (q > 0) { const s = Math.min(q, 1000); v *= dbl((s + 1023) << 20, 0); q -= s; }
    while (q < 0) { const s = Math.max(q, -1000); v *= dbl((s + 1023) << 20, 0); q -= s; }
    return neg ? -v : v;
  }
  function fmaSlow(a, b, c) {
    if (!Number.isFinite(a) || !Number.isFinite(b) || !Number.isFinite(c) || a === 0 || b === 0) return a * b + c;
    const A = decompose(a), B = decompose(b), C = decompose(c);
    let pm = A.m * B.m, pe = A.e + B.e, cm = C.m, ce = C.e;
    if (cm === 0n) return roundBig(pm, pe);
    const e = Math.min(pe, ce);
    pm <<= BigInt(pe - e); cm <<= BigInt(ce - e);
    const s = pm + cm;
    if (s === 0n) return 0 * a * b + c;                     // an exact zero takes the sign IEEE addition gives it
    return roundBig(s, e);
  }
  const SPLIT = 134217729;   // 2^27 + 1
  /** fma(a, b, c) = a*b + c rounded once: Dekker's exact product, Knuth's exact sum, then Boldo and Melquiond's
      rounding to odd of the low parts, which makes the final rounding the correct one */
  function fma(a, b, c) {
    if (a === 0 || b === 0) return a * b + c;
    const p = a * b, ap = Math.abs(a), bp = Math.abs(b), pp = Math.abs(p);
    if (!(ap < 1e150 && bp < 1e150 && pp > 1e-250 && pp < 1e300 && Math.abs(c) < 1e300)) return fmaSlow(a, b, c);
    let t = SPLIT * a; const ah = t - (t - a), al = a - ah;
    t = SPLIT * b; const bh = t - (t - b), bl = b - bh;
    const pl = ((ah * bh - p) + ah * bl + al * bh) + al * bl;      // a*b = p + pl exactly
    const s = p + c, sb = s - p, sl = (p - (s - sb)) + (c - sb);    // p + c = s + sl exactly
    let v = sl + pl;
    const vb = v - sl, ve = (sl - (v - vb)) + (pl - vb);            // sl + pl = v + ve exactly
    if (ve !== 0) {
      F64[0] = v;
      if ((U32[LOW] & 1) === 0) {                                     // round to odd: step towards the exact value
        let l = U32[LOW], h = U32[HIGH];
        if ((v > 0) === (ve > 0)) { l = (l + 1) >>> 0; if (l === 0) h = (h + 1) >>> 0; }
        else { if (l === 0) h = (h - 1) >>> 0; l = (l - 1) >>> 0; }
        U32[LOW] = l; U32[HIGH] = h; v = F64[0];
      }
    }
    return s + v;
  }

  // exp (e_exp.c, the FMA build)
  const ED = EXP_DATA.map(hex2d);
  const InvLn2N = ED[0], Shift = ED[1], NegLn2hiN = ED[2], NegLn2loN = ED[3], C2 = ED[4], C3 = ED[5], C4 = ED[6], C5 = ED[7];
  const EXP_TAIL = new Float64Array(128), EXP_SBH = new Uint32Array(128), EXP_SBL = new Uint32Array(128);
  for (let i = 0; i < 128; i++) {
    EXP_TAIL[i] = hex2d(EXP_TAB[2 * i]);
    EXP_SBH[i] = parseInt(EXP_TAB[2 * i + 1].slice(0, 8), 16); EXP_SBL[i] = parseInt(EXP_TAB[2 * i + 1].slice(8), 16);
  }
  /** large or tiny results: scale * (1 + tmp) without intermediate overflow or double rounding */
  function expSpecial(tmp, sbh, sbl, kiLo, isPow) {
    if ((kiLo & 0x80000000) === 0) {                              // k > 0: the exponent of scale may have overflowed
      const scale = dbl(sbh - (1009 << 20), sbl);
      return TWO1009 * fma(scale, tmp, scale);
    }
    const sb = (sbh + (1022 << 20)) >>> 0, scale = dbl(sb, sbl);   // k < 0: care in the subnormal range
    const st = scale * tmp;
    let y = scale + st;
    if (isPow ? Math.abs(y) < 1.0 : y < 1.0) {
      const one = isPow && y < 0.0 ? -1.0 : 1.0;
      let lo = scale - y + st;
      const hi = one + y;
      lo = one - hi + y + lo;
      y = (hi + lo) - one;
      if (y === 0) y = isPow && (sb >>> 31) ? -0 : 0;            // pow: the sign of zero is the scale's (the sign bias)
    }
    return TINY * y;
  }
  function glibcExp(x) {
    const hx = hiw(x);
    let abstop = (hx >>> 20) & 0x7ff;
    if (((abstop - 0x3c9) >>> 0) >= 0x3f) {
      if (((abstop - 0x3c9) >>> 0) >= 0x80000000) return 1.0 + x;   // tiny x
      if (abstop >= 0x409) {
        if (x === -Infinity) return 0.0;
        if (abstop >= 0x7ff) return 1.0 + x;
        return hx >>> 31 ? 0.0 : Infinity;
      }
      abstop = 0;                                                   // large x: special-cased below
    }
    const kd0 = fma(x, InvLn2N, Shift);
    F64[0] = kd0; const kiLo = U32[LOW];
    const kd = kd0 - Shift;
    const r = fma(kd, NegLn2loN, fma(kd, NegLn2hiN, x));
    const i = kiLo & 127, sbh = (EXP_SBH[i] + (kiLo << 13)) >>> 0, sbl = EXP_SBL[i];
    const r2 = r * r;
    const tmp = fma(r2 * r2, fma(r, C5, C4), fma(fma(r, C3, C2), r2, r + EXP_TAIL[i]));
    if (abstop === 0) return expSpecial(tmp, sbh, sbl, kiLo, false);
    const scale = dbl(sbh, sbl);
    return fma(scale, tmp, scale);
  }

  // log (e_log.c, the FMA build)
  const LD = LOG_DATA.map(hex2d);
  const Ln2hi = LD[0], Ln2lo = LD[1], LA = LD.slice(2, 7), LB = LD.slice(7, 18);
  const LOG_INVC = new Float64Array(128), LOG_LOGC = new Float64Array(128);
  for (let i = 0; i < 128; i++) { LOG_INVC[i] = hex2d(LOG_TAB[2 * i]); LOG_LOGC[i] = hex2d(LOG_TAB[2 * i + 1]); }
  function glibcLog(x) {
    F64[0] = x; const h = U32[HIGH], l = U32[LOW];
    if (h >= 0x3fee0000 && h < 0x3ff10900) {                     // close to 1.0
      if (h === 0x3ff00000 && l === 0) return 0;
      const r = x - 1.0, r2 = r * r, r3 = r * r2;
      const p1 = fma(r2, LB[3], fma(r, LB[2], LB[1]));
      const p2 = fma(r2, LB[6], fma(r, LB[5], LB[4]));
      const p3 = fma(r3, LB[10], fma(r2, LB[9], fma(r, LB[8], LB[7])));
      const q1 = fma(fma(p3, r3, p2), r3, p1);
      const rhi = fma(-TWO27, r, fma(r, TWO27, r));
      const rlo = r - rhi, rhi2 = rhi * rhi;
      const hi = fma(rhi2, LB[0], r);
      let lo = fma(rhi2, LB[0], r - hi);
      lo = fma(LB[0] * rlo, rhi + r, lo);
      return hi + fma(q1, r3, lo);
    }
    let ixh = h, ixl = l;
    const top = h >>> 16;
    if (((top - 0x0010) >>> 0) >= 0x7fe0) {                      // x < 2^-1022, inf or nan
      if ((h & 0x7fffffff) === 0 && l === 0) return -Infinity;
      if (h === 0x7ff00000 && l === 0) return x;
      if ((top & 0x8000) || (top & 0x7ff0) === 0x7ff0) return NaN;
      F64[0] = x * TWO52; ixh = (U32[HIGH] - (52 << 20)) >>> 0; ixl = U32[LOW];   // subnormal: normalise
    }
    const tmph = (ixh - 0x3fe60000) >>> 0;
    const i = (tmph >>> 13) & 127, k = (tmph | 0) >> 20;
    const z = dbl((ixh - (tmph & 0xfff00000)) >>> 0, ixl);
    const r = fma(z, LOG_INVC[i], -1.0);
    const w = fma(k, Ln2hi, LOG_LOGC[i]);
    const hi = r + w;
    const lo = fma(k, Ln2lo, (w - hi) + r);
    const r2 = r * r;
    const t = fma(fma(r, LA[4], LA[3]), r2, fma(r, LA[2], LA[1]));
    return fma(r * r2, t, fma(r2, LA[0], lo)) + hi;
  }

  // pow (e_pow.c, the FMA build)
  const PD = POW_DATA.map(hex2d);
  const PLn2hi = PD[0], PLn2lo = PD[1], PA = PD.slice(2, 9);
  const POW_INVC = new Float64Array(128), POW_LOGC = new Float64Array(128), POW_LOGCT = new Float64Array(128);
  for (let i = 0; i < 128; i++) { POW_INVC[i] = hex2d(POW_TAB[4 * i]); POW_LOGC[i] = hex2d(POW_TAB[4 * i + 2]); POW_LOGCT[i] = hex2d(POW_TAB[4 * i + 3]); }
  let powTail = 0;
  /** log(x) as y + powTail with about 15 more bits; x's bits (ixh, ixl), normalised */
  function powLog(ixh, ixl) {
    const tmph = (ixh - 0x3fe69555) >>> 0;
    const i = (tmph >>> 13) & 127, k = (tmph | 0) >> 20;
    const z = dbl((ixh - (tmph & 0xfff00000)) >>> 0, ixl);
    const r = fma(z, POW_INVC[i], -1.0);
    const t1 = fma(k, PLn2hi, POW_LOGC[i]);
    const t2 = r + t1;
    const lo1 = fma(k, PLn2lo, POW_LOGCT[i]);
    const lo2 = (t1 - t2) + r;
    const ar = r * PA[0], ar2 = r * ar, ar3 = r * ar2;
    const hi = t2 + ar2;
    const lo3 = fma(ar, r, -ar2);
    const lo4 = (t2 - hi) + ar2;
    const q1 = fma(fma(r, PA[6], PA[5]), ar2, fma(r, PA[4], PA[3]));
    const q2 = fma(ar2, q1, fma(r, PA[2], PA[1]));
    const lo = fma(ar3, q2, ((lo1 + lo2) + lo3) + lo4);
    const y = hi + lo;
    powTail = (hi - y) + lo;
    return y;
  }
  function powExp(x, xtail, signBias) {
    const hx = hiw(x);
    let abstop = (hx >>> 20) & 0x7ff;
    if (((abstop - 0x3c9) >>> 0) >= 0x3f) {
      if (((abstop - 0x3c9) >>> 0) >= 0x80000000) { const one = 1.0 + x; return signBias ? -one : one; }
      if (abstop >= 0x409) { const y = hx >>> 31 ? 0 : Infinity; return signBias ? -y : y; }
      abstop = 0;
    }
    const kd0 = fma(x, InvLn2N, Shift);
    F64[0] = kd0; const kiLo = U32[LOW];
    const kd = kd0 - Shift;
    const r = xtail + fma(kd, NegLn2loN, fma(kd, NegLn2hiN, x));
    const i = kiLo & 127, sbh = (EXP_SBH[i] + ((kiLo + signBias) << 13)) >>> 0, sbl = EXP_SBL[i];
    const r2 = r * r;
    const tmp = fma(r2 * r2, fma(r, C5, C4), fma(fma(r, C3, C2), r2, r + EXP_TAIL[i]));
    if (abstop === 0) return expSpecial(tmp, sbh, sbl, kiLo, true);
    const scale = dbl(sbh, sbl);
    return fma(scale, tmp, scale);
  }
  /** 0 if y is not an integer, 1 if odd, 2 if even (y finite, non-zero) */
  function checkint(yh, yl) {
    const e = (yh >>> 20) & 0x7ff;
    if (e < 0x3ff) return 0;
    if (e > 0x3ff + 52) return 2;
    const iy = (BigInt(yh) << 32n) | BigInt(yl), sh = BigInt(0x3ff + 52 - e);
    if (iy & ((1n << sh) - 1n)) return 0;
    return iy & (1n << sh) ? 1 : 2;
  }
  const zeroinfnan = (h, l) => ((h & 0x7fffffff) === 0 && l === 0) || (h & 0x7ff00000) === 0x7ff00000;
  function glibcPow(x, y) {
    let signBias = 0;
    F64[0] = x; let ixh = U32[HIGH], ixl = U32[LOW];
    F64[0] = y; const iyh = U32[HIGH], iyl = U32[LOW];
    let topx = ixh >>> 20; const topy = iyh >>> 20;
    if (((topx - 1) >>> 0) >= 0x7fe || (((topy & 0x7ff) - 0x3be) >>> 0) >= 0x80) {
      if (zeroinfnan(iyh, iyl)) {
        if ((iyh & 0x7fffffff) === 0 && iyl === 0) return 1.0;
        if (ixh === 0x3ff00000 && ixl === 0) return 1.0;
        if (Number.isNaN(x) || Number.isNaN(y)) return x + y;
        if ((ixh & 0x7fffffff) === 0x3ff00000 && ixl === 0) return 1.0;
        if ((Math.abs(x) < 1.0) === !(iyh >>> 31)) return 0.0;
        return y * y;
      }
      if (zeroinfnan(ixh, ixl)) {
        let x2 = x * x;
        if ((ixh >>> 31) && checkint(iyh, iyl) === 1) x2 = -x2;
        return iyh >>> 31 ? 1 / x2 : x2;
      }
      if (ixh >>> 31) {                                           // finite x < 0
        const yint = checkint(iyh, iyl);
        if (yint === 0) return NaN;
        if (yint === 1) signBias = 0x800 << 7;
        ixh &= 0x7fffffff; topx &= 0x7ff;
      }
      if ((((topy & 0x7ff) - 0x3be) >>> 0) >= 0x80) {
        const big = ixh > 0x3ff00000 || (ixh === 0x3ff00000 && ixl > 0);
        if (ixh === 0x3ff00000 && ixl === 0) return 1.0;
        if ((topy & 0x7ff) < 0x3be) return big ? 1.0 + y : 1.0 - y;
        return big === (topy < 0x800) ? Infinity : 0.0;
      }
      if (topx === 0) { F64[0] = x * TWO52; ixh = ((U32[HIGH] & 0x7fffffff) - (52 << 20)) >>> 0; ixl = U32[LOW]; }
    }
    const lhi = powLog(ixh, ixl), ltail = powTail;
    const ehi = y * lhi;
    const elo = fma(y, ltail, fma(lhi, y, -ehi));
    return powExp(ehi, elo, signBias);
  }

  /** Python's float ** float (floatobject.c's float_pow: its own special cases, then the C library's pow) */
  function pyPow(v, w) {
    if (w === 0) return 1.0;
    if (Number.isNaN(v)) return v;
    if (Number.isNaN(w)) return v === 1.0 ? 1.0 : w;
    let neg = false;
    if (Number.isFinite(v) && Number.isFinite(w) && v < 0.0) {
      if (w !== Math.floor(w)) return NaN;                       // Python: a complex result
      v = -v; neg = Math.abs(w) < 9007199254740992 && Math.abs(w % 2) === 1;
    }
    if (v === 1.0) return neg ? -1.0 : 1.0;
    const r = glibcPow(v, w);
    return neg ? -r : r;
  }

  PyRandom.math = { log: glibcLog, exp: glibcExp, pow: pyPow, fma, native: { log: Math.log, exp: Math.exp, pow: Math.pow } };
  PyRandom.bisectRight = bisectRight;
  PyRandom.bitLength = bitLength;
  return PyRandom;
});
