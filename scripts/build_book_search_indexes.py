#!/usr/bin/env python3
"""Build one client-side search index per published book."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re


class BookPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.sections: list[dict[str, str]] = []
        self._in_article_prose = False
        self._prose_div_depth = 0
        self._in_page_title = False
        self._heading_parts: list[str] | None = None
        self._section: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = (attributes.get("class") or "").split()

        if tag == "h1" and "article-title" in classes:
            self._in_page_title = True

        if tag == "div" and "article-prose" in classes:
            self._in_article_prose = True
            self._prose_div_depth = 1
            return

        if not self._in_article_prose:
            return

        if tag == "div":
            self._prose_div_depth += 1
        elif tag in {"h2", "h3"}:
            self._section = {
                "heading": "",
                "id": attributes.get("id") or "",
                "text": "",
            }
            self.sections.append(self._section)
            self._heading_parts = []
        elif tag in {"p", "li", "blockquote"}:
            self._append_text(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag == "h1":
            self._in_page_title = False

        if not self._in_article_prose:
            return

        if tag in {"h2", "h3"} and self._heading_parts is not None:
            heading = self._clean_text(" ".join(self._heading_parts))
            if self._section is not None:
                self._section["heading"] = heading
                self._section["text"] = heading
            self._heading_parts = None
        elif tag in {"p", "li", "blockquote"}:
            self._append_text(" ")
        elif tag == "div":
            self._prose_div_depth -= 1
            if self._prose_div_depth == 0:
                self._in_article_prose = False

    def handle_data(self, data: str) -> None:
        if self._in_page_title:
            self.title_parts.append(data)
        if self._in_article_prose:
            self._append_text(data)

    def _append_text(self, text: str) -> None:
        if self._heading_parts is not None:
            self._heading_parts.append(text)
            return
        if self._section is None:
            self._section = {"heading": "", "id": "", "text": ""}
            self.sections.append(self._section)
        self._section["text"] += text

    @staticmethod
    def _clean_text(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def result(self, fallback_title: str) -> dict[str, object]:
        sections = []
        for section in self.sections:
            text = self._clean_text(section["text"])
            if text:
                sections.append({**section, "text": text})
        title = self._clean_text(" ".join(self.title_parts)) or fallback_title
        return {"title": title, "sections": sections}


def book_route(page: Path, site_root: Path) -> str:
    relative = page.parent.relative_to(site_root).as_posix()
    return f"/{relative}/"


def page_sort_key(page: Path, book_dir: Path) -> tuple[int, tuple[object, ...]]:
    relative = page.parent.relative_to(book_dir).as_posix()
    if relative == ".":
        return (0, ())

    route = relative.rsplit("/", 1)[-1]
    if route == "executive-summary":
        priority = 1
    elif route.startswith("chapter-"):
        priority = 2
    elif route.startswith("appendix-"):
        priority = 3
    elif route == "plain-retelling":
        priority = 4
    else:
        priority = 5

    parts: list[tuple[int, str | int]] = []
    for part in re.split(r"(\d+)", relative.lower()):
        parts.append((1, int(part)) if part.isdigit() else (0, part))
    return priority, tuple(parts)


def add_book_search_widget(page_html: str, book_slug: str, index_url: str) -> str:
    if 'class="book-search"' in page_html:
        return page_html

    search_script = '<script defer src="/book-search.js"></script>'
    if "</head>" not in page_html:
        raise ValueError("Book page is missing its closing head tag")
    page_html = page_html.replace("</head>", f"    {search_script}\n  </head>", 1)

    input_id = f"book-search-{book_slug}"
    widget = f"""\
        <section class="book-search" aria-labelledby="{input_id}-heading" data-index-url="{index_url}">
          <h2 id="{input_id}-heading">Search this book</h2>
          <form role="search" action="/books/{book_slug}/" method="get">
            <label for="{input_id}">Search terms</label>
            <div class="book-search-controls">
              <input id="{input_id}" name="q" type="search" autocomplete="off">
              <button type="submit">Search</button>
            </div>
          </form>
          <noscript><p>Enable JavaScript to search this book.</p></noscript>
          <div class="book-search-results" role="status" aria-live="polite" aria-atomic="true"></div>
        </section>
"""
    article_heading = re.search(r'<header class="article-heading">[\s\S]*?</header>', page_html)
    if article_heading:
        insertion_point = article_heading.end()
    else:
        article_prose = page_html.find('<div class="article-prose">')
        if article_prose < 0:
            raise ValueError("Book page has neither an article heading nor article prose")
        insertion_point = article_prose

    return page_html[:insertion_point] + "\n" + widget + page_html[insertion_point:]


def build_indexes(site_root: Path) -> int:
    books_root = site_root / "books"
    if not books_root.is_dir():
        raise FileNotFoundError(f"Published books directory not found: {books_root}")

    index_count = 0
    for book_dir in sorted(path for path in books_root.iterdir() if path.is_dir()):
        book_slug = book_dir.name
        documents = []
        pages = sorted(book_dir.rglob("*.html"), key=lambda page: page_sort_key(page, book_dir))
        for page in pages:
            source_html = page.read_text(encoding="utf-8")
            parser = BookPageParser()
            parser.feed(source_html)
            parsed = parser.result(page.parent.name.replace("-", " "))
            if parsed["sections"]:
                documents.append(
                    {
                        "title": parsed["title"],
                        "url": book_route(page, site_root),
                        "sections": parsed["sections"],
                    }
                )

            if (
                '<header class="article-heading">' in source_html
                or '<div class="article-prose">' in source_html
            ):
                index_url = f"/books/{book_slug}/search-index.json"
                page.write_text(
                    add_book_search_widget(source_html, book_slug, index_url),
                    encoding="utf-8",
                )

        if documents:
            index_path = book_dir / "search-index.json"
            index_path.write_text(
                json.dumps({"version": 1, "documents": documents}, ensure_ascii=False),
                encoding="utf-8",
            )
            index_count += 1

    return index_count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--site",
        type=Path,
        required=True,
        help="Assembled site directory containing books/",
    )
    args = parser.parse_args()
    count = build_indexes(args.site)
    print(f"Built within-book search indexes for {count} published books.")


if __name__ == "__main__":
    main()
