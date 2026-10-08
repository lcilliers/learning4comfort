import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from build_book_search_indexes import BookPageParser, build_indexes  # noqa: E402


class BookSearchIndexTests(unittest.TestCase):
    def test_parser_extracts_section_text_and_decodes_entities(self) -> None:
        parser = BookPageParser()
        parser.feed(
            """\
            <h1 class="article-title">A Sample Book</h1>
            <div class="article-prose">
              <p>Opening &amp; introduction.</p>
              <h2 id="first-section">First section</h2>
              <p>Some <em>searchable</em> text.</p>
            </div>
            """
        )

        self.assertEqual(
            parser.result("fallback"),
            {
                "title": "A Sample Book",
                "sections": [
                    {"heading": "", "id": "", "text": "Opening & introduction."},
                    {
                        "heading": "First section",
                        "id": "first-section",
                        "text": "First section Some searchable text.",
                    },
                ],
            },
        )

    def test_builds_book_scoped_indexes_and_adds_search_controls(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            site = Path(temporary_directory)
            opening = site / "books" / "sample-book" / "index.html"
            chapter = site / "books" / "sample-book" / "chapter-01" / "index.html"
            second_opening = site / "books" / "another-book" / "index.html"
            second_chapter = site / "books" / "another-book" / "chapter-01" / "index.html"
            opening.parent.mkdir(parents=True)
            chapter.parent.mkdir(parents=True)
            second_opening.parent.mkdir(parents=True)
            second_chapter.parent.mkdir(parents=True)
            opening.write_text(
                """\
                <!doctype html><html><head></head><body>
                <nav aria-label="Main navigation"><a href="/">Home</a></nav>
                <article><header class="article-heading"><h1 class="article-title">Sample Book</h1></header>
                <nav class="book-contents"><a href="/books/sample-book/chapter-01/">Chapter 1</a></nav></article>
                </body></html>
                """,
                encoding="utf-8",
            )
            chapter.write_text(
                """\
                <!doctype html><html><head></head><body>
                <nav aria-label="Main navigation"><a href="/">Home</a></nav>
                <article><header class="article-heading"><h1 class="article-title">Chapter 1</h1></header>
                <div class="article-prose"><h2 id="searchable">Searchable heading</h2>
                <p>Searchable chapter text.</p></div></article>
                </body></html>
                """,
                encoding="utf-8",
            )
            second_opening.write_text(
                """\
                <!doctype html><html><head></head><body>
                <nav aria-label="Main navigation"><a href="/">Home</a></nav>
                <header class="article-heading"><h1 class="article-title">Another Book</h1></header>
                </body></html>
                """,
                encoding="utf-8",
            )
            second_chapter.write_text(
                """\
                <!doctype html><html><head></head><body>
                <nav aria-label="Main navigation"><a href="/">Home</a></nav>
                <header class="article-heading"><h1 class="article-title">Another Chapter</h1></header>
                <div class="article-prose"><p>Text from a different book.</p></div>
                </body></html>
                """,
                encoding="utf-8",
            )
            readme = opening.parent / "README.md"
            readme.write_text("# Never indexed", encoding="utf-8")

            self.assertEqual(build_indexes(site), 2)

            index = json.loads(
                (opening.parent / "search-index.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                [document["url"] for document in index["documents"]],
                ["/books/sample-book/chapter-01/"],
            )
            self.assertEqual(index["documents"][0]["title"], "Chapter 1")
            self.assertEqual(
                index["documents"][0]["sections"][0]["text"],
                "Searchable heading Searchable chapter text.",
            )
            global_index = json.loads(
                (site / "search-index.json").read_text(encoding="utf-8")
            )
            self.assertEqual(len(global_index["documents"]), 2)
            self.assertEqual(
                [document["book_title"] for document in global_index["documents"]],
                ["Another Book", "Sample Book"],
            )
            self.assertEqual(
                global_index["documents"][1]["url"],
                "/books/sample-book/chapter-01/",
            )
            for page in (opening, chapter):
                published_html = page.read_text(encoding="utf-8")
                self.assertLess(
                    published_html.index('src="/search-match.js"'),
                    published_html.index('src="/book-search.js"'),
                )
                self.assertIn('class="book-search"', published_html)
                self.assertIn('data-index-url="/books/sample-book/search-index.json"', published_html)
                self.assertIn('href="/search/">Search</a>', published_html)
                self.assertIn('src="/reading-progress.js"', published_html)

            opening_html = opening.read_text(encoding="utf-8")
            self.assertIn('class="reading-resume" data-reading-book="sample-book"', opening_html)


if __name__ == "__main__":
    unittest.main()
