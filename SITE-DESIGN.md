# Site page and interaction guidance

This document records the agreed direction for the Learning4Comfort reading experience. It is guidance for the site framework and its page templates, not permission to edit or publish a book's text.

## Shared header and footer

- Show a consistent site header and footer on the home page, book contents pages, chapters, search results, and legal/contact pages.
- The header should identify Learning4Comfort and provide simple navigation to Home, Books, and Search. Keep it compact and usable on phones, with an accessible menu if needed.
- The footer should provide a contact route and links to the applicable privacy, cookie, accessibility, and other legal information. Include only pages and details that have been confirmed and published; do not ship broken or placeholder links.
- The selected contact approach is a dedicated public email address: `leroux@cilliers.co.uk`, approved for public display by the operator.
- Keep both areas visually quiet so the book text remains the focus. Use semantic `header`, `nav`, and `footer` landmarks, descriptive link names, keyboard access, visible focus, and mobile-friendly controls.
- The starter page now demonstrates the site identity and approved email contact in its header/footer. Legal links should be added once the applicable pages and accurate content are ready; do not create dead or placeholder legal links.

## Readers and visual direction

- Serve both general readers and people familiar with Bible study.
- Use an editorial, book-like reading experience, not a reference-work interface.
- Use warm ivory backgrounds, muted blue accents, and charcoal text.
- Prefer readable typography, generous spacing, and a restrained visual design over dense interface elements.
- Design for phones first and ensure text, controls, and navigation remain comfortable and usable on small screens.
- Keep chapter text in a comfortably readable column on larger screens; do not stretch long lines across the full viewport.
- Provide visible keyboard focus, semantic headings and landmarks, adequate contrast, and controls with clear labels.

## Page templates

### Home

- Introduce Learning4Comfort briefly.
- Present the available books as clear, readable choices.
- Provide a global search entry point.
- Offer a continue-reading link when a saved position exists in this browser.

### Book opening / contents

- Show the book title and a short introduction.
- List chapters in their authored order, with clear titles and links.
- Make the first chapter easy to start.

### Chapter

- Identify the book and chapter near the title.
- Keep the reading column uncluttered and preserve the approved text and inline references.
- Provide a contents link and previous/next chapter navigation, including clear beginning and end states.
- On narrow screens, keep navigation easy to reach without obscuring the text.
- Restore the reader's last position in that book when it is reopened in the same browser on the same device. Provide a way to continue from the beginning; store progress locally, not as an account or on a server.

## Search and progress behavior

- Search the text of all published books and chapters from anywhere on the site.
- Present results with the book and chapter title and a link to the relevant page. Do not require readers to use a reference-study workflow to reach a result.
- Index only approved, published content. Exclude inbox files, archived originals, authoring instructions, and unpublished drafts.
- Save a separate reading position per book in the current browser's local storage. Do not transmit reading history.
- If local storage is unavailable or cleared, pages must remain usable and display no false claim that progress was saved.
- Account-based storage, cross-device sync, highlighting, and notes are not part of the current scope.

## Editorial handling

- The approved manuscript is authoritative. Preserve its meaning and wording unless the book's `README.md` or an explicit author request says otherwise.
- Preserve supplied Scripture references inline. Do not silently turn them into links, footnotes, or a reference apparatus.
- Do not invent summaries, author biographies, dates, or other book metadata. Ask if required information is missing.
- See the root `README.md` for the intake, approval, archive, and publication workflow.

## Legal and contact launch readiness

The site operator is based in the United Kingdom, and the intended audience is worldwide, including the UK. Some implementation details are still to be confirmed. A `.uk` domain alone does not establish every reader's jurisdiction or the full set of applicable obligations. Check the rules applicable to the actual service and audience before launch; do not represent this checklist as legal advice or claim compliance without checking the applicable requirements. Seek qualified advice where appropriate.

Before launch, confirm and document:

- The operator's public identity and whether any further contact or business details must be disclosed.
- Which jurisdiction-specific obligations apply to the intended worldwide audience and whether the site should limit or tailor availability in any places.
- The UK privacy and electronic communications requirements relevant to the actual data uses and technologies selected; do not assume that a static site, an email link, or a local-storage feature has a particular legal outcome without checking its implementation.
- What personal data is actually collected or processed by the site, hosting provider, contact channel, and any third-party services; why it is used, how long it is retained, and how readers can exercise applicable rights.
- Whether analytics, advertising, embedded third-party content, or non-essential cookies/storage are used, and what notices, consent, or controls applicable law requires. Reading progress is intended to remain in local browser storage, but this behavior must be accurately disclosed if implemented.
- Which legal and accessibility pages are appropriate, their accurate content, and how they will be kept current.
- A contact mechanism that works, is monitored, and explains what to expect. Do not collect more information than needed.
- That any required notices or consent controls are available before enabling the relevant processing, and that deployed links, privacy behavior, and contact routes have been tested.

Do not invent an operator identity, postal address, privacy promise, retention period, cookie statement, or legal terms. The public email address is confirmed, but until the remaining facts above are confirmed, treat public deployment and any unverified legal pages as launch blockers rather than adding generic boilerplate.

## Reusable source outlines

Use `templates/book-opening.md` and `templates/chapter.md` as structural outlines during preparation. They are not published content. A book's own `README.md` may add rules, but should not silently contradict the site-wide publication safeguards.
