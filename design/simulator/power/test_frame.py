import asyncio, os
os.environ['PLAYWRIGHT_BROWSERS_PATH']='/opt/pw-browsers'
from playwright.async_api import async_playwright
STUB = """
(() => { const doc = {assetId:'X', version:'v3.108'};
  const db = Object.freeze({ doc: p => Object.freeze({ get: async () => ({exists:true, data:()=>doc}),
      onSnapshot: (cb, err) => { setTimeout(() => cb({exists:true, id:'latest', data:()=>doc}), 50); return () => {}; } }) });
  window.claude = Object.freeze({ use: name => new Promise(r => setTimeout(() => r(name === 'db' ? db : null), 300)) });
})();"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        # 1) sandboxed frame, no stub: does the script run at all?
        pg=await b.new_page(viewport={'width':1220,'height':880}); errs=[]
        pg.on('console', lambda m: errs.append(('frame',m.type,m.text)))
        await pg.goto('http://localhost:8765/frame.html'); await pg.wait_for_timeout(1500)
        f=pg.frame_locator('#f')
        print("sandboxed frame — status:", repr(await f.locator('#status').text_content()), "| empty shown:", await f.locator('#empty').is_visible())
        # 2) top level with a viewer-like window.claude, serving the blob path
        pg2=await b.new_page(viewport={'width':1220,'height':880}); errs2=[]
        pg2.on('console', lambda m: errs2.append((m.type,m.text))); pg2.on('pageerror', lambda e: errs2.append(('pageerror',str(e))))
        await pg2.route('**/_blob/X', lambda r: r.fulfill(path='/home/user/Uncharted-Horizons/design/simulator/outputs/tech_tree_v108.md', content_type='text/markdown'))
        await pg2.add_init_script(STUB)
        await pg2.goto('http://localhost:8765/index.html'); await pg2.wait_for_timeout(2500)
        print("viewer stub — status:", repr(await pg2.text_content('#status')), "| version:", repr(await pg2.text_content('#version')), "| nodes:", await pg2.locator('.node').count())
        print("frame console:", [e for e in errs if e[1] in ('error','warning')][:5])
        print("stub console:", [e for e in errs2 if e[0] in ('error','pageerror')][:5])
        await b.close()
asyncio.run(main())
