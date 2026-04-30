import crypto from 'node:crypto'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

import type {
  OfficeXTaskConfirmationCard,
  OfficeXTaskChoiceId,
  OfficeXThreadStage,
  OfficeXThreadTaskRecord,
} from '../shared/types'

const WORKBENCH_STATE_SCHEMA_VERSION = 'workbench-state-v1'
const DEFAULT_WORKSPACE_ID = 'default-workspace'
const DEFAULT_THREAD_ID = 'default-thread'
const VALID_THREAD_STAGES = [
  'intake',
  'awaiting_confirmation',
  'workbench',
  'archived',
] as const
const VALID_TASK_CLASSIFICATIONS = [
  'generation',
  'modification',
  'review',
  'rewrite',
  'repair',
  'mixed',
] as const
const VALID_TASK_CHOICE_IDS = [
  'draft',
  'modify',
  'review',
  'rewrite',
  'repair',
  'custom',
] as const
const VALID_BASIS_INPUT_IDS = [
  'template',
  'writing_requirements',
  'review_rubric',
  'source_document',
] as const
const VALID_BASIS_INPUT_STATUSES = ['present', 'missing', 'optional'] as const

interface OfficeXWorkbenchThreadState {
  id: string
  title: string
  stage: OfficeXThreadStage
  openingRequest: string | null
  confirmationCard: OfficeXTaskConfirmationCard | null
  taskRecord: OfficeXThreadTaskRecord | null
  createdAt: string
  updatedAt: string
}

interface OfficeXWorkbenchWorkspaceState {
  id: string
  title: string
  createdAt: string
  updatedAt: string
  threads: OfficeXWorkbenchThreadState[]
}

export interface OfficeXWorkbenchState {
  schemaVersion: string
  activeWorkspaceId: string
  activeThreadId: string | null
  workspaces: OfficeXWorkbenchWorkspaceState[]
}

export function resolveOfficeXHomePath(): string {
  return process.env.OFFICEX_SETTINGS_DIR ?? path.join(os.homedir(), 'Library', 'Application Support', 'OfficeX')
}

function workbenchStatePath(): string {
  return path.join(resolveOfficeXHomePath(), 'workbench-state.json')
}

function ensureHomeDir(): void {
  fs.mkdirSync(resolveOfficeXHomePath(), { recursive: true })
}

function nowIso(): string {
  return new Date().toISOString()
}

function buildDefaultThreadState(timestamp: string): OfficeXWorkbenchThreadState {
  return {
    id: DEFAULT_THREAD_ID,
    title: '新线程',
    stage: 'intake',
    openingRequest: null,
    confirmationCard: null,
    taskRecord: null,
    createdAt: timestamp,
    updatedAt: timestamp,
  }
}

function buildDefaultWorkbenchState(): OfficeXWorkbenchState {
  const timestamp = nowIso()
  return {
    schemaVersion: WORKBENCH_STATE_SCHEMA_VERSION,
    activeWorkspaceId: DEFAULT_WORKSPACE_ID,
    activeThreadId: DEFAULT_THREAD_ID,
    workspaces: [
      {
        id: DEFAULT_WORKSPACE_ID,
        title: '默认工作区',
        createdAt: timestamp,
        updatedAt: timestamp,
        threads: [buildDefaultThreadState(timestamp)],
      },
    ],
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === 'string')
}

function isThreadStage(value: unknown): value is OfficeXThreadStage {
  return (
    typeof value === 'string' &&
    (VALID_THREAD_STAGES as readonly string[]).includes(value)
  )
}

function isTaskClassification(value: unknown): boolean {
  return (
    typeof value === 'string' &&
    (VALID_TASK_CLASSIFICATIONS as readonly string[]).includes(value)
  )
}

function isTaskChoiceId(value: unknown): value is OfficeXTaskChoiceId {
  return (
    typeof value === 'string' &&
    (VALID_TASK_CHOICE_IDS as readonly string[]).includes(value)
  )
}

function isBasisInputStatus(value: unknown): boolean {
  return (
    typeof value === 'string' &&
    (VALID_BASIS_INPUT_STATUSES as readonly string[]).includes(value)
  )
}

function isBasisStatusMap(value: unknown): boolean {
  if (!isRecord(value)) {
    return false
  }

  return VALID_BASIS_INPUT_IDS.every((key) => isBasisInputStatus(value[key]))
}

function isRecommendedChoice(value: unknown): boolean {
  return (
    isRecord(value) &&
    isTaskChoiceId(value.id) &&
    typeof value.label === 'string' &&
    typeof value.description === 'string'
  )
}

function isConfirmationCard(value: unknown): value is OfficeXTaskConfirmationCard {
  return (
    isRecord(value) &&
    typeof value.id === 'string' &&
    typeof value.createdAt === 'string' &&
    typeof value.requestText === 'string' &&
    typeof value.understanding === 'string' &&
    isTaskClassification(value.classification) &&
    (value.selectedChoiceId === null || isTaskChoiceId(value.selectedChoiceId)) &&
    (value.customDescription === null || typeof value.customDescription === 'string') &&
    isBasisStatusMap(value.basisStatus) &&
    typeof value.proposedFirstStep === 'string' &&
    Array.isArray(value.missingInputs) &&
    value.missingInputs.every((item) =>
      typeof item === 'string' &&
      (VALID_BASIS_INPUT_IDS as readonly string[]).includes(item),
    ) &&
    typeof value.readyToTransition === 'boolean' &&
    typeof value.summary === 'string' &&
    isTaskClassification(value.taskType) &&
    Array.isArray(value.recommendedChoices) &&
    value.recommendedChoices.every(isRecommendedChoice) &&
    isStringArray(value.basisPrompts) &&
    typeof value.nextStepSummary === 'string'
  )
}

function isTaskRecord(value: unknown): value is OfficeXThreadTaskRecord {
  return (
    isRecord(value) &&
    isTaskChoiceId(value.choiceId) &&
    isTaskClassification(value.classification) &&
    (value.customDescription === null || typeof value.customDescription === 'string') &&
    isBasisStatusMap(value.basisSnapshot) &&
    typeof value.confirmedAt === 'string'
  )
}

function isThreadState(value: unknown): value is OfficeXWorkbenchThreadState {
  return (
    isRecord(value) &&
    typeof value.id === 'string' &&
    typeof value.title === 'string' &&
    isThreadStage(value.stage) &&
    (value.openingRequest === null || typeof value.openingRequest === 'string') &&
    (value.confirmationCard === null || isConfirmationCard(value.confirmationCard)) &&
    (value.taskRecord === null || isTaskRecord(value.taskRecord)) &&
    typeof value.createdAt === 'string' &&
    typeof value.updatedAt === 'string'
  )
}

function isWorkspaceState(value: unknown): value is OfficeXWorkbenchWorkspaceState {
  return (
    isRecord(value) &&
    typeof value.id === 'string' &&
    typeof value.title === 'string' &&
    typeof value.createdAt === 'string' &&
    typeof value.updatedAt === 'string' &&
    Array.isArray(value.threads) &&
    value.threads.every(isThreadState)
  )
}

function isWorkbenchState(value: unknown): value is OfficeXWorkbenchState {
  if (
    !isRecord(value) ||
    value.schemaVersion !== WORKBENCH_STATE_SCHEMA_VERSION ||
    typeof value.activeWorkspaceId !== 'string' ||
    !(value.activeThreadId === null || typeof value.activeThreadId === 'string') ||
    !Array.isArray(value.workspaces) ||
    value.workspaces.length === 0 ||
    !value.workspaces.every(isWorkspaceState)
  ) {
    return false
  }

  const activeWorkspace = value.workspaces.find(
    (workspace) => workspace.id === value.activeWorkspaceId,
  )
  if (!activeWorkspace) {
    return false
  }

  if (value.activeThreadId === null) {
    return true
  }

  return activeWorkspace.threads.some(
    (thread) => thread.id === value.activeThreadId,
  )
}

function writeStateAtomically(
  targetPath: string,
  payload: OfficeXWorkbenchState,
): void {
  const tempPath = `${targetPath}.${process.pid}.${Date.now()}.tmp`
  fs.writeFileSync(tempPath, JSON.stringify(payload, null, 2), 'utf-8')
  fs.renameSync(tempPath, targetPath)
}

function persistWorkbenchState(
  payload: OfficeXWorkbenchState,
): OfficeXWorkbenchState {
  ensureHomeDir()
  writeStateAtomically(workbenchStatePath(), payload)
  return payload
}

function generateWorkbenchId(prefix: 'workspace' | 'thread'): string {
  return `${prefix}-${crypto.randomUUID()}`
}

function findWorkspace(
  state: OfficeXWorkbenchState,
  workspaceId: string,
): OfficeXWorkbenchWorkspaceState {
  const workspace = state.workspaces.find((candidate) => candidate.id === workspaceId)
  if (!workspace) {
    throw new Error(`Unknown workspace: ${workspaceId}`)
  }
  return workspace
}

function findThreadAcrossWorkspaces(
  state: OfficeXWorkbenchState,
  threadId: string,
): {
  workspace: OfficeXWorkbenchWorkspaceState
  thread: OfficeXWorkbenchThreadState
} {
  for (const workspace of state.workspaces) {
    const thread = workspace.threads.find((candidate) => candidate.id === threadId)
    if (thread) {
      return { workspace, thread }
    }
  }

  throw new Error(`Unknown thread: ${threadId}`)
}

function buildTaskRecord(
  choiceId: OfficeXTaskChoiceId,
  confirmationCard: OfficeXTaskConfirmationCard,
): OfficeXThreadTaskRecord {
  return {
    choiceId,
    classification: confirmationCard.classification,
    customDescription: confirmationCard.customDescription,
    basisSnapshot: {
      ...confirmationCard.basisStatus,
    },
    confirmedAt: nowIso(),
  }
}

export function loadWorkbenchState(): OfficeXWorkbenchState {
  ensureHomeDir()
  const targetPath = workbenchStatePath()
  if (!fs.existsSync(targetPath)) {
    const defaults = buildDefaultWorkbenchState()
    return persistWorkbenchState(defaults)
  }

  try {
    const raw = fs.readFileSync(targetPath, 'utf-8')
    const payload = JSON.parse(raw) as unknown
    if (isWorkbenchState(payload)) {
      return payload
    }

    const defaults = buildDefaultWorkbenchState()
    return persistWorkbenchState(defaults)
  } catch {
    const defaults = buildDefaultWorkbenchState()
    return persistWorkbenchState(defaults)
  }
}

export function createWorkspace(title: string): OfficeXWorkbenchState {
  const state = loadWorkbenchState()
  const timestamp = nowIso()
  const workspace: OfficeXWorkbenchWorkspaceState = {
    id: generateWorkbenchId('workspace'),
    title,
    createdAt: timestamp,
    updatedAt: timestamp,
    threads: [],
  }

  state.workspaces.push(workspace)
  state.activeWorkspaceId = workspace.id
  state.activeThreadId = null
  return persistWorkbenchState(state)
}

export function createThread(
  workspaceId: string,
  title: string,
): OfficeXWorkbenchState {
  const state = loadWorkbenchState()
  const workspace = findWorkspace(state, workspaceId)
  const timestamp = nowIso()
  const thread: OfficeXWorkbenchThreadState = {
    id: generateWorkbenchId('thread'),
    title,
    stage: 'intake',
    openingRequest: null,
    confirmationCard: null,
    taskRecord: null,
    createdAt: timestamp,
    updatedAt: timestamp,
  }

  workspace.threads.push(thread)
  workspace.updatedAt = timestamp
  state.activeWorkspaceId = workspaceId
  state.activeThreadId = thread.id
  return persistWorkbenchState(state)
}

export function saveTaskConfirmationCard(
  threadId: string,
  openingRequest: string,
  confirmationCard: OfficeXTaskConfirmationCard,
): OfficeXWorkbenchState {
  const state = loadWorkbenchState()
  const { workspace, thread } = findThreadAcrossWorkspaces(state, threadId)
  const timestamp = nowIso()

  thread.stage = 'awaiting_confirmation'
  thread.openingRequest = openingRequest
  thread.confirmationCard = {
    ...confirmationCard,
  }
  thread.taskRecord = null
  thread.updatedAt = timestamp
  workspace.updatedAt = timestamp
  state.activeWorkspaceId = workspace.id
  state.activeThreadId = thread.id
  return persistWorkbenchState(state)
}

export function confirmTaskCard(
  workspaceId: string,
  threadId: string,
  choiceId: OfficeXTaskChoiceId,
): OfficeXWorkbenchState {
  const state = loadWorkbenchState()
  const workspace = findWorkspace(state, workspaceId)
  const thread = workspace.threads.find((candidate) => candidate.id === threadId)
  if (!thread) {
    throw new Error(`Unknown thread ${threadId} in workspace ${workspaceId}`)
  }
  if (!thread.confirmationCard) {
    throw new Error(`Thread ${threadId} has no confirmation card to confirm`)
  }
  if (
    choiceId !== 'custom' &&
    !thread.confirmationCard.recommendedChoices.some(
      (choice) => choice.id === choiceId,
    )
  ) {
    throw new Error(`Requested choice ${choiceId} is not available for thread ${threadId}`)
  }

  const timestamp = nowIso()
  thread.confirmationCard = {
    ...thread.confirmationCard,
    selectedChoiceId: choiceId,
  }
  thread.stage = 'workbench'
  thread.taskRecord = buildTaskRecord(choiceId, thread.confirmationCard)
  thread.updatedAt = timestamp
  workspace.updatedAt = timestamp
  state.activeWorkspaceId = workspaceId
  state.activeThreadId = threadId
  return persistWorkbenchState(state)
}

export function selectThread(
  workspaceId: string,
  threadId: string,
): OfficeXWorkbenchState {
  const state = loadWorkbenchState()
  const workspace = findWorkspace(state, workspaceId)
  const threadExists = workspace.threads.some((candidate) => candidate.id === threadId)
  if (!threadExists) {
    throw new Error(`Unknown thread ${threadId} in workspace ${workspaceId}`)
  }

  state.activeWorkspaceId = workspaceId
  state.activeThreadId = threadId
  return persistWorkbenchState(state)
}
