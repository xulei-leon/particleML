# VitePress GitHub Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish every Markdown file under `docs/` as a VitePress site with automatic navigation and GitHub Pages deployment.

**Architecture:** A single VitePress configuration recursively reads `docs/` and derives grouped sidebar entries from directory names and first-level Markdown headings. Root npm scripts build the static output, and one GitHub Actions workflow deploys that output from `main`.

**Tech Stack:** Node.js 20, npm, VitePress 1.6.4, Node's built-in test runner, GitHub Pages Actions

## Global Constraints

- Keep all repository text, code, and comments in English.
- Use `docs/` as the VitePress content root.
- Configure the production base path as `/particleML/`.
- Do not add a custom theme, application framework, or navigation plugin.
- Leave existing HTML and PDF documents unchanged and outside automatic Markdown navigation.

---

### Task 1: Automatic VitePress Documentation Site

**Files:**
- Create: `package.json`
- Create: `package-lock.json`
- Create: `docs/index.md`
- Create: `docs/.vitepress/config.mjs`
- Create: `tests/docs-config.test.mjs`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: Markdown files recursively stored below `docs/`.
- Produces: `createSidebar(directory?: string): SidebarItem[]`, npm scripts `docs:dev`, `docs:build`, and `test`.

- [ ] **Step 1: Write the failing navigation test**

```js
import assert from 'node:assert/strict'
import { readdirSync } from 'node:fs'
import { join, relative, sep } from 'node:path'
import test from 'node:test'
import { fileURLToPath } from 'node:url'

import config, { createSidebar } from '../docs/.vitepress/config.mjs'

const docsRoot = fileURLToPath(new URL('../docs', import.meta.url))

function markdownLinks(directory = docsRoot) {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    if (entry.name.startsWith('.')) return []
    const path = join(directory, entry.name)
    if (entry.isDirectory()) return markdownLinks(path)
    if (!entry.name.endsWith('.md')) return []
    const route = relative(docsRoot, path).split(sep).join('/').replace(/\.md$/, '')
    return [route === 'index' ? '/' : `/${route.replace(/\/index$/, '')}`]
  })
}

function sidebarLinks(items) {
  return items.flatMap((item) => item.link ? [item.link] : sidebarLinks(item.items ?? []))
}

test('sidebar contains every Markdown page', () => {
  assert.deepEqual(sidebarLinks(createSidebar()).sort(), markdownLinks().sort())
})

test('site uses the repository Pages base path', () => {
  assert.equal(config.base, '/particleML/')
})
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `node --test tests/docs-config.test.mjs`

Expected: FAIL because `docs/.vitepress/config.mjs` does not exist.

- [ ] **Step 3: Add the minimal package and VitePress configuration**

Create `package.json` with VitePress 1.6.4, the three npm scripts, and Node 20 as the engine. Implement `createSidebar()` in `docs/.vitepress/config.mjs` with `node:fs` and `node:path`; recursively include non-hidden directories and `.md` files, sort each level alphabetically, use each document's first `#` heading with a humanized file-name fallback, and export the configured site with local search and `/particleML/` as its base.

Create `docs/index.md` as a short English landing page linking to the researcher profile, engineering, learning, and research sections. Add `node_modules/`, `docs/.vitepress/cache/`, and `docs/.vitepress/dist/` to `.gitignore`.

- [ ] **Step 4: Install dependencies and run checks**

Run: `npm install`

Expected: `package-lock.json` is created with no installation error.

Run: `npm test`

Expected: 2 tests pass.

Run: `npm run docs:build`

Expected: VitePress reports `build complete` and writes `docs/.vitepress/dist/index.html`.

- [ ] **Step 5: Commit the site**

```bash
git add package.json package-lock.json .gitignore docs/index.md docs/.vitepress/config.mjs tests/docs-config.test.mjs
git commit -m "feat: add VitePress documentation site"
```

### Task 2: GitHub Pages Deployment

**Files:**
- Create: `.github/workflows/docs.yml`

**Interfaces:**
- Consumes: the `npm run docs:build` script and `docs/.vitepress/dist` output from Task 1.
- Produces: automatic GitHub Pages deployments on pushes to `main` and manual workflow dispatches.

- [ ] **Step 1: Add the official Pages workflow**

Create `.github/workflows/docs.yml` with `contents: read`, `pages: write`, and `id-token: write`; use `actions/checkout@v4`, `actions/setup-node@v4` with Node 20 and npm caching, `actions/configure-pages@v5`, `npm ci`, `npm run docs:build`, `actions/upload-pages-artifact@v3`, and `actions/deploy-pages@v4`. Trigger it on `main` pushes and `workflow_dispatch`, and serialize deployments with the `pages` concurrency group.

- [ ] **Step 2: Re-run the complete local verification**

Run: `npm test && npm run docs:build`

Expected: 2 tests pass and VitePress reports `build complete`.

- [ ] **Step 3: Commit the deployment workflow and relocated planning documents**

```bash
git add .github/workflows/docs.yml project/superpowers docs/superpowers
git commit -m "ci: deploy documentation to GitHub Pages"
```
