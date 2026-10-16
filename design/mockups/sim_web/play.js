/* play.js: the live game. A research race played turn by turn in the browser on the simulator's engine (engine.js), drawn
   with the shared research screen (screen.js) and Faster than light screen (ftl.js) from view.js's view models.

   Each turn the player chooses what the funded share goes to: a focus (the radio buttons, or the Fund menu), a Grand
   Endeavour on a revealed breakthrough, or, once a hypothesis's build is complete, its prototype. Then Next turn, 5 or 10
   turns keeping the choice, To the next event, or Fast-forward with the Advisor. When a focus the player chose has nothing
   revealed left under study, funding moves to the next focus in line, or back to Automatic (the field with the most work
   waiting, the simulator's generalist), and the notice says so. The game is won when the ship launches: a working
   prototype, then the SS FTL Drive from Production, then one turn to launch; the victory turn is set against base Civ V's
   science victory on the same income (305 on the good economy, 380 on the average one).

   Saving: the engine's options and the player's choices (UHEngine serialize/restore), with this page's settings, in
   localStorage under 'uh-play-v1' after every turn and every choice, and as a save code to copy. The game's log copies in
   the simulator's trace format (w7f.py's TRACE output), which the replay viewer loads.

   window.UHPlay exposes the state for the tests: {state, get engine(), advance(kind), stats}. */
(function (G) {
  'use strict';
  const V = G.UHView;
  const SAVE_KEY = 'uh-play-v1';
  const WORLDS = [
    { id: 'familiar', name: 'Familiar world', sub: 'Matter is made of atoms, as on Earth: atomic and quantum physics' },
    { id: 'Process', name: 'Process world', sub: 'Elemental: the five phases and their cycles are the real forces' },
    { id: 'Substance', name: 'Substance world', sub: 'Elemental: the four elements are fundamental, and transmutation works' },
  ];
  const WORLD_NAME = { familiar: 'Familiar world', Process: 'Process world', Substance: 'Substance world' };
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const L = f => V.focusLabel(f);
  const median = xs => { if (!xs.length) return null; const s = xs.slice().sort((a, b) => a - b), m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };
  const pct = x => Math.round(100 * (x || 0)) + '%';
  const vsText = (delta, ref) => (delta === 0 ? 'level with' : V.turns(Math.abs(delta)) + (delta < 0 ? ' sooner than' : ' later than')) + ' base Civ V’s science victory on the same income (turn ' + ref + ')';
  const defaultUi = () => ({ queue: [], advisor: false, dry: 'queue', engineView: false, ftlShown: false, ftlUnseen: false, ends: [] });

  function start() {
    const $ = id => document.getElementById(id);
    let bundle;
    try { bundle = JSON.parse($('uh-bundle').textContent); }
    catch (err) { $('pl-error').textContent = 'The page’s data could not be read: ' + err.message; $('pl-error').hidden = false; return; }
    const Engine = G.UHEngine;
    const P = { e: null, ui: defaultUi(), batch: [], running: false, stopReq: false, notices: [], stats: { step: [], render: [] }, victoryShown: false, byFocus: null };

    const screen = UHScreen.create($('pl-screen'), { onFund, onEndeavour, onStopEndeavour, onOpenFtl: openFtl });
    const ftl = UHFtl.create($('pl-ftl'), { onCommit, onClose: closeFtl });

    // ================================================================== small helpers on the engine
    function rowsOf(f) {
      if (!P.byFocus) { P.byFocus = {}; for (const k of P.e.IDS) (P.byFocus[P.e.ROWS[k].focus] = P.byFocus[P.e.ROWS[k].focus] || []).push(k); }
      return P.byFocus[f] || [];
    }
    /** the revealed ideas under study in focus f, as the research screen counts them (its badge) */
    function badge(f) {
      const e = P.e, S = e.S;
      let n = 0;
      for (const k of rowsOf(f)) {
        if (S.have.has(k) || (S.locked.has(k) && k !== S.end_k) || !e.prereqsMet(k, S.have)) continue;
        if (e.tier(k) === 'CORE' || ((S.glimpsed.has(k) || S.diff_since.has(k) || S.diff_unc.has(k)) && S.occurred.has(k))) n++;
      }
      return n;
    }
    const enteredFoci = () => [...P.e.S.foci].sort((a, b) => L(a).localeCompare(L(b)));
    const busyWith = () => { const S = P.e.S; return S.proto ? 'prototype' : (S.end_k !== null || S.endRequest) ? 'endeavour' : null; };
    function committable() { const out = new Set(); for (const m of P.e.METHODS) if (!P.e.prototypeCheck(m)) out.add(m); return out; }
    const name = k => (bundle.rows[k] ? bundle.rows[k].name : 'a breakthrough');

    // ================================================================== notices: what just happened, in plain words
    function note(text, tone, turn) {
      P.notices.unshift({ turn: turn != null ? turn : P.e ? P.e.turn : 0, text, tone: tone || '' });
      P.notices.length = Math.min(P.notices.length, 3);
    }
    function drawNotices() {
      $('pl-notice').innerHTML = P.notices.slice(0, 2).map(n => '<div class="' + (n.tone ? 'is-' + n.tone : '') + '"><span class="pl-nt">Turn ' + n.turn + '</span><span>' + esc(n.text) + '</span></div>').join('');
    }

    // ================================================================== a new game, a saved one
    $('pl-worlds').innerHTML = WORLDS.map((w, i) => '<label class="pl-opt"><input type="radio" name="pl-world" value="' + w.id + '"' + (i === 0 ? ' checked' : '') + '><span class="pl-opt-text"><span>' + esc(w.name) +
      '</span><span class="pl-opt-sub">' + esc(w.sub) + '</span></span></label>').join('');
    const radioVal = n => { const r = document.querySelector('input[name="' + n + '"]:checked'); return r ? r.value : null; };
    $('pl-seed').addEventListener('focus', () => { document.querySelector('input[name="pl-seedmode"][value="typed"]').checked = true; });
    $('pl-start').addEventListener('click', () => {
      let seed;
      if (radioVal('pl-seedmode') === 'typed') {
        seed = Math.floor(Number($('pl-seed').value));
        if (!Number.isFinite(seed) || seed < 0 || seed > 999999999) { showError('A seed is a whole number from 0 to 999,999,999.'); return; }
      } else seed = Engine.SEED0 + Math.floor(Math.random() * 300);
      newGame({ world: radioVal('pl-world') || 'familiar', econ: radioVal('pl-econ') || '1.0', rivals: $('pl-diff').checked, seed });
    });
    $('pl-cancel').addEventListener('click', () => { $('pl-setup').hidden = true; layout(); });
    $('pl-new').addEventListener('click', () => {
      if (P.running) return;
      const s = $('pl-setup');
      s.hidden = !s.hidden;
      $('pl-cancel').hidden = !P.e;
      if (!s.hidden) { s.scrollIntoView({ block: 'start' }); $('pl-start').focus({ preventScroll: true }); }
      layout();
    });
    $('pl-load-save').addEventListener('click', () => {
      let saved;
      try { saved = JSON.parse($('pl-save-text').value); } catch (err) { showError('That is not a save code (it is not valid JSON): ' + err.message); return; }
      if (loadGame(saved, 'Loaded the game from its save code.')) $('pl-save-text').value = '';
    });
    function showError(msg) { $('pl-error').textContent = msg || ''; $('pl-error').hidden = !msg; }

    function begin(e, ui) {
      P.e = e; P.ui = Object.assign(defaultUi(), ui || {}); P.byFocus = null; P.notices = []; P.victoryShown = !!e.victory; P.stats = { step: [], render: [] };
      P.batch = V.normalizeEvents(bundle, e.S.events).map(x => Object.assign(x, { turn: e.turn }));
      showError('');
      $('pl-setup').hidden = true;
      for (const id of ['pl-turnbar', 'pl-fundbar', 'pl-main', 'pl-summary', 'pl-logwrap']) $(id).hidden = false;
      $('pl-copylog').disabled = false; $('pl-copysave').disabled = false;
      $('pl-advisor').checked = P.ui.advisor; $('pl-dry').value = P.ui.dry;
      setView(P.ui.engineView);
    }
    function newGame(cfg) {
      let e;
      try { e = new Engine(bundle, { world: cfg.world, econ: cfg.econ, rivals: cfg.rivals, seed: cfg.seed, player: 'human', trace: true }); }
      catch (err) { showError('The game could not start: ' + err.message); return; }
      begin(e, null);
      screen.select('insight');
      note('A new game: ' + WORLD_NAME[e.world] + ', ' + (e.ECON === 1 ? 'good' : 'average') + ' economy, knowledge diffusion ' + (e.DIFF ? 'on' : 'off') + ', seed ' + e.seed +
        '. Choose a focus to fund (the radio buttons on the left), then press Next turn.');
      render(); save();
    }
    function loadGame(saved, msg) {
      if (!saved || saved.format !== 'uh-play-1' || !saved.engine) { showError('That is not a save code from this page.'); return false; }
      let e;
      try {
        const eng = Object.assign({}, saved.engine, { options: Object.assign({}, saved.engine.options, { trace: true }) });
        e = Engine.restore(bundle, eng);
      } catch (err) { showError('The saved game could not be restored: ' + err.message); return false; }
      begin(e, saved.ui);
      note(msg + (e.restoreWarning ? ' ' + e.restoreWarning : ''), e.restoreWarning ? 'warn' : '');
      render(); save();
      return true;
    }
    function save() {
      if (!P.e) return;
      try { localStorage.setItem(SAVE_KEY, JSON.stringify(saveCode())); } catch (err) { /* private window, blocked storage: the game goes on unsaved */ }
    }
    /** the engine's options and the player's choices; the working method and the world's truth are left out (the engine
        draws them again from the game's index), so a save code does not give the game away */
    function saveCode() {
      const eng = P.e.serialize();
      eng.options = Object.assign({}, eng.options);
      delete eng.options.method; delete eng.options.truth;
      return { format: 'uh-play-1', engine: eng, ui: P.ui, savedAt: new Date().toISOString() };
    }

    // ================================================================== the player's choices
    function onFund(f) {
      if (!P.e || P.running || P.e.over) return;
      if (P.ui.advisor) { P.ui.advisor = false; $('pl-advisor').checked = false; }
      chooseFocus(f);
    }
    function chooseFocus(f) {
      const e = P.e;
      e.setFocus(f || null);
      if (f) P.ui.queue = P.ui.queue.filter(q => q !== f);
      const busy = busyWith();
      if (!f) note('Automatic: each turn the funded share goes to the field with the most work waiting.');
      else if (busy === 'endeavour') note('The Grand Endeavour keeps the funded share until it is complete; then ' + L(f) + ' is funded. To fund it now, stop the Endeavour.');
      else if (busy === 'prototype') note('The prototype keeps the funded share until it is built; then ' + L(f) + ' is funded.');
      else note('Next turn the funded share goes to ' + L(f) + '.' + (badge(f) ? '' : ' Nothing revealed is under study there: its share goes to unseen ideas there, or spills to the other foci.'));
      render(); save();
    }
    function onEndeavour(id) {
      const e = P.e;
      if (!e || P.running || e.over) return;
      const q = e.endeavourQuote(id);
      if (!q || !q.eligible) { note((q && q.reason) || 'Not available now.', 'warn'); render(); return; }
      const S = e.S, running = S.end_k;
      const doIt = () => {
        const r = e.requestEndeavour(id);
        if (!r.ok) note(r.reason, 'warn');
        else {
          if (r.replaced) P.ui.ends.push([e.turn, r.replaced, 'dropped']);
          note('The Grand Endeavour on ' + name(id) + ' begins next turn: ' + V.fmt(q.cost) + ' Insight, about ' + V.turns(q.turns) + ' of the funded share' + (q.aheadOfTime ? ' (dearer: it is ahead of its time)' : '') + '. It cannot fail.');
          screen.select('row:' + id);
        }
        render(); save();
      };
      if (running !== null && running !== id && S.end_prog > 0) {
        dialog('Replace the Grand Endeavour?', '<p>The Endeavour on ' + esc(name(running)) + ' is ' + pct(S.end_prog / S.end_cost) + ' done. A new Endeavour replaces it, and its progress is lost.</p>' +
          '<p>The Endeavour on ' + esc(name(id)) + ' would cost ' + V.fmt(q.cost) + ' Insight, about ' + V.turns(q.turns) + ' of the funded share.</p>', [['Replace it', doIt, 'pl-primary'], ['Keep the one under way']]);
      } else doIt();
    }
    function onStopEndeavour() {
      const e = P.e;
      if (!e || P.running) return;
      const S = e.S, k = S.end_k !== null ? S.end_k : S.endRequest;
      if (!k) return;
      const doIt = () => {
        const wasRunning = S.end_k !== null;
        const r = e.stopEndeavour();
        if (r.ok) { if (wasRunning) P.ui.ends.push([e.turn, k, 'dropped']); note('Stopped the Grand Endeavour on ' + name(k) + '. ' + (S.choice ? L(S.choice) + ' is funded next turn.' : 'Automatic funding resumes next turn.')); }
        render(); save();
      };
      if (S.end_k !== null && S.end_prog > 0) dialog('Stop the Grand Endeavour?', '<p>The Endeavour on ' + esc(name(k)) + ' is ' + pct(S.end_prog / S.end_cost) + ' done. Stopping it loses that progress.</p>', [['Stop it', doIt, 'pl-stop'], ['Keep going']]);
      else doIt();
    }
    function onCommit(m, intro) {
      const e = P.e;
      if (!e || P.running || e.over) return;
      const q = e.prototypeQuote(m);
      if (!q.eligible) { note(q.reason, 'warn'); render(); return; }
      const sure = e.status(e.S.have, e.turn).certain;
      const share = e.S.have.has('SO05') ? 80 : 50, S = e.S, running = S.end_k !== null ? S.end_k : S.endRequest;
      let body = (intro ? '<p>' + esc(intro) + '</p>' : '') + '<p>The prototype costs ' + V.fmt(q.cost) + ' Insight: about ' + V.turns(q.turns) + ' of the funded share (' + share + '%). Research goes on with the rest.</p>';
      body += sure ? '<p>The Faster than light screen is certain: ' + esc(m) + ' is the way to outrun light.</p>'
        : '<p class="pl-warn">Nothing is certain yet. If ' + esc(m) + ' is not the way to outrun light, the prototype fails and returns nothing: the Insight is lost, and ' + esc(m) + ' is ruled out.</p>';
      if (running) body += '<p class="pl-warn">The Grand Endeavour on ' + esc(name(running)) + ' stops, and its progress is lost.</p>';
      body += '<p class="pl-dim">If it works, the SS FTL Drive is built from Production, and the ship launches the turn after.</p>';
      dialog('Commit to a ' + m + ' prototype?', body, [['Commit', () => {
        const r = e.commitPrototype(m);
        if (!r.ok) note(r.reason, 'warn');
        else {
          if (r.stoppedEndeavour && S.end_k === null) P.ui.ends.push([e.turn, r.stoppedEndeavour, 'dropped']);
          note('Committed to a ' + m + ' prototype: ' + V.fmt(r.cost) + ' Insight, about ' + V.turns(q.turns) + '.' + (sure ? '' : ' A Hail Mary: it may fail.'), sure ? 'good' : 'warn');
        }
        render(); save();
      }, 'pl-primary'], ['Not yet']]);
    }
    function openFtl() { P.ui.ftlShown = true; P.ui.ftlUnseen = false; render(); save(); if (window.innerWidth <= 1180) $('pl-ftl').scrollIntoView({ block: 'start' }); }
    function closeFtl() { P.ui.ftlShown = false; render(); save(); if (window.innerWidth <= 1180) $('pl-main').scrollIntoView({ block: 'start' }); }

    // the funding bar
    $('pl-focus').addEventListener('change', ev => { if (P.ui.advisor) { P.ui.advisor = false; $('pl-advisor').checked = false; } chooseFocus(ev.target.value || null); });
    $('pl-advisor').addEventListener('change', ev => {
      P.ui.advisor = ev.target.checked;
      note(P.ui.advisor ? 'The Advisor chooses the focus each turn: the field with the most work waiting, and once the Faster than light screen opens, the field its hints point to.' : 'The Advisor is off: you choose the focus.');
      render(); save();
    });
    $('pl-queue-add').addEventListener('change', ev => {
      const f = ev.target.value;
      if (f && !P.ui.queue.includes(f)) P.ui.queue.push(f);
      ev.target.value = '';
      render(); save();
    });
    $('pl-queue').addEventListener('click', ev => {
      const b = ev.target.closest('button[data-unqueue]');
      if (!b) return;
      P.ui.queue = P.ui.queue.filter(q => q !== b.dataset.unqueue);
      render(); save();
    });
    $('pl-dry').addEventListener('change', ev => { P.ui.dry = ev.target.value; save(); });
    $('pl-ftltab').addEventListener('click', () => (P.ui.ftlShown ? closeFtl() : openFtl()));
    for (const b of document.querySelectorAll('[data-view]')) b.addEventListener('click', () => { setView(b.dataset.view === 'engine'); render(); save(); });
    function setView(engine) {
      P.ui.engineView = !!engine;
      document.querySelectorAll('[data-view]').forEach(x => x.setAttribute('aria-pressed', String((x.dataset.view === 'engine') === P.ui.engineView)));
    }

    // ================================================================== playing turns
    $('pl-next').addEventListener('click', () => advance('next'));
    $('pl-5').addEventListener('click', () => advance(5));
    $('pl-10').addEventListener('click', () => advance(10));
    $('pl-event').addEventListener('click', () => advance('event'));
    $('pl-ff').addEventListener('click', () => advance('ff'));
    $('pl-stop').addEventListener('click', () => { P.stopReq = true; });

    /** one turn: the Advisor's choice, the engine's step, the queue when the funded focus runs dry, and why to stop */
    function stepOnce(spec, batch) {
      const e = P.e, S = e.S;
      const advisor = !!(spec.advisor || P.ui.advisor);
      if (advisor) { const a = e.advise(); if ((a.focus || null) !== S.choice) e.setFocus(a.focus || null); }
      const before = e._revealedSet(), chosen = S.choice, busy = busyWith();
      const watchDry = chosen && !advisor && !busy;
      const prevBadge = watchDry ? badge(chosen) : 0;
      const canBefore = spec.until === 'ff' ? committable() : null, certBefore = S.cert, closedBefore = S.have.has(e.F.CLOSE), openBefore = S.have.has(e.OPENS);
      const t0 = performance.now();
      const evs = e.step();
      P.stats.step.push(performance.now() - t0);
      const T = e.turn;
      for (const x of evs) {
        if (x.type === 'endeavour_started') P.ui.ends.push([T, x.id, 'start']);
        else if (x.type === 'discovered' && x.via === 'endeavour') P.ui.ends.push([T, x.id, 'done']);
        else if (x.type === 'endeavour_ended') P.ui.ends.push([T, x.id, 'dropped']);
        else if (x.type === 'ftl' && !P.ui.ftlShown) P.ui.ftlUnseen = true;
      }
      const norm = V.normalizeEvents(bundle, evs).map(x => Object.assign(x, { turn: T }));
      const stops = [], big = [];
      let dry = null;
      if (watchDry && S.choice === chosen && prevBadge > 0 && !e.over && badge(chosen) === 0) {
        dry = runDry(chosen);
        norm.push({ kind: 'focus', focus: chosen, text: dry, turn: T });
        stops.push(dry);
        note(dry, 'warn', T);
      }
      for (const x of norm) batch.push(x);
      if (batch.length > 3000) batch.splice(0, batch.length - 3000);
      const textOf = x => { const n = V.normalizeEvents(bundle, [x]); return (n[1] || n[0] || { text: '' }).text; };   // an FTL change: its first line after the announcement
      const STOP = { era_entered: 1, focus_entered: 1, ftl: 1, endeavour_ended: 1, prototype_result: 1, drive_done: 1, victory: 1 };
      for (const x of evs) {
        if (x.hidden) continue;
        const t = x.type;
        if ((t === 'discovered' && (x.via !== 'own' || before.has(x.id))) || (t === 'revealed' && x.how !== 'core') || STOP[t]) stops.push(textOf(x));
        if (t === 'prototype_result' || t === 'victory') big.push(textOf(x));
        if (t === 'ftl' && S.proto) for (const c of x.changes || []) if (c.kind === 'ruled_out' && c.method === S.proto.method)
          big.push(c.method + ' is ruled out while its prototype is being built: the prototype will fail and return nothing.');
      }
      if (spec.until === 'ff') {
        if (!openBefore && S.have.has(e.OPENS)) big.push('Relativity opens the question of how to exceed the speed of light: the Faster than light screen is open.');
        if (!closedBefore && S.have.has(e.F.CLOSE)) big.push(name(e.F.CLOSE) + ' closes the list of hypotheses.');
        if (certBefore === null && S.cert !== null) big.push('The Faster than light screen is certain: ' + certainMethod() + ' is the way to outrun light.');
        const now = committable();
        for (const m of now) if (!canBefore.has(m)) big.push('Every build need of ' + m + ' is met: its prototype can be committed on the Faster than light screen.');
      }
      if (e.over && !e.victory) big.push('The game ends on turn ' + T + ' without a launch.');
      return { stops, big, dry };
    }
    /** what Automatic funds on turn 1: the engine's rule (the focus with the most work waiting; the first on a tie) */
    function autoFirst() {
      const e = P.e, S = e.S, d = e.D[1], waiting = new Map();
      for (const k of e.IDS) {
        if (S.have.has(k) || !S.met.has(k) || S.locked.has(k) || !(e.tier(k) === 'CORE' || S.occurred.has(k))) continue;
        const f = e.ROWS[k].focus;
        waiting.set(f, (waiting.get(f) || 0) + e.TARGET[e.tier(k)] * (1 + Math.max(0, d - e.ROWS[k].eraI)));
      }
      return Engine.maxKey(waiting);
    }
    function certainMethod() {
      const e = P.e, st = e.status(e.S.have, e.turn);
      return st.alive.length === 1 ? st.alive[0] : e.METHODS.find(o => e.F.COND[o].every(c => st.kn[c])) || e.method;
    }
    function runDry(f) {
      const e = P.e;
      if (P.ui.dry === 'keep') return 'Nothing revealed is left under study in ' + L(f) + '. You keep funding it: its share goes to unseen ideas there, or spills to the other foci.';
      const skipped = [];
      while (P.ui.queue.length) {
        const q = P.ui.queue.shift();
        if (q === f) continue;
        if (e.S.foci.has(q) && badge(q) > 0) {
          e.setFocus(q);
          return 'Nothing revealed is left under study in ' + L(f) + ': funding moves to ' + L(q) + ', next in line' + (skipped.length ? ' (passing over ' + V.listText(skipped.map(L)) + ', with nothing revealed under study either)' : '') + '.';
        }
        skipped.push(q);
      }
      e.setFocus(null);
      return 'Nothing revealed is left under study in ' + L(f) + (skipped.length ? ' or in ' + V.listText(skipped.map(L)) + ', next in line' : '') + ': funding goes back to Automatic, the field with the most work waiting.';
    }
    async function advance(kind) {
      const e = P.e;
      if (!e || P.running || e.over) return;
      const spec = kind === 'next' ? { n: 1 } : typeof kind === 'number' ? { n: kind } : kind === 'event' ? { n: Infinity, until: 'event' } : { n: Infinity, until: 'ff', advisor: true };
      if (spec.until === 'ff' && !e.S.proto && !e.S.protoWorked && e.S.have.has(e.OPENS) && e.status(e.S.have, e.turn).certain) {
        const m = certainMethod();       // the Advisor never commits for you: it stops here, and asks
        if (!e.prototypeCheck(m)) { onCommit(m, 'The Advisor stops here: ' + m + ' is certain and its build is complete, and it does not commit a prototype for you.'); return; }
      }
      if (spec.until === 'ff') {
        const can = [...committable()];
        if (can.length && !e.S.proto) note('The Advisor chooses the focus but does not commit a prototype for you: ' + V.listText(can) + ' can be committed now, on the Faster than light screen.', 'warn');
      }
      const from = e.turn + 1, batch = [];
      let reason = null, n = 0, lastN = 0, lastPaint = performance.now(), lastDry = null;
      P.running = true; P.stopReq = false;
      if (spec.n > 1) controls();
      try {
        while (!e.over) {
          const r = stepOnce(spec, batch);
          n++;
          if (r.dry) lastDry = r.dry;
          if (r.big.length) { reason = r.big[0]; break; }
          if (spec.until === 'event' && r.stops.length) { reason = r.stops[0]; break; }
          if (n >= spec.n || P.stopReq) break;
          if (performance.now() - lastPaint > 60 || n - lastN >= 20) {   // let the page draw, and Stop be pressed
            lastN = n;
            P.batch = batch.slice();
            render();
            await new Promise(res => setTimeout(res, 0));
            lastPaint = performance.now();
            if (P.e !== e) return;
          }
        }
      } finally { P.running = false; }
      P.batch = batch;
      const tone = reason && /fail|without a launch/.test(reason) ? 'warn' : reason && /Victory|works|certain|committed/.test(reason) ? 'good' : '';
      if (reason && reason !== lastDry) note((spec.n > 1 ? 'Stopped: ' : '') + reason, tone);
      else if (!reason && spec.n > 1) note(P.stopReq ? 'Stopped on turn ' + e.turn + '.' : 'Played turns ' + from + ' to ' + e.turn + '.');
      P.stopReq = false;
      render(); save();
      if (e.victory && !P.victoryShown) { P.victoryShown = true; showVictory(); }
    }

    // ================================================================== drawing
    function snap() {
      const e = P.e, S = e.S, s = e.snapshot({ ftl: false });
      if (e.turn === 0) { s.inc = e.INC[1]; s.share = 0.5; }
      if (!s.prototype && !s.endeavour) {
        if (S.choice) s.funded = S.choice;
        else if (e.turn === 0) s.funded = autoFirst();
      }
      if (!s.endeavour && S.endRequest) { const q = e.endeavourQuote(S.endRequest); s.endeavour = { id: S.endRequest, progress: 0, cost: q ? q.cost : null, pending: true }; }
      s.prototypeResults = S.protoResults.slice();
      s.events = batchEvents();
      return s;
    }
    function batchEvents() {
      const e = P.e;
      if (e.turn === 0) return [{ kind: 'focus', text: 'Choose a focus to fund, then press Next turn.' }];
      const b = P.ui.engineView ? P.batch : P.batch.filter(x => !x.hidden);
      if (!b.length) return [];
      if (b[0].turn === b[b.length - 1].turn) return b;
      // a run of turns: newest turn first, each turn's events in order. Rows and foci are tagged New for the whole run
      // when it is short; after a long one, only for its last turn (the events keep their glyphs, without their ids).
      const last = b[b.length - 1].turn, newFrom = last - b[0].turn < 10 ? b[0].turn : last;
      const out = [];
      for (let i = b.length - 1; i >= 0 && out.length < 400;) {
        let j = i;
        while (j > 0 && b[j - 1].turn === b[i].turn) j--;
        for (let k = j; k <= i; k++) {
          const x = Object.assign({}, b[k], { text: 'Turn ' + b[k].turn + ': ' + b[k].text });
          if (x.turn < newFrom) { delete x.id; delete x.ids; delete x.focus; }
          out.push(x);
        }
        i = j - 1;
      }
      return out;
    }
    function render() {
      const e = P.e;
      if (!e) return;
      const t0 = performance.now();
      const s = snap(), engine = P.ui.engineView;
      screen.render(V.researchModel(bundle, s, { engine, quote: id => e.endeavourQuote(id) }));
      if (!e.S.choice && !e.over) $('pl-screen').querySelectorAll('.uh-radio[disabled]').forEach(r => { r.disabled = false; r.title = 'Automatic chose it last turn: fund it yourself'; });
      const b = P.batch;
      if (b.length && e.turn > 0 && b[0].turn !== b[b.length - 1].turn) {
        const h = $('pl-screen').querySelector('.uh-events-head');
        if (h) h.textContent = 'Turns ' + b[0].turn + ' to ' + e.turn + ', newest first';
      }
      const open = e.S.have.has(e.OPENS);
      if (!open) P.ui.ftlShown = false;
      const main = $('pl-main');
      main.classList.toggle('has-ftl', P.ui.ftlShown);
      main.classList.toggle('is-busy', P.running);
      $('pl-ftl').hidden = !P.ui.ftlShown;
      if (P.ui.ftlShown) {
        ftl.render(V.ftlModel(bundle, s, { engine, canCommit: m => { const r = e.prototypeCheck(m); return { ok: !r, reason: r }; } }));
      }
      controls();
      drawNotices();
      summary(s);
      if ($('pl-logwrap').open) drawLog();
      P.stats.render.push(performance.now() - t0);
      layout();
    }
    function controls() {
      const e = P.e, S = e.S, over = e.over, run = P.running;
      $('pl-turn').textContent = 'Turn ' + e.turn;
      for (const id of ['pl-next', 'pl-5', 'pl-10', 'pl-event', 'pl-ff']) { $(id).disabled = over || run; $(id).hidden = run && id !== 'pl-next'; }
      $('pl-stop').hidden = !run;
      $('pl-new').disabled = run;
      const open = S.have.has(e.OPENS);
      $('pl-ftltab').hidden = !open;
      $('pl-ftltab').setAttribute('aria-pressed', String(P.ui.ftlShown));
      $('pl-ftldot').hidden = !P.ui.ftlUnseen || P.ui.ftlShown;
      // the funding bar
      const foci = enteredFoci(), auto = !S.choice;
      const autoNow = S.active && !S.choice && e.turn > 0 ? ' (now ' + L(S.active) + ')' : '';
      $('pl-focus').innerHTML = '<option value="">Automatic' + esc(autoNow) + '</option>' + foci.map(f => { const n = badge(f); return '<option value="' + esc(f) + '"' + (S.choice === f ? ' selected' : '') + '>' + esc(L(f)) + (n ? ' · ' + n + ' under study' : '') + '</option>'; }).join('');
      if (auto) $('pl-focus').value = '';
      $('pl-focus').disabled = run || over;
      $('pl-advisor').disabled = run || over;
      $('pl-advisor').checked = P.ui.advisor;
      $('pl-queue').innerHTML = P.ui.queue.map(f => '<span class="pl-qchip">' + esc(L(f)) + '<button type="button" data-unqueue="' + esc(f) + '" aria-label="Take ' + esc(L(f)) + ' out of the line"' + (run ? ' disabled' : '') + '>×</button></span>').join('');
      $('pl-queue-add').innerHTML = '<option value="">' + (P.ui.queue.length ? 'and then…' : 'add a focus…') + '</option>' + foci.filter(f => !P.ui.queue.includes(f) && f !== S.choice).map(f => '<option value="' + esc(f) + '">' + esc(L(f)) + '</option>').join('');
      $('pl-queue-add').disabled = run || over;
      $('pl-dry').disabled = run || over;
      const busy = busyWith();
      let fn = '';
      if (P.ui.advisor) fn = 'The Advisor chooses each turn.';
      if (busy === 'endeavour') fn = 'The Grand Endeavour on ' + name(S.end_k !== null ? S.end_k : S.endRequest) + (S.end_k === null ? ' begins next turn and' : '') + ' has the funded share until it is complete.';
      else if (busy === 'prototype') fn = 'The ' + S.proto.method + ' prototype has the funded share until it is built.';
      else if (S.choice && !P.ui.advisor && !badge(S.choice)) fn = 'Nothing revealed is under study in ' + L(S.choice) + '.';
      if (over) fn = e.victory ? 'Victory: the game is over.' : 'The game is over.';
      $('pl-fundnote').textContent = fn;
      const W = WORLD_NAME[e.world];
      $('pl-headline').innerHTML = esc(W) + ' · ' + (e.ECON === 1 ? 'good' : 'average') + ' economy · diffusion ' + (e.DIFF ? 'on' : 'off') + ' · seed ' + e.seed +
        (e.victory ? ' · <strong>victory on turn ' + e.victory.turn + '</strong> (base Civ V: ' + e.victory.reference + ')' : '');
    }
    function summary(s) {
      const e = P.e, S = e.S, engine = P.ui.engineView;
      const fact = (k, v, note, wide, hid) => '<div class="rp-fact' + (wide ? ' is-wide' : '') + '"><dt' + (hid ? ' class="pl-hidden-ink"' : '') + '>' + esc(k) + '</dt><dd' + (hid ? ' class="pl-hidden-ink"' : '') + '>' + v +
        (note ? '<span class="rp-note">' + esc(note) + '</span>' : '') + '</dd></div>';
      const counts = { own: 0, diffusion: 0, endeavour: 0 };
      for (const v of S.have.values()) counts[v.via] = (counts[v.via] || 0) + 1;
      const begun = P.ui.ends.filter(x => x[2] === 'start').length, done = P.ui.ends.filter(x => x[2] === 'done').length;
      const ref = Engine.REFERENCE[e.econ];
      const open = S.have.has(e.OPENS), closeT = S.have.has(e.F.CLOSE) ? S.have.get(e.F.CLOSE).turn : null;
      const failed = S.protoResults.filter(r => !r.works);
      let proto = 'none yet';
      if (S.proto) proto = S.proto.method + ': ' + pct(S.proto.progress / S.proto.cost) + ' built';
      else if (S.protoWorked) proto = S.protoWorked + ' works (turn ' + S.protoResults.find(r => r.works).turn + ')';
      let drive = 'needs a working prototype';
      if (S.drive && S.drive.done !== null) drive = 'built on turn ' + S.drive.done;
      else if (S.drive) drive = V.turns(S.drive.turnsLeft) + ' of building left';
      const ftlText = !open ? 'opens with Relativity' : S.cert !== null ? 'certain on turn ' + S.cert + ': ' + certainMethod() : closeT ? 'the list closed on turn ' + closeT : 'open since turn ' + S.have.get(e.OPENS).turn;
      let html = '<h2 class="rp-sum-title">' + esc(WORLD_NAME[e.world]) + ' · ' + (e.ECON === 1 ? 'good economy' : 'average economy (four-fifths of the Insight)') + ' · knowledge diffusion ' + (e.DIFF ? 'on' : 'off') + ' · seed ' + e.seed + '</h2><dl class="rp-facts">' +
        fact('Turn', String(e.turn), s.era + ' era by count · development ' + s.devEra) +
        fact('Discoveries', String(S.have.size), counts.own + ' own · ' + counts.diffusion + ' from abroad · ' + counts.endeavour + ' by Endeavour') +
        fact('Grand Endeavours', begun ? begun + ' begun' : 'none yet', begun ? done + ' completed' : '') +
        fact('Faster than light', esc(ftlText)) +
        fact('Prototypes', esc(proto), failed.length ? 'failed: ' + failed.map(r => r.method + ' (turn ' + r.turn + ')').join(', ') : 'none failed') +
        fact('SS FTL Drive', esc(drive)) +
        fact('Victory', e.victory ? '<strong>turn ' + e.victory.turn + '</strong>' : e.over ? 'none' : 'not yet', e.victory ? vsText(e.victory.delta, ref) : 'base Civ V’s science victory on this income: turn ' + ref, true);
      if (engine) {
        const st = P.stats, ms = x => x == null ? '–' : x < 10 ? x.toFixed(2) : Math.round(x);
        html += fact('Working method', esc(e.method), 'hidden from the player', false, true) +
          fact('World truth', esc(Object.keys(e.F.HOST).map(c => (e.truth[c] ? '✓ ' : '✗ ') + e.F.QUESTION[c]).join('; ')), '', true, true) +
          fact('Simulator game', String(e.game), 'rivals from the pool’s games of ' + e.method, false, true) +
          fact('Time a turn', ms(median(st.step)) + ' ms', 'drawing the screens: ' + ms(median(st.render)) + ' ms (medians, this session)', false, true);
      }
      html += '</dl>';
      $('pl-summary').innerHTML = html;
    }
    function drawLog() {
      const e = P.e, engine = P.ui.engineView;
      const items = V.normalizeEvents(bundle, e.S.log).map((x, i) => Object.assign(x, { turn: e.S.log[i] ? e.S.log[i].turn : 0 }));
      // normalizeEvents can expand an ftl event into several lines: carry turns forward
      let t = 0;
      for (const x of items) { if (x.turn) t = x.turn; else x.turn = t; }
      const shown = items.filter(x => engine || !x.hidden).reverse().slice(0, 800);
      $('pl-log').innerHTML = shown.map(x => '<li class="' + (x.hidden ? 'is-hidden' : '') + '"><span class="pl-lt">' + x.turn + '</span><span>' + esc(x.text) + '</span></li>').join('') || '<li><span class="pl-dim">Nothing yet.</span></li>';
    }
    $('pl-logwrap').addEventListener('toggle', () => { if ($('pl-logwrap').open && P.e) drawLog(); });

    // on a desktop the screens fill the window below the bars
    function layout() {
      const root = document.documentElement;
      if (window.innerWidth <= 760 || $('pl-main').hidden) { root.style.removeProperty('--uh-screen-h'); return; }
      const top = $('pl-main').getBoundingClientRect().top + window.scrollY;
      root.style.setProperty('--uh-screen-h', Math.round(Math.max(480, Math.min(900, window.innerHeight - top - 10))) + 'px');
    }
    let rt = null;
    window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(layout, 120); });

    // ================================================================== dialogs (the frame blocks alert and confirm)
    let lastFocus = null;
    function dialog(title, body, buttons, cls) {
      const d = $('pl-dialog');
      lastFocus = document.activeElement;
      d.className = 'pl-dialog' + (cls ? ' ' + cls : '');
      d.innerHTML = '<h2 id="pl-dialog-h">' + esc(title) + '</h2>' + body + '<div class="pl-row">' + buttons.map((b, i) => '<button type="button" class="rp-btn ' + (b[2] || '') + '" data-i="' + i + '">' + esc(b[0]) + '</button>').join('') + '</div>';
      d.querySelectorAll('button[data-i]').forEach(btn => btn.addEventListener('click', () => { closeDialog(); const f = buttons[+btn.dataset.i][1]; if (f) f(); }));
      $('pl-modal').hidden = false;
      const first = d.querySelector('button[data-i]');
      if (first) first.focus();
    }
    function closeDialog() {
      $('pl-modal').hidden = true;
      if (lastFocus && document.contains(lastFocus)) lastFocus.focus({ preventScroll: true });
    }
    document.addEventListener('keydown', ev => { if (ev.key === 'Escape' && !$('pl-modal').hidden) closeDialog(); });
    $('pl-modal').addEventListener('click', ev => { if (ev.target === $('pl-modal')) closeDialog(); });

    function showVictory() {
      const e = P.e, v = e.victory, S = e.S;
      const counts = { own: 0, diffusion: 0, endeavour: 0 };
      for (const x of S.have.values()) counts[x.via] = (counts[x.via] || 0) + 1;
      const begun = P.ui.ends.filter(x => x[2] === 'start').length, done = P.ui.ends.filter(x => x[2] === 'done').length;
      const failed = S.protoResults.filter(r => !r.works);
      const body = '<p class="pl-big">Victory on turn ' + v.turn + '</p><p>' + esc(vsText(v.delta, v.reference).replace(/^./, c => c.toUpperCase())) + '.</p><dl class="pl-facts">' +
        '<dt>The way to outrun light</dt><dd>' + esc(v.method) + '</dd>' +
        '<dt>Discoveries</dt><dd>' + S.have.size + ': ' + counts.own + ' your own, ' + counts.diffusion + ' from abroad, ' + counts.endeavour + ' by Endeavour</dd>' +
        '<dt>Grand Endeavours</dt><dd>' + (begun ? begun + ' begun, ' + done + ' completed' : 'none') + '</dd>' +
        '<dt>Prototypes failed</dt><dd>' + (failed.length ? esc(failed.map(r => r.method + ' (turn ' + r.turn + ')').join(', ')) : 'none') + '</dd>' +
        '<dt>Certain</dt><dd>' + (S.cert !== null ? 'turn ' + S.cert : 'never: a Hail Mary that worked') + '</dd>' +
        '<dt>Prototype works</dt><dd>turn ' + S.protoResults.find(r => r.works).turn + '</dd>' +
        '<dt>SS FTL Drive built</dt><dd>turn ' + S.drive.done + ' (' + V.turns(S.drive.total) + ' from Production)</dd>' +
        '<dt>Seed</dt><dd>' + e.seed + ' · ' + esc(WORLD_NAME[e.world]) + ' · ' + (e.ECON === 1 ? 'good' : 'average') + ' economy</dd></dl>';
      dialog('The ship launches', body, [['Copy the game’s log', copyLog, 'pl-primary'], ['New game', () => $('pl-new').click()], ['Look around']], 'is-victory');
    }

    // ================================================================== the log and the save code, copied
    function buildLog() {
      const e = P.e, S = e.S, F = e.F;
      const records = e.traceRecords.map(r => { const o = Object.assign({}, r); delete o.raw; return o; });
      const entries = [...S.have.entries()].sort((a, b) => a[1].turn - b[1].turn);
      const alive = {}, h = new Map();
      let i = 0;
      for (let T = 1; T <= S.turn; T++) {
        while (i < entries.length && entries[i][1].turn <= T) { h.set(entries[i][0], entries[i][1]); i++; }
        const st = e.status(h, T);
        alive[T] = { alive: st.alive, known: st.kn, certain: st.certain };
      }
      const tAt = k => (S.have.has(k) ? S.have.get(k).turn : Infinity);
      const bm = F.BUILD[e.method].map(g => Math.min(...g.map(tAt)));
      const built = bm.length && Math.max(...bm) < Infinity ? Math.max(...bm) : null;
      let cert = null;
      if (S.cert !== null) { const hc = new Map(entries.filter(x => x[1].turn <= S.cert)); cert = [S.cert, Object.keys(e.knowledge(hc, S.cert)).length]; }
      const instr = {};
      for (const c of Object.keys(F.HOST)) instr[c] = e.INSTR[c] || null;
      const focus = {};
      for (const k of e.IDS) focus[k] = e.ROWS[k].focus;
      const ends = P.ui.ends.slice().sort((a, b) => a[0] - b[0]);
      const build = {};
      for (const o of e.METHODS) build[o] = F.BUILD[o];
      return {
        m: e.method, truth: e.truth, seed: e.seed, truthseed: 31, records, alive, cert, ends, instr, instr_d: e.INSTR_D, close: F.CLOSE, focus,
        world: e.world, econ: e.ECON, player: 'human', game: e.game, built, build, cond: F.COND, host: F.HOST, settings: bundle.settings,
        // beyond w7f.py's format: what only the live game has
        source: 'live game (sim_web/play.html), ' + bundle.version, diffusion: !!e.DIFF, victory: e.victory, prototypes: S.protoResults, choices: e.actions,
      };
    }
    function copyLog() { if (P.e) copyText(JSON.stringify(buildLog()), 'The game’s log', 'In the replay viewer, choose Paste a log (or save it as a .json file and open it).'); }
    $('pl-copylog').addEventListener('click', copyLog);
    $('pl-copysave').addEventListener('click', () => { if (P.e) copyText(JSON.stringify(saveCode()), 'The save code', 'Paste it under New game, Load a game from a save code, to carry on from this turn.'); });
    async function copyText(text, what, how) {
      let ok = false;
      try { if (navigator.clipboard && navigator.clipboard.writeText) { await navigator.clipboard.writeText(text); ok = true; } } catch (err) { ok = false; }
      if (ok) { note(what + ' is copied to the clipboard (' + Math.round(text.length / 1024) + ' KB). ' + how, 'good'); drawNotices(); return; }
      dialog(what, '<p>The clipboard is not available here: select all of the text below and copy it. ' + esc(how) + '</p><textarea id="pl-copy-text" readonly spellcheck="false" aria-label="' + esc(what) + '"></textarea>', [['Done']]);
      const ta = $('pl-copy-text');
      ta.value = text;
      ta.focus(); ta.select();
    }

    // ================================================================== start: carry on a saved game, or set up a new one
    let saved = null;
    try { const raw = localStorage.getItem(SAVE_KEY); saved = raw ? JSON.parse(raw) : null; } catch (err) { saved = null; }
    if (!(saved && loadGame(saved, 'Carried on your saved game.'))) {
      $('pl-setup').hidden = false;
    }
    layout();
    G.UHPlay = { get engine() { return P.e; }, state: P, advance, render, buildLog, saveCode, newGame, loadGame, get stats() { return P.stats; } };
  }

  if (typeof document !== 'undefined' && document.getElementById && document.getElementById('pl-setup')) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
  }
})(typeof window !== 'undefined' ? window : globalThis);
