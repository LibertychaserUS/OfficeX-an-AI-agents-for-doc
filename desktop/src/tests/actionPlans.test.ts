import { afterAll, beforeEach, describe, expect, it } from 'bun:test'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

const settingsDir = fs.mkdtempSync(path.join(os.tmpdir(), 'officex-action-plans-'))
const previousSettingsDir = process.env.OFFICEX_SETTINGS_DIR
process.env.OFFICEX_SETTINGS_DIR = settingsDir

const {
  buildActionPlan,
  buildDesktopBootstrap,
  buildDefaultSettings,
  resolveOfficeXHomePath,
} = await import('../main/actionPlans')

const fixtureRoots: string[] = []

function makeRepoFixture(withPython: boolean): string {
  const repoRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'officex-desktop-fixture-'))
  fixtureRoots.push(repoRoot)

  if (withPython) {
    const pythonPath = path.join(repoRoot, '.venv', 'bin')
    fs.mkdirSync(pythonPath, { recursive: true })
    const pythonExecutable = path.join(pythonPath, 'python')
    fs.writeFileSync(pythonExecutable, '#!/usr/bin/env python3\n', 'utf-8')
    fs.chmodSync(pythonExecutable, 0o755)
  }

  return repoRoot
}

function latestDoctorReportPath(): string {
  return path.join(resolveOfficeXHomePath(), 'reports', 'doctor', 'latest.json')
}

function writeLatestDoctorReport(
  overrides: Partial<Record<string, unknown>> = {},
): void {
  const settings = buildDefaultSettings()
  const payload = {
    overall_status: 'pass',
    recommended_next_action: 'This Mac is ready for the first OfficeX app MVP run.',
    workspace_root: settings.workspaceRoot,
    sandbox_root: settings.sandboxRoot,
    report_markdown_path: path.join(resolveOfficeXHomePath(), 'reports', 'doctor', 'sample.md'),
    checks: [
      { check_id: 'python_runtime', status: 'pass', summary: 'ok' },
      { check_id: 'word_app', status: 'pass', summary: 'ok' },
      { check_id: 'workspace_root', status: 'pass', summary: 'ok' },
      { check_id: 'sandbox_root', status: 'pass', summary: 'ok' },
      { check_id: 'smoke_run', status: 'pass', summary: 'ok' },
    ],
    ...overrides,
  }
  const targetPath = latestDoctorReportPath()
  fs.mkdirSync(path.dirname(targetPath), { recursive: true })
  fs.writeFileSync(targetPath, JSON.stringify(payload, null, 2), 'utf-8')
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

describe('buildDesktopBootstrap', () => {
  it('reports the product-facing home path and keeps readiness false until doctor has run', () => {
    const repoRoot = makeRepoFixture(true)

    const bootstrap = buildDesktopBootstrap(repoRoot)

    expect(bootstrap.schemaVersion).toBe('desktop-bootstrap-v1')
    expect(bootstrap.homePath).toBe(resolveOfficeXHomePath())
    expect(bootstrap.runtime.ready).toBe(false)
    expect(bootstrap.runtime.pythonExecutable).toBe(path.join(repoRoot, '.venv', 'bin', 'python'))
    expect(bootstrap.runtime.doctorStatus).toBe('unknown')
    expect(bootstrap.primaryActionId).toBe('doctor')
    expect(bootstrap.shell.mode).toBe('intake')
    expect(bootstrap.navigation.threads[0]?.stage).toBe('intake')
    expect(bootstrap.utilityActions).toHaveLength(3)
  })

  it('drops back to a stubbed runtime summary when python is not ready', () => {
    const repoRoot = makeRepoFixture(false)

    const bootstrap = buildDesktopBootstrap(repoRoot)
    const plan = buildActionPlan(repoRoot, 'doctor')

    expect(bootstrap.runtime.ready).toBe(false)
    expect(bootstrap.primaryActionId).toBe('doctor')
    expect(plan.kind).toBe('stub')
    expect(plan.summary).toContain('Python sidecar')
  })

  it('prefers the docx demo action only after a matching doctor report passes the core checks', () => {
    const repoRoot = makeRepoFixture(true)
    const wordAppPath = path.join(repoRoot, 'Applications', 'Microsoft Word.app')
    fs.mkdirSync(wordAppPath, { recursive: true })
    const previousWordPath = process.env.OFFICEX_WORD_APP_PATH
    process.env.OFFICEX_WORD_APP_PATH = wordAppPath
    writeLatestDoctorReport()

    try {
      const bootstrap = buildDesktopBootstrap(repoRoot)

      expect(bootstrap.runtime.ready).toBe(true)
      expect(bootstrap.runtime.wordDetected).toBe(true)
      expect(bootstrap.runtime.doctorStatus).toBe('pass')
      expect(bootstrap.primaryActionId).toBe('run-docx-demo')
    } finally {
      if (previousWordPath === undefined) {
        delete process.env.OFFICEX_WORD_APP_PATH
      } else {
        process.env.OFFICEX_WORD_APP_PATH = previousWordPath
      }
    }
  })
})

describe('buildActionPlan', () => {
  it('maps doctor to the product entry surface instead of the raw legacy CLI root', () => {
    const repoRoot = makeRepoFixture(true)

    const plan = buildActionPlan(repoRoot, 'doctor')

    expect(plan.traceId).toContain('doctor-')
    expect(plan.requestedBy).toBe('desktop-shell')
    expect(plan.createdAt).toContain('T')
    expect(plan.kind).toBe('python-cli')
    expect(plan.args).toEqual(
      expect.arrayContaining(['-m', 'tools.report_scaffold_v3.product_entry', 'doctor', '--as-json']),
    )
  })

  it('maps render-boundary and run-docx-demo through the product entry runtime', () => {
    const repoRoot = makeRepoFixture(true)
    const settings = {
      workspaceRoot: '/tmp/officex-workspace',
      sandboxRoot: '/tmp/officex-sandboxes',
      approvalMode: 'full_auto_in_sandbox' as const,
    }

    const boundaryPlan = buildActionPlan(repoRoot, 'render-boundary', settings)
    const runPlan = buildActionPlan(repoRoot, 'run-docx-demo', settings)

    expect(boundaryPlan.args).toEqual(
      expect.arrayContaining([
        '-m',
        'tools.report_scaffold_v3.product_entry',
        'render-boundary',
        '--workspace-root',
        settings.workspaceRoot,
        '--sandbox-root',
        settings.sandboxRoot,
        '--as-json',
      ]),
    )
    expect(runPlan.args).toEqual(
      expect.arrayContaining([
        '-m',
        'tools.report_scaffold_v3.product_entry',
        'runtime',
        'task',
        'run-docx-mvp',
        '--sandbox-root',
        settings.sandboxRoot,
        '--approval-mode',
        settings.approvalMode,
        '--as-json',
      ]),
    )
    expect(runPlan.args.some((item) => item.startsWith('desktop-docx-demo-'))).toBe(true)
    expect(boundaryPlan.traceId).toContain('render-boundary-')
    expect(runPlan.traceId).toContain('run-docx-demo-')
  })
})
