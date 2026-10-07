"""Convert Inner Being manuscripts (Markdown) into site pages.

Usage:
    python scripts/publish_inner_being.py [--src DIR] [--write]

Default source is publication-inbox/the_inner_being. Without --write it only reports
which pages would change. Chapters not present in the source keep their published
text; they are still used for titles, previous/next links and the opening-page
contents. A file named NN-00-... is chapter NN's opening page and NN-0x-... its
sub-chapters; any chapter may have them. Held working notes at the foot of a
chapter are never published.
"""
import argparse
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "content" / "books" / "the_inner_being"
B = "/books/the_inner_being/"
HELD = ("## Held", "*Held (working note")


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


def parse(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    title = lines[0][2:].strip()
    out, h2s, seen = [], [], {}
    para, lst, ltype, quote = [], [], None, []
    pad = " " * 10

    def flush():
        nonlocal para, lst, ltype, quote
        if para:
            out.append(f"{pad}<p>{inline(' '.join(para))}</p>")
            para = []
        if lst:
            out.append(f"{pad}<{ltype}>" + "".join(f"<li>{inline(x)}</li>" for x in lst) + f"</{ltype}>")
            lst, ltype = [], None
        if quote:
            out.append(f"{pad}<blockquote><p>{inline(' '.join(quote))}</p></blockquote>")
            quote = []

    for ln in lines[1:]:
        if ln.startswith(HELD):
            break
        if re.match(r"^\s*(---|\*\*\*)\s*$", ln):
            flush()
            out.append(f"{pad}<hr>")
            continue
        if not ln.strip():
            flush()
            continue
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
        m = re.match(r"^[-*] (.+)", ln)
        if m:
            if para or quote or ltype == "ol":
                flush()
            ltype = "ul"
            lst.append(m.group(1))
            continue
        m = re.match(r"^\d+\. (.+)", ln)
        if m:
            if para or quote or ltype == "ul":
                flush()
            ltype = "ol"
            lst.append(m.group(1))
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(ROOT / "publication-inbox" / "the_inner_being"))
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    src = pathlib.Path(args.src)
    files = [p for p in src.glob("*.md") if not p.name.startswith("00-")]
    routes = {}
    for p in sorted(files):
        routes.setdefault(route(p.name), []).append(p.name)
    clashes = {r: n for r, n in routes.items() if len(n) > 1}
    if clashes:
        sys.exit("Source files share a page; remove the superseded one:\n"
                 + "\n".join(f"  {r}: {', '.join(n)}" for r, n in clashes.items()))
    parsed = {route(p.name): parse(p) for p in files}
    titles = {d.name: published_title(d.name) for d in OUT.glob("chapter-*") if (d / "index.html").exists()}
    for r, (t, _, _) in parsed.items():
        titles[r] = t
    order = sorted(titles, key=route_key)

    tmpl = (OUT / "chapter-10-11" / "index.html").read_text(encoding="utf-8")
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
                        lambda m: f"<title>{esc(title)} - The Inner Being - Learning4Comfort</title>", hp)
            page = (hp + '<main class="reading-page">\n      <article class="book-article">\n'
                    f'        <p class="crumb"><a href="{B}">The Inner Being</a></p>\n'
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
    idx = OUT / "index.html"
    old = idx.read_text(encoding="utf-8").replace("\r\n", "\n")
    new = re.sub(r'(<ul class="contents-plain">\n).*?(\n          </ul>)',
                 lambda m: m.group(1) + "\n".join(items) + m.group(2), old, count=1, flags=re.S)
    put(idx, new)

    print("\n".join(changed) or "No page changes.")
    print(f"{len(changed)} page(s) {'written' if args.write else 'would change'}; "
          f"{len(parsed)} source chapter(s).")


if __name__ == "__main__":
    main()
