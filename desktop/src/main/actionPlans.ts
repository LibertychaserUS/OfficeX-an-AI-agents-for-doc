import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

import type {
  OfficeXActionId,
  OfficeXActionPlan,
  OfficeXChatControls,
  OfficeXCheckStatus,
  OfficeXDesktopActionSummary,
  OfficeXDesktopBootstrap,
  OfficeXRuntimeStatus,
  OfficeXThreadSummary,
  OfficeXUserSettings,
  OfficeXWorkbenchNavigation,
  OfficeXWorkbenchShell,
  OfficeXWorkspaceSummary,
} from '../shared/types'
import { loadWorkbenchState } from './workbenchStateStore'

export function resolveOfficeXHomePath(): string {
  return process.env.OFFICEX_SETTINGS_DIR ?? path.join(os.homedir(), 'Library', 'Application Support', 'OfficeX')
}

export const OFFICEX_HOME_PATH = resolveOfficeXHomePath()
const DESKTOP_BOOTSTRAP_SCHEMA_VERSION = 'desktop-bootstrap-v1'
const DEFAULT_WORKSPACE_ID = 'default-workspace'
const DEFAULT_THREAD_ID = 'default-thread'

interface DoctorCheckRecord {
  check_id?: unknown
  status?: unknown
  summary?: unknown
}

interface DoctorReportRecord {
  overall_status?: unknown
  recommended_next_action?: unknown
  workspace_root?: unknown
  sandbox_root?: unknown
  report_json_path?: unknown
  report_markdown_path?: unknown
  checks?: unknown
}

function hasExecutable(binaryName: string): boolean {
  const searchPath = process.env.PATH ?? ''
  return searchPath
    .split(path.delimiter)
    .filter(Boolean)
    .some((entry) => fs.existsSync(path.join(entry, binaryName)))
}

function detectWordApp(): boolean {
  const override = process.env.OFFICEX_WORD_APP_PATH
  const candidates = [
    override,
    '/Applications/Microsoft Word.app',
    path.join(os.homedir(), 'Applications', 'Microsoft Word.app'),
  ].filter(Boolean) as string[]
  return candidates.some((candidate) => fs.existsSync(candidate))
}

function detectPythonExecutable(repoRoot: string): string | null {
  const candidates = [
    process.env.OFFICEX_PYTHON_PATH,
    path.join(repoRoot, '.venv', 'bin', 'python'),
    path.join(repoRoot, '.venv', 'bin', 'python3'),
  ].filter(Boolean) as string[]
  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) {
      return candidate
    }
  }
  return null
}

export function buildDefaultSettings(): OfficeXUserSettings {
  const homePath = resolveOfficeXHomePath()
  return {
    workspaceRoot: path.join(homePath, 'workspace'),
    sandboxRoot: path.join(homePath, 'sandboxes'),
    approvalMode: 'ask_every_conflict',
  }
}

function doctorLatestReportPath(): string {
  return path.join(resolveOfficeXHomePath(), 'reports', 'doctor', 'latest.json')
}

function isCheckStatus(value: unknown): value is OfficeXCheckStatus {
  return (
    value === 'pass' ||
    value === 'warning' ||
    value === 'fail' ||
    value === 'skipped' ||
    value === 'unknown'
  )
}

function findCheck(
  report: DoctorReportRecord,
  checkId: string,
): DoctorCheckRecord | null {
  if (!Array.isArray(report.checks)) {
    return null
  }
  const match = report.checks.find((item) => {
    if (!item || typeof item !== 'object') {
      return false
    }
    return (item as DoctorCheckRecord).check_id === checkId
  })
  if (!match || typeof match !== 'object') {
    return null
  }
  return match as DoctorCheckRecord
}

function readLatestDoctorState(settings: OfficeXUserSettings): {
  status: OfficeXCheckStatus
  reportPath: string | null
  summary: string
  ready: boolean
} {
  const latestPath = doctorLatestReportPath()
  if (!fs.existsSync(latestPath)) {
    return {
      status: 'unknown',
      reportPath: null,
      summary: '还没有运行当前工作区的环境自检。',
      ready: false,
    }
  }

  try {
    const raw = fs.readFileSync(latestPath, 'utf-8')
    const payload = JSON.parse(raw) as DoctorReportRecord
    if (
      payload.workspace_root !== settings.workspaceRoot ||
      payload.sandbox_root !== settings.sandboxRoot
    ) {
      return {
        status: 'unknown',
        reportPath:
          typeof payload.report_markdown_path === 'string'
            ? payload.report_markdown_path
            : typeof payload.report_json_path === 'string'
              ? payload.report_json_path
            : latestPath,
        summary: '最近一次 doctor 针对的是另一组 workspace/sandbox，当前设置仍需重新检查。',
        ready: false,
      }
    }

    const wordCheck = findCheck(payload, 'word_app')
    const smokeCheck = findCheck(payload, 'smoke_run')
    const workspaceCheck = findCheck(payload, 'workspace_root')
    const sandboxCheck = findCheck(payload, 'sandbox_root')
    const pythonCheck = findCheck(payload, 'python_runtime')
    const overallStatus = isCheckStatus(payload.overall_status)
      ? payload.overall_status
      : 'unknown'
    const coreReady =
      wordCheck?.status === 'pass' &&
      smokeCheck?.status === 'pass' &&
      workspaceCheck?.status === 'pass' &&
      sandboxCheck?.status === 'pass' &&
      pythonCheck?.status === 'pass'

    return {
      status: overallStatus,
      reportPath:
        typeof payload.report_markdown_path === 'string'
          ? payload.report_markdown_path
          : typeof payload.report_json_path === 'string'
            ? payload.report_json_path
          : latestPath,
      summary:
        typeof payload.recommended_next_action === 'string'
          ? payload.recommended_next_action
          : '环境自检已完成。',
      ready: coreReady,
    }
  } catch {
    return {
      status: 'fail',
      reportPath: latestPath,
      summary: '最近一次 doctor 报告已损坏，当前需要重新运行环境自检。',
      ready: false,
    }
  }
}

function buildRuntimeStatus(
  repoRoot: string,
  settings: OfficeXUserSettings,
): OfficeXRuntimeStatus {
  const pythonExecutable = detectPythonExecutable(repoRoot)
  const wordDetected = detectWordApp()
  const bunDetected = hasExecutable('bun')
  const providerConfigured = Boolean(
    process.env.OPENAI_API_KEY || process.env.ANTHROPIC_API_KEY,
  )
  const doctorState = readLatestDoctorState(settings)
  const ready = Boolean(pythonExecutable) && wordDetected && doctorState.ready
  const summary = !pythonExecutable
    ? 'Python sidecar 还没有准备好。'
    : !wordDetected
      ? 'Microsoft Word 当前不可见，不能视为已准备就绪。'
    : doctorState.status === 'unknown'
      ? '还没有完成当前工作区的环境自检。'
      : doctorState.ready
        ? doctorState.status === 'warning'
          ? '最近一次 doctor 已通过核心检查，但仍有非阻塞警告。'
          : '最近一次 doctor 已通过核心检查，可以运行受控任务。'
        : doctorState.status === 'fail'
          ? '最近一次 doctor 存在失败项，需要先修复。'
          : '最近一次 doctor 还没有满足产品入口的就绪条件。'
  return {
    ready,
    pythonExecutable,
    wordDetected,
    bunDetected,
    providerConfigured,
    doctorStatus: doctorState.status,
    doctorReportPath: doctorState.reportPath,
    doctorSummary: doctorState.summary,
    summary,
  }
}

function makeRunId(prefix: string): string {
  const stamp = new Date().toISOString().replace(/[-:TZ.]/g, '').slice(0, 14)
  return `${prefix}-${stamp}`
}

function makeTraceId(actionId: OfficeXActionId): string {
  return `${actionId}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`
}

function makeActionPlanBase(
  actionId: OfficeXActionId,
): Pick<OfficeXActionPlan, 'id' | 'traceId' | 'createdAt' | 'requestedBy'> {
  return {
    id: actionId,
    traceId: makeTraceId(actionId),
    createdAt: new Date().toISOString(),
    requestedBy: 'desktop-shell',
  }
}

function buildAvailableActions(): OfficeXDesktopActionSummary[] {
  return [
    {
      id: 'doctor',
      label: '检查这台 Mac',
      description: '验证 Python sidecar、Word、Bun 和最小 smoke path。',
    },
    {
      id: 'render-boundary',
      label: '验证 Word 输出',
      description: '测出当前渲染环境对长度、结构和操作的真实边界。',
    },
    {
      id: 'run-docx-demo',
      label: '运行受控文档任务',
      description: '直接跑一次 OfficeX docx MVP，并查看 candidate 与报告。',
    },
  ]
}

function buildThreadSummary(thread: {
  id: string
  title: string
  stage: OfficeXThreadSummary['stage']
  openingRequest: string | null
  confirmationCard: OfficeXThreadSummary['confirmationCard']
  taskRecord: OfficeXThreadSummary['taskRecord']
}): OfficeXThreadSummary {
  return {
    id: thread.id,
    title: thread.title,
    stage: thread.stage,
    openingRequest: thread.openingRequest,
    confirmationCard: thread.confirmationCard,
    taskRecord: thread.taskRecord,
  }
}

function buildWorkspaceSummary(workspace: {
  id: string
  title: string
  threads: Array<{ stage: OfficeXThreadSummary['stage'] }>
}): OfficeXWorkspaceSummary {
  return {
    id: workspace.id,
    title: workspace.title,
    threadCount: workspace.threads.length,
    archivedThreadCount: workspace.threads.filter(
      (thread) => thread.stage === 'archived',
    ).length,
  }
}

function buildWorkbenchNavigation(): OfficeXWorkbenchNavigation {
  const state = loadWorkbenchState()
  const workspaces = state.workspaces.map(buildWorkspaceSummary)
  const activeWorkspace =
    state.workspaces.find((workspace) => workspace.id === state.activeWorkspaceId) ??
    state.workspaces[0] ??
    null
  const threads = activeWorkspace?.threads.map(buildThreadSummary) ?? []
  const activeThreadId = threads.some((thread) => thread.id === state.activeThreadId)
    ? state.activeThreadId
    : threads[0]?.id ?? null

  return {
    workspaces,
    activeWorkspaceId: activeWorkspace?.id ?? DEFAULT_WORKSPACE_ID,
    activeThreadId,
    threads,
  }
}

function buildChatControls(): OfficeXChatControls {
  return {
    placeholder: '今天想要处理什么文档任务？',
    models: [
      { id: 'gpt-5.4', label: 'GPT-5.4' },
      { id: 'gpt-5.4-mini', label: 'GPT-5.4 Mini' },
    ],
    selectedModelId: 'gpt-5.4',
    reasoningChoices: [
      { id: 'low', label: '低' },
      { id: 'medium', label: '中' },
      { id: 'high', label: '高' },
    ],
    selectedReasoningId: 'medium',
    voiceInputEnabled: true,
  }
}

function buildWorkbenchShell(
  navigation: OfficeXWorkbenchNavigation,
): OfficeXWorkbenchShell {
  const activeThread =
    navigation.threads.find((thread) => thread.id === navigation.activeThreadId) ?? null

  return {
    mode: activeThread?.stage === 'workbench' ? 'workbench' : 'intake',
    headline:
      activeThread?.stage === 'workbench'
        ? '回到当前任务工作台'
        : '从任务开始，而不是从编辑器开始',
  }
}

export function buildDesktopBootstrap(
  repoRoot: string,
  settings: OfficeXUserSettings = buildDefaultSettings(),
): OfficeXDesktopBootstrap {
  const runtime = buildRuntimeStatus(repoRoot, settings)
  const actions = buildAvailableActions()
  const navigation = buildWorkbenchNavigation()
  return {
    schemaVersion: DESKTOP_BOOTSTRAP_SCHEMA_VERSION,
    homePath: resolveOfficeXHomePath(),
    repoRoot,
    primaryHeadline: '让这台 Mac 准备就绪',
    primaryActionId: runtime.ready ? 'run-docx-demo' : 'doctor',
    runtime,
    settings,
    actions,
    shell: buildWorkbenchShell(navigation),
    navigation,
    chatControls: buildChatControls(),
    utilityActions: actions,
  }
}

export function buildActionPlan(
  repoRoot: string,
  actionId: OfficeXActionId,
  settings: OfficeXUserSettings = buildDefaultSettings(),
): OfficeXActionPlan {
  const actionPlanBase = makeActionPlanBase(actionId)
  const pythonExecutable = detectPythonExecutable(repoRoot)
  if (!pythonExecutable) {
    return {
      ...actionPlanBase,
      kind: 'stub',
      cwd: repoRoot,
      pythonExecutable: null,
      commandLabel: 'setup-required',
      summary: 'Python sidecar 还没有准备好，当前不能运行 OfficeX 产品动作。',
      args: [],
    }
  }

  const baseArgs = ['-m', 'tools.report_scaffold_v3.product_entry']
  switch (actionId) {
    case 'doctor':
      return {
        ...actionPlanBase,
        kind: 'python-cli',
        cwd: repoRoot,
        pythonExecutable,
        commandLabel: 'officex doctor',
        summary: '检查这台 Mac 是否准备好运行 OfficeX。',
        args: [
          ...baseArgs,
          'doctor',
          '--workspace-root',
          settings.workspaceRoot,
          '--sandbox-root',
          settings.sandboxRoot,
          '--desktop-shell-dir',
          path.join(repoRoot, 'desktop'),
          '--as-json',
        ],
      }
    case 'render-boundary':
      return {
        ...actionPlanBase,
        kind: 'python-cli',
        cwd: repoRoot,
        pythonExecutable,
        commandLabel: 'officex render-boundary',
        summary: '验证当前 Word 环境对 OfficeX 任务的真实边界。',
        args: [
          ...baseArgs,
          'render-boundary',
          '--workspace-root',
          settings.workspaceRoot,
          '--sandbox-root',
          settings.sandboxRoot,
          '--as-json',
        ],
      }
    case 'run-docx-demo':
      return {
        ...actionPlanBase,
        kind: 'python-cli',
        cwd: repoRoot,
        pythonExecutable,
        commandLabel: 'officex task run-docx-mvp',
        summary: '运行一次受控 docx 任务，并生成 candidate 与审计报告。',
        args: [
          ...baseArgs,
          'runtime',
          'task',
          'run-docx-mvp',
          '--run-id',
          makeRunId('desktop-docx-demo'),
          '--sandbox-root',
          settings.sandboxRoot,
          '--approval-mode',
          settings.approvalMode,
          '--as-json',
        ],
      }
  }
  const unreachableActionId: never = actionId
  throw new Error(`Unsupported OfficeX action id: ${unreachableActionId}`)
}

export function inferRepoRoot(startPath: string): string {
  const override = process.env.OFFICEX_REPO_ROOT
  if (override) {
    return path.resolve(override)
  }
  let current = path.resolve(startPath)
  if (fs.existsSync(current) && fs.statSync(current).isFile()) {
    current = path.dirname(current)
  }
  for (let i = 0; i < 8; i += 1) {
    const pyprojectPath = path.join(current, 'pyproject.toml')
    const cliPath = path.join(current, 'tools', 'report_scaffold_v3', 'cli.py')
    if (fs.existsSync(pyprojectPath) && fs.existsSync(cliPath)) {
      return current
    }
    const parent = path.dirname(current)
    if (parent === current) {
      break
    }
    current = parent
  }
  return path.resolve(startPath, '..')
}
