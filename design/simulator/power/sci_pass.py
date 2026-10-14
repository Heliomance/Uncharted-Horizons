import re, json
t=open('tt.md',encoding='utf-8').read()
t=t.replace('(v3.79)','(v3.80)',1)
inv=json.load(open('power/sci_inventory.json'))
LANDMARK={'Printing House':1,'Experimental Laboratory':2,'Nuclear Physics Lab':2,'Deep Matter Lab':2,'Computer Centre':2}
SCI_TOK=re.compile(r'^\s*\+\d+ Science\s*$')
def edit_spec(spec,keep=None):
    """strip Science from a building spec; return (new_spec, science_only)"""
    parts=[p for p in re.split(r';(?![^⟨]*⟩)',spec)]
    out=[]; had_other=False
    for i,p in enumerate(parts):
        if i==0 and re.match(r'\s*(\d+/\d+|national wonder|world wonder)',p): out.append(p); continue
        if re.search(r'⟨[^⟩]*(?:\[Science\]|Science\] per)[^⟩]*⟩',p) and re.fullmatch(r'\s*⟨[^⟩]+⟩\s*',p): continue   # science % or per-pop unique
        desc=''
        m=re.match(r'(.*?)(\s+—\s+.*)$',p,re.S)
        body,desc=(m.group(1),m.group(2)) if m else (p,'')
        toks=[x for x in body.split(',')]
        if all(re.fullmatch(r'\s*[+-]\d+ \w+\s*',x) for x in toks if x.strip()):
            kept=[x.strip() for x in toks if x.strip() and not SCI_TOK.match(x)]
            if keep: kept=[f'+{keep} Science']+kept
            if kept: out.append(' '+', '.join(kept)+desc); had_other=had_other or any('Science' not in k for k in kept)
            elif desc: out.append(desc.lstrip()[2:].strip() and ' '+desc.strip('— ').strip())
            continue
        out.append(p); had_other=had_other or bool(p.strip()) and not re.match(r'\s*—',p)
    new=';'.join(x for x in out if x is not None and x.strip())
    return new, not had_other and not keep
changed=[]; removed=[]
for x in inv:
    if x['tier']=='UNIQUE' or x['wonder']: continue
    L=t.split('\n'); idx=[i for i,l in enumerate(L) if l.startswith(f"| {x['rid']} |")]; assert len(idx)==1
    line=L[idx[0]]
    m=re.search(r'\*\*'+re.escape(x['b'])+r'\*\*ⁿ\s*\[((?:[^\[\]]|\[[^\]]*\])*)\]',line); assert m,x['b']
    new,sci_only=edit_spec(m.group(1),LANDMARK.get(x['b']))
    if sci_only:
        pat=re.compile(r'(?:;\s*|,\s*)?\*\*'+re.escape(x['b'])+r'\*\*ⁿ\s*\['+re.escape(m.group(1))+r'\](?:\s+—\s+[^.;|]*[.;]?)?')
        line2=pat.sub('',line,count=1); removed.append((x['rid'],x['b']))
    else:
        line2=line.replace(m.group(0),f"**{x['b']}**ⁿ [{new}]",1); changed.append((x['rid'],x['b']))
    line2=re.sub(r'\|\s*[.;,]\s*',lambda mm:'| ',line2); line2=re.sub(r'  +',' ',line2)
    L[idx[0]]=line2; t='\n'.join(L)
open('tt.md','w',encoding='utf-8').write(t)
json.dump(dict(changed=changed,removed=removed),open('power/sci_changes.json','w'))
print(f"Science stripped from {len(changed)} buildings (kept for their other content), {len(removed)} science-only buildings removed")
