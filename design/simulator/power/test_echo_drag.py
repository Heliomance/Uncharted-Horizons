import asyncio, os
os.environ['PLAYWRIGHT_BROWSERS_PATH']='/opt/pw-browsers'
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1440,'height':900}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file:///home/user/Uncharted-Horizons/design/simulator/outputs/tech_tree_viewer.html'); await pg.wait_for_timeout(300)
        await pg.set_input_files('#file2','/home/user/Uncharted-Horizons/design/simulator/outputs/tech_tree_v109.md'); await pg.wait_for_timeout(700)
        await pg.fill('#search','FA03'); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(700)
        e=pg.locator('.echo-node[data-key="echo:FA03:Animal Husbandry"]'); home=pg.locator('.node[data-key="FA03"]'); link=pg.locator('path.echo.on')
        bb=await e.bounding_box(); vp=pg.viewport_size
        print("echo on screen:", 0 < bb['x'] < vp['width'] and 0 < bb['y'] < vp['height'], bb)
        hb=await home.get_attribute('transform'); d0=await link.get_attribute('d')
        await pg.mouse.move(bb['x']+40,bb['y']+20); await pg.mouse.down(); await pg.mouse.move(bb['x']+160,bb['y']+70,steps=8); await pg.mouse.up(); await pg.wait_for_timeout(200)
        print("echo moved:", await e.get_attribute('transform'), "| home unmoved:", hb == await home.get_attribute('transform'), "| link redrawn:", d0 != await link.get_attribute('d'))
        print("saved:", await pg.evaluate("localStorage.getItem('uh-techtree:positions')"))
        await pg.screenshot(path='/tmp/d3_echo_drag.png')
        print("page errors:", errs or 'none'); await b.close()
asyncio.run(main())
