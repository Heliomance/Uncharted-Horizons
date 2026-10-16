/* screen.js: the research screen, drawn from a view model (view.js researchModel). Plain DOM, no framework.

   const screen = UHScreen.create(container, {
     readOnly,                 // true: every action is shown but disabled (the replay viewer)
     onFund(focus),            // the player funds a focus
     onEndeavour(rowId),       // the player begins a Grand Endeavour on a revealed row
     onStopEndeavour(),        // the player stops the running Endeavour
     onSelect(sel),            // 'row:<id>' | 'focus:<name>' | 'insight' | 'era' (for the app's own use; optional)
     onOpenFtl(),              // the Faster than light button (shown once Relativity is discovered)
   });
   screen.render(vm);          // draw (or redraw) a view model; selection, filter and collapsed sections persist
   screen.select(sel);         // select something from outside
   screen.destroy();
*/
(function (G) {
  'use strict';
  const V = G.UHView;
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  // glyphs: statuses differ by fill, border pattern and glyph, never by hue alone (shapes from the earlier mockup)
  const FLASK = '<path d="M5 1.5h4M5.8 1.5v4L2.2 11.6c-.4.7.1 1.4.9 1.4h7.8c.8 0 1.3-.7.9-1.4L8.2 5.5v-4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M3.6 9.5h6.8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>';
  const GLYPH = {
    studying: '<svg class="uh-g" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="7.5" fill="#FFFFFF"/><g transform="translate(2.3 2.1) scale(.82)" color="#000033">' + FLASK + '</g></svg>',
    waiting: '<svg class="uh-g" viewBox="0 0 14 14" aria-hidden="true"><circle cx="7" cy="7" r="5.2" fill="none" stroke="currentColor" stroke-width="1.5" stroke-dasharray="2.2 1.6"/><circle cx="7" cy="7" r="1.6" fill="currentColor"/></svg>',
    unreach: '<svg class="uh-g" viewBox="0 0 14 14" aria-hidden="true"><rect x="2.75" y="6.25" width="8.5" height="6.25" rx="1.2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M4.8 6.25V4.5a2.2 2.2 0 0 1 4.4 0v1.75" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>',
    closed: '<svg class="uh-g" viewBox="0 0 14 14" aria-hidden="true"><rect x="2.25" y="2.25" width="9.5" height="9.5" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M2.5 5.6h9M2.5 8.4h9" stroke="currentColor" stroke-width="1.3"/></svg>',
    not_taken: '<svg class="uh-g" viewBox="0 0 14 14" aria-hidden="true"><path d="M3 12.5V8.3L7 5V1.5M7 5l4.5 3.6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><path d="M8.6 10.9l2.6-3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
    endeavour: '<svg class="uh-g" viewBox="0 0 16 16" aria-hidden="true"><rect x="1" y="1" width="14" height="14" rx="3" fill="#FFFFFF"/><path d="M3 12.5h10L8 3.5z" fill="#000033"/></svg>',
    owned: '<svg class="uh-g" viewBox="0 0 14 14" aria-hidden="true"><rect x="1.5" y="3.5" width="11" height="7" rx="3.5" fill="#FFD700" stroke="#B3B3B3"/></svg>',
    insight: '<svg class="uh-g" viewBox="0 0 14 14" aria-hidden="true">' + FLASK + '</svg>',
    focus: '<svg class="uh-g" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="8" cy="8" r="3.5" fill="currentColor"/></svg>',
    era: '<svg class="uh-g" viewBox="0 0 14 14" aria-hidden="true"><path d="M2 12V5l5-3 5 3v7" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="M5 12V8h4v4" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>',
    hidden: '<svg class="uh-g" viewBox="0 0 14 14" aria-hidden="true"><path d="M1.5 7s2-3.5 5.5-3.5S12.5 7 12.5 7 10.5 10.5 7 10.5 1.5 7 1.5 7z" fill="none" stroke="currentColor" stroke-width="1.3"/><path d="M2.5 12L11.5 2" stroke="currentColor" stroke-width="1.3"/></svg>',
  };
  const radio = on => '<svg class="uh-g" viewBox="0 0 14 14" aria-hidden="true"><circle cx="7" cy="7" r="5.75" fill="none" stroke="currentColor" stroke-width="1.5"/>' + (on ? '<circle cx="7" cy="7" r="3" fill="currentColor"/>' : '') + '</svg>';
  const chevron = open => '<svg class="uh-chev" viewBox="0 0 10 10" aria-hidden="true"><path d="' + (open ? 'M2 3.5l3 3 3-3' : 'M3.5 2l3 3-3 3') + '" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  const EVENT_GLYPH = { discovered: 'owned', revealed: 'waiting', passed: 'closed', not_taken: 'not_taken', rediscovered: 'studying', occurred: 'studying',
    focus: 'focus', era: 'era', endeavour: 'endeavour', ftl: 'insight', 'ftl-result': 'insight', finish: 'endeavour' };
  const SEGS = [['studying', 'Being studied', 'Studied'], ['waiting', 'Awaiting the idea', 'Awaiting'], ['unreach', 'Not yet reachable', 'Not yet'],
    ['closed', 'Moment passed', 'Passed'], ['not_taken', 'Path not taken', 'Not taken'], ['owned', 'Owned', 'Owned']];

  function create(container, opts) {
    opts = opts || {};
    const st = { vm: null, sel: 'insight', filter: null, collapsed: {} };
    const root = document.createElement('div');
    root.className = 'uh-screen';
    container.appendChild(root);

    function chip(c) {
      const sel = st.sel === 'row:' + c.id;
      const live = c.status !== 'owned' && c.status !== 'not_taken';
      const tags = c.tags.map(t => '<span class="uh-tag tag-' + t.kind + '">' + esc(t.text) + '</span>').join('');
      const era = live ? '<span class="uh-era tone-' + c.eraTone + '">' + esc(c.eraAbbr) + '</span>' : '';
      const g = c.status === 'owned' ? '' : (GLYPH[c.status] || '');
      const label = c.name + ' — ' + V.STATUS_LABEL[c.status] + (c.hidden ? ' (hidden from the player)' : '') + ' — ' + c.focusLabel + ', ' + c.era + ' era' +
        (c.tags.length ? ' — ' + c.tags.map(t => t.text).join(', ') : '');
      return '<button type="button" class="uh-chip st-' + c.status + (c.hidden ? ' is-hidden' : '') + (sel ? ' is-sel' : '') + '" data-sel="row:' + esc(c.id) +
        '" aria-label="' + esc(label) + '" aria-pressed="' + (sel ? 'true' : 'false') + '">' + (c.hidden ? GLYPH.hidden : '') + g +
        '<span class="uh-chip-name">' + esc(c.name) + '</span>' + era + tags + '</button>';
    }
    function section(s) {
      const open = !st.collapsed[s.key];
      const head = '<button type="button" class="uh-sec-head" data-toggle="' + s.key + '" aria-expanded="' + open + '">' + (GLYPH[s.key] || '') +
        '<span class="uh-sec-title">' + esc(s.title) + '</span><span class="uh-sec-count">' + s.count + '</span>' +
        (s.hiddenCount ? '<span class="uh-sec-hidden">+' + s.hiddenCount + ' hidden</span>' : '') + chevron(open) +
        '<span class="uh-sec-why">' + esc(s.why) + '</span></button>';
      if (!open) return '<section class="uh-sec sec-' + s.key + '">' + head + '</section>';
      const runs = s.groups.map(g => '<div class="uh-run"><button type="button" class="uh-run-label' + (g.funded ? ' is-funded' : '') + (st.sel === 'focus:' + g.focus ? ' is-sel' : '') +
        '" data-sel="focus:' + esc(g.focus) + '">' + esc(g.label) + '</button><div class="uh-chips">' + g.rows.map(chip).join('') + '</div></div>').join('');
      return '<section class="uh-sec sec-' + s.key + '">' + head + '<div class="uh-runs">' + runs + '</div></section>';
    }
    function ownedBlock(vm) {
      const O = vm.owned, open = !st.collapsed.owned;
      if (!O.count) return '<section class="uh-sec sec-owned"><div class="uh-sec-head is-static">' + GLYPH.owned + '<span class="uh-sec-title">Owned</span><span class="uh-sec-count">0</span>' +
        '<span class="uh-sec-why">nothing discovered yet: each breakthrough you discover is listed here, under its era</span></div></section>';
      const nRare = O.bands.reduce((n, b) => n + b.rows.filter(r => r.tier === 'RARE').length, 0), nUnique = O.bands.reduce((n, b) => n + b.rows.filter(r => r.tier === 'UNIQUE').length, 0);
      const nAbroad = O.bands.reduce((n, b) => n + b.rows.filter(r => r.via === 'diffusion').length, 0);
      const why = ['newest era first, newest discovery first'];
      if (nAbroad) why.push(nAbroad + ' from abroad');
      if (nRare) why.push(nRare + ' rare');
      if (nUnique) why.push(nUnique + ' unique');
      let html = '<section class="uh-sec sec-owned"><button type="button" class="uh-sec-head" data-toggle="owned" aria-expanded="' + open + '">' + GLYPH.owned +
        '<span class="uh-sec-title">Owned</span><span class="uh-sec-count">' + O.count + '</span>' + chevron(open) + '<span class="uh-sec-why">' + esc(why.join(' · ')) + '</span></button>';
      if (open) {
        html += O.bands.map(b => {
          const bo = !st.collapsed['band:' + b.era];
          return '<div class="uh-band"><button type="button" class="uh-band-head band-' + b.tone + '" data-toggle="band:' + esc(b.era) + '" aria-expanded="' + bo + '">' +
            '<span>' + esc(b.label) + '</span><span class="uh-band-count">· ' + b.count + ' owned</span>' + chevron(bo) + '</button>' +
            (bo ? '<div class="uh-chips uh-band-chips">' + b.rows.map(chip).join('') + '</div>' : '') + '</div>';
        }).join('');
      }
      return html + '</section>';
    }
    function fundCard(vm) {
      const H = vm.header, f = H.funded, ins = V.fmt(H.insight);
      let slot;
      if (f.kind === 'focus') slot = '<span class="uh-fund-slot is-focus">' + radio(true) + '<span class="uh-fund-name">' + esc(f.label) + '</span><span class="uh-fund-right">' + H.sharePct + '% · ' + V.fmt(H.fundedInsight) + '</span></span>';
      else if (f.kind === 'endeavour' || f.kind === 'prototype') {
        const pct = Math.round(100 * (f.progress || 0));
        slot = '<span class="uh-fund-slot is-endeavour"><span class="uh-fund-line">' + GLYPH.endeavour + '<span class="uh-fund-name">' + esc(f.name) + '</span><span class="uh-fund-right">' + H.sharePct + '%</span></span>' +
          '<span class="uh-fund-line"><span>' + (f.kind === 'prototype' ? 'Prototype' : f.done ? 'Completed' : 'Endeavour') + '</span><span class="uh-meter"><span style="width:' + Math.min(100, pct) + '%"></span></span><span>' + pct + '%</span></span></span>';
      } else slot = '<span class="uh-fund-slot is-none">' + radio(false) + '<span class="uh-fund-name">Nothing funded</span><span class="uh-fund-right">' + H.splitPct + '%</span></span>';
      return '<button type="button" class="uh-fund' + (st.sel === 'insight' ? ' is-sel' : '') + '" data-sel="insight" aria-label="Funding: ' + esc(f.kind === 'focus' ? f.label : f.name || 'nothing') + '">' +
        '<span class="uh-fund-ins">' + GLYPH.insight + '<span>' + ins + ' Insight a turn</span></span>' + slot +
        '<span class="uh-fund-spread"><span>Spread to other foci</span><span>' + (100 - H.sharePct) + '% · ' + V.fmt(H.spreadInsight) + '</span></span></button>';
    }
    function fociList(vm) {
      const ro = !!opts.readOnly;
      return vm.foci.map(f => {
        const sel = st.sel === 'focus:' + f.name;
        return '<div class="uh-focus' + (f.funded ? ' is-funded' : '') + (sel ? ' is-sel' : '') + '" role="listitem">' +
          '<button type="button" class="uh-radio" data-act="fund" data-arg="' + esc(f.name) + '" aria-pressed="' + f.funded + '" aria-label="Fund ' + esc(f.label) + '"' + (ro || f.funded ? ' disabled' : '') + '>' + radio(f.funded) + '</button>' +
          '<button type="button" class="uh-focus-name" data-sel="focus:' + esc(f.name) + '">' + esc(f.label) + '</button>' +
          (f.holdsEndeavour ? '<span class="uh-mini" title="holds the Grand Endeavour">' + GLYPH.endeavour + '</span>' : '') +
          (f.isNew ? '<span class="uh-tag tag-new">New</span>' : '') +
          (f.flow != null ? '<span class="uh-flow" title="Insight this turn (engine)">' + V.fmt(f.flow) + '</span>' : '') +
          (f.hiddenBadge ? '<span class="uh-badge is-hidden" title="hidden ideas under study (engine)">+' + f.hiddenBadge + '</span>' : '') +
          (f.badge ? '<span class="uh-badge" title="' + f.badge + ' revealed under study">' + f.badge + '</span>' : '') + '</div>';
      }).join('');
    }
    function topBar(vm) {
      const segs = SEGS.map(([k, label, short]) => {
        const n = vm.counts[k] || 0, on = st.filter === k, dis = !n && !on;
        return '<button type="button" class="uh-seg' + (on ? ' is-on' : '') + '" data-filter="' + k + '" aria-pressed="' + on + '"' + (dis ? ' disabled' : '') + ' aria-label="' + esc(label + ': ' + n) + '">' +
          (GLYPH[k] || '') + '<span class="uh-seg-label">' + esc(label) + '</span><span class="uh-seg-short">' + esc(short) + '</span><span class="uh-seg-n">' + n + '</span></button>';
      }).join('');
      return '<div class="uh-segs">' + segs + '</div><button type="button" class="uh-erapill' + (st.sel === 'era' ? ' is-sel' : '') + '" data-sel="era" aria-label="' + esc(vm.header.era.text) + '">' +
        '<span class="uh-era-long">' + esc(vm.header.era.text) + '</span><span class="uh-era-short">' + esc(vm.header.era.short) + '</span></button>';
    }
    function needsHtml(needs) {
      if (!needs || !needs.length) return '';
      const part = p => '<span class="' + (p.met ? 'uh-ok' : 'uh-no') + '">' + (p.met ? '✓' : '✗') + '</span> ' + esc(p.name);
      return '<div class="uh-line">Needs ' + needs.map(g => {
        const s = g.options.map(o => o.map(part).join(' + ')).join(' or ');
        return g.options.length > 1 ? '(' + s + ')' : s;
      }).join(' + ') + '</div>';
    }
    function bar(vm) {
      let d = vm.detailOf(st.sel);
      if (!d) { st.sel = 'insight'; d = vm.detailOf('insight'); }
      const g = d.status === 'owned' ? GLYPH.owned : GLYPH[d.status] || GLYPH.insight;
      const ro = !!opts.readOnly;
      const acts = d.actions.map(a => {
        const enabled = a.enabled && !ro && a.act;
        return '<button type="button" class="uh-act' + (a.act ? '' : ' is-state') + '"' + (a.act ? ' data-act="' + a.act + '" data-arg="' + esc(a.arg || '') + '"' : '') + (enabled ? '' : ' disabled') +
          (ro && a.act ? ' title="The replay is read-only"' : '') + '><span class="uh-act-l1">' + esc(a.label) + '</span>' + (a.sub ? '<span class="uh-act-l2">' + esc(a.sub) + '</span>' : '') + '</button>';
      }).join('');
      const lines = d.lines.map(l => '<div class="uh-line' + (l.tone ? ' tone-' + l.tone : '') + '">' + esc(l.text) + '</div>').join('');
      const eng = d.engine.length ? '<div class="uh-engine-lines">' + d.engine.map(t => '<div>' + GLYPH.hidden + esc(t) + '</div>').join('') + '</div>' : '';
      const ev = vm.events.length ? vm.events.map(e => '<li class="ev-' + esc(e.kind) + (e.hidden ? ' is-hidden' : '') + '">' + (GLYPH[EVENT_GLYPH[e.kind]] || GLYPH.insight) +
        '<span>' + esc(e.text) + '</span></li>').join('') : '<li class="ev-none"><span>Nothing new this turn.</span></li>';
      return '<div class="uh-bar-left">' + (vm.ftlOpen ? '<button type="button" class="uh-act uh-ftl-btn" data-act="ftl"' + (opts.onOpenFtl ? '' : ' disabled') + '><span class="uh-act-l1">Faster than light</span></button>' : '') + '</div>' +
        '<div class="uh-desc uh-scroll" data-k="desc" aria-live="polite"><div class="uh-desc-head">' + g + '<span class="uh-desc-title">' + esc(d.title) + '</span><span class="uh-desc-meta">' + esc(d.meta) + '</span>' +
        (d.hidden ? '<span class="uh-tag tag-hidden">Hidden</span>' : '') + '</div>' + lines + needsHtml(d.needs) + (d.quote ? '<div class="uh-line tone-quote">“' + esc(d.quote) + '”</div>' : '') + eng + '</div>' +
        '<div class="uh-acts">' + acts + '</div>' +
        '<div class="uh-events uh-scroll" data-k="events"><div class="uh-events-head">Turn ' + vm.turn + '</div><ul>' + ev + '</ul></div>';
    }
    function board(vm) {
      const secs = vm.sections.filter(s => s.key === 'endeavour' || !st.filter || st.filter === s.key).map(section).join('');
      const own = !st.filter || st.filter === 'owned' ? ownedBlock(vm) : '';
      const eng = vm.engineInfo ? '<div class="uh-engine-note">' + GLYPH.hidden + '<span>Engine view: hidden ideas, meters and tiers are shown and marked.' +
        (vm.engineInfo.method ? ' The working method is ' + esc(vm.engineInfo.method) + '.' : '') +
        (vm.engineInfo.rivalsAhead != null ? ' Rivals hold ' + vm.engineInfo.rivalsAhead + ' breakthroughs you do not.' : '') + '</span></div>' : '';
      return eng + secs + own;
    }

    function render(vm) {
      if (vm) st.vm = vm;
      vm = st.vm;
      if (!vm) return;
      if (st.filter && !(vm.counts[st.filter] > 0)) st.filter = null;
      const keep = {};
      root.querySelectorAll('.uh-scroll').forEach(el => { if (el.dataset.k) keep[el.dataset.k] = el.scrollTop; });
      const a = document.activeElement, focusKey = a && root.contains(a) ? ['data-sel', 'data-act', 'data-toggle', 'data-filter'].map(n => a.getAttribute(n) ? '[' + n + '="' + CSS.escape(a.getAttribute(n)) + '"]' : '').join('') : null;
      root.className = 'uh-screen' + (opts.readOnly ? ' is-readonly' : '') + (vm.engine ? ' is-engine' : '');
      root.innerHTML =
        '<div class="uh-left">' + fundCard(vm) + '<div class="uh-foci uh-scroll" data-k="foci" role="list" aria-label="Foci">' + fociList(vm) + '</div>' +
        '<div class="uh-hint">' + radio(false) + '<span>' + (opts.readOnly ? 'the simulated player’s choices' : 'funds a focus') + '</span></div></div>' +
        '<div class="uh-divider" aria-hidden="true"></div>' +
        '<div class="uh-right"><div class="uh-top">' + topBar(vm) + '</div><div class="uh-board uh-scroll" data-k="board">' + board(vm) + '</div></div>' +
        '<div class="uh-bar">' + bar(vm) + '</div>';
      root.querySelectorAll('.uh-scroll').forEach(el => { if (keep[el.dataset.k] != null) el.scrollTop = keep[el.dataset.k]; });
      if (focusKey) { const el = root.querySelector(focusKey); if (el) el.focus({ preventScroll: true }); }
    }
    function select(sel) {
      st.sel = sel || 'insight';
      if (opts.onSelect) opts.onSelect(st.sel);
      render();
    }
    function onClick(e) {
      const t = e.target.closest('button');
      if (!t || !root.contains(t) || t.disabled) return;
      if (t.dataset.toggle) { st.collapsed[t.dataset.toggle] = !st.collapsed[t.dataset.toggle]; render(); return; }
      if (t.dataset.filter) { st.filter = st.filter === t.dataset.filter ? null : t.dataset.filter; render(); return; }
      if (t.dataset.act) {
        const act = t.dataset.act, arg = t.dataset.arg;
        if (act === 'ftl') { if (opts.onOpenFtl) opts.onOpenFtl(); return; }
        if (opts.readOnly) return;
        if (act === 'fund' && opts.onFund) opts.onFund(arg);
        else if (act === 'endeavour' && opts.onEndeavour) opts.onEndeavour(arg);
        else if (act === 'stop' && opts.onStopEndeavour) opts.onStopEndeavour();
        return;
      }
      if (t.dataset.sel) select(t.dataset.sel);
    }
    root.addEventListener('click', onClick);
    return { render, select, get selected() { return st.sel; }, destroy() { root.removeEventListener('click', onClick); root.remove(); }, root };
  }

  const API = { create, GLYPH, esc };
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
  G.UHScreen = API;
})(typeof window !== 'undefined' ? window : globalThis);
