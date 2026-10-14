import asyncio, os, re
from defaults import CANONICAL   # the design document, design/tech_tree.md
os.environ['PLAYWRIGHT_BROWSERS_PATH']='/opt/pw-browsers'
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1440,'height':900}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file:///home/user/Uncharted-Horizons/design/simulator/outputs/tech_tree_viewer.html'); await pg.wait_for_timeout(300)
        t=await pg.evaluate("performance.now()")
        await pg.set_input_files('#file2',CANONICAL)
        await pg.wait_for_function("document.querySelector('#status').textContent.includes('crossings')", timeout=20000)
        print("loaded in", round(await pg.evaluate("performance.now()")-t), "ms")
        print("status:", await pg.text_content('#status'))
        print("first bands:", await pg.evaluate("[...document.querySelectorAll('.lane .lname')].slice(0,6).map(x=>x.textContent).join(' / ')"))
        print("Tidy further shown:", await pg.is_visible('#tidy'))
        await pg.screenshot(path='/tmp/o1_solved.png')
        await pg.select_option('#order-sel','document'); await pg.wait_for_timeout(500)
        print("document order:", re.search(r'[\d,]+ crossings[^,]*', await pg.text_content('#status')).group(0), "| first bands:", await pg.evaluate("[...document.querySelectorAll('.lane .lname')].slice(0,3).map(x=>x.textContent).join(' / ')"), "| tidy shown:", await pg.is_visible('#tidy'))
        await pg.select_option('#order-sel','solved'); await pg.wait_for_timeout(500)
        # tidy for a few seconds, then stop and apply
        await pg.click('#tidy'); await pg.wait_for_timeout(6000)
        print("while tidying:", (await pg.text_content('#status'))[:90], "| button:", await pg.text_content('#tidy'))
        print("page still responds:", await pg.evaluate("1+1")==2)
        await pg.click('#tidy'); await pg.wait_for_timeout(800)
        print("after stop:", re.search(r'[\d,]+ crossings[^,]*', await pg.text_content('#status')).group(0), "| tidy shown:", await pg.is_visible('#tidy'))
        # selection, dragging and echoes still work under the new layout
        await pg.fill('#search','FA03'); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(700)
        print("select FA03:", await pg.text_content('#p-name'), "| echo selected:", await pg.locator('.echo-node.selected').count(), "| lit:", await pg.locator('.edge.in').count(), "/", await pg.locator('.edge.out').count())
        await pg.screenshot(path='/tmp/o2_fa03.png')
        print("page errors:", errs or 'none'); await b.close()
asyncio.run(main())
