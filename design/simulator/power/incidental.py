"""What a racing expert gives up: the breakthroughs a non-racing expert holds that the racer lacks (Tamsin's test, 15 Oct 2026).

Games are paired across settings by their number (the same world truth and seed), from results saved with SAVE_T=1. A game's
finish is the turn its science race is complete (certainty and build both done; victory follows after the prototype and
the Drive, when the simulation has stopped). Two comparisons:
  at the racer's finish: what the non-racer held by that same turn that the racer lacks (the research it diverted);
  at each one's own finish: what the non-racer holds when it is ready that the racer lacked when it was.
Usage: python3 incidental.py <non-racer pattern> <label>=<racer pattern> ...   (patterns name result files
results/w7f_<world><pattern>.json, with {m} for the method), e.g.
  python3 incidental.py _incN_{m} 70/20/10=_incA_{m} 70/10/20=_incB_{m}
"""
import sys, os, re, json, collections, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import gen_data as G
from defaults import TREE

NAME, GIVES = {}, {}
for line in open(TREE, encoding='utf-8'):
    m = re.match(r'^\| ([A-Z][A-Z0-9-]*) \| \*\*(.+?)\*\* \| ', line)
    if m:
        cells = line.rstrip('\n').split(' | ')
        NAME[m.group(1)] = m.group(2); GIVES[m.group(1)] = cells[5] if len(cells) > 5 else ''
WORLDS = {'familiar': ['Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Tunnelling'],
          'Process': ['Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum'], 'Substance': ['Warp', 'Wormhole', 'Hyperspace', 'Tachyonic', 'Plenum']}
EXOTIC = {'Warp', 'Wormhole', 'Plenum'}
ECON = re.compile(r'\b(Production|Gold|Food|Science|Insight|Culture|Happiness|growth|maintenance|Trade Route)\b')   # an effect on the economy
ECONOMIC = {k for k, g in GIVES.items() if ECON.search(g)}


def finish(g):
    return max(g['cert'], g['built']) if g['cert'] and g['built'] else None


def victory(g):   # the expert: prototype 5 turns, Drive 4 (3 for the exotic methods), launch 1 (victory_table.py)
    f = finish(g)
    return f + 5 + (3 if g['m'] in EXOTIC else 4) + 1 if f else None


def held(g, by):
    return {k for k, t in g['t'].items() if t <= by}


def short(text, n=110):
    text = re.sub(r'\s+', ' ', text.replace('**', '')).strip()
    return text if len(text) <= n else text[:n - 1] + '…'


base = sys.argv[1]
for label, pat in (a.split('=', 1) for a in sys.argv[2:]):
    pairs = []
    for w, methods in WORLDS.items():
        for m in methods:
            pn = os.path.join(HERE, 'results', f'w7f_{w}{base.format(m=m)}.json'); pr = os.path.join(HERE, 'results', f'w7f_{w}{pat.format(m=m)}.json')
            if not (os.path.exists(pn) and os.path.exists(pr)): print(f'  (missing {w} {m})'); continue
            pairs += [(w, n, r) for n, r in zip(json.load(open(pn)), json.load(open(pr)))]
    done = [(w, n, r) for w, n, r in pairs if finish(n) and finish(r) and n.get('t') and r.get('t')]
    unf_n = sum(1 for _, n, _ in pairs if not finish(n)); unf_r = sum(1 for _, _, r in pairs if not finish(r))
    print(f'\n{label}: {len(pairs)} paired games ({unf_n} unfinished for the non-racer, {unf_r} for the racer; {len(done)} compared)')
    vn = [victory(n) for _, n, _ in done]; vr = [victory(r) for _, _, r in done]
    print(f'  victory, median: non-racer {st.median(vn):.0f}, racer {st.median(vr):.0f}; the racer is sooner in '
          f'{100 * sum(1 for a, b in zip(vn, vr) if b < a) / len(done):.0f}% of pairs, later in {100 * sum(1 for a, b in zip(vn, vr) if b > a) / len(done):.0f}%')
    miss_same, extra_same, miss_own, extra_own = [], [], [], []
    count_n_same, count_r, count_n_own = [], [], []
    freq = collections.Counter(); by_focus = collections.Counter(); by_era = collections.Counter(); by_tier = collections.Counter()
    gained = collections.Counter(); econ_same, econ_own = [], []
    for w, n, r in done:
        fr, fn = finish(r), finish(n)
        hr = held(r, fr); hn_same = held(n, fr); hn_own = held(n, fn)
        ms = hn_same - hr; miss_same.append(len(ms)); extra_same.append(len(hr - hn_same))
        econ_same.append(len(ms & ECONOMIC)); econ_own.append(len((hn_own - hr) & ECONOMIC))
        for k in hr - hn_same: gained[k] += 1
        miss_own.append(len(hn_own - hr)); extra_own.append(len(hr - hn_own))
        count_n_same.append(len(hn_same)); count_r.append(len(hr)); count_n_own.append(len(hn_own))
        for k in ms:
            freq[k] += 1; row = G.ROWS.get(k, {})
            by_focus[row.get('focus', '?')] += 1; by_era[row.get('era', '?')] += 1; by_tier[row.get('tier', '?')] += 1
    N = len(done)
    print(f'  breakthroughs held at its own finish, median: non-racer {st.median(count_n_own):.0f}, racer {st.median(count_r):.0f}')
    print(f'  at the racer\'s finish, the non-racer held a median {st.median(count_n_same):.0f}')
    print(f'  the racer lacks, of what the non-racer held by the same turn: mean {st.mean(miss_same):.1f}, median {st.median(miss_same):.0f}, '
          f'90th percentile {sorted(miss_same)[int(0.9 * (N - 1))]}; and holds {st.mean(extra_same):.1f} the non-racer did not')
    print(f'  at each one\'s own finish: lacks {st.mean(miss_own):.1f} the non-racer holds (median {st.median(miss_own):.0f}), holds {st.mean(extra_own):.1f} it does not')
    print(f'  of them with an economic effect (yields, growth, maintenance, trade): {st.mean(econ_same):.1f} at the same turn, {st.mean(econ_own):.1f} at its own finish')
    print('  lacking at the same turn, a game, by era: ' + ', '.join(f'{e} {by_era[e] / N:.1f}' for e in G.EO if by_era[e]))
    print('  by tier: ' + ', '.join(f'{t} {by_tier[t] / N:.1f}' for t in ('CORE', 'STANDARD', 'UNCOMMON', 'RARE', 'UNIQUE') if by_tier[t]))
    print('  by focus (a game): ' + ', '.join(f'{f} {c / N:.2f}' for f, c in by_focus.most_common(14)))
    print('  most often lacking (share of games: name [focus, era, tier] — what it gives):')
    for k, c in freq.most_common(25):
        row = G.ROWS.get(k, {})
        print(f'    {100 * c / N:4.0f}%  {NAME.get(k, k)} ({k}) [{row.get("focus", "?")}, {row.get("era", "?")}, {row.get("tier", "?")}]{" (economic)" if k in ECONOMIC else ""} — {short(GIVES.get(k, ""))}')
    print('  held by the racer at its finish but not by the non-racer at that turn, most often:')
    for k, c in gained.most_common(12):
        row = G.ROWS.get(k, {})
        print(f'    {100 * c / N:4.0f}%  {NAME.get(k, k)} ({k}) [{row.get("focus", "?")}, {row.get("era", "?")}, {row.get("tier", "?")}]')
