import fs from 'node:fs'
import path from 'node:path'

import type { OfficeXActionExecution } from '../shared/types'
import { resolveOfficeXHomePath } from './actionPlans'

function executionHistoryRoot(): string {
  return path.join(resolveOfficeXHomePath(), 'runtime-logs', 'executions')
}

function executionDir(executionId: string): string {
  return path.join(executionHistoryRoot(), executionId)
}

export function persistExecutionRecord(
  execution: OfficeXActionExecution,
): OfficeXActionExecution {
  const recordDir = executionDir(execution.executionId)
  fs.mkdirSync(recordDir, { recursive: true })

  const executionRecordPath = path.join(recordDir, 'execution.json')
  const stdoutLogPath = path.join(recordDir, 'stdout.log')
  const stderrLogPath = path.join(recordDir, 'stderr.log')

  fs.writeFileSync(stdoutLogPath, execution.stdout, 'utf-8')
  fs.writeFileSync(stderrLogPath, execution.stderr, 'utf-8')

  const persistedExecution: OfficeXActionExecution = {
    ...execution,
    executionRecordPath,
    stdoutLogPath,
    stderrLogPath,
    artifactPaths: Array.from(
      new Set(
        [
          ...execution.artifactPaths,
          executionRecordPath,
          stdoutLogPath,
          stderrLogPath,
        ].filter((item): item is string => Boolean(item)),
      ),
    ),
  }

  fs.writeFileSync(
    executionRecordPath,
    JSON.stringify(persistedExecution, null, 2),
    'utf-8',
  )

  return persistedExecution
}

export function loadExecutionHistory(limit = 20): OfficeXActionExecution[] {
  const root = executionHistoryRoot()
  if (!fs.existsSync(root)) {
    return []
  }

  return fs
    .readdirSync(root, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join(root, entry.name, 'execution.json'))
    .filter((recordPath) => fs.existsSync(recordPath))
    .map((recordPath) => {
      const raw = fs.readFileSync(recordPath, 'utf-8')
      const parsed = JSON.parse(raw) as OfficeXActionExecution
      return {
        recordPath,
        execution: parsed,
      }
    })
    .sort((left, right) => right.execution.startedAt.localeCompare(left.execution.startedAt))
    .slice(0, limit)
    .map((entry) => entry.execution)
}
