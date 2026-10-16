/* Uncharted Horizons research engine: the simulator's discovery model, ported to JavaScript so that a game can be played in
   the browser.

   A line-by-line port of design/simulator/power/harness_ftl_e.py's run() for the configuration in use (model Pmom, spill
   routing, spread floor 0, compression, idea windows by tier with the grace rule, glimpses by tier, no observational
   revelation, rediscovery on demand with the FTL screen's goals, no W16, the spread fix, Competing Solutions' lock-outs,
   knowledge diffusion from five replayed rivals with the Printing Press and Internet rules, Grand Endeavours by request at
   2x, RUN_ON), with w7f.py's game setup around it (truth draws, rivals, seeds, the FTL definitions, knowledge, status and
   the FTL goals, the hints), plus what victory.py adds: the prototype, the SS FTL Drive and the launch.

   It plays the same game as the Python harness, draw for draw: the same random streams in the same order (pyrandom.js),
   CPython's compensated float sum wherever the harness calls sum() on floats (pysum below), Python's max() tie rule (the
   first maximal key in insertion order), dicts as insertion-ordered Maps, ids in Python's string order, and Python's
   ** and the meters' log and exp as glibc computes them (pyrandom.js's ports of its exp, log and pow, identical to
   Python's on every argument tested), so every hidden meter and every Insight flow equals Python's to the bit, and a
   saved game replays identically in any browser (Math.pow, Math.exp and Math.log differ from glibc and between engines).

   Data: bundle.json (build_bundle.py). Runs in Node (module.exports) and the browser (window.UHEngine); needs PyRandom
   (pyrandom.js) loaded first in the browser. No DOM, no other dependencies.

   API (see SPEC.md):
     const e = new UHEngine(bundle, {world, econ, game, seed, method, truth, rivals, player, maxTurns});
     e.setFocus(f | null); e.requestEndeavour(id); e.stopEndeavour(); e.commitPrototype(method);
     e.step() -> this turn's events; e.snapshot(); e.ftl(); e.endeavourQuote(id); e.prototypeQuote(method); e.advise();
     e.victory; e.over; e.serialize(); UHEngine.restore(bundle, saved).
   Players: 'human' (the UI chooses), 'generalist' (the simulator's: the focus with the most work waiting, no Endeavours,
   the reference for the bit-for-bit test), 'advisor' (follows the FTL screen's hints, otherwise the generalist). */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(require('./pyrandom.js'));
  else root.UHEngine = factory(root.PyRandom);
})(typeof self !== 'undefined' ? self : this, function (PyRandom) {
  'use strict';
  if (!PyRandom) throw new Error('engine.js needs pyrandom.js (PyRandom) loaded first');

  // ---- Python's arithmetic -----------------------------------------------------------------------------------------
  /** CPython 3.12+'s sum() of floats with an int start of 0: the first float added to 0 (so -0.0 becomes 0.0), then
      Neumaier's compensated summation, the compensation added at the end if it is non-zero and finite. */
  function pysum(xs) {
    const n = xs.length;
    if (n === 0) return 0;
    let f = 0 + xs[0], c = 0.0;
    for (let i = 1; i < n; i++) {
      const x = xs[i], t = f + x;
      if (Math.abs(f) >= Math.abs(x)) c += (f - t) + x;
      else c += (x - t) + f;
      f = t;
    }
    if (c !== 0 && Number.isFinite(c)) f += c;
    return f;
  }
  /** max(d, key=d.get) over a Map: the first key with the greatest value; null when empty */
  function maxKey(map) {
    let best = null, bv = 0, first = true;
    for (const [k, v] of map) { if (first || v > bv) { best = k; bv = v; first = false; } }
    return best;
  }
  /** Python's sorted() for strings (code-point order; the ids and names are in the Basic Multilingual Plane) */
  const pysorted = (it) => Array.from(it).sort((a, b) => (a < b ? -1 : a > b ? 1 : 0));
  const pow = (a, b) => PyRandom.math.pow(a, b);   // Python's a ** b: glibc's pow, to the bit (pyrandom.js)

  const SEED0 = 17000, TRUTHSEED = 31;
  const ERA_COUNT = { Ancient: 5, Classical: 3, Medieval: 3, 'Early Modern': 5, Modern: 7, Atomic: 6, Space: 4 };   // §2, era entry by count
  const REFERENCE = { '1.0': 305, '0.8': 380 };   // base Civ V's science victory on the same income (base_race.py)
  const FTL_TEXT = 'This bears on the question of how to exceed the speed of light.';

  function econKey(e) {
    if (e === undefined || e === null) return '1.0';
    const x = typeof e === 'string' ? parseFloat(e) : e;
    return x === 1 ? '1.0' : String(x);
  }

  class UHEngine {
    constructor(bundle, options) {
      const o = Object.assign({ world: 'familiar', econ: 1.0, player: 'human', rivals: true }, options || {});
      const B = this.B = bundle;
      if (!B.worlds[o.world]) throw new Error('unknown world ' + o.world);
      const W = B.worlds[o.world];
      this.world = o.world; this.ontology = W.ontology;
      this.econ = econKey(o.econ);
      if (!B.economy[this.econ]) throw new Error('no economy ' + this.econ);
      this.ECON = parseFloat(this.econ);
      this.INC = B.economy[this.econ].inc; this.D = B.economy[this.econ].d;
      this.player = o.player;
      this.EO = B.eras; this.SPAN_E = this.EO.length;

      // ---- the world's rows (w7f.py: HF.ROWS, IDS, FOCUS, ERA_I; prices.apply: COSTMULT; competing.apply: COMPETE) ----
      this.IDS = pysorted(W.ids);
      this.ROWS = {};
      for (const k of this.IDS) {
        const r = B.rows[k];
        this.ROWS[k] = { focus: r.focus, tier: (W.tiers && W.tiers[k]) || r.tier, era: r.era, pre: r.pre, eraI: this.EO.indexOf(r.era) };
      }
      this.COSTMULT = W.costmult || {};
      this.COMPETE = W.compete || {};
      this.alts_of = new Map();
      for (const a of Object.keys(this.COMPETE)) {
        const p = this.COMPETE[a];
        if (!this.alts_of.has(p)) this.alts_of.set(p, []);
        this.alts_of.get(p).push(a);
      }
      this.dependents = new Map();                          // row -> the rows that name it as a prerequisite (with repeats)
      for (const k of this.IDS) for (const grp of this.ROWS[k].pre) for (const opt of grp) for (const p of opt) {
        if (!this.dependents.has(p)) this.dependents.set(p, []);
        this.dependents.get(p).push(k);
      }

      // ---- the model (harness_ftl_e.P with w7c_cfg.json and the run's switches) ----
      const P = this.P = B.model;
      this.PRICE = P.price; this.TARGET = P.target; this.TURNS = P.turns; this.WIN_TURNS = P.win_turns;
      this.GLIMPSE = P.glimpse;
      this.contactEra = this.EO.indexOf(P.contact_era);
      this.COST = {};                                       // w7f.COST: each row's price, fixed for the run (hints)
      for (const k of this.IDS) this.COST[k] = this.PRICE[this.ROWS[k].era] * (this.COSTMULT[k] !== undefined ? this.COSTMULT[k] : 1.0);

      // ---- the FTL definitions (w7f.py) ----
      const F = this.F = B.ftl[this.ontology];
      this.METHODS = Object.keys(F.COND);
      this.INSTR = B.ftl.INSTR; this.INSTRUMENT = B.ftl.INSTRUMENT; this.OPENS = B.ftl.OPENS;
      this.INSTR_D = o.instrD !== undefined ? o.instrD : B.ftl.INSTR_D[this.econ];

      // ---- the game: w7f.py's draws (Random(TRUTHSEED): game s has method METHODS[s % 5] and a truth drawn for it) ----
      let game = o.game;
      if (game === undefined || game === null) game = o.seed !== undefined ? Math.abs(o.seed - SEED0) % 300 : Math.floor(Math.random() * 300);
      this.game = game;
      const trng = new PyRandom(o.truthSeed !== undefined ? o.truthSeed : TRUTHSEED);
      let m = null, a = null;
      for (let s = 0; s <= game; s++) { m = this.METHODS[s % this.METHODS.length]; a = trng.choice(F.TRUTHS[m]); }
      this.method = o.method || m;
      this.truth = o.truth || (o.method && o.method !== m ? new PyRandom(SEED0 + game + 1).choice(F.TRUTHS[o.method]) : a);
      this.seed = o.seed !== undefined ? o.seed : SEED0 + game;

      // ---- rivals: the pool's games of the same method, five in a row from (game // 5) * 5, at the player's pace ----
      this.DIFF = null;
      if (o.rivals) {
        let rivals;
        if (Array.isArray(o.rivals)) rivals = o.rivals.map((r) => (r instanceof Map ? r : new Map(Object.entries(r))));
        else {
          const pm = W.pool.filter((g) => g.m === this.method), j0 = Math.floor(game / this.METHODS.length) * 5;
          rivals = [];
          for (let j = 0; j < 5; j++) {
            const g = pm[(j0 + j) % pm.length], r = new Map();
            W.ids.forEach((k, i) => { if (g.t[i] !== null && g.t[i] !== undefined) r.set(k, g.t[i] / this.ECON); });
            rivals.push(r);
          }
        }
        this.DIFF = { rivals, contact_era: this.contactEra };
      }

      // ---- the player's switches ----
      const human = this.player === 'human' || this.player === 'advisor';
      this.END_MULT = human ? P.end_mult : null;            // Grand Endeavours (END=2, END_RULE 'request')
      this.END_FROM = o.endFrom !== undefined ? o.endFrom : null;   // the design: any time (w7f's simulated players: the Space era)
      this.END_UNOCCURRED_ONLY = !!o.endUnoccurredOnly;     // the design allows both since v3.121
      this.W16 = !!P.w16; this.SPREAD_FIX = true; this.RUN_ON = o.runOn !== undefined ? !!o.runOn : true;
      this.maxTurns = o.maxTurns || (human ? Math.min(this.INC.length - 2, (B.victory.drive[this.econ].plain.length || 700) - 2) : 450);
      this.recordTrace = !!o.trace; this.traceRecords = [];

      this.opts = { world: this.world, econ: this.ECON, game, seed: this.seed, method: this.method, truth: this.truth,
        rivals: Array.isArray(o.rivals) ? o.rivals : !!o.rivals, player: this.player, maxTurns: this.maxTurns,
        endFrom: this.END_FROM, endUnoccurredOnly: this.END_UNOCCURRED_ONLY, instrD: this.INSTR_D };
      this._init();
    }

    _init() {
      const s = this.seed;
      this.rng = new PyRandom(s);
      this.grng = new PyRandom(s * 7919 + 13);              // glimpses' own stream
      this.rrng = new PyRandom(s * 104729 + 7);             // rediscovery's own stream
      const S = this.S = {
        turn: 0, have: new Map(), met: new Set(), new_rows: [], locked: new Set(),
        progress: new Map(), need: new Map(), opened: new Map(), occurred: new Set(), occ_turn: new Map(),
        diff_since: new Map(), diff_unc: new Map(), contact_turn: null, cp04_turn: null,
        glimpsed: new Set(), lost: new Set(), rediscovered: new Map(), lost_at: new Map(),
        active: null, end_k: null, end_prog: 0.0, end_cost: 0.0, bank: 0.0,
        d: 0.0, inc: 0.0, share: 0.0, flow: new Map(), live: [], fund: ['FOCUS', null],
        // the human's choices and the endgame
        choice: null, endRequest: null, proto: null, protoResults: [], protoFailed: new Set(), protoWorked: null,
        drive: null, victory: null, cert: null, events: [], log: [], eraName: this.EO[0], foci: new Set(),
        ftlSig: null, maxEraHeld: -1,
      };
      for (const k of this.IDS) if (this.prereqsMet(k, S.have)) S.met.add(k);
      this.actions = [];
      S.foci = this._fociEntered();
      S.ftlSig = this._ftlSignature();
    }

    // ---- the harness's helpers ---------------------------------------------------------------------------------------
    prereqsMet(k, have) {
      for (const grp of this.ROWS[k].pre) {
        let any = false;
        for (const opt of grp) { let all = true; for (const p of opt) if (!have.has(p)) { all = false; break; } if (all) { any = true; break; } }
        if (!any) return false;
      }
      return true;
    }
    tier(k) { return this.ROWS[k].tier; }
    _cm(k) { return this.COSTMULT[k] !== undefined ? this.COSTMULT[k] : 1.0; }
    /** the price a breakthrough is studied at, development d: era price x calibration x premium^(eras ahead) */
    priceAt(k, d) { return this.PRICE[this.ROWS[k].era] * this.P.scale * 1.0 * pow(this.P.premium, Math.max(0.0, this.ROWS[k].eraI - d - 0.0)); }
    estPrice(k, d) { return this.PRICE[this.ROWS[k].era] * this.P.scale * pow(this.P.premium, Math.max(0.0, this.ROWS[k].eraI - d)); }
    endPrice(k, d) { const full = this._cm(k) * this.estPrice(k, d); return this.P.end_mult * full; }

    // ---- w7f.py: what the FTL screen knows --------------------------------------------------------------------------
    readyTurn(c, have) {
      const hosts = this.F.HOST[c].filter((h) => have.has(h)).map((h) => have.get(h).turn);
      if (!hosts.length) return null;
      if (this.INSTR_D === null || this.INSTR_D === undefined || !this.INSTR[c]) return Math.min(...hosts);
      const unl = this.INSTR[c].filter((u) => have.has(u)).map((u) => have.get(u).turn);
      return Math.max(Math.min(...hosts), Math.min(...unl) + this.INSTR_D);
    }
    knowledge(have, clock) {
      const kn = {}, a = this.truth;
      for (const c of Object.keys(this.F.HOST)) {
        const hosts = this.F.HOST[c];
        const rt = hosts.some((h) => have.has(h)) ? this.readyTurn(c, have) : null;
        if (rt !== null && rt <= clock && !(hosts.length === 1 && hosts[0] === 'MS08' && !a.exotic)) kn[c] = a[c];
      }
      return kn;
    }
    status(have, clock) {
      const kn = this.knowledge(have, clock), F = this.F, S = this.S;
      const alive = this.METHODS.filter((o) => !F.COND[o].some((c) => c in kn && !kn[c]) && !S.protoFailed.has(o));
      const m = this.method;
      const certain = have.has(F.CLOSE) && (F.COND[m].every((c) => kn[c]) || (alive.length === 1 && alive[0] === m));
      return { kn, alive, certain };
    }
    /** rediscovery's goals once the FTL screen opens: each standing hypothesis's prototype and each open question */
    ftlGoals(have, clock) {
      if (!have.has('RC01')) return [];
      const { kn, alive } = this.status(have, clock), F = this.F;
      const open = new Set();
      for (const o of alive) for (const c of F.COND[o]) if (!(c in kn)) open.add(c);
      return alive.map((o) => F.BUILD[o]).concat(pysorted(open).map((c) => [F.HOST[c]]));
    }

    /** w7f.smart_targets: the undiscovered rows a thoughtful player would pursue for a list of requirements */
    smartTargets(reqs, have) {
      const S = this.S, memo = new Map(), EMPTY = new Set(), cost = (k) => this.COST[k];
      const need = (k) => {
        if (memo.has(k)) return memo.get(k);
        if (have.has(k)) return EMPTY;
        if (!this.ROWS[k]) return null;
        if (S.lost.has(k) && !S.glimpsed.has(k) && !S.diff_since.has(k) && !S.diff_unc.has(k)) return null;   // an idea that isn't coming
        if (S.locked.has(k) && k !== S.end_k) return null;                                                     // a path not taken
        memo.set(k, new Set([k])); const req = new Set([k]);
        for (const grp of this.ROWS[k].pre) {
          let best = null;
          for (const opt of grp) {
            const s = new Set(); let ok = true;
            for (const p of opt) { const q = need(p); if (q === null) { ok = false; break; } for (const x of q) s.add(x); }
            if (!ok) continue;
            if (s.size === 0) { best = [0, s]; break; }
            const c = pysum([...s].map(cost));
            if (best === null || c < best[0]) best = [c, s];
          }
          if (best === null) { memo.set(k, null); return null; }
          for (const x of best[1]) req.add(x);
        }
        memo.set(k, req); return req;
      };
      const out = new Set();
      for (const alts of reqs) {
        const opts = alts.map(need).filter((q) => q !== null);
        if (!opts.length || opts.some((q) => q.size === 0)) continue;
        let best = null, bc = 0;
        for (const q of opts) { const c = pysum([...q].map(cost)); if (best === null || c < bc) { best = q; bc = c; } }
        for (const x of best) out.add(x);
      }
      return out;
    }
    /** w7f.hint_row: the cheapest workable next step on the cheapest path; hint_focus: its field */
    hintRow(alts, have) {
      have = have || this.S.have;
      const fr = [...this.smartTargets([alts], have)].filter((k) => this.prereqsMet(k, have));
      if (!fr.length) return null;
      let best = fr[0];
      for (const k of fr) if (this.COST[k] < this.COST[best]) best = k;
      return best;
    }
    hintFocus(alts, have) { const k = this.hintRow(alts, have); return k ? this.ROWS[k].focus : null; }

    // ---- the player's choices ----------------------------------------------------------------------------------------
    /** the focus to fund from the next turn on (null: automatic, the focus with the most work waiting) */
    setFocus(f) {
      if (f !== null && f !== undefined && !this.B.foci.some((x) => x.name === f)) return { ok: false, reason: 'No such focus.' };
      if ((f || null) !== this.S.choice) { this.S.choice = f || null; this._act('focus', this.S.choice); }
      return { ok: true };
    }
    isRevealed(k) {
      const S = this.S;
      return (this.tier(k) === 'CORE' && S.occurred.has(k)) || S.glimpsed.has(k) || S.diff_since.has(k) || S.diff_unc.has(k);
    }
    endeavourCheck(id) {
      const S = this.S;
      if (!this.ROWS[id]) return 'That breakthrough cannot exist in this world.';
      if (S.have.has(id)) return 'Already discovered.';
      if (!this.isRevealed(id)) return 'Only a revealed breakthrough can be the goal of an Endeavour.';
      if (!this.prereqsMet(id, S.have)) return 'Its prerequisites are not all discovered.';
      if (this.END_UNOCCURRED_ONLY && S.occurred.has(id)) return 'Endeavours are only for ideas that have not occurred.';
      if (this.END_FROM !== null && ![...S.have.keys()].some((k) => this.ROWS[k].eraI >= this.END_FROM)) return 'Endeavours are not yet available.';
      if (S.proto) return 'The prototype is under construction.';
      return null;
    }
    /** pursue a revealed breakthrough as a Grand Endeavour from the next turn (2x its price then; replaces a running one) */
    requestEndeavour(id) {
      if (this.over) return { ok: false, reason: 'The game is over.' };
      const why = this.endeavourCheck(id);
      if (why) return { ok: false, reason: why };
      const S = this.S, replaced = S.end_k;
      if (S.end_k !== null && S.end_k !== id) { S.end_k = null; S.end_prog = 0.0; S.end_cost = 0.0; }
      if (S.end_k === id) return { ok: true, running: true };
      S.endRequest = id; this._act('end', id);
      return { ok: true, replaced: replaced || null };
    }
    stopEndeavour() {
      const S = this.S;
      if (S.end_k === null && S.endRequest === null) return { ok: false, reason: 'No Endeavour is under way.' };
      S.end_k = null; S.end_prog = 0.0; S.end_cost = 0.0; S.endRequest = null; this._act('stop', null);
      return { ok: true };
    }
    /** what an Endeavour on id would cost if it started next turn, and how many turns its share would take to fill it */
    endeavourQuote(id) {
      const S = this.S, t1 = S.turn + 1, d = this.D[t1];
      if (!this.ROWS[id]) return null;
      const cost = this.endPrice(id, d), es = S.have.has('SO05') ? 0.8 : 0.5;
      return { cost, turns: this._turnsToFill(cost, es, t1), premium: pow(this.P.premium, Math.max(0.0, this.ROWS[id].eraI - d)),
        aheadOfTime: this.ROWS[id].eraI - d > 0, eligible: !this.endeavourCheck(id), reason: this.endeavourCheck(id) };
    }
    _turnsToFill(cost, share, t1) {
      let acc = 0.0, t = t1;
      while (acc < cost && t < this.INC.length) { acc += this.INC[t] * share; t++; }
      return t - t1;
    }
    /** the prototype's price if committed now (victory.py: PROTOX x the Space price x calibration x the premium at d) */
    protoCost() {
      const V = this.B.victory;
      return V.protox * V.p_space * V.scale * V.spaceprice * pow(4, Math.max(0.0, V.space - this.S.d));
    }
    prototypeQuote(method) {
      const S = this.S, cost = this.protoCost(), es = S.have.has('SO05') ? 0.8 : 0.5;
      return { cost, turns: this._turnsToFill(cost, es, S.turn + 1), eligible: !this.prototypeCheck(method), reason: this.prototypeCheck(method) };
    }
    prototypeCheck(method) {
      const S = this.S, F = this.F;
      if (!F.COND[method]) return 'No such hypothesis in this world.';
      if (S.victory) return 'The game is won.';
      if (S.protoWorked) return 'A prototype already works.';
      if (S.proto) return 'A prototype is already under construction.';
      if (!S.have.has(this.OPENS)) return 'The question has not been asked yet.';
      if (!this._proposed(method)) return 'That hypothesis has not been proposed.';
      if (S.protoFailed.has(method)) return 'Its prototype failed.';
      const kn = this.knowledge(S.have, S.turn);
      if (F.COND[method].some((c) => c in kn && !kn[c])) return 'The hypothesis has been ruled out.';
      if (!F.BUILD[method].every((g) => g.some((x) => S.have.has(x)))) return 'Its build needs are not all met.';
      return null;
    }
    /** commit the prototype of a proposed, standing hypothesis whose build is complete (a running Endeavour is stopped) */
    commitPrototype(method) {
      const why = this.prototypeCheck(method);
      if (why) return { ok: false, reason: why };
      const S = this.S;
      const stopped = S.end_k || S.endRequest;
      S.end_k = null; S.end_prog = 0.0; S.end_cost = 0.0; S.endRequest = null;
      S.proto = { method, cost: this.protoCost(), progress: 0.0, committed: S.turn };
      this._act('proto', method);
      return { ok: true, cost: S.proto.cost, stoppedEndeavour: stopped || null };
    }
    _act(a, v) { this.actions.push({ t: this.S.turn, a, v }); }

    get over() { const S = this.S; return !!S.victory || S.turn >= this.maxTurns || S.have.size >= this.IDS.length; }
    get turn() { return this.S.turn; }
    get victory() { return this.S.victory; }

    // ---- one turn: harness_ftl_e.run()'s loop body -----------------------------------------------------------------
    step() {
      if (this.over) return [];
      const S = this.S, P = this.P, ROWS = this.ROWS, rng = this.rng, TARGET = this.TARGET;
      const before = this._revealedSet();
      S.turn += 1; const turn = S.turn;
      const inc = this.INC[turn], d = this.D[turn];
      const have = S.have, events = [];
      let end_done = null, proto_done = false;
      for (const p of S.new_rows) for (const k of (this.dependents.get(p) || [])) if (!S.met.has(k) && this.prereqsMet(k, have)) S.met.add(k);
      S.new_rows = [];
      const disc = [];
      for (const k of this.IDS) if (!have.has(k) && S.met.has(k) && (!S.locked.has(k) || k === S.end_k)) disc.push(k);
      const diff_due = [];
      if (this.DIFF) {                                      // knowledge diffusion (§1.2): contacted rivals, Printing Press, Internet
        if (S.contact_turn === null && S.maxEraHeld >= this.DIFF.contact_era) S.contact_turn = turn;
        if (S.cp04_turn === null && have.has('CP04')) S.cp04_turn = turn;
        if (S.contact_turn !== null) {
          const riv = this.DIFF.rivals, nr = riv.length;
          for (const k of disc) {
            const tk = ROWS[k].tier;
            if (tk === 'UNIQUE') continue;
            let nh = 0;
            for (const r of riv) { const v = r.get(k); if ((v === undefined ? 1e9 : v) <= turn) nh++; }
            if (nh === 0) continue;
            if (nh / nr < P.diff_share) continue;
            if ((tk === 'CORE' || tk === 'STANDARD') && have.has('MC06')) {
              if (!S.diff_since.has(k)) S.diff_since.set(k, turn);
              const s0 = S.diff_since.get(k);
              if (turn - s0 >= P.diff_wait || (S.cp04_turn !== null && turn - Math.max(s0, S.cp04_turn) >= P.diff_wait_net)) diff_due.push(k);
            } else if (tk === 'UNCOMMON' && S.cp04_turn !== null) {
              if (!S.diff_unc.has(k)) S.diff_unc.set(k, turn);
              const s0 = S.diff_unc.get(k);
              if (turn - s0 >= P.diff_wait_net) diff_due.push(k);
            }
          }
        }
      }
      for (const k of disc) if (!S.opened.has(k)) S.opened.set(k, turn);
      const occ0 = this.recordTrace ? new Set(S.occurred) : null, gl0 = new Set(S.glimpsed), lost0 = new Set(S.lost);
      const seen0 = new Set([...S.diff_since.keys(), ...S.diff_unc.keys()]), lk0 = new Set(S.locked);
      // the moment: a non-CORE idea occurs to the civilisation with a small chance each turn while it lasts
      for (const k of disc) {
        if (S.occurred.has(k)) continue;
        const t = ROWS[k].tier;
        if (t === 'CORE') { S.occurred.add(k); continue; }   // (W16 is off: no funded-focus rule)
        if (S.lost.has(k)) continue;
        const era = ROWS[k].era;
        let W = (this.WIN_TURNS ? (this.WIN_TURNS[era] !== undefined ? this.WIN_TURNS[era] : this.TURNS[era]) : this.TURNS[era]) * P.window[t] * 1.0;
        const behind = d - (ROWS[k].eraI + 1);
        if (P.compress && behind > 0) W = W / (1 + P.compress * behind);
        W = Math.max(W, 1.0);
        const t0 = S.opened.get(k);
        if (turn - t0 > W) { S.lost.add(k); if (!S.lost_at.has(k)) S.lost_at.set(k, turn); continue; }   // the moment has passed
        if (t !== 'STANDARD' && d > ROWS[k].eraI + 1 + P.grace) { S.lost.add(k); if (!S.lost_at.has(k)) S.lost_at.set(k, turn); continue; }
        if (rng.random() < 1 - pow(1 - Math.min(TARGET[t], 0.999), 1 / W)) { S.occurred.add(k); S.occ_turn.set(k, turn); }
        else {                                              // proximity revelation: glimpsed, not found
          const g = this.GLIMPSE[t] || 0.0;
          if (g && !S.glimpsed.has(k) && this.grng.random() < g) S.glimpsed.add(k);
        }
      }
      const redisc = [];
      if (P.rediscover) {                                   // rediscovery on demand: a lost idea that other work waits on comes back
        let goals = null;
        for (const k of disc) {
          if (!S.lost.has(k) || S.occurred.has(k) || !P.rediscover_tiers.includes(ROWS[k].tier)) continue;
          if (goals === null) goals = this.ftlGoals(have, turn);
          let n = 0;
          for (const j of (this.dependents.get(k) || [])) {
            if (have.has(j) || S.met.has(j)) continue;
            if (ROWS[j].pre.every((grp) => grp.some((opt) => opt.every((p) => have.has(p) || p === k)))) n++;   // ready but for k
          }
          for (const gs of goals) {                       // a goal ready but for k
            if (!gs.every((g) => g.some((x) => have.has(x))) && gs.every((g) => g.some((x) => have.has(x)) || g.includes(k))) n++;
          }
          if (n && this.rrng.random() < 1 - pow(1 - P.rediscover, n)) {
            S.occurred.add(k); S.occ_turn.set(k, turn); S.lost.delete(k); S.rediscovered.set(k, turn); redisc.push(k);
          }
        }
      }
      const live = disc.filter((k) => S.occurred.has(k));
      const pool = new Map();
      for (const k of live) { const f = ROWS[k].focus; if (!pool.has(f)) pool.set(f, []); pool.get(f).push(k); }
      const waiting = new Map(), pull = new Map();         // the simulated player's sense of where work waits; each focus's draw on the spread
      for (const [f, ks] of pool) {
        waiting.set(f, pysum(ks.map((k) => TARGET[ROWS[k].tier] * (1 + Math.max(0.0, d - ROWS[k].eraI)))));
        pull.set(f, P.tier_attention ? waiting.get(f) : pysum(ks.map((k) => (1 + Math.max(0.0, d - ROWS[k].eraI)))));
      }
      // the funded focus
      let active;
      if (this.player === 'generalist') active = maxKey(waiting);
      else if (this.player === 'advisor') active = this._adviceFocus(waiting) || maxKey(waiting);
      else active = S.choice || maxKey(waiting);
      const funded_choice = active;
      const sh = have.has('SO05') ? 0.8 : 0.5, es = sh;
      let started = false;
      if (S.end_k !== null && have.has(S.end_k)) {          // study found it first: the Endeavour ends
        events.push({ type: 'endeavour_ended', id: S.end_k, reason: 'studied' }); S.end_k = null; S.end_prog = 0.0; S.end_cost = 0.0;
      }
      if (this.END_MULT && S.end_k === null && !S.proto && (this.END_FROM === null || S.maxEraHeld >= this.END_FROM)) {
        const req = S.endRequest;
        if (req && !have.has(req) && this.prereqsMet(req, have) && !(this.END_UNOCCURRED_ONLY && S.occurred.has(req))) {
          S.end_k = req; S.end_cost = this.endPrice(req, d); S.end_prog = 0.0; started = true; S.endRequest = null;
          events.push({ type: 'endeavour_started', id: req, cost: S.end_cost });
        } else if (req && have.has(req)) S.endRequest = null;
      }
      const busy = S.end_k !== null || !!S.proto;
      if (S.end_k !== null) {                               // the Endeavour is the focus: it takes the active share; the spread still rolls
        S.end_prog += inc * es + S.bank; S.bank = 0.0; active = null;
        if (S.end_prog >= S.end_cost) { end_done = S.end_k; S.end_k = null; }
      } else if (S.proto) {                                 // the prototype: an Endeavour of its own kind (§4)
        S.proto.progress += inc * es; active = null;
        if (S.proto.progress >= S.proto.cost) proto_done = true;
      }
      const fociSet = new Set(pool.keys());
      for (const k of have.keys()) fociSet.add(ROWS[k].focus);
      const open_foci = pysorted(fociSet);
      let share = sh;
      const flow = new Map();
      const others = open_foci.filter((f) => f !== active && (P.spread_floor > 0 || pool.has(f)));
      if (active) { flow.set(active, inc * share + S.bank); S.bank = 0.0; }
      else if (!(this.SPREAD_FIX && (busy || end_done))) share = 0.0;   // no active focus: the spread takes everything
      const wt = new Map();
      for (const f of others) wt.set(f, (pull.has(f) ? pull.get(f) : 0) + P.spread_floor);
      const tw = pysum([...wt.values()]) || 1;
      for (const f of others) flow.set(f, (flow.has(f) ? flow.get(f) : 0) + inc * (1 - share) * wt.get(f) / tw);
      const found = [], foundSet = new Set(), via = new Map();
      if (end_done) { found.push(end_done); foundSet.add(end_done); via.set(end_done, 'endeavour'); }
      for (const k of diff_due) if (!foundSet.has(k)) { found.push(k); foundSet.add(k); via.set(k, 'diffusion'); }
      const need = S.need, progress = S.progress, shape = P.shape, momentum = P.momentum;
      const use = (f, ins) => {                             // spend `ins` Insight in focus f; return what it could not use
        let cands = (pool.get(f) || []).filter((k) => !have.has(k) && !foundSet.has(k));
        if (!cands.length) return ins;
        for (const k of cands) if (!need.has(k)) need.set(k, rng.gammavariate(shape, 1 / shape) * this._cm(k));
        let left = ins;
        const rounds = cands.length + 1;
        for (let it = 0; it < rounds; it++) {
          cands = cands.filter((k) => !foundSet.has(k));
          if (!cands.length || left <= 1e-9) break;
          const ws = cands.map((k) => (P.tier_attention ? TARGET[ROWS[k].tier] : 1.0) * ((progress.has(k) ? progress.get(k) : 0) + momentum) * 1.0);
          const tot = pysum(ws);
          let spent = 0.0; const done = [];
          for (let i = 0; i < cands.length; i++) {
            const k = cands[i], att = left * ws[i] / tot, pk = this.priceAt(k, d);
            const pr = progress.has(k) ? progress.get(k) : 0, room = (need.get(k) - pr) * pk;
            if (att >= room) { progress.set(k, need.get(k)); done.push(k); spent += room; }
            else { progress.set(k, pr + att / pk); spent += att; }
          }
          for (const k of done) { found.push(k); foundSet.add(k); }
          left -= spent;
          if (!done.length) { left = 0.0; break; }
        }
        return left;
      };
      const unused = new Map();
      for (const [f, ins] of flow) unused.set(f, use(f, ins));
      const spare = pysum([...unused.values()]);
      if (spare > 1e-9) {                                   // spill: Insight a focus cannot use goes at once to the other open foci
        const takers = new Map();
        for (const [f, ks] of pool) {
          const remaining = ks.some((k) => !have.has(k) && !foundSet.has(k));
          if (remaining && (unused.has(f) ? unused.get(f) : 0) <= 1e-9) takers.set(f, (pull.has(f) ? pull.get(f) : 0) + 0.1);
        }
        const tw2 = pysum([...takers.values()]);
        if (tw2 > 0) for (const [f, w] of takers) use(f, spare * w / tw2);
      }
      for (const k of found) {
        have.set(k, { turn, d, via: via.get(k) || 'own' }); S.new_rows.push(k);
        if (ROWS[k].eraI > S.maxEraHeld) S.maxEraHeld = ROWS[k].eraI;
      }
      for (const k of found) for (const a of (this.alts_of.get(k) || [])) if (!have.has(a)) S.locked.add(a);   // a primary found first
      S.d = d; S.inc = inc; S.share = share; S.flow = flow; S.live = live; S.active = active;
      S.fund = end_done || S.end_k !== null ? ['END', end_done || S.end_k] : S.proto ? ['PROTO', S.proto.method] : ['FOCUS', active];
      S.fundedChoice = funded_choice;

      if (this.recordTrace) {
        const newOcc = pysorted([...S.occurred].filter((k) => !occ0.has(k)));
        const prog = {};
        for (const k of live) if (!have.has(k) && need.get(k)) prog[k] = Math.min(progress.get(k) / need.get(k), 1.0);
        this.traceRecords.push({ turn, d, found: found.slice(), diff: found.filter((k) => diff_due.includes(k)), endv: end_done ? [end_done] : [],
          occ: newOcc.map((k) => [k, ROWS[k].tier === 'CORE' ? 'core' : 'chance']), glim: pysorted([...S.glimpsed].filter((k) => !gl0.has(k))),
          fund: S.fund[0] === 'PROTO' ? ['FOCUS', null] : S.fund, lost: pysorted([...S.lost].filter((k) => !lost0.has(k))),
          seen: pysorted([...S.diff_since.keys(), ...S.diff_unc.keys()].filter((k) => !seen0.has(k))), locked: pysorted([...S.locked].filter((k) => !lk0.has(k))),
          redisc: pysorted(redisc), inc, share, flow: Object.fromEntries(flow), prog,
          end: S.end_k !== null ? [S.end_k, S.end_cost ? S.end_prog / S.end_cost : 0.0] : null,
          raw: { progress: Object.fromEntries(live.filter((k) => need.has(k)).map((k) => [k, progress.has(k) ? progress.get(k) : 0.0])),
            need: Object.fromEntries(live.filter((k) => need.has(k)).map((k) => [k, need.get(k)])), end_prog: S.end_prog } });
      }

      // ---- the endgame: the prototype's result, the Drive, the launch (victory.py) ----
      if (proto_done) {
        const pm = S.proto.method, works = pm === this.method;
        S.protoResults.push({ method: pm, turn, works });
        events.push({ type: 'prototype_result', method: pm, works });
        if (works) {
          S.protoWorked = pm;
          const kind = this.B.victory.exotic.includes(pm) ? 'exotic' : 'plain';
          const tbl = this.B.victory.drive[this.econ][kind];
          const n = tbl[Math.min(turn, tbl.length - 1)];
          S.drive = { method: pm, turnsLeft: n, total: n, start: turn, done: null };
          events.push({ type: 'drive_started', method: pm, turns: n });
        } else S.protoFailed.add(pm);
        S.proto = null;
      } else if (S.drive && S.drive.done === null && turn > S.drive.start) {
        S.drive.turnsLeft -= 1;
        if (S.drive.turnsLeft <= 0) { S.drive.done = turn; events.push({ type: 'drive_done', method: S.drive.method }); }
      } else if (S.drive && S.drive.done !== null && turn === S.drive.done + 1) {
        const ref = REFERENCE[this.econ];
        S.victory = { turn, reference: ref, delta: ref !== undefined ? turn - ref : null, method: S.drive.method };
        events.push({ type: 'victory', turn, reference: ref, delta: S.victory.delta });
      }

      this._events(events, { found, via, redisc, gl0, lost0, seen0, lk0, before, turn });
      S.events = events.map((e) => Object.assign({ turn }, e));
      for (const e of S.events) S.log.push(e);
      return S.events;
    }

    /** advisor: the field the FTL screen's hints point to (questions first, then the builds of what still stands) */
    _adviceFocus() {
      const S = this.S, F = this.F, have = S.have;
      if (!have.has(this.OPENS)) return null;
      const { kn, alive, certain } = this.status(have, S.turn);
      const reqs = [];
      if (certain) { const m = alive.length === 1 ? alive[0] : this.METHODS.find((o) => F.COND[o].every((c) => kn[c])); for (const g of F.BUILD[m]) if (!g.some((x) => have.has(x))) reqs.push(g); }
      else {
        const qs = new Set();
        for (const o of alive) for (const c of F.COND[o]) if (!(c in kn) && !F.HOST[c].some((h) => have.has(h))) qs.add(c);
        for (const c of pysorted(qs)) reqs.push(F.HOST[c]);
        if (!reqs.length) for (const o of alive) for (const g of F.BUILD[o]) if (!g.some((x) => have.has(x))) reqs.push(g);
      }
      const cnt = new Map();
      for (const r of reqs) { const f = this.hintFocus(r, have); if (f) cnt.set(f, (cnt.get(f) || 0) + 1); }
      let best = null;
      for (const [f, n] of cnt) if (best === null || n > cnt.get(best) || (n === cnt.get(best) && f > best)) best = f;
      return best;
    }
    /** a suggestion for the human: the advisor's focus, and the prototype to commit once a method is certain and built */
    advise() {
      const S = this.S, f = this._adviceFocus();
      const st = S.have.has(this.OPENS) ? this.status(S.have, S.turn) : null;
      let proto = null;
      if (st && st.certain && !S.proto && !S.protoWorked) {
        const m = st.alive.length === 1 ? st.alive[0] : this.METHODS.find((o) => this.F.COND[o].every((c) => st.kn[c]));
        if (m && !this.prototypeCheck(m)) proto = m;
      }
      return { focus: f, prototype: proto, why: f ? 'Where the FTL screen points.' : 'The field with the most work waiting.' };
    }

    // ---- what the player sees change ---------------------------------------------------------------------------------
    _revealedSet() {
      const out = new Set(), S = this.S;
      for (const k of S.occurred) if (this.tier(k) === 'CORE') out.add(k);
      for (const k of S.glimpsed) out.add(k);
      for (const k of S.diff_since.keys()) out.add(k);
      for (const k of S.diff_unc.keys()) out.add(k);
      return out;
    }
    _fociEntered() {
      const S = this.S, out = new Set();
      for (const k of S.met) if (this.ROWS[k]) out.add(this.ROWS[k].focus);
      for (const k of S.have.keys()) out.add(this.ROWS[k].focus);
      return out;
    }
    eraByCount() {
      const S = this.S, n = new Array(this.SPAN_E).fill(0);
      for (const k of S.have.keys()) n[this.ROWS[k].eraI]++;
      let atLeast = 0, era = this.EO[0];
      const cum = new Array(this.SPAN_E).fill(0);
      for (let i = this.SPAN_E - 1; i >= 0; i--) { atLeast += n[i]; cum[i] = atLeast; }
      for (let i = 1; i < this.SPAN_E; i++) if (ERA_COUNT[this.EO[i]] !== undefined && cum[i] >= ERA_COUNT[this.EO[i]]) era = this.EO[i];
      return era;
    }
    _events(events, x) {
      const S = this.S, ROWS = this.ROWS;
      const now = this._revealedSet();
      for (const k of x.found) events.push({ type: 'discovered', id: k, via: x.via.get(k) || 'own', focus: ROWS[k].focus, era: ROWS[k].era });
      for (const k of now) if (!x.before.has(k) && !S.have.has(k)) {
        const how = S.glimpsed.has(k) && !x.gl0.has(k) ? 'glimpse' : (S.diff_since.has(k) || S.diff_unc.has(k)) && !x.seen0.has(k) ? 'rivals' : 'core';
        events.push({ type: 'revealed', id: k, how });
      }
      for (const k of pysorted([...S.lost].filter((k) => !x.lost0.has(k)))) events.push({ type: 'moment_passed', id: k, hidden: !now.has(k) });
      for (const k of pysorted([...S.locked].filter((k) => !x.lk0.has(k)))) events.push({ type: 'path_not_taken', id: k, primary: this.COMPETE[k], hidden: !now.has(k) });
      for (const k of x.redisc) events.push({ type: 'rediscovered', id: k, hidden: !now.has(k) });
      const foci = this._fociEntered();
      for (const f of foci) if (!S.foci.has(f)) events.push({ type: 'focus_entered', focus: f });
      S.foci = foci;
      const era = this.eraByCount();
      if (era !== S.eraName) { events.push({ type: 'era_entered', era }); S.eraName = era; }
      // the FTL screen: every change is announced, saying only that something changed
      const sig = this._ftlSignature();
      if (sig.key !== S.ftlSig.key) {
        const changes = this._ftlChanges(S.ftlSig, sig);
        if (changes.length) events.push({ type: 'ftl', text: FTL_TEXT, changes });
        for (const ch of changes) if (ch.kind === 'instrument') events.push({ type: 'instrument_complete', cond: ch.cond, instrument: this.INSTRUMENT[ch.cond] });
      }
      S.ftlSig = sig;
      if (S.cert === null && S.have.has(this.OPENS) && this.status(S.have, S.turn).certain) S.cert = S.turn;
    }
    _ftlSignature() {
      const S = this.S, F = this.F, have = S.have;
      if (!have.has(this.OPENS)) return { key: 'closed', open: false };
      const kn = this.knowledge(have, S.turn);
      const proposed = this.METHODS.filter((o) => this._proposed(o));
      const alive = this.METHODS.filter((o) => !F.COND[o].some((c) => c in kn && !kn[c]) && !S.protoFailed.has(o));
      const standing = proposed.filter((o) => alive.includes(o));        // what the checklist shows: proposed and not disproved
      const awaiting = Object.keys(F.HOST).filter((c) => !(c in kn) && F.HOST[c].some((h) => have.has(h)) && standing.some((o) => F.COND[o].includes(c)));
      const built = this.METHODS.map((o) => (standing.includes(o) ? F.BUILD[o].map((g) => (g.some((y) => have.has(y)) ? 1 : 0)).join('') : ''));
      const sig = { open: true, closed: have.has(F.CLOSE), proposed, kn, alive, awaiting, built };
      sig.key = JSON.stringify(sig);
      return sig;
    }
    _ftlChanges(a, b) {
      const out = [], F = this.F;
      if (!a.open) out.push({ kind: 'opened' });
      for (const o of b.proposed) if (!a.open || !a.proposed.includes(o)) out.push({ kind: 'proposed', method: o });
      if (b.closed && !a.closed) out.push({ kind: 'list_closed' });
      for (const c of Object.keys(b.kn)) if (!a.open || !(c in a.kn)) {
        out.push({ kind: 'result', cond: c, holds: !!b.kn[c], question: F.QUESTION[c] });
        if (a.open && a.awaiting.includes(c)) out.push({ kind: 'instrument', cond: c });
      }
      for (const c of b.awaiting) if (!a.open || !a.awaiting.includes(c)) if (this.INSTR[c]) out.push({ kind: 'awaiting', cond: c, instrument: this.INSTRUMENT[c] });
      for (const o of this.METHODS) {
        if (a.open && a.alive.includes(o) && !b.alive.includes(o)) out.push({ kind: 'ruled_out', method: o });
        const i = this.METHODS.indexOf(o);
        if (a.open && b.built[i] && a.built[i] && a.built[i] !== b.built[i]) out.push({ kind: 'build', method: o, complete: !b.built[i].includes('0') });
      }
      if (b.alive.length === 1 && (!a.open || a.alive.length !== 1) && b.closed) out.push({ kind: 'last_standing', method: b.alive[0] });
      return out;
    }
    _proposed(o) {
      const have = this.S.have;
      return have.has(this.OPENS) && (have.has(this.F.PROPOSER[o]) || have.has(this.F.CLOSE));
    }

    // ---- the FTL screen ------------------------------------------------------------------------------------------------
    /** the FTL screen's state (null until Relativity opens it): every hypothesis with its conditions, build needs and hints,
        the running results and the prototype; the view hides what the player cannot know (unproposed hypotheses, names
        of rows not revealed, the truth). opts.hints false skips the hints (they search the tree). */
    ftl(opts) {
      const S = this.S, F = this.F, have = S.have, now = S.turn;
      if (!have.has(this.OPENS)) return null;
      const hints = !opts || opts.hints !== false;
      const kn = this.knowledge(have, now);
      const name = (k) => (this.B.rows[k] ? this.B.rows[k].name : k);
      const condState = (c) => {
        const hosts = F.HOST[c], held = hosts.filter((h) => have.has(h));
        const st = { id: c, question: F.QUESTION[c], hosts: hosts.map((h) => ({ id: h, name: name(h), held: have.has(h), revealed: this.ROWS[h] ? this.isRevealed(h) : false })),
          instrument: this.INSTR[c] ? this.INSTRUMENT[c] : null };
        if (c in kn) { st.state = kn[c] ? 'holds' : 'fails'; st.turn = this.readyTurn(c, have); }
        else if (held.length) {
          const rt = this.readyTurn(c, have);
          if (rt !== null && rt > now) { st.state = 'awaiting'; st.turnsLeft = rt - now; st.readyTurn = rt; }
          else { st.state = 'open'; st.untestable = true; }   // MS08 where exotic matter does not exist: the answer never comes
        } else { st.state = 'open'; if (hints) st.hint = this.hintFocus(hosts, have); }
        return st;
      };
      const conds = {};
      for (const c of Object.keys(F.HOST)) conds[c] = condState(c);
      const closed = have.has(F.CLOSE);
      const hyps = this.METHODS.map((o) => {
        const proposed = this._proposed(o);
        const pt = proposed ? (have.has(F.PROPOSER[o]) ? Math.max(have.get(F.PROPOSER[o]).turn, have.get(this.OPENS).turn) : have.get(F.CLOSE).turn) : null;
        const cs = F.COND[o].map((c) => conds[c]);
        const fails = cs.filter((c) => c.state === 'fails').map((c) => c.id);
        const build = F.BUILD[o].map((g) => {
          const met = g.some((x) => have.has(x));
          return { options: g.map((x) => ({ id: x, name: name(x), held: have.has(x), inWorld: !!this.ROWS[x], revealed: this.ROWS[x] ? this.isRevealed(x) : false })),
            met, hint: !met && hints ? this.hintFocus(g, have) : null };
        });
        return { method: o, proposed, proposedTurn: pt, conditions: cs, build, buildComplete: build.every((g) => g.met),
          alive: !fails.length && !S.protoFailed.has(o), ruledOutBy: fails, prototypeFailed: S.protoFailed.has(o),
          confirmed: cs.every((c) => c.state === 'holds'), canCommit: !this.prototypeCheck(o) };
      });
      const alive = hyps.filter((h) => h.alive);
      for (const h of hyps) h.lastStanding = closed && h.alive && alive.length === 1;
      const results = Object.values(conds).filter((c) => c.state === 'holds' || c.state === 'fails')
        .map((c) => ({ turn: c.turn, cond: c.id, question: c.question, holds: c.state === 'holds' }))
        .sort((x, y) => x.turn - y.turn || (x.cond < y.cond ? -1 : 1));
      const st = this.status(have, now);
      return { open: true, openedTurn: have.get(this.OPENS).turn, closed, count: this.METHODS.length, hypotheses: hyps, results,
        certain: st.certain, certainTurn: S.cert, prototype: S.proto ? Object.assign({ fraction: Math.min(S.proto.progress / S.proto.cost, 1) }, S.proto) : null,
        prototypeResults: S.protoResults.slice(), drive: S.drive ? Object.assign({}, S.drive) : null, victory: S.victory,
        prototypeQuote: { cost: this.protoCost() }, instrumentTurns: this.INSTR_D };
    }

    // ---- the state for the screens -----------------------------------------------------------------------------------
    snapshot(opts) {
      const S = this.S, ROWS = this.ROWS, have = {};
      for (const [k, v] of S.have) have[k] = { turn: v.turn, via: v.via };
      const prog = {};
      for (const k of S.live) if (!S.have.has(k) && S.need.get(k)) prog[k] = Math.min(S.progress.get(k) / S.need.get(k), 1.0);
      const riv = {};
      if (this.DIFF) for (const k of this.IDS) {
        if (S.have.has(k)) continue;
        let n = 0; for (const r of this.DIFF.rivals) { const v = r.get(k); if (v !== undefined && v <= S.turn) n++; }
        if (n) riv[k] = n;
      }
      const spread = [...S.flow.entries()].filter(([f]) => f !== S.active).reduce((a, [, v]) => a + v, 0);
      return {
        turn: S.turn, world: this.world, ontology: this.ontology, econ: this.ECON, d: S.d, inc: S.inc, share: S.share,
        funded: S.active, fund: S.fund, choice: S.choice, spread, maxTurns: this.maxTurns, over: this.over, player: this.player,
        era: this.eraByCount(), devEra: this.EO[Math.min(Math.floor(S.d), this.SPAN_E - 1)],
        endeavour: S.end_k !== null ? { id: S.end_k, progress: S.end_cost ? S.end_prog / S.end_cost : 0, cost: S.end_cost, spent: S.end_prog } : null,
        endeavourRequest: S.endRequest,
        prototype: S.proto ? { method: S.proto.method, progress: Math.min(S.proto.progress / S.proto.cost, 1), cost: S.proto.cost, spent: S.proto.progress } : null,
        drive: S.drive && S.drive.done === null ? { method: S.drive.method, turnsLeft: S.drive.turnsLeft, total: S.drive.total } :
          S.drive ? { method: S.drive.method, turnsLeft: 0, total: S.drive.total, done: S.drive.done } : null,
        victory: S.victory,
        have, occurred: pysorted(S.occurred), glimpsed: pysorted(S.glimpsed), seen: pysorted([...S.diff_since.keys(), ...S.diff_unc.keys()]),
        lost: pysorted(S.lost), locked: pysorted(S.locked), prog, flow: Object.fromEntries(S.flow),
        foci: pysorted(S.foci), discoverable: this.IDS.filter((k) => !S.have.has(k) && S.met.has(k) && (!S.locked.has(k) || k === S.end_k)),
        events: S.events.slice(), ftl: (opts && opts.ftl === false) ? null : this.ftl(opts),
        hidden: { method: this.method, truth: Object.assign({}, this.truth), seed: this.seed, game: this.game, rivalsHold: riv,
          rediscovered: Object.fromEntries(S.rediscovered), lostAt: Object.fromEntries(S.lost_at), certainTurn: S.cert },
      };
    }

    // ---- saving: the options and every choice, replayed ------------------------------------------------------------------
    serialize() { return { format: 'uh-engine-1', version: this.B.version, options: this.opts, actions: this.actions.slice(), turn: this.S.turn }; }
    static restore(bundle, saved) {
      if (!saved || saved.format !== 'uh-engine-1') throw new Error('not a saved game');
      const e = new UHEngine(bundle, saved.options);
      if (saved.version && saved.version !== bundle.version) e.restoreWarning = `Saved under ${saved.version}; this is ${bundle.version}: the game may differ.`;
      for (const act of saved.actions) {
        while (e.S.turn < act.t && !e.over) e.step();
        if (act.a === 'focus') e.setFocus(act.v);
        else if (act.a === 'end') e.requestEndeavour(act.v);
        else if (act.a === 'stop') e.stopEndeavour();
        else if (act.a === 'proto') e.commitPrototype(act.v);
      }
      while (e.S.turn < saved.turn && !e.over) e.step();
      return e;
    }

    /** play to the end (generalist or advisor), returning {row: turn} */
    runToEnd() { while (!this.over) this.step(); const t = {}; for (const [k, v] of this.S.have) t[k] = v.turn; return t; }
  }

  UHEngine.pysum = pysum;
  UHEngine.maxKey = maxKey;
  UHEngine.SEED0 = SEED0;
  UHEngine.REFERENCE = REFERENCE;
  UHEngine.ERA_COUNT = ERA_COUNT;
  UHEngine.FTL_TEXT = FTL_TEXT;
  UHEngine.PyRandom = PyRandom;
  return UHEngine;
});
