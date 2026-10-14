import asyncio, os
os.environ['PLAYWRIGHT_BROWSERS_PATH']='/opt/pw-browsers'
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1440,'height':900}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file:///home/user/Uncharted-Horizons/design/simulator/outputs/tech_tree_viewer.html'); await pg.wait_for_timeout(300)
        await pg.set_input_files('#file2','/home/user/Uncharted-Horizons/design/simulator/outputs/tech_tree_v109.md'); await pg.wait_for_timeout(700)
        print("status:", await pg.text_content('#status'))
        print("echo nodes:", await pg.locator('.echo-node').count(), "| echo links:", await pg.locator('path.echo').count(), "| home badges:", await pg.locator('.nalso').count(), "| flagged homes:", await pg.locator('.node.dual-issue').count())
        await pg.fill('#search','FA03'); await pg.wait_for_timeout(150); print("search row:", (await pg.text_content('#results li')).strip())
        await pg.keyboard.press('Enter'); await pg.wait_for_timeout(700)
        print("panel also:", await pg.text_content('#p-also'), "| issues shown:", await pg.is_visible('#p-issues-wrap'))
        print("echo of FA03 selected:", await pg.locator('.echo-node.selected').count(), "| its link lit:", await pg.locator('path.echo.on').count())
        await pg.screenshot(path='/tmp/d1_fa03.png')
        # select through an echo: click the Animal Husbandry echo of FA03
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(100)
        ec=pg.locator('.echo-node[data-key="echo:FA03:Animal Husbandry"]'); await ec.scroll_into_view_if_needed()
        await pg.evaluate("document.querySelector('.echo-node[data-key=\"echo:FA03:Animal Husbandry\"]').dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,pointerId:7,clientX:0,clientY:0}))")
        await pg.evaluate("document.querySelector('#graph').dispatchEvent(new PointerEvent('pointerup',{bubbles:true,pointerId:7,clientX:0,clientY:0}))")
        await pg.wait_for_timeout(600); print("clicking the echo selects:", await pg.text_content('#p-id'), await pg.text_content('#p-name'))
        # a flagged row
        await pg.fill('#search','GN08'); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(700)
        print("GN08 also:", await pg.text_content('#p-also')); print("GN08 issues:", (await pg.text_content('#p-issues')).strip())
        await pg.screenshot(path='/tmp/d2_gn08.png')
        await pg.fill('#search','EL04'); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(600)
        print("EL04 also shown:", await pg.is_visible('#p-also'), "| issues:", (await pg.text_content('#p-issues')).strip())
        # drag an echo; its home stays where it was
        await pg.fill('#search','CH12'); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(700)
        e=pg.locator('.echo-node[data-key="echo:CH12:Farming"]'); home=pg.locator('.node[data-key="CH12"]')
        hb=await home.get_attribute('transform'); await e.scroll_into_view_if_needed(); bb=await e.bounding_box()
        await pg.mouse.move(bb['x']+40,bb['y']+20); await pg.mouse.down(); await pg.mouse.move(bb['x']+140,bb['y']+80,steps=6); await pg.mouse.up(); await pg.wait_for_timeout(200)
        print("echo dragged; home unmoved:", hb == await home.get_attribute('transform'), "| saved:", await pg.evaluate("localStorage.getItem('uh-techtree:positions')"))
        await pg.keyboard.press('Escape'); await pg.select_option('#world-sel','Substance'); await pg.wait_for_timeout(200)
        print("Substance world, absent echoes:", await pg.locator('.echo-node.absent').count(), "| hidden echo links:", await pg.locator('path.echo.hidden').count())
        print("page errors:", errs or 'none'); await b.close()
asyncio.run(main())
