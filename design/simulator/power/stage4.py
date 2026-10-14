"""Stage 4 (v3.89): every wonder-only row gains a benefit that every civilisation receives."""
exec(open('/home/user/Uncharted-Horizons/design/simulator/power/stage3a.py', encoding='utf-8').read().split('log = []')[0])
BENEFIT = {
    'S06':    '⟨[-25]% Culture cost of natural border growth [in all cities]⟩ — the stones mark whose land this is',
    'CO06':   '⟨[+15]% Production when constructing [University] buildings [in all cities]⟩ — the masons who raised the cathedrals raised the colleges',
    'CH21':   "⟨[Great Merchant] is earned [+15]% faster⟩ — every adept's gold, if not the Stone itself",
    'QM-E11': '⟨[Great Sage] is earned [+15]% faster⟩ — the harmony studied everywhere, if not the Wheel itself',
    'QM-E10': '⟨[+10]% Great Person generation [in all cities]⟩ — long-lived masters',
    'ES12':   '⟨[+1 Production] from all [Power Plant] buildings⟩ — the vacuum hums faintly in every plant',
    'QM-E07': '⟨[+1 Production] from all [Power Plant] buildings⟩ — the engine\'s principle, in every plant',
    'RK06':   '⟨[+2 Gold] from all [Spaceship Factory] buildings⟩ — orbit pays',
    'RK12':   '⟨[+25]% Production when constructing [Launch Complex] buildings [in all cities]⟩ — the tether\'s materials serve every launch site',
    'SE08':   '⟨[Great Engineer] is earned [+10]% faster⟩ — the engineering of whole worlds',
    'SE09':   '⟨[+1 Production] from all [Solar Plant] buildings⟩ — collectors learned from the swarm',
}
for rid, benefit in BENEFIT.items(): unlock_cell_prepend(rid, benefit)
namespace['t'] = namespace['t'].replace('Complete Tech Tree Design Document (v3.88)', 'Complete Tech Tree Design Document (v3.89)', 1)
open('/home/user/Uncharted-Horizons/design/simulator/tt.md', 'w', encoding='utf-8').write(namespace['t']); print('applied', len(BENEFIT))
