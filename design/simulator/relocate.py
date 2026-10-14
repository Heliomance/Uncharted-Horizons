"""Point the simulator's scripts at the folder this package lives in.

The scripts hold absolute paths. They were written on a machine whose layout this package reproduces: the
working tree at /home/claude/tt.md, the tools in /home/claude/power, Unciv data in /home/claude/unciv, and
saved outputs in /mnt/user-data/outputs. The folder they currently point at is recorded in .relocated-root,
so the script can be run again after the folder moves (a different checkout, another machine):

    python3 relocate.py            # rewrites every script's paths to this folder
    python3 relocate.py --check    # lists the paths it would change, changing nothing
"""
import os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
MARKER = os.path.join(ROOT, '.relocated-root')
previous = open(MARKER, encoding='utf-8').read().strip() if os.path.exists(MARKER) else None

MAP = [('/mnt/user-data/outputs/power_tools', ROOT + '/power'),
       ('/mnt/user-data/outputs', ROOT + '/outputs'),
       ('/home/claude', ROOT)]
if previous and previous != ROOT:
    MAP.append((previous, ROOT))
MAP.sort(key=lambda pair: len(pair[0]), reverse=True)              # longest prefixes first
RX = re.compile('|'.join(re.escape(old) for old, _ in MAP) + r'(?=[/\s"\'):;,]|$)', re.M)

check = '--check' in sys.argv
files = hits = 0
for folder, _, names in os.walk(ROOT):
    if os.sep + 'results' in folder:
        continue                                   # results are data, not scripts
    for name in names:
        if not name.endswith(('.py', '.sh', '.js', '.html')) or name == 'relocate.py':
            continue
        path = os.path.join(folder, name)
        text = open(path, encoding='utf-8').read()
        n = len(RX.findall(text))
        if not n:
            continue
        files += 1
        hits += n
        if check:
            print(f'{n:4}  {os.path.relpath(path, ROOT)}')
            continue
        open(path, 'w', encoding='utf-8').write(RX.sub(lambda m: dict(MAP)[m.group(0)], text))
if not check:
    open(MARKER, 'w', encoding='utf-8').write(ROOT + '\n')
print(f"{'would change' if check else 'changed'} {hits} paths in {files} files"
      + ('' if check else f'; the scripts now use {ROOT}'))
