# Learning4Comfort

This is the independent repository for the Learning4Comfort website. The site framework, GitHub Pages deployment, custom-domain configuration, and published experience belong here, not in `Bible_Projects`.

## How the site is organized

The site contains separate study results, each treated as a **book**. A book's published pages belong under `content/books/<book-folder>/`. Each book folder has a `README.md` with any rules specific to that book. The existing folders are `holy_spirit`, `is_bible_sexist`, and `the_inner_being`.

## Design direction

The site should lean toward an **editorial reading experience**: inviting, clear, and comfortable for reading a book from beginning to end. It is for a mix of general and experienced readers. A reference-oriented study interface is not a current goal.

The design direction is warm ivory with muted blue accents and charcoal text. Prioritize mobile readability, simple navigation, clear chapter sequence, and comfortable line length. Chapter pages should have previous/next navigation and a route back to the book contents. Book opening pages should have a title, short introduction, and contents. Keep source references inline as supplied; do not convert them to linked reference tools or footnotes.

Every page should use a consistent site header and footer. The header should identify the site and provide clear navigation; the footer should provide contact and applicable legal/accessibility information. The approved public contact address is `leroux@cilliers.co.uk`; accurate legal page contents and any additional legal details still need confirmation before launch.

Site-wide search should find text across all published books and chapters. Remember each reader's most recent reading position locally in that browser and on that device; no account or cross-device syncing is expected. See [SITE-DESIGN.md](SITE-DESIGN.md) for the page, interaction, and launch-readiness guidance, and the reusable source outlines in `templates/`.

## Preparing a publication

`publication-inbox/` is a local-only staging folder. Place each batch in `publication-inbox/<book-folder>/`, using the matching folder name under `content/books/`. Process one book folder at a time; do not mix books in one batch. When asked to prepare its contents, I will:

1. Read the site instructions in this file and the applicable book's `content/books/<book-folder>/README.md`.
2. Inspect all inbox files as one batch, identify their intended order, and prepare site-ready pages in that book's `content/books/<book-folder>/` directory, following its specific rules.
3. Preserve the supplied meaning and wording unless the book's rules or your request explicitly permit edits. If the book, ordering, or a necessary editorial decision is unclear, ask before proceeding.
4. Check the prepared output, record the preparation in `PUBLICATION-TRACKER.md`, then move the original inbox files into the local-only `publication-archive/<book-folder>/YYYY-MM-DD/` folder. Do not overwrite existing files; stop and resolve any name collision.

The inbox and archive are excluded from Git. The tracker records preparation and actual publication as separate events. Preparing files is not approval to publish them: ask for your review and explicit approval before committing or pushing prepared content. A push to `main` triggers the Pages deployment workflow.

## Published content and authoring instructions

`content/` is the site build's input and may hold prepared pages while they await your review. Do not commit or push unapproved material; only explicitly approved pages may be published. Book folders also contain instruction files, which the deployment workflow excludes from the generated site. Use the source outlines in `templates/` when preparing book and chapter pages. The source-side workflow in `Bible_Projects` may also sync selected files into `content/`; see [SOURCE-SETUP.md](SOURCE-SETUP.md).

## Activity history

Append each event to [PUBLICATION-TRACKER.md](PUBLICATION-TRACKER.md) in date order. Preparation entries identify the book, source files, destination pages, and archive location. Publication entries identify the approved pages and the deployment date or run when known. Never record that something was published merely because it was prepared.

## Launch readiness

Do not deploy the site publicly or claim legal compliance until the actual data handling, applicable legal requirements, required disclosures, and accurate policy text have been confirmed. The contact address is set, but the remaining legal and operational checks are still launch blockers. See the launch-readiness checklist in [SITE-DESIGN.md](SITE-DESIGN.md).

## Setup status

- Standalone repository location: `C:\learning4comfort`
- Custom domain: `learning4comfort.uk` (purchased; DNS and GitHub Pages still need configuration)
- Pages build/deployment: workflow configured in `.github/workflows/deploy-pages.yml`; enable GitHub Actions as the Pages build source in repository settings
- Source-to-site transfer: workflow prepared in `Bible_Projects`; it requires a target repository deploy key and a matching Actions secret

See [SOURCE-SETUP.md](SOURCE-SETUP.md) for the cross-repository handoff setup.

The workflow publishes the site shell from `site/` together with approved pages and assets from `content/`. Files in `content/` take precedence if they have the same path as a site-shell file. Until published content arrives, the shell serves a simple preparation page.
