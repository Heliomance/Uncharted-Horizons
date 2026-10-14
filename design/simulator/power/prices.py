"""The agreed design's research prices, applied to the harness exactly as the FTL runner (w7f.py) applies them: the Space
era's price per discovery (SPACEPRICE) and the price multipliers of Space-era rows: the signature fields' rows at 2.5x,
the W18 pools at 2.5x with capstones at 4x, and the round-two settings. LEVERS letters as in docs/WORKSPACE.md; the
finalised design's are the defaults (defaults.py). Any script that runs the harness on the agreed design calls apply()."""
import os

SIG = ('CP16', 'CP21', 'CP10', 'AE14', 'AE20', 'MS08', 'QM-E23', 'ES22', 'ES18', 'ES14', 'ES08', 'MA15', 'MA19', 'NP11', 'NP15', 'TH20')
POOL_ROWS = ('CP17', 'CP18', 'CP19', 'CP20', 'CP15', 'CP09', 'ES17', 'ES19', 'ES20', 'ES11', 'MS10', 'MS11', 'MS12', 'MS13', 'MS16', 'MA16', 'MA17',
             'MA18', 'MA22', 'MA23', 'MA20', 'NP12', 'NP13', 'NP16', 'NP-F03', 'TH15', 'TH16', 'TH17', 'TH18', 'TH21', 'AE15', 'AE16', 'AE17', 'AE18')
CAPSTONES = ('CP22', 'CP12', 'ES21', 'ES12', 'QM-E07', 'MS15', 'MS07', 'MA21', 'NP17', 'NP09', 'NP-F04', 'TH22', 'AE19')


def apply(HF, rows):
    """Set HF.COSTMULT and the Space era's price for the levers in force. Safe to call more than once."""
    L = os.environ.get('LEVERS', '')
    HF.COSTMULT = {k: 2.5 for k in SIG}
    if 'z' in L:   # assumed non-FTL pools: 2.5x, capstones 4x
        for k in rows:
            if k.startswith('ZZ'): HF.COSTMULT[k] = 4.0 if k.endswith('C') else 2.5
    if 'q' in L:   # W18 pool prices: entry and pool rows 2.5x, capstones 4x (round-two settings below override)
        for k in POOL_ROWS: HF.COSTMULT[k] = 2.5
        for k in CAPSTONES: HF.COSTMULT[k] = 4.0
    if 'a' in L:   # rows that host a condition cost as deciders do
        for k in ('CP21', 'MS08', 'AE20'): HF.COSTMULT[k] = 1.0
    if not hasattr(HF, 'SPACE_BASE'): HF.SPACE_BASE = HF.PRICE['Space']
    HF.PRICE['Space'] = HF.SPACE_BASE * float(os.environ.get('SPACEPRICE') or 1.0)   # every Space-era row's cost derives from it
    if 'w' in L: HF.COSTMULT['MS17'] = float(os.environ.get('WROWX', '2.5'))      # Wormhole's engineering row outside its tests
    if 'x' in L: HF.COSTMULT['ES18'] = 1.0
    if 'p' in L: HF.COSTMULT['AE14'] = 1.0
    if 'h' in L: HF.COSTMULT['MA19'] = 1.0    # round two: Hyperspace's Higher-Dimensional Geometry at 1x
    if 'u' in L: HF.COSTMULT['CP16'] = 1.0    # round two: Tunnelling's Planetary Data Networks at 1x
    if 'k' in L: HF.COSTMULT['TH20'] = 4.0    # round two: elemental Tachyonic's Boundary Ring at 4x
    if 'm' in L: HF.COSTMULT['CP10'] = 2.0    # agreed nudge: Tunnelling's Quantum Computing at 2x
