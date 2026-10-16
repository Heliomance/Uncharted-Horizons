"""The replay viewer, played in Chromium (Playwright). Run after assemble.py:
  python3 design/mockups/sim_web/test/test_replay.py
Checks, with no console errors throughout: every sample log steps through every turn, in both views; at the last turn the
owned count equals the rows the log found, the FTL screen is certain on the log's turn, and the chart's launch turn equals
victory.py's (re-derived here from the bundle, as victory.py computes it; test/check_victory.py checks it against
victory.py itself); the player view shows no hidden rows and no row ids; Play runs a whole log to its end; Next event
lands on a turn with an event; selecting a chip describes it; a log loads from a file and from the paste box, and bad
input shows an error; no horizontal scroll at 400 px. Screenshots go to test/shots/.
"""
import json, math, os, re, sys, time
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAGE = 'file://' + os.path.join(ROOT, 'dist', 'replay.local.html')
SHOTS = os.path.join(HERE, 'shots')
os.makedirs(SHOTS, exist_ok=True)
BUNDLE = json.load(open(os.path.join(ROOT, 'bundle.json'), encoding='utf-8'))
ORDER = ['expert_familiar_Warp', 'novice_Process_Plenum', 'average_Substance_Wormhole']   # assemble.py's order of the samples
TRACES = {n: json.load(open(os.path.join(ROOT, 'traces', n + '.json'), encoding='utf-8')) for n in ORDER}
ROW_ID = re.compile(r'\b(?:QM-E|NP-F|MD-V|[A-Z]{1,3})\d{2}[A-Z]?(?:-W)?\b')
fails = []


def check(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg)
    if not cond: fails.append(msg)


def victory(t):
    """victory.py's victory(): the race's finish, the prototype, the SS FTL Drive and a turn to launch"""
    V = BUNDLE['victory']; key = '%.1f' % t['econ']; E = BUNDLE['economy'][key]
    fin = max(t['cert'][0], t['built'])
    price = V['protox'] * V['p_space'] * V['scale'] * V['spaceprice'] * 4 ** max(0, V['space'] - E['d'][fin])
    proto = fin + math.ceil(price / (0.8 * E['inc'][fin + 1]))
    return proto + V['drive'][key]['exotic' if t['m'] in V['exotic'] else 'plain'][proto] + 1


def goto_turn(pg, t):
    pg.evaluate("t => { const s = document.getElementById('rp-slider'); s.value = t; s.dispatchEvent(new Event('input')); }", t)


def player_text_has_ids(pg):
    txt = pg.evaluate("document.getElementById('uh-app').innerText")
    return ROW_ID.findall(txt)


with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1440, 'height': 810})
    errors = []
    pg.on('console', lambda m: errors.append(m.type + ': ' + m.text) if m.type in ('error', 'warning') else None)
    pg.on('pageerror', lambda e: errors.append('pageerror: ' + str(e)))
    pg.goto(PAGE)
    pg.wait_for_selector('.uh-screen')
    pg.screenshot(path=os.path.join(SHOTS, 'desk_expert_t001.png'))

    for i, name in enumerate(ORDER):
        t = TRACES[name]
        print(name)
        pg.select_option('#rp-sample', str(i))
        pg.wait_for_timeout(100)
        first, last = t['records'][0]['turn'], t['records'][-1]['turn']
        check(pg.inner_text('#rp-of') == 'of %d' % last, 'the slider spans the log (of %d)' % last)
        t0 = time.time(); bad = 0; leaked = []; hidden_in_player = 0; hidden_in_engine = 0
        for T in range(first, last + 1):
            goto_turn(pg, T)
            if pg.inner_text('#rp-turn') != 'Turn %d' % T: bad += 1
            if T % 40 == 0:
                leaked += player_text_has_ids(pg)
                hidden_in_player += pg.locator('.uh-chip.is-hidden').count()
                pg.click('[data-view=engine]')
                hidden_in_engine += pg.locator('.uh-chip.is-hidden').count()
                pg.click('[data-view=player]')
        dt = time.time() - t0
        check(bad == 0, 'stepped through all %d turns (%.1f s, %.0f ms a turn)' % (last - first + 1, dt, 1000 * dt / (last - first + 1)))
        check(not leaked, 'no row ids in the player view' + (': ' + ', '.join(sorted(set(leaked))[:8]) if leaked else ''))
        check(hidden_in_player == 0, 'no hidden rows in the player view')
        check(hidden_in_engine > 0, 'the engine view shows hidden rows (%d chips over the sampled turns)' % hidden_in_engine)
        found = sum(len(r['found']) for r in t['records'])
        owned = int(pg.inner_text('.uh-seg[data-filter=owned] .uh-seg-n'))
        check(owned == found, 'owned at the last turn %d = rows the log found %d' % (owned, found))
        cert = pg.locator('.ftl-certain').inner_text() if pg.locator('.ftl-certain').count() else ''
        check(('turn %d' % t['cert'][0]) in cert and t['m'] in cert, 'the FTL screen is certain of %s on turn %d: "%s"' % (t['m'], t['cert'][0], cert.strip()))
        chart = pg.inner_text('#rp-chart') if False else pg.evaluate("document.getElementById('rp-chart').textContent")
        v = victory(t)
        check(('Launch %d' % v) in chart, 'the chart marks the launch on turn %d (victory.py)' % v)
        check(('turn %d' % v) in pg.inner_text('#rp-summary'), 'the summary reports victory on turn %d' % v)
        check(('Certain %d' % t['cert'][0]) in chart and ('Build complete %d' % t['built']) in chart, 'the chart marks certainty and the build')

    # Play runs the expert's log to its end
    pg.select_option('#rp-sample', '0')
    pg.select_option('#rp-speed', '25')
    pg.click('#rp-start')
    t0 = time.time()
    pg.click('#rp-play')
    pg.wait_for_function("document.getElementById('rp-turn').textContent === 'Turn 277'", timeout=40000)
    pg.wait_for_timeout(150)
    check(pg.inner_text('#rp-play .rp-play-label') == 'Play', 'Play ran the whole log to turn 277 in %.1f s and stopped' % (time.time() - t0))

    # Next event lands on a turn whose events include an era, a focus, an FTL change or an Endeavour
    pg.click('#rp-start')
    pg.click('#rp-next')
    T = int(pg.inner_text('#rp-turn').split()[1])
    kinds = pg.evaluate("[...document.querySelectorAll('.uh-events li')].map(li => li.className)")
    check(T > 1 and any(k.startswith(('ev-era', 'ev-focus', 'ev-ftl', 'ev-endeavour', 'ev-finish')) for k in kinds), 'Next event went to turn %d: %s' % (T, kinds))
    for _ in range(6): pg.click('#rp-next')
    T2 = int(pg.inner_text('#rp-turn').split()[1])
    check(T2 > T, 'Next event moves on (turn %d)' % T2)

    # selecting a chip describes it in the bottom bar; selecting a focus describes the focus
    goto_turn(pg, 200)
    chip = pg.locator('.uh-chip.st-studying').first
    name_ = chip.locator('.uh-chip-name').inner_text()
    chip.click()
    check(pg.inner_text('.uh-desc-title') == name_, 'clicking %s describes it' % name_)
    check(pg.locator('.uh-act[data-act=endeavour]').count() == 0 or pg.locator('.uh-act[data-act=endeavour]').first.is_disabled(), 'the replay is read-only')
    pg.locator('.uh-focus-name').first.click()
    check(pg.locator('.uh-desc-title').inner_text() == pg.locator('.uh-focus-name').first.inner_text(), 'clicking a focus describes it')
    pg.screenshot(path=os.path.join(SHOTS, 'desk_expert_t200_selected.png'))

    # loading a log: from a file, then a bad paste, then a good paste
    pg.set_input_files('#rp-file', os.path.join(ROOT, 'traces', 'novice_Process_Plenum.json'))
    pg.wait_for_function("document.getElementById('rp-headline').textContent.startsWith('Novice')")
    check('Novice' in pg.inner_text('#rp-headline') and pg.inner_text('#rp-of') == 'of 292', 'a log loads from a file')
    pg.click('#rp-paste-toggle')
    pg.fill('#rp-paste-text', '{"not": "a log"}')
    pg.click('#rp-paste-load')
    check(pg.is_visible('#rp-error') and 'not a simulator log' in pg.inner_text('#rp-error'), 'a bad paste shows an error: ' + pg.inner_text('#rp-error'))
    pg.fill('#rp-paste-text', open(os.path.join(ROOT, 'traces', 'average_Substance_Wormhole.json'), encoding='utf-8').read())
    pg.click('#rp-paste-load')
    pg.wait_for_timeout(200)
    check(not pg.is_visible('#rp-error') and pg.inner_text('#rp-of') == 'of 358', 'a pasted log loads')

    # desktop screenshots
    shots = [('desk_expert_t230_engine.png', 0, 230, True, None), ('desk_novice_t270_endeavour.png', 1, 270, False, None),
             ('desk_expert_t277_ftl.png', 0, 277, False, 650), ('desk_average_t358.png', 2, 358, False, None)]
    for fn, i, T, eng, ftl_scroll in shots:
        pg.select_option('#rp-sample', str(i)); goto_turn(pg, T)
        pg.click('[data-view=%s]' % ('engine' if eng else 'player'))
        if ftl_scroll: pg.evaluate("y => { document.querySelector('.ftl-scroll').scrollTop = y; }", ftl_scroll)
        pg.wait_for_timeout(100)
        pg.screenshot(path=os.path.join(SHOTS, fn))
    pg.click('[data-view=player]')
    pg.screenshot(path=os.path.join(SHOTS, 'desk_average_full.png'), full_page=True)

    # the phone
    ph = b.new_page(viewport={'width': 400, 'height': 800})
    ph.on('console', lambda m: errors.append('phone ' + m.type + ': ' + m.text) if m.type in ('error', 'warning') else None)
    ph.on('pageerror', lambda e: errors.append('phone pageerror: ' + str(e)))
    ph.goto(PAGE)
    ph.wait_for_selector('.uh-screen')
    over = []
    for i, T in ((0, 1), (0, 150), (0, 277), (1, 270), (2, 300)):
        ph.select_option('#rp-sample', str(i)); goto_turn(ph, T)
        sw, cw = ph.evaluate('[document.documentElement.scrollWidth, document.documentElement.clientWidth]')
        if sw > cw: over.append((i, T, sw))
    check(not over, 'no horizontal scroll at 400 px' + (': ' + str(over) if over else ''))
    ph.select_option('#rp-sample', '0'); goto_turn(ph, 150)
    ph.screenshot(path=os.path.join(SHOTS, 'phone_expert_t150.png'))
    ph.screenshot(path=os.path.join(SHOTS, 'phone_expert_t150_full.png'), full_page=True)
    ph.select_option('#rp-sample', '1'); goto_turn(ph, 270); ph.click('[data-view=engine]')
    ph.evaluate("window.scrollTo(0, document.querySelector('.uh-screen').getBoundingClientRect().top + window.scrollY - 8)")
    ph.screenshot(path=os.path.join(SHOTS, 'phone_novice_t270_engine.png'))
    ph.evaluate("window.scrollTo(0, document.querySelector('.uh-ftl').getBoundingClientRect().top + window.scrollY - 8)")
    ph.screenshot(path=os.path.join(SHOTS, 'phone_novice_t270_ftl.png'))

    check(not errors, 'no console errors' + (': ' + '; '.join(errors[:5]) if errors else ''))
    b.close()

print('\n%d failed' % len(fails) if fails else '\nall passed')
sys.exit(1 if fails else 0)
