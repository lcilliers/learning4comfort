from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from publish_book import pick_sources  # noqa: E402


def names(paths):
    return sorted(p.name for p in paths)


class PickSourcesTests(unittest.TestCase):
    def test_renamed_chapter_keeps_the_newer_file(self) -> None:
        files = [Path("11-patterns-of-the-inner-life-v29-20261012.md"),
                 Path("11-other-sides-of-the-inner-being-v31-20261012.md"),
                 Path("12-when-the-inner-being-goes-wrong-v20-20261012.md")]
        chosen, superseded, undecided = pick_sources(files)
        self.assertEqual(names(chosen), ["11-other-sides-of-the-inner-being-v31-20261012.md",
                                         "12-when-the-inner-being-goes-wrong-v20-20261012.md"])
        self.assertEqual(superseded, [("11-patterns-of-the-inner-life-v29-20261012.md",
                                       "11-other-sides-of-the-inner-being-v31-20261012.md")])
        self.assertEqual(undecided, {})

    def test_later_date_wins_over_higher_version(self) -> None:
        files = [Path("05-old-name-v9-20261001.md"), Path("05-new-name-v1-20261012.md")]
        chosen, superseded, _ = pick_sources(files)
        self.assertEqual(names(chosen), ["05-new-name-v1-20261012.md"])
        self.assertEqual(superseded[0][0], "05-old-name-v9-20261001.md")

    def test_sub_chapters_are_separate_pages(self) -> None:
        files = [Path("10-00-the-inner-being-at-work-v5-20261002.md"), Path("10-01-feeling-v20-20261012.md")]
        chosen, superseded, undecided = pick_sources(files)
        self.assertEqual(len(chosen), 2)
        self.assertEqual((superseded, undecided), ([], {}))

    def test_unversioned_clash_is_left_to_the_author(self) -> None:
        files = [Path("03-a.md"), Path("03-b-v2-20261012.md")]
        chosen, _, undecided = pick_sources(files)
        self.assertEqual(chosen, [])
        self.assertEqual(undecided, {"chapter-03": ["03-a.md", "03-b-v2-20261012.md"]})

    def test_same_date_and_version_is_left_to_the_author(self) -> None:
        files = [Path("04-a-v3-20261012.md"), Path("04-b-v3-20261012.md")]
        _, _, undecided = pick_sources(files)
        self.assertIn("chapter-04", undecided)


if __name__ == "__main__":
    unittest.main()
