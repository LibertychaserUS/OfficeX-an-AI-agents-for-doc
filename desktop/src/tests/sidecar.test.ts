import { afterAll, describe, expect, it, mock } from 'bun:test'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

import type { OfficeXActionPlan } from '../shared/types'

const settingsDir = fs.mkdtempSync(path.join(os.tmpdir(), 'officex-sidecar-settings-'))
const previousSettingsDir = process.env.OFFICEX_SETTINGS_DIR
process.env.OFFICEX_SETTINGS_DIR = settingsDir

type ExecFileCallback = (
  error: { code?: number | string; message?: string } | null,
  stdout: string,
  stderr: string,
) => void

let execFileImpl = (
  _command: string,
  _args: string[],
  _options: Record<string, unknown>,
  callback: ExecFileCallback,
): void => {
  callback(null, '', '')
}

mock.module('node:child_process', () => ({
  execFile: (
    command: string,
    args: string[],
    options: Record<string, unknown>,
    callback: ExecFileCallback,
  ) => execFileImpl(command, args, options, callback),
}))

const { executeActionPlan } = await import('../main/sidecar')

function makePlan(actionId: OfficeXActionPlan['id']): OfficeXActionPlan {
  return {
    id: actionId,
    traceId: `${actionId}-trace`,
    createdAt: '2026-04-21T15:00:00.000Z',
    requestedBy: 'desktop-shell',
    kind: 'python-cli',
    cwd: '/tmp/officex-workspace',
    pythonExecutable: '/tmp/officex-workspace/.venv/bin/python',
    commandLabel: `officex ${actionId}`,
    summary: `Run ${actionId}`,
    args: ['-m', 'tools.report_scaffold_v3.product_entry', actionId],
  }
}

afterAll(() => {
  fs.rmSync(settingsDir, { recursive: true, force: true })
  if (previousSettingsDir === undefined) {
    delete process.env.OFFICEX_SETTINGS_DIR
  } else {
    process.env.OFFICEX_SETTINGS_DIR = previousSettingsDir
  }
})

describe('executeActionPlan', () => {
  it('parses JSON stdout into status and artifact paths', async () => {
    const payload = {
      overall_status: 'warning',
      candidate_docx: '/tmp/officex-workspace/candidate.docx',
      validation_report_path: '/tmp/officex-workspace/validation.json',
      task_packet_path: '/tmp/officex-workspace/task-packet.json',
      sandbox_manifest_path: '/tmp/officex-workspace/sandbox.json',
      report_markdown_path: '/tmp/officex-workspace/report.md',
    }

    execFileImpl = (_command, _args, _options, callback) => {
      callback(null, JSON.stringify(payload), '')
    }

    const execution = await executeActionPlan(makePlan('run-docx-demo'))

    expect(execution.executionId).toContain('run-docx-demo-')
    expect(execution.status).toBe('warning')
    expect(execution.verificationScope).toBe('mixed')
    expect(execution.executedBy).toBe('desktop-shell')
    expect(execution.message).toBe('受控文档任务完成，但仍有人工复核项。')
    expect(execution.payload).toEqual(payload)
    expect(execution.executionRecordPath).not.toBeNull()
    expect(execution.stdoutLogPath).not.toBeNull()
    expect(execution.stderrLogPath).not.toBeNull()
    expect(execution.artifactPaths).toEqual(
      expect.arrayContaining([
        '/tmp/officex-workspace/candidate.docx',
        '/tmp/officex-workspace/validation.json',
        '/tmp/officex-workspace/task-packet.json',
        '/tmp/officex-workspace/sandbox.json',
        '/tmp/officex-workspace/report.md',
        execution.executionRecordPath!,
        execution.stdoutLogPath!,
        execution.stderrLogPath!,
      ]),
    )
    expect(fs.existsSync(execution.executionRecordPath!)).toBe(true)
  })

  it('treats a non-zero exit as a failed action even without JSON output', async () => {
    execFileImpl = (_command, _args, _options, callback) => {
      callback(Object.assign(new Error('sidecar failed'), { code: 2 }), '', 'sidecar exploded')
    }

    const execution = await executeActionPlan(makePlan('doctor'))

    expect(execution.executionId).toContain('doctor-')
    expect(execution.status).toBe('fail')
    expect(execution.verificationScope).toBe('mixed')
    expect(execution.message).toBe('环境自检失败。')
    expect(execution.payload).toBeUndefined()
    expect(execution.artifactPaths).toEqual(
      expect.arrayContaining([
        execution.executionRecordPath!,
        execution.stdoutLogPath!,
        execution.stderrLogPath!,
      ]),
    )
    expect(execution.stderr).toBe('sidecar exploded')
  })

  it('treats string spawn error codes as failures and preserves the error message', async () => {
    execFileImpl = (_command, _args, _options, callback) => {
      callback(
        Object.assign(new Error('spawn ENOENT'), { code: 'ENOENT' }),
        '',
        '',
      )
    }

    const execution = await executeActionPlan(makePlan('doctor'))

    expect(execution.status).toBe('fail')
    expect(execution.stderr).toContain('spawn ENOENT')
  })
})
