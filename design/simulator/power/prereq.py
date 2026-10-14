"""The one prerequisite parser, shared by the battery, the generator and the harness.

  • A parenthesis whose content begins with a row ID is a group; any other parenthesis is a description, stripped
    innermost-first (so "(Archery — the samurai bow)" and "(but NOT SO04)" are commentary, "(G07 or FA01 + FA02)" is a group).
  • Commentary after a dash outside every parenthesis is dropped ("… — Botanical Classification, or …").
  • Terms are split on '+' outside parentheses (AND). When one group holds all of a term's IDs — as in
    "HIGH_ENERGY_PHYSICS (NP03 …, or QM-E02 …)" — the group is the term.
  • Within a term that contains 'or', options are split on 'or' and on commas outside parentheses (OR); the IDs within
    an option are ANDed.
Returns [[[ids…], …], …]: a list of AND-terms, each a list of OR-options, each a list of ANDed IDs."""
import re
IDRX = r'\b([A-Z]{1,3}-?[A-Z]?\d{1,2}[A-Z]?(?:-W|-V\d+)?|ME-B)\b'
_START_ID = re.compile(r'\s*(?:' + IDRX + r')')
def _strip_descriptions(s):
    while True:
        for m in re.finditer(r'\(([^()]*)\)', s):
            if not _START_ID.match(m.group(1)):
                s = s[:m.start()] + s[m.end():]; break
        else:
            return s
def _depth0(s):
    d = 0
    for i, ch in enumerate(s):
        d += ch == '('; d -= ch == ')'
        yield i, ch, d
def _cut_commentary(s):
    for i, ch, d in _depth0(s):
        if d == 0 and s.startswith(' — ', i): return s[:i]
    return s
def _split(s, seps):
    out, last = [], 0
    for i, ch, d in _depth0(s):
        if d != 0 or i < last: continue
        for sep in seps:
            if s.startswith(sep, i) and (sep in '+,' or (not s[i-1:i].isalnum() and not s[i+len(sep):i+len(sep)+1].isalnum())):
                out.append(s[last:i]); last = i + len(sep); break
    return out + [s[last:]]
def _groups(s):
    """top-level parenthesised groups (start, end) of s"""
    out, d, st = [], 0, None
    for i, ch in enumerate(s):
        if ch == '(':
            if d == 0: st = i
            d += 1
        elif ch == ')':
            d -= 1
            if d == 0 and st is not None: out.append((st, i))
    return out
def _term_body(term, known):
    """if one top-level group holds all of the term's IDs, the group is the term"""
    t = term.strip()
    ids_all = [x for x in re.findall(IDRX, t) if known is None or x in known]
    for a, b in _groups(t):
        inner = t[a + 1:b]; ids_in = [x for x in re.findall(IDRX, inner) if known is None or x in known]
        if ids_in and len(ids_in) == len(ids_all): return _term_body(inner, known)
    return t
def parse(pre, known=None):
    s = _cut_commentary(_strip_descriptions(pre))
    out = []
    for term in _split(s, ['+']):
        body = _term_body(term, known)
        has_or = re.search(r'\bor\b', body) is not None
        opts = []
        for o in _split(body, ['or', ','] if has_or else ['or']):
            ids = [x for x in re.findall(IDRX, o) if known is None or x in known]
            if ids: opts.append(ids)
        if opts: out.append(opts)
    return out

def written_ids(pre, known=None):
    """the IDs a reader sees once descriptions and trailing commentary are set aside"""
    return [x for x in re.findall(IDRX, _cut_commentary(_strip_descriptions(pre))) if known is None or x in known]
