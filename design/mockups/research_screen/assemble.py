"""Assemble the canvas artboards from src/ and the data: canvas/project/*.dc.html.

  python3 assemble.py            # writes the artboards (font url from canvas/font_url.txt, if present)
Inputs: mockup_data.json (build_data.py), texts.json (the player-facing text of every breakthrough), src/Main.template.html,
src/main.js. Main.dc.html carries the whole screen; the other artboards import it with a different `view`.
"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'canvas', 'project')
P = lambda *a: os.path.join(HERE, *a)

DATA = json.load(open(P('mockup_data.json'), encoding='utf-8'))
TEXTS = {r['id']: r for r in json.load(open(P('texts.json'), encoding='utf-8'))} if os.path.exists(P('texts.json')) else {}
FONT_URL = open(P('canvas', 'font_url.txt')).read().strip() if os.path.exists(P('canvas', 'font_url.txt')) else 'about:blank'

# Endeavour prices at turn 226: 2 x era price x per-city multiplier 1.2864 x the premium for eras ahead of development
PRICES = {'Primitive': 12, 'Ancient': 37, 'Classical': 168, 'Medieval': 371, 'Early Modern': 1130, 'Modern': 2447, 'Atomic': 5340, 'Space': 21827}
# W19 (mechanism open): what each focus tends to help with; static text naming no breakthrough
HELP = {'Aeronautics': 'air units and sight', 'Animal Husbandry': 'mounted units and food', 'Chemistry': 'materials, fuels and medicines',
        'Computing': 'science and administration', 'Construction': 'buildings and defences', 'Electricity': 'power and communication',
        'Electronics': 'detection and devices', 'Energy Systems': 'power and production', 'Farming': 'food and growth',
        'Fire': 'production and early weapons', 'Foraging': 'food and medicine', 'Genetics': 'health and food',
        'Materials Science': 'production and protection', 'Mathematics': 'science and engineering', 'Mechanics': 'production and machines',
        'Medicine': 'health and growth', 'Metallurgy': 'weapons, armour and production', 'Mining': 'resources and production',
        'Nuclear Physics': 'power and weapons', 'Observation': 'science and knowing the land', 'Optics': 'sight and instruments',
        'Philosophy and the Arts': 'culture, faith and learning', 'Quantum Physics': 'science and instruments',
        'Relativity & Cosmology': 'science and trade', 'Rocketry': 'launches and missiles', 'Seafaring': 'ships and sea trade',
        'Social Organization': 'government and specialists', 'Stonework': 'building and tools', 'Textiles & Materials': 'trade goods and equipment',
        'Thermodynamics': 'engines and power', 'Trade': 'gold and trade routes', 'Warfare': 'military units and tactics',
        'Water Management': 'food and water power'}
# Insight modifiers (§1.3 and owned breakthroughs) for the declared lands: a river-valley start, volcanic, earthquake-prone
MODS = {'*': ['+5% Natural Philosophy (all foci)'], 'Farming': ['+20% river start', '+10% Botanical Classification'],
        'Trade': ['+20% river start'], 'Construction': ['+20% river start', '+25% earthquake-prone land'],
        'Metallurgy': ['+20% volcanic region'], 'Chemistry': ['+20% volcanic region'], 'Medicine': ['+10% Botanical Classification'],
        'Electronics': ['+10% Quantum Electrodynamics'], 'Nuclear Physics': ['+10% Special Relativity']}
ERA = {
    't226': dict(era='Modern', devEra='Modern', eraText='Modern era · 5 of 6 toward Atomic', newFoci=['Materials Science'], eraLines=[
        'You enter an era when you hold enough breakthroughs from it or later.',
        'The Atomic era needs 6 from the Atomic era or later: you hold 5.',
        'Synthesis can be used once in each era: unused in the Modern era.']),
    't231': dict(era='Atomic', devEra='Modern', eraText='Atomic era · 2 of 4 toward Space', newFoci=[], eraLines=[
        'You enter an era when you hold enough breakthroughs from it or later.',
        'You entered the Atomic era with your 6th breakthrough from it or later.',
        'The Space era needs 4 from the Space era: you hold 2.',
        'Synthesis can be used once in each era: unused in the Atomic era.']),
}
STATIC = ('name', 'focus', 'era', 'src', 'also', 'competes', 'instead', 'by', 'needs_focus')


def build():
    rows, snaps = {}, {}
    for m, S in DATA.items():
        snap = dict(turn=S['turn'], insight=S['insight'], funded=S['funded'], queue=S['queue'], foci=S['foci'], badges=S['badges'],
                    endeavour=S['endeavour'], rows=[], **ERA[m])
        for r in S['rows']:
            st = {k: r[k] for k in STATIC if k in r}
            if isinstance(r.get('needs'), str): st['needs_name'] = r['needs']
            t = TEXTS.get(r['id'], {})
            for k in ('fx', 'fx2', 'opens', 'flav', 'conj'):
                if t.get(k): st[k] = t[k]
            if t.get('needs'): st['needs'] = [{'label': n['label'], 'ref': n['ref'], 'alt': n['alt']} for n in t['needs']]
            rows.setdefault(r['id'], {}).update(st)
            snap['rows'].append(dict(id=r['id'], status=r['status'], tags=r.get('tags', []), **({'turn': r['turn']} if 'turn' in r else {})))
        snaps[m] = snap
    return dict(rows=rows, snap=snaps, prices=PRICES, help=HELP, mods=MODS, wholeHeight=WHOLE_HEIGHT)


WHOLE_HEIGHT = 2040


def main():
    os.makedirs(OUT, exist_ok=True)
    D = build()
    js = open(P('src', 'main.js'), encoding='utf-8').read().replace('__DATA__', json.dumps(D, ensure_ascii=False, separators=(',', ':')))
    assert '</script' not in js
    html = open(P('src', 'Main.template.html'), encoding='utf-8').read().replace('__SCRIPT__', js).replace('__FONT_URL__', FONT_URL)
    open(os.path.join(OUT, 'Main.dc.html'), 'w', encoding='utf-8').write(html)
    for name, view, (w, h), title in WRAPPERS:
        open(os.path.join(OUT, name), 'w', encoding='utf-8').write(WRAP.format(view=view, w=w, h=h, title=title))
    print('wrote', len(html) // 1024, 'KB Main.dc.html;', len(D['rows']), 'rows;', sum(1 for r in D['rows'].values() if r.get('needs')), 'with texts')


WRAPPERS = [('Whole_board.dc.html', 'a2', (1440, WHOLE_HEIGHT), 'Research screen, whole board'),
            ('Endeavour.dc.html', 'a3', (1440, 810), 'Research screen, a Grand Endeavour'),
            ('Switch_away.dc.html', 'a3b', (1440, 810), 'Research screen, switching away from an Endeavour'),
            ('Focus_view.dc.html', 'a4', (1440, 810), 'Research screen, one focus'),
            ('Phone.dc.html', 'a1" phone="true', (1300, 600), 'Research screen on a phone')]
WRAP = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<style>
body{{margin:0;background:#000033}}
</style>
</helmet>
<dc-import name="Main" view="{view}" hint-size="{w}px,{h}px"></dc-import>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{w},"height":{h}}}}}'>
class Component extends DCLogic {{
  renderVals() {{ return {{}}; }}
}}
</script>
</body>
</html>
"""

if __name__ == '__main__':
    main()
