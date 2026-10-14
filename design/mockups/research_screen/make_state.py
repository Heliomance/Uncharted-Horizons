"""A late-game research state for the research-screen mockup, taken from one simulated game.

Plays one game of the expert benchmark player (the familiar world, today's rules) with a snapshot hook patched into a
private copy of the engine (design/simulator/power/harness_ftl_e.py is not modified), and writes the research state
some turns before the game's research ends: every breakthrough the player owns, has under study, or has seen revealed,
with its focus, era, tier, prerequisites and unlocks from the design document, plus the funded focus and Insight flows.

Run from the repository root:
  cd design/simulator/power && env PYTHONHASHSEED=0 DET=smart ORSMART=1 PARALLEL=1 RUNON=1 DIFF=1 OBS=0 GLIMPSE=0.1 \
    GLIMPSEU=0.03 END=2 ENDRULE=active INSTR_D=5 EXPFIX=1 ENDFROM=theory METHODS=Warp WORKERS=1 \
    bash scratch_run.sh python3 ../../mockups/research_screen/make_state.py [turns_before_end=15] [game=0]
Output: design/mockups/research_screen/late_game_state.json
"""
import sys, os, re, json, types, runpy
HERE = os.path.dirname(os.path.abspath(__file__))
POWER = os.path.normpath(os.path.join(HERE, '..', '..', 'simulator', 'power'))
sys.path.insert(0, POWER)
BEFORE = int(sys.argv[1]) if len(sys.argv) > 1 else 15
GAME = int(sys.argv[2]) if len(sys.argv) > 2 else 0

# the engine, with a snapshot of the whole research state at the end of every turn from SNAP['from']
src = open(os.path.join(POWER, 'harness_ftl_e.py'), encoding='utf-8').read()
anchor = "        log.append((turn, d, len(found)))\n"
assert src.count(anchor) == 1
hook = anchor + (
    "        if SNAP is not None and turn >= SNAP['from']:\n"
    "            SNAP['states'][turn] = dict(have=dict(have), occurred=set(occurred), lost=set(lost), glimpsed=set(glimpsed),\n"
    "                diff=dict(diff_since), diff_unc=dict(diff_unc), progress=dict(progress), need=dict(need), active=active,\n"
    "                end_k=end_k, end_prog=end_prog, end_cost=end_cost, inc=inc, d=d, flow=dict(flow), opened=dict(opened),\n"
    "                funded=set(FUNDED), att=dict(att_turn), occ_turn=dict(occ_turn), lost_at=dict(lost_at), disc=list(disc))\n")
mod = types.ModuleType('harness_ftl_e'); mod.__file__ = os.path.join(POWER, 'harness_ftl_e.py')
exec(compile(src.replace(anchor, hook), mod.__file__, 'exec'), mod.__dict__)
mod.SNAP = {'from': 150, 'states': {}}
sys.modules['harness_ftl_e'] = mod

sys.argv = ['w7f.py', 'familiar', str(GAME + 1), '_mockupsnap']
os.chdir(POWER)
try: runpy.run_path(os.path.join(POWER, 'w7f.py'), run_name='__main__')
except SystemExit: pass
res = json.load(open(os.path.join(POWER, 'results', 'w7f_familiar_mockupsnap.json')))
os.remove(os.path.join(POWER, 'results', 'w7f_familiar_mockupsnap.json'))
g = res[GAME]
end = max(g['cert'] or 0, g['built'] or 0) or max(mod.SNAP['states'])
turn = end - BEFORE
if os.environ.get('LIST'):                   # LIST=1: one line a turn, to choose the turn to show
    for t, X in sorted(mod.SNAP['states'].items()):
        if t >= end - 60: print(t, 'funded', X['active'], 'endeavour', X['end_k'], 'studying', len(X['occurred'] - set(X['have'])))
    sys.exit(0)
S = mod.SNAP['states'][turn]

# names, prerequisites and unlocks from the design document's focus tables
tree = open(os.environ.get('UH_TREE') or os.path.join(HERE, '..', '..', 'tech_tree.md'), encoding='utf-8').read()
FOCI = []
for m in re.finditer(r'^### FOCUS: (.+?)\s*$', tree, re.M):
    head = m.group(1).strip(); parts = head.rsplit(' ', 1)
    FOCI.append(dict(name=parts[0].title().replace(' And ', ' and '), icon=parts[1] if len(parts) > 1 else ''))
ROWINFO = {}
for line in tree.split('\n'):
    mm = re.match(r'^\| ([A-Z][A-Z0-9-]*[0-9][A-Z]?(?:-W)?|ME-B) \| \*\*(.+?)\*\* \| (\w+) \| ([\w ]+?) \| (.*?) \| (.*?) \|', line)
    if mm:
        unl = [u for u in re.findall(r'\*\*(.+?)\*\*', mm.group(6)) if len(u) < 40][:4]
        ROWINFO[mm.group(1)] = dict(name=mm.group(2), prereq=re.sub(r'\s+', ' ', mm.group(5)).strip()[:160], unlocks=unl)

R = mod.ROWS; EO = mod.EO
def status(k):
    """the player's view: an idea occurring does not reveal it (workshop report, the candidate model)"""
    if k in S['have']: return 'owned'
    revealed = R[k]['tier'] == 'CORE' and k in S['occurred'] or k in S['glimpsed'] or k in S['diff'] or k in S['diff_unc']
    if not revealed: return None
    if k in S['occurred']: return 'studying'
    return 'closed' if k in S['lost'] else 'waiting'
rows = []
for k in sorted(R):
    st = status(k)
    if st is None: continue
    r = dict(id=k, name=ROWINFO.get(k, {}).get('name', k), focus=R[k]['focus'], era=R[k]['era'], tier=R[k]['tier'], status=st,
             prereq=ROWINFO.get(k, {}).get('prereq', ''), unlocks=ROWINFO.get(k, {}).get('unlocks', []))
    if st == 'owned': r['turn'] = S['have'][k][0]; r['new'] = S['have'][k][0] == turn
    r['ahead'] = EO.index(R[k]['era']) > int(S['d'])   # from a later era than the civilisation's development: costs the premium
    if st == 'studying':
        r['progress'] = round(min(S['progress'].get(k, 0.0) / S['need'][k], 0.99), 2) if S['need'].get(k) else 0.0
        r['since'] = S['occ_turn'].get(k)
    if st == 'waiting': r['source'] = 'rival' if (k in S['diff'] or k in S['diff_unc']) else 'glimpse'
    if st == 'closed': r['source'] = 'rival' if (k in S['diff'] or k in S['diff_unc']) else 'glimpse'; r['closed_turn'] = S['lost_at'].get(k, [None])[0]
    r['target'] = k in S['funded']
    rows.append(r)
# Competing Solutions (design §6), which the engine does not model: a revealed alternative whose primary is owned is
# locked out, a Path Not Taken; one whose primary is not yet owned is marked as competing
PAIRS = [('FA16', 'CH12'), ('CO05', 'CO03'), ('WA08', 'WA07'), ('WM11', 'CO23'), ('MD20', 'MD06'), ('NP08', 'ES06'), ('NP-F01', 'NP04'),
         ('ES03-W', 'ES03'), ('ES05-W', 'ES05'), ('ES14', 'ES08'), ('TH08', 'MC09'), ('TH14', 'MC08'), ('CH09-W', 'CH09'), ('CP13', 'CP01'),
         ('CP14', 'CP07'), ('EL14', 'EL07')]
byid = {r['id']: r for r in rows}
for alt, prim in PAIRS:
    r = byid.get(alt)
    if not r or r['status'] == 'owned': continue
    if prim in S['have']: r['status'] = 'not_taken'; r['instead'] = ROWINFO.get(prim, {}).get('name', prim)
    elif prim in byid: r['competes_with'] = byid[prim]['name']
out = dict(turn=turn, research_ends=end, method=g['m'], era=EO[min(int(S['d']), len(EO) - 1)], development=round(S['d'], 2),
           insight_per_turn=round(S['inc'], 1), funded_focus=S['active'], endeavour=S['end_k'],
           endeavour_progress=round(S['end_prog'] / S['end_cost'], 2) if S['end_k'] and S['end_cost'] else None,
           flow={f: round(v, 1) for f, v in sorted(S['flow'].items(), key=lambda kv: -kv[1])}, foci=FOCI,
           counts={s: sum(1 for r in rows if r['status'] == s) for s in ('owned', 'studying', 'waiting', 'closed', 'not_taken')},
           hidden_under_study=sum(1 for k in S['occurred'] if k not in S['have'] and status(k) is None),
           foci_entered=sorted({R[k]['focus'] for k in R if k in S['have'] or k in S['disc']}), rows=rows)
json.dump(out, open(os.path.join(HERE, os.environ.get('OUT', 'late_game_state.json')), 'w'), indent=1, ensure_ascii=False)
print(f"turn {turn} (research ends {end}), era {out['era']} ({out['development']}), funded {out['funded_focus']}, "
      f"Insight {out['insight_per_turn']}/turn; {out['counts']}")
