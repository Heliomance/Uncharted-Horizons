"""The screens' live-game API, in Chromium: view.js, screen.js and ftl.js loaded on a bare page with the bundle, driven as
play.js will drive them (not read-only), on snapshots rebuilt from a sample log. Checks that the fund radio, Fund
button, Grand Endeavour (with a quote), Stop, Faster than light and Commit buttons call their callbacks with the right
arguments, that a refused quote disables the Endeavour with its reason, and that selection survives a re-render.
  python3 design/mockups/sim_web/test/test_api.py
"""
import json, os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
js = lambda f: open(os.path.join(ROOT, f), encoding='utf-8').read()
html = ('<!doctype html><html><head><meta charset="utf-8"><style>' + js('style.css').replace("url(__FONT_URL__) format('woff2')", "local('DejaVu Sans')") + '</style></head><body>'
        '<div id="s"></div><div id="f"></div><script type="application/json" id="b">' + js('bundle.json').replace('</', '<\\/') + '</script>'
        '<script type="application/json" id="t">' + js('traces/novice_Process_Plenum.json').replace('</', '<\\/') + '</script>'
        + ''.join('<script>' + js(f) + '</script>' for f in ('view.js', 'screen.js', 'ftl.js', 'replay.js')) + '</body></html>')
fails = []
def check(c, m):
    print(('  ok   ' if c else '  FAIL ') + m)
    if not c: fails.append(m)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1440, 'height': 900})
    errors = []
    pg.on('pageerror', lambda e: errors.append(str(e))); pg.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    pg.set_content(html)
    pg.evaluate("""() => {
      const bundle = JSON.parse(document.getElementById('b').textContent), trace = JSON.parse(document.getElementById('t').textContent);
      const g = UHReplay.reconstruct(bundle, trace);
      window.calls = [];
      const quote = id => id.startsWith('QM') ? { cost: 1234, turns: 3 } : { reason: 'a test refusal' };
      window.screen1 = UHScreen.create(document.getElementById('s'), { onFund: f => calls.push(['fund', f]), onEndeavour: id => calls.push(['endeavour', id]),
        onStopEndeavour: () => calls.push(['stop']), onSelect: s => calls.push(['select', s]), onOpenFtl: () => calls.push(['ftl']) });
      window.ftl1 = UHFtl.create(document.getElementById('f'), { onCommit: m => calls.push(['commit', m]) });
      window.show = T => { const s = g.snapshot(T); screen1.render(UHView.researchModel(bundle, s, { quote }));
        ftl1.render(UHView.ftlModel(bundle, s, { truth: trace.truth, instrD: trace.instr_d, canCommit: m => ({ ok: true }) })); };
      show(260);
    }""")
    pg.click('.uh-focus:not(.is-funded) .uh-radio')
    check(pg.evaluate('calls.at(-1)[0]') == 'fund', 'the fund radio calls onFund(%s)' % pg.evaluate('calls.at(-1)[1]'))
    pg.locator('.uh-chip.st-studying').first.click()
    check(pg.evaluate('calls.at(-1)[0]') == 'select', 'a chip calls onSelect(%s)' % pg.evaluate('calls.at(-1)[1]'))
    btn = pg.locator('.uh-act[data-act=fund]')
    if btn.count() and btn.first.is_enabled():
        btn.first.click(); check(pg.evaluate('calls.at(-1)[0]') == 'fund', 'the Fund button calls onFund')
    en = pg.locator('.uh-act[data-act=endeavour]').first
    check(en.count() == 1, 'an idea under study offers a Grand Endeavour')
    sub = en.locator('.uh-act-l2').inner_text()
    check(('a test refusal' in sub and en.is_disabled()) or ('1,234 Insight' in sub and en.is_enabled()), 'the Endeavour button carries the quote or its refusal: ' + sub)
    waiting = pg.locator('.uh-chip.st-waiting').filter(has_text='').all()
    clicked = None
    for c in pg.locator('.uh-chip').all():
        c.click()
        e = pg.locator('.uh-act[data-act=endeavour]')
        if e.count() and e.first.is_enabled(): clicked = pg.inner_text('.uh-desc-title'); e.first.click(); break
    check(clicked is not None and pg.evaluate('calls.at(-1)[0]') == 'endeavour', 'Begin Grand Endeavour calls onEndeavour(%s) for %s' % (pg.evaluate('calls.at(-1)[1]'), clicked))
    sel = pg.inner_text('.uh-desc-title')
    pg.evaluate('show(261)')
    check(pg.inner_text('.uh-desc-title') == sel, 'the selection survives a new turn (%s)' % sel)
    pg.click('.uh-ftl-btn'); check(pg.evaluate('calls.at(-1)[0]') == 'ftl', 'the Faster than light button calls onOpenFtl')
    pg.evaluate('show(270)')   # the novice's Endeavour on Higher Strata Theory runs on turn 270
    pg.locator('.uh-chip.st-endeavour').first.click()
    stop = pg.locator('.uh-act[data-act=stop]')
    check(stop.count() == 1 and stop.is_enabled(), 'a running Endeavour offers Stop')
    stop.click(); check(pg.evaluate('calls.at(-1)[0]') == 'stop', 'Stop calls onStopEndeavour')
    pg.evaluate('show(291)')   # certain and built: Plenum's prototype can be committed
    c = pg.locator('[data-commit]:not([disabled])')
    check(c.count() >= 1, 'a complete, standing hypothesis can be committed (%d)' % c.count())
    if c.count(): c.first.click(); check(pg.evaluate('calls.at(-1)') == ['commit', 'Plenum'], 'Commit calls onCommit(%s)' % pg.evaluate('calls.at(-1)'))
    check(not errors, 'no console errors' + (': ' + '; '.join(errors[:3]) if errors else ''))
    b.close()
print('\n%d failed' % len(fails) if fails else '\nall passed'); sys.exit(1 if fails else 0)
