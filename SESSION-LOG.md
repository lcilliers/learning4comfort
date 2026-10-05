# Session Log and Follow-up Tasks

Working log of open tasks for Learning4Comfort. Publication history stays in `PUBLICATION-TRACKER.md`.

## Session 2026-10-03

Done: site established; books published (Is the Bible Sexist?, The Holy Spirit, The Inner Being, The Significance of God's Word and Its Personification in Jesus); header/footer, Feedback and Credits & Privacy pages; custom domain `learning4comfort.uk` live.

## Session 2026-10-04

Done: fifth book "When Forgiveness Feels Impossible" published, with the summary leading the opening page and the research chapters and appendices as supporting material. Added a "Site presentation overrides" section (TITLE, SUBTITLE, DESCRIPTION) to every book README, documented in the root README, and applied all five sets to the opening pages and Home cards. Card wording fixed for Is the Bible Sexist?. Everything is pushed (latest `ff356cb`).

## Open follow-up tasks

| # | Task | Owner | Status |
|---|------|-------|--------|
| 1 | Enforce HTTPS in GitHub Settings → Pages once the option is available for `learning4comfort.uk` | Author | Open |
| 2 | Fix Formspree, then give the new form ID so a contact form can be added to the Feedback page and the privacy text updated to say Formspree receives the message | Author, then assistant | Open |
| 3 | Review and fix inconsistencies and refinements noted by the author across the published books and site | Author lists, assistant fixes | Open |
| 4 | Global search across all books | Assistant | Done 2026-10-05: deployment-built global index, Search page and home entry point; per-book search remains separately scoped |
| 5 | Chapter navigation improvements | Assistant | Verified 2026-10-05: all 49 chapter pages already have a book-contents route and previous/next pager; no missing navigation found |
| 6 | Local reading-position feature (update the privacy page if it stores data on the reader's device) | Assistant | Done 2026-10-05: per-book local resume positions, continue links on home/book pages, start-over control, and privacy disclosure |
| 7 | Set up the Bible_Projects deploy key and secret, if still needed | Author and assistant | Open |
| 9 | Check how the Forgiveness opening page reads: the summary should carry the weight, the supporting sections less. Adjust the layout if needed | Author reviews, assistant adjusts | Open |
| 10 | Decide whether overrides should also change browser tab titles and chapter breadcrumbs (currently they keep the original titles) | Author | Open |
| 11 | Tidy wording in overrides: "woman" vs "women" in the Is the Bible Sexist? description and subtitle, and the double space in the Forgiveness description | Author | Open |
| 12 | Automate applying README overrides in the build, if wanted (currently applied by the assistant on request) | Assistant | Open |
| 8 | Review the Credits & Privacy wording if features change (analytics, forms, local storage) | Author | Updated local-storage disclosure 2026-10-05; author review remains open |
