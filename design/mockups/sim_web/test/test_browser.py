"""engine.js in the browser: pyrandom.js and engine.js loaded as plain scripts (no modules) in Chromium, window.UHEngine
plays a generalist game and an advisor game to the end, and the results must equal Node's for the same games
(node test/browser_ref.js writes them). Usage (from design/mockups/sim_web):
  node test/browser_ref.js > /tmp/x.json && python3 test/test_browser.py /tmp/x.json
Needs Playwright (pip install playwright==1.56.0) with the Chromium at /opt/pw-browsers."""
import sys, os, json
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
ref = json.load(open(sys.argv[1]))
js = lambda f: open(os.path.join(ROOT, f), encoding='utf-8').read()
html = ('<!doctype html><meta charset="utf-8"><title>engine test</title><body>'
        '<script>window.BUNDLE = ' + js('bundle.json') + ';</script>'
        '<script>' + js('pyrandom.js') + '</script><script>' + js('engine.js') + '</script></body>')
with sync_playwright() as p:
    exe = '/opt/pw-browsers/chromium' if os.path.exists('/opt/pw-browsers/chromium') else None
    try: browser = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
    except Exception: browser = p.chromium.launch()
    page = browser.new_page(); errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.set_content(html)
    out = page.evaluate("""() => {
        const res = {};
        for (const [label, o] of [['generalist', {world: 'Process', econ: 0.8, game: 7, player: 'generalist'}],
                                  ['advisor', {world: 'familiar', econ: 1.0, game: 12, player: 'advisor'}]]) {
            const e = new window.UHEngine(window.BUNDLE, o);
            while (!e.over) { e.step(); const a = e.advise(); if (o.player === 'advisor' && a.prototype) e.commitPrototype(a.prototype); }
            res[label] = {t: Object.fromEntries([...e.S.have].map(([k, v]) => [k, v.turn])), victory: e.victory, turn: e.turn,
                          snapshotKeys: Object.keys(e.snapshot()).length};
        }
        return {res, hasEngine: typeof window.UHEngine === 'function', hasRandom: typeof window.PyRandom === 'function'};
    }""")
    browser.close()
bad = errors[:]
if not (out['hasEngine'] and out['hasRandom']): bad.append('window.UHEngine or window.PyRandom missing')
for label in ('generalist', 'advisor'):
    a, b = out['res'][label], ref[label]
    if a['t'] != b['t']: bad.append(f'{label}: discovery turns differ from Node')
    if a['victory'] != b['victory']: bad.append(f'{label}: victory differs from Node ({a["victory"]} vs {b["victory"]})')
    print(f'browser {label}: {len(a["t"])} rows discovered by turn {a["turn"]}, victory {a["victory"] and a["victory"]["turn"]}; '
          f'{"identical to Node" if a["t"] == b["t"] and a["victory"] == b["victory"] else "DIFFERS from Node"}')
print('browser test:', 'FAILED ' + '; '.join(bad) if bad else 'passed')
sys.exit(1 if bad else 0)
