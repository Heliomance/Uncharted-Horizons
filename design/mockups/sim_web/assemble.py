"""Build the web mockups as single self-contained files (the artifact sandbox blocks every fetch), in dist/:

  replay.html        the replay viewer: style.css, the DejaVu Sans subset as a data URI, view.js, screen.js, ftl.js, replay.js,
                     the bundle's rows, foci, eras, worlds, ftl, victory and economy, and the sample logs in traces/
  play.html          the live game (src/play.html, play.js): style.css and the font, pyrandom.js, engine.js, the same screens
                     (view.js, screen.js, ftl.js) and play.js, with the whole bundle, the world truths included (the engine
                     draws each game's truth from them); skipped, with a note, while play.js or engine.js is missing
  *.local.html       each page wrapped in a full HTML document, for opening locally and for the Playwright tests

The published pages have no <html>, <head> or <body> (the artifact publisher wraps them): they start with <title> and the
viewport-fit meta. Run: python3 design/mockups/sim_web/assemble.py
"""
import base64, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda *a: os.path.join(HERE, *a)
FONT = os.path.normpath(os.path.join(HERE, '..', 'research_screen', 'canvas', 'DejaVuSansUH-subset.woff2'))

PAGES = {
    'replay': dict(template='src/replay.html', scripts=['view.js', 'screen.js', 'ftl.js', 'replay.js'], need=['replay.js'],
                   bundle_keys=['version', 'eras', 'foci', 'rows', 'worlds', 'model', 'ftl', 'victory', 'economy', 'settings'], traces=True),
    'play': dict(template='src/play.html', scripts=['pyrandom.js', 'pysum.js', 'engine.js', 'view.js', 'screen.js', 'ftl.js', 'play.js'],
                 need=['play.js', 'engine.js'], bundle_keys=None, traces=False),
}


def json_for_script(obj):
    """JSON safe inside <script type="application/json">: no '</' and no '<!--' (both valid JSON escapes)"""
    s = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    return s.replace('</', '<\\/').replace('<!--', '<\\u0021--')


def replay_bundle(bundle, keys):
    b = {k: bundle[k] for k in keys if k in bundle}
    # the replay never draws world truths (the log carries its own): drop them, they are a fifth of the bundle
    b['ftl'] = {k: ({kk: vv for kk, vv in v.items() if kk != 'TRUTHS'} if isinstance(v, dict) and 'TRUTHS' in v else v) for k, v in bundle['ftl'].items()}
    return b


def build(name, spec, bundle, font_uri):
    tpl_path = P(spec['template'])
    missing = [f for f in [spec['template']] + spec['need'] if not os.path.exists(P(f))]
    if missing:
        print(f'{name}: skipped ({", ".join(missing)} not written yet)')
        return None
    tpl = open(tpl_path, encoding='utf-8').read()
    css = open(P('style.css'), encoding='utf-8').read().replace('__FONT_URL__', font_uri)
    scripts = []
    for f in spec['scripts']:
        if os.path.exists(P(f)):
            js = open(P(f), encoding='utf-8').read()
            assert '</script' not in js.lower(), f + ' contains </script'
            scripts.append(f'<script>\n/* {f} */\n{js}\n</script>')
    b = replay_bundle(bundle, spec['bundle_keys']) if spec['bundle_keys'] else bundle
    data = [f'<script type="application/json" id="uh-bundle">{json_for_script(b)}</script>']
    if spec['traces']:
        traces = []
        for f in sorted(os.listdir(P('traces'))):
            if f.endswith('.json'):
                traces.append(dict(id=f[:-5], trace=json.load(open(P('traces', f), encoding='utf-8'))))
        order = {'expert': 0, 'novice': 1, 'average': 2}
        traces.sort(key=lambda t: order.get(t['id'].split('_')[0], 9))
        data.append(f'<script type="application/json" id="uh-traces">{json_for_script(traces)}</script>')
    for ph in ('/*__CSS__*/', '<!--__DATA__-->', '<!--__SCRIPTS__-->'):
        assert tpl.count(ph) == 1, f'{spec["template"]} must hold {ph} exactly once'
    page = tpl.replace('/*__CSS__*/', css).replace('<!--__DATA__-->', '\n'.join(data)).replace('<!--__SCRIPTS__-->', '\n'.join(scripts))
    assert page.lstrip().startswith('<title>'), 'the page must start with its <title>'
    assert 'name="claude:viewport-fit-sides"' in page[:400], 'the page must carry the viewport-fit meta after its <title>'
    os.makedirs(P('dist'), exist_ok=True)
    out = P('dist', name + '.html')
    open(out, 'w', encoding='utf-8').write(page)
    # the local copy: the publisher's skeleton (charset, viewport with viewport-fit=cover, a small reset) around the page
    head_end = page.index('</style>') + len('</style>')
    local = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
             '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
             '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n'
             + page[:head_end] + '\n</head>\n<body>\n' + page[head_end:] + '\n</body>\n</html>\n')
    open(P('dist', name + '.local.html'), 'w', encoding='utf-8').write(local)
    print(f'{out}: {os.path.getsize(out) / 1e6:.2f} MB ({len(scripts)} scripts{", " + str(len(traces)) + " sample logs" if spec["traces"] else ""})')
    return out


def main():
    bundle = json.load(open(P('bundle.json'), encoding='utf-8'))
    font_uri = 'data:font/woff2;base64,' + base64.b64encode(open(FONT, 'rb').read()).decode('ascii')
    names = sys.argv[1:] or list(PAGES)
    for n in names:
        build(n, PAGES[n], bundle, font_uri)


if __name__ == '__main__':
    main()
