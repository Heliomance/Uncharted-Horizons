import asyncio, os, json
from defaults import CANONICAL   # the design document, design/tech_tree.md
os.environ['PLAYWRIGHT_BROWSERS_PATH']='/opt/pw-browsers'
from playwright.async_api import async_playwright
LAY=open('/tmp/layout_v3.109.json').read()
STUB = """
(() => { const latest = {assetId:'X', version:'v3.109'}; const layout = %s;
  const docs = {'meta/latest': latest, 'layouts/v3.109': layout};
  const db = Object.freeze({ doc: p => Object.freeze({ get: async () => (docs[p] ? {exists:true, id:p, data:()=>docs[p]} : {exists:false, id:p, data:()=>undefined}),
      onSnapshot: (cb, err) => { setTimeout(() => cb(docs[p] ? {exists:true, id:p, data:()=>docs[p]} : {exists:false}), 50); return () => {}; } }) });
  window.claude = Object.freeze({ use: name => new Promise(r => setTimeout(() => r(name === 'db' ? db : null), 200)) });
})();""" % LAY
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1440,'height':900}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/_blob/X', lambda r: r.fulfill(path=CANONICAL, content_type='text/markdown'))
        await pg.add_init_script(STUB)
        t=0; await pg.goto('http://localhost:8765/index.html')
        await pg.wait_for_function("document.querySelector('#status').textContent.includes('crossings')", timeout=20000)
        print("status:", await pg.text_content('#status'))
        print("Tidy further shown (should not be):", await pg.is_visible('#tidy'))
        print("bands:", await pg.evaluate("[...document.querySelectorAll('.lane .lname')].map(x=>x.textContent).join(' / ')"))
        await pg.screenshot(path='/tmp/o3_stored_fit.png')
        await pg.select_option('#order-sel','document'); await pg.wait_for_timeout(400); await pg.keyboard.press('0'); await pg.wait_for_timeout(300)
        await pg.screenshot(path='/tmp/o4_document_fit.png'); await pg.select_option('#order-sel','solved'); await pg.wait_for_timeout(400)
        await pg.fill('#search','EL06'); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(800)
        await pg.screenshot(path='/tmp/o5_stored_el06.png')
        print("page errors:", errs or 'none'); await b.close()
asyncio.run(main())
