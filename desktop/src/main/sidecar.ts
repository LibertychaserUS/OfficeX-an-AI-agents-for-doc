import { execFile } from 'node:child_process'

import type {
  OfficeXActionExecution,
  OfficeXActionId,
  OfficeXActionPlan,
  OfficeXActionStatus,
  OfficeXVerificationScope,
} from '../shared/types'
import { persistExecutionRecord } from './executionHistoryStore'

function extractArtifactPaths(payload: unknown): string[] {
  if (!payload || typeof payload !== 'object') {
    return []
  }
  const record = payload as Record<string, unknown>
  const keys = [
    'candidate_docx',
    'validation_report_path',
    'candidate_audit_path',
    'stage_history_review_path',
    'task_packet_path',
    'sandbox_manifest_path',
    'build_source_path',
    'report_json_path',
    'report_markdown_path',
    'source_fixture_dir',
    'benchmark_run_root',
  ]
  return keys
    .map((key) => record[key])
    .filter((value): value is string => typeof value === 'string')
}

function inferStatusFromPayload(payload: unknown): OfficeXActionStatus {
  if (!payload || typeof payload !== 'object') {
    return 'pass'
  }
  const record = payload as Record<string, unknown>
  const overall = record.overall_status
  if (overall === 'fail') {
    return 'fail'
  }
  if (overall === 'warning') {
    return 'warning'
  }
  if (
    typeof record.validation_error_count === 'number' &&
    record.validation_error_count > 0
  ) {
    return 'fail'
  }
  if (
    typeof record.candidate_error_count === 'number' &&
    record.candidate_error_count > 0
  ) {
    return 'fail'
  }
  return 'pass'
}

function buildMessage(actionId: OfficeXActionId, status: OfficeXActionStatus): string {
  const prefix =
    actionId === 'doctor'
      ? '环境自检'
      : actionId === 'render-boundary'
        ? '渲染边界测试'
        : '受控文档任务'
  if (status === 'fail') {
    return `${prefix}失败。`
  }
  if (status === 'warning') {
    return `${prefix}完成，但仍有人工复核项。`
  }
  return `${prefix}完成。`
}

function verificationScopeForAction(
  actionId: OfficeXActionId,
): OfficeXVerificationScope {
  if (actionId === 'doctor') {
    return 'mixed'
  }
  if (actionId === 'render-boundary') {
    return 'layout'
  }
  return 'mixed'
}

function maybeParseJson(stdout: string): unknown {
  const trimmed = stdout.trim()
  if (!trimmed) {
    return undefined
  }
  try {
    return JSON.parse(trimmed)
  } catch {
    return undefined
  }
}

function normalizeExitCode(
  error: { code?: number | string | null; message?: string } | null,
): number {
  if (!error) {
    return 0
  }
  if (typeof error.code === 'number') {
    return error.code
  }
  if (typeof error.code === 'string' && error.code.length > 0) {
    return 1
  }
  return 1
}

function mergeSpawnError(
  stderr: string,
  error: { code?: number | string | null; message?: string } | null,
): string {
  if (stderr) {
    return stderr
  }
  if (!error?.message) {
    return stderr
  }
  return error.message
}

function makeExecutionId(actionId: OfficeXActionId): string {
  return `${actionId}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`
}

export async function executeActionPlan(
  plan: OfficeXActionPlan,
): Promise<OfficeXActionExecution> {
  const startedAt = new Date()

  if (plan.kind === 'stub' || !plan.pythonExecutable) {
    const finishedAt = new Date()
    return persistExecutionRecord({
      executionId: makeExecutionId(plan.id),
      actionId: plan.id,
      plan,
      status: 'fail',
      startedAt: startedAt.toISOString(),
      finishedAt: finishedAt.toISOString(),
      durationMs: finishedAt.getTime() - startedAt.getTime(),
      verificationScope: verificationScopeForAction(plan.id),
      executedBy: 'desktop-shell',
      message: plan.summary,
      stdout: '',
      stderr: '',
      executionRecordPath: null,
      stdoutLogPath: null,
      stderrLogPath: null,
      artifactPaths: [],
    })
  }

  const result = await new Promise<{
    code: number
    stdout: string
    stderr: string
  }>((resolve) => {
    execFile(
      plan.pythonExecutable!,
      plan.args,
      {
        cwd: plan.cwd,
        encoding: 'utf-8',
        maxBuffer: 20 * 1024 * 1024,
        timeout: 10 * 60 * 1000,
      },
      (error, stdout, stderr) => {
        resolve({
          code: normalizeExitCode(error),
          stdout: stdout ?? '',
          stderr: mergeSpawnError(stderr ?? '', error),
        })
      },
    )
  })

  const payload = maybeParseJson(result.stdout)
  const status =
    result.code === 0 ? inferStatusFromPayload(payload) : ('fail' as const)
  const finishedAt = new Date()
  return persistExecutionRecord({
    executionId: makeExecutionId(plan.id),
    actionId: plan.id,
    plan,
    status,
    startedAt: startedAt.toISOString(),
    finishedAt: finishedAt.toISOString(),
    durationMs: finishedAt.getTime() - startedAt.getTime(),
    verificationScope: verificationScopeForAction(plan.id),
    executedBy: 'desktop-shell',
    message: buildMessage(plan.id, status),
    stdout: result.stdout,
    stderr: result.stderr,
    executionRecordPath: null,
    stdoutLogPath: null,
    stderrLogPath: null,
    payload,
    artifactPaths: extractArtifactPaths(payload),
  })
}
