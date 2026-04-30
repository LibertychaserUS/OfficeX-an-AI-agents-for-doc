import { afterAll, beforeEach, describe, expect, it } from 'bun:test'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

const settingsDir = fs.mkdtempSync(path.join(os.tmpdir(), 'officex-workbench-bootstrap-'))
const previousSettingsDir = process.env.OFFICEX_SETTINGS_DIR
process.env.OFFICEX_SETTINGS_DIR = settingsDir

const { buildDesktopBootstrap, resolveOfficeXHomePath } = await import('../main/actionPlans')

const fixtureRoots: string[] = []

function makeRepoFixture(): string {
  const repoRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'officex-workbench-repo-'))
  fixtureRoots.push(repoRoot)
  return repoRoot
}

function resetSettingsHome(): void {
  fs.rmSync(resolveOfficeXHomePath(), { recursive: true, force: true })
}

beforeEach(() => {
  process.env.OFFICEX_SETTINGS_DIR = settingsDir
  resetSettingsHome()
})

afterAll(() => {
  for (const fixtureRoot of fixtureRoots) {
    fs.rmSync(fixtureRoot, { recursive: true, force: true })
  }
  fs.rmSync(settingsDir, { recursive: true, force: true })
  if (previousSettingsDir === undefined) {
    delete process.env.OFFICEX_SETTINGS_DIR
  } else {
    process.env.OFFICEX_SETTINGS_DIR = previousSettingsDir
  }
})

describe('buildDesktopBootstrap workbench contract', () => {
  it('returns the intake-first defaults for a new desktop session', () => {
    const bootstrap = buildDesktopBootstrap(makeRepoFixture())

    expect(bootstrap).toEqual(
      expect.objectContaining({
        shell: expect.objectContaining({
          mode: 'intake',
        }),
      }),
    )
    expect(bootstrap.navigation.workspaces).toEqual([
      {
        id: 'default-workspace',
        title: '默认工作区',
        threadCount: 1,
        archivedThreadCount: 0,
      },
    ])
    expect(bootstrap.navigation.activeWorkspaceId).toBe('default-workspace')
    expect(bootstrap.navigation.activeThreadId).toBe('default-thread')
    expect(bootstrap.navigation.threads).toEqual([
      {
        id: 'default-thread',
        title: '新线程',
        stage: 'intake',
        openingRequest: null,
        confirmationCard: null,
        taskRecord: null,
      },
    ])
    expect(bootstrap.chatControls.placeholder).toContain('今天想要处理什么')
    expect(bootstrap.chatControls.models.map((model) => model.id)).toEqual([
      'gpt-5.4',
      'gpt-5.4-mini',
    ])
    expect(bootstrap.utilityActions.map((action) => action.id)).toEqual([
      'doctor',
      'render-boundary',
      'run-docx-demo',
    ])
  })
})
