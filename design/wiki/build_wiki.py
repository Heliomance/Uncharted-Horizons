#!/usr/bin/env python3
"""Build the Uncharted Horizons design wiki from the tech-tree design document.

The design document (design/tech_tree.md) is the source of truth, and every wiki page is generated
from it. The pages are cross-linked: breakthrough IDs, section references (§1.2), section titles
cited in italics, World-Truth axes, flags and understanding tokens, and focus names all become links,
and every breakthrough lists the breakthroughs it leads to.

    python3 design/wiki/build_wiki.py --out build/wiki          # write the pages into a folder
    python3 design/wiki/build_wiki.py --sync-into Repo.wiki      # update a checkout of the wiki
    python3 design/wiki/build_wiki.py --check                    # build and validate, write nothing

--sync-into writes the pages into an existing checkout of the wiki repository, deletes the pages this
script generated last time but no longer produces (it records them in .generated-pages), and leaves
pages written by hand alone. Every build validates every internal link and anchor first, and writes
nothing if one is broken.
"""

from __future__ import annotations

import argparse
import collections
import dataclasses
import html
import re
import sys
import unicodedata
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
DEFAULT_SOURCE = HERE.parent / 'tech_tree.md'
MANIFEST = '.generated-pages'
SOURCE_PATH_IN_REPO = 'design/tech_tree.md'

TIERS = ['CORE', 'STANDARD', 'UNCOMMON', 'RARE', 'UNIQUE']
ERAS = ['Primitive', 'Ancient', 'Classical', 'Medieval', 'Early Modern', 'Modern', 'Atomic', 'Space']


class BuildError(Exception):
    pass


# ---------------------------------------------------------------------------------------------------
# Markdown helpers

def plain_text(md: str) -> str:
    """The text GitHub renders for a line of inline Markdown (used to derive heading anchors)."""
    s = re.sub(r'`([^`]*)`', r'\1', md)
    s = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', s)
    s = re.sub(r'(\*\*|__)(.+?)\1', r'\2', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'\1', s)
    return html.unescape(s)


def github_slug(heading: str) -> str:
    """GitHub's heading anchor: lowercase, punctuation and symbols dropped, spaces to hyphens."""
    kept = []
    for ch in plain_text(heading).strip().lower():
        category = unicodedata.category(ch)
        if ch in '- ' or category[0] in 'LM' or category in ('Nd', 'Pc'):
            kept.append(ch)
    return ''.join(kept).replace(' ', '-')


def page_anchors(markdown: str) -> list[str]:
    """Every heading anchor a rendered page will have, with GitHub's numbering of repeats."""
    seen = collections.Counter()
    anchors = []
    in_fence = False
    for line in markdown.split('\n'):
        if line.startswith('```'):
            in_fence = not in_fence
            continue
        m = re.match(r'^(#{1,6})\s+(.*\S)\s*$', line)
        if m and not in_fence:
            slug = github_slug(m.group(2))
            anchors.append(slug if not seen[slug] else f'{slug}-{seen[slug]}')
            seen[slug] += 1
    return anchors


def link_title(text: str) -> str:
    return text.replace('"', "'").replace('\n', ' ').strip()


def norm_title(text: str) -> str:
    s = plain_text(text).lower().replace('&', ' and ')
    s = re.sub(r'[^\w\s-]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def trim_lines(lines: list[str]) -> list[str]:
    """Drop blank lines and horizontal rules from both ends of a block."""
    lines = list(lines)
    while lines and lines[0].strip() in ('', '---'):
        lines.pop(0)
    while lines and lines[-1].strip() in ('', '---'):
        lines.pop()
    return lines


def split_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|'):
        s = s[:-1]
    return [c.strip() for c in s.split('|')]


def title_case(upper: str) -> str:
    small = {'AND': 'and', 'THE': 'the', 'OF': 'of', '&': '&'}
    words = upper.split()
    return ' '.join(small.get(w, w.capitalize()) if i else w.capitalize() for i, w in enumerate(words))


# ---------------------------------------------------------------------------------------------------
# The document as a tree of sections

@dataclasses.dataclass
class Section:
    title: str
    level: int
    body: list[str]
    children: list['Section']

    def child(self, pattern: str) -> 'Section':
        for c in self.children:
            if re.search(pattern, c.title, re.I):
                return c
        raise BuildError(f'no section matching {pattern!r} under {self.title!r}')

    def take(self, pattern: str) -> 'Section':
        """Remove and return the child matching pattern."""
        c = self.child(pattern)
        self.children.remove(c)
        return c


def parse_sections(lines: list[str]) -> Section:
    root = Section('', 0, [], [])
    stack = [root]
    for line in lines:
        m = re.match(r'^(#{1,6})\s+(.*\S)\s*$', line)
        if m:
            sec = Section(m.group(2), len(m.group(1)), [], [])
            while stack[-1].level >= sec.level:
                stack.pop()
            stack[-1].children.append(sec)
            stack.append(sec)
        else:
            stack[-1].body.append(line)
    return root


LEADIN_RE = re.compile(r'^\*\*(?P<title>(?:[^*]|\*(?!\*))+?)\*\*(?P<paren>\s*\([^()]*\))?(?P<punct>[.:])?(?P<rest>.*)$')


def split_leadin(line: str):
    """A paragraph opening with a bold title ("**Filter discipline.** Text...") -> (heading, text)."""
    m = LEADIN_RE.match(line)
    if not m:
        return None
    title, paren, punct, rest = m.group('title').strip(), (m.group('paren') or '').strip(), m.group('punct'), m.group('rest')
    if title.endswith((':', '.')) and (paren or punct):       # "**Title.** (1) text": the parenthesis is text
        rest = line[m.end('title') + 2:]
        paren, punct = '', None
    if len(plain_text(title)) > 100:
        return None
    if not (title.endswith((':', '.')) or punct or not rest.strip()):
        return None
    if rest.strip() and not re.match(r'\s+[A-Z0-9(*"“⟨\[`]', rest):
        return None
    heading = title.rstrip(':.').strip() + (f' {paren}' if paren else '')
    return heading, rest.strip()


def promote_leadins(sec: Section, recursive: bool = True) -> None:
    """Turn paragraph lead-ins into child sections, so they get headings and anchors."""
    body, promoted, current = [], [], None
    for line in sec.body:
        lead = split_leadin(line)
        if lead:
            current = Section(lead[0], sec.level + 1, [lead[1]] if lead[1] else [], [])
            promoted.append(current)
            continue
        (current.body if current else body).append(line)
    sec.body = body
    sec.children = promoted + sec.children
    if recursive:
        for c in sec.children:
            if c not in promoted:
                promote_leadins(c)


# ---------------------------------------------------------------------------------------------------
# Breakthroughs and focus areas

@dataclasses.dataclass(eq=False)
class Breakthrough:
    id: str
    name: str
    tier: str
    era: str
    prereq: str
    unlocks: str
    notes: str
    focus: 'Focus'
    hard: list[str] = dataclasses.field(default_factory=list)
    alt: list[str] = dataclasses.field(default_factory=list)
    leads_to: list['Breakthrough'] = dataclasses.field(default_factory=list)

    @property
    def heading(self) -> str:
        return f'{self.id} · {self.name}'

    @property
    def anchor(self) -> str:
        return github_slug(self.heading)

    @property
    def hover(self) -> str:
        return link_title(f'{self.name} · {self.tier} · {self.era}')


@dataclasses.dataclass
class FocusGroup:
    title: str | None
    prose: list[str]
    rows: list[Breakthrough]


@dataclasses.dataclass(eq=False)
class Focus:
    name: str
    emoji: str
    page: str
    available: str
    also: str
    intro: list[str]
    groups: list[FocusGroup]
    outro: list[str]

    @property
    def rows(self) -> list[Breakthrough]:
        return [b for g in self.groups for b in g.rows]


def parse_focus(sec: Section) -> Focus:
    raw = re.match(r'FOCUS:\s*(.+)$', sec.title).group(1).strip()
    m = re.match(r"([A-Z][A-Z &'-]*[A-Z])\s*(.*)$", raw)
    name, emoji = title_case(m.group(1)), m.group(2).strip()
    focus = Focus(name, emoji, name.replace('&', 'and').replace(' ', '-'), '', '', [], [], [])
    blocks: list[tuple[str, list]] = []          # ('prose', lines) / ('table', rows)
    for line in sec.body:
        s = line.strip()
        if s.startswith('*Available from:'):
            focus.available = s[1:-1].split(':', 1)[1].strip() if s.endswith('*') else s.split(':', 1)[1].strip()
            continue
        if s.startswith('*Also reachable in this focus'):
            focus.also = s
            continue
        if s.startswith('|'):
            cells = split_row(s)
            if cells[0] == '#' or re.fullmatch(r':?-+:?', cells[0]):
                if not blocks or blocks[-1][0] != 'table':
                    blocks.append(('table', []))
                continue
            if len(cells) != 7:
                raise BuildError(f'{name}: row {cells[0]} has {len(cells)} cells, not 7')
            bid, bname, tier, era, prereq, unlocks, notes = cells
            nm = re.fullmatch(r'\*\*(.+?)\*\*', bname)
            if not nm or tier not in TIERS or era not in ERAS:
                raise BuildError(f'{name}: unexpected row {cells[:4]}')
            blocks[-1][1].append(Breakthrough(bid, nm.group(1), tier, era, prereq, unlocks, notes, focus))
            continue
        if blocks and blocks[-1][0] == 'prose':
            blocks[-1][1].append(line)
        else:
            blocks.append(('prose', [line]))
    pending: list[str] = []
    seen_table = False
    for kind, content in blocks:
        if kind == 'prose':
            pending += content
            continue
        prose = trim_lines(pending)
        pending = []
        if not seen_table:
            focus.intro = prose
            focus.groups.append(FocusGroup(None, [], content))
            seen_table = True
            continue
        title = None
        if prose:
            lead = split_leadin(prose[0])
            if lead and not lead[1]:
                title = lead[0].title() if lead[0].isupper() else lead[0]
                prose = trim_lines(prose[1:])
        focus.groups.append(FocusGroup(title, prose, content))
    focus.outro = trim_lines(pending)
    return focus


def strip_cost(prereq: str) -> str:
    return re.split(r'\s+—\s+\*\*cost', prereq)[0]


def cost_note(prereq: str) -> str:
    m = re.search(r'\*\*cost ([^*]+)\*\*', prereq)
    return m.group(1) if m else ''


class Tree:
    """Every focus and breakthrough, with the regular expressions that find their IDs in text."""

    def __init__(self, foci: list[Focus]):
        self.foci = foci
        self.by_id: dict[str, Breakthrough] = {}
        for f in foci:
            for b in f.rows:
                if b.id in self.by_id:
                    raise BuildError(f'duplicate breakthrough ID {b.id}')
                self.by_id[b.id] = b
        ids = sorted(self.by_id, key=len, reverse=True)
        self.id_re = re.compile(r'(?<![A-Za-z0-9_-])(' + '|'.join(map(re.escape, ids)) + r')(?![A-Za-z0-9_-])')
        self.focus_by_page = {f.page: f for f in foci}
        self.order = {b.id: i for i, b in enumerate(b for f in foci for b in f.rows)}
        for f in foci:
            for b in f.rows:
                b.hard, b.alt = self.parse_prereq(b.prereq)
                for pid in b.hard + b.alt:
                    if pid in self.by_id:
                        self.by_id[pid].leads_to.append(b)

    def starts_with_id(self, text: str) -> bool:
        t = text.lstrip()
        return t.startswith('⟦') or bool(self.id_re.match(t))

    def collapse_groups(self, text: str) -> str:
        """Mark grouping parentheses ⟦…⟧ and delete descriptive ones, innermost first."""
        t = text
        while '(' in t:
            new = re.sub(r'\(([^()]*)\)', lambda m: f'⟦{m.group(1)}⟧' if self.starts_with_id(m.group(1)) else ' ', t)
            if new == t:
                break
            t = new
        return t

    @staticmethod
    def split_top(text: str, sep_re: str) -> list[str]:
        parts, depth, start = [], 0, 0
        masked = []
        for ch in text:
            if ch == '⟦':
                depth += 1
            elif ch == '⟧':
                depth -= 1
            masked.append(ch if depth == 0 or ch in '⟦⟧' else '\0')
        masked = ''.join(masked)
        for m in re.finditer(sep_re, masked):
            parts.append(text[start:m.start()])
            start = m.end()
        parts.append(text[start:])
        return parts

    def parse_prereq(self, prereq: str) -> tuple[list[str], list[str]]:
        """Required IDs and alternative IDs, read by the notation of §7.0 (descriptions ignored)."""
        hard, alt = [], []
        for term in self.split_top(self.collapse_groups(strip_cost(prereq)), r'\+'):
            ids = self.id_re.findall(term)
            if not ids:
                continue
            target = alt if re.search(r'\bor\b|,', term) else hard
            target += [i for i in ids if i not in target]
        return hard, alt

    def parse_available(self, text: str) -> list[list[str]]:
        """'A + B, or C' -> [[A, B], [C]]; alternatives without an ID come back empty."""
        t = self.collapse_groups(text).replace('⟦', '').replace('⟧', '')
        return [self.id_re.findall(alt) for alt in re.split(r',\s*or\s+|\s+or\s+', t)]

    def focus_era(self, f: Focus) -> str:
        """The era a focus normally opens in: 'Start', or the era of its earliest route made only of CORE
        breakthroughs (the route every civilisation is certain to find), else of its earliest route."""
        if 'Game Start' in f.available:
            return 'Start'
        alternatives = self.parse_available(f.available)
        if any(not ids for ids in alternatives) and 'location' in f.available:
            return 'Start'
        routes = [[self.by_id[i] for i in ids if i in self.by_id] for ids in alternatives]
        routes = [r for r in routes if r]
        if not routes:
            return 'Start'
        core = [r for r in routes if all(b.tier == 'CORE' for b in r)] or routes
        return ERAS[min(max(ERAS.index(b.era) for b in r) for r in core)]


# ---------------------------------------------------------------------------------------------------
# Pages

@dataclasses.dataclass
class Page:
    name: str
    crumb: tuple | None           # (where it comes from, e.g. "Design document §1.3", (parent page, its title) or None)
    items: list = dataclasses.field(default_factory=list)
    text: str = ''

    def h(self, level: int, text: str):
        self.items.append(('h', level, text))

    def md(self, lines, **opts):
        lines = trim_lines(lines if isinstance(lines, list) else lines.split('\n'))
        if lines:
            self.items.append(('md', lines, opts))

    def lazy(self, fn: Callable[[], str]):
        self.items.append(('lazy', fn))

    def raw(self, text: str):
        self.items.append(('raw', text))



SECTION_PAGES = {'1': 'Discovery-Mechanics', '1.1': 'Discovery-Mechanics', '1.2': 'Discovery-Mechanics',
                 '1.3': 'Environmental-Modifiers', '1.4': 'Discovery-States', '1.5': 'Grand-Endeavours',
                 '2': 'Eras', '3': 'Focus-Areas', '4': 'FTL-Endgame', '5': 'World-Truths', '6': 'Game-Balance-Rules',
                 '7': 'Base-Game-Object-Assignments', '7.0': 'Mechanical-Grounding', '8': 'Summary-Statistics'}

# Words near a section reference that point it at a more specific page (checked in order).
SECTION_CONTEXT = {
    '1.2': [(r'airship disaster|confidence ladder', 'Competing-Solutions', 'Lost Confidence — the Airship Disaster'),
            (r'multiplier', 'Breakthrough-Tiers', 'Cost Multipliers (World-Truth-conditional thresholds)'),
            (r'competing solution|locked out|lock-out|detour margin', 'Competing-Solutions', None),
            (r'diffusion|post-press|internet phase', 'Knowledge-Diffusion', None),
            (r'chain', 'Breakthrough-Tiers', 'RARE Gateway Chains'),
            (r'resource rule|trade (?:can supply|satisfies)|strategic re', 'Discovery-Mechanics', 'Strategic Resource Access'),
            (r'50/50|80/20|routing|pacing', 'Discovery-Mechanics', 'Early-Game Pacing & Insight Routing'),
            (r'calibration', 'Discovery-Mechanics', 'Insight Scale & Calibration'),
            (r'roll', 'Discovery-Mechanics', 'Insight and Discovery'),
            (r'absent|absence|removal truth|dead-end|consolation|validate', 'Breakthrough-Tiers', 'How It Feels to the Player'),
            (r'\bcore\b|tier', 'Breakthrough-Tiers', None)],
    '4': [(r'elemental worlds', 'FTL-in-Elemental-Worlds', None),
          (r'victor|generation ship', 'Victories', None)],
    '5': [(r'qualifies as a world truth', 'Foundational-Questions', 'What qualifies as a World Truth'),
          (r'principle 3', 'World-Truths', 'The Six Anti-Explosion Principles')],
    '6': [(r'guarantee', 'Game-Balance-Rules', 'Guaranteed Path Integrity'),
          (r'competing solutions group', 'Game-Balance-Rules', 'Competing Solutions Reference')],
    '7.0': [(r'filter discipline', 'Mechanical-Grounding', 'Filter discipline'),
            (r'ruleset derivation', 'Mechanical-Grounding', 'World-Truth ruleset derivation'),
            (r'resource discipline', 'Mechanical-Grounding', 'Resource discipline'),
            (r'rulebook|enumerates', 'Mechanical-Grounding', None)],
}

TOKEN_TARGETS = {
    'GUNPOWDER_ABSENT': ('Worked-Example-Worlds', 'The No-Gunpowder World'),
    'FOSSIL_FUELS_ABSENT': ('Worked-Example-Worlds', 'The No-Fossil-Fuels World'),
    'FUSION_ABSENT': ('Worked-Example-Worlds', 'The No-Fusion World'),
    'AEOLIPILE_VIABLE': ('Worked-Example-Worlds', 'The Early Steam World'),
    'ENHANCED_SPRINGS': ('Worked-Example-Worlds', 'The Enhanced Springs World'),
    'ANTIKYTHERA_TRADITION': ('Worked-Example-Worlds', 'The Antikythera Tradition'),
    'MATTER_THEORY': ('Foundational-Questions', 'Understanding Tokens'),
    'DISEASE_THEORY': ('Foundational-Questions', 'Understanding Tokens'),
    'MASS_MEDICINE': ('Foundational-Questions', 'Understanding Tokens'),
    'LIFE_THEORY': ('Foundational-Questions', 'Understanding Tokens'),
    'THERMO_THEORY': ('Foundational-Questions', 'Understanding Tokens'),
    'HIGH_ENERGY_PHYSICS': ('Foundational-Questions', 'The deep-physics tokens (Symmetry Principle)'),
    'EXOTIC_MATTER': ('Foundational-Questions', 'The deep-physics tokens (Symmetry Principle)'),
}

FOCUS_ALIASES = {'Social Organisation': 'Social-Organization', 'Textiles': 'Textiles-and-Materials',
                 'Textiles and Materials': 'Textiles-and-Materials', 'Relativity and Cosmology': 'Relativity-and-Cosmology',
                 'Philosophy & the Arts': 'Philosophy-and-the-Arts'}

ITALIC_ALIASES = {'competing solution': 'Competing-Solutions', 'competing solutions': 'Competing-Solutions',
                  'grand endeavour': 'Grand-Endeavours', 'grand endeavours': 'Grand-Endeavours',
                  'knowledge diffusion': 'Knowledge-Diffusion', 'world truths': 'World-Truths'}

PAGE_BLURBS = {
    'Discovery-Mechanics': 'research by focus area, the active/spread split, Insight and the discovery roll',
    'Breakthrough-Tiers': 'CORE to UNIQUE, cost multipliers and RARE gateway chains',
    'Competing-Solutions': 'pre-empted alternatives, lock-out, and the Airship Disaster',
    'Knowledge-Diffusion': 'how widespread breakthroughs spread, before and after the press and the Internet',
    'Environmental-Modifiers': 'how geography and circumstance tilt Insight',
    'Discovery-States': 'Unknown, Revealed and Discovered, and how ideas are revealed',
    'Grand-Endeavours': 'directed research towards a revealed breakthrough',
    'Eras': 'era entry, and the Insight span and pace of each era',
    'FTL-Endgame': 'the science victory: hypotheses, tests, building and the prototype',
    'FTL-in-Elemental-Worlds': 'the six FTL methods across both ontologies',
    'Victories': 'how the FTL ship and the Generation Ship victories are built in Unciv',
    'World-Truths': 'the variable laws of physics and the rules that keep them bounded',
    'Foundational-Questions': 'matter, disease, life and heat: the decisive experiments and understanding tokens',
    'Worked-Example-Worlds': 'no gunpowder, no fusion, no fossil fuels, early steam, springs, Antikythera',
    'Game-Balance-Rules': 'removal and enabling truths, guarantees, trading, Competing Solutions reference',
    'Mechanical-Grounding': 'what a breakthrough may grant in Unciv, and the notation used in the tables',
    'Base-Game-Object-Assignments': 'every Civ V wonder, building, improvement and unit mapped to its breakthrough',
    'Summary-Statistics': 'counts of foci, breakthroughs and tiers',
    'Changelog': 'every revision of the design, newest first',
    'Breakthrough-Index': 'every breakthrough, A to Z',
    'Breakthroughs-by-Era': 'every breakthrough, era by era',
    'Breakthroughs-by-Tier': 'every breakthrough, tier by tier',
    'New-Objects': 'every new building, unit, improvement and resource, with the breakthrough that grants it',
    'Focus-Areas': 'all 35 foci, how each opens, and how they connect',
}


class Wiki:
    def __init__(self, source_text: str):
        self.lines = source_text.split('\n')
        self.root = parse_sections(self.lines)
        if len(self.root.children) != 1:
            raise BuildError('expected exactly one top-level (#) heading')
        self.doc = self.root.children[0]
        self.pages: dict[str, Page] = {}
        self.links: list[tuple[str, str, str | None]] = []
        self.warnings: list[str] = []
        self.version = ''
        self.used: set[int] = set()
        self.parse()

    # -- parsing -------------------------------------------------------------------------------------

    def numbered(self, n: str) -> Section:
        return self.doc.child(rf'^{re.escape(n)}\.\s')

    def parse(self):
        foci_sec = self.numbered('3')
        self.tree = Tree([parse_focus(s) for s in foci_sec.children if s.title.startswith('FOCUS:')])
        self.used.add(id(foci_sec))
        for s in foci_sec.children:
            if s.title.startswith('FOCUS:'):
                if s.children:
                    raise BuildError(f'{s.title} has subsections, which a focus page has no place for')
                self.used.add(id(s))
        if len(self.tree.foci) < 30:
            raise BuildError(f'found only {len(self.tree.foci)} focus sections')
        self.changelog = self.doc.child(r'^Changelog')
        versions = [re.match(r'v(\d+\.\d+)', c.title) for c in self.changelog.children]
        self.version = next(('v' + m.group(1) for m in versions if m), '')
        title_version = re.search(r'\((v[\d.]+)\)', self.doc.title)
        if title_version and title_version.group(1) != self.version:
            self.warnings.append(f'document title says {title_version.group(1)}, latest changelog entry is {self.version}')
        axes = re.findall(r'\*\*FQ(\d+): ([^*]+)\*\*', '\n'.join(self.lines))
        self.axes = {int(n): name.strip() for n, name in axes}

    def emit(self, page: Page, sec: Section, level: int, heading: str | None = None, with_heading: bool = True, **opts):
        """Place a section (and everything under it) on a page."""
        self.used.add(id(sec))
        if with_heading:
            page.h(level, heading or sec.title)
            level += 1
        page.md(sec.body, **opts)
        for c in sec.children:
            self.emit(page, c, level, **opts)

    def check_everything_placed(self):
        """Fail rather than drop a section the generator does not know where to put."""
        missing = []

        def walk(sec, path):
            for c in sec.children:
                here = path + [c.title]
                if id(c) not in self.used and (any(l.strip() not in ('', '---') for l in c.body) or c.children):
                    missing.append(' › '.join(here))
                else:
                    walk(c, here)
        walk(self.doc, [])
        if missing:
            raise BuildError('these sections of the document have no place in the wiki; extend build_wiki.py:\n  '
                             + '\n  '.join(missing))

    # -- page registry, titles and anchors -----------------------------------------------------------

    def page(self, name: str, crumb: tuple | None) -> Page:
        if name in self.pages:
            raise BuildError(f'page {name} built twice')
        p = Page(name, crumb)
        self.pages[name] = p
        return p

    def index_titles(self):
        """Every heading, by normalised title, for links from italic citations and section references."""
        self.heading_anchor: dict[tuple[str, str], str] = {}
        self.title_index: dict[str, tuple[str, str | None]] = {}
        for name in self.pages:
            self.title_index.setdefault(norm_title(name.replace('-', ' ')), (name, None))
        for name, page in self.pages.items():
            seen = collections.Counter()
            for item in page.items:
                if item[0] != 'h':
                    continue
                slug = github_slug(item[2])
                anchor = slug if not seen[slug] else f'{slug}-{seen[slug]}'
                seen[slug] += 1
                key = norm_title(item[2])
                self.heading_anchor.setdefault((name, key), anchor)
                for variant in {key, norm_title(re.split(r':| — ', plain_text(item[2]))[0])}:
                    self.title_index.setdefault(variant, (name, anchor))
        for alias, page in ITALIC_ALIASES.items():
            self.title_index[alias] = (page, None)

    def anchor_for(self, page: str, title: str) -> str:
        key = (page, norm_title(title))
        if key not in self.heading_anchor:
            raise BuildError(f'no heading {title!r} on page {page}')
        return self.heading_anchor[key]

    # -- links -------------------------------------------------------------------------------------

    def url(self, here: str, page: str, anchor: str | None = None) -> str:
        self.links.append((here, page, anchor))
        if page == here:
            return f'#{anchor}' if anchor else page
        return page + (f'#{anchor}' if anchor else '')

    def link(self, here: str, text: str, page: str, anchor: str | None = None, title: str | None = None) -> str:
        if page == here and not anchor:
            return text
        tip = f' "{link_title(title)}"' if title else ''
        return f'[{text}]({self.url(here, page, anchor)}{tip})'

    def bt_link(self, here: str, b: Breakthrough, text: str | None = None) -> str:
        return self.link(here, text or b.id, b.focus.page, b.anchor, b.hover)

    # -- inline Markdown: escaping and cross-linking ------------------------------------------------

    LINK_RE = re.compile(r'\[[^\]\n]*\]\([^)\s]+(?: "[^"\n]*")?\)')

    def outside_links(self, text: str, pattern: re.Pattern, repl) -> str:
        parts, pos = [], 0
        for m in self.LINK_RE.finditer(text):
            parts.append(pattern.sub(repl, text[pos:m.start()]))
            parts.append(m.group(0))
            pos = m.end()
        parts.append(pattern.sub(repl, text[pos:]))
        return ''.join(parts)

    def inline(self, text: str, here: str, self_id: str | None = None, focus_cells: bool = False) -> str:
        out, pos = [], 0
        for m in re.finditer(r'(`+)(.+?)\1', text):
            out.append(self.prose(text[pos:m.start()], here, self_id, focus_cells))
            out.append(m.group(1) + self.break_wiki_links(m.group(2)) + m.group(1))
            pos = m.end()
        out.append(self.prose(text[pos:], here, self_id, focus_cells))
        return ''.join(out)

    def prose(self, text: str, here: str, self_id: str | None, focus_cells: bool) -> str:
        if not text:
            return text
        t = text.replace('<', '&lt;')       # Unciv conditionals (<when defending>) would be eaten as HTML

        def italic(m):
            inner = m.group(1)
            key = norm_title(inner)
            words = key.split()
            target = self.title_index.get(key)
            focus_page = self.focus_page_for(inner)
            if focus_page:
                target = (focus_page, None)
            if not target or (len(words) < 2 and not focus_page):
                return m.group(0)
            page, anchor = target
            if page == here and not anchor:
                return m.group(0)
            return f'*{self.link(here, inner, page, anchor)}*'
        t = self.outside_links(t, re.compile(r'(?<![*\w])\*([^*\n]{3,80}?)\*(?![*\w])'), italic)

        def section_ref(m):
            number = m.group(2) or m.group(4)
            line_before = m.string[:m.start()]
            if re.search(r'Models? I(?:I|\b)[^()]*$', line_before.split('(')[-1]) or 'Model' in line_before[-25:]:
                return m.group(0)
            page = SECTION_PAGES.get(number)
            if not page:
                return m.group(0)
            anchor = None
            start = max(line_before.rfind('. '), line_before.rfind('; '))
            window = (line_before[start + 1:] if start >= 0 and len(line_before) - start > 40 else line_before[-90:]).lower()
            after = m.string[m.end():m.end() + 40]
            for pattern, target_page, title in SECTION_CONTEXT.get(number, []):
                if re.search(pattern, window + ' ' + after.lower()):
                    page, anchor = target_page, (self.anchor_for(target_page, title) if title else None)
                    break
            following = re.match(r',\s*\*?([A-Z][^,;)*]{2,60}?)\*?\s*[),;]', after)
            if following and (page, norm_title(following.group(1))) in self.heading_anchor:
                anchor = self.heading_anchor[(page, norm_title(following.group(1)))]
            return self.link(here, m.group(0), page, anchor) if (page != here or anchor) else m.group(0)
        t = self.outside_links(t, re.compile(r'(§ ?)(\d+(?:\.\d+)?)|\b(Sections?) (\d+(?:\.\d+)?)\b'), section_ref)

        def bt(m):
            b = self.tree.by_id[m.group(1)]
            return m.group(0) if b.id == self_id else self.bt_link(here, b)
        t = self.outside_links(t, self.tree.id_re, bt)

        def axis(m):
            n = int(m.group(1))
            if n not in self.axes:
                return m.group(0)
            page = 'Foundational-Questions' if n >= 9 else 'World-Truths'
            anchor = None if n >= 9 else self.anchor_for('World-Truths', 'Truth Axes')
            return self.link(here, m.group(0), page, anchor, f'FQ{n}: {self.axes[n]}')
        t = self.outside_links(t, re.compile(r'(?<![\w-])FQ(\d{1,2})(?![\w-])'), axis)

        def token(m):
            page, title = TOKEN_TARGETS[m.group(1)]
            return self.link(here, m.group(1), page, self.anchor_for(page, title))
        t = self.outside_links(t, re.compile(r'\b(' + '|'.join(TOKEN_TARGETS) + r')\b'), token)

        t = self.link_focus_names(t, here, focus_cells)
        return self.break_wiki_links(t)

    @staticmethod
    def break_wiki_links(text: str) -> str:
        """GitHub's wiki turns "[[…]]" into a link to a page, even when the first bracket is written as an
        entity or sits in code, so an invisible word joiner (U+2060) goes between adjacent brackets."""
        return re.sub(r'\[(?=\[)', '[\u2060', text)

    def focus_page_for(self, name: str) -> str | None:
        name = name.strip()
        for f in self.tree.foci:
            if name == f.name:
                return f.page
        return FOCUS_ALIASES.get(name)

    def focus_patterns(self):
        """Contexts in which a focus name is a reference to the focus (compiled once)."""
        if hasattr(self, '_focus_patterns'):
            return self._focus_patterns
        names = sorted({f.name for f in self.tree.foci} | set(FOCUS_ALIASES), key=len, reverse=True)
        name = r'(?<![\w-])(?:' + '|'.join(map(re.escape, names)) + r')(?![\w-])'
        sep = r'(?:,\s+(?:and\s+|or\s+)?|\s+(?:and|or)\s+)(?:the\s+)?'
        names_list = name + r'(?:' + sep + name + r')*'
        triggers = [
            rf'\*\*(?P<names>{name})\*\*(?= focus)',
            rf'Insight (?:to|toward|towards) (?P<names>{names_list})',
            rf'(?:discoverable|reachable) through (?:the )?(?P<names>{names_list})',
            rf', from (?P<names>{name})(?=\))',
            rf'\bsee (?P<names>{name})',
            rf'\b(?:Warp|Wormhole|Hyperspace|Tunnelling|Tachyonic|Plenum) in (?P<names>{name})',
            rf'fields \((?P<names>{names_list})',
            rf'(?P<names>{names_list})(?= (?:focus|foci|focuses)\b)',
        ]
        self._focus_patterns = (re.compile(name), re.compile(names_list), [re.compile(t) for t in triggers])
        return self._focus_patterns

    def link_focus_names(self, t: str, here: str, focus_cells: bool) -> str:
        name_re, list_re, triggers = self.focus_patterns()

        def link_names(segment: str) -> str:
            return name_re.sub(lambda m: self.link(here, m.group(0), self.focus_page_for(m.group(0))), segment)

        if focus_cells:                                  # a column that holds nothing but focus names
            return self.outside_links(t, list_re, lambda m: link_names(m.group(0)))

        def repl(m):
            whole, start = m.group(0), m.start('names') - m.start()
            return whole[:start] + link_names(m.group('names')) + whole[start + len(m.group('names')):]
        for trigger in triggers:
            t = self.outside_links(t, trigger, repl)
        return t

    # -- building the pages -------------------------------------------------------------------------

    def build(self) -> dict[str, str]:
        self.build_rules_pages()
        self.build_focus_pages()
        self.build_endgame_pages()
        self.build_truth_pages()
        self.build_reference_pages()
        self.build_changelog_pages()
        self.build_index_pages()
        self.build_home()
        self.check_everything_placed()
        self.index_titles()
        files = {f'{name}.md': self.render(page) for name, page in self.pages.items()}
        files['_Sidebar.md'] = self.sidebar()
        files['_Footer.md'] = self.footer()
        self.validate(files)
        return files

    def render(self, page: Page) -> str:
        here = page.name
        out = []
        if page.crumb:
            source, parent = page.crumb
            bits = ([self.link(here, parent[1], parent[0])] if parent else []) + [source]
            out.append('<sub>' + ' · '.join(bits) + '</sub>')
        for item in page.items:
            kind = item[0]
            if kind == 'h':
                out.append('#' * item[1] + ' ' + item[2].replace('<', '&lt;'))
            elif kind == 'md':
                out.append('\n'.join(self.inline(line, here, focus_cells=self.is_focus_table_row(line, item[2]))
                                     for line in item[1]))
            elif kind == 'lazy':
                out.append(item[1]())
            else:
                out.append(item[1])
        text = '\n\n'.join(part.rstrip() for part in out if part.strip()) + '\n'
        page.text = text
        return text

    @staticmethod
    def is_focus_table_row(line: str, opts: dict) -> bool:
        return bool(opts.get('focus_column')) and line.startswith('|') and not line.startswith('|---')

    @staticmethod
    def crumb(source: str, parent: tuple[str, str] | None = None) -> tuple:
        """The line at the top of a page: its parent page, and where it comes from in the document."""
        return (source, parent)

    # Rules: §1 and §2
    def build_rules_pages(self):
        s1 = self.numbered('1')
        core = s1.child(r'^1\.1\b')
        mech = s1.child(r'^1\.2\b')
        promote_leadins(mech)
        groups = {
            'Discovery-Mechanics': [r'^The Active Focus', r'^Insight and Discovery', r'^Early-Game Pacing', r'^Insight Scale',
                                    r'^Strategic Resource Access'],
            'Breakthrough-Tiers': [r'^Breakthrough Tiers', r'^CORE means', r'^UNIQUE Scaling', r'^UNIQUE Design',
                                   r'^How It Feels', r'^Cost Multipliers', r'^RARE Gateway'],
            'Competing-Solutions': [r'^Competing Solutions', r'^Lost Confidence'],
            'Knowledge-Diffusion': [r'^Knowledge Diffusion'],
        }
        assigned = {}
        for page, patterns in groups.items():
            for c in mech.children:
                if any(re.search(p, c.title) for p in patterns):
                    assigned[id(c)] = page
        for c in mech.children:
            if id(c) not in assigned:
                self.warnings.append(f'§1.2 section {c.title!r} is not assigned to a page; it goes on Discovery-Mechanics')
                assigned[id(c)] = 'Discovery-Mechanics'
        self.used.update({id(s1), id(core), id(mech)})
        p = self.page('Discovery-Mechanics', self.crumb('Design document §1.1–1.2'))
        p.h(2, 'Core Concept')
        p.md(core.body)
        p.md(mech.body)
        for c in mech.children:
            if assigned[id(c)] == 'Discovery-Mechanics':
                self.emit(p, c, 2)
        p.lazy(lambda: '*Section 1.2 continues on ' + ', '.join(
            self.link('Discovery-Mechanics', n.replace('-', ' '), n) for n in groups if n != 'Discovery-Mechanics') + '.*')
        for name in ('Breakthrough-Tiers', 'Competing-Solutions', 'Knowledge-Diffusion'):
            p = self.page(name, self.crumb('Design document §1.2', ('Discovery-Mechanics', 'Discovery Mechanics')))
            mine = [c for c in mech.children if assigned[id(c)] == name]
            for c in mine:      # a section named exactly like its page needs no heading of its own
                self.emit(p, c, 2, with_heading=norm_title(c.title) != norm_title(name.replace('-', ' ')))
            if name == 'Competing-Solutions':
                p.lazy(lambda: 'Every group, with its primary, its alternative and what happens if the primary arrives later: '
                       + self.link('Competing-Solutions', 'Competing Solutions Reference', 'Game-Balance-Rules',
                                   self.anchor_for('Game-Balance-Rules', 'Competing Solutions Reference')) + ' (§6).')
        for number, name in (('1.3', 'Environmental-Modifiers'), ('1.4', 'Discovery-States'), ('1.5', 'Grand-Endeavours')):
            sec = s1.child(rf'^{re.escape(number)}\b')
            promote_leadins(sec)
            p = self.page(name, self.crumb(f'Design document §{number}'))
            self.emit(p, sec, 2, with_heading=False, focus_column=(name == 'Environmental-Modifiers'))
        eras = self.numbered('2')
        promote_leadins(eras)
        p = self.page('Eras', self.crumb('Design document §2'))
        self.emit(p, eras, 2, with_heading=False)
        p.lazy(self.era_counts_line)

    def era_counts_line(self) -> str:
        counts = collections.Counter(b.era for b in self.tree.by_id.values())
        parts = [self.link('Eras', f'{e} ({counts[e]})', 'Breakthroughs-by-Era', github_slug(e)) for e in ERAS]
        return '**Breakthroughs by era:** ' + ' · '.join(parts)

    # Focus pages: §3
    def build_focus_pages(self):
        p = self.page('Focus-Areas', self.crumb('Design document §3'))
        p.lazy(self.focus_areas_body)
        for f in self.tree.foci:
            fp = self.page(f.page, self.crumb('Design document §3', ('Focus-Areas', 'Focus Areas')))
            fp.lazy(lambda f=f: self.focus_header(f))
            if f.intro:
                fp.md(f.intro)
            fp.h(2, 'Overview')
            fp.lazy(lambda f=f: self.focus_overview(f))
            fp.h(2, 'Prerequisite map')
            fp.lazy(lambda f=f: self.focus_graph(f))
            for i, g in enumerate(f.groups):
                fp.h(2, 'Breakthroughs' if i == 0 else (g.title or f'Breakthroughs ({i + 1})'))
                if g.prose:
                    fp.md(g.prose)
                for b in g.rows:
                    fp.h(3, b.heading)
                    fp.lazy(lambda b=b: self.entry(b))
            if f.outro:
                fp.h(2, 'Notes')
                fp.md(f.outro)

    def tier_counts(self, rows) -> str:
        c = collections.Counter(b.tier for b in rows)
        return ' · '.join(f'{t} {c[t]}' for t in TIERS if c[t])

    def era_span(self, rows) -> str:
        idx = sorted(ERAS.index(b.era) for b in rows)
        return ERAS[idx[0]] if idx[0] == idx[-1] else f'{ERAS[idx[0]]} – {ERAS[idx[-1]]}'

    def focus_connections(self, f: Focus):
        builds_on, leads_into = collections.Counter(), collections.Counter()
        for b in f.rows:
            for pid in b.hard + b.alt:
                src = self.tree.by_id.get(pid)
                if src and src.focus is not f:
                    builds_on[src.focus.page] += 1
            for d in b.leads_to:
                if d.focus is not f:
                    leads_into[d.focus.page] += 1
        return builds_on, leads_into

    def focus_header(self, f: Focus) -> str:
        here = f.page
        lines = [f'**Available from:** {self.inline(f.available, here)}']
        if f.also:
            lines.append(self.inline(f.also, here))
        lines.append(f'**{len(f.rows)} breakthroughs** — {self.tier_counts(f.rows)} — {self.era_span(f.rows)}')
        builds_on, leads_into = self.focus_connections(f)
        order = [x.page for x in self.tree.foci]
        if builds_on:
            lines.append('**Builds on:** ' + ' · '.join(
                f'{self.link(here, self.tree.focus_by_page[pg].name, pg)} ({n})' for pg, n in sorted(builds_on.items(), key=lambda kv: order.index(kv[0]))))
        if leads_into:
            lines.append('**Leads into:** ' + ' · '.join(
                f'{self.link(here, self.tree.focus_by_page[pg].name, pg)} ({n})' for pg, n in sorted(leads_into.items(), key=lambda kv: order.index(kv[0]))))
        lines.append('<sub>The numbers count prerequisite links between this focus and the other. '
                     + self.link(here, 'How to read the tables', 'Mechanical-Grounding',
                                 self.anchor_for('Mechanical-Grounding', 'Notation in the Unlocks column')) + '.</sub>')
        return '\n\n'.join(lines)

    def focus_overview(self, f: Focus) -> str:
        here = f.page
        out = []
        for i, g in enumerate(f.groups):
            if i:
                out.append(f'**{g.title or "Further breakthroughs"}**')
            rows = ['| ID | Breakthrough | Tier | Era | Prerequisites |', '|---|---|---|---|---|']
            for b in g.rows:
                rows.append(f'| {self.link(here, b.id, here, b.anchor)} | {b.name} | {b.tier} | {b.era} | '
                            f'{self.inline(b.prereq, here, self_id=b.id)} |')
            out.append('\n'.join(rows))
        return '\n\n'.join(out)

    def entry(self, b: Breakthrough) -> str:
        here = b.focus.page
        lines = [f'- **Tier:** {b.tier} · **Era:** {b.era}',
                 f'- **Prerequisites:** {self.inline(b.prereq, here, self_id=b.id)}',
                 f'- **Unlocks:** {self.inline(b.unlocks, here, self_id=b.id)}']
        if b.notes:
            lines.append(f'- **Notes:** {self.inline(b.notes, here, self_id=b.id)}')
        if b.leads_to:
            order = self.tree.order
            targets = sorted(set(b.leads_to), key=lambda d: order[d.id])
            lines.append('- **Leads to:** ' + ', '.join(self.bt_link(here, d, f'{d.id} {d.name}') for d in targets))
        return '\n'.join(lines)

    def depth_first(self, f: Focus) -> list[Breakthrough]:
        """The focus's breakthroughs, each followed by its descendants within the focus."""
        mine = {b.id for b in f.rows}
        children = {b.id: [d for d in b.leads_to if d.id in mine] for b in f.rows}
        has_parent = {d.id for b in f.rows for d in children[b.id]}
        order, seen = [], set()

        def visit(b):
            if b.id not in seen:
                seen.add(b.id)
                order.append(b)
                for d in sorted(children[b.id], key=lambda x: self.tree.order[x.id]):
                    visit(d)
        for b in [b for b in f.rows if b.id not in has_parent] + f.rows:
            visit(b)
        return order

    def mermaid_id(self, bid: str) -> str:
        return 'n_' + re.sub(r'\W', '_', bid)

    @staticmethod
    def mermaid_label(text: str) -> str:
        return text.replace('"', '#quot;').replace('&', '#38;').replace('<', '#lt;').replace('>', '#gt;')

    MERMAID_STYLES = [
        'classDef CORE fill:#dbeafe,stroke:#1d4ed8,color:#0b1b3b',
        'classDef STANDARD fill:#f1f5f9,stroke:#64748b,color:#0f172a',
        'classDef UNCOMMON fill:#dcfce7,stroke:#15803d,color:#052e16',
        'classDef RARE fill:#fef3c7,stroke:#b45309,color:#3b2005',
        'classDef UNIQUE fill:#fae8ff,stroke:#a21caf,color:#3b0a3f',
        'classDef EXT fill:#ffffff,stroke:#94a3b8,stroke-dasharray:4 3,color:#334155',
    ]

    def focus_graph(self, f: Focus) -> str:
        """The focus's own prerequisite chains. Prerequisites from other foci are left to the overview table:
        drawn as nodes, they turn a large focus into an unreadable web."""
        mine = {b.id for b in f.rows}
        nodes, edges, external = [], [], collections.Counter()
        for b in self.depth_first(f):      # declaring chains together gives Mermaid's layout a better start
            nodes.append(f'  {self.mermaid_id(b.id)}["{self.mermaid_label(b.id + " " + b.name)}"]:::{b.tier}')
        for b in f.rows:
            for kind, ids in (('-->', b.hard), ('-.->', b.alt)):
                for pid in ids:
                    if pid in mine:
                        edges.append(f'  {self.mermaid_id(pid)} {kind} {self.mermaid_id(b.id)}')
                    elif pid in self.tree.by_id:
                        external[b.id] += 1
        body = ['```mermaid', 'flowchart LR', *nodes, *edges, *('  ' + s for s in self.MERMAID_STYLES[:-1]), '```']
        legend = ('<sub>Prerequisites within this focus. Box colour is the tier (blue CORE, grey STANDARD, green UNCOMMON, '
                  'amber RARE, purple UNIQUE); dotted arrows are alternatives (“or”); a line can pass behind another box, '
                  f'so follow it from its start. {sum(1 for n in external.values() if n)} of these {len(f.rows)} breakthroughs '
                  'also need breakthroughs from other foci, which the overview above lists.</sub>')
        return '\n'.join(body) + '\n\n' + legend

    def focus_areas_body(self) -> str:
        here = 'Focus-Areas'
        out = ['Research is directed at focus areas rather than at technologies; each breakthrough below belongs to one home '
               'focus, and some can also be found through another ([' 'dual paths](' + self.url(here, 'Game-Balance-Rules',
               self.anchor_for('Game-Balance-Rules', 'Dual-Path Discovery')) + ')). Five foci are open from the start; '
               'each of the others opens with a breakthrough.']
        rows = ['| Focus | Available from | Breakthroughs | ' + ' | '.join(TIERS) + ' | Eras |',
                '|---|---|---|' + '---|' * len(TIERS) + '---|']
        for f in self.tree.foci:
            c = collections.Counter(b.tier for b in f.rows)
            rows.append(f'| {f.emoji} {self.link(here, f.name, f.page)} | {self.inline(f.available, here)} | {len(f.rows)} | '
                        + ' | '.join(str(c[t] or '') for t in TIERS) + f' | {self.era_span(f.rows)} |')
        out.append('\n'.join(rows))
        out.append('## How the foci open')
        out.append(self.focus_unlock_graph())
        return '\n\n'.join(out)

    def focus_unlock_graph(self) -> str:
        lines = ['```mermaid', 'flowchart LR']
        key = {f.page: 'f_' + re.sub(r'\W', '_', f.page) for f in self.tree.foci}
        for f in self.tree.foci:
            lines.append(f'  {key[f.page]}["{self.mermaid_label(f.emoji + " " + f.name)}"]')
        for f in self.tree.foci:
            alternatives = [ids for ids in self.tree.parse_available(f.available) if ids]
            arrow = '-.->' if len(self.tree.parse_available(f.available)) > 1 else '-->'
            by_source = collections.OrderedDict()
            for ids in alternatives:
                for i in ids:
                    src = self.tree.by_id.get(i)
                    if src:
                        by_source.setdefault(src.focus.page, []).append(i)
            for src_page, ids in by_source.items():
                lines.append(f'  {key[src_page]} {arrow}|{", ".join(dict.fromkeys(ids))}| {key[f.page]}')
        lines.append('```')
        return ('\n'.join(lines) + '\n\n<sub>An arrow is labelled with the breakthroughs that open the focus; dotted arrows '
                'are one of several ways in. Seafaring is also open from the start to coastal and river civilisations, and '
                'Warfare to any civilisation drawn into conflict.</sub>')

    # Endgame: §4
    def build_endgame_pages(self):
        s4 = self.numbered('4')
        elemental = s4.take(r'^FTL in Elemental Worlds')
        victories = s4.take(r'^How the Victories Are Built')
        promote_leadins(s4)
        promote_leadins(elemental)
        promote_leadins(victories)
        p = self.page('FTL-Endgame', self.crumb('Design document §4'))
        self.emit(p, s4, 2, with_heading=False)
        p.lazy(lambda: '*Section 4 continues on ' + self.link('FTL-Endgame', 'FTL in Elemental Worlds', 'FTL-in-Elemental-Worlds')
               + ' and ' + self.link('FTL-Endgame', 'How the Victories Are Built', 'Victories') + '. The decisions behind it are '
               'summarised in `design/notes/ftl_decisions_digest.md` in the repository.*')
        p = self.page('FTL-in-Elemental-Worlds', self.crumb('Design document §4', ('FTL-Endgame', 'FTL Endgame')))
        self.emit(p, elemental, 2, with_heading=False)
        p = self.page('Victories', self.crumb('Design document §4 — How the Victories Are Built', ('FTL-Endgame', 'FTL Endgame')))
        self.emit(p, victories, 2, with_heading=False)

    # World Truths: §5
    def build_truth_pages(self):
        s5 = self.numbered('5')
        foundational = s5.take(r'^Foundational Questions')
        examples = s5.take(r'^Worked Examples')
        promote_leadins(s5)
        promote_leadins(foundational)
        promote_leadins(examples)
        p = self.page('World-Truths', self.crumb('Design document §5'))
        self.used.add(id(s5))
        p.md(s5.body)
        s5.body = []
        for c in s5.children:
            self.emit(p, c, 2)
        p.lazy(lambda: '*Section 5 continues on ' + self.link('World-Truths', 'Foundational Questions', 'Foundational-Questions')
               + ' and ' + self.link('World-Truths', 'Worked Example Worlds', 'Worked-Example-Worlds') + '.*')
        p = self.page('Foundational-Questions', self.crumb('Design document §5', ('World-Truths', 'World Truths')))
        self.emit(p, foundational, 2, with_heading=False)
        p = self.page('Worked-Example-Worlds', self.crumb('Design document §5 — Worked Examples: The First Worlds', ('World-Truths', 'World Truths')))
        self.emit(p, examples, 2, with_heading=False)

    # Balance, Unciv mapping, statistics: §6–§8
    def build_reference_pages(self):
        s6 = self.numbered('6')
        promote_leadins(s6)
        p = self.page('Game-Balance-Rules', self.crumb('Design document §6'))
        self.used.add(id(s6))
        for c in s6.children:
            self.emit(p, c, 2)
            if re.match(r'^Dual-Path Discovery', c.title):
                p.lazy(self.dual_path_table)
        s7 = self.numbered('7')
        grounding = s7.take(r'^7\.0\b')
        promote_leadins(grounding)
        promote_leadins(s7)
        p = self.page('Mechanical-Grounding', self.crumb('Design document §7.0'))
        self.emit(p, grounding, 2, with_heading=False)
        p = self.page('Base-Game-Object-Assignments', self.crumb('Design document §7'))
        self.used.add(id(s7))
        p.md(s7.body)
        for c in s7.children:
            self.emit(p, c, 2)
        s8 = self.numbered('8')
        self.summaries = {}
        kept = []
        for line in s8.body:
            m = re.match(r'^\*Version (\d+\.\d+) — (.*)\*\s*$', line)
            if m:
                self.summaries[m.group(1)] = m.group(2)
            else:
                kept.append(line)
        s8.body = kept
        promote_leadins(s8)
        p = self.page('Summary-Statistics', self.crumb('Design document §8'))
        self.emit(p, s8, 2, with_heading=False)
        p.h(2, 'Counted from the focus tables')
        p.lazy(self.computed_counts)

    def dual_path_table(self) -> str:
        here = 'Game-Balance-Rules'
        rows = {}
        for f in self.tree.foci:
            for m in re.finditer(r'\(([A-Z][A-Z0-9-]*), from ([^)]+)\)', f.also):
                b = self.tree.by_id.get(m.group(1))
                if b:
                    rows.setdefault(b.id, (b, []))[1].append(f)
        lines = ['Every dual path, as recorded on the focus pages:', '',
                 '| Breakthrough | Home focus | Also reachable through |', '|---|---|---|']
        for b, others in sorted(rows.values(), key=lambda r: r[0].id):
            lines.append(f'| {self.bt_link(here, b, f"{b.id} {b.name}")} | {self.link(here, b.focus.name, b.focus.page)} | '
                         + ', '.join(self.link(here, o.name, o.page) for o in others) + ' |')
        return '\n'.join(lines)

    def computed_counts(self) -> str:
        bts = list(self.tree.by_id.values())
        c = collections.Counter((b.era, b.tier) for b in bts)
        lines = ['<sub>Generated from the breakthrough tables when this wiki was built; the figures above are the '
                 'document\'s own.</sub>', '',
                 f'{len(self.tree.foci)} foci, {len(bts)} breakthroughs.', '',
                 '| Era | ' + ' | '.join(TIERS) + ' | Total |', '|---|' + '---|' * (len(TIERS) + 1)]
        for e in ERAS:
            lines.append(f'| {e} | ' + ' | '.join(str(c[(e, t)]) for t in TIERS) + f' | {sum(c[(e, t)] for t in TIERS)} |')
        totals = collections.Counter(b.tier for b in bts)
        lines.append('| **Total** | ' + ' | '.join(f'**{totals[t]}**' for t in TIERS) + f' | **{len(bts)}** |')
        return '\n'.join(lines)

    # Changelog
    def build_changelog_pages(self):
        entries, extra = [], []
        for c in self.changelog.children:
            m = re.match(r'v(\d+)\.(\d+)\b', c.title)
            if m:
                entries.append(((int(m.group(1)), int(m.group(2))), c))
            else:
                extra.append(c)
        known = {f'{a}.{b}' for (a, b), _ in entries}
        for v in self.summaries:
            if v not in known:
                a, b = map(int, v.split('.'))
                entries.append(((a, b), Section(f'v{v}', 3, [], [])))
        entries.sort(key=lambda e: e[0], reverse=True)
        buckets = collections.OrderedDict()
        for (a, b), sec in entries:
            buckets.setdefault(f'Changelog-v{a}-{b // 10 * 10}s', []).append(((a, b), sec))
        oldest = next(reversed(buckets))
        hub = self.page('Changelog', self.crumb('Design document — Changelog'))
        self.used.add(id(self.changelog))
        hub.md([f'*{self.changelog.title}.* Newest first. Each entry keeps the one-paragraph summary the document records '
                'for it, where there is one, above the full notes.'])
        for name, items in buckets.items():
            first, last = items[0][0], items[-1][0]
            label = f'v{first[0]}.{first[1]}' + ('' if first == last else f' – v{last[0]}.{last[1]}')
            hub.h(2, label)
            hub.lazy(lambda name=name, items=items: '\n'.join(
                f'- {self.link("Changelog", plain_text(sec.title), name, github_slug(sec.title))}' for _, sec in items))
            p = self.page(name, self.crumb('Design document — Changelog', ('Changelog', 'Changelog')))
            p.md(['*Breakthrough IDs link to the breakthrough that holds the ID today. A few early entries predate a '
                  'renumbering or a merge, so an ID there may since have passed to another breakthrough.*'])
            for (a, b), sec in items:
                p.h(2, sec.title)
                summary = self.summaries.get(f'{a}.{b}')
                if summary:
                    p.md([f'> **Summary:** {summary}'])
                self.emit(p, sec, 3, with_heading=False)
            if name == oldest:
                for sec in extra:
                    self.emit(p, sec, 2)

    # Generated indexes
    def build_index_pages(self):
        p = self.page('Breakthrough-Index', self.crumb('Generated index'))
        p.lazy(self.alphabetical_index)
        p = self.page('Breakthroughs-by-Era', self.crumb('Generated index'))
        for e in ERAS:
            p.h(2, e)
            p.lazy(lambda e=e: self.listing('Breakthroughs-by-Era', [b for f in self.tree.foci for b in f.rows if b.era == e],
                                             ('Focus', 'Tier')))
        p = self.page('Breakthroughs-by-Tier', self.crumb('Generated index'))
        for t in TIERS:
            p.h(2, t)
            p.lazy(lambda t=t: self.listing('Breakthroughs-by-Tier', sorted(
                (b for f in self.tree.foci for b in f.rows if b.tier == t), key=lambda b: ERAS.index(b.era)),
                ('Focus', 'Era') + (('Prerequisites',) if t == 'UNIQUE' else ())))
        p = self.page('New-Objects', self.crumb('Generated index'))
        p.lazy(self.new_objects)

    def listing(self, here: str, bts: list[Breakthrough], columns: tuple) -> str:
        head = '| ID | Breakthrough | ' + ' | '.join(columns) + ' |'
        rows = [f'{len(bts)} breakthroughs.', '', head, '|---|---|' + '---|' * len(columns)]
        for b in bts:
            cells = {'Focus': self.link(here, b.focus.name, b.focus.page), 'Tier': b.tier, 'Era': b.era,
                     'Prerequisites': self.inline(b.prereq, here)}
            rows.append(f'| {self.bt_link(here, b)} | {b.name} | ' + ' | '.join(cells[c] for c in columns) + ' |')
        return '\n'.join(rows)

    def alphabetical_index(self) -> str:
        here = 'Breakthrough-Index'
        bts = sorted(self.tree.by_id.values(), key=lambda b: (plain_text(b.name).lower(), b.id))
        by_letter = collections.OrderedDict()
        for b in bts:
            letter = plain_text(b.name)[0].upper()
            by_letter.setdefault(letter if letter.isalpha() else '#', []).append(b)
        out = [' · '.join(self.link(here, L, here, github_slug(L)) for L in by_letter)]
        for letter, items in by_letter.items():
            out.append(f'## {letter}')
            rows = ['| Breakthrough | ID | Focus | Tier | Era |', '|---|---|---|---|---|']
            for b in items:
                rows.append(f'| {self.bt_link(here, b, b.name)} | {b.id} | {self.link(here, b.focus.name, b.focus.page)} | '
                            f'{b.tier} | {b.era} |')
            out.append('\n'.join(rows))
        return '\n\n'.join(out)

    @staticmethod
    def object_kind(name: str, before: str, after: str, previous: str | None) -> str:
        """What kind of object a new (ⁿ) object is, read from its specification and the words around it."""
        s = after.lstrip()
        if s.startswith('[the same') and previous:
            return previous
        if re.search(r'promotion⟩\s*\($', before):
            return 'Promotion'
        if re.match(r'\s*—\s*a perpetual process', after):
            return 'Process'
        if re.match(r'\s*—\s*a new (?:\*?stockpiled\*?|luxury|strategic) resource', after):
            return 'Resource'
        if name.endswith(' Lode') or name.startswith(('Turning of', 'the Five Turnings')):
            return 'Improvement'
        spec = s[1:].lstrip() if s[:1] in '[(' else ''
        low = spec.lower()
        if not spec:
            word = re.match(r'\s*([a-z][a-z -]{2,30}?)\b(?:[\s,.;)]|$)', after)
            following = word.group(1).strip() if word else ''
            for kind in ('promotion', 'event', 'improvement', 'resource', 'unit', 'building', 'wonder', 'specialist'):
                if following.startswith(kind) or following.endswith(kind):
                    return kind.capitalize()
            return 'Other'
        if low.startswith('unit'):
            return 'Unit'
        if 'national wonder' in low[:40]:
            return 'National wonder'
        if 'world wonder' in low[:30]:
            return 'World wonder'
        if low.startswith('improvement') or 'terrainscanbebuilton' in low[:60]:
            return 'Improvement'
        if low.startswith('replaces'):
            return 'Building (replacement)'
        if re.match(r'\d+(/\d+)?\b', spec) or low.startswith(('a grid plant', 'building', '⟨costs')):
            return 'Building'
        for kind, label in (('resource', 'Resource'), ('specialist', 'Specialist'), ('great person', 'Great Person')):
            if kind in low[:40]:
                return label
        if re.match(r'(forest|desert|grassland|tundra|hill|mountain|coast|marsh|plains)', low):
            return 'Improvement'
        return 'Other'

    def new_objects(self) -> str:
        here = 'New-Objects'
        found = []
        for f in self.tree.foci:
            for b in f.rows:
                previous = None
                for m in re.finditer(r'\*\*([^*]+?)\*\*ⁿ', b.unlocks):
                    previous = self.object_kind(m.group(1), b.unlocks[max(0, m.start() - 60):m.start()],
                                                b.unlocks[m.end():m.end() + 80], previous)
                    found.append((previous, m.group(1), b))
        kinds = ['Building', 'Building (replacement)', 'National wonder', 'World wonder', 'Unit', 'Improvement',
                 'Promotion', 'Resource', 'Process', 'Specialist', 'Great Person', 'Event', 'Other']
        out = [f'Every new object the design declares (marked ⁿ in the Unlocks text: {len(found)} in all), with the '
               'breakthrough that grants it. The full specification is in the breakthrough\'s entry. '
               '"Replacement" buildings take a canonical building\'s place for the civilisation that holds the breakthrough.']
        for kind in kinds + sorted({k for k, _, _ in found} - set(kinds)):
            items = sorted((x for x in found if x[0] == kind), key=lambda x: x[1].lower())
            if not items:
                continue
            out.append(f'## {kind}')
            rows = ['| Object | Granted by | Focus | Tier | Era |', '|---|---|---|---|---|']
            for _, name, b in items:
                rows.append(f'| {name} | {self.bt_link(here, b, f"{b.id} {b.name}")} | {self.link(here, b.focus.name, b.focus.page)} | '
                            f'{b.tier} | {b.era} |')
            out.append('\n'.join(rows))
        return '\n\n'.join(out)

    # Home, sidebar, footer
    def build_home(self):
        p = self.page('Home', None)
        p.lazy(self.home_body)

    def home_body(self) -> str:
        here = 'Home'
        core = self.numbered('1').child(r'^1\.1\b')
        concept = ' '.join(l.strip() for l in core.body if l.strip())
        link = lambda name, text=None: self.link(here, text or name.replace('-', ' '), name)
        bts = list(self.tree.by_id.values())
        out = [f'**Uncharted Horizons** is a fork of [Unciv](https://github.com/yairm210/Unciv) that replaces the '
               f'technology tree with a research system built on discovery. This wiki is the complete tech-tree design '
               f'document, **{self.version}**: {len(self.tree.foci)} focus areas and {len(bts)} breakthroughs.',
               '> ' + self.inline(concept, here)]
        out.append('## Start here')
        steps = ['Discovery-Mechanics', 'Breakthrough-Tiers', 'Discovery-States', 'Grand-Endeavours', 'Competing-Solutions',
                 'Knowledge-Diffusion', 'Environmental-Modifiers', 'Eras', 'Focus-Areas']
        out.append('\n'.join(f'{i}. **{link(n)}** — {PAGE_BLURBS[n]}' for i, n in enumerate(steps, 1)))
        out.append('## Endgame and world variation')
        out.append('\n'.join(f'- **{link(n)}** — {PAGE_BLURBS[n]}' for n in
                             ['FTL-Endgame', 'FTL-in-Elemental-Worlds', 'Victories', 'World-Truths', 'Foundational-Questions',
                              'Worked-Example-Worlds', 'Game-Balance-Rules']))
        out.append('## Focus areas')
        rows = ['| | Focus | Breakthroughs | Eras |', '|---|---|---|---|']
        for f in self.tree.foci:
            rows.append(f'| {f.emoji} | {link(f.page, f.name)} | {len(f.rows)} | {self.era_span(f.rows)} |')
        out.append('\n'.join(rows))
        out.append('## Reference')
        out.append('\n'.join(f'- **{link(n)}** — {PAGE_BLURBS[n]}' for n in
                             ['Mechanical-Grounding', 'Base-Game-Object-Assignments', 'Breakthrough-Index', 'Breakthroughs-by-Era',
                              'Breakthroughs-by-Tier', 'New-Objects', 'Summary-Statistics', 'Changelog']))
        out.append('## About this wiki')
        out.append(f'Every page is generated from [`{SOURCE_PATH_IN_REPO}`](../blob/master/{SOURCE_PATH_IN_REPO}) by '
                   f'[`design/wiki/build_wiki.py`](../blob/master/design/wiki/build_wiki.py), so edit the document rather than '
                   'the wiki: a hand edit to a generated page is overwritten the next time the wiki is published. Pages you '
                   'add yourself are left alone.\n\n'
                   'Breakthrough IDs link to their entries (hover over one for its name, tier and era); `§` references link '
                   'to the section they cite; each focus page lists what its breakthroughs build on and lead to, and draws '
                   'its prerequisite map.')
        return '\n\n'.join(out)

    def sidebar(self) -> str:
        link = lambda name, text=None: f'[{text or name.replace("-", " ")}]({name})'
        groups = collections.OrderedDict((k, []) for k in ['Start'] + ERAS)
        for f in self.tree.foci:
            groups[self.tree.focus_era(f)].append(f)
        lines = [f'**{link("Home")}**', '', '**Rules**', '']
        lines += [f'- {link(n)}' for n in ['Discovery-Mechanics', 'Breakthrough-Tiers', 'Competing-Solutions',
                                           'Knowledge-Diffusion', 'Environmental-Modifiers', 'Discovery-States',
                                           'Grand-Endeavours', 'Eras']]
        lines += ['', f'**{link("Focus-Areas", "Focus areas")}**', '']
        for era, foci in groups.items():
            if foci:
                label = 'From the start' if era == 'Start' else f'Opening in the {era} era'
                lines.append(f'- *{label}:* ' + ' · '.join(link(f.page, f.name) for f in foci))
        lines += ['', '**Endgame and worlds**', '']
        lines += [f'- {link(n)}' for n in ['FTL-Endgame', 'FTL-in-Elemental-Worlds', 'Victories', 'World-Truths',
                                           'Foundational-Questions', 'Worked-Example-Worlds', 'Game-Balance-Rules']]
        lines += ['', '**Reference**', '']
        lines += [f'- {link(n)}' for n in ['Mechanical-Grounding', 'Base-Game-Object-Assignments', 'Breakthrough-Index',
                                           'Breakthroughs-by-Era', 'Breakthroughs-by-Tier', 'New-Objects',
                                           'Summary-Statistics', 'Changelog']]
        for line in lines:
            for target in re.findall(r'\]\(([^)#]+)\)', line):
                self.links.append(('_Sidebar', target, None))
        return '\n'.join(lines) + '\n'

    def footer(self) -> str:
        return (f'<sub>Generated from `{SOURCE_PATH_IN_REPO}` ({self.version}) — edit the document, not the wiki. '
                '[Home](Home) · [Breakthrough index](Breakthrough-Index) · [Changelog](Changelog)</sub>\n')

    # -- validation ----------------------------------------------------------------------------------

    def validate(self, files: dict[str, str]):
        errors = []
        anchors = {name[:-3]: set(page_anchors(text)) for name, text in files.items()}
        for here, page, anchor in self.links:
            if page not in anchors:
                errors.append(f'{here}: link to missing page {page}')
            elif anchor and anchor not in anchors[page]:
                errors.append(f'{here}: link to missing anchor {page}#{anchor}')
        for name, text in files.items():
            if '[[' in html.unescape(text):
                errors.append(f'{name}: contains "[[", which the wiki would read as a link to a page')
            stripped = re.sub(r'```.*?```', '', text, flags=re.S)
            stripped = re.sub(r'`[^`\n]*`', '', stripped)
            for tag in re.findall(r'<(/?[A-Za-z][A-Za-z0-9-]*)', stripped):
                if tag.lstrip('/') not in ('sub', 'code', 'br', 'details', 'summary'):
                    errors.append(f'{name}: unexpected HTML tag <{tag}>')
            counts = collections.Counter(page_anchors(text))
            dupes = [a for a, n in counts.items() if n > 1]
            if dupes:
                self.warnings.append(f'{name}: repeated headings {dupes[:5]}')
        bt_pages = collections.Counter()
        for b in self.tree.by_id.values():
            if b.anchor not in anchors[b.focus.page]:
                errors.append(f'{b.id}: no entry on {b.focus.page}')
            bt_pages[b.id] += 1
        if errors:
            raise BuildError('the wiki has broken links:\n  ' + '\n  '.join(errors[:40])
                             + (f'\n  … and {len(errors) - 40} more' if len(errors) > 40 else ''))


# ---------------------------------------------------------------------------------------------------

def write_pages(files: dict[str, str], out: Path):
    out.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (out / name).write_text(text, encoding='utf-8')


def version_key(version: str) -> tuple[int, ...]:
    return tuple(int(n) for n in re.findall(r'\d+', version))


def sync_pages(files: dict[str, str], wiki: Path, version: str) -> str:
    """Write the pages into a wiki checkout, removing pages generated last time but no longer produced.
    Refuses to replace the wiki with an older design version (a stale branch must not undo a newer one)."""
    if not (wiki / '.git').exists():
        raise BuildError(f'{wiki} is not a checkout of the wiki repository')
    manifest = wiki / MANIFEST
    lines = manifest.read_text(encoding='utf-8').split('\n') if manifest.exists() else []
    published = next((l.split()[-1] for l in lines if l.startswith('# version')), '')
    if published and version_key(version) < version_key(published):
        return f'not synced: the wiki shows {published}, newer than this document ({version})'
    previous = {l for l in lines if l and not l.startswith('#')}
    removed = 0
    for name in sorted(previous - set(files)):
        if (wiki / name).exists():
            (wiki / name).unlink()
            removed += 1
    write_pages(files, wiki)
    manifest.write_text(f'# version {version}\n' + '\n'.join(sorted(files)) + '\n', encoding='utf-8')
    return f'synced into {wiki}: {len(files)} pages written, {removed} stale pages removed'


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--source', type=Path, default=DEFAULT_SOURCE, help='the design document (default: %(default)s)')
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument('--out', type=Path, help='write the pages into this folder')
    group.add_argument('--sync-into', type=Path, help='update this checkout of the wiki repository')
    group.add_argument('--check', action='store_true', help='build and validate only')
    args = ap.parse_args(argv)
    try:
        wiki = Wiki(args.source.read_text(encoding='utf-8'))
        files = wiki.build()
    except BuildError as e:
        print(f'error: {e}', file=sys.stderr)
        return 1
    for w in wiki.warnings:
        print(f'warning: {w}', file=sys.stderr)
    print(f'{len(files)} pages, {len(wiki.links)} internal links checked, {len(wiki.tree.by_id)} breakthroughs '
          f'in {len(wiki.tree.foci)} foci ({wiki.version})')
    if args.out:
        write_pages(files, args.out)
        print(f'written to {args.out}')
    elif args.sync_into:
        print(sync_pages(files, args.sync_into, wiki.version))
    return 0


if __name__ == '__main__':
    sys.exit(main())
