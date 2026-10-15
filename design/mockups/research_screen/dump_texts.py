"""Every sentence the mockup can show in its bottom bar: selects each breakthrough, each focus, the funding header and the
era pill, in both snapshots (turn 226 and turn 231), and writes what the bar says, with the action buttons.

Usage: python3 dump_texts.py [out.txt]   (default: bar_texts.txt beside this file)
"""
import sys, os, json, pathlib
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import preview

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'bar_texts.txt'
MAIN = HERE / 'canvas' / 'project' / 'Main.dc.html'
DATA = json.load(open(HERE / 'mockup_data.json', encoding='utf-8'))
READ = """() => { const bar = [...document.querySelectorAll('div')].find(d => d.style.height === '121px' && d.style.display === 'flex');
  if (!bar) return null; const cells = bar.children;
  const desc = cells[1]; const title = desc.children[0].innerText.replace(/\\s+/g, ' ').trim();
  const lines = [...desc.children].slice(1).map(x => x.innerText.trim()).filter(Boolean);
  const acts = [...cells[2].querySelectorAll('button')].map(b => (b.disabled ? '[disabled] ' : '') + b.innerText.replace(/\\s+/g, ' ').trim());
  return { title, lines, acts }; }"""

with sync_playwright() as p:
    b = p.chromium.launch(); out = []
    for view, snap in (('a1', 't226'), ('a3', 't231')):
        html = preview.build(str(MAIN), {'view': view})
        tmp = HERE / f'_dump_{view}.html'; tmp.write_text(html, encoding='utf-8')
        pg = b.new_page(viewport={'width': 1440, 'height': 810}); pg.goto(tmp.as_uri()); pg.wait_for_timeout(200)
        sels = [{'kind': 'row', 'id': r['id']} for r in DATA[snap]['rows']] + [{'kind': 'focus', 'id': f} for f in DATA[snap]['foci']] + [{'kind': 'funding'}, {'kind': 'era'}]
        out.append(f'===== {snap} ({view})')
        for s in sels:
            pg.evaluate(f"comp.setState({{ sel: {json.dumps(s)} }})")
            r = pg.evaluate(READ)
            if not r: out.append(f'!! no bar for {s}'); continue
            st = next((x['status'] for x in DATA[snap]['rows'] if x['id'] == s.get('id')), s['kind'])
            out.append(f"--- {s.get('id', s['kind'])} [{st}] {r['title']}")
            out += ['    ' + l for l in r['lines']]
            out.append('    ACTIONS: ' + ' | '.join(r['acts']))
        pg.close(); tmp.unlink()
    b.close()
OUT.write_text('\n'.join(out) + '\n', encoding='utf-8')
print('wrote', OUT, len(out), 'lines')
