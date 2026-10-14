import asyncio, os
os.environ['PLAYWRIGHT_BROWSERS_PATH']='/opt/pw-browsers'
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1440,'height':900}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file:///home/user/Uncharted-Horizons/design/simulator/outputs/tech_tree_viewer.html'); await pg.wait_for_timeout(300)
        await pg.set_input_files('#file2','/home/user/Uncharted-Horizons/design/simulator/outputs/tech_tree_v111.md')
        await pg.wait_for_function("document.querySelector('#status').textContent.includes('links')", timeout=20000)
        print("status:", await pg.text_content('#status'))
        print("order selector:", await pg.eval_on_selector('#order-sel','e=>e.value'), "| tidy button present:", await pg.locator('#tidy').count())
        lanes="[...document.querySelectorAll('.lane .lname')].map(x=>x.textContent)"
        o=await pg.evaluate(lanes); print("bands (opening):", ' / '.join(o[:8]), '…', ' / '.join(o[-3:]))
        await pg.keyboard.press('0'); await pg.wait_for_timeout(300); await pg.screenshot(path='/tmp/op1_fit.png')
        await pg.select_option('#order-sel','document'); await pg.wait_for_timeout(400)
        print("bands (document):", ' / '.join((await pg.evaluate(lanes))[:4]))
        await pg.select_option('#order-sel','opening'); await pg.wait_for_timeout(400)
        await pg.fill('#search','FA03'); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(700)
        print("select FA03:", await pg.text_content('#p-name'), "| echo selected:", await pg.locator('.echo-node.selected').count(), "| lit in/out:", await pg.locator('.edge.in').count(), "/", await pg.locator('.edge.out').count())
        await pg.fill('#search','RC04'); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(700); await pg.screenshot(path='/tmp/op2_rc04.png')
        await pg.reload(); await pg.wait_for_timeout(500)
        print("after reload, selector remembers:", await pg.eval_on_selector('#order-sel','e=>e.value'))
        print("page errors:", errs or 'none'); await b.close()
asyncio.run(main())
