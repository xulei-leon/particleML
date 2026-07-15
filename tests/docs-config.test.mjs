import assert from 'node:assert/strict'
import { readFileSync, readdirSync } from 'node:fs'
import { join, relative, sep } from 'node:path'
import test from 'node:test'
import { fileURLToPath } from 'node:url'

import config, { createSidebar } from '../docs/.vitepress/config.mjs'

const docsRoot = fileURLToPath(new URL('../docs', import.meta.url))
const packageJson = JSON.parse(readFileSync(new URL('../package.json', import.meta.url), 'utf8'))

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

test('package scripts use VitePress subcommands', () => {
  assert.equal(packageJson.scripts['docs:dev'], 'vitepress dev docs')
  assert.equal(packageJson.scripts['docs:build'], 'vitepress build docs')
})
