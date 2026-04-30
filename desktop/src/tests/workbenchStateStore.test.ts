import { afterAll, beforeEach, describe, expect, it } from 'bun:test'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

import type { OfficeXTaskConfirmationCard } from '../shared/types'

const settingsDir = fs.mkdtempSync(path.join(os.tmpdir(), 'officex-workbench-state-'))
const previousSettingsDir = process.env.OFFICEX_SETTINGS_DIR
process.env.OFFICEX_SETTINGS_DIR = settingsDir

const { buildDesktopBootstrap, resolveOfficeXHomePath } = await import('../main/actionPlans')

const workbenchStateStoreModule: Record<string, unknown> = await import(
  '../main/workbenchStateStore',
).catch(() => ({}))

const loadWorkbenchState = workbenchStateStoreModule.loadWorkbenchState as
  | undefined
  | (() => {
      schemaVersion: string
      activeWorkspaceId: string
      activeThreadId: string | null
      workspaces: Array<{
        id: string
        title: string
        createdAt: string
        updatedAt: string
        threads: Array<{
          id: string
          title: string
          stage: string
          openingRequest: string | null
          confirmationCard: unknown
          taskRecord: unknown
          createdAt: string
          updatedAt: string
        }>
      }>
    })
const createWorkspace = workbenchStateStoreModule.createWorkspace as
  | undefined
  | ((title: string) => {
      activeWorkspaceId: string
      activeThreadId: string | null
      workspaces: Array<{
        id: string
        title: string
        threads: Array<{ id: string; title: string; stage: string }>
      }>
    })
const createThread = workbenchStateStoreModule.createThread as
  | undefined
  | ((workspaceId: string, title: string) => {
      activeWorkspaceId: string
      activeThreadId: string | null
      workspaces: Array<{
        id: string
        title: string
        threads: Array<{
          id: string
          title: string
          stage: string
          openingRequest: string | null
          confirmationCard: unknown
          taskRecord: unknown
        }>
      }>
    })
const saveTaskConfirmationCard = workbenchStateStoreModule.saveTaskConfirmationCard as
  | undefined
  | ((threadId: string, openingRequest: string, confirmationCard: OfficeXTaskConfirmationCard) => {
      workspaces: Array<{
        id: string
        title: string
        threads: Array<{
          id: string
          title: string
          stage: string
          openingRequest: string | null
          confirmationCard: OfficeXTaskConfirmationCard | null
          taskRecord: unknown
        }>
      }>
    })
const confirmTaskCard = workbenchStateStoreModule.confirmTaskCard as
  | undefined
  | ((workspaceId: string, threadId: string, choiceId: string) => {
      activeWorkspaceId: string
      activeThreadId: string | null
      workspaces: Array<{
        id: string
        title: string
        threads: Array<{
          id: string
          title: string
          stage: string
          openingRequest: string | null
          confirmationCard: OfficeXTaskConfirmationCard | null
          taskRecord: {
            choiceId: string
            classification: string
            customDescription: string | null
            basisSnapshot: Record<string, string>
            confirmedAt: string
          } | null
        }>
      }>
    })
const selectThread = workbenchStateStoreModule.selectThread as
  | undefined
  | ((workspaceId: string, threadId: string) => {
      activeWorkspaceId: string
      activeThreadId: string | null
    })

function workbenchStatePath(): string {
  return path.join(resolveOfficeXHomePath(), 'workbench-state.json')
}

function writeWorkbenchState(payload: unknown): void {
  fs.mkdirSync(resolveOfficeXHomePath(), { recursive: true })
  fs.writeFileSync(workbenchStatePath(), JSON.stringify(payload, null, 2), 'utf-8')
}

function resetOfficeXHome(): void {
  fs.rmSync(resolveOfficeXHomePath(), { recursive: true, force: true })
}

function buildConfirmationCard(
  overrides: Partial<OfficeXTaskConfirmationCard> = {},
): OfficeXTaskConfirmationCard {
  return {
    id: 'card-001',
    createdAt: '2026-04-21T08:00:00.000Z',
    requestText: 'Review the source document and identify gaps.',
    understanding: 'You want a structured review before any edits happen.',
    classification: 'review',
    selectedChoiceId: null,
    customDescription: null,
    basisStatus: {
      template: 'present',
      writing_requirements: 'missing',
      review_rubric: 'optional',
      source_document: 'present',
    },
    proposedFirstStep: 'Inspect the source document and summarize the review scope.',
    missingInputs: ['writing_requirements'],
    readyToTransition: true,
    summary: 'Review the current document against the available basis inputs.',
    taskType: 'review',
    recommendedChoices: [
      {
        id: 'review',
        label: 'Review',
        description: 'Audit the current document before changing content.',
      },
    ],
    basisPrompts: ['Please provide the detailed writing requirements if available.'],
    nextStepSummary: 'Enter the workbench and start a review-focused task.',
    ...overrides,
  }
}

function readThread(workspaceId: string, threadId: string) {
  const state = loadWorkbenchState!()
  const workspace = state.workspaces.find((candidate) => candidate.id === workspaceId)
  return workspace?.threads.find((candidate) => candidate.id === threadId) ?? null
}

beforeEach(() => {
  process.env.OFFICEX_SETTINGS_DIR = settingsDir
  resetOfficeXHome()
})

afterAll(() => {
  fs.rmSync(settingsDir, { recursive: true, force: true })
  if (previousSettingsDir === undefined) {
    delete process.env.OFFICEX_SETTINGS_DIR
  } else {
    process.env.OFFICEX_SETTINGS_DIR = previousSettingsDir
  }
})

describe('workbenchStateStore', () => {
  it('first load seeds one default workspace titled 默认工作区 and one default thread titled 新线程', () => {
    expect(typeof loadWorkbenchState).toBe('function')

    const state = loadWorkbenchState!()

    expect(state.schemaVersion).toBe('workbench-state-v1')
    expect(state.activeWorkspaceId).toBe('default-workspace')
    expect(state.activeThreadId).toBe('default-thread')
    expect(state.workspaces).toHaveLength(1)
    expect(state.workspaces[0]).toMatchObject({
      id: 'default-workspace',
      title: '默认工作区',
    })
    expect(state.workspaces[0]?.threads).toHaveLength(1)
    expect(state.workspaces[0]?.threads[0]).toMatchObject({
      id: 'default-thread',
      title: '新线程',
      stage: 'intake',
      openingRequest: null,
      confirmationCard: null,
      taskRecord: null,
    })
    expect(fs.existsSync(workbenchStatePath())).toBe(true)
  })

  it('buildDesktopBootstrap(repoRoot) restores persisted workbench navigation instead of temporary defaults', () => {
    writeWorkbenchState({
      schemaVersion: 'workbench-state-v1',
      activeWorkspaceId: 'workspace-alpha',
      activeThreadId: 'thread-beta',
      workspaces: [
        {
          id: 'default-workspace',
          title: '默认工作区',
          createdAt: '2026-04-21T08:00:00.000Z',
          updatedAt: '2026-04-21T08:00:00.000Z',
          threads: [
            {
              id: 'default-thread',
              title: '新线程',
              stage: 'intake',
              openingRequest: null,
              confirmationCard: null,
              taskRecord: null,
              createdAt: '2026-04-21T08:00:00.000Z',
              updatedAt: '2026-04-21T08:00:00.000Z',
            },
          ],
        },
        {
          id: 'workspace-alpha',
          title: '项目工作区',
          createdAt: '2026-04-21T09:00:00.000Z',
          updatedAt: '2026-04-21T09:15:00.000Z',
          threads: [
            {
              id: 'thread-beta',
              title: '需求澄清',
              stage: 'workbench',
              openingRequest: 'Please inspect the current source and move into the workbench.',
              confirmationCard: null,
              taskRecord: {
                choiceId: 'review',
                classification: 'review',
                customDescription: null,
                basisSnapshot: {
                  template: 'present',
                  writing_requirements: 'missing',
                  review_rubric: 'optional',
                  source_document: 'present',
                },
                confirmedAt: '2026-04-21T09:10:00.000Z',
              },
              createdAt: '2026-04-21T09:00:00.000Z',
              updatedAt: '2026-04-21T09:10:00.000Z',
            },
          ],
        },
      ],
    })

    const bootstrap = buildDesktopBootstrap(settingsDir)

    expect(bootstrap.navigation.workspaces).toEqual([
      {
        id: 'default-workspace',
        title: '默认工作区',
        threadCount: 1,
        archivedThreadCount: 0,
      },
      {
        id: 'workspace-alpha',
        title: '项目工作区',
        threadCount: 1,
        archivedThreadCount: 0,
      },
    ])
    expect(bootstrap.navigation.activeWorkspaceId).toBe('workspace-alpha')
    expect(bootstrap.navigation.activeThreadId).toBe('thread-beta')
    expect(bootstrap.navigation.threads).toEqual([
      {
        id: 'thread-beta',
        title: '需求澄清',
        stage: 'workbench',
        openingRequest: 'Please inspect the current source and move into the workbench.',
        confirmationCard: null,
        taskRecord: {
          choiceId: 'review',
          classification: 'review',
          customDescription: null,
          basisSnapshot: {
            template: 'present',
            writing_requirements: 'missing',
            review_rubric: 'optional',
            source_document: 'present',
          },
          confirmedAt: '2026-04-21T09:10:00.000Z',
        },
      },
    ])
    expect(bootstrap.shell.mode).toBe('workbench')
  })

  it('parseable but structurally invalid workbench-state.json recovers to seeded defaults instead of crashing bootstrap', () => {
    writeWorkbenchState({
      schemaVersion: 'workbench-state-v1',
      activeWorkspaceId: 'broken-workspace',
      activeThreadId: 'broken-thread',
      workspaces: 'not-an-array',
    })

    const state = loadWorkbenchState!()
    const bootstrap = buildDesktopBootstrap(settingsDir)
    const persistedState = JSON.parse(
      fs.readFileSync(workbenchStatePath(), 'utf-8'),
    ) as Record<string, unknown>

    expect(state).toMatchObject({
      schemaVersion: 'workbench-state-v1',
      activeWorkspaceId: 'default-workspace',
      activeThreadId: 'default-thread',
    })
    expect(state.workspaces).toHaveLength(1)
    expect(state.workspaces[0]).toMatchObject({
      id: 'default-workspace',
      title: '默认工作区',
    })
    expect(state.workspaces[0]?.threads).toHaveLength(1)
    expect(state.workspaces[0]?.threads[0]).toMatchObject({
      id: 'default-thread',
      title: '新线程',
      stage: 'intake',
    })
    expect(bootstrap.navigation).toEqual({
      workspaces: [
        {
          id: 'default-workspace',
          title: '默认工作区',
          threadCount: 1,
          archivedThreadCount: 0,
        },
      ],
      activeWorkspaceId: 'default-workspace',
      activeThreadId: 'default-thread',
      threads: [
        {
          id: 'default-thread',
          title: '新线程',
          stage: 'intake',
          openingRequest: null,
          confirmationCard: null,
          taskRecord: null,
        },
      ],
    })
    expect(persistedState).toMatchObject({
      schemaVersion: 'workbench-state-v1',
      activeWorkspaceId: 'default-workspace',
      activeThreadId: 'default-thread',
    })
  })

  it('createWorkspace(title) persists a workspace and updates activeWorkspaceId', () => {
    expect(typeof createWorkspace).toBe('function')

    const state = createWorkspace!('项目工作区')
    const createdWorkspace = state.workspaces.find(
      (workspace) => workspace.id === state.activeWorkspaceId,
    )
    const reloadedState = loadWorkbenchState!()

    expect(state.activeWorkspaceId).not.toBe('default-workspace')
    expect(createdWorkspace).toMatchObject({
      title: '项目工作区',
      threads: [],
    })
    expect(reloadedState.activeWorkspaceId).toBe(state.activeWorkspaceId)
    expect(
      reloadedState.workspaces.some(
        (workspace) =>
          workspace.id === state.activeWorkspaceId &&
          workspace.title === '项目工作区',
      ),
    ).toBe(true)
  })

  it('createThread(workspaceId, title) persists a thread with stage intake and updates activeThreadId', () => {
    expect(typeof createWorkspace).toBe('function')
    expect(typeof createThread).toBe('function')

    const workspaceState = createWorkspace!('线程工作区')
    const workspaceId = workspaceState.activeWorkspaceId
    const state = createThread!(workspaceId, '需求澄清')
    const createdWorkspace = state.workspaces.find((workspace) => workspace.id === workspaceId)
    const createdThread = createdWorkspace?.threads.find(
      (thread) => thread.id === state.activeThreadId,
    )
    const reloadedThread = readThread(workspaceId, state.activeThreadId!)

    expect(state.activeWorkspaceId).toBe(workspaceId)
    expect(state.activeThreadId).toBeTruthy()
    expect(createdThread).toMatchObject({
      title: '需求澄清',
      stage: 'intake',
      openingRequest: null,
      confirmationCard: null,
      taskRecord: null,
    })
    expect(reloadedThread).toMatchObject({
      id: state.activeThreadId,
      title: '需求澄清',
      stage: 'intake',
    })
  })

  it('saveTaskConfirmationCard(threadId, openingRequest, confirmationCard) persists confirmationCard and stage awaiting_confirmation', () => {
    expect(typeof saveTaskConfirmationCard).toBe('function')

    const confirmationCard = buildConfirmationCard()
    const openingRequest = 'Please review this candidate before we edit it.'
    const state = saveTaskConfirmationCard!(
      'default-thread',
      openingRequest,
      confirmationCard,
    )
    const persistedThread = readThread('default-workspace', 'default-thread')

    expect(
      state.workspaces[0]?.threads.find((thread) => thread.id === 'default-thread'),
    ).toMatchObject({
      stage: 'awaiting_confirmation',
      openingRequest,
      confirmationCard: expect.objectContaining({
        id: confirmationCard.id,
        classification: confirmationCard.classification,
        selectedChoiceId: null,
      }),
      taskRecord: null,
    })
    expect(persistedThread).toMatchObject({
      id: 'default-thread',
      stage: 'awaiting_confirmation',
      openingRequest,
      confirmationCard: expect.objectContaining({
        id: confirmationCard.id,
        understanding: confirmationCard.understanding,
      }),
    })
  })

  it('confirmTaskCard(workspaceId, threadId, choiceId) moves only the thread to stage workbench and creates taskRecord', () => {
    expect(typeof createThread).toBe('function')
    expect(typeof saveTaskConfirmationCard).toBe('function')
    expect(typeof confirmTaskCard).toBe('function')
    expect(typeof selectThread).toBe('function')

    const extraThreadState = createThread!('default-workspace', '旁路线程')
    const untouchedThreadId = extraThreadState.activeThreadId!
    selectThread!('default-workspace', 'default-thread')
    saveTaskConfirmationCard!(
      'default-thread',
      'Review this source and confirm the task path.',
      buildConfirmationCard(),
    )

    const state = confirmTaskCard!('default-workspace', 'default-thread', 'review')
    const targetThread = readThread('default-workspace', 'default-thread')
    const untouchedThread = readThread('default-workspace', untouchedThreadId)
    const targetConfirmedAt =
      targetThread?.taskRecord &&
      typeof targetThread.taskRecord === 'object' &&
      'confirmedAt' in targetThread.taskRecord
        ? (targetThread.taskRecord as { confirmedAt?: string }).confirmedAt
        : null

    expect(state.activeWorkspaceId).toBe('default-workspace')
    expect(state.activeThreadId).toBe('default-thread')
    expect(targetThread).toMatchObject({
      id: 'default-thread',
      stage: 'workbench',
      confirmationCard: expect.objectContaining({
        selectedChoiceId: 'review',
      }),
      taskRecord: expect.objectContaining({
        choiceId: 'review',
        classification: 'review',
        customDescription: null,
        basisSnapshot: {
          template: 'present',
          writing_requirements: 'missing',
          review_rubric: 'optional',
          source_document: 'present',
        },
      }),
    })
    expect(targetConfirmedAt).toContain('T')
    expect(untouchedThread).toMatchObject({
      id: untouchedThreadId,
      title: '旁路线程',
      stage: 'intake',
      taskRecord: null,
    })
  })

  it('confirmTaskCard(workspaceId, threadId, choiceId) rejects a non-custom choice that is not in recommendedChoices', () => {
    expect(typeof saveTaskConfirmationCard).toBe('function')
    expect(typeof confirmTaskCard).toBe('function')

    saveTaskConfirmationCard!(
      'default-thread',
      'Review this source and confirm the task path.',
      buildConfirmationCard(),
    )

    expect(() =>
      confirmTaskCard!('default-workspace', 'default-thread', 'rewrite'),
    ).toThrow('not available')

    const targetThread = readThread('default-workspace', 'default-thread')

    expect(targetThread).toMatchObject({
      id: 'default-thread',
      stage: 'awaiting_confirmation',
      confirmationCard: expect.objectContaining({
        selectedChoiceId: null,
      }),
      taskRecord: null,
    })
  })
})
