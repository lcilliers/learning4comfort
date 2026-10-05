# Learning4Comfort content handoff

`content/` is the destination for pages and assets explicitly selected for publication from `Bible_Projects`. The target repository owns the website, build, GitHub Pages deployment, and custom domain. It is an independent site, not a subset of the research repository.

To copy the Inner Being manuscripts from the source side, use the routine `Copy-NarrativeToLearning4Comfort.ps1` in `iba\app\ps\`. It copies the files to `publishing/learning4comfort/publication-inbox/the_inner_being`. It does not copy the Bible_Projects repository, alter the target site's framework, or configure GitHub Pages.

## Access setup

After creating `lcilliers/learning4comfort` with a `main` branch:

1. Create an SSH deploy key for that repository with write access and add its public key as a deploy key on `lcilliers/learning4comfort`.
2. Add the private key as the `LEARNING4COMFORT_DEPLOY_KEY` Actions repository secret in `lcilliers/Bible_Projects`.
3. In `lcilliers/learning4comfort`, set **Settings → Pages → Build and deployment → Source** to **GitHub Actions**. The workflow in `.github/workflows/deploy-pages.yml` combines the site shell in `site/` with published files in `content/` and deploys them. The first push to `main` (or a manual workflow run) triggers deployment.
4. Configure `learning4comfort.uk` as the custom domain in the target repository's Pages settings and complete the DNS records with the domain registrar. `site/CNAME` ensures the custom domain is included in each deployment.

The private key must never be committed to either repository. The sync workflow only writes to `content/`; it leaves the target repository's other files untouched.

## Visibility

`lcilliers/Bible_Projects` is public. Any files placed in its staging folder are public there as well as copied to this repository. The staging folder is a publishing boundary, not a privacy boundary.

For files prepared locally in this repository, use the Git-ignored `publication-inbox/` folder. Follow the workflow in the root [README.md](README.md). Originals are moved after preparation into the Git-ignored `publication-archive/`; only approved material in `content/` is eligible for deployment. Book `README.md` files are authoring instructions and are omitted from the generated site.
