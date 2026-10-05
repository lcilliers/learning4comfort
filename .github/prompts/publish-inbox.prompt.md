---
description: Process new files in publication-inbox into book pages, rebuild search, archive, and publish the site
agent: agent
---

Publish whatever is waiting in `publication-inbox`. Follow the workflow in `README.md` and the rules in `SITE-DESIGN.md`. Run Python as `.venv\Scripts\python`.

Invoking this command is the author's approval to publish. Site-wide legal and privacy compliance is handled separately; do not raise it for book updates.

1. **Check the inbox.** List the files in `publication-inbox\<book>\` for every book folder. If nothing is there, say so and stop. Read each book's `content\books\<book>\README.md` and apply its rules and presentation overrides. Do not infer rules that are not written.

2. **Convert.**
   - `the_inner_being`: run `python scripts\publish_inner_being.py` for a dry run and review the list of changed pages. Then run it with `--write`. It converts the Markdown, drops the `00-index` file and any "Held" working notes, and rebuilds chapter contents, previous/next links and the opening-page contents. Chapters not in the inbox keep their published text.
   - Any other book has no converter yet. Stop and ask the author how it should be converted. Do not guess a structure.

3. **Verify.** Spot-check that new or changed pages exist, that text matches the source, that heading anchors match the contents list, and that no "Held" or working-note text was published. Run `python -m unittest discover -s tests`.

4. **Search indexes.** The deploy workflow runs `scripts\build_book_search_indexes.py` itself, so nothing is committed for search. To check locally, copy `site\` and `content\` into a temporary folder, remove the README files, run `python scripts\build_book_search_indexes.py --site <folder>`, confirm the book's `search-index.json` includes the new pages, and delete the temporary folder.

5. **Archive.** Copy each inbox file to `publication-archive\<book>\<yyyy-mm-dd>\`. Delete the inbox copy only after its SHA-256 hash matches. Never commit the inbox or archive; both are git-ignored.

6. **Track.** Add a row to `PUBLICATION-TRACKER.md` with the date, "Approved and published (update)", the book, the source and destination, the publish method, and a short note. Say which chapters are new and which changed.

7. **Publish.** Stage only the book's `content\books\<book>` folder, `PUBLICATION-TRACKER.md`, and any script changes made in this run. Leave unrelated working-tree changes alone and mention them. Commit with a clear message and the trailer `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`, then `git push`. Watch the "Deploy Learning4Comfort site" run until it succeeds, then confirm that a new or changed page on https://learning4comfort.uk returns 200.

8. **Report briefly:** what was new or changed, the commit, the deploy result, and anything left unpublished or needing the author's decision.

Stop and ask the author, rather than continuing, when a file name or format is not recognised, when a converter would change a published page in a way the source does not explain, or when a check fails.
