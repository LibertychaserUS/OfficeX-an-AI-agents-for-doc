import { afterAll, beforeEach, describe, expect, it } from 'bun:test'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

const settingsDir = fs.mkdtempSync(path.join(os.tmpdir(), 'officex-open-path-'))
const previousSettingsDir = process.env.OFFICEX_SETTINGS_DIR
process.env.OFFICEX_SETTINGS_DIR = settingsDir

const { validateOpenPath } = await import('../main/openPathPolicy')

const fixtureRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'officex-open-path-fixture-'))
const repoRoot = path.join(fixtureRoot, 'repo')
const workspaceRoot = path.join(fixtureRoot, 'workspace')
const sandboxRoot = path.join(fixtureRoot, 'sandboxes')

beforeEach(() => {
  fs.rmSync(fixtureRoot, { recursive: true, force: true })
  fs.mkdirSync(repoRoot, { recursive: true })
  fs.mkdirSync(workspaceRoot, { recursive: true })
  fs.mkdirSync(sandboxRoot, { recursive: true })
  fs.mkdirSync(settingsDir, { recursive: true })
})

afterAll(() => {
  fs.rmSync(fixtureRoot, { recursive: true, force: true })
  fs.rmSync(settingsDir, { recursive: true, force: true })
  if (previousSettingsDir === undefined) {
    delete process.env.OFFICEX_SETTINGS_DIR
  } else {
    process.env.OFFICEX_SETTINGS_DIR = previousSettingsDir
  }
})

function makeSettings() {
  return {
    workspaceRoot,
    sandboxRoot,
    approvalMode: 'ask_every_conflict' as const,
  }
}

describe('validateOpenPath', () => {
  it('allows OfficeX artifacts inside the sandbox root', () => {
    const reportPath = path.join(sandboxRoot, 'demo', 'reports', 'validation_report.md')
    fs.mkdirSync(path.dirname(reportPath), { recursive: true })
    fs.writeFileSync(reportPath, '# report\n', 'utf-8')

    const validated = validateOpenPath(reportPath, repoRoot, makeSettings())

    expect(validated).toBe(fs.realpathSync(reportPath))
  })

  it('allows machine-local reports under the OfficeX settings root', () => {
    const reportPath = path.join(settingsDir, 'reports', 'doctor', 'latest.md')
    fs.mkdirSync(path.dirname(reportPath), { recursive: true })
    fs.writeFileSync(reportPath, '# doctor\n', 'utf-8')

    const validated = validateOpenPath(reportPath, repoRoot, makeSettings())

    expect(validated).toBe(fs.realpathSync(reportPath))
  })

  it('rejects files outside the OfficeX roots', () => {
    const outsidePath = path.join(fixtureRoot, 'outside.md')
    fs.writeFileSync(outsidePath, '# outside\n', 'utf-8')

    expect(() => validateOpenPath(outsidePath, repoRoot, makeSettings())).toThrow(
      'outside the allowed OfficeX roots',
    )
  })

  it('rejects blocked file types even inside allowed roots', () => {
    const executablePath = path.join(sandboxRoot, 'demo', 'script.sh')
    fs.mkdirSync(path.dirname(executablePath), { recursive: true })
    fs.writeFileSync(executablePath, 'echo hi\n', 'utf-8')

    expect(() => validateOpenPath(executablePath, repoRoot, makeSettings())).toThrow(
      'blocked file type',
    )
  })
})
