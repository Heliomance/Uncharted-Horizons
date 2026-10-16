/* view.js: the research screen's and the FTL screen's view models, built from a snapshot (both apps; no DOM).

   researchModel(bundle, snap, opts) -> what screen.js draws: the header, the foci entered, the board's sections, the
   owned history by era, the turn's events, and detailOf(sel) for the bottom bar. It applies the player's visibility
   rules (SPEC.md); opts.engine = true shows everything, hidden things marked as hidden.
   ftlModel(bundle, snap, opts) -> what ftl.js draws: the hypotheses proposed so far, their questions and build needs with
   hints, the results list, the closing statement, and the prototype, Drive and victory slots.
   victory(bundle, game) -> the victory turn as design/simulator/power/victory.py computes it.

   Runs in the browser (window.UHView) and in Node (module.exports). */
(function (G) {
  'use strict';

  const EO = ['Primitive', 'Ancient', 'Classical', 'Medieval', 'Early Modern', 'Modern', 'Atomic', 'Space'];
  const ERA_ABBR = { Primitive: 'Prim.', Ancient: 'Anc.', Classical: 'Class.', Medieval: 'Mediev.', 'Early Modern': 'E. Mod.', Modern: 'Mod.', Atomic: 'Atom.', Space: 'Space' };
  const ERA_NEED = [0, 5, 3, 3, 5, 7, 6, 4];   // section 2: breakthroughs of that era or later that enter it
  const REFERENCE = { '1.0': 305, '0.8': 380 };   // base Civ V's science victory on the same income (base_race.py)
  const STATUS_ORDER = ['endeavour', 'studying', 'waiting', 'unreach', 'closed', 'not_taken'];
  const SECTION = {
    endeavour: { title: 'Grand Endeavour', why: 'takes the funded share until it is complete; it cannot fail' },
    studying: { title: 'Being studied', why: 'revealed, its idea has occurred: each takes a share of its focus’s Insight every turn' },
    waiting: { title: 'Awaiting the idea', why: 'revealed, not yet occurred: no Insight until the idea occurs, and it still may' },
    unreach: { title: 'Not yet reachable', why: 'revealed: a prerequisite must be discovered first' },
    closed: { title: 'Moment passed', why: 'revealed, its moment passed: only an Endeavour is certain' },
    not_taken: { title: 'Path not taken', why: 'a rival line came first: these will never be developed' },
  };
  const STATUS_LABEL = { owned: 'Owned', studying: 'Being studied', waiting: 'Awaiting the idea', unreach: 'Not yet reachable', closed: 'Moment passed', not_taken: 'Path not taken', endeavour: 'Grand Endeavour' };
  const TIER_SHORT = { CORE: 'Core', STANDARD: 'Std', UNCOMMON: 'Unc', RARE: 'Rare', UNIQUE: 'Uniq' };
  const SOURCE_TEXT = { glimpse: 'Glimpsed by our scholars', abroad: 'Seen in another civilisation’s hands', core: '' };
  // the hypotheses' player-facing names: what each would do (section 4 leaves the names to spec work)
  const METHOD_LINE = {
    Warp: 'Carry the ship inside a bubble of bent space', Wormhole: 'Open a shortcut through spacetime',
    Hyperspace: 'Cross through a hidden higher dimension', Tunnelling: 'Tunnel through the light barrier',
    Tachyonic: 'Ride a field that only moves faster than light', Plenum: 'Ride the currents of the medium',
  };

  // ------------------------------------------------------------------ small helpers
  const focusLabel = f => (f || '').replace(/ And /g, ' and ').replace(/ The /g, ' the ');
  function fmt(n) {
    if (n == null || !isFinite(n)) return '–';
    const t = Math.round(n * 10) / 10;
    return Math.abs(t) < 10 && t !== Math.round(t) ? t.toFixed(1) : Math.round(n).toLocaleString('en-GB');
  }
  const turns = n => n + (n === 1 ? ' turn' : ' turns');
  const econKey = e => (Number(e) || 1).toFixed(1);
  const listText = xs => xs.length <= 1 ? (xs[0] || '') : xs.slice(0, -1).join(', ') + ' and ' + xs[xs.length - 1];
  const asSet = x => x instanceof Set ? x : new Set(x || []);

  // ------------------------------------------------------------------ world data, cached per bundle
  const CACHE = new WeakMap();
  function world(bundle, name) {
    let c = CACHE.get(bundle);
    if (!c) CACHE.set(bundle, c = {});
    if (c[name]) return c[name];
    const W = bundle.worlds[name];
    if (!W) throw new Error('Unknown world: ' + name);
    const R = bundle.rows, ids = W.ids, idset = new Set(ids), eraI = {}, cost = {}, tierOv = W.tiers || {};
    for (const k of ids) { eraI[k] = EO.indexOf(R[k].era); cost[k] = bundle.model.price[R[k].era] * ((W.costmult || {})[k] || 1); }
    const altsOf = {};
    for (const a in (W.compete || {})) (altsOf[W.compete[a]] = altsOf[W.compete[a]] || []).push(a);
    const F = bundle.ftl[W.ontology];
    const buildRows = {};
    for (const o in F.BUILD) buildRows[o] = new Set([].concat(...F.BUILD[o]));
    return c[name] = { name, ontology: W.ontology, ids, idset, eraI, cost, primaryOf: W.compete || {}, altsOf, F, buildRows, pool: W.pool || [],
      tier: k => tierOv[k] || R[k].tier };
  }
  function prereqsMet(row, have) {
    const pre = row.pre;
    for (let i = 0; i < pre.length; i++) {
      let ok = false;
      for (const opt of pre[i]) { if (opt.every(p => have[p] !== undefined)) { ok = true; break; } }
      if (!ok) return false;
    }
    return true;
  }
  function eraByCount(W, have) {
    const cnt = new Array(EO.length).fill(0);
    for (const k in have) if (W.eraI[k] !== undefined) cnt[W.eraI[k]]++;
    const at = new Array(EO.length + 1).fill(0);
    for (let i = EO.length - 1; i >= 0; i--) at[i] = at[i + 1] + cnt[i];
    let i = 0;
    while (i < EO.length - 1 && at[i + 1] >= ERA_NEED[i + 1]) i++;
    return { index: i, name: EO[i], next: i < EO.length - 1 ? { name: EO[i + 1], need: ERA_NEED[i + 1], have: at[i + 1] } : null };
  }
  function enteredFoci(bundle, W, have, locked) {
    const out = new Set();
    for (const k of W.ids) {
      const f = bundle.rows[k].focus;
      if (out.has(f)) continue;
      if (have[k] !== undefined || (!locked.has(k) && prereqsMet(bundle.rows[k], have))) out.add(f);
    }
    return out;
  }

  // the player's knowledge of one row: null if unseen, else {status, hidden, source}
  function classifier(bundle, W, snap, engine) {
    const R = bundle.rows, have = snap.have || {}, occ = asSet(snap.occurred), gl = asSet(snap.glimpsed), seen = asSet(snap.seen),
      lost = asSet(snap.lost), locked = asSet(snap.locked);
    const en = snap.endeavour && have[snap.endeavour.id] === undefined ? snap.endeavour : null;
    const metC = {};
    const met = k => (metC[k] !== undefined ? metC[k] : (metC[k] = prereqsMet(R[k], have)));
    function classify(k) {
      if (have[k] !== undefined) return { status: 'owned' };
      if (en && en.id === k) return { status: 'endeavour', source: gl.has(k) ? 'glimpse' : seen.has(k) ? 'abroad' : 'core' };
      const core = W.tier(k) === 'CORE', m = met(k);
      const revealed = (core && (occ.has(k) || (m && !locked.has(k)))) || gl.has(k) || seen.has(k);
      if (revealed) {
        const source = gl.has(k) ? 'glimpse' : seen.has(k) ? 'abroad' : 'core';
        if (locked.has(k)) return { status: 'not_taken', source };
        if (!m) return { status: 'unreach', source };
        if (occ.has(k) || core) return { status: 'studying', source };
        if (lost.has(k)) return { status: 'closed', source };
        return { status: 'waiting', source };
      }
      if (!engine) return null;
      if (locked.has(k)) return { status: 'not_taken', hidden: true };
      if (!m) return null;
      if (occ.has(k)) return { status: 'studying', hidden: true };
      if (lost.has(k)) return { status: 'closed', hidden: true };
      return { status: 'waiting', hidden: true };
    }
    return { classify, met, have, occ, gl, seen, lost, locked, en };
  }

  // the breakthroughs a row needs, as AND-groups of OR-options, named, each part marked met or not
  function needsOf(bundle, W, k, have) {
    const R = bundle.rows, out = [];
    for (const grp of R[k].pre) {
      const opts = grp.filter(opt => opt.every(p => W.idset.has(p)));
      if (!opts.length) continue;
      const done = opts.find(opt => opt.every(p => have[p] !== undefined));
      const show = done ? [done] : opts;
      out.push({ met: !!done, options: show.map(opt => opt.map(p => ({ name: R[p].name, met: have[p] !== undefined }))) });
    }
    return out;
  }

  // ------------------------------------------------------------------ events: the replay's {kind, text}, or the engine's {type, ...}
  const FTL_TEXT = 'This bears on the question of how to exceed the speed of light.';
  function normalizeEvents(bundle, list) {
    const out = [], R = bundle.rows, nm = k => (R[k] ? R[k].name : 'a breakthrough');
    for (const e of list || []) {
      if (e.kind && e.text) { out.push(e); continue; }
      const t = e.type, id = e.id;
      if (t === 'discovered') out.push({ kind: 'discovered', id, via: e.via, text: e.via === 'diffusion' ? 'Learned ' + nm(id) + ' from abroad.' : e.via === 'endeavour' ? 'Completed the Grand Endeavour: ' + nm(id) + '.' : 'Discovered ' + nm(id) + '.' });
      else if (t === 'revealed') out.push({ kind: 'revealed', id, text: e.how === 'glimpse' ? 'Glimpsed: ' + nm(id) + '. Its idea has not occurred yet.' : e.how === 'rivals' || e.how === 'abroad' || e.how === 'seen' ? 'Seen in another civilisation’s hands: ' + nm(id) + '.' : 'Now under study: ' + nm(id) + '.' });
      else if (t === 'moment_passed') out.push({ kind: 'passed', id, hidden: !!e.hidden, text: e.hidden ? nm(id) + '’s moment passed, unseen.' : 'Its moment passed: ' + nm(id) + '.' });
      else if (t === 'path_not_taken') out.push({ kind: 'not_taken', id, hidden: !!e.hidden, text: (e.hidden ? nm(id) + ' is locked out, unseen: ' : 'Path not taken: ' + nm(id) + '. ') + (e.primary ? nm(e.primary) + ' came first.' : '') });
      else if (t === 'rediscovered') out.push({ kind: 'rediscovered', id, hidden: !!e.hidden, text: nm(id) + (e.hidden ? ' came back unseen: its idea occurred again.' : ' came back: its idea occurred again, and it is under study.') });
      else if (t === 'occurred') out.push({ kind: 'occurred', id, hidden: true, text: 'The idea of ' + nm(id) + ' occurred, unseen.' });
      else if (t === 'focus_entered') out.push({ kind: 'focus', focus: e.focus, text: 'Entered the ' + focusLabel(e.focus) + ' focus.' });
      else if (t === 'era_entered') out.push({ kind: 'era', text: 'Entered the ' + e.era + ' era.' });
      else if (t === 'ftl') {
        out.push({ kind: 'ftl', text: e.text || FTL_TEXT });
        for (const c of e.changes || []) {
          const txt = { proposed: 'Proposed: ' + c.method + '.', list_closed: 'The unified theory closes the list of hypotheses.', ruled_out: c.method + ' is ruled out.',
            last_standing: c.method + ' is the only hypothesis left.', result: c.question ? (c.holds ? 'Confirmed: ' : 'Disproved: ') + lowerFirst(c.question) + '.' : null,
            build: c.complete ? 'Every build need of ' + c.method + ' is met: its prototype can be committed.' : null,
            awaiting: c.instrument ? 'To settle an open question, we’ll need to build a ' + c.instrument + '.' : null }[c.kind];
          if (txt) out.push({ kind: 'ftl-result', text: txt });
        }
      }
      else if (t === 'instrument_complete') out.push({ kind: 'ftl-result', text: 'The ' + (e.instrument || 'instrument') + ' is complete.' });
      else if (t === 'endeavour_started') out.push({ kind: 'endeavour', id, text: 'Began a Grand Endeavour on ' + nm(id) + '.' });
      else if (t === 'endeavour_ended') out.push({ kind: 'endeavour', id, text: 'The Grand Endeavour on ' + nm(id) + ' ended' + (e.reason === 'studied' ? ': study found it first.' : '.') });
      else if (t === 'prototype_started') out.push({ kind: 'endeavour', text: 'Committed to a ' + e.method + ' prototype.' });
      else if (t === 'prototype_result') out.push({ kind: 'endeavour', text: e.works ? 'The ' + e.method + ' prototype works.' : 'The ' + e.method + ' prototype failed: ' + e.method + ' is proven invalid.' });
      else if (t === 'drive_started') out.push({ kind: 'endeavour', text: 'Building the SS FTL Drive: ' + turns(e.turns) + ' from Production.' });
      else if (t === 'drive_done') out.push({ kind: 'endeavour', text: 'The SS FTL Drive is built: the ship launches next turn.' });
      else if (t === 'victory') out.push({ kind: 'finish', text: 'Victory: the ship launches on turn ' + e.turn + (e.reference ? ', ' + (e.delta === 0 ? 'level with' : turns(Math.abs(e.delta)) + (e.delta < 0 ? ' sooner than' : ' later than')) + ' base Civ V’s ' + e.reference : '') + '.' });
      else if (t) out.push({ kind: t, id, hidden: !!e.hidden, text: e.text || t.replace(/_/g, ' ') });
    }
    return out;
  }
  const lowerFirst = s => s.charAt(0).toLowerCase() + s.slice(1);
  // the engine view's hidden information: the replay's snap.engine, or the engine's snap.hidden
  function hiddenInfo(snap) {
    if (snap.engine) return snap.engine;
    const h = snap.hidden;
    if (!h) return {};
    return { method: h.method, truth: h.truth, rivals: h.rivalsHold || null, nRivals: h.nRivals || (h.rivalsHold ? 5 : 0) };
  }

  // ------------------------------------------------------------------ the research screen
  function researchModel(bundle, snap, opts) {
    opts = opts || {};
    const engine = !!opts.engine, R = bundle.rows, W = world(bundle, snap.world), T = snap.turn;
    const C = classifier(bundle, W, snap, engine), have = C.have, prog = snap.prog || {};
    const era = eraByCount(W, have);
    const allEvents = normalizeEvents(bundle, snap.events);
    const events = allEvents.filter(e => engine || !e.hidden);
    const newIds = new Set();
    for (const e of allEvents) {
      if ((e.kind === 'revealed' || e.kind === 'discovered') && (engine || !e.hidden)) for (const x of [].concat(e.id || [], e.ids || [])) newIds.add(x);
    }
    const newFoci = new Set(allEvents.filter(e => e.kind === 'focus').map(e => e.focus));
    const info = hiddenInfo(snap);

    // every row the player (or, in the engine view, Tamsin) can see
    const rows = {}, list = [];
    for (const k of W.ids) {
      const c = C.classify(k);
      if (!c) continue;
      const r = R[k], e = W.eraI[k], tier = W.tier(k);
      const chip = { id: k, name: r.name, focus: r.focus, focusLabel: focusLabel(r.focus), era: r.era, eraAbbr: ERA_ABBR[r.era], eraI: e,
        eraTone: e < era.index ? 'past' : e === era.index ? 'current' : 'later', status: c.status, hidden: !!c.hidden, source: c.source || null,
        tier, tags: [], isNew: newIds.has(k), meter: null, turn: null, via: null };
      if (c.status === 'owned') { chip.turn = have[k].turn; chip.via = have[k].via || 'own'; if (chip.turn === T) chip.isNew = true; }
      if (chip.isNew) chip.tags.push({ text: 'New', kind: 'new' });
      if (c.status === 'owned') {
        if (tier === 'RARE') chip.tags.push({ text: 'Rare', kind: 'rare' });
        if (tier === 'UNIQUE') chip.tags.push({ text: '★ Unique', kind: 'unique' });
        if (chip.via === 'diffusion') chip.tags.push({ text: 'Abroad', kind: 'abroad' });
        if (chip.via === 'endeavour') chip.tags.push({ text: 'Endeavour', kind: 'endeavour' });
      }
      if (c.status === 'endeavour' && snap.endeavour) chip.tags.push({ text: 'Endeavour ' + Math.round(100 * (snap.endeavour.progress || 0)) + '%', kind: 'endeavour' });
      if (engine) {
        if (c.hidden) chip.tags.push({ text: 'Hidden', kind: 'hidden' });
        if (c.status !== 'owned') chip.tags.push({ text: TIER_SHORT[tier] || tier, kind: 'tier' });
        if (prog[k] !== undefined) { chip.meter = prog[k]; chip.tags.push({ text: Math.round(100 * prog[k]) + '%', kind: 'meter' }); }
      }
      rows[k] = chip; list.push(chip);
    }
    // Competing Solutions: a revealed pair, neither yet developed, carries a Rival tag on both chips
    for (const a in W.primaryOf) {
      const p = W.primaryOf[a], ra = rows[a], rp = rows[p];
      if (ra && rp && !ra.hidden && !rp.hidden && ra.status !== 'owned' && ra.status !== 'not_taken' && rp.status !== 'owned') {
        ra.tags.push({ text: 'Rival', kind: 'rival' }); rp.tags.push({ text: 'Rival', kind: 'rival' });
        ra.rival = rp.name; rp.rival = ra.name; ra.rivalRole = 'alt'; rp.rivalRole = 'primary';
      }
    }

    const byEraName = (a, b) => a.eraI - b.eraI || a.name.localeCompare(b.name);
    const counts = { studying: 0, waiting: 0, unreach: 0, closed: 0, not_taken: 0, owned: 0, endeavour: 0 };
    const hiddenCounts = {};
    for (const c of list) { if (!c.hidden) counts[c.status]++; else hiddenCounts[c.status] = (hiddenCounts[c.status] || 0) + 1; }
    const sections = STATUS_ORDER.map(st => {
      const rs = list.filter(c => c.status === st);
      if (!rs.length) return null;
      const by = {};
      rs.forEach(c => (by[c.focus] = by[c.focus] || []).push(c));
      const groups = Object.keys(by).sort((a, b) => focusLabel(a).localeCompare(focusLabel(b))).map(f => ({
        focus: f, label: focusLabel(f), funded: snap.funded === f && !snap.endeavour, rows: by[f].sort(byEraName) }));
      return { key: st, title: SECTION[st].title, why: SECTION[st].why, count: rs.length - (hiddenCounts[st] || 0), hiddenCount: hiddenCounts[st] || 0, groups };
    }).filter(Boolean);
    const owned = list.filter(c => c.status === 'owned');
    const bands = [];
    for (let i = EO.length - 1; i >= 0; i--) {
      const rs = owned.filter(c => c.eraI === i);
      if (!rs.length) continue;
      rs.sort((a, b) => b.turn - a.turn || a.name.localeCompare(b.name));
      bands.push({ era: EO[i], label: EO[i] + ' era', tone: i < era.index ? 'past' : i === era.index ? 'current' : 'later', count: rs.length, rows: rs });
    }

    // the foci entered: a focus is entered when any of its rows is discoverable or owned
    const entered = enteredFoci(bundle, W, have, C.locked);
    const enFocus = C.en ? R[C.en.id].focus : null;
    const foci = [...entered].sort((a, b) => focusLabel(a).localeCompare(focusLabel(b))).map(f => {
      const mine = list.filter(c => c.focus === f && c.status === 'studying');
      return { name: f, label: focusLabel(f), funded: snap.funded === f && !snap.endeavour && !snap.prototype, badge: mine.filter(c => !c.hidden).length,
        hiddenBadge: engine ? mine.filter(c => c.hidden).length : 0, flow: engine && snap.flow ? (snap.flow[f] || 0) : null,
        isNew: newFoci.has(f), holdsEndeavour: enFocus === f };
    });

    // the header: what is funded, the split and the spread
    const inc = snap.inc || 0, share = snap.share == null ? (have.SO05 ? 0.8 : 0.5) : snap.share;
    const splitPct = have.SO05 !== undefined ? 80 : 50;
    let funded;
    if (snap.prototype) funded = { kind: 'prototype', method: snap.prototype.method, name: snap.prototype.method + ' prototype', progress: snap.prototype.progress || 0 };
    else if (snap.endeavour) funded = { kind: 'endeavour', id: snap.endeavour.id, name: R[snap.endeavour.id].name, progress: snap.endeavour.progress || 0, done: have[snap.endeavour.id] !== undefined };
    else if (snap.funded) funded = { kind: 'focus', focus: snap.funded, label: focusLabel(snap.funded) };
    else funded = { kind: 'none' };
    const d = snap.d || 0, devEra = EO[Math.min(Math.floor(d), EO.length - 1)];
    const header = {
      turn: T, era: { name: era.name, index: era.index, next: era.next,
        text: era.name + ' era' + (era.next ? ' · ' + era.next.have + ' of ' + era.next.need + ' toward ' + era.next.name : ''),
        short: era.name + (era.next ? ' · ' + era.next.have + '/' + era.next.need : '') },
      development: { d, era: devEra, text: 'Development ' + d.toFixed(2) + ' · ' + devEra },
      insight: inc, share, sharePct: Math.round(share * 100), splitPct, fundedInsight: inc * share, spreadInsight: inc * (1 - share), funded,
    };

    const ftlOpen = have[bundle.ftl.OPENS] !== undefined;
    const vm = {
      turn: T, world: snap.world, engine, header, foci, sections, owned: { count: owned.length, bands }, counts, hiddenCounts, rows, events, ftlOpen,
      prototype: snap.prototype || null, drive: snap.drive || null, victory: snap.victory || null,
      engineInfo: engine ? { method: info.method || null, truth: info.truth || null, hiddenStudying: hiddenCounts.studying || 0, nRivals: info.nRivals || 0,
        rivalsAhead: info.rivals ? W.ids.filter(k => info.rivals[k] && have[k] === undefined).length : null } : null,
      detailOf: sel => detail(bundle, W, snap, vm, C, sel, opts),
    };
    return vm;
  }

  // the bottom bar: Close | description | actions, for a selected row, focus, the funding header or the era
  function detail(bundle, W, snap, vm, C, sel, opts) {
    if (!sel) return null;
    const R = bundle.rows, have = C.have, engine = vm.engine, H = vm.header, out = { title: '', meta: '', status: null, lines: [], needs: null, quote: null, actions: [], engine: [] };
    const line = (text, tone) => out.lines.push({ text, tone: tone || '' });
    const shareText = fmt(H.insight * (H.splitPct / 100));
    if (sel.startsWith('row:')) {
      const k = sel.slice(4), c = vm.rows[k];
      if (!c) return null;
      const r = R[k], fundedHere = H.funded.kind === 'focus' && H.funded.focus === r.focus;
      out.title = r.name; out.status = c.status; out.hidden = c.hidden;
      out.meta = focusLabel(r.focus) + ' · ' + r.era + ' era' + (c.status === 'owned' && (c.tier === 'RARE' || c.tier === 'UNIQUE') ? ' · ' + (c.tier === 'RARE' ? 'Rare' : 'Unique') : '');
      const src = c.source && SOURCE_TEXT[c.source] ? SOURCE_TEXT[c.source] + '. ' : '';
      const q = opts.quote ? opts.quote(k) : undefined;
      const endeavourAction = (label) => {
        if (q === undefined) out.actions.push({ act: 'endeavour', arg: k, label, sub: 'not in this replay', enabled: false });
        else if (!q || q.cost == null || q.eligible === false) out.actions.push({ act: 'endeavour', arg: k, label, sub: (q && q.reason) || 'not available now', enabled: false });
        else out.actions.push({ act: 'endeavour', arg: k, label, sub: fmt(q.cost) + ' Insight · about ' + turns(q.turns), enabled: true });
      };
      if (c.hidden) line('Hidden from the player: ' + ({ studying: 'its idea has occurred, unseen', waiting: 'eligible, its idea has not occurred', closed: 'its moment passed unseen', not_taken: 'locked out unseen' }[c.status] || 'unseen') + '.', 'hidden');
      if (c.status === 'owned') {
        const via = { diffusion: ' Learned from abroad (diffusion).', endeavour: ' Completed as a Grand Endeavour.', own: '' }[c.via] || '';
        line('Discovered on turn ' + c.turn + '.' + via);
        if (r.fx) line(r.fx);
        if (c.tier === 'UNIQUE') line('Unique to your civilisation: it cannot be traded or stolen, and never diffuses.');
        if (c.tier === 'RARE') line('A rare find.');
        if (r.flav) out.quote = r.flav;
        out.actions.push({ act: null, label: 'Discovered', enabled: false });
      } else if (c.status === 'studying') {
        line(fundedHere ? 'Being studied in ' + focusLabel(r.focus) + ', which you fund: it takes Insight every turn.'
          : 'Being studied in ' + focusLabel(r.focus) + ': it takes a share of that focus’s Insight every turn.');
        if (c.rival) line(c.rivalRole === 'alt' ? 'Rival of ' + c.rival + ': if that comes first, this is never developed.' : 'Rival of ' + c.rival + ': if this comes first, ' + c.rival + ' is never developed.');
        if (r.conj) out.quote = r.conj;
        out.actions.push(fundedHere ? { act: null, label: 'Funded', enabled: false } : { act: 'fund', arg: r.focus, label: 'Fund ' + focusLabel(r.focus), enabled: true });
        endeavourAction('Grand Endeavour');
      } else if (c.status === 'waiting') {
        line(src + 'Awaiting the idea: no Insight until the idea occurs.');
        if (c.rival) line('Rival of ' + c.rival + '.');
        if (r.conj) out.quote = r.conj;
        endeavourAction('Begin Grand Endeavour');
      } else if (c.status === 'unreach') {
        line(src + 'Not yet reachable: a prerequisite must be discovered first.');
        out.actions.push({ act: null, label: 'Not yet reachable', enabled: false });
      } else if (c.status === 'closed') {
        line(src + 'Its moment passed — only an Endeavour is certain.');
        if (r.conj) out.quote = r.conj;
        endeavourAction('Begin Grand Endeavour');
      } else if (c.status === 'not_taken') {
        const p = W.primaryOf[k];
        line(src + 'Path not taken: ' + (p ? R[p].name : 'a rival line') + ' came first, so this will never be developed.');
        out.actions.push({ act: null, label: 'Never developed', enabled: false });
      } else if (c.status === 'endeavour') {
        const e = snap.endeavour, pct = Math.round(100 * (e.progress || 0));
        line(pct + '% done' + (e.cost ? ' — ' + fmt(e.cost * (e.progress || 0)) + ' of ' + fmt(e.cost) + ' Insight' : '') + '. It cannot fail.');
        line('It takes the funded share, ' + H.splitPct + '%; the ' + (100 - H.splitPct) + '% spread still reaches your other foci.');
        out.actions.push({ act: null, label: 'Endeavour under way', sub: pct + '% done', enabled: false });
        out.actions.push({ act: 'stop', label: 'Stop the Endeavour', enabled: !!opts.quote });
      }
      if (c.status !== 'owned') out.needs = needsOf(bundle, W, k, have);
      if (engine) {
        out.engine.push('Row ' + k + ' · ' + c.tier + (C.occ.has(k) ? ' · occurred' : '') + (C.lost.has(k) ? ' · lost' : '') + (C.gl.has(k) ? ' · glimpsed' : '') + (C.seen.has(k) ? ' · seen abroad' : ''));
        if (c.meter != null) out.engine.push('Hidden meter ' + Math.round(100 * c.meter) + '% full');
        const hi = hiddenInfo(snap), riv = hi.rivals;
        if (riv) out.engine.push('Rivals holding it: ' + (riv[k] || 0) + ' of ' + (hi.nRivals || 5));
      }
    } else if (sel.startsWith('focus:')) {
      const f = sel.slice(6), fv = vm.foci.find(x => x.name === f);
      out.title = focusLabel(f); out.status = 'focus';
      out.meta = fv && fv.funded ? 'funded · ' + H.splitPct + '% of your Insight' : 'not funded';
      const here = Object.values(vm.rows).filter(c => c.focus === f && c.status === 'studying' && !c.hidden).map(c => c.name);
      line(here.length ? 'Under study here: ' + listText(here) + '.' : 'Nothing revealed is under study here.');
      if (fv && !fv.funded) line('Switching loses nothing: every breakthrough keeps its progress.', 'muted');
      out.actions.push(fv && fv.funded ? { act: null, label: 'Funded', enabled: false } : { act: 'fund', arg: f, label: 'Fund ' + focusLabel(f), enabled: true });
      if (engine) {
        const hid = Object.values(vm.rows).filter(c => c.focus === f && c.status === 'studying' && c.hidden).map(c => c.name + (c.meter != null ? ' ' + Math.round(100 * c.meter) + '%' : ''));
        out.engine.push('Insight here this turn: ' + fmt(fv ? fv.flow : 0));
        if (hid.length) out.engine.push('Hidden under study: ' + hid.join(', '));
      }
    } else if (sel === 'insight') {
      out.title = 'Insight'; out.status = 'insight'; out.meta = fmt(H.insight) + ' a turn, equal to your science';
      const f = H.funded;
      if (f.kind === 'none') line('Nothing is funded: the whole of your Insight spreads to the foci with work under study.');
      else line(H.splitPct + '% (' + shareText + ') goes to ' + (f.kind === 'focus' ? f.label : f.kind === 'endeavour' ? 'the Grand Endeavour on ' + f.name : 'the ' + f.name) + (H.splitPct === 80 ? ', since Specialization of Labor; before it, 50%.' : '.'));
      line('The other ' + (100 - H.splitPct) + '% (' + fmt(H.insight * (1 - H.splitPct / 100)) + ') spreads to foci with work under study.');
      if (H.splitPct === 50) line('Your people cannot yet direct their inquiry more sharply than that.', 'muted');
    } else if (sel === 'era') {
      const E = H.era;
      out.title = E.name + ' era'; out.status = 'era'; out.meta = 'entered by count';
      line('You enter an era when you hold enough breakthroughs from it or later.');
      if (E.next) line('The ' + E.next.name + ' era needs ' + E.next.need + ' from the ' + E.next.name + ' era or later: you hold ' + E.next.have + '.');
      if (engine) out.engine.push(H.development.text);
    } else return null;
    return out;
  }

  // ------------------------------------------------------------------ FTL: smart_targets, hints, knowledge (w7f.py)
  function smartTargets(bundle, W, reqs, have, S) {
    const R = bundle.rows, memo = new Map(), cost = W.cost, EMPTY = new Set();
    const sum = s => { let x = 0; for (const k of s) x += cost[k]; return x; };
    function need(k) {
      if (memo.has(k)) return memo.get(k);
      if (have[k] !== undefined) return EMPTY;
      if (!W.idset.has(k)) return null;
      if (S.lost.has(k) && !S.gl.has(k) && !S.seen.has(k)) return null;   // an idea that isn't coming
      if (S.locked.has(k) && k !== S.endK) return null;                    // locked out by its primary
      memo.set(k, new Set([k]));
      const req = new Set([k]);
      for (const grp of R[k].pre) {
        let best = null;
        for (const opt of grp) {
          const s = new Set(); let ok = true;
          for (const p of opt) { const q = need(p); if (q === null) { ok = false; break; } for (const x of q) s.add(x); }
          if (!ok) continue;
          if (!s.size) { best = [0, s]; break; }
          const c = sum(s);
          if (best === null || c < best[0]) best = [c, s];
        }
        if (best === null) { memo.set(k, null); return null; }
        for (const x of best[1]) req.add(x);
      }
      memo.set(k, req);
      return req;
    }
    const out = new Set();
    for (const alts of reqs) {
      const opts = alts.map(need).filter(q => q !== null);
      if (!opts.length || opts.some(q => q.size === 0)) continue;
      let best = opts[0], bc = sum(opts[0]);
      for (let i = 1; i < opts.length; i++) { const c = sum(opts[i]); if (c < bc) { best = opts[i]; bc = c; } }
      for (const x of best) out.add(x);
    }
    return out;
  }
  function hintRow(bundle, W, alts, have, S) {
    const fr = [...smartTargets(bundle, W, [alts], have, S)].filter(k => prereqsMet(bundle.rows[k], have)).sort();
    let best = null;
    for (const k of fr) if (best === null || W.cost[k] < W.cost[best]) best = k;
    return best;
  }
  function knowledge(bundle, W, have, truth, T, instrD) {
    const F = W.F, INSTR = bundle.ftl.INSTR, known = {}, pending = {};
    for (const c in F.HOST) {
      const hosts = F.HOST[c], ht = hosts.filter(h => have[h] !== undefined).map(h => have[h].turn);
      if (!ht.length) continue;
      let rt = Math.min(...ht), instrTurn = null;
      if (instrD != null && INSTR[c]) {
        const unl = INSTR[c].filter(u => have[u] !== undefined).map(u => have[u].turn);
        if (unl.length) { instrTurn = Math.min(...unl) + instrD; rt = Math.max(rt, instrTurn); }
      }
      const ms08 = hosts.length === 1 && hosts[0] === 'MS08' && truth && !truth.exotic;
      if (truth && rt <= T && !ms08) known[c] = { value: !!truth[c], turn: rt, instrTurn };
      else pending[c] = { turn: rt, instrTurn, ms08: !!ms08 };
    }
    return { known, pending };
  }

  // ------------------------------------------------------------------ the FTL screen
  function ftlModel(bundle, snap, opts) {
    opts = opts || {};
    const engine = !!opts.engine, R = bundle.rows, W = world(bundle, snap.world), F = W.F, FT = bundle.ftl, T = snap.turn;
    const C = classifier(bundle, W, snap, false), have = C.have;
    const hi = hiddenInfo(snap);
    const truth = opts.truth || hi.truth || null;
    const trueMethod = opts.method || hi.method || null;
    const instrD = opts.instrD != null ? opts.instrD : FT.INSTR_D[econKey(snap.econ)];
    const open = have[FT.OPENS] !== undefined;
    const vm = { open, turn: T, engine, closed: have[F.CLOSE] !== undefined, closeName: R[F.CLOSE].name, opensName: R[FT.OPENS].name,
      statement: '', hypotheses: [], results: [], certain: null, prototype: snap.prototype || null, drive: snap.drive || null, victory: snap.victory || null,
      engineInfo: null, signature: '', projection: opts.projection || null };
    if (!open && !engine) { vm.statement = 'Nothing is proposed yet: before the light barrier is established, going faster than light is no special achievement.'; return vm; }
    const S = { lost: C.lost, gl: C.gl, seen: C.seen, locked: C.locked, endK: snap.endeavour ? snap.endeavour.id : null };
    const visible = k => engine || have[k] !== undefined || !!C.classify(k);
    const { known, pending } = knowledge(bundle, W, have, truth, T, instrD);
    const protoResults = snap.prototypeResults || (snap.ftl && snap.ftl.prototypeResults) || [];
    const failed = new Set(snap.failedPrototypes || opts.failed || protoResults.filter(r => !r.works).map(r => r.method));
    const methods = Object.keys(F.COND);
    // proposed by its theory row once Relativity has opened the question, or at the latest by the unified theory, which
    // closes the list (section 4: the candidates are these five)
    const proposedTurn = o => {
      if (!open) return null;
      const ts = [F.PROPOSER[o], F.CLOSE].filter(k => have[k] !== undefined).map(k => have[k].turn);
      return ts.length ? Math.max(Math.min(...ts), have[FT.OPENS].turn) : null;
    };
    const alive = methods.filter(o => !F.COND[o].some(c => known[c] && !known[c].value) && !failed.has(o));
    const allTrue = o => F.COND[o].every(c => known[c] && known[c].value);
    const closed = vm.closed;
    const certainM = closed ? (methods.find(allTrue) || (alive.length === 1 ? alive[0] : null)) : null;
    const hintCache = {};
    const hint = alts => {
      const key = alts.join(',');
      if (!(key in hintCache)) { const k = hintRow(bundle, W, alts, have, S); hintCache[key] = k ? { focus: R[k].focus, label: focusLabel(R[k].focus) } : null; }
      return hintCache[key];
    };
    const sig = [];
    for (const o of methods) {
      const pt = proposedTurn(o);
      if (pt === null && !engine) continue;
      const fails = F.COND[o].filter(c => known[c] && !known[c].value);
      const failedAt = failed.has(o) ? (protoResults.find(r => r.method === o && !r.works) || {}).turn : null;
      const ruledTurn = fails.length ? Math.max(Math.min(...fails.map(c => known[c].turn)), pt || 0) : failedAt != null ? failedAt : null;
      const standing = failed.has(o) || fails.length ? 'ruled_out' : allTrue(o) ? 'confirmed' : (closed && alive.length === 1 && alive[0] === o) ? 'only' : 'standing';
      const live = standing !== 'ruled_out' && pt !== null;
      const questions = F.COND[o].map(c => {
        const hosts = F.HOST[c].filter(h => W.idset.has(h));
        const merged = hosts.some(h => W.buildRows[o].has(h));
        const q = { cond: c, text: F.QUESTION[c], merged, state: 'open', turn: null, instrument: null, turnsLeft: null, hint: null,
          hosts: hosts.map(h => visible(h) ? { name: R[h].name, owned: have[h] !== undefined } : null).filter(Boolean),
          truth: engine && truth ? !!truth[c] : null };
        if (known[c]) { q.state = known[c].value ? 'holds' : 'fails'; q.turn = known[c].turn; if (known[c].instrTurn) q.instrument = FT.INSTRUMENT[c]; }
        else if (pending[c]) {
          if (pending[c].ms08) q.state = 'silent';
          else { q.state = 'awaiting'; q.instrument = FT.INSTRUMENT[c] || null; q.turnsLeft = pending[c].turn - T; }
        } else if (live) q.hint = hint(F.HOST[c]);
        return q;
      });
      let buildMet = 0, buildTurn = 0;
      const build = F.BUILD[o].map(g => {
        const opts_ = g.filter(k => W.idset.has(k));
        const met = opts_.filter(k => have[k] !== undefined);
        const power = opts_.length >= 3;
        const b = { power, label: power ? 'Considerable amounts of energy: a power plant' : null, met: met.length > 0,
          metName: met.length ? R[met[0]].name : null, options: opts_.map(k => visible(k) ? { name: R[k].name, owned: have[k] !== undefined } : null),
          hint: null };
        if (b.met) { buildMet++; buildTurn = Math.max(buildTurn, Math.min(...met.map(k => have[k].turn))); }
        else if (live) b.hint = hint(g);
        return b;
      });
      const complete = buildMet === build.length;
      const proto = { state: 'none', canCommit: false, reason: '', cost: null, turns: null, progress: null };
      if (snap.prototype && snap.prototype.method === o) Object.assign(proto, { state: 'running', progress: snap.prototype.progress || 0, cost: snap.prototype.cost || null });
      else if (failed.has(o)) proto.state = 'failed';
      else if ((snap.drive && snap.drive.method === o) || (snap.victory && snap.victory.method === o)) proto.state = 'worked';
      else {
        const qt = prototypeQuote(bundle, snap);
        Object.assign(proto, qt);
        const check = opts.canCommit ? opts.canCommit(o) : null;
        if (pt === null) proto.reason = 'not yet proposed';
        else if (standing === 'ruled_out') proto.reason = 'a disproved hypothesis cannot be committed';
        else if (!complete) proto.reason = 'needs every build need met';
        else if (snap.prototype) proto.reason = 'another prototype is under way';
        else if (snap.drive || snap.victory) proto.reason = 'the Drive is already under way';
        else if (check && !check.ok) proto.reason = check.reason || 'not available now';
        else if (!opts.canCommit && !opts.allowCommit) proto.reason = 'not in this replay';
        else { proto.canCommit = true; proto.state = 'available'; }
      }
      vm.hypotheses.push({ method: o, title: o, tagline: METHOD_LINE[o] || '', proposed: pt !== null, proposedTurn: pt, standing, ruledTurn,
        isTrue: engine && trueMethod ? trueMethod === o : null, questions, build, buildMet, buildTotal: build.length, complete, buildTurn: complete ? buildTurn : null, prototype: proto });
      sig.push(o + ':' + (pt !== null) + ':' + standing + ':' + questions.map(q => q.state + (q.hint ? q.hint.focus : '')).join(',') + ':' + build.map(b => (b.met ? 1 : 0) + (b.hint ? b.hint.focus : '')).join(','));
    }

    // the closing statement
    if (closed) vm.statement = 'The unified theory closes the list: every consistent completion of it admits exactly one way to outrun light, the candidates are these ' +
      ({ 5: 'five' }[methods.length] || methods.length) + ', and which holds depends on properties not yet measured.';
    else if (open) vm.statement = 'The light barrier stands. Before a unified theory, no claim is made that any proposal is true, or that the list is complete.';
    if (certainM) vm.certain = { method: certainM, turn: certainTurn(bundle, W, snap, truth, instrD, certainM) };

    // the running results list
    const res = [];
    const add = (turn, text, kind) => { if (turn != null && turn <= T) res.push({ turn, text, kind: kind || 'fact' }); };
    if (open) add(have[FT.OPENS].turn, vm.opensName + ': the light barrier stands, and how to exceed the speed of light is an open question.', 'open');
    const byTurn = {};
    for (const h of vm.hypotheses) if (h.proposed) (byTurn[h.proposedTurn] = byTurn[h.proposedTurn] || []).push(h.method);
    for (const t in byTurn) add(+t, 'Proposed: ' + listText(byTurn[t]) + '.', 'proposal');
    if (closed) add(have[F.CLOSE].turn, vm.closeName + ' closes the list of hypotheses.', 'close');
    const condOnScreen = c => vm.hypotheses.some(h => h.proposed && F.COND[h.method].includes(c));
    const instrDone = {};
    for (const c in known) {
      if (!condOnScreen(c)) continue;
      const k = known[c];
      if (k.instrTurn && FT.INSTRUMENT[c] && !instrDone[FT.INSTRUMENT[c]]) { instrDone[FT.INSTRUMENT[c]] = 1; add(k.instrTurn, 'The ' + FT.INSTRUMENT[c] + ' is complete.', 'instrument'); }
      add(Math.max(k.turn, Math.min(...vm.hypotheses.filter(h => h.proposed && F.COND[h.method].includes(c)).map(h => h.proposedTurn))),
        (k.value ? 'Confirmed: ' : 'Disproved: ') + lower(F.QUESTION[c]) + '.', k.value ? 'holds' : 'fails');
    }
    for (const h of vm.hypotheses) {
      if (!h.proposed) continue;
      if (h.ruledTurn != null && !failed.has(h.method)) add(h.ruledTurn, h.method + ' is ruled out.', 'ruled');
      if (h.standing === 'confirmed') add(Math.max(...F.COND[h.method].map(c => known[c].turn), h.proposedTurn), h.method + ' is confirmed: all its conditions hold.', 'confirmed');
      if (h.complete) add(Math.max(h.buildTurn, h.proposedTurn), 'Every build need of ' + h.method + ' is met: its prototype can be committed.', 'build');
    }
    if (vm.certain && vm.certain.turn != null && !vm.hypotheses.some(h => h.standing === 'confirmed'))
      add(vm.certain.turn, vm.certain.method + ' is the only hypothesis left.', 'only');
    for (const e of snap.ftlLog || []) add(e.turn, e.text, e.kind || 'prototype');
    for (const r of protoResults) add(r.turn, r.works ? 'The ' + r.method + ' prototype works.' : 'The ' + r.method + ' prototype failed: ' + r.method + ' is proven invalid.', r.works ? 'confirmed' : 'ruled');
    if (snap.drive && snap.drive.done) add(snap.drive.done, 'The SS FTL Drive is built.', 'build');
    if (snap.victory) add(snap.victory.turn, 'The ship launches: victory.', 'confirmed');
    vm.results = res.map((r, i) => Object.assign(r, { i })).sort((a, b) => a.turn - b.turn || a.i - b.i);
    vm.signature = (closed ? 'C' : '') + '|' + sig.join('|') + '|' + Object.keys(known).sort().join(',') + '|' + Object.keys(pending).sort().join(',');
    if (engine) vm.engineInfo = { method: trueMethod, truth: truth ? Object.keys(F.HOST).map(c => ({ text: F.QUESTION[c], value: !!truth[c] })) : null, alive };
    return vm;
  }
  const lower = s => s.charAt(0).toLowerCase() + s.slice(1);
  function certainTurn(bundle, W, snap, truth, instrD, m) {
    // the first turn at which the screen was certain: the unified theory held, and every answer it needed in hand
    const F = W.F, have = snap.have;
    let lo = have[F.CLOSE] ? have[F.CLOSE].turn : null;
    if (lo == null) return null;
    for (let t = lo; t <= snap.turn; t++) {
      const h = {};
      for (const k in have) if (have[k].turn <= t) h[k] = have[k];
      const kn = knowledge(bundle, W, h, truth, t, instrD).known;
      const alive = Object.keys(F.COND).filter(o => !F.COND[o].some(c => kn[c] && !kn[c].value));
      if (F.COND[m].every(c => kn[c] && kn[c].value) || (alive.length === 1 && alive[0] === m)) return t;
    }
    return snap.turn;
  }
  // a prototype's price at commitment (section 4): 5x the Space era's price x the calibration x the ahead-of-time premium
  function prototypeQuote(bundle, snap) {
    const V = bundle.victory, d = snap.d || 0;
    const cost = V.protox * V.p_space * V.scale * V.spaceprice * Math.pow(4, Math.max(0, V.space - d));
    const per = (snap.inc || 0) * (snap.have && snap.have.SO05 ? 0.8 : 0.5);
    return { cost, turns: per > 0 ? Math.ceil(cost / per) : null };
  }

  // the victory turn as victory.py computes it: the race's finish (certainty and the build), the prototype, the Drive, a turn to launch
  function victory(bundle, g) {
    if (!(g.cert && g.built)) return null;
    const V = bundle.victory, E = bundle.economy[econKey(g.econ)], key = econKey(g.econ);
    const fin = Math.max(g.cert, g.built);
    const price = V.protox * V.p_space * V.scale * V.spaceprice * Math.pow(4, Math.max(0, V.space - E.d[fin]));
    const protoTurns = Math.ceil(price / (0.8 * E.inc[fin + 1]));
    const proto = fin + protoTurns;
    const exotic = V.exotic.includes(g.m);
    const driveTurns = V.drive[key][exotic ? 'exotic' : 'plain'][proto];
    const launch = proto + driveTurns + 1;
    return { fin, price, protoTurns, proto, driveTurns, exotic, launch, reference: REFERENCE[key], vsReference: launch - REFERENCE[key] };
  }

  const API = { EO, ERA_ABBR, ERA_NEED, REFERENCE, SECTION, STATUS_LABEL, METHOD_LINE, FTL_TEXT, focusLabel, fmt, turns, econKey, listText, world, prereqsMet, eraByCount,
    enteredFoci, classifier, needsOf, normalizeEvents, hiddenInfo, researchModel, ftlModel, smartTargets, hintRow, knowledge, prototypeQuote, victory };
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
  G.UHView = API;
})(typeof window !== 'undefined' ? window : globalThis);
