"""Convert a book's Markdown manuscripts into site pages.

Usage:
    python scripts/publish_book.py --book BOOK [--src DIR] [--write]

BOOK is the folder name under content/books/. Its opening page (index.html) must
already exist: its <title> gives the book's short name, and its page shell is used
for every chapter. Default source is publication-inbox/BOOK. Without --write it
only reports which pages would change. Chapters not present in the source keep their published
text; they are still used for titles, previous/next links and the opening-page
contents. A file named NN-00-... is chapter NN's opening page and NN-0x-... its
sub-chapters; any chapter may have them. A 00-... file other than 00-index-...
(the author's status file) is an introduction, published before Chapter 1. Held working notes at the foot of a
chapter are never published.
"""
import argparse
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = B = None  # set from --book in main()
HELD = ("## Held", "*Held (working note", "*Working note, not part of the narrative text")
# This marker begins a note that is one block: it ends at the next blank line,
# and text after it is published. The others run to the next "## " heading.
NOTE = "*Working note, not part of the narrative text"


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))


def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)


def slug(t):
    return re.sub(r"[^\w]+", "-", t.lower().replace("&", "")).strip("-")


def route(name):
    m = re.match(r"(\d\d)(?:-(\d\d))?-", name)
    if not m:
        raise ValueError(f"Unrecognised file name: {name}")
    a, b = m.groups()
    # NN-00 is a chapter's opening page; NN-0x are its sub-chapters.
    if b is None or b == "00":
        return "chapter-" + a
    return f"chapter-{a}-{int(b)}"


def parent(r):
    """The chapter a sub-chapter route belongs to, or None for a chapter."""
    parts = r.split("-")
    return "-".join(parts[:2]) if len(parts) > 2 else None


def route_key(r):
    parts = r.split("-")[1:]
    return tuple(int(p) for p in parts) if len(parts) > 1 else (int(parts[0]), 0)


VERSIONED = re.compile(r"-v(\d+)-(\d{8})\.md$")


def pick_sources(files):
    """One source file per page.

    A chapter file can be renamed between versions (for example 11-patterns-of-the-inner-life-v30
    becoming 11-other-sides-of-the-inner-being-v31), so the inbox can hold two files for the same
    page. The page number decides the page; the file with the later date, then the higher version,
    is the current one. Returns (chosen files, [(superseded name, chosen name)], {page: names}
    for clashes that cannot be decided: a file without -vN-YYYYMMDD, or two with the same date
    and version).
    """
    routes = {}
    for p in sorted(files, key=lambda p: p.name):
        routes.setdefault(route(p.name), []).append(p)
    chosen, superseded, undecided = [], [], {}
    for r, ps in routes.items():
        if len(ps) == 1:
            chosen.append(ps[0])
            continue
        keys = [VERSIONED.search(p.name) for p in ps]
        if not all(keys):
            undecided[r] = [p.name for p in ps]
            continue
        ranked = sorted(zip(ps, keys), key=lambda pk: (pk[1].group(2), int(pk[1].group(1))), reverse=True)
        top, second = ranked[0][1], ranked[1][1]
        if (top.group(2), int(top.group(1))) == (second.group(2), int(second.group(1))):
            undecided[r] = [p.name for p in ps]
            continue
        chosen.append(ranked[0][0])
        superseded += [(p.name, ranked[0][0].name) for p, _ in ranked[1:]]
    return chosen, superseded, undecided


def parse(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    title = lines[0][2:].strip()
    out, h2s, seen = [], [], {}
    para, lst, ltype, quote, table = [], [], None, [], []
    pad = " " * 10

    def flush():
        nonlocal para, lst, ltype, quote, table
        if para:
            out.append(f"{pad}<p>{inline(' '.join(para))}</p>")
            para = []
        if lst:
            def li(text, sub):
                if not sub:
                    return f"<li>{inline(text)}</li>"
                tag = sub[0][0]
                return (f"<li>{inline(text)}<{tag}>"
                        + "".join(f"<li>{inline(x)}</li>" for _, x in sub) + f"</{tag}></li>")
            out.append(f"{pad}<{ltype}>" + "".join(li(t, s) for t, s in lst) + f"</{ltype}>")
            lst, ltype = [], None
        if quote:
            out.append(f"{pad}<blockquote><p>{inline(' '.join(quote))}</p></blockquote>")
            quote = []
        if table:
            # The first row is the header; a |---| row under it only separates.
            rows = [[c.strip() for c in r.strip().strip("|").split("|")]
                    for r in table if not re.fullmatch(r"[\s|:-]+", r)]
            out.append(f'{pad}<div class="table-wrap"><table>\n'
                       + "<tr>" + "".join(f"<th>{inline(c)}</th>" for c in rows[0]) + "</tr>\n"
                       + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>\n"
                                 for r in rows[1:])
                       + "</table></div>")
            table = []

    held = None  # "section": skip to the next "## " heading; "block": to a blank line
    for ln in lines[1:]:
        # Notes are never published. A Held section or note runs to the next "## "
        # heading (or the end); a working note is its own block, so the text after
        # it, in the same section, is published.
        if held != "section" and ln.startswith(HELD):
            flush()
            held = "block" if ln.startswith(NOTE) else "section"
            continue
        if held:
            if re.match(r"^## ", ln) or (held == "block" and not ln.strip()):
                held = None
            else:
                continue
        if re.match(r"^\s*(---|\*\*\*)\s*$", ln):
            flush()
            out.append(f"{pad}<hr>")
            continue
        if not ln.strip():
            flush()
            continue
        if ln.lstrip().startswith("|"):
            if not table:
                flush()
            table.append(ln)
            continue
        if table:
            flush()
        m = re.match(r"^(#{2,3}) (.+)", ln)
        if m:
            flush()
            text = m.group(2).strip()
            level = len(m.group(1))
            sid = slug(text)
            n = seen.get(sid, 0)
            seen[sid] = n + 1
            if n:
                sid = f"{sid}-{n + 1}"
            if level == 2:
                h2s.append((sid, text))
            out.append(f'{pad}<h{level} id="{sid}">{inline(text)}</h{level}>')
            continue
        # One level of nesting: an indented item belongs to the item above it.
        m = re.match(r"^\s+(?:([-*])|\d+\.) (.+)", ln)
        if m and lst:
            lst[-1][1].append(("ul" if m.group(1) else "ol", m.group(2)))
            continue
        m = re.match(r"^[-*] (.+)", ln)
        if m:
            if para or quote or ltype == "ol":
                flush()
            ltype = "ul"
            lst.append((m.group(1), []))
            continue
        m = re.match(r"^\d+\. (.+)", ln)
        if m:
            if para or quote or ltype == "ul":
                flush()
            ltype = "ol"
            lst.append((m.group(1), []))
            continue
        m = re.match(r"^> ?(.*)", ln)
        if m:
            if para or lst:
                flush()
            quote.append(m.group(1))
            continue
        if lst:
            flush()
        para.append(ln.strip())
    flush()
    # A trailing rule only separated the working note from the text.
    if out and out[-1].endswith("<hr>"):
        out.pop()
    return title, out, h2s


def published_title(r):
    text = (OUT / r / "index.html").read_text(encoding="utf-8")
    m = re.search(r'<h1 class="article-title">(.*?)</h1>', text)
    return html.unescape(re.sub(r"</?(?:em|strong)>", "", m.group(1)))


def main():
    global OUT, B
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True, help="folder name under content/books/")
    ap.add_argument("--src", help="source folder (default publication-inbox/BOOK)")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    OUT = ROOT / "content" / "books" / args.book
    B = f"/books/{args.book}/"
    idx = OUT / "index.html"
    if not idx.exists():
        sys.exit(f"No opening page at {idx.relative_to(ROOT)}; create it first.")
    src = pathlib.Path(args.src or ROOT / "publication-inbox" / args.book)
    if not src.is_dir():
        sys.exit(f"No source folder at {src}")
    # 00-index-... is the author's status file and is never published; any other
    # 00-... file (an introduction) becomes page chapter-00, before Chapter 1.
    files = [p for p in src.glob("*.md") if not p.name.startswith("00-index")]
    files, superseded, undecided = pick_sources(files)
    if undecided:
        sys.exit("Source files share a page and the newer one cannot be told from the names; "
                 "remove the superseded one:\n"
                 + "\n".join(f"  {r}: {', '.join(n)}" for r, n in undecided.items()))
    for old, new in superseded:
        print(f"SUPERSEDED {old} (page {route(new)} is built from {new})")
    parsed = {route(p.name): parse(p) for p in files}
    titles = {d.name: published_title(d.name) for d in OUT.glob("chapter-*") if (d / "index.html").exists()}
    for r, (t, _, _) in parsed.items():
        titles[r] = t
    order = sorted(titles, key=route_key)

    # The opening page supplies the page shell and the book's short name.
    tmpl = idx.read_text(encoding="utf-8").replace("\r\n", "\n")
    name = html.unescape(re.search(r"<title>(.*?) - Learning4Comfort</title>", tmpl).group(1))
    head = tmpl[: tmpl.index("<main")]
    foot = tmpl[tmpl.index("    </main>"):]
    changed = []

    def put(target, content):
        old = target.read_text(encoding="utf-8") if target.exists() else None
        if old is not None and old.replace("\r\n", "\n") == content:
            return
        if args.verbose and old:
            import difflib; print("\n".join(list(difflib.unified_diff(old.splitlines(), content.splitlines(), lineterm="", n=0))[:10]))
        changed.append(("NEW " if old is None else "CHANGED ") + str(target.relative_to(OUT)))
        if args.write:
            target.parent.mkdir(exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="\n")

    def link(r, cls, label):
        return f'<a class="pager-{cls}" href="{B}{r}/"><span>{label}</span>{inline(titles[r])}</a>'

    for i, r in enumerate(order):
        prev = link(order[i - 1], "prev", "Previous") if i else "<span></span>"
        nxt = link(order[i + 1], "next", "Next") if i + 1 < len(order) else "<span></span>"
        pager = f'        <nav class="pager" aria-label="Chapter navigation">{prev}{nxt}</nav>\n'
        target = OUT / r / "index.html"
        if r in parsed:
            title, body, h2s = parsed[r]
            toc = "        \n"
            if h2s:
                toc = ('        <nav class="article-contents" aria-labelledby="contents-title">\n'
                       '<h2 id="contents-title">In this chapter</h2>\n<ol>\n'
                       + "\n".join(f'<li><a href="#{s}">{inline(t)}</a></li>' for s, t in h2s)
                       + "\n</ol>\n</nav>\n")
            hp = re.sub(r'(<meta name="description" content=").*?(">)',
                        lambda m: m.group(1) + esc(title) + m.group(2), head)
            hp = re.sub(r"<title>.*?</title>",
                        lambda m: f"<title>{esc(title)} - {esc(name)} - Learning4Comfort</title>", hp)
            page = (hp + '<main class="reading-page">\n      <article class="book-article">\n'
                    f'        <p class="crumb"><a href="{B}">{esc(name)}</a></p>\n'
                    f'        <header class="article-heading"><h1 class="article-title">{inline(title)}</h1></header>\n'
                    + toc + '        <div class="article-prose">\n' + "\n".join(body) + "\n        </div>\n"
                    + pager + "      </article>\n" + foot)
        else:
            old = target.read_text(encoding="utf-8")
            page = re.sub(r'        <nav class="pager" aria-label="Chapter navigation">.*?</nav>\n',
                          lambda m: pager, old, count=1, flags=re.S)
        put(target, page)

    # Opening-page contents
    items = []
    for r in order:
        if parent(r):
            continue
        li = f'<li><a href="{B}{r}/">{inline(titles[r])}</a>'
        subs = [s for s in order if parent(s) == r]
        if subs:
            li += ('\n<ol class="sub-contents">\n'
                   + "\n".join(f'<li><a href="{B}{s}/">{inline(titles[s])}</a></li>' for s in subs)
                   + "\n</ol>\n")
        items.append(li + "</li>")
    new = re.sub(r'(<ul class="contents-plain">\n).*?(\n          </ul>)',
                 lambda m: m.group(1) + "\n".join(items) + m.group(2), tmpl, count=1, flags=re.S)
    start = (f'<nav class="pager" aria-label="Start reading"><span></span>'
             f'<a class="pager-next" href="{B}{order[0]}/"><span>Start reading</span>'
             f'{inline(titles[order[0]])}</a></nav>')
    new = re.sub(r'<nav class="pager" aria-label="Start reading">.*?</nav>',
                 lambda m: start, new, count=1)
    put(idx, new)

    print("\n".join(changed) or "No page changes.")
    print(f"{len(changed)} page(s) {'written' if args.write else 'would change'}; "
          f"{len(parsed)} source chapter(s).")


if __name__ == "__main__":
    main()
