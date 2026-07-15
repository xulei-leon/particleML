# VitePress GitHub Pages Design

## Goal

Publish the repository's `docs/` Markdown files as a VitePress site on GitHub Pages, with navigation that updates automatically when documentation files are added or removed.

## Architecture

- Use VitePress with `docs/` as the content root.
- Keep Node package metadata and commands at the repository root.
- Generate sidebar entries recursively from Markdown files in `docs/` without an additional navigation dependency.
- Use the first level-one heading as the page label, falling back to the file name.
- Configure the production base path as `/particleML/`.
- Deploy the generated static site through GitHub Actions and the official GitHub Pages actions.

## Content Behavior

- Every Markdown file below `docs/` is compiled into a page.
- Directory structure determines sidebar grouping, with directories and pages ordered alphabetically.
- Existing HTML and PDF files remain unchanged and are outside automatic Markdown navigation.
- VitePress configuration and internal Superpowers specifications are excluded from generated navigation.

## Deployment

- A workflow runs on pushes to `main` and through manual dispatch.
- The workflow installs locked dependencies, builds the site, uploads `docs/.vitepress/dist`, and deploys it to GitHub Pages.
- The workflow requests only the permissions required by GitHub Pages deployment.

## Verification

- Install dependencies and generate the lockfile.
- Run the VitePress production build locally.
- Confirm the generated output contains the site entry point and representative documentation pages.

## Non-goals

- No custom theme or application framework.
- No additional navigation plugin.
- No conversion of existing HTML or PDF documents.
- No automatic publishing outside the `main` branch workflow.
