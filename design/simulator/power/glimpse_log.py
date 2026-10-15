"""What becomes of glimpsed ideas, one JSON line per game (patched private copy of the engine; the simulator is not modified).
Usage through scratch_run.sh with a cell's environment: python3 glimpse_log.py <world> <games> <suffix>; GLIMPSELOG=<path prefix>.
Line: [seed, turns, glimpsed {tier: n}, of them later occurred anyway, of them completed by an Endeavour, of them never had,
       Endeavours started, of them on glimpsed ideas, glimpsed ideas never had by tier]
Example (one expert cell, familiar world; the log lands in /tmp):
  cd design/simulator/power && env PYTHONHASHSEED=0 DET=smart ORSMART=1 PARALLEL=1 RUNON=1 DIFF=1 OBS=0 GLIMPSE=0.1 \
    GLIMPSEU=0.03 END=2 ENDRULE=active INSTR_D=5 EXPFIX=1 ENDFROM=theory METHODS=Warp GLIMPSELOG=/tmp/glimpse_log \
    bash scratch_run.sh python3 glimpse_log.py familiar 60 _glimpselog
  (then delete results/w7f_familiar_glimpselog.json, which w7f.py writes as usual)
"""
import sys, os, json, types, runpy
POWER = '/home/user/Uncharted-Horizons/design/simulator/power'
sys.path.insert(0, POWER)
src = open(os.path.join(POWER, 'harness_ftl_e.py'), encoding='utf-8').read()
anchor = "    acct['banked_end'] = bank; acct['recovered_ideas'] = len(rediscovered);"
assert src.count(anchor) == 1
hook = ("    _tier = lambda k: ROWS[k]['tier']\n"
        "    _ends = [k for (_t, k, e) in END_LOG if e == 'start']; _endone = {k for (_t, k, e) in END_LOG if e == 'done'}\n"
        "    _g = sorted(glimpsed); _occ = [k for k in _g if k in occurred]; _end = [k for k in _g if k in _endone]; _never = [k for k in _g if k not in have]\n"
        "    _byt = {}; [_byt.__setitem__(_tier(k), _byt.get(_tier(k), 0) + 1) for k in _g]\n"
        "    _nevt = {}; [_nevt.__setitem__(_tier(k), _nevt.get(_tier(k), 0) + 1) for k in _never]\n"
        "    with open(GLIMPSELOG_PATH + '.' + str(__import__('os').getpid()), 'a') as _fh:\n"
        "        _fh.write(json.dumps([seed, turn, _byt, len(_occ), len(_end), len(_never), len(_ends), sum(1 for k in _ends if k in glimpsed), _nevt]) + '\\n')\n"
        + anchor)
mod = types.ModuleType('harness_ftl_e'); mod.__file__ = os.path.join(POWER, 'harness_ftl_e.py')
exec(compile(src.replace(anchor, hook), mod.__file__, 'exec'), mod.__dict__)
mod.GLIMPSELOG_PATH = os.environ['GLIMPSELOG']
sys.modules['harness_ftl_e'] = mod
sys.argv = ['w7f.py'] + sys.argv[1:4]
os.chdir(POWER)
try: runpy.run_path(os.path.join(POWER, 'w7f.py'), run_name='__main__')
except SystemExit: pass
