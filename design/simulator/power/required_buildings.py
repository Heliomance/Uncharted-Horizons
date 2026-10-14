"""v3.87: requiredBuilding — a notation token, the 29 requirements the fork's own rules imply, and a battery check."""
import json
exec(open('/home/user/Uncharted-Horizons/design/simulator/power/stage3a.py', encoding='utf-8').read().split('log = []')[0])
fork = json.load(open('/home/user/Uncharted-Horizons/design/simulator/power/fork_buildings.json'))

REQ = {'Steam Works': 'Workshop', 'Engine House': 'Workshop', 'Tide Computer': 'Harbor', 'Phage Institute': 'Hospital',
       'Sanitation Works': 'Aqueduct', 'Pharmacopoeia': 'Balancing Clinic', 'Bard Council': 'Monument', 'Royal Court': 'Monument',
       'Swordsmith': 'Barracks', 'Bronze Foundry Temple': 'Shrine', 'River Temple': 'Shrine'}
REQ.update({f['name']: 'Factory' for f in fork if 'Power Plant' in f['tags']})
article = lambda b: 'an' if b[0] in 'AEIOU' else 'a'

def add_requirement(spec, required):
    parts = split_top(spec)
    lead = r'\s*(\d+(?:/\d+)?|maintenance \d+|a grid plant: ⟨Power Plant⟩ \(tag\))\s*'
    i = max(n for n, p in enumerate(parts[:4]) if re.fullmatch(lead, p))
    parts.insert(i + 1, f' requires {article(required)} **{required}** in this city')
    return ';'.join(parts)

done = []
for f in fork:
    if f['name'] in REQ:
        done.append((f['rid'], f['name'], edit_building(f['rid'], f['name'], lambda s, r=REQ[f['name']]: add_requirement(s, r))))
print(len(done), 'requirements written;', sorted(set(s for *_, s in done)))

t = namespace['t']
old = "*Reveals* **X** — a resource's `revealedBy`;"
new = ("*Reveals* **X** — a resource's `revealedBy`; `requires a **X** in this city` inside a spec — the building's `requiredBuilding`: "
       "X, or a building that replaces X, must stand in the city (Unciv's `containsBuildingOrEquivalent`). X always names a real building, "
       "never a slot tag, because the rejection message looks the name up. A fork building that takes a canonical building's place carries that "
       "building's requirement: a replacement copies its base's, as the Wat copies the University's; an early version copies its successor's; "
       "an alternative that removes a building copies the removed building's; a paradigm's stand-in copies the one it stands in for; and every "
       "member of the Power Plant slot requires a Factory, as the canonical Nuclear and Solar Plants do.")
assert t.count(old) == 1; t = t.replace(old, new)
old = "`cityStrength`, `cityHealth`, `requiredResource`,"
assert t.count(old) == 1; t = t.replace(old, "`cityStrength`, `cityHealth`, `requiredResource`, `requiredBuilding`,")
t = t.replace('Complete Tech Tree Design Document (v3.86)', 'Complete Tech Tree Design Document (v3.87)', 1)
open('/home/user/Uncharted-Horizons/design/simulator/tt.md', 'w', encoding='utf-8').write(t)
