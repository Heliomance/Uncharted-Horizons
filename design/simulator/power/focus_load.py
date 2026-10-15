"""Ideas under study per focus, turn by turn, in benchmark games (a patched private copy of the engine; the simulator is
not modified). Usage, through scratch_run.sh with a cell's environment: python3 focus_load.py <world> <games> <suffix>
FOCUSLOG=<path prefix> receives one JSON line per turn per worker process:
[seed, turn, development, funded focus, endeavour target, {focus: ideas under study}, funded focus's ideas, of them faster as an Endeavour]
'Faster as an Endeavour': its share of the funded focus is below (meter left) / (2 x its cost multiplier), i.e. a 2x
Endeavour fed the whole active share would finish it sooner than ordinary study at its current share.
Example (one expert cell, familiar world; the log lands in /tmp):
  cd design/simulator/power && env PYTHONHASHSEED=0 DET=smart ORSMART=1 PARALLEL=1 RUNON=1 DIFF=1 OBS=0 GLIMPSE=0.1 \
    GLIMPSEU=0.03 END=2 ENDRULE=active INSTR_D=5 EXPFIX=1 ENDFROM=theory METHODS=Warp FOCUSLOG=/tmp/focus_load \
    bash scratch_run.sh python3 focus_load.py familiar 60 _focusload
  (then delete results/w7f_familiar_focusload.json, which w7f.py writes as usual)
"""
import sys, os, json, types, runpy
POWER = '/home/user/Uncharted-Horizons/design/simulator/power'
sys.path.insert(0, POWER)
src = open(os.path.join(POWER, 'harness_ftl_e.py'), encoding='utf-8').read()
anchor = "        log.append((turn, d, len(found)))\n"
assert src.count(anchor) == 1
hook = anchor + (
    "        _ks = [k for k in pool.get(active, [])] if active else []\n"
    "        _w = {k: (progress.get(k, 0.0) + prm.momentum) for k in _ks}; _tw = sum(_w.values()) or 1.0\n"
    "        _fast = sum(1 for k in _ks if k in need and _w[k] / _tw < max(need[k] - progress.get(k, 0.0), 0.0) / (2 * COSTMULT.get(k, 1.0)))\n"
    "        with open(FOCUSLOG_PATH + '.' + str(__import__('os').getpid()), 'a') as _fh:\n"
    "            _fh.write(json.dumps([seed, turn, round(d, 2), active, end_k, {f: len(ks) for f, ks in pool.items()}, len(_ks), _fast]) + '\\n')\n")
mod = types.ModuleType('harness_ftl_e'); mod.__file__ = os.path.join(POWER, 'harness_ftl_e.py')
exec(compile(src.replace(anchor, hook), mod.__file__, 'exec'), mod.__dict__)
mod.FOCUSLOG_PATH = os.environ['FOCUSLOG']
sys.modules['harness_ftl_e'] = mod
sys.argv = ['w7f.py'] + sys.argv[1:4]
os.chdir(POWER)
try: runpy.run_path(os.path.join(POWER, 'w7f.py'), run_name='__main__')
except SystemExit: pass
