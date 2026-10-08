---
description: Process new files in publication-inbox into book pages, rebuild search, archive, and publish the site
---

Follow the workflow in `.github/prompts/publish-inbox.prompt.md` exactly. It is shared with GitHub Copilot, so keep it as the single source of the steps.

When running it in Claude Code:

- Use the Claude co-author trailer on the commit instead of the Copilot one.
- If `gh` is not signed in, follow the deploy run through `https://api.github.com/repos/lcilliers/learning4comfort/actions/runs?head_sha=<commit>` until it completes.
