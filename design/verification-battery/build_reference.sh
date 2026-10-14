#!/bin/bash
# Rebuild the battery's three derived reference files from Unciv's own documentation and rulesets
# (recipes as first used on 2026-09-22/24). Run again whenever unciv/ is refreshed from a newer Unciv.
set -e
cd "$(dirname "$0")/unciv"
grep -E '^\?\?\? example' uniques.md | sed 's/^??? example  //; s/"//g' > unique_templates.txt
# conditionals: newer uniques.md files escape them as &lt;…&gt;, so match both forms; quotes stripped (the battery unescapes and compares bare)
grep -oE '^\?\?\? example  "(<|&lt;)[^"]+"' uniques.md | sed 's/^??? example  //; s/"//g' | sort -u > conditionals.txt
python3 - <<'EOF'
import re,json,json5
P=open('Unique-parameters.md',encoding='utf-8').read()
def section(name):
    m=re.search(r'^## '+re.escape(name)+r'\s*$(.*?)(?=^## )',P,re.M|re.S); return m.group(1) if m else ''
kw={}
for name in ['tileFilter','terrainFilter','cityFilter','baseUnitFilter','mapUnitFilter','buildingFilter','improvementFilter','populationFilter','civFilter','combatantFilter','resourceFilter','specialist']:
    s=section(name)
    toks=set(re.findall(r'`([^`\[\]{}]+)`',s))|set(re.findall(r'^\s*-\s+([A-Z][A-Za-z\- ]+?)(?:\s*[-–(:]|\s*$)',s,re.M))
    kw[name]={x.strip() for x in toks if len(x.strip())<40}
names={}
for f,key in [('Terrains','terrain'),('TileResources','resource'),('TileImprovements','improvement'),('Buildings','building'),('Units','unit'),('UnitTypes','unittype'),('UnitPromotions','promotion'),('Specialists','specialist')]:
    names[key]={x['name'] for x in json5.load(open(f+'.json',encoding='utf-8'))}
json.dump({'kw':{k:sorted(v) for k,v in kw.items()},'names':{k:sorted(v) for k,v in names.items()}},open('vocab.json','w'))
print(f"vocab.json: {sum(len(v) for v in kw.values())} filter keywords, {sum(len(v) for v in names.values())} names")
EOF
echo "unique_templates.txt: $(wc -l < unique_templates.txt) templates; conditionals.txt: $(wc -l < conditionals.txt) conditionals"
