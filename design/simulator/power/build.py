shell=open('/home/user/Uncharted-Horizons/design/simulator/viewer/shell.html').read()
parts={'/*PARSE*/':open('/home/user/Uncharted-Horizons/design/simulator/viewer/parse.js').read(),'/*SOLVER*/':open('/home/user/Uncharted-Horizons/design/simulator/viewer/solver.js').read(),'/*APP*/':open('/home/user/Uncharted-Horizons/design/simulator/viewer/app.js').read()}
for k in parts: assert shell.count(k)==1, k
html=shell
for k,v in parts.items(): html=html.replace(k,v)
assert not any(k in html for k in parts)
open('/home/user/Uncharted-Horizons/design/simulator/outputs/tech_tree_viewer.html','w').write(html); print("built", len(html), "bytes")
