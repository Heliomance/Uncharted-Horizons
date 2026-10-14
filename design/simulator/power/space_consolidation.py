"""v3.92: the Space era's buildings consolidated."""
exec(open('/home/user/Uncharted-Horizons/design/simulator/power/stage3a.py', encoding='utf-8').read().split('log = []')[0])
def replace_once(old, new):
    assert namespace['t'].count(old) == 1, old[:70]; namespace['t'] = namespace['t'].replace(old, new)
# 1. the Planetary Defense Network becomes a national wonder
edit_row_text('SE13', '**Planetary Defense Network**ⁿ [750/4; cityStrength +10; cityHealth +100]',
    '**Planetary Defense Network**ⁿ [national wonder; 750/0; cityStrength +10; cityHealth +100; ⟨[+15]% Strength for cities⟩; ⟨Cost increases by [180] per owned city⟩] — one network for the whole planet, hardest at its centre')
# 2. Orbital Resource Delivery upgrades the Asteroid Mining Station instead of adding a depot
assert edit_building('SE06', 'Orbital Depot', lambda s: None) == 'removed'
unlock_cell_prepend('SE06', 'Upgrades every **Asteroid Mining Station**: each also provides 2 Aluminum and 2 Rare Earths — deliveries from orbit, not just the belt')
edit_row_text('MI12', '⟨Provides [2] [Aluminum]⟩; ⟨Limited to [3] per Civilization⟩]',
    '⟨Provides [2] [Aluminum]⟩; ⟨Provides [2] [Aluminum] <after discovering [Orbital Resource Delivery]>⟩; ⟨Provides [2] [Rare Earths] <after discovering [Orbital Resource Delivery]>⟩; ⟨Limited to [3] per Civilization⟩]')
# 3. Quantum Communication carries the trade-route Gold itself
assert edit_building('QP14', 'Quantum Network', lambda s: None) == 'removed'
unlock_cell_prepend('QP14', '⟨[+2 Gold] from each Trade Route⟩ — every route on the unhackable network')
namespace['t'] = namespace['t'].replace('Complete Tech Tree Design Document (v3.91)', 'Complete Tech Tree Design Document (v3.92)', 1)
open('/home/user/Uncharted-Horizons/design/simulator/tt.md', 'w', encoding='utf-8').write(namespace['t']); print('applied')
