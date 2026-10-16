"""Reference games for the engine's human path (test_engine_scripted.js): a scripted player in the Python harness.

The harness has no human player, so this patches a private copy of harness_ftl_e.py at run time (the file itself is never
modified, as make_state.py does): a hook at the start of every turn, before anything happens, that sets the funded focus
(HUMAN_FOCUS: funded even if nothing in it is under study, its share then spilling) and a Grand Endeavour request
(END_REQUEST, END_RULE 'request' at 2x, any time, under study or not: the design's rules, which the engine gives the
human), from the state the previous turn left. The policy is simple and the same in both languages:
  - focus: on turns divisible by 4, none chosen (the focus with the most work waiting); otherwise the foci of the rows
    discovered so far, sorted, taken in turn (turn modulo their number), whether or not anything waits there;
  - Endeavour: on turns divisible by 15, the first revealed breakthrough (ids sorted) not discovered whose prerequisites are
    met, preferring one whose idea has not occurred (revealed: a CORE idea that has occurred, a glimpsed idea, or one seen
    in rivals' hands); a request while an Endeavour runs is ignored, as the harness ignores it.
Otherwise w7f.py's game: the generalist's settings (make_python_ref.sh), rivals and diffusion, every turn traced, with
each turn's raw floats (float.hex) as well as the trace's rounded ones.

Run through scratch_run.sh, from design/simulator/power:
  env PLAYER=generalist DIFF=1 OBS=0 GLIMPSE=0.1 GLIMPSEU=0.03 RUNON=1 SAVE_T=1 PYTHONHASHSEED=0 INSTR_D=5 ECON=1.0 END=2 \
    bash scratch_run.sh python3 ../../mockups/sim_web/test/py_scripted.py <world> <games_per_method> <out.json>
"""
import sys, os, json, types, runpy
HERE = os.path.dirname(os.path.abspath(__file__))
POWER = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'simulator', 'power'))
sys.path.insert(0, POWER)
WORLD, N, OUT = sys.argv[1], sys.argv[2], sys.argv[3]

src = open(os.path.join(POWER, 'harness_ftl_e.py'), encoding='utf-8').read()
def patch(anchor, new):
    global src
    assert src.count(anchor) == 1, anchor
    src = src.replace(anchor, new)
patch("    rng = random.Random(seed); m = prm.model\n",
      "    global END_RULE, END_FROM, END_UNOCCURRED_ONLY\n"
      "    if HOOK is not None: END_RULE = 'request'; END_FROM = None; END_UNOCCURRED_ONLY = False\n"
      "    rng = random.Random(seed); m = prm.model\n")
patch("        CLOCK['turn'] = turn\n", "        CLOCK['turn'] = turn\n        if HOOK is not None: HOOK(turn, have)\n")
patch("        else: active = _ftl_active(waiting, pool, have)\n",
      "        else: active = _ftl_active(waiting, pool, have)\n        if HOOK is not None and HUMAN_FOCUS is not None: active = HUMAN_FOCUS\n")
patch("    return have, log\n", "    if TRACE is not None: ALL_TRACES.append(TRACE)\n    return have, log\n")
# every turn's raw values, to the bit: the Insight, each focus's flow, every idea under study's progress and meter, the
# running Endeavour's progress (the trace itself rounds them)
end_of_record = "end=[end_k, round(end_prog / end_cost, 3) if end_cost else 0.0] if end_k is not None else None))\n"
patch(end_of_record, end_of_record + "            TRACE[-1]['raw'] = dict(inc=float(inc).hex(), flow={f: float(v).hex() for f, v in flow.items()}, "
      "progress={k: float(progress.get(k, 0.0)).hex() for k in live if k in need}, need={k: need[k].hex() for k in live if k in need}, "
      "end_prog=float(end_prog).hex())\n")
HF = types.ModuleType('harness_ftl_e'); HF.__file__ = os.path.join(POWER, 'harness_ftl_e.py')
exec(compile(src, HF.__file__, 'exec'), HF.__dict__)
HF.HUMAN_FOCUS = None; HF.ALL_TRACES = []
sys.modules['harness_ftl_e'] = HF


def hook(turn, have):
    S = HF.STATE
    foci = sorted({HF.FOCUS[k] for k in have})
    HF.HUMAN_FOCUS = None if (turn % 4 == 0 or not foci) else foci[turn % len(foci)]
    HF.END_REQUEST = None
    if turn % 15 == 0:
        rev = [k for k in HF.IDS if k not in have and HF.prereqs_met(k, have) and ((HF.ROWS[k]['tier'] == 'CORE' and k in S['occurred'])
               or k in S['glimpsed'] or k in S['diff'] or k in S['diff_unc'])]
        unocc = [k for k in rev if k not in S['occurred']]
        HF.END_REQUEST = (unocc or rev or [None])[0]
HF.HOOK = hook

os.environ['TRACE'] = OUT + '.lasttrace'   # w7f.py then plays the games one after another and keeps every turn's record
sys.argv = ['w7f.py', WORLD, N, '_webscripted']
os.chdir(POWER)
try: runpy.run_path(os.path.join(POWER, 'w7f.py'), run_name='__main__')
except SystemExit: pass
res_path = os.path.join(POWER, 'results', f'w7f_{WORLD}_webscripted.json')
res = json.load(open(res_path)); os.remove(res_path); os.remove(OUT + '.lasttrace')
assert len(res) == len(HF.ALL_TRACES)
json.dump([dict(m=r['m'], truth=r['truth'], t=r['t'], ends=r['ends'], records=tr) for r, tr in zip(res, HF.ALL_TRACES)], open(OUT, 'w'))
print(f'{WORLD}: {len(res)} scripted games, {sum(1 for r in res for e in r["ends"] if e[2] == "start")} Endeavours started, written to {OUT}')
