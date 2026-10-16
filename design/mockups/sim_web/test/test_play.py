"""The live game, played in Chromium (Playwright). Run after assemble.py:
  python3 design/mockups/sim_web/test/test_play.py

Three games, with no console errors throughout:
  1. Desktop 1440x810, familiar world, good economy, diffusion on, a typed seed: 20 turns played by hand (clicking focus
     radios, a chip's Fund button and a Grand Endeavour), then Fast-forward with the Advisor until a prototype can be
     committed for the method the FTL screen is certain of, the FTL screen opened, the prototype committed through the
     warning dialog, and fast-forwarded to victory. Also checked: the queue (the funded focus running dry hands funding to
     the next focus in line, and the notice says so), the engine view, no row ids in the player's view, reload continues the
     saved game, the game's log copies (through the selectable-text fallback) and loads in the replay viewer.
  2. Desktop, Process world (elemental), good economy, diffusion off: fast-forward to a hypothesis that can be committed
     before anything is certain, commit it through the Hail Mary warning, see it fail and its method ruled out, then
     fast-forward, commit the true method and win; the victory screen lists the failed prototype.
  3. Phone 400x800, Substance world (elemental), average economy: setup, a few turns by tapping, fast-forward, the FTL
     screen in place of the research screen, commit, victory; no horizontal scroll.
Victory turns are reported against base Civ V's 305 (good economy) and 380 (average), with the time a turn takes to
compute and to draw in the browser. Screenshots go to test/shots/play_*.png.
"""
import json, os, re, sys, time
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAGE = 'file://' + os.path.join(ROOT, 'dist', 'play.local.html')
REPLAY = 'file://' + os.path.join(ROOT, 'dist', 'replay.local.html')
SHOTS = os.path.join(HERE, 'shots')
os.makedirs(SHOTS, exist_ok=True)
ROW_ID = re.compile(r'\b(?:QM-E|NP-F|MD-V|[A-Z]{1,3})\d{2}[A-Z]?(?:-W)?\b')
fails, report = [], []


def check(cond, msg):
    print(('  ok   ' if cond else '  FAIL ') + msg, flush=True)
    if not cond: fails.append(msg)


def shot(pg, name, full=False):
    pg.screenshot(path=os.path.join(SHOTS, 'play_' + name + '.png'), full_page=full)


def turn(pg): return pg.evaluate('UHPlay.engine.turn')
def idle(pg, timeout=120000): pg.wait_for_function('!UHPlay.state.running', timeout=timeout)
def notice(pg): return pg.inner_text('#pl-notice')


def ids_in_player_view(pg):
    txt = pg.evaluate("document.getElementById('uh-app').innerText")
    return sorted(set(ROW_ID.findall(txt)))


def setup(pg, world, econ, diffusion, seed=None):
    if pg.is_hidden('#pl-setup'): pg.click('#pl-new')
    pg.check('input[name=pl-world][value="%s"]' % world)
    pg.check('input[name=pl-econ][value="%s"]' % econ)
    if pg.is_checked('#pl-diff') != diffusion: pg.click('#pl-diff')
    if seed is not None:
        pg.fill('#pl-seed', str(seed)); pg.check('input[name=pl-seedmode][value=typed]')
    else: pg.check('input[name=pl-seedmode][value=random]')
    pg.click('#pl-start')
    pg.wait_for_selector('.uh-screen')
    check(turn(pg) == 0, '%s world, economy %s, diffusion %s: the game starts on turn 0' % (world, econ, 'on' if diffusion else 'off'))


def certain_and_committable(pg):
    """the FTL screen's certainty and whether its method's prototype can be committed now (from the engine, as the page checks)"""
    return pg.evaluate("""() => { const e = UHPlay.engine, st = e.S.have.has(e.OPENS) ? e.status(e.S.have, e.turn) : null;
      if (!st || !st.certain) return null; const m = st.alive.length === 1 ? st.alive[0] : e.METHODS.find(o => e.F.COND[o].every(c => st.kn[c]));
      return { m, can: !e.prototypeCheck(m), turn: e.turn }; }""")


def fast_forward_to_commit(pg, label):
    """Fast-forward with the Advisor, milestone by milestone, until the certain method's prototype can be committed"""
    stops = []
    for _ in range(40):
        c = certain_and_committable(pg)
        if c and c['can']: break
        t0 = time.time(); pg.click('#pl-ff'); idle(pg)
        stops.append('%d: %s' % (turn(pg), notice(pg).split('\n')[1] if '\n' in notice(pg) else notice(pg)))
        if pg.evaluate('UHPlay.engine.over'): break
    for s in stops: print('     ff ->', s[:150])
    c = certain_and_committable(pg)
    check(c and c['can'], label + ': the Advisor fast-forwards to a committable, certain prototype (turn %s)' % (c and c['turn']))
    return c


def commit(pg, method, label, phone=False):
    if pg.is_hidden('#pl-ftl'): pg.click('#pl-ftltab')
    pg.wait_for_selector('#pl-ftl:not([hidden]) .uh-ftl')
    btn = pg.locator('[data-commit="%s"]' % method)
    check(btn.count() == 1 and btn.is_enabled(), label + ': the FTL screen offers Commit to a prototype for ' + method)
    btn.scroll_into_view_if_needed()
    btn.click()
    pg.wait_for_selector('#pl-modal:not([hidden])')
    txt = pg.inner_text('#pl-dialog')
    check('Commit to a ' + method + ' prototype?' in txt, label + ': the commit asks first: ' + txt.split('\n')[0])
    check('certain' in txt or 'returns nothing' in txt, label + ': the dialog says whether it is certain, or warns that a failed prototype returns nothing')
    pg.click('#pl-dialog button:has-text("Commit")')
    check(pg.is_hidden('#pl-modal') and pg.evaluate('!!UHPlay.engine.S.proto'), label + ': the prototype is under construction')


def play_to_victory(pg, label, ref, phone=False):
    for _ in range(10):
        if pg.evaluate('!!UHPlay.engine.victory') or pg.evaluate('UHPlay.engine.over'): break
        if not pg.is_hidden('#pl-modal'): pg.click('#pl-dialog button:last-child')
        pg.click('#pl-ff'); idle(pg)
    v = pg.evaluate('UHPlay.engine.victory')
    check(v is not None, label + ': victory')
    if not v: return None
    pg.wait_for_selector('#pl-modal:not([hidden]) .is-victory')
    txt = pg.inner_text('#pl-dialog')
    check(('Victory on turn %d' % v['turn']) in txt and str(ref) in txt, label + ': the victory screen gives the launch turn and base Civ V\'s %d' % ref)
    check('Discoveries' in txt and 'Grand Endeavours' in txt and 'Prototypes failed' in txt and v['method'] in txt, label + ': it gives the method, the discoveries, the Endeavours and the failed prototypes')
    return v


def timings(pg):
    return pg.evaluate("""() => { const med = xs => { const s = xs.slice().sort((a, b) => a - b); return s.length ? s[s.length >> 1] : null; };
      const st = UHPlay.stats; return { step: med(st.step), render: med(st.render), n: st.step.length, maxStep: Math.max(...st.step) }; }""")


with sync_playwright() as p:
    b = p.chromium.launch()
    errors = []

    def page(w, h, ctx=None):
        ctx = ctx or b.new_context(viewport={'width': w, 'height': h})
        pg = ctx.new_page()
        pg.on('console', lambda m: errors.append(m.type + ': ' + m.text) if m.type in ('error', 'warning') else None)
        pg.on('pageerror', lambda e: errors.append('pageerror: ' + str(e)))
        return ctx, pg

    # ------------------------------------------------------------------ game 1: by hand, then the Advisor, to victory
    print('game 1: familiar world, good economy, diffusion on, seed 17012 (desktop)')
    ctx, pg = page(1440, 810)
    pg.goto(PAGE)
    pg.evaluate('localStorage.clear()'); pg.reload()
    pg.wait_for_selector('#pl-setup:not([hidden])')
    shot(pg, 'desk_setup')
    setup(pg, 'familiar', '1.0', True, 17012)
    check(pg.evaluate('UHPlay.engine.seed') == 17012 and pg.evaluate('UHPlay.engine.game') == 12, 'the typed seed is the simulator\'s game 12')
    shot(pg, 'desk_t000')
    # the queue: fund a focus with one idea under study, line up another, and play until the first runs dry
    pg.locator('.uh-focus:has(.uh-focus-name:text-is("Fire")) .uh-radio').click()
    check(pg.evaluate('UHPlay.engine.S.choice') == 'Fire', 'clicking the Fire radio funds Fire')
    pg.select_option('#pl-queue-add', 'Foraging')
    check(pg.locator('.pl-qchip').count() == 1, 'Foraging is next in line')
    hand_turns, endeavour, dry_seen = 0, None, []
    while hand_turns < 20:
        t = turn(pg)
        if t in (4, 9, 15):     # choose another focus with revealed work by its radio
            radios = pg.locator('.uh-focus:not(.is-funded) .uh-radio:not([disabled])')
            for i in range(radios.count()):
                badge = radios.nth(i).locator('xpath=..').locator('.uh-badge:not(.is-hidden)')
                if badge.count():
                    radios.nth(i).click(); break
        if t == 15:             # and line up the focus with the most revealed work after it
            best = pg.evaluate("""() => [...document.querySelectorAll('.uh-focus:not(.is-funded)')].map(el => [el.querySelector('.uh-focus-name').textContent,
              +((el.querySelector('.uh-badge:not(.is-hidden)') || {}).textContent || 0)]).sort((a, b) => b[1] - a[1])[0][0]""")
            opt = pg.evaluate("n => [...document.querySelectorAll('#pl-queue-add option')].find(o => o.textContent === n).value", best)
            pg.select_option('#pl-queue-add', opt)
            queued = opt
        if t == 7:              # select a chip and fund its focus from the bar
            pg.locator('.uh-chip.st-studying').last.click()
            fb = pg.locator('.uh-act[data-act=fund]')
            if fb.count() and fb.first.is_enabled(): fb.first.click()
        if t == 11 and endeavour is None:   # a Grand Endeavour on a revealed breakthrough
            for c in pg.locator('.uh-chip.st-studying, .uh-chip.st-waiting').all():
                c.click()
                en = pg.locator('.uh-act[data-act=endeavour]')
                if en.count() and en.first.is_enabled():
                    endeavour = pg.inner_text('.uh-desc-title'); sub = en.first.locator('.uh-act-l2').inner_text()
                    en.first.click(); break
            check(endeavour is not None, 'turn 11: a Grand Endeavour begins on %s (%s)' % (endeavour, sub if endeavour else ''))
            check(pg.locator('.uh-fund-slot.is-endeavour').count() == 1, 'the funding card shows the Endeavour')
            shot(pg, 'desk_t011_endeavour')
        pg.click('#pl-next'); idle(pg)
        hand_turns += 1
        if 'Nothing revealed is left under study' in notice(pg).split('\n')[1] and notice(pg).split('\n')[0] == 'Turn %d' % turn(pg):
            dry_seen.append((turn(pg), notice(pg).split('\n')[1], pg.evaluate('UHPlay.engine.S.choice')))
    check(turn(pg) == 20, '20 turns played by hand (turn %d)' % turn(pg))
    for d in dry_seen:
        moved = re.search(r'funding moves to (.+?), next in line', d[1])
        check((moved and d[2] and moved.group(1).lower() == d[2].lower()) or ('Automatic' in d[1] and d[2] is None),
              'turn %d: the funded focus ran dry, the notice says so and funding moved as it says (%s): %s' % (d[0], d[2] or 'Automatic', d[1]))
    check(any('next in line' in d[1] for d in dry_seen), 'the line of foci was used when a funded focus ran dry')
    if not dry_seen: check(False, 'the funded focus never ran dry in 20 turns played by hand')
    ends = pg.evaluate('UHPlay.state.ui.ends')
    check(any(e[2] == 'start' for e in ends), 'the Endeavour started (%s)' % ends)
    check(not ids_in_player_view(pg), 'no row ids in the player view: %s' % ids_in_player_view(pg)[:5])
    shot(pg, 'desk_t020')
    # the engine view
    pg.click('[data-view=engine]')
    check(pg.locator('.uh-chip.is-hidden').count() > 0 and 'working method' in pg.inner_text('#pl-summary').lower(), 'the engine view shows hidden ideas (%d) and the working method' % pg.locator('.uh-chip.is-hidden').count())
    shot(pg, 'desk_t020_engine')
    pg.click('[data-view=player]')
    check(pg.locator('.uh-chip.is-hidden').count() == 0, 'the player view hides them again')
    # To the next event stops on an event
    t0 = turn(pg); pg.click('#pl-event'); idle(pg)
    check(turn(pg) > t0 and 'Stopped' in notice(pg), 'To the next event stops on turn %d: %s' % (turn(pg), ' '.join(notice(pg).split('\n')[:2])[:140]))
    t0 = turn(pg); pg.click('#pl-5'); idle(pg)
    check(turn(pg) == t0 + 5, '5 turns plays five turns (%d to %d)' % (t0, turn(pg)))
    # reload: the saved game carries on
    have0 = pg.evaluate('UHPlay.engine.S.have.size'); t0 = turn(pg)
    pg.reload(); pg.wait_for_selector('.uh-screen')
    check(turn(pg) == t0 and pg.evaluate('UHPlay.engine.S.have.size') == have0, 'reloading carries on the saved game (turn %d, %d discoveries)' % (turn(pg), have0))
    # Stop interrupts a run of turns
    t0 = turn(pg)
    pg.evaluate("() => { UHPlay.advance('ff'); setTimeout(() => document.getElementById('pl-stop').click(), 0); }"); idle(pg)
    check(t0 < turn(pg) < 150 and 'Stopped on turn %d' % turn(pg) in notice(pg), 'Stop interrupts a fast-forward (turn %d to %d)' % (t0, turn(pg)))
    # the game's log
    pg.click('#pl-logwrap summary'); pg.wait_for_selector('#pl-log li')
    n_log = pg.locator('#pl-log li').count()
    check(n_log > 50 and not ids_in_player_view(pg), 'the game\'s log lists %d events, newest first, with no row ids' % n_log)
    pg.click('#pl-logwrap summary')
    # the Advisor to the race's end
    t_ff = time.time()
    c = fast_forward_to_commit(pg, 'game 1')
    shot(pg, 'desk_certain')
    t0 = turn(pg); pg.click('#pl-ff')
    pg.wait_for_selector('#pl-modal:not([hidden])')
    check('The Advisor stops here' in pg.inner_text('#pl-dialog') and turn(pg) == t0, 'once the certain method can be committed, Fast-forward stops and offers the commit')
    pg.click('#pl-dialog button:has-text("Not yet")')
    check(pg.is_hidden('#pl-modal') and turn(pg) == t0 and not pg.evaluate('UHPlay.engine.S.proto'), 'Not yet commits nothing')
    pg.click('#pl-ftltab'); pg.wait_for_selector('#pl-ftl:not([hidden]) .uh-ftl')
    shot(pg, 'desk_ftl')
    check(not ids_in_player_view(pg), 'no row ids on the FTL screen: %s' % ids_in_player_view(pg)[:5])
    if c:
        commit(pg, c['m'], 'game 1')
        shot(pg, 'desk_prototype')
        v = play_to_victory(pg, 'game 1', 305)
        if v:
            shot(pg, 'desk_victory')
            tm = timings(pg)
            report.append('game 1 (familiar, good, diffusion on, seed 17012, %s): certain %s, committed %d, victory %d (%+d against 305); a turn %.2f ms to compute, %.1f ms to draw (medians over %d turns; slowest step %.1f ms)'
                          % (v['method'], pg.evaluate('UHPlay.engine.S.cert'), c['turn'], v['turn'], v['delta'], tm['step'], tm['render'], tm['n'], tm['maxStep']))
    print('     fast-forward and the endgame took %.1f s' % (time.time() - t_ff))
    # the log, copied (the clipboard is denied here, so through the selectable text) and loaded in the replay viewer
    if not pg.is_hidden('#pl-modal'): pg.click('#pl-dialog button:has-text("Look around")')
    pg.click('#pl-copylog')
    pg.wait_for_selector('#pl-modal:not([hidden]) #pl-copy-text')
    log_text = pg.input_value('#pl-copy-text')
    sel = pg.evaluate("(() => { const t = document.getElementById('pl-copy-text'); return t.selectionEnd - t.selectionStart; })()")
    check(sel == len(log_text) and len(log_text) > 1000, 'the log is offered as selected text (%d KB)' % (len(log_text) // 1024))
    log = json.loads(log_text)
    check(len(log['records']) == turn(pg) and log['m'] == v['method'] and log['player'] == 'human', 'the log has %d turn records, the method and the player' % len(log['records']))
    pg.click('#pl-dialog button:has-text("Done")')
    shot(pg, 'desk_after')
    rp = ctx.new_page()
    rp.on('pageerror', lambda e: errors.append('replay pageerror: ' + str(e)))
    rp.goto(REPLAY); rp.wait_for_selector('.uh-screen')
    rp.click('#rp-paste-toggle'); rp.fill('#rp-paste-text', log_text); rp.click('#rp-paste-load')
    rp.wait_for_timeout(300)
    check(rp.is_hidden('#rp-error'), 'the replay viewer loads the live game\'s log' + ('' if rp.is_hidden('#rp-error') else ': ' + rp.inner_text('#rp-error')))
    rp.evaluate("t => { const s = document.getElementById('rp-slider'); s.value = t; s.dispatchEvent(new Event('input')); }", log['records'][-1]['turn'])
    owned = rp.inner_text('.sec-owned .uh-sec-count')
    check(owned == str(len([1 for r in log['records'] for k in r['found']])), 'the replay shows the same discoveries at the last turn (%s)' % owned)
    rp.screenshot(path=os.path.join(SHOTS, 'play_desk_replay_of_live.png'))
    rp.close()
    # the save code copies and loads
    pg.click('#pl-copysave'); pg.wait_for_selector('#pl-copy-text')
    code = pg.input_value('#pl-copy-text'); pg.click('#pl-dialog button:has-text("Done")')
    check(json.loads(code)['format'] == 'uh-play-1', 'a save code is offered (%d KB)' % (len(code) // 1024))
    opts = json.loads(code)['engine']['options']
    check('method' not in opts and 'truth' not in opts and v['method'] not in json.dumps(opts), 'the save code does not give away the working method or the world\'s truth')
    pg.evaluate('localStorage.clear()'); pg.reload(); pg.wait_for_selector('#pl-setup:not([hidden])')
    check(pg.is_hidden('#pl-main'), 'with nothing saved, the page opens on a new game')
    pg.click('.pl-paste summary'); pg.fill('#pl-save-text', code); pg.click('#pl-load-save'); pg.wait_for_selector('.uh-screen')
    check(pg.evaluate('UHPlay.engine.victory && UHPlay.engine.victory.turn') == v['turn'], 'the save code restores the game to its victory on turn %d' % v['turn'])
    pg.click('#pl-new'); pg.fill('#pl-save-text', '{"not": "a save"}'); pg.click('#pl-load-save')
    check(not pg.is_hidden('#pl-error') and 'not a save code' in pg.inner_text('#pl-error'), 'a bad save code is refused in plain words: ' + pg.inner_text('#pl-error'))
    ctx.close()

    # ------------------------------------------------------------------ game 2: an elemental world without diffusion, and a Hail Mary
    print('game 2: Process world, good economy, diffusion off, seed 17046 (desktop): a wrong prototype first')
    ctx, pg = page(1440, 810)
    pg.goto(PAGE); pg.evaluate('localStorage.clear()'); pg.reload(); pg.wait_for_selector('#pl-setup:not([hidden])')
    setup(pg, 'Process', '1.0', False, 17046)
    check(pg.evaluate('UHPlay.engine.DIFF') is None, 'no rivals: knowledge diffusion is off')
    for _ in range(5): pg.click('#pl-next')
    pg.check('#pl-advisor')
    pg.click('#pl-10'); idle(pg)
    check(turn(pg) == 15, 'the Advisor plays 10 turns (turn %d)' % turn(pg))
    gamble = None
    for _ in range(20):          # fast-forward until a hypothesis can be committed before anything is certain
        pg.click('#pl-ff'); idle(pg)
        st = pg.evaluate("""() => { const e = UHPlay.engine; const can = e.METHODS.filter(m => !e.prototypeCheck(m));
          return { can, certain: e.S.have.has(e.OPENS) && e.status(e.S.have, e.turn).certain, method: e.method }; }""")
        if st['can'] or pg.evaluate('UHPlay.engine.over'): break
    if st['can'] and not st['certain']:
        gamble = [m for m in st['can'] if m != st['method']][0] if any(m != st['method'] for m in st['can']) else None
    check(gamble is not None, 'turn %d: a hypothesis that is not the way can be committed before certainty (%s)' % (turn(pg), gamble))
    if gamble:
        pg.click('#pl-ftltab'); pg.wait_for_selector('#pl-ftl:not([hidden]) .uh-ftl')
        check('Hail Mary' in pg.inner_text('#pl-ftl'), 'the FTL screen notes that committing now is a Hail Mary')
        btn = pg.locator('[data-commit="%s"]' % gamble); btn.scroll_into_view_if_needed(); btn.click()
        pg.wait_for_selector('#pl-modal:not([hidden])')
        txt = pg.inner_text('#pl-dialog')
        check('Nothing is certain yet' in txt and 'returns nothing' in txt, 'the commit dialog warns that a failed prototype returns nothing')
        shot(pg, 'desk_hail_mary')
        pg.click('#pl-dialog button:has-text("Commit")')
        for _ in range(3):
            pg.click('#pl-ff'); idle(pg)
            if 'ruled out while its prototype is being built' in notice(pg): print('     ff ->', turn(pg), notice(pg).split('\n')[1])
            if ('The %s prototype failed' % gamble) in notice(pg): break
        check(('The %s prototype failed' % gamble) in notice(pg), 'the wrong prototype fails: ' + notice(pg).split('\n')[1])
        check(gamble in pg.evaluate('[...UHPlay.engine.S.protoFailed]'), gamble + ' is ruled out')
        check(pg.locator('.ftl-hyp.st-ruled_out:has-text("Its prototype failed")').count() >= 1 or 'proven invalid' in pg.inner_text('#pl-ftl'), 'the FTL screen shows the failure')
        shot(pg, 'desk_prototype_failed')
    c = fast_forward_to_commit(pg, 'game 2')
    if c:
        commit(pg, c['m'], 'game 2')
        shot(pg, 'desk_process_prototype')
        v = play_to_victory(pg, 'game 2', 305)
        if v:
            if gamble: check(('%s (turn' % gamble) in pg.inner_text('#pl-dialog'), 'the victory screen lists the failed prototype')
            shot(pg, 'desk_process_victory')
            tm = timings(pg)
            diffused = pg.evaluate("[...UHPlay.engine.S.have.values()].filter(x => x.via === 'diffusion').length")
            check(diffused == 0, 'nothing arrived from abroad (%d)' % diffused)
            report.append('game 2 (Process, good, diffusion off, seed 17046, %s; a failed %s prototype first): certain %s, committed %d, victory %d (%+d against 305); a turn %.2f ms to compute, %.1f ms to draw'
                          % (v['method'], gamble, pg.evaluate('UHPlay.engine.S.cert'), c['turn'], v['turn'], v['delta'], tm['step'], tm['render']))
    ctx.close()

    # ------------------------------------------------------------------ game 3: phone, Substance world, average economy
    print('game 3: Substance world, average economy, diffusion on, random seed (phone 400x800)')
    ctx, pg = page(400, 800, b.new_context(viewport={'width': 400, 'height': 800}, is_mobile=True, has_touch=True, device_scale_factor=2))
    pg.goto(PAGE); pg.evaluate('localStorage.clear()'); pg.reload(); pg.wait_for_selector('#pl-setup:not([hidden])')
    shot(pg, 'phone_setup')
    setup(pg, 'Substance', '0.8', True)
    hscroll = lambda: pg.evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth')
    check(hscroll() <= 0, 'no horizontal scroll at 400 px on turn 0 (%d)' % hscroll())
    shot(pg, 'phone_t000')
    for i in range(6):
        if i == 2:
            r = pg.locator('.uh-focus:not(.is-funded) .uh-radio:not([disabled])').first
            r.tap()
        pg.locator('#pl-next').tap(); idle(pg)
    check(turn(pg) == 6, 'six turns by tapping (turn %d)' % turn(pg))
    shot(pg, 'phone_t006')
    shot(pg, 'phone_t006_full', full=True)
    c = fast_forward_to_commit(pg, 'game 3')
    check(hscroll() <= 0, 'no horizontal scroll at 400 px late in the game (%d)' % hscroll())
    if c:
        pg.locator('#pl-ftltab').tap(); pg.wait_for_selector('#pl-ftl:not([hidden]) .uh-ftl')
        check(pg.is_hidden('#pl-screen') or pg.evaluate("getComputedStyle(document.getElementById('pl-screen')).display") == 'none', 'on a phone the FTL screen takes the research screen\'s place')
        shot(pg, 'phone_ftl')
        commit(pg, c['m'], 'game 3', phone=True)
        pg.locator('.ftl-close').tap()
        check(pg.is_hidden('#pl-ftl'), 'Close returns to the research screen')
        shot(pg, 'phone_prototype')
        v = play_to_victory(pg, 'game 3', 380, phone=True)
        if v:
            shot(pg, 'phone_victory')
            check(hscroll() <= 0, 'no horizontal scroll at 400 px with the victory screen (%d)' % hscroll())
            tm = timings(pg)
            report.append('game 3 (Substance, average, diffusion on, seed %d, %s): certain %s, committed %d, victory %d (%+d against 380); a turn %.2f ms to compute, %.1f ms to draw'
                          % (pg.evaluate('UHPlay.engine.seed'), v['method'], pg.evaluate('UHPlay.engine.S.cert'), c['turn'], v['turn'], v['delta'], tm['step'], tm['render']))
    ctx.close()
    check(not errors, 'no console errors or warnings' + (': ' + '; '.join(errors[:4]) if errors else ''))
    b.close()

print()
for r in report: print(r)
print('\n%d failed' % len(fails) if fails else '\nall passed')
sys.exit(1 if fails else 0)
