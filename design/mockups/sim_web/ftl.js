/* ftl.js: the Faster than light screen, drawn from a view model (view.js ftlModel). Plain DOM, no framework.

   const ftl = UHFtl.create(container, {
     readOnly,            // true: commit buttons are shown but disabled (the replay viewer)
     onCommit(method),    // the player commits to a prototype of a proposed, standing hypothesis whose build is complete
     onClose(),           // optional: a Close button (the live game's FTL screen as an overlay)
   });
   ftl.render(vm);
   ftl.destroy();

   Section 4: the hypotheses proposed so far, each with its questions (open, awaiting an instrument, confirmed, disproved)
   and its build needs, each open item with a hint of the focus where progress is possible now; the closing statement;
   the running results list; and the prototype, SS FTL Drive and victory. Facts only: no odds, no advice. */
(function (G) {
  'use strict';
  const V = G.UHView;
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const MARK = { holds: ['✓', 'is-ok', 'Holds'], fails: ['✗', 'is-no', 'Does not hold'], awaiting: ['…', 'is-wait', 'Awaiting its instrument'],
    open: ['?', 'is-open', 'Open'], silent: ['?', 'is-open', 'No answer'] };
  const STANDING = { standing: 'Standing', ruled_out: 'Ruled out', confirmed: 'Confirmed', only: 'The only one left' };

  function create(container, opts) {
    opts = opts || {};
    const root = document.createElement('div');
    root.className = 'uh-ftl';
    container.appendChild(root);
    let last = null;

    function question(q, live) {
      const m = MARK[q.state] || MARK.open;
      let sub = '';
      if (q.state === 'holds' || q.state === 'fails') sub = (q.state === 'holds' ? 'Confirmed' : 'Disproved') + ' on turn ' + q.turn + (q.instrument ? ', by the ' + q.instrument : '') + '.';
      else if (q.state === 'awaiting') sub = 'To settle this unanswered question, we’ll need to build ' + (q.instrument ? 'a ' + q.instrument : 'its instrument') + ': ' + V.turns(q.turnsLeft) + ' left.';
      else if (q.state === 'silent') sub = 'No answer has come.';
      else if (live && q.hint) sub = 'Progress is possible now in ' + q.hint.label + '.';
      else if (live) sub = 'No step towards it can be worked on now.';
      const tested = q.hosts.length ? '<span class="ftl-host">Tested by ' + esc(q.hosts.map(h => h.name).join(' or ')) + (q.merged ? ', which the build needs' : '') + '</span>' : (q.merged ? '<span class="ftl-host">Tested by building it</span>' : '');
      const eng = q.truth != null ? '<span class="ftl-eng">engine: ' + (q.truth ? 'holds' : 'does not hold') + '</span>' : '';
      return '<li class="ftl-q ' + m[1] + '"><span class="ftl-mark" aria-label="' + m[2] + '">' + m[0] + '</span><span class="ftl-qbody"><span class="ftl-qtext">' + esc(q.text) + '</span>' +
        (sub ? '<span class="ftl-sub">' + esc(sub) + '</span>' : '') + tested + eng + '</span></li>';
    }
    function need(b, live) {
      let name;
      if (b.met) name = b.power ? b.label + ' (' + b.metName + ')' : b.metName;
      else if (b.power) name = b.label;
      else {
        const named = b.options.filter(Boolean).map(o => o.name);
        name = named.length ? named.join(' or ') : 'A breakthrough not yet revealed';
      }
      const sub = !b.met && live ? (b.hint ? 'Progress is possible now in ' + b.hint.label + '.' : 'No step towards it can be worked on now.') : '';
      return '<li class="ftl-q ' + (b.met ? 'is-ok' : 'is-open') + '"><span class="ftl-mark" aria-label="' + (b.met ? 'Met' : 'Not yet met') + '">' + (b.met ? '✓' : '✗') + '</span><span class="ftl-qbody"><span class="ftl-qtext">' +
        esc(name) + '</span>' + (sub ? '<span class="ftl-sub">' + esc(sub) + '</span>' : '') + '</span></li>';
    }
    function proto(h) {
      const p = h.prototype, ro = !!opts.readOnly;
      if (p.state === 'running') return '<div class="ftl-proto is-running"><span>Prototype under way: ' + Math.round(100 * p.progress) + '%</span><span class="uh-meter"><span style="width:' + Math.round(100 * p.progress) + '%"></span></span></div>';
      if (p.state === 'failed') return '<div class="ftl-proto is-failed"><span>The prototype failed: this method is proven invalid.</span></div>';
      if (p.state === 'worked') return '<div class="ftl-proto is-worked"><span>The prototype works.</span></div>';
      const can = p.canCommit && !ro;
      const price = p.cost ? V.fmt(p.cost) + ' Insight' + (p.turns ? ' · about ' + V.turns(p.turns) : '') : '';
      return '<div class="ftl-proto"><button type="button" class="uh-act" data-commit="' + esc(h.method) + '"' + (can ? '' : ' disabled') + '><span class="uh-act-l1">Commit to a prototype</span><span class="uh-act-l2">' +
        esc(p.canCommit ? price : p.reason) + '</span></button>' + (p.canCommit && h.standing === 'standing' ? '<span class="ftl-note">Not yet certain: committing now is a Hail Mary.</span>' : '') + '</div>';
    }
    function hyp(h) {
      const live = h.proposed && h.standing !== 'ruled_out';
      if (h.proposed && h.standing === 'ruled_out') {   // a dead end is signposted plainly: the result that disproved it, nothing more
        const why = h.questions.filter(q => q.state === 'fails').map(q => question(q, false)).join('') ||
          (h.prototype.state === 'failed' ? '<li class="ftl-q is-no"><span class="ftl-mark">✗</span><span class="ftl-qbody"><span class="ftl-qtext">Its prototype failed.</span></span></li>' : '');
        return '<article class="ftl-hyp st-ruled_out' + (h.isTrue ? ' is-true' : '') + '"><header class="ftl-hyp-head"><h3>' + esc(h.title) + '</h3><span class="ftl-standing">Ruled out' +
          (h.ruledTurn ? ' · turn ' + h.ruledTurn : '') + '</span></header><p class="ftl-tagline">' + esc(h.tagline) + '</p><ul class="ftl-list">' + why + '</ul></article>';
      }
      const qs = h.questions.map(q => question(q, live)).join('');
      const bs = h.build.map(b => need(b, live)).join('');
      const st = h.proposed ? STANDING[h.standing] + (h.standing === 'ruled_out' && h.ruledTurn ? ' · turn ' + h.ruledTurn : '') : 'Not yet proposed';
      return '<article class="ftl-hyp st-' + h.standing + (h.proposed ? '' : ' is-unproposed') + (h.isTrue ? ' is-true' : '') + '">' +
        '<header class="ftl-hyp-head"><h3>' + esc(h.title) + '</h3><span class="ftl-standing">' + esc(st) + '</span>' + (h.isTrue ? '<span class="uh-tag tag-hidden">Works (engine)</span>' : '') + '</header>' +
        '<p class="ftl-tagline">' + esc(h.tagline) + (h.proposed ? ' · proposed on turn ' + h.proposedTurn : '') + '</p>' +
        '<div class="ftl-cols"><div><h4>Questions</h4><ul class="ftl-list">' + qs + '</ul></div>' +
        '<div><h4>Build needs <span class="ftl-count">' + h.buildMet + ' of ' + h.buildTotal + '</span></h4><ul class="ftl-list">' + bs + '</ul></div></div>' +
        (h.proposed ? proto(h) : '') + '</article>';
    }
    function slots(vm) {
      const P = vm.projection;
      const row = (label, val, cls) => '<div class="ftl-slot ' + (cls || '') + '"><span class="ftl-slot-label">' + esc(label) + '</span><span class="ftl-slot-val">' + esc(val) + '</span></div>';
      let html = '';
      if (vm.prototype) html += row('Prototype', vm.prototype.method + ': ' + Math.round(100 * (vm.prototype.progress || 0)) + '% built', 'is-on');
      else if (P) html += row('Prototype', P.method + ': committed on turn ' + P.fin + ', works on turn ' + P.proto + ' (' + V.turns(P.protoTurns) + ')', 'is-proj');
      else html += row('Prototype', 'none committed');
      if (vm.drive && vm.drive.done) html += row('SS FTL Drive', vm.drive.method + ': built on turn ' + vm.drive.done, 'is-on');
      else if (vm.drive) html += row('SS FTL Drive', vm.drive.method + ': ' + V.turns(vm.drive.turnsLeft) + ' of building left' + (vm.drive.total ? ' (of ' + vm.drive.total + ')' : ''), 'is-on');
      else if (P) html += row('SS FTL Drive', 'built from Production in ' + V.turns(P.driveTurns) + ', by turn ' + (P.proto + P.driveTurns), 'is-proj');
      else html += row('SS FTL Drive', 'needs a working prototype');
      if (vm.victory) html += row('Victory', 'Launched on turn ' + vm.victory.turn + (vm.victory.reference ? ': ' + (vm.victory.delta === 0 ? 'level with' : V.turns(Math.abs(vm.victory.delta)) + (vm.victory.delta < 0 ? ' sooner than' : ' later than')) + ' base Civ V’s ' + vm.victory.reference : ''), 'is-win');
      else if (P) html += row('Victory', 'launch on turn ' + P.launch + ': ' + (P.vsReference === 0 ? 'level with' : V.turns(Math.abs(P.vsReference)) + (P.vsReference < 0 ? ' sooner than' : ' later than')) + ' base Civ V’s ' + P.reference, 'is-proj is-win');
      else html += row('Victory', 'the ship launches a turn after the Drive is built');
      return '<div class="ftl-slots">' + (P ? '<p class="ftl-proj-note">Projected after the log ends, as victory.py computes it.</p>' : '') + html + '</div>';
    }
    function render(vm) {
      if (vm) last = vm;
      vm = last;
      if (!vm) return;
      const sc = root.querySelector('.ftl-scroll'), top = sc ? sc.scrollTop : 0;
      let body;
      if (!vm.open && !vm.engine) body = '<p class="ftl-statement">' + esc(vm.statement) + '</p><p class="ftl-dim">This screen opens when Relativity is discovered.</p>';
      else {
        const rank = h => !h.proposed ? 2 : h.standing === 'ruled_out' ? 3 : h.standing === 'standing' ? 1 : 0;
        const shown = vm.hypotheses.map((h, i) => [h, i]).sort((a, b) => rank(a[0]) - rank(b[0]) || a[1] - b[1]).map(x => x[0]);
        const eng = vm.engineInfo ? '<div class="ftl-engine">' + '<strong>Engine:</strong> the working method is ' + esc(vm.engineInfo.method || 'unknown') +
          (vm.engineInfo.truth ? '. World truth: ' + esc(vm.engineInfo.truth.map(t => (t.value ? '✓ ' : '✗ ') + t.text).join('; ')) : '') + '.</div>' : '';
        const cert = vm.certain ? '<div class="ftl-certain"><strong>Certain:</strong> ' + esc(vm.certain.method) + ' is the way to outrun light' + (vm.certain.turn ? ' (turn ' + vm.certain.turn + ')' : '') + '.</div>' : '';
        const res = vm.results.length ? '<ol class="ftl-results">' + vm.results.slice().reverse().map(r => '<li class="res-' + esc(r.kind) + '"><span class="ftl-rturn">' + r.turn + '</span><span>' + esc(r.text) + '</span></li>').join('') + '</ol>' : '<p class="ftl-dim">No results yet.</p>';
        body = '<p class="ftl-statement">' + esc(vm.statement) + '</p>' + cert + eng +
          (shown.length ? '<div class="ftl-hyps">' + shown.map(hyp).join('') + '</div>' : '<p class="ftl-dim">Nothing is proposed yet.</p>') +
          '<h3 class="ftl-h">Results <span class="ftl-count">newest first</span></h3>' + res + '<h3 class="ftl-h">Prototype, Drive and launch</h3>' + slots(vm);
      }
      root.className = 'uh-ftl' + (vm.engine ? ' is-engine' : '') + (opts.readOnly ? ' is-readonly' : '');
      root.innerHTML = '<div class="ftl-head"><h2>Faster than light</h2><span class="ftl-turn">Turn ' + vm.turn + '</span>' +
        (opts.onClose ? '<button type="button" class="uh-act ftl-close" data-close="1"><span class="uh-act-l1">Close</span></button>' : '') + '</div>' +
        '<div class="ftl-scroll uh-scroll">' + body + '</div>';
      const sc2 = root.querySelector('.ftl-scroll');
      if (sc2) sc2.scrollTop = top;
    }
    function onClick(e) {
      const t = e.target.closest('button');
      if (!t || !root.contains(t) || t.disabled) return;
      if (t.dataset.close && opts.onClose) { opts.onClose(); return; }
      if (t.dataset.commit && !opts.readOnly && opts.onCommit) opts.onCommit(t.dataset.commit);
    }
    root.addEventListener('click', onClick);
    return { render, destroy() { root.removeEventListener('click', onClick); root.remove(); }, root };
  }

  const API = { create };
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
  G.UHFtl = API;
})(typeof window !== 'undefined' ? window : globalThis);
