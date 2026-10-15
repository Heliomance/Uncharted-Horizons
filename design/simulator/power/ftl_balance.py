"""The FTL methods' relative length (Tamsin, 15 Oct 2026: re-analyse the methods for relative length; recommend how to bring
them into sync). For each world, method and benchmark player: the victory median against the world's field, and the race
taken apart: when the unified theory arrives, when the player is certain which method is true, when the method's build is
complete, which of the two binds, and what comes last (the build requirement, or the condition answered last).
Reads results saved with SAVE_T=1 (results/w7f_<world>_<label><X|N|A>_<method>.json); RESULTS reads them from another folder.
The definitions follow w7f.py with the agreed levers (MS17 in Wormhole's build, no NP11 in atomic Tachyonic's) and the
instruments' 5 turns of construction (INSTR_D=5).
Usage: python3 ftl_balance.py <label> [X|N|A ...]   e.g.  python3 ftl_balance.py cmpV125
"""
import sys, os, json, statistics as st, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import victory as V

WORLDS = {'familiar': 'atomic', 'Process': 'elemental', 'Substance': 'elemental'}
BUILD = {'atomic': {'Warp': [['RC01'], ['QP08'], ['QP11'], ['MS08'], ['ES06', 'ES07', 'ES14', 'ES08'], ['ES18']],
                    'Wormhole': [['RC01'], ['QP08'], ['QP11'], ['MS08'], ['RC04'], ['QP12'], ['MA13'], ['MS17']],
                    'Hyperspace': [['QP08'], ['MA13'], ['ES06', 'ES07', 'ES14', 'ES08'], ['MA19']],
                    'Tunnelling': [['QP02'], ['CP10'], ['MS02', 'GN05'], ['QP14'], ['CP21']],
                    'Tachyonic': [['QP06'], ['QP08'], ['SE02'], ['ES06', 'ES07', 'ES14', 'ES08'], ['NP15']]},
         'elemental': {'Warp': [['RC01'], ['QM-E27'], ['QM-E06'], ['MS08'], ['ES07', 'ES15', 'QM-E05'], ['ES18']],
                       'Wormhole': [['RC01'], ['QM-E27'], ['QM-E06'], ['MS08'], ['RC04'], ['QM-E13'], ['MA13'], ['MS17']],
                       'Hyperspace': [['QM-E27'], ['MA13'], ['ES07', 'ES15', 'QM-E05'], ['MA19']],
                       'Tachyonic': [['QM-E17'], ['QM-E27'], ['ES07', 'ES15', 'QM-E05'], ['SE02'], ['TH20']],
                       'Plenum': [['QM-E27'], ['MS02'], ['QM-E19'], ['QM-E23'], ['AE20']]}}
HOST = {'atomic': {'exotic': ['QP11'], 'extradim': ['QP09', 'QP10'], 'discrete': ['QP09', 'QP10'], 'bubble': ['MS08'], 'closed': ['RC07'],
                   'throat': ['MS08'], 'leak': ['RC11'], 'dark': ['RC05'], 'coherence': ['CP21'], 'hartman': ['QP14'], 'tachDE': ['RC06'], 'tachyon': ['QP15']},
        'elemental': {'exotic': ['QM-E06'], 'strata': ['QM-E12'], 'bubble': ['MS08'], 'closed': ['RC07'], 'throat': ['MS08'], 'leak': ['RC11'],
                      'dark': ['RC05'], 'superlum': ['RC06'], 'catalogue': ['QM-E28'], 'currents': ['QM-E19'], 'coupling': ['AE20']}}
COND = {'atomic': {'Warp': ['exotic', 'extradim', 'bubble'], 'Wormhole': ['exotic', 'closed', 'throat'], 'Hyperspace': ['extradim', 'leak', 'dark'],
                   'Tunnelling': ['coherence', 'discrete', 'hartman'], 'Tachyonic': ['tachDE', 'closed', 'tachyon']},
        'elemental': {'Warp': ['exotic', 'strata', 'bubble'], 'Wormhole': ['exotic', 'closed', 'throat'], 'Hyperspace': ['strata', 'leak', 'dark'],
                      'Tachyonic': ['superlum', 'closed', 'catalogue'], 'Plenum': ['currents', 'superlum', 'coupling']}}
CLOSE = {'atomic': 'QP08', 'elemental': 'QM-E27'}
INSTR = {'coherence': ['CP21'], 'leak': ['RC11'], 'dark': ['RC05', 'RC06'], 'tachDE': ['RC05', 'RC06'], 'superlum': ['RC05', 'RC06'],
         'tachyon': ['QP15'], 'catalogue': ['QM-E28']}
INSTR_D = 5
PLAYERS = {'X': ('expert', 1.0), 'N': ('novice', 1.0), 'A': ('average', 0.8)}


def ready(c, t, host):
    """turn condition c's answer is known: its host's discovery, or for a measurement its instrument's completion"""
    hs = [t[h] for h in host[c] if h in t]
    if not hs: return None
    if c not in INSTR: return min(hs)
    us = [t[u] for u in INSTR[c] if u in t]
    return max(min(hs), min(us) + INSTR_D) if us else None


def analyse(g, ont, econ):
    t = g.get('t') or {}; m = g['m']; v = V.victory(g, econ)
    if v is None: return None
    fin = max(g['cert'], g['built'])
    met = {tuple(gr): min((t[o] for o in gr if o in t), default=None) for gr in BUILD[ont][m]}
    last_build = max(met, key=lambda k: met[k] or 0)
    conds = {c: ready(c, t, HOST[ont]) for c in COND[ont][m]}
    last_cond = max(conds, key=lambda c: conds[c] or 0)
    bind = 'build' if g['built'] > g['cert'] else ('certainty' if g['cert'] > g['built'] else 'both')
    return dict(v=v, fin=fin, close=t.get(CLOSE[ont]) or g.get('close'), cert=g['cert'], built=g['built'], bind=bind,
                last_build='/'.join(last_build), last_build_t=met[last_build], last_cond=last_cond, last_cond_t=conds[last_cond],
                tail=v - fin)


def main():
    label = sys.argv[1].lstrip('_'); codes = sys.argv[2:] or ['X', 'N', 'A']
    R = os.environ.get('RESULTS') or os.path.join(HERE, 'results')
    for code in codes:
        name, econ = PLAYERS[code]
        print(f'\n=== {name}')
        for w, ont in WORLDS.items():
            rows = {}
            for m in BUILD[ont]:
                gs = json.load(open(os.path.join(R, f'w7f_{w}_{label}{code}_{m}.json')))
                rs = [a for a in (analyse(g, ont, econ) for g in gs) if a]
                rows[m] = (rs, len(gs) - len(rs))
            field = st.median([r['v'] for rs, _ in rows.values() for r in rs])
            print(f'== {w} (field median {field:.0f})')
            print(f"  {'method':11} {'victory':>7} {'vs field':>8} {'theory':>6} {'certain':>7} {'built':>5} {'finish':>6}  binds (build/cert/both)   last build need (share, median turn)        last own condition")
            for m, (rs, un) in rows.items():
                md = lambda k: st.median([r[k] for r in rs if r[k] is not None])
                binds = collections.Counter(r['bind'] for r in rs); n = len(rs)
                lb = collections.Counter(r['last_build'] for r in rs).most_common(2)
                lbt = {k: st.median([r['last_build_t'] for r in rs if r['last_build'] == k]) for k, _ in lb}
                lc = collections.Counter(r['last_cond'] for r in rs).most_common(1)[0]
                print(f"  {m:11} {md('v'):7.0f} {md('v') - field:+8.0f} {md('close'):6.0f} {md('cert'):7.0f} {md('built'):5.0f} {md('fin'):6.0f}  "
                      f"{binds['build'] / n:4.0%}/{binds['certainty'] / n:4.0%}/{binds['both'] / n:4.0%}   "
                      + ', '.join(f'{k} ({c / n:.0%}, {lbt[k]:.0f})' for k, c in lb).ljust(40)
                      + f"   {lc[0]} ({lc[1] / n:.0%})" + (f'  unfinished {un}' if un else ''))


if __name__ == '__main__':
    main()
