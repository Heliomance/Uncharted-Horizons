"""Local preview of a .dc.html artboard: renders its template with its own renderVals() in Chromium and screenshots it.

A minimal stand-in for the canvas runtime, for checking layout while building: <sc-for>, <sc-if>, {{ dotted.lookup }} holes
in text and attributes, on* handlers from renderVals(), setState. It does not load the canvas's support.js, and it renders
nothing from the published artifact.

Usage: python3 preview.py <file.dc.html> <out.png> [--size WxH] [--full] [--click "<css selector>"]... [--eval "<js>"]
"""
import sys, re, json, argparse, pathlib
from playwright.sync_api import sync_playwright

ENGINE = r"""
class DCLogic { constructor(props) { this.props = props || {}; this.state = {}; }
  setState(p) { this.state = Object.assign({}, this.state, typeof p === 'function' ? p(this.state, this.props) : p); window.__render(); }
  forceUpdate() { window.__render(); } }
function lookup(path, scope) {
  path = path.trim();
  if (path === 'true') return true; if (path === 'false') return false; if (path === 'null') return null;
  if (/^-?\d+(\.\d+)?$/.test(path)) return Number(path);
  if (/^'.*'$|^".*"$/.test(path)) return path.slice(1, -1);
  let v = scope; for (const p of path.split('.')) { if (v == null) return undefined; v = v[p]; } return v;
}
const WHOLE = /^\s*\{\{\s*([^}]+?)\s*\}\}\s*$/, ANY = /\{\{\s*([^}]+?)\s*\}\}/g;
const interp = (s, scope) => s.replace(ANY, (m, p) => { const v = lookup(p, scope); return v == null ? '' : String(v); });
function expand(src, scope, out) {
  for (const n of src.childNodes) {
    if (n.nodeType === 3) { out.appendChild(document.createTextNode(interp(n.textContent, scope))); continue; }
    if (n.nodeType !== 1) continue;
    const tag = n.localName.toLowerCase();
    if (tag === 'helmet') continue;
    if (tag === 'sc-for') {
      const m = WHOLE.exec(n.getAttribute('list') || ''); const list = (m && lookup(m[1], scope)) || [];
      const as = n.getAttribute('as') || 'item';
      list.forEach((it, i) => expand(n, Object.assign({}, scope, { [as]: it, $index: i }), out)); continue;
    }
    if (tag === 'sc-if') { const m = WHOLE.exec(n.getAttribute('value') || ''); if (m && lookup(m[1], scope)) expand(n, scope, out); continue; }
    const el = document.createElementNS(n.namespaceURI, n.localName);
    for (const a of n.attributes) {
      if (a.name.startsWith('hint-')) continue;
      const m = WHOLE.exec(a.value);
      if (a.name.startsWith('on') && m) { const fn = lookup(m[1], scope); if (typeof fn === 'function') el.addEventListener(a.name.slice(2).toLowerCase(), fn); continue; }
      if (m) { const v = lookup(m[1], scope); if (v === false || v == null) continue; el.setAttribute(a.name, v === true ? '' : String(v)); continue; }
      el.setAttribute(a.name, interp(a.value, scope));
    }
    expand(n.localName === 'template' ? n.content : n, scope, el); out.appendChild(el);
  }
}
"""


def build(path):
    src = pathlib.Path(path).read_text(encoding='utf-8')
    i, j = src.index('<x-dc>') + len('<x-dc>'), src.rindex('</x-dc>')
    tpl = src[i:j]
    helmet = re.search(r'<helmet>(.*?)</helmet>', tpl, re.S)
    head = helmet.group(1) if helmet else ''
    sm = re.search(r"<script type=\"text/x-dc\"[^>]*data-props='([^']*)'[^>]*>(.*?)</script>", src, re.S)
    props = json.loads(sm.group(1).replace('&#39;', "'").replace('&amp;', '&')) if sm else {}
    defaults = {k: v.get('default') for k, v in props.items() if isinstance(v, dict) and 'default' in v and not k.startswith('$')}
    code = sm.group(2) if sm else 'class Component extends DCLogic { renderVals() { return {}; } }'
    return f"""<!doctype html><html><head><meta charset="utf-8">{head}</head><body>
<template id="tpl">{tpl}</template><div id="root"></div>
<script>{ENGINE}
{code}
const comp = new Component({json.dumps(defaults)});
window.__render = () => {{ const root = document.getElementById('root'); root.innerHTML = '';
  expand(document.getElementById('tpl').content, comp.renderVals(), root); }};
if (comp.componentDidMount) comp.componentDidMount();
window.__render();
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file'); ap.add_argument('out')
    ap.add_argument('--size', default='1440x810'); ap.add_argument('--full', action='store_true')
    ap.add_argument('--click', action='append', default=[]); ap.add_argument('--eval', action='append', default=[])
    a = ap.parse_args()
    w, h = map(int, a.size.split('x'))
    html = build(a.file)
    tmp = pathlib.Path(a.out).with_suffix('.preview.html'); tmp.write_text(html, encoding='utf-8')
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': w, 'height': h})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
        pg.goto(tmp.resolve().as_uri()); pg.wait_for_timeout(300)
        for sel in a.click: pg.click(sel); pg.wait_for_timeout(100)
        for js in a.eval: print(pg.evaluate(js))
        pg.screenshot(path=a.out, full_page=a.full)
        b.close()
    tmp.unlink()
    print('errors:', errs if errs else 'none')


if __name__ == '__main__':
    main()
