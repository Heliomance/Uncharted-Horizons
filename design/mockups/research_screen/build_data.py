"""The mockup's data: the three simulated snapshots (turn 1 before anything is discovered, turn 226, and turn 231 with an
Endeavour running) with the build spec's corrections applied (build_spec.md §8), written to mockup_data.json. Corrections cover what the engine does not model:
Competing Solutions lock-outs, superseded and dead-ended theories, theory-revealed rows, and rows a prerequisite still
blocks. They are illustrative and marked `curated` in the output.
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
EO = ['Primitive', 'Ancient', 'Classical', 'Medieval', 'Early Modern', 'Modern', 'Atomic', 'Space']
NORM = lambda f: f.replace('Philosophy And The Arts', 'Philosophy and the Arts')

ADD_T226 = [
    dict(id='MD20', name='Phage Therapy', focus='Medicine', era='Modern', tier='STANDARD', status='waiting', src='Revealed by Germ Theory'),
    dict(id='ES05', name='Oil Power Plant', focus='Energy Systems', era='Modern', tier='STANDARD', status='waiting', src='Revealed by Turbine Design'),
    dict(id='RK09', name='Ion Drive', focus='Rocketry', era='Space', tier='STANDARD', status='waiting', src='Revealed by Quantum Electrodynamics'),
    dict(id='RC03', name='Gravitational Waves Detection', focus='Relativity & Cosmology', era='Atomic', tier='STANDARD', status='unreach',
         src='Revealed by General Relativity', needs='Laser', needs_focus='Optics'),
    dict(id='AE13', name='Rigid Airship', focus='Aeronautics', era='Modern', tier='STANDARD', status='unreach',
         src='Seen in use by another civilisation', needs='Dirigible/Airship', needs_focus='Aeronautics'),
]
ADD_T231 = [
    dict(id='QP09', name='String Theory Validation', focus='Quantum Physics', era='Space', tier='STANDARD', status='waiting',
         src='Revealed by Quantum Gravity Theory', new=True),
    dict(id='QP10', name='Loop Quantum Gravity', focus='Quantum Physics', era='Space', tier='STANDARD', status='waiting',
         src='Revealed by Quantum Gravity Theory', new=True),
]
NOT_TAKEN = {'CO05': 'Arch Construction', 'WA08': 'Cavalry Tactics'}
SUPERSEDED = {'FA16': 'Catalysis', 'WM11': 'Railway Network'}
SUPERSEDED_TEXT = {'FA16': 'Superseded by Catalysis (turn 203): its +1 Food from Farms passed to the Haber process.',
                   'WM11': 'Superseded by Railway Network: its Pound Lock can no longer be built.'}
PERSISTS_TEXT = {'TH08': 'Persists: Internal Combustion Engine came later, and the Stirling Works stays available.',
                 'CH09-W': 'Persists: Petrochemistry came later, and the Bio-Refinery stays available.'}
# not entered: Computing opens only with EN02 + MA07, MC14 or QM-E03, none of which this civilisation holds; so CP13,
# which the engine had under study there, is dropped (the engine counts a focus as entered once any row is discoverable)
NOT_ENTERED = {'Computing'}
DROP = {'CP13'}
ROW_MULT = {'TH15': 2.5, 'NP12': 2.5}   # true row multipliers (W18) that an Endeavour price includes
DEAD_END = {'TH09'}
FTL = {'RC01', 'RC02', 'QP02', 'QP12'}   # illustrative: proposals after RC01, and QP12, a build requirement met (hint moves not tracked)
# dual-path reach (R85), from §3's 'Also reachable in this focus' lists
REACH = {'Farming': ['CH12', 'ES13', 'ES03-W'], 'Animal Husbandry': ['MD04', 'FA03'], 'Mining': ['CH08'],
         'Seafaring': ['F06'], 'Warfare': ['F06'], 'Mechanics': ['O15', 'TH08'],
         'Chemistry': ['MI13', 'MC09', 'ES13', 'WA10', 'TR16'], 'Computing': ['GN08', 'GN09', 'GN11', 'GN14'],
         'Materials Science': ['EL12'], 'Electronics': ['EL12'], 'Genetics': ['MD-V01'], 'Aeronautics': ['SF15'],
         'Energy Systems': ['WM05', 'MC04', 'TH08']}
COMPETES = {'ES03-W': 'ES03', 'MD20': 'MD06'}   # alternative -> primary, both revealed in the shown state


def load(mode):
    S = json.load(open(os.path.join(HERE, {'t231': 'endeavour_state.json', 't001': 'start_state.json'}.get(mode, 'late_game_state.json')), encoding='utf-8'))
    rows = []
    for r in S['rows']:
        r = dict(r); r['focus'] = NORM(r['focus']); tags = []
        src = {'glimpse': 'Glimpsed by our scholars', 'rival': 'Learned of from another civilisation'}.get(r.pop('source', None))
        if src: r['src'] = src
        if r['id'] == 'MS02': r['name'] = 'Nanotechnology'
        if r['id'] in NOT_TAKEN: r['status'] = 'not_taken'; r['instead'] = NOT_TAKEN[r['id']]; r['curated'] = True; r.setdefault('src', 'Glimpsed by our scholars')
        if r['id'] in SUPERSEDED: tags.append('Superseded'); r['by'] = SUPERSEDED[r['id']]; r['curated'] = True
        if r['id'] in DEAD_END: tags.append('Dead end'); r['curated'] = True
        if r['status'] == 'owned' and r['tier'] == 'RARE': tags.append('Rare')
        if r['status'] == 'owned' and r['tier'] == 'UNIQUE': tags.append('Unique')
        if r['id'] in DROP: continue
        if r['id'] in FTL or (mode == 't231' and r['id'] in ('QP08', 'QP06')): tags.append('FTL')
        if r['id'] in SUPERSEDED_TEXT: r['superseded'] = SUPERSEDED_TEXT[r['id']]
        if r['id'] in PERSISTS_TEXT: r['persists'] = PERSISTS_TEXT[r['id']]
        if r['id'] in ROW_MULT: r['mult'] = ROW_MULT[r['id']]
        new = (r['status'] == 'closed' and r.get('closed_turn') == S['turn']) or (r['status'] == 'owned' and r.get('turn') == S['turn'])
        if mode == 't231': new = r['id'] in ('QP06', 'QP08', 'PH10', 'CO13')
        if new: tags.append('New')
        r['tags'] = tags
        for k in ('target', 'ahead', 'new', 'unlocks', 'prereq', 'since', 'progress', 'closed_turn'): r.pop(k, None)
        rows.append(r)
    for a in (ADD_T226 if mode != 't001' else []) + (ADD_T231 if mode == 't231' else []):   # rows the engine does not reveal
        a = dict(a); a['tags'] = ['New'] if a.pop('new', False) else []; a['curated'] = True; rows.append(a)
    byid = {r['id']: r for r in rows}
    for alt, prim in COMPETES.items():
        if alt in byid and prim in byid and byid[alt]['status'] != 'owned': byid[alt]['competes'] = byid[prim]['name']
    funded = {'t231': None, 't001': None}.get(mode, 'Quantum Physics')   # turn 1: the first choice is still to make
    queue = {'t231': ['Quantum Physics', 'Energy Systems', 'Medicine'], 't001': []}.get(mode, ['Energy Systems', 'Medicine'])
    badges = {}
    for r in rows:
        if r['status'] == 'studying': badges[r['focus']] = badges.get(r['focus'], 0) + 1
    for f, ids in REACH.items():
        for k in ids:
            if k in byid and byid[k]['status'] == 'studying': badges[f] = badges.get(f, 0) + 1
    reach = {k: sorted(f for f, ids in REACH.items() if k in ids) for k in byid}
    for r in rows:
        if reach.get(r['id']): r['also'] = reach[r['id']]
    for alt, prim in COMPETES.items():   # a revealed rival pair: both chips carry a Rival tag
        if alt in byid and prim in byid and byid[alt]['status'] not in ('owned', 'not_taken') and byid[prim]['status'] != 'owned':
            byid[alt]['tags'].append('Rival'); byid[prim]['tags'].append('Rival'); byid[prim]['rivalOf'] = byid[alt]['name']
    owned = {r['id'] for r in rows if r['status'] == 'owned'}
    # what the civilisation's discoveries allow: the 80/20 split (SO05; 50/50 before it), Experiment (PH04), Synthesis (PH08),
    # and the Faster than light screen, which opens with Special Relativity (RC01, section 4)
    unlocked = dict(split=0.8 if 'SO05' in owned else 0.5, experiment='PH04' in owned, synthesis='PH08' in owned, ftl='RC01' in owned)
    return dict(turn=S['turn'], era={'t231': 'Atomic', 't001': 'Primitive'}.get(mode, 'Modern'), insight=S['insight_per_turn'], funded=funded, **unlocked,
                queue=queue, foci=sorted(set(NORM(f) for f in S['foci_entered']) - NOT_ENTERED), badges={f: n for f, n in badges.items() if f not in NOT_ENTERED},
                endeavour=dict(id='EL11', pct=64, paid=3415, price=5340, committed=226, aside=False) if mode == 't231' else None, rows=rows)


if __name__ == '__main__':
    out = {m: load(m) for m in ('t226', 't231', 't001')}
    json.dump(out, open(os.path.join(HERE, 'mockup_data.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    from collections import Counter
    for m, d in out.items(): print(m, dict(Counter(r['status'] for r in d['rows'])), len(d['rows']), 'rows;', len(d['foci']), 'foci')
