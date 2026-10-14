import asyncio, os, json
from defaults import CANONICAL   # the design document, design/tech_tree.md
os.environ['PLAYWRIGHT_BROWSERS_PATH']='/opt/pw-browsers'
from playwright.async_api import async_playwright
URL='file:///home/user/Uncharted-Horizons/design/simulator/outputs/tech_tree_viewer.html'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        pg=await b.new_page(viewport={'width':1440,'height':900})
        errs=[]; pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None); pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(600)
        print("empty state visible:", await pg.is_visible('#empty'), "| status:", await pg.text_content('#status'))
        await pg.screenshot(path='/tmp/v0_empty.png')
        await pg.set_input_files('#file2',CANONICAL); await pg.wait_for_timeout(800)
        print("after load — status:", await pg.text_content('#status'), "| version:", await pg.text_content('#version'))
        print("nodes:", await pg.locator('.node').count(), "| edges:", await pg.locator('.edge').count(), "| ribbon eras:", await pg.locator('.era').count(), "| lanes:", await pg.locator('.lane').count())
        await pg.screenshot(path='/tmp/v1_fit.png')
        # search and select
        await pg.fill('#search','Distil'); await pg.wait_for_timeout(200)
        print("search hits:", await pg.locator('#results li').count(), "| first:", (await pg.text_content('#results li'))[:60])
        await pg.keyboard.press('Enter'); await pg.wait_for_timeout(700)
        print("panel:", await pg.is_visible('#panel'), "| name:", await pg.text_content('#p-name'), "| needs:", (await pg.text_content('#p-pre'))[:80])
        print("in/out edges lit:", await pg.locator('.edge.in').count(), "/", await pg.locator('.edge.out').count())
        await pg.screenshot(path='/tmp/v2_selected.png')
        await pg.check('#lineage'); await pg.wait_for_timeout(300)
        print("lineage edges lit:", await pg.locator('.edge.in').count(), "/", await pg.locator('.edge.out').count())
        await pg.screenshot(path='/tmp/v3_lineage.png')
        # drag the selected node
        g=pg.locator('.node[data-id="CH04"]'); bb=await g.bounding_box()
        before=await g.get_attribute('transform')
        await pg.mouse.move(bb['x']+bb['width']/2, bb['y']+bb['height']/2); await pg.mouse.down()
        await pg.mouse.move(bb['x']+bb['width']/2+120, bb['y']+bb['height']/2+90, steps=8); await pg.mouse.up(); await pg.wait_for_timeout(200)
        print("drag:", before, "→", await g.get_attribute('transform'), "| reset enabled:", not await pg.is_disabled('#reset'))
        print("saved positions:", await pg.evaluate("localStorage.getItem('uh-techtree:positions')"))
        await pg.screenshot(path='/tmp/v4_dragged.png')
        # zoom with ctrl+wheel and pan with wheel
        z0=await pg.text_content('#zoom-level')
        await pg.mouse.move(700,450); await pg.keyboard.down('Control'); await pg.mouse.wheel(0,-400); await pg.keyboard.up('Control'); await pg.wait_for_timeout(150)
        z1=await pg.text_content('#zoom-level'); await pg.mouse.wheel(0,300); await pg.wait_for_timeout(150)
        print("zoom:", z0, "→", z1)
        # world filter
        await pg.select_option('#world-sel','Substance'); await pg.wait_for_timeout(300)
        print("Substance world: absent nodes", await pg.locator('.node.absent').count(), "| hidden edges", await pg.locator('.edge.hidden').count())
        await pg.keyboard.press('Escape'); await pg.keyboard.press('0'); await pg.wait_for_timeout(300)
        await pg.screenshot(path='/tmp/v5_substance.png')
        await pg.click('#legend-toggle'); await pg.wait_for_timeout(150); await pg.screenshot(path='/tmp/v6_legend.png')
        # reload keeps the moved node
        await pg.reload(); await pg.wait_for_timeout(300); await pg.set_input_files('#file2',CANONICAL); await pg.wait_for_timeout(600)
        print("after reload, CH04 at:", await pg.locator('.node[data-id="CH04"]').get_attribute('transform'))
        # dark mode and a phone
        d=await b.new_page(viewport={'width':390,'height':800}, color_scheme='dark'); await d.goto(URL); await d.wait_for_timeout(300)
        await d.set_input_files('#file2',CANONICAL); await d.wait_for_timeout(600)
        await d.fill('#search','QM-E04'); await d.keyboard.press('Enter'); await d.wait_for_timeout(700); await d.screenshot(path='/tmp/v7_phone_dark.png')
        print("console errors:", errs or 'none')
        await b.close()
asyncio.run(main())
