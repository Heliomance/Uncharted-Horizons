"""Uncharted Horizons verification battery — mirrors the checks used through v3.72.
Usage: python3 battery.py [file]   (default tt.md)
Note: filtercheck.py builds `report` but never prints it; this script prints it."""
import re,sys,html
import os as _os
if len(sys.argv) > 1: sys.argv[1] = _os.path.abspath(sys.argv[1])   # resolve the tree's path before moving into the battery's own folder
_os.chdir(_os.path.dirname(_os.path.abspath(__file__)))               # unciv/, filtercheck.py and prereq.py live beside this script
from collections import Counter
F=sys.argv[1] if len(sys.argv)>1 else 'tt.md'
t=open(F,encoding='utf-8').read()
def innermost(s,tok='[]'):                      # collapse nested brackets innermost-first
    while True:
        n=re.sub(r'\[[^\[\]]*\]','§',s)
        if n==s: break
        s=n
    return s.replace('§',tok)
tpl=[l.strip() for l in open('unciv/unique_templates.txt',encoding='utf-8') if l.strip()]
conds=[html.unescape(l.strip()) for l in open('unciv/conditionals.txt',encoding='utf-8') if l.strip()]
skel=lambda s: re.sub(r'\s+',' ',innermost(re.sub(r'<[^<>]*>','',s))).strip().rstrip('.')
cskel=lambda s: re.sub(r'\s+',' ',innermost(s)).strip()
TAGS={'Power Plant','Regimen Hall','Caloric Reservoir','Ironworks','Launch Complex','Propulsion'}   # tag uniques naming shared slots (§7.0)
ts={skel(x) for x in tpl}|TAGS; cs={cskel(c) for c in conds}; badu=[]; badc=[]
for u in re.findall(r'⟨([^⟩]+)⟩',t):
    if u=='…' or 'conversion of city production to [' in u: continue
    core=re.sub(r'\s*\([^)]*\)\s*$','',u).split(' — ')[0]
    badc+=[c for c in re.findall(r'<[^<>]+>',core) if cskel(c) not in cs]
    if skel(core) not in ts: badu.append(core)
g={}; exec(open('filtercheck.py').read().replace("open('tt.md'",f"open('{F}'").replace("ours['building'].add('Power Plant')","ours['building']|={'Power Plant','Regimen Hall','Caloric Reservoir','Ironworks','Launch Complex'}; ours['unit'].add('SS FTL Drive'); ours['building'].discard('SS FTL Drive')"),g); report=g['report']
rows={}
for l in t.split('\n'):
    if l.startswith('|'):
        c=[x.strip() for x in l.strip().strip('|').split('|')]
        if len(c)>=6 and re.match(r'^([A-Z]{1,3}-?[A-Z]?\d{1,2}[A-Z]?(-W|-V\d+)?|ME-B)$',c[0]) and c[1].startswith('**'): rows[c[0]]=c
IDRX=r'\b([A-Z]{1,3}-?[A-Z]?\d{1,2}[A-Z]?(?:-W|-V\d+)?|ME-B)\b'
TOK={'HIGH_ENERGY_PHYSICS','EXOTIC_MATTER','MATTER_THEORY','DISEASE_THEORY','LIFE_THEORY','THERMO_THEORY','MASS_MEDICINE'}
dang=[(k,x) for k,c in rows.items() for x in re.findall(IDRX,c[4]) if x not in rows and x not in TOK and not x.startswith(('FQ','WA'))]
dups=[k for k in rows if sum(1 for l in t.split('\n') if l.startswith(f'| {k} |'))>1]
def terms(pre):
    d=0; out=[]; cur=''
    for ch in pre:
        if ch=='(': d+=1
        if ch==')': d-=1
        if ch=='+' and d==0: out.append(cur); cur=''
        else: cur+=ch
    return out+[cur]
required=lambda pre:{x for tm in terms(pre) if not re.search(r'\bor\b',tm) for x in re.findall(IDRX,tm) if x in rows}
closure=[(k,p) for k,c in rows.items() if c[2]=='CORE' for p in required(c[4]) if rows[p][2]!='CORE']
orgaps=[(k,tm.strip()[:45]) for k,c in rows.items() if c[2]=='CORE' for tm in terms(c[4])
        if re.search(r'\bor\b',tm) and (ids:=[x for x in re.findall(IDRX,tm) if x in rows]) and not any(rows[x][2]=='CORE' for x in ids)]
SUB={'CH20','CH21','CH27','QM-E09','QM-E10','QM-E26'}; PRO={'CH22','CH23','CH24','CH26','TR16','QM-E11','QM-E24','QM-E25'}
ATOM={k for k in rows if k.startswith(('NP','QP'))}|{'EN02','EN08','EN09','CP10','GN10','MI10','ES06','ES08','ES12','ES14','CH06'}
QM={k for k in rows if k.startswith('QM-E')}
exists={'Corpuscular':lambda k:k not in SUB|PRO|QM,'Substance':lambda k:k not in ATOM|PRO,'Process':lambda k:k not in ATOM|SUB}
gap=[]
for tok in ['MATTER_THEORY','HIGH_ENERGY_PHYSICS','THERMO_THEORY','DISEASE_THEORY','LIFE_THEORY']:
    src=[k for k,c in rows.items() if re.search(r'[Gg]rants?\s+(the\s+)?\*{0,2}'+tok,c[5]) or (tok=='LIFE_THEORY' and k=='CH07')]
    gap+=[(tok,w) for w,f in exists.items() if not [x for x in src if f(x)]]
P=lambda ok:'PASS' if ok else 'FAIL'
print(f"  {P(not badu and not badc)}  templates/conditionals — bad uniques {len(badu)}, bad conditionals {len(badc)} {(badu+badc)[:3] or ''}")
print(f"  {P(not report)}  filter values — {len(report)} {report[:3] or ''}")
print(f"  {P(not dang)}  prerequisite references — rows {len(rows)}, dangling {len(dang)} {dang[:3] or ''}")
print(f"  {P(not dups)}  duplicate IDs — {len(dups)} {dups or ''}")
print(f"  {P(not closure)}  CORE closure (mandatory prerequisites) — {len(closure)} {closure[:3] or ''}")
print(f"  {P(not gap)}  per-world token sources — gaps {len(gap)} {gap or ''}")
print(f"  info  CORE rows whose OR-group has no CORE option (not checked before v3.73): {len(orgaps)}")

# ---- v3.76 checks: exclusion by replacement ----
body=t[:t.index('## Changelog')]
blocking=[(re.match(r'^\| ([^|]+) \|',l) or [None,'§'])[1].strip() for l in body.split('\n') for _ in re.findall(r'⟨Only available <in cities without a \[[^\]]+\]>⟩',l)]
placeholder=[k for k,c in rows.items() if re.search(r'`replaces: (Power Plant|Regimen Hall|Caloric Reservoir|Ironworks)`',c[5])]
selfrm=[]
for l in body.split('\n'):
    for m in re.finditer(r'⟨Remove \[(.+?)\] \[in (?:this city|all cities)\]⟩',l):
        owners=[x.group(1) for x in re.finditer(r'\*\*([^*]+)\*\*ⁿ?\s*[\[(]',l[:m.start()])]
        owner=owners[-1] if owners else '?'; f=m.group(1)
        canon=re.search(r'canonical ([A-Z][\w\- ]*?) (?:gains |carries )?$',l[max(0,m.start()-90):m.start()])
        if canon: owner=canon.group(1)          # a clause the ruleset derivation gives a canonical building
        seg=l[l.rfind('**'+owner+'**',0,m.start()):m.start()]
        tags={x for x in TAGS if f'⟨{x}⟩' in seg}
        mm=re.fullmatch(r'\{(.+)\} \{non-\[(.+)\]\}',f)
        if mm: bad = mm.group(2)!=owner and 'its own name' not in mm.group(2) and owner!='?'
        else:  bad = f==owner or f in tags
        if bad: selfrm.append((owner,f))
names={c[1].strip('*'):k for k,c in rows.items()}
collide=[]
for f in set(re.findall(r'(?:⟨Remove \[|<in cities with(?:out)? a \[)([^<>⟩]+?)\](?: \[in| ?>)',body)):
    for atom in re.findall(r'[A-Z][A-Za-z\- ]+',f.replace('non-','')):
        atom=atom.strip()
        if atom in names: collide.append((atom,names[atom],re.findall(r'\*\*([^*]+)\*\*ⁿ',rows[names[atom]][5])))
print(f"  {P(not blocking)}  exclusion by replacement — blocking clauses left {len(blocking)} {blocking or ''}")
print(f"  {P(not placeholder)}  no placeholder `replaces` — {len(placeholder)} {placeholder or ''}")
print(f"  {P(not selfrm)}  no Remove clause removes its own building — {len(selfrm)} {selfrm or ''}")
print(f"  info  building-filter atoms sharing a breakthrough's name (harmless if it unlocks only that building): {sorted(set((a,k,tuple(o)) for a,k,o in collide))}")

# ---- v3.78 checks: table integrity and era order ----
cellbad=[k for l in t.split('\n') if (mm:=re.match(r'^\| ([A-Z]{1,3}(?:-[A-Z])?\d+[A-Z]?(?:-W|-V\d+)?|ME-B) \| \*\*',l)) and len(l.strip().strip('|').split('|'))!=7 for k in [mm.group(1)]]
EO=['Primitive','Ancient','Classical','Medieval','Early Modern','Modern','Atomic','Space','Interstellar']
eraord=[]
for k,c in rows.items():
    for tm in terms(c[4]):
        if re.search(r'\bor\b',tm): continue
        for p in re.findall(IDRX,tm):
            if p in rows and c[3] in EO and rows[p][3] in EO and EO.index(rows[p][3])>EO.index(c[3]): eraord.append((k,c[3],p,rows[p][3]))
print(f"  {P(not cellbad)}  every row has seven cells — {len(cellbad)} {cellbad or ''}")
print(f"  {P(not eraord)}  no hard prerequisite sits in a later era than its dependent — {len(eraord)} {eraord[:3] or ''}")

hdrbad=[]; LL=t.split('\n')
for i,l in enumerate(LL[:-1]):
    if l.startswith('| # |') and not re.match(r'^\|[-: |]+\|\s*$',LL[i+1]): hdrbad.append(i+1)
print(f"  {P(not hdrbad)}  every focus table's header is followed by its separator — {len(hdrbad)} {hdrbad[:3] or ''}")
print(f"  tiers {dict(Counter(c[2] for c in rows.values()))}")

# ---- v3.87 check: required buildings ----
import json5
_canon = {b['name']: b.get('requiredBuilding') for b in json5.load(open('unciv/Buildings.json', encoding='utf-8'))}
_sec7 = {}
for _m in re.finditer(r'^\| ([A-Z][^|]+?) \| [^|]+ \| \*\*([A-Z][A-Z0-9-]*)\*\* \|', t, re.M): _sec7.setdefault(_m.group(1).strip(), []).append(_m.group(2))
def _world(c, seen=()):
    """the world a row belongs to: stated in its text, or inherited from a hard prerequisite that belongs to one"""
    if c[0].startswith('QM-E'): return 'Elemental'
    m = re.search(r'Only in ([A-Z][a-z]+) worlds|([A-Z][a-z]+) worlds only', c[5])
    if m: return m.group(1) or m.group(2)
    for tm in terms(c[4]):
        if re.search(r'\bor\b', tm): continue
        for p in re.findall(IDRX, tm):
            if p in rows and p not in seen and (w := _world(rows[p], seen + (c[0],))): return w
    return None
_new = {}
for k, c in rows.items():
    for m in re.finditer(r'\*\*([^*]+)\*\*ⁿ\s*\[', c[5]): _new.setdefault(m.group(1), []).append(k)
def _granted(b):
    """rows that grant building b — requirement tokens name a predecessor, they do not grant it"""
    strip = lambda s: re.sub(r'requires an? \*\*[^*]+\*\* in this city', '', s)
    return sorted(set([k for k, c in rows.items() if re.search(rf'\*\*{re.escape(b)}\*\*(?!ⁿ)', strip(c[5]))] + _new.get(b, []) + [k for k in _sec7.get(b, []) if k in rows]))
reqbad = []; reqn = 0
for k, c in rows.items():
    for m in re.finditer(r'\*\*([^*]+)\*\*ⁿ\s*\[', c[5]):
        name = m.group(1); d = 0; j = m.end() - 1
        for e in range(j, len(c[5])):
            d += c[5][e] == '['; d -= c[5][e] == ']'
            if d == 0: break
        spec = c[5][j + 1:e]
        req = re.findall(r'requires an? \*\*([^*]+)\*\* in this city', spec); reqn += len(req)
        for r in req:
            src = _granted(r)
            if r in TAGS or not src: reqbad.append((name, r, 'not a building granted anywhere')); continue
            if c[3] in EO and min(EO.index(rows[s][3]) for s in src if rows[s][3] in EO) > EO.index(c[3]): reqbad.append((name, r, 'arrives later'))
            ws = {_world(rows[s]) for s in src}
            if None not in ws and _world(c) not in ws: reqbad.append((name, r, f'only in {ws}'))
        base = re.search(r'replaces ([A-Z][A-Za-z\' ]+?)\s*[;\]]', spec)
        if base and _canon.get(base.group(1)) and _canon[base.group(1)] not in req: reqbad.append((name, _canon[base.group(1)], f'replaces {base.group(1)} without its requirement'))
        if '⟨Power Plant⟩' in spec and 'Factory' not in req: reqbad.append((name, 'Factory', 'Power Plant slot without a Factory'))
print(f"  {P(not reqbad)}  required buildings exist, arrive in time, share their worlds, and are inherited — {reqn} requirements, {len(reqbad)} problems {reqbad[:3] or ''}")

# ---- v3.88 check: every required building is a safe predecessor ----
import functools, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); import prereq as PQ
@functools.lru_cache(None)
def _sure(k):
    """rows certain to be discovered before row k: every OR branch of its prerequisites leads through them (shared parser)"""
    out = set()
    for grp in PQ.parse(rows[k][4], set(rows)):
        per = [set().union(*[{p} | _sure(p) for p in o if p != k]) for o in grp]
        if per: out |= set.intersection(*per)
    return frozenset(out)
_ENV = re.compile(r'biome|terrain|[Ll]ocation|access|region|start\b|Coastal|River|Desert|Mountain|Forest|Marsh|Volcanic|Tundra|Tropical|Grassland|steppe|Lake|wetland|Island|Jungle')
@functools.lru_cache(None)
def _env(k):
    """terrain conditions row k needs, directly or through hard prerequisites (resources are excluded: trade satisfies them, §1.2)"""
    out = set()
    for tm in terms(rows[k][4]):
        if re.search(r'\bor\b', tm): continue
        rest = re.sub(IDRX, '', re.sub(r'\([^)]*\)', '', tm))
        if _ENV.search(rest) and not re.search(r'deposits|resource', rest): out.add(re.sub(r'\s+', ' ', rest.strip()))
        for p in re.findall(IDRX, tm):
            if p in rows and p != k: out |= _env(p)
    return frozenset(out)
_REQTOK = r'requires an? \*\*[^*]+\*\* in this city'
def _grants(b):
    g = [k for k, c in rows.items() if re.search(rf'\*\*{re.escape(b)}\*\*(?!ⁿ)', re.sub(_REQTOK, '', c[5]))] + _new.get(b, []) + [k for k in _sec7.get(b, []) if k in rows]
    return sorted(set(g))
_over = {}
_ov = re.search(r'\*\*Requirement overrides\.\*\*.*?\n\n\| Building \| Vanilla requires \| Fork requires \|\n\|[-|]+\|\n((?:\|[^\n]*\|\n)+)', t, re.S)
if _ov:
    for l in _ov.group(1).strip().split('\n'):
        a, _v, f = [x.strip() for x in l.strip('|').split('|')]; _over[a] = None if f == '—' else f
_fork_req = {n: r for k, c in rows.items() for n, r in re.findall(r'\*\*([^*]+)\*\*ⁿ\s*\[[^\]]*?' + _REQTOK.replace('\\*\\*[^*]+\\*\\*', '\\*\\*([^*]+)\\*\\*'), c[5])}
pairs = [(n, r, 'fork') for n, r in _fork_req.items()] + [(n, _over.get(n, r), 'canonical') for n, r in _canon.items() if _over.get(n, r)]
def _safe(dep_row, pred):
    src = _grants(pred)
    if not src: return 'predecessor granted nowhere'
    if any(p == dep_row or p in _sure(dep_row) for p in src): return None
    for p in src:
        if rows[p][2] == 'CORE' and rows[p][3] in EO and rows[dep_row][3] in EO and EO.index(rows[p][3]) <= EO.index(rows[dep_row][3]) and _env(p) <= _env(dep_row): return None
    return f"{pred} comes from {[(p, rows[p][2][:4], rows[p][3][:5]) for p in src]}"
unsafe = []; checked = 0
for dep, pred, kind in pairs:
    for dk in _grants(dep):
        checked += 1
        why = _safe(dk, pred)
        if why: unsafe.append((kind, dep, dk, why))
print(f"  {P(not unsafe)}  every required building is a safe predecessor — {checked} links checked, {len(unsafe)} unsafe {unsafe[:3] or ''}")

# ---- v3.89 check: no row's only grant is a world wonder ----
_W = {b['name'] for b in json5.load(open('unciv/Buildings.json', encoding='utf-8')) if b.get('isWonder')}
def _specs(s):
    """every **Name**ⁿ [spec] in s, bracket-balanced: (name, spec, start, end)"""
    out = []
    for m in re.finditer(r'\*\*([^*]+)\*\*ⁿ\s*\[', s):
        d = 0
        for e in range(m.end() - 1, len(s)):
            d += s[e] == '['; d -= s[e] == ']'
            if d == 0: out.append((m.group(1), s[m.end():e], m.start(), e)); break
    return out
wonly = []
for k, c in rows.items():
    rest, wonders = c[5], []
    for name, spec, a, e in sorted(_specs(rest), key=lambda x: -x[2]):
        if re.search(r'world wonder|\bwonder\b', spec[:40]) and 'national' not in spec[:40]: wonders.append(name); rest = rest[:a] + rest[e + 1:]
    for w in _W:
        if f'**{w}**' in rest: wonders.append(w); rest = rest.replace(f'**{w}**', '')
    rest = re.sub(r'\((?:world )?wonders?\)|\(and [^)]*\)', '', rest)
    if wonders and not re.findall(r'\*\*([^*]+)\*\*', rest) and not re.search(r'⟨|\*Unlocks\*|\*Reveals\*', rest): wonly.append(k)
print(f"  {P(not wonly)}  no row's only grant is a world wonder — {len(wonly)} {wonly or ''}")

# ---- v3.90 check: every fork building carries an explicit cost, and the cost-scaling table covers every era ----
_LEAD = r'\s*(\d+/\d+|\d{2,4}|maintenance \d+)\s*'
def _top(spec):
    d = 0; out = []; cur = ''
    for ch in spec:
        d += ch in '[⟨('; d -= ch in ']⟩)'
        if ch == ';' and d == 0: out.append(cur); cur = ''
        else: cur += ch
    return out + [cur]
nocost = []
for k, c in rows.items():
    for name, spec, a, e in _specs(c[5]):
        if re.match(r'\s*unit\b', spec) or re.search(r'\bStrength \d', spec[:80]) or re.search(r'world wonder|national wonder|\bwonder\b|Unbuildable|buy-only|improvement\b', spec[:60]): continue
        if re.search(r'Costs \[\d+\] \[', spec) and not any(re.fullmatch(_LEAD, p) for p in _top(spec)[:4]): continue   # bought from a stockpile
        if not any(re.fullmatch(r'\s*\d+/\d+\s*', p) or re.fullmatch(r'\s*\d{2,4}\s*', p) for p in _top(spec)[:4]): nocost.append(name)
_cs = re.search(r'\| Era \| Buildings \| Units, wonders and spaceship parts \|\n\|[-|]+\|\n((?:\|[^\n]*\|\n)+)', t)
_eras = [l.strip('|').split('|')[0].strip() for l in _cs.group(1).strip().split('\n')] if _cs else []
missing = [e for e in EO if e not in _eras]
print(f"  {P(not nocost and not missing)}  every fork building has an explicit cost; the cost-scaling table covers every era — {len(nocost)} without cost {nocost[:4] or ''}, eras missing {missing or 0}")

# ---- v3.95 check: every breakthrough named in a tech conditional exists, including names nested in De Morgan ORs ----
_names = {re.sub(r'^\*\*|\*\*$', '', c[1]).strip() for c in rows.values()}
_names |= {m for c in rows.values() for m in re.findall(r'\(([^()]+)\)', c[1])}          # alternative names in a row title
_canon_tech = set()
try:
    for _col in json5.load(open('unciv/Techs.json', encoding='utf-8')):
        for _tt in _col.get('techs', []): _canon_tech.add(_tt['name'])
except Exception: pass
_body_all = t[:t.index('## Changelog')]
badtech = []
_uniq = ' '.join(re.findall(r'⟨[^⟩]*⟩', _body_all))       # real uniques only; backticked text describes patterns with placeholders
for m in re.finditer(r'<(?:after|before) discovering \[((?:[^\[\]]|\[(?:[^\[\]]|\[[^\[\]]*\])*\])*)\]>', _uniq):
    inner = m.group(1)
    leaves = [x.strip() for x in re.findall(r'\[([^\[\]{}]+)\]', '[' + inner + ']')] if '[' in inner or '{' in inner else [inner]
    for x in leaves:
        x = re.sub(r'^non-', '', x).strip()
        if x in ('...', '…') or not x: continue
        if x not in _names and x not in _canon_tech: badtech.append(x)
print(f"  {P(not badtech)}  every breakthrough named in a tech conditional exists — {len(badtech)} {sorted(set(badtech))[:5] or ''}")

# ---- v3.98 check: no prerequisite cell nests parentheses (the strip pattern would silently lose an ID) ----
nested = []
for k, c in rows.items():
    d = mx = 0
    for ch in c[4]:
        d += ch == '('; d -= ch == ')'; mx = max(mx, d)
    if mx >= 2: nested.append(k)
lost_ids = []
for k, c in rows.items():
    written = set(PQ.written_ids(c[4], set(rows))) - {k}
    read = {p for grp in PQ.parse(c[4], set(rows)) for o in grp for p in o}
    if written - read: lost_ids.append((k, sorted(written - read)))
nested = []
print(f"  {P(not lost_ids)}  every prerequisite ID is read by the shared parser (prereq.py) — {len(nested)} nested, {len(lost_ids)} losing IDs {(nested + lost_ids)[:4] or ''}")

# ---- v3.105 check: no prerequisite relies on operator precedence ----
prec = []
for k, c in rows.items():
    s = PQ._cut_commentary(PQ._strip_descriptions(c[4]))
    terms = PQ._split(s, ['+'])
    for term in terms:
        tt = term.strip()
        ids_here = [x for x in re.findall(IDRX, tt) if x in rows]
        token_group = re.match(r'[A-Z_]+ (token )?\(', tt)
        if len(terms) > 1 and re.search(r'\bor\b', tt) and ids_here and not token_group and not (tt.startswith('(') and tt.endswith(')')):
            prec.append((k, 'ungrouped alternatives')); break
        body_ = PQ._term_body(term, set(rows))
        if re.search(r'\bor\b', body_):
            for o in PQ._split(body_, ['or', ',']):
                oo = o.strip()
                if len([x for x in re.findall(IDRX, oo) if x in rows]) > 1 and not (oo.startswith('(') and oo.endswith(')')):
                    prec.append((k, 'ungrouped multi-row alternative')); break
print(f"  {P(not prec)}  no prerequisite relies on operator precedence — {len(prec)} {prec[:4] or ''}")

# ---- v3.107 check: a prerequisite on a validated result appears only on a row that declares the matching world ----
DECL = re.compile(r'Only in [A-Z][a-z-]+(?: [A-Z][a-z-]+)? worlds|[A-Z][a-z-]+ worlds only|\*[A-Z][a-z-]+ only\.?\*|[A-Z][a-z]+-exclusive|only where the FTL method is')   # v3.111: FQ1-outcome rows declare the method, not a World Truth
undeclared = [k for k, c in rows.items() if re.search(r'validated\)', c[4]) and not DECL.search(c[5])]
print(f"  {P(not undeclared)}  every validated prerequisite sits on a row that declares its world — {len(undeclared)} {undeclared or ''}")

# ---- v3.109 check: both records of every dual path agree, and every focus they name exists ----
def _dual_check(text):
    import re as _re
    bd = text[:text.index('\n## 4.')]; cur = None; homef = {}; lines_of = {}
    for l in bd.split('\n'):
        m = _re.match(r"^#{2,4} FOCUS: ([A-Z][A-Z &'-]+?)\s*(?:\S+)?\s*$", l)
        if m: cur = m.group(1).strip().title(); continue
        mm = _re.match(r'^\| ([A-Z][A-Z0-9-]*) \| \*\*', l)
        if mm and cur: homef[mm.group(1)] = cur
        if cur and l.startswith('*Also reachable in this focus'):
            for x in set(_re.findall(IDRX, l)) & set(rows): lines_of.setdefault(x, set()).add(cur)
    foci = set(homef.values()); text_of = {}; bad = []
    for k, c in rows.items():
        if k not in homef: continue
        m = _re.search(r'(?:Also )?(?:discoverable|reachable) through ([^.*()]+)', c[5] + ' ' + c[6], _re.I)
        if not m: continue
        for n in _re.split(r',\s*|\s+or\s+|\s+and\s+', m.group(1)):
            n = _re.sub(r'\s+focus$', '', _re.sub(r'^the\s+', '', n.strip(), flags=_re.I), flags=_re.I).strip()
            hit = [f for f in foci if f.lower() == n.lower()]
            if hit and hit[0] != homef[k]: text_of.setdefault(k, set()).add(hit[0])
            elif not hit and n: bad.append((k, 'names "' + n + '"'))
    for k in set(lines_of) | set(text_of):
        if lines_of.get(k, set()) != text_of.get(k, set()): bad.append((k, f"line {sorted(lines_of.get(k, set()))} ≠ text {sorted(text_of.get(k, set()))}"))
    return bad, len(set(lines_of) | set(text_of))
_db, _dn = _dual_check(open(sys.argv[1] if len(sys.argv) > 1 else 'tt.md', encoding='utf-8').read())
print(f"  {P(not _db)}  both records of every dual path agree, every named focus exists — {_dn} dual-path rows, {len(_db)} problems {_db[:4] or ''}")

# ---- v3.111 check: every breakthrough row is a well-formed table row, closing pipe included ----
# (the battery reads a row without its closing pipe, but reach.py — and so the generator, the harness and the viewer's
#  reference parse — does not, so a malformed row would vanish from the tools while every check here still passed)
_raw = [l for l in open(F, encoding='utf-8').read().split('\n') if re.match(r'^\| [A-Z][A-Z0-9-]* \| \*\*', l)]
_bad = [l.split(' | ')[0][2:] for l in _raw if not l.rstrip().endswith('|')]
print(f"  {P(not _bad)}  every breakthrough row is a well-formed table row, closing pipe included — {len(_raw)} rows, {len(_bad)} malformed {_bad[:5] or ''}")
