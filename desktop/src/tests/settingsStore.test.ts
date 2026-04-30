import { afterAll, beforeEach, describe, expect, it } from 'bun:test'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

const settingsDir = fs.mkdtempSync(path.join(os.tmpdir(), 'officex-settings-dir-'))
const previousSettingsDir = process.env.OFFICEX_SETTINGS_DIR
process.env.OFFICEX_SETTINGS_DIR = settingsDir

const { buildDefaultSettings, resolveOfficeXHomePath } = await import('../main/actionPlans')
const { loadSettings, saveSettings } = await import('../main/settingsStore')

afterAll(() => {
  fs.rmSync(settingsDir, { recursive: true, force: true })
  if (previousSettingsDir === undefined) {
    delete process.env.OFFICEX_SETTINGS_DIR
  } else {
    process.env.OFFICEX_SETTINGS_DIR = previousSettingsDir
  }
})

function settingsPath(): string {
  return path.join(resolveOfficeXHomePath(), 'settings.json')
}

function resetSettingsHome(): void {
  fs.rmSync(resolveOfficeXHomePath(), { recursive: true, force: true })
}

describe('loadSettings and saveSettings', () => {
  beforeEach(() => {
    process.env.OFFICEX_SETTINGS_DIR = settingsDir
  })

  it('returns the default OfficeX settings shape when no file exists', () => {
    resetSettingsHome()

    const settings = loadSettings()

    expect(settings).toEqual({
      workspaceRoot: path.join(resolveOfficeXHomePath(), 'workspace'),
      sandboxRoot: path.join(resolveOfficeXHomePath(), 'sandboxes'),
      approvalMode: 'ask_every_conflict',
    })
  })

  it('merges partial settings and persists the canonical three-field payload', () => {
    resetSettingsHome()

    const nextSettings = saveSettings({
      sandboxRoot: '/tmp/officex-sandboxes',
      approvalMode: 'full_auto_in_sandbox',
    })

    const raw = JSON.parse(fs.readFileSync(settingsPath(), 'utf-8')) as Record<string, unknown>

    expect(nextSettings).toEqual({
      workspaceRoot: path.join(resolveOfficeXHomePath(), 'workspace'),
      sandboxRoot: '/tmp/officex-sandboxes',
      approvalMode: 'full_auto_in_sandbox',
    })
    expect(raw).toEqual(nextSettings)
    expect(Object.keys(raw).sort()).toEqual([
      'approvalMode',
      'sandboxRoot',
      'workspaceRoot',
    ])
  })

  it('saveSettings rewrites settings.json back to the canonical three fields when legacy keys exist', () => {
    resetSettingsHome()
    fs.mkdirSync(resolveOfficeXHomePath(), { recursive: true })
    fs.writeFileSync(
      settingsPath(),
      JSON.stringify(
        {
          workspaceRoot: '/tmp/officex-workspace',
          sandboxRoot: '/tmp/officex-sandboxes',
          approvalMode: 'ask_every_conflict',
          legacyFlag: true,
          lastOpenedAt: '2026-04-21T08:00:00.000Z',
        },
        null,
        2,
      ),
      'utf-8',
    )

    const nextSettings = saveSettings({
      approvalMode: 'review_only',
    })
    const raw = JSON.parse(fs.readFileSync(settingsPath(), 'utf-8')) as Record<string, unknown>

    expect(nextSettings).toEqual({
      workspaceRoot: '/tmp/officex-workspace',
      sandboxRoot: '/tmp/officex-sandboxes',
      approvalMode: 'review_only',
    })
    expect(raw).toEqual(nextSettings)
    expect(Object.keys(raw).sort()).toEqual([
      'approvalMode',
      'sandboxRoot',
      'workspaceRoot',
    ])
  })

  it('falls back to defaults when the persisted settings payload is malformed', () => {
    fs.mkdirSync(resolveOfficeXHomePath(), { recursive: true })
    fs.writeFileSync(settingsPath(), '{"workspaceRoot":', 'utf-8')

    const settings = loadSettings()

    expect(settings).toEqual({
      workspaceRoot: path.join(resolveOfficeXHomePath(), 'workspace'),
      sandboxRoot: path.join(resolveOfficeXHomePath(), 'sandboxes'),
      approvalMode: 'ask_every_conflict',
    })
  })
})
