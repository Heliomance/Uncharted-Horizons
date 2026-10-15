// Research screen mockup (Uncharted Horizons). Data: one simulated late game, corrected (see build_data.py), with the
// player-facing text of every breakthrough. Views: a1 turn 226; a2 the whole board; a3 a Grand Endeavour at turn 231;
// a3b switching away from it; a4 one focus chosen.
const D = __DATA__;
const EO = ['Primitive', 'Ancient', 'Classical', 'Medieval', 'Early Modern', 'Modern', 'Atomic', 'Space'];
const AB = { Primitive: 'Prim', Ancient: 'Anc', Classical: 'Class', Medieval: 'Med', 'Early Modern': 'E.Mod', Modern: 'Mod', Atomic: 'Atom', Space: 'Space' };
const VIEWS = {
  a1: { snap: 't226', sel: { kind: 'row', id: 'EL11' } },
  a2: { snap: 't226', sel: { kind: 'row', id: 'EL11' }, whole: true },
  a3: { snap: 't231', sel: { kind: 'row', id: 'EL11' } },
  a3b: { snap: 't231', sel: { kind: 'row', id: 'EL11' }, popup: { kind: 'switch', focus: 'Quantum Physics' } },
  a4: { snap: 't226', sel: { kind: 'focus', id: 'Energy Systems' }, focusView: 'Energy Systems' },
};
const FONT = "'DejaVu Sans UH','DejaVu Sans',sans-serif";
const CH_UP = 'M2 6.5l3-3 3 3', CH_DOWN = 'M2 3.5l3 3 3-3', CH_RIGHT = 'M3.5 2l3 3-3 3';

// desktop at Unciv's Large size, and a phone at Unciv's Small size (landscape) with 44-px touch targets
const DESK = { w: 1440, h: 810, left: 252, chipH: 22, chipR: 11, closedR: 4, rowH: 20, segH: 30, runLH: 22, gapY: 3, gapX: 4, runGap: 14, secH: 24, btnW: 290, btnH: 50, barH: 121 };
const PHONE = { w: 1300, h: 600, left: 300, chipH: 36, chipR: 18, closedR: 6, rowH: 44, segH: 36, runLH: 36, gapY: 8, gapX: 8, runGap: 16, secH: 30, btnW: 240, btnH: 46, barH: 110 };
const chipBase = M => 'display:inline-flex;align-items:center;gap:5px;height:' + M.chipH + 'px;box-sizing:border-box;font-size:14px;line-height:1;white-space:nowrap;';
const radius = (css, M, st) => css.replace('border-radius:11px', 'border-radius:' + M.chipR + 'px').replace('border-radius:4px', 'border-radius:' + M.closedR + 'px');
const BODY = {
  owned: 'background:#FFD700;border:1.5px solid #B3B3B3;border-radius:11px;color:#6B4300;',
  studying: 'background:#4893AF;border:1.5px solid #B3B3B3;border-radius:11px;color:#000033;',
  waiting: 'background:#0E5C56;border:1.5px dashed #FFFFFF;border-radius:11px;color:#FFFFFF;',
  unreach: 'background:transparent;border:1.5px dashed #B3B3B3;border-radius:11px;color:#FFFFFF;',
  closed: 'background:#111111;border:1.5px dotted #B3B3B3;border-radius:4px;color:#B3B3B3;',
  not_taken: 'background:transparent;border:1.5px dashed #6A6A8C;border-radius:11px;color:#9C9CB4;',
  endeavour: 'background:#334D80;border:2px solid #FFFFFF;border-radius:11px;color:#FFFFFF;',
};
const ERA_TAG = {
  studying: 'background:rgba(0,0,51,0.78);color:#FFFFFF;',
  waiting: 'background:rgba(0,0,0,0.55);color:#FFFFFF;',
  unreach: 'background:rgba(255,255,255,0.16);color:#FFFFFF;',
  closed: 'background:rgba(255,255,255,0.13);color:#B3B3B3;',
  endeavour: 'background:rgba(0,0,0,0.45);color:#FFFFFF;',
};
const TAG = {
  New: 'background:#FFFFFF;color:#000033;', Rare: 'background:#7F3200;color:#FFFFFF;', Unique: 'background:#3F1046;color:#FFFFFF;',
  'Dead end': 'background:#6B4300;color:#FFD700;', Superseded: 'background:#252B3E;color:#FFFFFF;', FTL: 'background:#334D80;color:#FFFFFF;',
  'Path not taken': 'background:#252B3E;color:#FFFFFF;', Endeavour: 'background:#FFFFFF;color:#000033;',
};
const TAG_BASE = 'display:inline-flex;align-items:center;height:16px;border-radius:8px;padding:0 6px;font-size:14px;line-height:1;white-space:nowrap;';
const STATUS_LABEL = { owned: 'Owned', studying: 'Being studied', waiting: 'Awaiting the idea', unreach: 'Not yet reachable', closed: 'Moment passed', not_taken: 'Path not taken', endeavour: 'Grand Endeavour' };
const SECTIONS = [
  { st: 'endeavour', title: 'Grand Endeavour', why: 'takes the funded share until it is complete; it cannot fail' },
  { st: 'studying', title: 'Being studied', why: 'revealed, its idea has occurred: each takes a share of its focus’s Insight every turn' },
  { st: 'waiting', title: 'Awaiting the idea', why: 'revealed, not yet occurred: no Insight until the idea occurs, and it still may' },
  { st: 'unreach', title: 'Not yet reachable', why: 'revealed: a prerequisite must be discovered first' },
  { st: 'closed', title: 'Moment passed', why: 'revealed, its window closed: only an Endeavour is certain' },
];
const ORD = n => ['', '1st', '2nd', '3rd', '4th', '5th', '6th', '7th'][n] || n + 'th';
const fmt = n => Math.round(n).toLocaleString('en-GB');
const bandColours = (era, cur) => {
  const d = EO.indexOf(era) - EO.indexOf(cur);
  return d < 0 ? 'background:#FFAF00;color:#782E10;' : d === 0 ? 'background:#0E5C56;color:#FFFFFF;' : 'background:#111111;color:#FFFFFF;';
};
const BTN = M => 'width:' + M.btnW + 'px;height:' + M.btnH + 'px;flex:none;border-radius:20px;color:#FFFFFF;text-align:center;padding:0 13px 0 12px;box-sizing:border-box;display:flex;flex-direction:column;align-items:center;justify-content:center;';

class Component extends DCLogic {
  constructor(props) {
    super(props);
    const v = VIEWS[(props && props.view) || 'a1'] || VIEWS.a1, s = D.snap[v.snap], ph = props && props.phone && props.phone !== 'false';
    this.state = { view: (props && props.view) || 'a1', snap: v.snap, sel: ph ? { kind: 'row', id: 'QP06' } : v.sel, focusView: v.focusView || null, filter: null, collapsed: {},
      funded: s.funded, queue: s.queue.slice(), endeavour: s.endeavour ? Object.assign({}, s.endeavour) : null, popup: v.popup || null };
  }

  // ---------------------------------------------------------------- data access
  snapData() { return D.snap[this.state.snap]; }
  rowsNow() {
    const S = this.snapData(), en = this.state.endeavour;
    return S.rows.map(r => Object.assign({}, D.rows[r.id], r, { status: en && en.id === r.id && !en.aside ? 'endeavour' : r.status }));
  }
  rowById(id) { return this.rowsNow().find(r => r.id === id); }
  ownedIds() { return new Set(this.rowsNow().filter(r => r.status === 'owned').map(r => r.id)); }
  price(r) { const p = D.prices[r.era] || 0; return { price: p, turns: Math.max(1, Math.round(p / this.share())) }; }
  insight() { return this.snapData().insight; }
  share() { return Math.round(this.insight() * 0.8); }
  spread() { return Math.round(this.insight() * 0.2); }

  // ---------------------------------------------------------------- actions
  select(sel) { this.setState({ sel: sel }); }
  openFocus(f) { this.setState({ sel: { kind: 'focus', id: f }, focusView: f }); }
  fund(f) {
    const en = this.state.endeavour;
    if (en && !en.aside) { this.setState({ popup: { kind: 'switch', focus: f } }); return; }
    this.setState({ funded: f, queue: this.state.queue.filter(q => q !== f) });
  }
  toggleQueue(f) {
    const q = this.state.queue;
    if (f === this.state.funded) return;
    this.setState({ queue: q.includes(f) ? q.filter(x => x !== f) : q.concat([f]) });
  }
  moveQueue(f, d) {
    const q = this.state.queue.slice(), i = q.indexOf(f), j = i + d;
    if (i < 0 || j < 0 || j >= q.length) return;
    q[i] = q[j]; q[j] = f; this.setState({ queue: q });
  }
  beginEndeavour(id) {
    const r = this.rowById(id), p = this.price(r).price, f = this.state.funded;
    this.setState({ endeavour: { id: id, pct: 0, paid: 0, price: p, committed: this.snapData().turn }, funded: null,
      queue: f ? [f].concat(this.state.queue.filter(x => x !== f)) : this.state.queue, popup: null, sel: { kind: 'row', id: id } });
  }
  stopEndeavour(fundFocus) {
    const en = this.state.endeavour, q = this.state.queue;
    const next = fundFocus || q[0] || null;
    this.setState({ endeavour: Object.assign({}, en, { aside: true }), funded: next, queue: q.filter(x => x !== next), popup: null });
  }

  // ---------------------------------------------------------------- view model
  renderVals() {
    const st = this.state, S = this.snapData(), rows = this.rowsNow(), byId = {}, owned = this.ownedIds();
    rows.forEach(r => { byId[r.id] = r; });
    const view = VIEWS[st.view] || VIEWS.a1, whole = !!view.whole, cur = S.era, phone = !!(this.props && this.props.phone && this.props.phone !== 'false'), M = phone ? PHONE : DESK;
    const en = st.endeavour && !st.endeavour.aside ? st.endeavour : null;
    const sel = st.sel || {}, selRow = sel.kind === 'row' ? byId[sel.id] : null;
    const prereqOfSel = new Set(selRow && selRow.needs ? selRow.needs.filter(n => n.ref).map(n => n.ref) : []);
    const fv = st.focusView;
    const inFocus = r => !fv || r.focus === fv || (r.also || []).includes(fv);

    const chipOf = (r, card) => {
      const live = r.status !== 'owned' && r.status !== 'not_taken';
      const tags = (r.tags || []).map(t => ({ text: t === 'Unique' ? '★ Unique' : t, style: TAG_BASE + (TAG[t] || TAG.Superseded) }));
      if (r.status === 'not_taken') tags.push({ text: 'Path not taken', style: TAG_BASE + TAG['Path not taken'] });
      if (r.status === 'endeavour' && en) tags.push({ text: 'Endeavour ' + en.pct + '%', style: TAG_BASE + TAG.Endeavour });
      const lead = r.status === 'owned' ? 9 : 3, trail = (live || tags.length) ? 3 : 9;
      let over = '';
      if (sel.kind === 'row' && sel.id === r.id) over = 'outline:2px solid #FFFFFF;outline-offset:2px;';
      else if (prereqOfSel.has(r.id)) over = 'outline:1.5px dashed #FFFFFF;outline-offset:2px;';
      const style = chipBase(M) + radius(BODY[r.status], M) + 'padding:0 ' + (phone ? trail + 4 : trail) + 'px 0 ' + (phone ? lead + 4 : lead) + 'px;' + over;
      const cardStyle = 'display:flex;flex-direction:column;justify-content:center;gap:2px;height:' + (phone ? 60 : 50) + 'px;box-sizing:border-box;font-size:14px;line-height:1.2;text-align:left;min-width:0;padding:0 10px;' +
        BODY[r.status].replace('border-radius:11px', 'border-radius:15px') + over;
      const g = { studying: r.status === 'studying', waiting: r.status === 'waiting', unreach: r.status === 'unreach', closed: r.status === 'closed', notTaken: r.status === 'not_taken', endeavour: r.status === 'endeavour' };
      const eraStyle = TAG_BASE + 'border-radius:4px;padding:0 4px;' + (ERA_TAG[r.status] || '');
      const home = fv && r.focus !== fv ? ' · home: ' + r.focus : '';
      const line2 = (r.status === 'owned' || r.status === 'not_taken' ? (r.fx || '') : (r.conj ? '“' + r.conj + '”' : '')) + home;
      return { name: r.name, style: style, cardStyle: cardStyle, g: g, tags: tags, era: { show: live, text: AB[r.era], style: eraStyle },
        line2: line2, line2Style: 'display:block;height:18px;line-height:18px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;opacity:0.92',
        aria: r.name + ' — ' + STATUS_LABEL[r.status] + ' — ' + r.focus + ', ' + r.era + ' era' + (tags.length ? ' — ' + tags.map(t => t.text).join(', ') : ''),
        onClick: () => this.select({ kind: 'row', id: r.id }) };
    };
    const runsOf = (list, order) => {
      const by = {};
      list.forEach(r => { (by[r.focus] = by[r.focus] || []).push(r); });
      return Object.keys(by).sort().map(f => {
        const isF = f === st.funded, isSel = sel.kind === 'focus' && sel.id === f;
        return { label: f, aria: 'Show the ' + f + ' focus',
          labelStyle: 'flex:none;height:' + M.runLH + 'px;line-height:' + M.runLH + 'px;padding:0 6px 0 7px;font-size:14px;white-space:nowrap;border-left:2px solid ' + (isF ? '#4893AF' : '#334D80') + ';color:' + (isF || isSel ? '#FFFFFF' : '#B3B3B3') + ';' + (isSel ? 'box-shadow:inset 0 0 0 1px #FFFFFF;' : ''),
          onSelect: () => this.openFocus(f), chips: by[f].sort(order).map(r => chipOf(r)) };
      });
    };
    const byEraName = (a, b) => EO.indexOf(a.era) - EO.indexOf(b.era) || a.name.localeCompare(b.name);
    const toggle = key => () => { const c = Object.assign({}, st.collapsed); c[key] = !c[key]; this.setState({ collapsed: c }); };

    // sections
    const visible = rows.filter(inFocus);
    const counts = {}; visible.forEach(r => { counts[r.status] = (counts[r.status] || 0) + 1; });
    const sections = SECTIONS.filter(s => (counts[s.st] || 0) > 0 && (!st.filter || st.filter === s.st)).map(s => {
      const list = visible.filter(r => r.status === s.st), open = !st.collapsed[s.st];
      return { title: s.title, count: list.length, why: s.why, expandedStr: open ? 'true' : 'false', chevron: open ? CH_DOWN : CH_RIGHT,
        onToggle: toggle(s.st), g: { endeavour: s.st === 'endeavour', studying: s.st === 'studying', waiting: s.st === 'waiting', unreach: s.st === 'unreach', closed: s.st === 'closed' },
        showRuns: open && !fv, showCards: open && !!fv, runs: fv ? [] : runsOf(list, byEraName), cards: fv ? list.sort(byEraName).map(r => chipOf(r, true)) : [] };
    });
    const hist = visible.filter(r => r.status === 'owned' || r.status === 'not_taken');
    const ownOpen = !st.collapsed.owned;
    const bands = EO.slice().reverse().map(e => {
      const list = hist.filter(r => r.era === e);
      if (!list.length) return null;
      const key = 'band:' + e, open = !st.collapsed[key];
      const order = (a, b) => (a.status === 'not_taken') - (b.status === 'not_taken') || (a.turn || 0) - (b.turn || 0) || a.name.localeCompare(b.name);
      return { label: e + ' era', count: list.filter(r => r.status === 'owned').length + (list.some(r => r.status === 'not_taken') ? ' owned' : ''),
        expandedStr: open ? 'true' : 'false', onToggle: toggle(key),
        style: 'display:flex;align-items:center;width:100%;height:24px;box-sizing:border-box;border:1px solid #FFFFFF;padding-left:10px;font-size:18px;margin:6px 0 5px;' + bandColours(e, cur),
        showRuns: open && !fv, showCards: open && !!fv, runs: fv ? [] : runsOf(list, order), cards: fv ? list.sort(order).map(r => chipOf(r, true)) : [] };
    }).filter(Boolean);
    const nOwned = hist.filter(r => r.status === 'owned').length, notTaken = hist.length - nOwned;
    const tally = t => hist.filter(r => (r.tags || []).includes(t)).length;
    const whyBits = ['newest era first'];
    if (notTaken) whyBits.push(notTaken + (notTaken > 1 ? ' paths' : ' path') + ' not taken');
    [['Unique', 'unique'], ['Rare', 'rare'], ['Superseded', 'superseded'], ['Dead end', 'dead end']].forEach(([t, w]) => { const n = tally(t); if (n) whyBits.push(n + ' ' + w); });
    const ownedVM = { show: hist.length > 0 && (!st.filter || st.filter === 'owned'), count: nOwned, why: whyBits.join(' · '), expanded: ownOpen,
      expandedStr: ownOpen ? 'true' : 'false', chevron: ownOpen ? CH_DOWN : CH_RIGHT, onToggle: toggle('owned'), bands: bands };

    // status filter segments (counts cover shown rows only)
    const SEG = [['studying', 'Being studied'], ['waiting', 'Awaiting the idea'], ['unreach', 'Not yet reachable'], ['closed', 'Moment passed'], ['owned', 'Owned']];
    const segs = SEG.map(([k, label]) => {
      const on = st.filter === k;
      return { label: label, aria: label + ': ' + (counts[k] || 0) + (on ? ', showing only these' : ''), count: counts[k] || 0, pressed: on ? 'true' : 'false', g: { studying: k === 'studying', waiting: k === 'waiting', unreach: k === 'unreach', closed: k === 'closed', owned: k === 'owned' },
        style: 'display:flex;align-items:center;gap:6px;height:' + M.segH + 'px;box-sizing:border-box;border-radius:' + M.segH / 2 + 'px;padding:0 ' + (phone ? 12 : 11) + 'px;font-size:14px;white-space:nowrap;color:#FFFFFF;' + (on ? 'background:#334D80;box-shadow:inset 0 0 0 1.5px #FFFFFF;' : 'background:#252B3E;'),
        countStyle: 'color:' + (on ? '#FFFFFF' : '#B3B3B3'), onClick: () => this.setState({ filter: on ? null : k }) };
    });

    // focus list
    const badges = S.badges, q = st.queue;
    const foci = S.foci.map(f => {
      const isF = f === st.funded && !en, qi = q.indexOf(f), isQ = qi >= 0, isSel = sel.kind === 'focus' && sel.id === f;
      const holdsEn = en && byId[en.id] && byId[en.id].focus === f;
      const fill = isF ? 'background:#4893AF;color:#000033;' : isQ ? 'background:#0E5C56;color:#FFFFFF;' : 'color:#FFFFFF;';
      return { name: f, checked: isF ? 'true' : 'false', radioAria: 'Fund ' + f, selectAria: 'Show the ' + f + ' focus',
        rowStyle: 'display:flex;align-items:center;flex:none;height:' + M.rowH + 'px;border-radius:' + M.rowH / 2 + 'px;padding:0 ' + (phone ? 10 : 4) + 'px 0 ' + (phone ? 0 : 3) + 'px;' + fill + (isSel ? 'box-shadow:inset 0 0 0 2px #FFFFFF;' : ''),
        nameStyle: 'flex:1;min-width:0;height:' + M.rowH + 'px;line-height:' + M.rowH + 'px;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:inherit',
        ring: isF ? '#000033' : '#B3B3B3', dot: isF ? '#000033' : 'none',
        onFund: () => this.fund(f), onSelect: () => this.openFocus(f), onQueue: e => { if (e && e.preventDefault) e.preventDefault(); this.toggleQueue(f); },
        showPyramid: !!holdsEn, showNew: (S.newFoci || []).includes(f),
        showBadge: !!badges[f], badge: badges[f] || 0, badgeTitle: (badges[f] || 0) + ' revealed under study that funding ' + f + ' advances',
        badgeStyle: 'margin-left:4px;min-width:18px;height:15px;line-height:15px;box-sizing:border-box;border-radius:7.5px;padding:0 4px;background:#4893AF;color:#000033;text-align:center;flex:none;font-size:12px;' + (isF ? 'box-shadow:0 0 0 1px #000033;' : ''),
        showQueue: isQ, queueNo: qi + (st.funded || en ? 2 : 1), queueTitle: 'queued ' + ORD(qi + (st.funded || en ? 2 : 1)) };
    });

    // funding header
    const fund = { insight: fmt(this.insight()), spread: '20% · ' + fmt(this.spread()), isFocus: !en && !!st.funded, isEndeavour: !!en,
      onClick: () => this.select({ kind: 'funding' }),
      style: 'width:' + (M.left - 16) + 'px;flex:none;display:flex;flex-direction:column;gap:2px;border-radius:10px;padding:0 0 2px 0;' + (sel.kind === 'funding' ? 'box-shadow:0 0 0 2px #FFFFFF;' : '') };
    if (en) { const r = byId[en.id]; fund.name = r ? r.name : ''; fund.right = en.pct + '%'; fund.barFill = 'position:absolute;left:0;top:0;bottom:0;width:' + en.pct + '%;background:#FFFFFF;border-radius:2px'; fund.aria = 'Funding: Grand Endeavour on ' + fund.name + ', ' + en.pct + '% complete'; }
    else if (st.funded) { fund.name = st.funded; fund.right = '80% · ' + fmt(this.share()); fund.aria = 'Funding: ' + st.funded + ', 80%'; }
    else { fund.name = 'Nothing funded'; fund.right = ''; fund.aria = 'Nothing funded'; }

    // era pill (era entered by count)
    const era = { text: S.eraText, aria: S.eraText, onClick: () => this.select({ kind: 'era' }),
      style: 'height:24px;margin-top:3px;box-sizing:border-box;border:1px solid #FFFFFF;background:#0E5C56;color:#FFFFFF;padding:0 10px;font-size:14px;white-space:nowrap;' + (sel.kind === 'era' ? 'box-shadow:0 0 0 2px #FFFFFF;' : '') };

    const fvm = { show: !!fv };
    if (fv) {
      const home = rows.filter(r => r.focus === fv).length, reached = rows.filter(r => r.focus !== fv && (r.also || []).includes(fv)).length;
      Object.assign(fvm, { name: fv, summary: home + ' here' + (reached ? ' · ' + reached + ' reached from other foci' : ''), checked: fv === st.funded && !en ? 'true' : 'false',
        dot: fv === st.funded && !en ? '#FFFFFF' : 'none', radioAria: 'Fund ' + fv, onFund: () => this.fund(fv),
        onBack: () => this.setState({ focusView: null, sel: { kind: 'focus', id: st.funded || fv } }) });
    }

    const h = whole ? D.wholeHeight : M.h;
    const L = {
      leftStyle: 'width:' + M.left + 'px;flex:none;box-sizing:border-box;padding:4px 8px 0 8px;display:flex;flex-direction:column;min-height:0',
      listStyle: 'margin-top:4px;display:flex;flex-direction:column;gap:1px;' + (phone ? 'flex:1;min-height:0;overflow-y:auto;padding-bottom:6px' : ''),
      listRef: el => { if (el && phone && !this._scrolled) { this._scrolled = true; const i = S.foci.indexOf(st.funded || S.foci[0]); el.scrollTop = Math.max(0, (i - 4) * (M.rowH + 1)); } },
      radioStyle: 'width:' + (phone ? 44 : 22) + 'px;height:' + M.rowH + 'px;flex:none;display:flex;align-items:center;justify-content:center',
      topStyle: 'height:' + (phone ? 52 : 46) + 'px;flex:none;box-sizing:border-box;padding:' + (phone ? '8px 16px 0 16px' : '8px 16px 0 16px') + ';display:flex;align-items:flex-start;gap:' + (phone ? 6 : 4) + 'px',
      segLabels: !phone, ftlTop: phone, ftlBottom: !phone,
      ftlTopStyle: 'height:36px;border-radius:18px;background:#334D80;color:#FFFFFF;font-size:14px;padding:0 14px;white-space:nowrap;margin-right:6px',
      secHeadStyle: 'display:flex;align-items:center;height:' + M.secH + 'px;margin-bottom:' + (phone ? 6 : 3) + 'px;white-space:nowrap',
      showWhy: !phone,
      runsStyle: 'display:flex;flex-wrap:wrap;gap:' + M.gapY + 'px ' + M.runGap + 'px;align-items:flex-start;margin-bottom:2px',
      chipsStyle: 'display:flex;flex-wrap:wrap;gap:' + M.gapY + 'px ' + M.gapX + 'px;min-width:0',
      barStyle: 'height:' + M.barH + 'px;flex:none;box-sizing:border-box;padding:0 10px;display:flex',
      leftBtnsStyle: 'width:' + (phone ? 100 : 180) + 'px;flex:none;display:flex;flex-direction:column;gap:6px;padding-top:8px',
      closeStyle: 'width:' + (phone ? 100 : 90) + 'px;height:' + (phone ? 48 : 50) + 'px;border-radius:20px;background:#334D80;color:#FFFFFF;font-size:18px;text-align:center',
      descStyle: 'flex:1;min-width:0;margin:0 10px;box-sizing:border-box;padding:8px 10px;overflow-y:auto',
      actsStyle: 'width:' + M.btnW + 'px;flex:none;display:flex;flex-direction:column;gap:6px;padding-top:' + (phone ? 6 : 8) + 'px',
    };
    return {
      L: L,
      rootStyle: 'width:' + M.w + 'px;height:' + h + 'px;display:flex;position:relative;overflow:hidden;background:#000033;color:#FFFFFF;font-family:' + FONT + ';font-size:14px;line-height:1.25',
      boardStyle: 'flex:1;min-height:0;box-sizing:border-box;padding:0 10px 0 16px;' + (whole ? 'overflow:visible' : 'overflow-y:auto'),
      fund: fund, foci: foci, showHint: !phone && S.foci.length <= 33, segs: segs, era: era, fv: fvm, sections: sections, owned: ownedVM,
      bar: Object.assign({ show: !whole }, this.describe(byId, owned, en, M)), popup: this.popupVM(byId, en),
    };
  }

  // ---------------------------------------------------------------- the bottom bar
  describe(byId, owned, en, M) {
    const st = this.state, S = this.snapData(), sel = st.sel || {}, G = {};
    const b = { g: G, tags: [], lines: [], move: { show: false }, dot: 'none',
      primary: { show: false, disabled: false, l1: '', l2: '', style: '', onClick: null }, secondary: { show: false, disabled: false, l1: '', l2: '', style: '', onClick: null } };
    const line = (parts, extra) => b.lines.push({ style: 'line-height:19px;' + (extra || ''), parts: parts.map(p => typeof p === 'string' ? { text: p, style: '' } : p) });
    const grey = t => line([{ text: t, style: 'color:#B3B3B3' }]);
    const act = (slot, l1, l2, onClick, disabled) => { b[slot] = { show: true, disabled: !!disabled, l1: l1, l2: l2 || '', onClick: onClick || null,
      style: BTN(M) + 'background:' + (disabled ? '#252B3E' : '#334D80') + ';cursor:' + (disabled ? 'default' : 'pointer') + ';' }; };
    const needsLine = (r, lead) => {
      if (!r.needs || !r.needs.length) return;
      const parts = [lead || 'Needs '];
      r.needs.forEach((n, i) => {
        if (i) parts.push(n.alt && r.needs[i - 1].alt ? ' or ' : ' + ');
        const met = n.ref ? owned.has(n.ref) : true;
        parts.push({ text: met ? '✓ ' : '✗ ', style: 'color:' + (met ? '#65DC72' : '#FF6B6B') });
        let t = n.label;
        if (!met && n.ref && byId[n.ref] && byId[n.ref].status === 'studying') t += ' (under study in ' + byId[n.ref].focus + ')';
        parts.push(t);
      });
      line(parts);
    };
    const quote = t => t && grey('“' + t + '”');
    const enBtn = r => {
      const p = (r.id === (en && en.id)) ? null : this.price(r);
      act('secondary', en ? 'Replace the Endeavour' : 'Begin Grand Endeavour', fmt(p.price) + ' Insight · about ' + p.turns + (p.turns === 1 ? ' turn' : ' turns'),
        () => this.setState({ popup: { kind: en ? 'replace' : 'begin', id: r.id } }));
    };

    if (sel.kind === 'row' && byId[sel.id]) {
      const r = byId[sel.id], fundedHere = r.focus === st.funded && !en;
      G[{ owned: 'owned', studying: 'studying', waiting: 'waiting', unreach: 'unreach', closed: 'closed', not_taken: 'notTaken', endeavour: 'endeavour' }[r.status]] = true;
      b.title = r.name;
      b.meta = r.focus + ' · ' + r.era + ' era' + (r.status === 'endeavour' ? ' · Grand Endeavour' : '') + (r.also && r.also.length ? ' · also reached by ' + r.also.join(', ') : '');
      b.tags = (r.tags || []).filter(t => t === 'New').map(t => ({ text: t, style: TAG_BASE + TAG[t] + 'margin-left:8px' }));
      const src = r.src ? r.src + '. ' : '';
      if (r.status === 'owned') {
        line(['Discovered on turn ' + r.turn + '. ' + (r.fx || '')]);
        if (r.fx2) line([r.fx2]);
        if (r.opens) line(['Opens the ' + r.opens + ' focus.']);
        if ((r.tags || []).includes('Superseded')) line(['Superseded by ' + r.by + ': its buildings are no longer available.']);
        if ((r.tags || []).includes('Dead end')) line(['Dead end: Mechanical Equivalent of Heat reported that heat is motion, not a fluid.']);
        if ((r.tags || []).includes('Unique')) line(['Unique to your civilisation: it cannot be traded or stolen, and never diffuses.']);
        if ((r.tags || []).includes('Rare')) line(['A rare find.']);
        needsLine(r);
        if ((r.tags || []).includes('FTL')) line(['This bore on the question of how to exceed the speed of light.']);
        if (r.flav) grey(r.flav);
        act('primary', 'Discovered', '', null, true);
        if ((r.tags || []).includes('FTL')) act('secondary', 'Open the FTL screen', '', null, false);
      } else if (r.status === 'studying') {
        line([fundedHere ? 'Being studied in ' + r.focus + ', which you fund: it takes Insight every turn.' : 'Being studied in ' + r.focus + ': it takes a share of that focus’s Insight every turn.']);
        if (r.competes) line(['Competes with ' + r.competes + ', also under study: if that comes first, this is never developed.']);
        needsLine(r);
        quote(r.conj);
        if (fundedHere) act('primary', 'Funded', '', null, true); else act('primary', 'Fund ' + r.focus, '', () => this.fund(r.focus));
        enBtn(r);
      } else if (r.status === 'waiting') {
        line([src + 'Awaiting the idea: no Insight, however hard ' + r.focus + ' is funded, until the idea occurs.']);
        needsLine(r, 'Needs ');
        if (r.competes) line(['Competes with ' + r.competes + ', under study: if that comes first, this is never developed.']);
        quote(r.conj);
        act('primary', 'Experiment', '300 Gold · Scientific Method', null, false);
        enBtn(r);
      } else if (r.status === 'unreach') {
        line([src + 'Not yet reachable: a prerequisite must be discovered first.']);
        needsLine(r);
        line(['It cannot be a Grand Endeavour until ' + (r.needs_name || 'its prerequisites') + ' ' + (r.needs_name ? 'is' : 'are') + ' discovered.']);
        quote(r.conj);
        if (r.needs_focus) act('primary', 'Fund ' + r.needs_focus, '', () => this.fund(r.needs_focus)); else act('primary', 'Not yet reachable', '', null, true);
        act('secondary', 'Grand Endeavour', 'needs ' + (r.needs_name || 'a prerequisite') + ' first', null, true);
      } else if (r.status === 'closed') {
        line([src + 'Its moment passed — only an Endeavour is certain. It takes no Insight now.']);
        needsLine(r);
        const p = this.price(r), ahead = EO.indexOf(r.era) > EO.indexOf(S.devEra);
        line(['As an Endeavour: ' + fmt(p.price) + ' Insight, twice today’s price' + (ahead ? ', falling as development catches up.' : '; about ' + p.turns + (p.turns === 1 ? ' turn' : ' turns') + ' at ' + fmt(this.share()) + ' a turn.')]);
        quote(r.conj);
        act('primary', 'Synthesis', 'once this era · unused', null, false);
        enBtn(r);
      } else if (r.status === 'not_taken') {
        line([src + 'Path not taken: ' + r.instead + ' was discovered first, so this will never be developed.']);
        grey('A thing your civilisation glimpsed and let slip.');
        quote(r.conj);
        act('primary', 'Never developed', '', null, true);
      } else if (r.status === 'endeavour') {
        line([en.pct + '% complete — ' + fmt(en.paid) + ' of ' + fmt(en.price) + ' Insight; about ' + Math.max(1, Math.ceil((en.price - en.paid) / this.share())) + ' more turns at ' + fmt(this.share()) + ' a turn. It cannot fail.']);
        line(['It takes the funded share; the 20% spread still reaches your other foci.']);
        line(['Milestones at 25%, 50% and 75% may bring spin-offs. Committed on turn ' + en.committed + '.']);
        grey('Stopping it lets its progress decay slowly; you can resume it later.');
        act('primary', 'Endeavour under way', en.pct + '%', null, true);
        act('secondary', 'Stop the Endeavour', '', () => this.setState({ popup: { kind: 'stop' } }));
      }
    } else if (sel.kind === 'focus') {
      const f = sel.id, isF = f === st.funded && !en, qi = st.queue.indexOf(f);
      G.focus = true; b.dot = isF ? '#FFFFFF' : 'none'; b.title = f;
      b.meta = isF ? 'funded · 80% of your Insight' : 'not funded' + (qi >= 0 ? ' · queued ' + ORD(qi + (st.funded || en ? 2 : 1)) : '');
      const studying = Object.values(byId).filter(r => r.status === 'studying' && (r.focus === f || (r.also || []).includes(f))).map(r => r.name);
      line([studying.length ? 'Under study here: ' + studying.join(', ') + '.' : 'Nothing revealed is under study here.']);
      const mods = (D.mods[f] || []).concat(D.mods['*'] || []);
      line(['Tends to help with ' + (D.help[f] || 'a little of everything') + '.' + (mods.length ? ' Modifiers: ' + mods.join(', ') + '.' : '')]);
      if (qi >= 0) line(['Queued ' + ORD(qi + (st.funded || en ? 2 : 1)) + ': funding moves here when ' + (st.funded || 'the Endeavour') + ' has no revealed work under study.']);
      grey('Switching loses nothing: every breakthrough keeps its progress.');
      if (qi >= 0) b.move = { show: true, upAria: 'Move ' + f + ' up the queue', downAria: 'Move ' + f + ' down the queue', onUp: () => this.moveQueue(f, -1), onDown: () => this.moveQueue(f, 1) };
      if (isF) act('primary', 'Funded', '', null, true); else act('primary', 'Fund ' + f, en ? 'sets the Endeavour aside' : '', () => this.fund(f));
      if (!isF) act('secondary', qi >= 0 ? 'Remove from queue' : 'Add to queue', '', () => this.toggleQueue(f));
    } else if (sel.kind === 'funding') {
      G.insight = true; b.title = 'Insight'; b.meta = fmt(this.insight()) + ' a turn, equal to your science';
      line([(en ? 'The Endeavour takes 80% (' : '80% (') + fmt(this.share()) + ') ' + (en ? '' : 'goes to the funded focus, ') + 'since Specialization of Labor; before it, 50%.']);
      line(['The other 20% (' + fmt(this.spread()) + ') spreads to foci with work under study. Switching loses nothing.']);
      const qs = st.queue.map((f, i) => (i + (st.funded || en ? 2 : 1)) + ' ' + f).join(', ');
      line(['Queue: ' + (qs || 'empty') + '. It moves on when the funded focus has no revealed work under study.']);
      line(['Diffusion: after the press (Printing Press). Theories reveal their applications (Scientific Method).']);
      line(['Abilities: Experiment (Scientific Method) · Synthesis (Dialectical Thinking), unused this era.']);
      act('primary', en ? 'Grand Endeavour' : 'Funded: ' + st.funded, '', null, true);
    } else if (sel.kind === 'era') {
      b.title = S.era + ' era'; b.meta = 'entered by count';
      S.eraLines.forEach(t => line([t]));
    }
    return b;
  }

  popupVM(byId, en) {
    const p = this.state.popup;
    if (!p) return { show: false, ok: {}, cancel: {} };
    const keep = { label: 'Keep the Endeavour', onClick: () => this.setState({ popup: null }) };
    if (p.kind === 'switch') {
      const r = byId[en.id];
      return { show: true, title: 'Fund ' + p.focus + ' instead?', body: 'The ' + r.name + ' Endeavour stops at ' + en.pct + '%. Its progress then decays slowly, and you can resume it later.',
        ok: { label: 'Fund ' + p.focus, onClick: () => this.stopEndeavour(p.focus) }, cancel: keep };
    }
    if (p.kind === 'stop') {
      return { show: true, title: 'Stop the Endeavour?', body: 'Its progress decays slowly; you can resume it later. Funding goes to ' + (this.state.queue[0] || 'no focus') + '.',
        ok: { label: 'Stop the Endeavour', onClick: () => this.stopEndeavour(null) }, cancel: keep };
    }
    const r = byId[p.id], pr = this.price(r), f = this.state.funded;
    const body = (p.kind === 'replace' ? 'Replace the Endeavour on ' + byId[en.id].name + '? It stops at ' + en.pct + '%; its progress decays slowly, and you can resume it later. ' : '') +
      'A Grand Endeavour on ' + r.name + ' takes the funded share, ' + fmt(this.share()) + ' a turn, for about ' + pr.turns + (pr.turns === 1 ? ' turn' : ' turns') + ': ' + fmt(pr.price) + ' Insight in all. It cannot fail.' + (f ? ' ' + f + ' goes back to the head of the queue.' : '');
    return { show: true, title: p.kind === 'replace' ? 'Replace the Endeavour?' : 'Begin a Grand Endeavour?', body: body,
      ok: { label: 'Begin Grand Endeavour', onClick: () => this.beginEndeavour(p.id) }, cancel: p.kind === 'replace' ? keep : { label: 'Cancel', onClick: () => this.setState({ popup: null }) } };
  }
}
