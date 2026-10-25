# The Practice of Prayer — book instructions

## Book-specific rules

No book-specific editorial, formatting, translation, or citation rules have been supplied yet. Do not infer any. Follow the site-wide workflow in the root `README.md`, the page guidance in `SITE-DESIGN.md`, and the source outlines in `templates/`. Ask the author when a decision not covered there is needed.

Practice in the first version (2026-10-25), following The Presence of God, for the author to confirm or change: Scripture is quoted from the ESV, with "LORD" written as "the Lord", and every quotation is checked against the ESV text. The reference works' own words are quoted as written; Scripture they cite in the King James Version is given in the ESV.

## Sources

The editable sources are Markdown files, one per chapter, named `NN-short-name-vN-YYYYMMDD.md`; `00-introduction-...` is the introduction. Each starts with a `# N. Title` line (the introduction with `# Introduction`). To update the book, edit the latest copy, raise its version and date in the file name, and place the full set in `publication-inbox/prayer/`. Pages are built with `python scripts/publish_book.py --book prayer`.

The first version was written on 2026-10-25 from the folder `\\lsuk-synrack\HomeMedia\bible_study_projects\Short_studies\Prayer`, following its `Briefing.md` (what prayer is, its forms, how it is expressed, kinds of prayer, special prayers, reminding God of promises, what to pray, when to pray). The material: Logos research assistant answers (`Reminding God of promises.md`, `forms of prayer.md`, `expressing prayer.md`); Elwell and Beitzel, "Prayer" (*Baker Encyclopedia of the Bible*, `Prayer.md`); Hatchett, "Prayer" (*Holman Illustrated Bible Dictionary*, `Prayer dialogue.md`); Talbert, "Prayer in the Life of the Church" (*Lexham Survey of Theology*) and Hodge, *Systematic Theology* 3:692–709 (both in `forms of prayer.md`); Smith and Lee, *Handfuls on Purpose* (`Christian workers.md`); and the STEP verse export `prayer verses from STEP.md` (991 ESV verses). The file `prayer verses,.csv` holds verses on wonder and amazement, not prayer, and was not used. The chapters are a drafted study built from that material, not a transcription of it.

## Site presentation overrides

<!-- SITE-PRESENTATION: read by the site build. Fill a line to replace the current value; leave it blank to keep the current one. -->

- **TITLE:** 
- **SUBTITLE:** 
- **DESCRIPTION:** 

Current values (for reference, set by the build when a field above is blank):

- Title: The Practice of Prayer
- Subtitle: none
- Description (Home card): What prayer is, the forms it takes and how it is expressed, praying God’s promises back to him, and what and when to pray

## Destination

Prepared and approved pages for this book belong in this folder. Keep the original chapter order and preserve supplied meaning and wording unless the author gives different instructions.
