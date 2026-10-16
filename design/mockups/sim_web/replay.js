/* replay.js: the replay viewer. Plays a simulator log (w7f.py's TRACE output, one game) turn by turn on the research screen
   and the FTL screen.

   UHReplay.reconstruct(bundle, trace) -> game: rebuilds each turn's snapshot from the log's deltas (found, diff, endv,
   occ, glim, lost, redisc, locked, seen; each turn's d, inc, share, fund, flow, prog, end) and the turn's events, and
   derives the FTL screen from the hypotheses' proposers, the conditions' hosts and instruments, the build lists and the
   world's truth. The harness does not record rows first seen in rivals' hands (its `seen` field is always empty: it is
   measured after the diffusion step has already added them), so they are rebuilt from the bundle's rival pool exactly as
   the harness chooses rivals (the pool's games of the log's method, five from (game // 5) * 5), whenever the log shows
   diffusion at all. game.seenCheck reports how many diffusion arrivals that reconstruction explains.
   UHReplay.start() runs the page (src/replay.html). No DOM is touched by reconstruct(), so it runs in Node too. */
(function (G) {
  'use strict';
  const V = G.UHView || (typeof require !== 'undefined' ? require('./view.js') : null);
  const NOTABLE = new Set(['era', 'focus', 'ftl', 'endeavour', 'finish']);
  const PLAYER = (t) => t.player === 'novice' && Number(t.econ) < 0.95 ? 'average' : (t.player || 'expert');

  function reconstruct(bundle, trace) {
    if (!trace || !Array.isArray(trace.records) || !trace.records.length) throw new Error('This file is not a simulator log: it has no turn records (run w7f.py with TRACE=<file>, or copy the live game’s log).');
    if (!bundle.worlds[trace.world]) throw new Error('Unknown world in the log: ' + trace.world + '.');
    const econ = Number(trace.econ) || 1, key = V.econKey(econ);
    if (!bundle.economy[key] || !bundle.victory.drive[key])
      throw new Error('This log was played on a ×' + econ + ' economy; the bundle has only ' + Object.keys(bundle.economy).map(k => '×' + k).join(' and ') + '.');
    const W = V.world(bundle, trace.world), R = bundle.rows, recs = trace.records, E = bundle.economy[key];
    const byTurn = {};
    for (const r of recs) byTurn[r.turn] = r;
    const first = recs[0].turn, last = recs[recs.length - 1].turn;
    for (const r of recs) for (const k of r.found || []) if (!R[k]) throw new Error('The log names a row the bundle does not know (' + k + '): rebuild the bundle for the tree the log was made on.');
    // a live game's log (play.html) carries its own endgame: the choices, the prototypes, the Drive and the launch
    const live = Array.isArray(trace.choices) || trace.player === 'human';

    // the rivals, as w7f.py replays them, when the game had knowledge diffusion (the live game's log says; a simulator log
    // made by make_traces.sh records DIFF; otherwise any arrival from abroad shows it)
    const anyDiffusion = recs.some(r => (r.diff || []).length);
    const st = trace.settings || {};
    const diffusion = trace.diffusion != null ? !!trace.diffusion : st.DIFF != null ? String(st.DIFF) !== '0' : anyDiffusion;
    const num = (k, d) => (st[k] != null && isFinite(+st[k]) ? +st[k] : d);
    const DIFF_WAIT = num('DIFFWAIT', bundle.model.diff_wait), DIFF_WAIT_NET = num('DIFFWAITNET', bundle.model.diff_wait_net), DIFF_SHARE = num('DIFFSHARE', bundle.model.diff_share);
    const pm = W.pool.filter(g => g.m === trace.m), j0 = Math.floor((trace.game || 0) / 5) * 5;
    const rivals = diffusion && pm.length ? [0, 1, 2, 3, 4].map(j => pm[(j0 + j) % pm.length]) : [];
    const idx = {};
    W.ids.forEach((k, i) => { idx[k] = i; });
    const rivalTurn = (j, k) => { const v = rivals[j].t[idx[k]]; return v == null ? null : v / econ; };
    // rows first seen in rivals' hands: the log's own `seen` (the live game's), else rebuilt from the rivals (the harness's
    // `seen` is always empty: it is measured after its diffusion step has already added them)
    const rebuildSeen = rivals.length > 0 && anyDiffusion && !recs.some(r => (r.seen || []).length);

    // walk the log once, keeping the turn at which each thing happened
    const haveT = {}, occT = {}, glT = {}, lostT = {}, rediscT = {}, lockT = {}, seenT = {};
    const have = {}, dependents = {};
    for (const k of W.ids) for (const grp of R[k].pre) for (const opt of grp) for (const p of opt) (dependents[p] = dependents[p] || []).push(k);
    const met = new Set(W.ids.filter(k => V.prereqsMet(R[k], have)));
    let contact = null, cp04 = null, endK = null, maxEra = -1;
    const diffArrivals = [];
    for (let t = first; t <= last; t++) {
      const rec = byTurn[t];
      if (!rec) continue;
      if (rebuildSeen) {                                         // harness_ftl_e.run's diffusion step, before the turn's discoveries
        if (contact === null && maxEra >= V.EO.indexOf('Early Modern')) contact = t;
        if (cp04 === null && have.CP04) cp04 = t;
        if (contact !== null) {
          for (const k of met) {
            if (have[k] || (lockT[k] !== undefined && k !== endK)) continue;
            const tier = W.tier(k);
            if (tier === 'UNIQUE' || seenT[k] !== undefined) continue;
            let nh = 0;
            for (let j = 0; j < rivals.length; j++) { const v = rivalTurn(j, k); if (v !== null && v <= t) nh++; }
            if (!nh || nh / rivals.length < DIFF_SHARE) continue;
            if ((tier === 'CORE' || tier === 'STANDARD') && have.MC06) seenT[k] = t;
            else if (tier === 'UNCOMMON' && cp04 !== null) seenT[k] = t;
          }
        }
      } else if (cp04 === null && have.CP04) cp04 = t;
      for (const o of rec.occ || []) { const k = Array.isArray(o) ? o[0] : o; if (occT[k] === undefined) occT[k] = t; }
      for (const k of rec.glim || []) if (glT[k] === undefined) glT[k] = t;
      for (const k of rec.lost || []) lostT[k] = t;
      for (const k of rec.redisc || []) rediscT[k] = t;
      for (const k of rec.locked || []) if (lockT[k] === undefined) lockT[k] = t;
      for (const k of rec.seen || []) if (seenT[k] === undefined) seenT[k] = t;
      for (const k of rec.found || []) {
        const via = (rec.endv || []).includes(k) ? 'endeavour' : (rec.diff || []).includes(k) ? 'diffusion' : 'own';
        haveT[k] = { turn: t, via };
        have[k] = haveT[k];
        if (via === 'diffusion') diffArrivals.push([k, t]);
        if (W.eraI[k] !== undefined) maxEra = Math.max(maxEra, W.eraI[k]);
        for (const d of dependents[k] || []) if (!met.has(d) && V.prereqsMet(R[d], have)) met.add(d);
      }
      endK = rec.end ? rec.end[0] : null;
    }
    // how many diffusion arrivals the rows seen abroad explain (each needs its wait after being seen)
    let explained = 0;
    for (const [k, t] of diffArrivals) {
      const s0 = seenT[k];
      if (s0 === undefined) continue;
      const tier = W.tier(k);
      if (tier === 'UNCOMMON' ? t - s0 >= DIFF_WAIT_NET : (t - s0 >= DIFF_WAIT || (cp04 !== null && t - Math.max(s0, cp04) >= DIFF_WAIT_NET))) explained++;
    }

    // ---- the endgame of a live game: each prototype from its commitment to its result, the SS FTL Drive, the launch
    const V0 = bundle.victory;
    const protoCost = d => V0.protox * V0.p_space * V0.scale * V0.spaceprice * Math.pow(4, Math.max(0, V0.space - d));
    const runs = [];
    if (live) {
      const results = (trace.prototypes || []).slice().sort((a, b) => a.turn - b.turn);
      (trace.choices || []).filter(a => a.a === 'proto').forEach((c, i) => {
        const r = results[i] || null, dAt = c.t > 0 ? (byTurn[c.t] ? byTurn[c.t].d : E.d[c.t]) : 0;
        runs.push({ method: c.v, committed: c.t, from: c.t + 1, to: r ? r.turn : null, works: r ? !!r.works : null, cost: protoCost(dAt) });
      });
      // a log without the per-turn prototype record (before 16 October): its progress, as the engine accrues it
      for (const run of runs) {
        run.progress = {};
        let acc = 0;
        for (let t = run.from; t <= (run.to != null ? run.to : last); t++) {
          const rec = byTurn[t] || {};
          acc += (rec.inc != null ? rec.inc : E.inc[t]) * (haveT.SO05 && haveT.SO05.turn < t ? 0.8 : 0.5);
          run.progress[t] = Math.min(acc / run.cost, 1);
        }
      }
    }
    const actual = live && trace.victory ? trace.victory : null;
    let drive = null;
    if (live) {
      const worked = runs.find(r => r.works);
      if (trace.drive) drive = { method: trace.drive.method, start: trace.drive.start, total: trace.drive.total, done: trace.drive.done != null ? trace.drive.done : null };
      else if (worked && worked.to != null) {
        const tbl = V0.drive[key][V0.exotic.includes(worked.method) ? 'exotic' : 'plain'], n = tbl[Math.min(worked.to, tbl.length - 1)];
        drive = { method: worked.method, start: worked.to, total: n, done: worked.to + n <= (actual ? actual.turn : last) ? worked.to + n : null };
      }
    }
    // the prototype the funded share went to this turn; on its result turn it is finished (done), as the engine has it
    const protoAt = T => {
      const rec = byTurn[T] || {};
      let p = null;
      if (rec.proto) p = { method: rec.proto[0], progress: rec.proto[1], cost: rec.proto[2] };
      else { const run = runs.find(r => T >= r.from && (r.to == null || T <= r.to)); if (run) p = { method: run.method, progress: run.progress[T] || 0, cost: run.cost }; }
      if (p && (trace.prototypes || []).some(r => r.turn === T && r.method === p.method)) p.done = true;
      return p;
    };
    const driveAt = T => {
      if (!drive || T < drive.start) return null;
      if (drive.done != null && T >= drive.done) return { method: drive.method, turnsLeft: 0, total: drive.total, done: drive.done };
      return { method: drive.method, turnsLeft: drive.total - (T - drive.start), total: drive.total };
    };

    const states = {}, ftls = {}, evs = {};
    const pick = (m, T) => { const out = []; for (const k in m) if (m[k] <= T) out.push(k); return out; };
    function state(T) {
      if (states[T]) return states[T];
      const rec = byTurn[T] || {};
      const h = {};
      for (const k in haveT) if (haveT[k].turn <= T) h[k] = haveT[k];
      const fund = rec.fund || ['FOCUS', null], pr = live ? protoAt(T) : null;
      const s = {
        turn: T, world: trace.world, ontology: W.ontology, econ, d: rec.d != null ? rec.d : E.d[T], inc: rec.inc != null ? rec.inc : E.inc[T],
        share: rec.share != null ? rec.share : (h.SO05 ? 0.8 : 0.5),
        funded: fund[0] === 'FOCUS' ? fund[1] : null,
        endeavour: fund[0] === 'END' ? { id: fund[1], progress: rec.end ? rec.end[1] : 1 } : null,
        prototype: pr && !pr.done ? pr : null, prototypeDone: pr && pr.done ? pr : null, drive: live ? driveAt(T) : null, victory: actual && T >= actual.turn ? actual : null,
        prototypeResults: live ? (trace.prototypes || []).filter(r => r.turn <= T) : [],
        have: h, occurred: pick(occT, T), glimpsed: pick(glT, T), seen: pick(seenT, T),
        lost: pick(lostT, T).filter(k => !(rediscT[k] <= T)), locked: pick(lockT, T),
        prog: rec.prog || {}, flow: rec.flow || {}, events: [], ftl: null,
        engine: { method: trace.m, truth: trace.truth, nRivals: rivals.length, rivals: rivalCounts(T) },
      };
      if (pr) s.funded = null;
      s.ftl = { open: h[bundle.ftl.OPENS] !== undefined };
      return (states[T] = s);
    }
    function rivalCounts(T) {
      if (!rivals.length) return null;
      const out = {};
      for (const k of W.ids) { let n = 0; for (let j = 0; j < rivals.length; j++) { const v = rivalTurn(j, k); if (v !== null && v <= T) n++; } if (n) out[k] = n; }
      return out;
    }
    // a simulator log ends at the race's finish: the prototype, the Drive and the launch are projected as victory.py computes them
    const projection = (() => {
      if (live) return null;
      const v = V.victory(bundle, { cert: trace.cert && trace.cert[0], built: trace.built, m: trace.m, econ });
      return v ? Object.assign({ method: trace.m }, v) : null;
    })();
    function ftlAt(T, engine) {
      const k = T + (engine ? 'e' : 'p');
      if (ftls[k]) return ftls[k];
      return (ftls[k] = V.ftlModel(bundle, state(T), { engine, truth: trace.truth, method: trace.m, instrD: trace.instr_d,
        projection: T === last ? projection : null }));
    }
    const empty = T => ({ turn: T, world: trace.world, econ, have: {}, occurred: [], glimpsed: [], seen: [], lost: [], locked: [], d: 0, inc: 0, share: 0.5 });
    function events(T) {
      if (evs[T]) return evs[T];
      const rec = byTurn[T] || {}, s = state(T), p = T > first ? state(T - 1) : empty(T - 1);
      const Cn = V.classifier(bundle, W, s, false), Cp = V.classifier(bundle, W, p, false);
      const ev = [], name = k => R[k].name;
      for (const k of rec.found || []) {
        const via = haveT[k].via;
        ev.push({ kind: 'discovered', id: k, via, text: via === 'diffusion' ? 'Learned ' + name(k) + ' from abroad.' : via === 'endeavour' ? 'Completed the Grand Endeavour: ' + name(k) + '.' : 'Discovered ' + name(k) + '.' });
      }
      const core = [];
      for (const k of W.ids) {
        if (s.have[k]) continue;
        const a = Cp.classify(k), b = Cn.classify(k);
        if (!b) continue;
        if (!a) {
          if (b.source === 'glimpse') ev.push({ kind: 'revealed', id: k, text: 'Glimpsed: ' + name(k) + '. Its idea has not occurred yet.' });
          else if (b.source === 'abroad') ev.push({ kind: 'revealed', id: k, text: 'Seen in another civilisation’s hands: ' + name(k) + '.' });
          else core.push(k);
        } else if (a.status !== b.status) {
          if (b.status === 'studying') ev.push({ kind: 'rediscovered', id: k, text: a.status === 'closed' ? name(k) + ' came back: its idea occurred again, and it is under study.' : 'The idea of ' + name(k) + ' has occurred: it is under study.' });
          else if (b.status === 'closed') ev.push({ kind: 'passed', id: k, text: 'Its moment passed: ' + name(k) + '.' });
          else if (b.status === 'not_taken') ev.push({ kind: 'not_taken', id: k, text: 'Path not taken: ' + name(k) + '. ' + (W.primaryOf[k] ? name(W.primaryOf[k]) + ' came first.' : '') });
        }
      }
      if (core.length) ev.push({ kind: 'revealed', ids: core, text: 'Now under study: ' + V.listText(core.map(name)) + '.' });
      for (const o of rec.occ || []) {
        const k = Array.isArray(o) ? o[0] : o;
        if (W.tier(k) !== 'CORE' && !Cn.classify(k) && !s.have[k]) ev.push({ kind: 'occurred', id: k, hidden: true, text: 'The idea of ' + name(k) + ' occurred, unseen (' + W.tier(k).toLowerCase() + ').' });
      }
      for (const k of rec.lost || []) if (!Cn.classify(k)) ev.push({ kind: 'passed', id: k, hidden: true, text: name(k) + '’s moment passed, unseen (' + W.tier(k).toLowerCase() + ').' });
      for (const k of rec.locked || []) if (!Cn.classify(k)) ev.push({ kind: 'not_taken', id: k, hidden: true, text: name(k) + ' is locked out, unseen: ' + (W.primaryOf[k] ? name(W.primaryOf[k]) : 'its rival') + ' came first.' });
      for (const k of rec.redisc || []) if (!Cn.classify(k) && !s.have[k]) ev.push({ kind: 'rediscovered', id: k, hidden: true, text: name(k) + ' came back unseen: its idea occurred again.' });
      const fNow = V.enteredFoci(bundle, W, s.have, new Set(s.locked)), fPrev = V.enteredFoci(bundle, W, p.have, new Set(p.locked));
      for (const f of fNow) if (!fPrev.has(f)) ev.push({ kind: 'focus', focus: f, text: 'Entered the ' + V.focusLabel(f) + ' focus.' });
      const eNow = V.eraByCount(W, s.have), ePrev = V.eraByCount(W, p.have);
      if (eNow.index > ePrev.index) ev.push({ kind: 'era', text: 'Entered the ' + eNow.name + ' era.' });
      for (const e of trace.ends || []) {
        if (e[0] !== T) continue;
        if (e[2] === 'start') ev.push({ kind: 'endeavour', id: e[1], text: 'Began a Grand Endeavour on ' + name(e[1]) + '.' });
        else if (e[2] === 'dropped') ev.push({ kind: 'endeavour', id: e[1], text: 'Dropped the Grand Endeavour on ' + name(e[1]) + '.' });
      }
      // the live game's endgame, as the live game announces it
      const end = [];
      for (const run of runs) {
        if (run.from === T) end.push({ type: 'prototype_started', method: run.method });
        if (run.to === T) {
          end.push({ type: 'prototype_result', method: run.method, works: run.works });
          if (run.works && drive && drive.start === T) end.push({ type: 'drive_started', turns: drive.total });
        }
      }
      if (drive && drive.done === T) end.push({ type: 'drive_done', method: drive.method });
      if (actual && actual.turn === T) end.push(Object.assign({ type: 'victory' }, actual));
      const fn = ftlAt(T, false), fp = T > first ? ftlAt(T - 1, false) : null;
      if (fn.open && (!fp || fp.signature !== fn.signature)) {
        ev.push({ kind: 'ftl', text: 'This bears on the question of how to exceed the speed of light.' });
        for (const r of fn.results) if (r.turn === T && !r.endgame) ev.push({ kind: 'ftl-result', text: r.text });
      }
      for (const x of V.normalizeEvents(bundle, end)) ev.push(x);
      if (T === last && !actual) ev.push({ kind: 'finish', text: live
        ? 'The log ends on turn ' + T + (s.prototype ? ', with the ' + s.prototype.method + ' prototype ' + Math.round(100 * s.prototype.progress) + '% built' : s.drive ? ', with the SS FTL Drive under way' : ', before the launch') + '.'
        : 'The log ends: certainty on turn ' + (trace.cert ? trace.cert[0] : '–') + ', the build on turn ' + (trace.built || '–') + '. The prototype and the Drive follow.' });
      return (evs[T] = ev);
    }
    function snapshot(T) { return Object.assign({}, state(T), { events: events(T) }); }
    function nextEvent(T) {
      for (let t = T + 1; t <= last; t++) if (events(t).some(e => NOTABLE.has(e.kind) && !e.hidden)) return t;
      return last;
    }
    function prevEvent(T) {
      for (let t = T - 1; t >= first; t--) if (events(t).some(e => NOTABLE.has(e.kind) && !e.hidden)) return t;
      return first;
    }
    // the strip chart's series: discoveries a turn (own and diffused), the era entered by count, development's era
    const series = [];
    {
      const h = {};
      for (let t = first; t <= last; t++) {
        const rec = byTurn[t] || {};
        let own = 0, dif = 0;
        for (const k of rec.found || []) { h[k] = 1; if (haveT[k].via === 'diffusion') dif++; else own++; }
        series.push({ turn: t, own, dif, era: V.eraByCount(W, h).index, dev: Math.min(Math.floor(rec.d || 0), V.EO.length - 1), fund: rec.fund || null });
      }
    }
    const counts = { own: 0, diffusion: 0, endeavour: 0 };
    for (const k in haveT) counts[haveT[k].via]++;
    const marks = [];
    const F = W.F;
    if (haveT[bundle.ftl.OPENS]) marks.push({ turn: haveT[bundle.ftl.OPENS].turn, label: 'Relativity', short: 'Rel.', kind: 'open' });
    if (haveT[F.CLOSE]) marks.push({ turn: haveT[F.CLOSE].turn, label: 'Unified theory', short: 'Theory', kind: 'close' });
    if (trace.cert) marks.push({ turn: trace.cert[0], label: 'Certain', short: 'Cert.', kind: 'cert' });
    if (trace.built) marks.push({ turn: trace.built, label: 'Build complete', short: 'Built', kind: 'built' });
    for (const e of trace.ends || []) if (e[2] === 'done') marks.push({ turn: e[0], label: 'Endeavour', short: 'End.', kind: 'endeavour' });
    for (const run of runs) {
      if (run.to != null) marks.push({ turn: run.to, label: run.works ? 'Prototype works' : run.method + ' prototype failed', short: run.works ? 'Proto.' : 'Failed', kind: run.works ? 'built' : 'endeavour' });
    }
    if (projection) marks.push({ turn: projection.launch, label: 'Launch', short: 'Launch', kind: 'launch' });
    if (actual) marks.push({ turn: actual.turn, label: 'Launch', short: 'Launch', kind: 'launch' });

    const settingsDiff = [];
    for (const k in st) {
      const a = st[k], b = (bundle.settings || {})[k];
      if (a != null && b != null && String(a) !== String(b)) settingsDiff.push(k + ' ' + a + ' (the bundle has ' + b + ')');
    }
    return {
      trace, bundle, world: W, first, last, turns: last - first + 1, player: PLAYER(trace), econ, econKey: key, rivals: rivals.length, diffusion, live,
      seenRebuilt: rebuildSeen, seenCheck: { arrivals: diffArrivals.length, explained }, counts, marks, series, projection, actual, runs, drive, settingsDiff,
      certTurn: trace.cert ? trace.cert[0] : null, built: trace.built || null, closeTurn: haveT[F.CLOSE] ? haveT[F.CLOSE].turn : null,
      state, snapshot, events, ftlAt, nextEvent, prevEvent, haveAll: haveT,
    };
  }

  // ====================================================================== the page
  function start() {
    const $ = id => document.getElementById(id);
    const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
    let bundle, samples;
    try {
      bundle = JSON.parse($('uh-bundle').textContent);
      samples = JSON.parse($('uh-traces').textContent);
    } catch (e) { $('rp-error').textContent = 'The page’s data could not be read: ' + e.message; $('rp-error').hidden = false; return; }
    const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const S = { game: null, T: 1, playing: false, speed: 4, engine: false, timer: null, lastTick: 0, acc: 0, label: '' };
    let screen = null;
    const ftl = UHFtl.create($('rp-ftl'), { readOnly: true });
    screen = UHScreen.create($('rp-screen'), { readOnly: true, onOpenFtl: () => $('rp-ftl').scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' }) });

    // ---- choosing a log
    const sel = $('rp-sample');
    sel.innerHTML = samples.map((s, i) => '<option value="' + i + '">' + esc(sampleLabel(s.trace)) + '</option>').join('') + '<option value="loaded" hidden>Loaded log</option>';
    sel.addEventListener('change', () => { if (sel.value !== 'loaded') load(samples[+sel.value].trace, sampleLabel(samples[+sel.value].trace)); });
    $('rp-file').addEventListener('change', e => {
      const f = e.target.files && e.target.files[0];
      if (!f) return;
      const rd = new FileReader();
      rd.onload = () => loadText(rd.result, f.name);
      rd.onerror = () => showError('The file could not be read.');
      rd.readAsText(f);
      e.target.value = '';
    });
    const fileLabel = document.querySelector('label[for="rp-file"]');
    if (fileLabel) fileLabel.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); $('rp-file').click(); } });
    $('rp-paste-toggle').addEventListener('click', () => { const p = $('rp-paste'); p.hidden = !p.hidden; $('rp-paste-toggle').setAttribute('aria-expanded', String(!p.hidden)); if (!p.hidden) $('rp-paste-text').focus(); });
    $('rp-paste-load').addEventListener('click', () => loadText($('rp-paste-text').value, 'pasted log'));
    function loadText(text, name) {
      let t;
      try { t = JSON.parse(text); } catch (e) { showError('That is not valid JSON: ' + e.message); return; }
      if (load(t, name)) { sel.value = 'loaded'; sel.querySelector('option[value="loaded"]').textContent = 'Loaded: ' + name; sel.querySelector('option[value="loaded"]').hidden = false; $('rp-paste').hidden = true; }
    }
    function showError(msg) { $('rp-error').textContent = msg; $('rp-error').hidden = !msg; }
    function load(trace, label) {
      let g;
      try { g = reconstruct(bundle, trace); } catch (e) { showError(e.message); return false; }
      showError('');
      pause();
      S.game = g; S.label = label; S.T = g.first;
      screen.select('insight');
      const sl = $('rp-slider');
      sl.min = g.first; sl.max = g.last; sl.value = g.first;
      const lp = document.getElementById('rp-legend-proj');
      if (lp) lp.hidden = !g.projection;
      drawChart();
      show(g.first);
      return true;
    }

    // ---- the transport
    function show(T) {
      const g = S.game;
      if (!g) return;
      T = Math.max(g.first, Math.min(g.last, T | 0));
      S.T = T;
      const snap = g.snapshot(T);
      screen.render(V.researchModel(bundle, snap, { engine: S.engine }));
      ftl.render(g.ftlAt(T, S.engine));
      $('rp-slider').value = T;
      $('rp-turn').textContent = 'Turn ' + T;
      $('rp-of').textContent = 'of ' + g.last;
      $('rp-slider').setAttribute('aria-valuetext', 'Turn ' + T + ' of ' + g.last);
      moveCursor();
      summary();
    }
    function tick(now) {
      if (!S.playing) return;
      if (!S.lastTick) S.lastTick = now;
      S.acc += (now - S.lastTick) * S.speed / 1000;
      S.lastTick = now;
      if (S.acc >= 1) {
        const steps = Math.floor(S.acc);
        S.acc -= steps;
        if (S.T >= S.game.last) { pause(); return; }
        show(S.T + steps);
        if (S.T >= S.game.last) { pause(); return; }
      }
      S.timer = requestAnimationFrame(tick);
    }
    function play() {
      if (!S.game) return;
      if (S.T >= S.game.last) show(S.game.first);
      S.playing = true; S.lastTick = 0; S.acc = 1;
      $('rp-play').setAttribute('aria-pressed', 'true'); $('rp-play').querySelector('.rp-play-label').textContent = 'Pause';
      $('rp-play').querySelector('.rp-ico-play').hidden = true; $('rp-play').querySelector('.rp-ico-pause').hidden = false;
      S.timer = requestAnimationFrame(tick);
    }
    function pause() {
      S.playing = false;
      if (S.timer) cancelAnimationFrame(S.timer);
      S.timer = null;
      $('rp-play').setAttribute('aria-pressed', 'false'); $('rp-play').querySelector('.rp-play-label').textContent = 'Play';
      $('rp-play').querySelector('.rp-ico-play').hidden = false; $('rp-play').querySelector('.rp-ico-pause').hidden = true;
    }
    $('rp-play').addEventListener('click', () => (S.playing ? pause() : play()));
    $('rp-back').addEventListener('click', () => { pause(); show(S.T - 1); });
    $('rp-fwd').addEventListener('click', () => { pause(); show(S.T + 1); });
    $('rp-next').addEventListener('click', () => { pause(); show(S.game.nextEvent(S.T)); });
    $('rp-prev').addEventListener('click', () => { pause(); show(S.game.prevEvent(S.T)); });
    $('rp-start').addEventListener('click', () => { pause(); show(S.game.first); });
    $('rp-end').addEventListener('click', () => { pause(); show(S.game.last); });
    $('rp-slider').addEventListener('input', e => { pause(); show(+e.target.value); });
    $('rp-speed').addEventListener('change', e => { S.speed = +e.target.value; });
    S.speed = +$('rp-speed').value;
    for (const b of document.querySelectorAll('[data-view]')) b.addEventListener('click', () => {
      S.engine = b.dataset.view === 'engine';
      document.querySelectorAll('[data-view]').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
      show(S.T);
    });
    document.addEventListener('keydown', e => {
      if (e.target.closest && e.target.closest('input, textarea, select')) return;
      if (e.key === ' ' && !(e.target.closest && e.target.closest('button'))) { e.preventDefault(); S.playing ? pause() : play(); }
      else if (e.key === 'ArrowRight' && !e.target.closest('.uh-screen, .uh-ftl')) { pause(); show(S.T + 1); }
      else if (e.key === 'ArrowLeft' && !e.target.closest('.uh-screen, .uh-ftl')) { pause(); show(S.T - 1); }
    });

    // ---- the strip chart: discoveries a turn, own and from abroad, over the era entered by count and development's era
    const chart = $('rp-chart'), tip = $('rp-tip');
    let geo = null;
    function drawChart() {
      const g = S.game;
      if (!g) return;
      const w = Math.max(280, chart.clientWidth), padL = 34, padR = 10, bandH = 10;
      const t1 = g.first, t2 = Math.max(g.last, g.projection ? g.projection.launch : g.last);
      const x = t => padL + (t - t1) * (w - padL - padR) / Math.max(1, t2 - t1 + 1);
      const bw = Math.max(1, (w - padL - padR) / (t2 - t1 + 1));
      // milestone labels: each in the first row where it clears the labels already placed
      const rowsEnd = [], placed = [];
      for (const m of g.marks.slice().sort((a, b) => a.turn - b.turn)) {
        const mx = x(m.turn) + bw / 2, text = (w < 640 ? m.short : m.label) + ' ' + m.turn, tw = text.length * 5.9 + 4;
        const right = mx + 3 + tw <= w - padR;
        const x0 = right ? mx + 3 : mx - 3 - tw;
        let r = 0;
        while (rowsEnd[r] !== undefined && rowsEnd[r] > x0 - 6) r++;
        rowsEnd[r] = x0 + tw;
        placed.push({ m, mx, text, r, right });
      }
      const nRows = Math.max(1, rowsEnd.length), top = 4 + nRows * 11, plotH = 52, H = top + plotH + 4 + 2 * bandH + 14;
      const maxN = Math.max(3, ...g.series.map(s => s.own + s.dif));
      const y = n => top + plotH - n * plotH / maxN;
      geo = { x, t1, t2, padL, padR, w };
      let svg = '<svg width="' + w + '" height="' + H + '" viewBox="0 0 ' + w + ' ' + H + '" role="img" aria-label="Discoveries each turn, own and from abroad, with the eras and the race’s milestones">';
      for (let n = 0; n <= maxN; n += maxN > 6 ? 2 : 1) svg += '<line x1="' + padL + '" x2="' + (w - padR) + '" y1="' + y(n) + '" y2="' + y(n) + '" class="ch-grid"/><text x="' + (padL - 6) + '" y="' + (y(n) + 4) + '" class="ch-ax" text-anchor="end">' + n + '</text>';
      // era bands: the era entered by count, then development's era
      const band = (key, yy, label) => {
        let out = '', s0 = g.series[0], from = s0.turn;
        const flush = (to, e) => {
          const tone = ['ch-e0', 'ch-e1'][e % 2];
          out += '<rect x="' + x(from) + '" y="' + yy + '" width="' + Math.max(1, x(to + 1) - x(from)) + '" height="' + (bandH - 1) + '" class="' + tone + '"><title>' + label + ': ' + V.EO[e] + ' era from turn ' + from + '</title></rect>';
          if (x(to + 1) - x(from) > 44) out += '<text x="' + (x(from) + 3) + '" y="' + (yy + bandH - 2) + '" class="ch-band">' + V.ERA_ABBR[V.EO[e]] + '</text>';
        };
        let cur = s0[key];
        for (const s of g.series) { if (s[key] !== cur) { flush(s.turn - 1, cur); from = s.turn; cur = s[key]; } }
        flush(g.last, cur);
        return out;
      };
      const yb = top + plotH + 4;
      svg += '<text x="' + (padL - 6) + '" y="' + (yb + bandH - 2) + '" class="ch-ax" text-anchor="end">era</text>' + band('era', yb, 'Era entered by count');
      svg += '<text x="' + (padL - 6) + '" y="' + (yb + 2 * bandH - 2) + '" class="ch-ax" text-anchor="end">dev.</text>' + band('dev', yb + bandH, 'Development');
      // bars: own (gold) below, from abroad (blue) stacked above, a 1px gap between
      for (const s of g.series) {
        if (s.own) svg += '<rect x="' + x(s.turn) + '" y="' + y(s.own) + '" width="' + Math.max(1, bw - (bw > 3 ? 1 : 0)) + '" height="' + (y(0) - y(s.own)) + '" class="ch-own"/>';
        if (s.dif) svg += '<rect x="' + x(s.turn) + '" y="' + y(s.own + s.dif) + '" width="' + Math.max(1, bw - (bw > 3 ? 1 : 0)) + '" height="' + Math.max(1, y(s.own) - y(s.own + s.dif) - 1) + '" class="ch-dif"/>';
      }
      if (g.last < t2) svg += '<rect x="' + x(g.last + 1) + '" y="' + top + '" width="' + (x(t2 + 1) - x(g.last + 1)) + '" height="' + plotH + '" class="ch-proj"><title>After the log: the prototype and the Drive (projected)</title></rect>';
      // milestones
      for (const p of placed) svg += '<line x1="' + p.mx + '" x2="' + p.mx + '" y1="' + (4 + p.r * 11 + 2) + '" y2="' + (top + plotH) + '" class="ch-mark mk-' + p.m.kind + '"/>';
      for (const p of placed) {
        const tw = p.text.length * 5.9 + 4, x0 = p.right ? p.mx + 1 : p.mx - 1 - tw;
        svg += '<rect x="' + x0 + '" y="' + (3 + p.r * 11) + '" width="' + tw + '" height="11" class="ch-lbg"/>' +
          '<text x="' + (p.right ? p.mx + 3 : p.mx - 3) + '" y="' + (12 + p.r * 11) + '" class="ch-mlabel" text-anchor="' + (p.right ? 'start' : 'end') + '">' + esc(p.text) + '</text>';
      }
      svg += '<line id="rp-cursor" x1="0" x2="0" y1="' + (top - 4) + '" y2="' + (yb + 2 * bandH) + '" class="ch-cursor"/>';
      svg += '<text x="' + padL + '" y="' + (H - 4) + '" class="ch-ax">turn ' + t1 + '</text><text x="' + (w - padR) + '" y="' + (H - 4) + '" class="ch-ax" text-anchor="end">turn ' + t2 + '</text>';
      svg += '</svg>';
      chart.innerHTML = svg;
      moveCursor();
    }
    function moveCursor() {
      const c = document.getElementById('rp-cursor');
      if (!c || !geo) return;
      const bw = Math.max(1, (geo.w - geo.padL - geo.padR) / (geo.t2 - geo.t1 + 1)), xx = geo.x(S.T) + bw / 2;
      c.setAttribute('x1', xx); c.setAttribute('x2', xx);
    }
    const turnAt = ev => {
      const r = chart.getBoundingClientRect(), px = ev.clientX - r.left;
      return Math.round(geo.t1 + (px - geo.padL) * (geo.t2 - geo.t1 + 1) / (geo.w - geo.padL - geo.padR) - 0.5);
    };
    let dragging = false;
    chart.addEventListener('pointerdown', ev => { if (!geo) return; dragging = true; chart.setPointerCapture(ev.pointerId); pause(); show(turnAt(ev)); });
    chart.addEventListener('pointermove', ev => {
      if (!geo || !S.game) return;
      const t = turnAt(ev), s = S.game.series.find(x => x.turn === t);
      if (dragging) show(t);
      if (s) {
        tip.hidden = false;
        tip.textContent = 'Turn ' + t + ': ' + s.own + ' discovered, ' + s.dif + ' from abroad · ' + V.EO[s.era] + ' era';
        const r = chart.getBoundingClientRect();
        tip.style.left = Math.max(0, Math.min(r.width - 220, ev.clientX - r.left + 10)) + 'px';
      } else tip.hidden = true;
    });
    chart.addEventListener('pointerup', () => { dragging = false; });
    chart.addEventListener('pointerleave', () => { tip.hidden = true; });
    // on a desktop the two screens fill the window below the chart, so the whole screen is in the first view
    function fitScreens() {
      const root = document.documentElement;
      if (window.innerWidth <= 760) { root.style.removeProperty('--uh-screen-h'); return; }
      const top = $('rp-screen').getBoundingClientRect().top + window.scrollY;
      root.style.setProperty('--uh-screen-h', Math.round(Math.max(500, Math.min(900, window.innerHeight - top - 10))) + 'px');
    }
    let rt = null;
    window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(() => { drawChart(); fitScreens(); }, 120); });

    // ---- the summary
    function summary() {
      const g = S.game, t = g.trace, P = g.projection, A = g.actual, T = S.T;
      const showMethod = S.engine || (g.certTurn && T >= g.certTurn) || (A && T >= A.turn);
      const worldName = { familiar: 'Familiar (atomic) world', Process: 'Process (elemental) world', Substance: 'Substance (elemental) world' }[t.world] || t.world;
      const econ = g.econ >= 0.95 ? 'good economy' : 'average economy (×' + g.econ + ')';
      const fact = (k, v, note, wide) => '<div class="rp-fact' + (wide ? ' is-wide' : '') + '"><dt>' + esc(k) + '</dt><dd>' + v + (note ? '<span class="rp-note">' + esc(note) + '</span>' : '') + '</dd></div>';
      const vsText = (d, ref) => (d === 0 ? 'level with' : V.turns(Math.abs(d)) + (d < 0 ? ' sooner than' : ' later than')) + ' base Civ V’s ' + ref;
      const vs = P ? vsText(P.vsReference, P.reference) : A ? vsText(A.delta, A.reference) : '';
      // a live game's own endgame: the prototypes it committed, the Drive, the launch
      const worked = g.runs.find(r => r.works), failed = g.runs.filter(r => r.works === false);
      const victoryNote = A ? (worked ? 'prototype committed on turn ' + worked.committed + ', works on turn ' + worked.to + ', ' : '') + (g.drive ? 'SS FTL Drive ' + V.turns(g.drive.total) + ', ' : '') + '1 to launch: ' + vs
        : P ? 'projected as victory.py computes it: prototype ' + V.turns(P.protoTurns) + ', SS FTL Drive ' + V.turns(P.driveTurns) + ', 1 to launch: ' + vs
        : g.live ? 'the log ends on turn ' + g.last + ' before the launch' : 'the race never finished';
      let html = '<h2 class="rp-sum-title">' + esc(worldName) + ' · ' + esc(g.player) + ' player · ' + esc(econ) + '</h2><dl class="rp-facts">' +
        fact('Working method', showMethod ? esc(t.m) : '<span class="rp-dim">hidden until certainty' + (g.certTurn ? ' (turn ' + g.certTurn + ')' : '') + '</span>') +
        fact('Turns logged', g.first + '–' + g.last) +
        fact('Discoveries', String(g.counts.own + g.counts.diffusion + g.counts.endeavour), g.counts.own + ' own · ' + g.counts.diffusion + ' from abroad · ' + g.counts.endeavour + ' by Endeavour') +
        fact('Unified theory', g.closeTurn ? 'turn ' + g.closeTurn : '–') +
        fact('Certainty', g.certTurn ? 'turn ' + g.certTurn : 'not reached') +
        fact('Build complete', g.built ? 'turn ' + g.built : 'not reached') +
        fact('Race finished', g.certTurn && g.built ? 'turn ' + Math.max(g.certTurn, g.built) : 'unfinished') +
        (g.live ? fact('Prototypes', g.runs.length ? esc(g.runs.map(r => r.method + (r.works === true ? ' works' : r.works === false ? ' failed' : ' under way') + (r.to != null ? ' (turn ' + r.to + ')' : '')).join(', ')) : 'none committed',
          failed.length ? failed.length + ' failed: a failed prototype returns nothing' : '') : '') +
        fact('Victory', A ? '<strong>turn ' + A.turn + '</strong>' : P ? '<strong>turn ' + P.launch + '</strong>' : 'none', victoryNote, true) +
        '</dl>';
      const notes = [];
      if (g.seenRebuilt) notes.push((g.seenCheck.explained < g.seenCheck.arrivals ? 'Warning: only ' + g.seenCheck.explained + ' of ' + g.seenCheck.arrivals + ' arrivals from abroad are explained by the rows seen in rivals’ hands, which are rebuilt from the bundle’s rival pool (the log does not record them): the log was probably made with other rivals or diffusion settings, so rows seen abroad may show on the wrong turns.'
        : 'Rows seen in rivals’ hands are rebuilt from the bundle’s rival pool (the log does not record them): ' + g.seenCheck.explained + ' of ' + g.seenCheck.arrivals + ' arrivals from abroad explained.'));
      if (!g.diffusion) notes.push('Played without knowledge diffusion: no rivals.');
      if (g.settingsDiff.length) notes.push('Made under different settings from the bundle: ' + g.settingsDiff.join('; ') + '.');
      if (!t.records[0].prog) notes.push('This log predates the fuller trace: meters, flows and lost ideas are missing.');
      if (notes.length) html += '<p class="rp-notes">' + notes.map(esc).join(' ') + '</p>';
      $('rp-summary').innerHTML = html;
      $('rp-headline').innerHTML = esc(g.player.charAt(0).toUpperCase() + g.player.slice(1)) + ' player · ' + esc(worldName.replace(' world', '')) + ' · ' + esc(econ) +
        (A ? ' · victory <strong>turn ' + A.turn + '</strong> (base Civ V: ' + A.reference + ')' : P ? ' · victory <strong>turn ' + P.launch + '</strong>, projected (base Civ V: ' + P.reference + ')' :
          g.live ? ' · no launch by turn ' + g.last : ' · the race did not finish');
    }

    load(samples[0].trace, sampleLabel(samples[0].trace));
    fitScreens();
  }
  function sampleLabel(t) {
    const p = PLAYER(t);
    return p.charAt(0).toUpperCase() + p.slice(1) + ' · ' + ({ familiar: 'familiar world', Process: 'Process world', Substance: 'Substance world' }[t.world] || t.world) +
      ' · ' + t.records.length + ' turns';
  }

  const API = { reconstruct, start, sampleLabel, NOTABLE };
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
  G.UHReplay = API;
  if (typeof document !== 'undefined' && document.getElementById && document.getElementById('uh-traces')) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
  }
})(typeof window !== 'undefined' ? window : globalThis);
