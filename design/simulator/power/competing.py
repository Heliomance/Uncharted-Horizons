"""Competing Solutions (design document §1.2; the groups are §6's Competing Solutions Reference), for the harness.

Each group has a primary and an alternative. With COMPETE=1 (the default since v3.124, defaults.py):
- an alternative whose primary exists in this world costs its detour margin more (COMPETEMARGIN, x1.5 as the design
  starts it), and is locked out for good if the civilisation discovers the primary first: it never occurs, is never
  studied, never diffuses and never comes back, though an Endeavour may still take it (Grand Endeavours suspend
  lock-out). The harness does the locking, from HF.COMPETE;
- an alternative whose primary cannot exist in this world takes the primary's tier, with no margin and no lock-out.
  In the simulated worlds this never happens (each group's two rows exist in the same worlds), but the rule is here.
Whether a late primary supersedes the alternative or lets it persist changes only what the alternative's objects do,
so the harness ignores it. Before v3.124 no measurement modelled any of this (COMPETE=0 reproduces them)."""
import os, re
import defaults

IDRX = r'\(([A-Z]{1,3}(?:-[A-Z]+)?\d+(?:-[A-Z]+)?)\)'


def groups(tree=None):
    """§6's groups as (primary, alternative, outcome) — outcome 'superseded' or 'persists' — read from the tree."""
    t = open(tree or defaults.TREE, encoding='utf-8').read()
    sec = t[t.index('### Competing Solutions Reference'):]
    out = []
    for line in sec.split('\n')[2:]:
        if out and not line.startswith('|'): break
        c = [s.strip() for s in line.split('|')[1:-1]]
        if len(c) != 4 or c[0] == 'Goal' or set(c[0]) <= set('-'): continue
        out.append((re.findall(IDRX, c[1])[-1], re.findall(IDRX, c[2])[-1], c[3].split()[0]))
    return out


def apply(HF, rows):
    """Set HF.COMPETE ({alternative: primary} for the alternatives that can be locked out) and the margins in HF.COSTMULT,
    and give an alternative whose primary is absent its primary's tier. Call after HF.COSTMULT is set (prices.apply)."""
    HF.COMPETE = {}
    if os.environ.get('COMPETE', '0') != '1': return
    import gen_data as G
    margin = float(os.environ.get('COMPETEMARGIN', '1.5'))
    for p, a, _ in groups():
        if a not in rows: continue
        if p in rows:
            HF.COMPETE[a] = p; HF.COSTMULT[a] = HF.COSTMULT.get(a, 1.0) * margin
        elif p in G.ROWS:
            rows[a]['tier'] = G.ROWS[p]['tier']
