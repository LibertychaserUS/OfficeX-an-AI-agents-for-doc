# OfficeX Frontstage Workbench MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current readiness-first desktop shell with an intake-first three-column OfficeX workbench that keeps `doctor`, `render-boundary`, and `run-docx-mvp` behavior unchanged.

**Architecture:** Extend the desktop bootstrap with workbench navigation and chat-control state, persist workspace/thread metadata in a machine-local store under the OfficeX home directory, add a deterministic task-confirmation-card mapper in the Electron main process, and refactor the React renderer into a left-navigation / center-surface / right-chat workbench. Python runtime routing and product-entry commands stay unchanged.

**Tech Stack:** Electron, React 19, TypeScript, Bun test, machine-local JSON state files under `~/Library/Application Support/OfficeX`, existing Python product-entry runtime

---

## File Map

### Product contracts and bootstrap

- Modify: `desktop/src/shared/types.ts`
  - Extend desktop bootstrap and IPC contracts for workbench navigation, chat controls, and task confirmation cards.
- Modify: `desktop/src/main/actionPlans.ts`
  - Keep runtime action planning unchanged, but reshape bootstrap generation so the renderer receives workbench-first state instead of only readiness cards.

### Machine-local state

- Create: `desktop/src/main/workbenchStateStore.ts`
  - Persist and load workspace/thread state separately from `settings.json`.
- Modify: `desktop/src/main/settingsStore.ts`
  - Keep settings narrowly machine-local and separate from workbench thread state.

### Intake mapping and IPC

- Create: `desktop/src/main/taskIntake.ts`
  - Deterministically classify the first user request and build the task confirmation card.
- Modify: `desktop/src/main/index.ts`
  - Add IPC handlers for workspace/thread creation, selection, and intake submission.
- Modify: `desktop/src/preload/index.ts`
  - Expose the new bounded desktop bridge methods.

### Renderer

- Modify: `desktop/src/renderer/src/App.tsx`
  - Replace the current single-screen readiness UI with a workbench shell.
- Create: `desktop/src/renderer/src/components/WorkbenchSidebar.tsx`
  - Render workspaces, threads, and create-thread controls.
- Create: `desktop/src/renderer/src/components/WorkbenchCenter.tsx`
  - Render the empty intake state now and host the document surface later.
- Create: `desktop/src/renderer/src/components/ChatDock.tsx`
  - Render chat history, chat controls, intake composer, and utility actions.
- Create: `desktop/src/renderer/src/components/TaskConfirmationCardView.tsx`
  - Render the confirmation card sections and task-type choices.
- Create: `desktop/src/renderer/src/components/RunArtifactsPanel.tsx`
  - Render execution summaries, artifacts, and open-path buttons without collapsing back to the old home screen.
- Modify: `desktop/src/renderer/src/styles.css`
  - Add the three-column workbench layout and intake-first visual hierarchy.

### Tests

- Create: `desktop/src/tests/workbenchBootstrap.test.ts`
  - Verify default workbench bootstrap shape.
- Create: `desktop/src/tests/workbenchStateStore.test.ts`
  - Verify machine-local workspace/thread persistence and atomic writes.
- Create: `desktop/src/tests/taskIntake.test.ts`
  - Verify deterministic task-card classification and basis prompts.
- Create: `desktop/src/tests/rendererMarkup.test.tsx`
  - Verify renderer markup for empty intake state, confirmation card, and utility actions using `renderToStaticMarkup`.
- Modify: `desktop/src/tests/actionPlans.test.ts`
  - Keep runtime-plan assertions while updating bootstrap expectations.
- Modify: `desktop/src/tests/settingsStore.test.ts`
  - Keep settings isolated from new workbench state.

### Docs and trace

- Modify: `docs/ARCHITECTURE.md`
  - Change the app-surface description from readiness-first shell to intake-first workbench.
- Modify: `docs/blueprints/DESKTOP_RUNTIME_CONTRACT.md`
  - Record the frontstage transition from MVP launcher to workbench shell.
- Add: `trace/CHECKPOINT_26.md`
  - Record the frontstage-workbench transition.
- Modify: `trace/CURRENT_STATE.md`
  - Update the desktop-shell posture.
- Modify: `trace/SESSION_LOG.md`
  - Append the implementation session outcome.

## Task 1: Extend Desktop Contracts For The Workbench Shell

**Files:**
- Create: `desktop/src/tests/workbenchBootstrap.test.ts`
- Modify: `desktop/src/shared/types.ts`
- Modify: `desktop/src/main/actionPlans.ts`
- Modify: `desktop/src/tests/actionPlans.test.ts`

- [ ] **Step 1: Write the failing bootstrap-shape test**

```ts
import { afterAll, beforeEach, describe, expect, it } from 'bun:test'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

const settingsDir = fs.mkdtempSync(path.join(os.tmpdir(), 'officex-workbench-bootstrap-'))
const previousSettingsDir = process.env.OFFICEX_SETTINGS_DIR
process.env.OFFICEX_SETTINGS_DIR = settingsDir

const {
  buildDesktopBootstrap,
  resolveOfficeXHomePath,
} = await import('../main/actionPlans')

function makeRepoFixture(): string {
  const repoRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'officex-workbench-repo-'))
  const pythonBinDir = path.join(repoRoot, '.venv', 'bin')
  fs.mkdirSync(pythonBinDir, { recursive: true })
  fs.writeFileSync(path.join(pythonBinDir, 'python'), '#!/usr/bin/env python3\n', 'utf-8')
  return repoRoot
}

describe('buildDesktopBootstrap workbench shell', () => {
  beforeEach(() => {
    fs.rmSync(resolveOfficeXHomePath(), { recursive: true, force: true })
  })

  afterAll(() => {
    fs.rmSync(settingsDir, { recursive: true, force: true })
    if (previousSettingsDir === undefined) {
      delete process.env.OFFICEX_SETTINGS_DIR
    } else {
      process.env.OFFICEX_SETTINGS_DIR = previousSettingsDir
    }
  })

  it('returns an intake-first workbench bootstrap with default workspace and thread state', () => {
    const bootstrap = buildDesktopBootstrap(makeRepoFixture())

    expect(bootstrap.shell.mode).toBe('intake')
    expect(bootstrap.navigation.workspaces).toHaveLength(1)
    expect(bootstrap.navigation.workspaces[0]?.title).toBe('默认工作区')
    expect(bootstrap.navigation.threads).toHaveLength(1)
    expect(bootstrap.navigation.threads[0]?.title).toBe('新线程')
    expect(bootstrap.navigation.threads[0]?.stage).toBe('intake')
    expect(bootstrap.navigation.threads[0]?.confirmationCard).toBeNull()
    expect(bootstrap.chatControls.placeholder).toContain('今天想要处理什么')
    expect(bootstrap.chatControls.models.map((item) => item.id)).toEqual([
      'gpt-5.4',
      'gpt-5.4-mini',
    ])
    expect(bootstrap.utilityActions.map((item) => item.id)).toEqual([
      'doctor',
      'render-boundary',
      'run-docx-demo',
    ])
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/nihao/Documents/Playground/document-ops-system/desktop && bun test src/tests/workbenchBootstrap.test.ts`

Expected: FAIL because `shell`, `navigation`, `chatControls`, and `utilityActions` are missing from `OfficeXDesktopBootstrap`.

- [ ] **Step 3: Add the new shared desktop contract types**

```ts
export interface OfficeXModelChoice {
  id: string
  label: string
}

export interface OfficeXReasoningChoice {
  id: 'low' | 'medium' | 'high'
  label: string
}

export interface OfficeXTaskChoice {
  id: 'draft' | 'modify' | 'review' | 'rewrite' | 'repair' | 'custom'
  label: string
  description: string
}

export type OfficeXThreadStage =
  | 'intake'
  | 'awaiting_confirmation'
  | 'workbench'
  | 'archived'

export type OfficeXTaskClassification =
  | 'generation'
  | 'modification'
  | 'review'
  | 'rewrite'
  | 'repair'
  | 'mixed'

export type OfficeXTaskChoiceId =
  | 'draft'
  | 'modify'
  | 'review'
  | 'rewrite'
  | 'repair'
  | 'custom'

export type OfficeXBasisInputId =
  | 'template'
  | 'writing_requirements'
  | 'review_rubric'
  | 'source_document'

export type OfficeXBasisInputStatus = 'present' | 'missing' | 'optional'

export interface OfficeXTaskConfirmationCard {
  id: string
  createdAt: string
  requestText: string
  understanding: string
  classification: OfficeXTaskClassification
  selectedChoiceId: OfficeXTaskChoiceId | null
  customDescription: string | null
  basisStatus: Record<OfficeXBasisInputId, OfficeXBasisInputStatus>
  proposedFirstStep: string
  missingInputs: OfficeXBasisInputId[]
  readyToTransition: boolean
  summary: string
  taskType: OfficeXTaskClassification
  recommendedChoices: OfficeXTaskChoice[]
  basisPrompts: string[]
  nextStepSummary: string
}

export interface OfficeXThreadTaskRecord {
  choiceId: OfficeXTaskChoiceId
  classification: OfficeXTaskClassification
  customDescription: string | null
  basisSnapshot: Record<OfficeXBasisInputId, OfficeXBasisInputStatus>
  confirmedAt: string
}

export interface OfficeXThreadSummary {
  id: string
  title: string
  stage: OfficeXThreadStage
  openingRequest: string | null
  confirmationCard: OfficeXTaskConfirmationCard | null
  taskRecord: OfficeXThreadTaskRecord | null
}

export interface OfficeXWorkspaceSummary {
  id: string
  title: string
  threadCount: number
  archivedThreadCount: number
}

export interface OfficeXWorkbenchNavigation {
  workspaces: OfficeXWorkspaceSummary[]
  activeWorkspaceId: string
  activeThreadId: string | null
  threads: OfficeXThreadSummary[]
}

export interface OfficeXChatControls {
  placeholder: string
  models: OfficeXModelChoice[]
  selectedModelId: string
  reasoningChoices: OfficeXReasoningChoice[]
  selectedReasoningId: 'low' | 'medium' | 'high'
  voiceInputEnabled: boolean
}

export interface OfficeXWorkbenchShell {
  mode: 'intake' | 'workbench'
  headline: string
}

export interface OfficeXDesktopBootstrap {
  schemaVersion: string
  homePath: string
  repoRoot: string
  primaryHeadline: string
  primaryActionId: OfficeXActionId
  runtime: OfficeXRuntimeStatus
  settings: OfficeXUserSettings
  actions: OfficeXDesktopActionSummary[]
  shell: OfficeXWorkbenchShell
  navigation: OfficeXWorkbenchNavigation
  chatControls: OfficeXChatControls
  utilityActions: OfficeXDesktopActionSummary[]
}
```

- [ ] **Step 4: Return the new bootstrap shape from `actionPlans.ts`**

```ts
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

export function buildDesktopBootstrap(
  repoRoot: string,
  settings: OfficeXUserSettings = buildDefaultSettings(),
): OfficeXDesktopBootstrap {
  const runtime = buildRuntimeStatus(repoRoot, settings)
  const actions = buildAvailableActions()
  const workbench = loadWorkbenchState()
  const activeWorkspace =
    workbench.workspaces.find((workspace) => workspace.id === workbench.activeWorkspaceId) ??
    workbench.workspaces[0] ??
    null
  const activeThread =
    activeWorkspace?.threads.find((thread) => thread.id === workbench.activeThreadId) ?? null

  return {
    schemaVersion: DESKTOP_BOOTSTRAP_SCHEMA_VERSION,
    homePath: resolveOfficeXHomePath(),
    repoRoot,
    primaryHeadline: activeThread?.confirmationCard
      ? '继续当前文档任务'
      : '先描述你今天想处理的文档任务',
    primaryActionId: runtime.ready ? 'run-docx-demo' : 'doctor',
    runtime,
    settings,
    actions,
    shell: {
      mode: activeThread?.stage === 'workbench' ? 'workbench' : 'intake',
      headline: activeThread?.confirmationCard
        ? '文档工作台'
        : '从任务开始，而不是从编辑器开始',
    },
    navigation: {
      workspaces: workbench.workspaces.map(toWorkspaceSummary),
      activeWorkspaceId: workbench.activeWorkspaceId,
      activeThreadId: activeThread?.id ?? null,
      threads: activeWorkspace?.threads.map(toThreadSummary) ?? [],
    },
    chatControls: buildChatControls(),
    utilityActions: actions,
  }
}
```

- [ ] **Step 5: Update old bootstrap assertions and run the tests**

```ts
expect(bootstrap.primaryActionId).toBe('doctor')
expect(bootstrap.shell.mode).toBe('intake')
expect(bootstrap.utilityActions).toHaveLength(3)
expect(bootstrap.navigation.threads[0]?.stage).toBe('intake')
```

Run: `cd /Users/nihao/Documents/Playground/document-ops-system/desktop && bun test src/tests/workbenchBootstrap.test.ts src/tests/actionPlans.test.ts`

Expected: PASS

- [ ] **Step 6: Commit**

```bash
cd /Users/nihao/Documents/Playground/document-ops-system
git add desktop/src/shared/types.ts desktop/src/main/actionPlans.ts desktop/src/tests/workbenchBootstrap.test.ts desktop/src/tests/actionPlans.test.ts
git commit -m "feat: add workbench bootstrap contracts"
```

## Task 2: Add Machine-Local Workspace And Thread Persistence

**Files:**
- Create: `desktop/src/main/workbenchStateStore.ts`
- Create: `desktop/src/tests/workbenchStateStore.test.ts`
- Modify: `desktop/src/main/actionPlans.ts`
- Modify: `desktop/src/tests/settingsStore.test.ts`

- [ ] **Step 1: Write the failing store test**

```ts
import { afterAll, beforeEach, describe, expect, it } from 'bun:test'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'

const settingsDir = fs.mkdtempSync(path.join(os.tmpdir(), 'officex-workbench-store-'))
const previousSettingsDir = process.env.OFFICEX_SETTINGS_DIR
process.env.OFFICEX_SETTINGS_DIR = settingsDir

const {
  loadWorkbenchState,
  createWorkspace,
  createThread,
  selectThread,
  saveTaskConfirmationCard,
  confirmTaskCard,
  workbenchStatePath,
} = await import('../main/workbenchStateStore')

describe('workbenchStateStore', () => {
  beforeEach(() => {
    fs.rmSync(settingsDir, { recursive: true, force: true })
    fs.mkdirSync(settingsDir, { recursive: true })
    process.env.OFFICEX_SETTINGS_DIR = settingsDir
  })

  afterAll(() => {
    fs.rmSync(settingsDir, { recursive: true, force: true })
    if (previousSettingsDir === undefined) {
      delete process.env.OFFICEX_SETTINGS_DIR
    } else {
      process.env.OFFICEX_SETTINGS_DIR = previousSettingsDir
    }
  })

  it('seeds one default workspace and one default thread on first load', () => {
    const state = loadWorkbenchState()

    expect(state.workspaces).toHaveLength(1)
    expect(state.workspaces[0]?.title).toBe('默认工作区')
    expect(state.workspaces[0]?.threads).toHaveLength(1)
    expect(state.activeWorkspaceId).toBe(state.workspaces[0]?.id)
    expect(state.workspaces[0]?.threads[0]?.title).toBe('新线程')
  })

  it('persists workspace, thread, confirmation card, and confirmation stage separately from settings', () => {
    const initial = loadWorkbenchState()
    const workspace = createWorkspace('课程项目')
    const created = createThread(workspace.id, '审查线程')
    saveTaskConfirmationCard(created.id, '请按 rubric 审查', {
      id: 'card-1',
      createdAt: '2026-04-21T00:00:00.000Z',
      requestText: '请按 rubric 审查',
      understanding: '按 rubric 审查当前文档',
      classification: 'review',
      selectedChoiceId: 'review',
      customDescription: null,
      basisStatus: {
        template: 'optional',
        writing_requirements: 'optional',
        review_rubric: 'missing',
        source_document: 'present',
      },
      proposedFirstStep: '先确认审查目标，再补充 rubric。',
      missingInputs: ['review_rubric'],
      readyToTransition: false,
      summary: '按 rubric 审查当前文档',
      taskType: 'review',
      recommendedChoices: [],
      basisPrompts: ['补充审核规则 / rubric'],
      nextStepSummary: '确认任务类型后，再补充 rubric。',
    })
    confirmTaskCard(workspace.id, created.id, 'review')
    const selected = selectThread(workspace.id, created.id)
    const raw = JSON.parse(fs.readFileSync(workbenchStatePath(), 'utf-8')) as Record<string, unknown>

    expect(selected.activeThreadId).toBe(created.id)
    expect(raw).toHaveProperty('workspaces')
    expect(raw).toHaveProperty('activeWorkspaceId', workspace.id)
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/nihao/Documents/Playground/document-ops-system/desktop && bun test src/tests/workbenchStateStore.test.ts`

Expected: FAIL because `workbenchStateStore.ts` does not exist yet.

- [ ] **Step 3: Implement the workbench store with atomic writes**

```ts
export interface OfficeXThreadRecord {
  id: string
  title: string
  stage: 'intake' | 'awaiting_confirmation' | 'workbench' | 'archived'
  openingRequest: string | null
  confirmationCard: OfficeXTaskConfirmationCard | null
  taskRecord: OfficeXThreadTaskRecord | null
  createdAt: string
  updatedAt: string
}

export interface OfficeXWorkspaceRecord {
  id: string
  title: string
  createdAt: string
  updatedAt: string
  threads: OfficeXThreadRecord[]
}

export interface OfficeXWorkbenchState {
  schemaVersion: 'officex-workbench-state-v1'
  activeWorkspaceId: string
  activeThreadId: string | null
  workspaces: OfficeXWorkspaceRecord[]
}

export function workbenchStatePath(): string {
  return path.join(resolveOfficeXHomePath(), 'workbench-state.json')
}

export function loadWorkbenchState(): OfficeXWorkbenchState {
  ensureHomeDir()
  if (!fs.existsSync(workbenchStatePath())) {
    const seeded = buildDefaultWorkbenchState()
    writeWorkbenchStateAtomically(seeded)
    return seeded
  }
  return parseWorkbenchState(fs.readFileSync(workbenchStatePath(), 'utf-8'))
}

export function createWorkspace(title = '默认工作区'): OfficeXWorkspaceRecord {
  const state = loadWorkbenchState()
  const nextWorkspace = buildWorkspaceRecord(title)
  const nextState = {
    ...state,
    activeWorkspaceId: nextWorkspace.id,
    workspaces: [...state.workspaces, nextWorkspace],
  }
  writeWorkbenchStateAtomically(nextState)
  return nextWorkspace
}

export function createThread(workspaceId: string, title = '新线程'): OfficeXThreadRecord {
  const state = loadWorkbenchState()
  const nextThread = buildThreadRecord(title)
  const nextState = {
    ...state,
    activeWorkspaceId: workspaceId,
    activeThreadId: nextThread.id,
    workspaces: state.workspaces.map((workspace) =>
      workspace.id === workspaceId
        ? {
            ...workspace,
            updatedAt: nextThread.updatedAt,
            threads: [...workspace.threads, nextThread],
          }
        : workspace,
    ),
  }
  writeWorkbenchStateAtomically(nextState)
  return nextThread
}

export function saveTaskConfirmationCard(
  threadId: string,
  openingRequest: string,
  confirmationCard: OfficeXTaskConfirmationCard,
): OfficeXWorkbenchState {
  const nextState = mutateThread(loadWorkbenchState(), threadId, (thread) => ({
    ...thread,
    stage: 'awaiting_confirmation',
    openingRequest,
    confirmationCard,
    updatedAt: confirmationCard.createdAt,
  }))
  writeWorkbenchStateAtomically(nextState)
  return nextState
}

export function confirmTaskCard(
  workspaceId: string,
  threadId: string,
  choiceId: OfficeXTaskChoiceId,
): OfficeXWorkbenchState {
  const nextState = mutateThread(loadWorkbenchState(), threadId, (thread) => ({
    ...thread,
    stage: 'workbench',
    taskRecord: {
      choiceId,
      classification: thread.confirmationCard?.classification ?? 'mixed',
      customDescription: thread.confirmationCard?.customDescription ?? null,
      basisSnapshot: thread.confirmationCard?.basisStatus ?? {
        template: 'optional',
        writing_requirements: 'optional',
        review_rubric: 'optional',
        source_document: 'optional',
      },
      confirmedAt: new Date().toISOString(),
    },
    updatedAt: new Date().toISOString(),
  }))
  writeWorkbenchStateAtomically(nextState)
  return selectThread(workspaceId, threadId)
}

export function selectThread(workspaceId: string, threadId: string): OfficeXWorkbenchState {
  const nextState = {
    ...loadWorkbenchState(),
    activeWorkspaceId: workspaceId,
    activeThreadId: threadId,
  }
  writeWorkbenchStateAtomically(nextState)
  return nextState
}
```

- [ ] **Step 4: Keep settings and workbench state separate**

```ts
it('does not write workbench state into settings.json', () => {
  resetSettingsHome()

  saveSettings({
    workspaceRoot: '/tmp/officex-workspace',
  })

  const raw = JSON.parse(fs.readFileSync(settingsPath(), 'utf-8')) as Record<string, unknown>

  expect(raw).toEqual({
    workspaceRoot: '/tmp/officex-workspace',
    sandboxRoot: path.join(resolveOfficeXHomePath(), 'sandboxes'),
    approvalMode: 'ask_every_conflict',
  })
  expect(raw).not.toHaveProperty('workspaces')
  expect(raw).not.toHaveProperty('activeThreadId')
})
```

- [ ] **Step 5: Run the tests**

Run: `cd /Users/nihao/Documents/Playground/document-ops-system/desktop && bun test src/tests/workbenchStateStore.test.ts src/tests/settingsStore.test.ts src/tests/workbenchBootstrap.test.ts`

Expected: PASS

- [ ] **Step 6: Commit**

```bash
cd /Users/nihao/Documents/Playground/document-ops-system
git add desktop/src/main/workbenchStateStore.ts desktop/src/tests/workbenchStateStore.test.ts desktop/src/tests/settingsStore.test.ts desktop/src/main/actionPlans.ts
git commit -m "feat: persist local officex workbench state"
```

## Task 3: Add Deterministic Task Confirmation Card Mapping

**Files:**
- Create: `desktop/src/main/taskIntake.ts`
- Create: `desktop/src/tests/taskIntake.test.ts`
- Modify: `desktop/src/shared/types.ts`
- Modify: `desktop/src/main/workbenchStateStore.ts`
- Modify: `desktop/src/main/index.ts`
- Modify: `desktop/src/preload/index.ts`

- [ ] **Step 1: Write the failing intake-classification tests**

```ts
import { describe, expect, it } from 'bun:test'

const { buildTaskConfirmationCard } = await import('../main/taskIntake')

describe('buildTaskConfirmationCard', () => {
  it('classifies review requests and highlights rubric input', () => {
    const card = buildTaskConfirmationCard('请按照学校 rubric 审查这份 docx 并指出问题')

    expect(card.taskType).toBe('review')
    expect(card.understanding).toContain('审查')
    expect(card.recommendedChoices.map((item) => item.id)).toContain('review')
    expect(card.basisPrompts).toContain('补充审核规则 / rubric')
    expect(card.readyToTransition).toBe(false)
  })

  it('classifies modification requests and highlights source-document input', () => {
    const card = buildTaskConfirmationCard('基于现有文档修改第三章的写法')

    expect(card.taskType).toBe('modification')
    expect(card.recommendedChoices[0]?.id).toBe('modify')
    expect(card.basisPrompts).toContain('提供现有基础文档')
  })

  it('falls back to custom for ambiguous requests', () => {
    const card = buildTaskConfirmationCard('帮我处理一下这个东西')

    expect(card.taskType).toBe('mixed')
    expect(card.recommendedChoices.at(-1)?.id).toBe('custom')
    expect(card.selectedChoiceId).toBeNull()
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/nihao/Documents/Playground/document-ops-system/desktop && bun test src/tests/taskIntake.test.ts`

Expected: FAIL because `taskIntake.ts` does not exist yet.

- [ ] **Step 3: Implement deterministic classification and basis prompts**

```ts
const TASK_CHOICES: OfficeXTaskChoice[] = [
  { id: 'draft', label: '起草一份新文档', description: '从零开始生成第一版内容' },
  { id: 'modify', label: '基于现有文档修改', description: '沿着已有文档做定向改写' },
  { id: 'review', label: '按 rubric 审查文档', description: '输出问题、风险和复检项' },
  { id: 'rewrite', label: '按模板重写/重排', description: '重新组织结构与章节' },
  { id: 'repair', label: '修复格式与版式', description: '优先处理样式、编号和版面' },
  { id: 'custom', label: '自定义描述', description: '由用户进一步说明特殊目标' },
]

export function buildTaskConfirmationCard(input: string): OfficeXTaskConfirmationCard {
  const normalized = input.trim()
  const lower = normalized.toLowerCase()

  const taskType =
    /审查|review|rubric|检查/.test(normalized)
      ? 'review'
      : /修改|改写|update|revise/.test(normalized)
        ? 'modification'
        : /模板|重写|重排|rewrite/.test(normalized)
          ? 'rewrite'
          : /格式|版式|分页|编号|字体/.test(normalized)
            ? 'repair'
            : /起草|写一份|draft|new/.test(lower)
              ? 'generation'
              : 'mixed'

  const basisPrompts = [
    /模板/.test(normalized) ? null : '补充书写模板（如有）',
    /rubric|审查|review|审核/.test(lower) ? null : '补充审核规则 / rubric',
    /现有|基于|修改/.test(normalized) ? null : '提供现有基础文档',
    /要求|风格|口吻/.test(normalized) ? null : '补充个人写作要求（如有）',
  ].filter((item): item is string => Boolean(item))

  return {
    id: `task-card-${Date.now().toString(36)}`,
    createdAt: new Date().toISOString(),
    requestText: normalized,
    understanding: normalized || '请先描述你想处理的文档任务。',
    selectedChoiceId: null,
    customDescription: null,
    basisStatus: {
      template: /模板/.test(normalized) ? 'present' : 'optional',
      writing_requirements: /要求|风格|口吻/.test(normalized) ? 'present' : 'optional',
      review_rubric: /rubric|审查|review|审核/.test(lower) ? 'present' : 'missing',
      source_document: /现有|基于|修改/.test(normalized) ? 'present' : 'missing',
    },
    proposedFirstStep:
      taskType === 'review' ? '先确认审查目标与 rubric，再进入正式工作台。' : '先确认任务类型，再补充缺失 basis。',
    missingInputs: basisPrompts
      .map((item) =>
        item.includes('模板')
          ? 'template'
          : item.includes('rubric')
            ? 'review_rubric'
            : item.includes('基础文档')
              ? 'source_document'
              : 'writing_requirements',
      )
      .filter((item): item is OfficeXBasisInputId => Boolean(item)),
    summary: normalized || '请先描述你想处理的文档任务。',
    taskType,
    recommendedChoices: TASK_CHOICES,
    basisPrompts,
    nextStepSummary:
      basisPrompts.length === 0
        ? '已具备进入正式工作台的基础信息。'
        : `确认任务类型后，再补充 ${basisPrompts[0]}。`,
    readyToTransition: basisPrompts.length === 0,
  }
}
```

- [ ] **Step 4: Add bounded IPC methods without changing runtime commands**

```ts
ipcMain.handle('officex:create-thread', async (_event, workspaceId?: string, title?: string) => {
  const state = loadWorkbenchState()
  const targetWorkspaceId = workspaceId ?? state.activeWorkspaceId
  createThread(targetWorkspaceId, title ?? '新线程')
  return buildDesktopBootstrap(repoRoot, loadSettings())
})

ipcMain.handle('officex:select-thread', async (_event, workspaceId: string, threadId: string) => {
  selectThread(workspaceId, threadId)
  return buildDesktopBootstrap(repoRoot, loadSettings())
})

ipcMain.handle('officex:submit-intake', async (_event, prompt: string) => {
  const card = buildTaskConfirmationCard(prompt)
  const state = loadWorkbenchState()
  const activeThreadId = state.activeThreadId ?? createThread(state.activeWorkspaceId, '新线程').id
  saveTaskConfirmationCard(activeThreadId, prompt, card)
  return buildDesktopBootstrap(repoRoot, loadSettings())
})
```

```ts
export interface OfficeXDesktopAPI {
  getBootstrap(): Promise<OfficeXDesktopBootstrap>
  saveSettings(settings: Partial<OfficeXUserSettings>): Promise<OfficeXDesktopBootstrap>
  createThread(workspaceId?: string, title?: string): Promise<OfficeXDesktopBootstrap>
  selectThread(workspaceId: string, threadId: string): Promise<OfficeXDesktopBootstrap>
  submitIntake(prompt: string): Promise<OfficeXDesktopBootstrap>
  runAction(
    actionId: OfficeXActionId,
    settings?: Partial<OfficeXUserSettings>,
  ): Promise<OfficeXActionExecution>
  getExecutionHistory(limit?: number): Promise<OfficeXActionExecution[]>
  openPath(targetPath: string): Promise<void>
}
```

- [ ] **Step 5: Run the tests**

Run: `cd /Users/nihao/Documents/Playground/document-ops-system/desktop && bun test src/tests/taskIntake.test.ts src/tests/workbenchStateStore.test.ts src/tests/workbenchBootstrap.test.ts`

Expected: PASS

- [ ] **Step 6: Commit**

```bash
cd /Users/nihao/Documents/Playground/document-ops-system
git add desktop/src/main/taskIntake.ts desktop/src/tests/taskIntake.test.ts desktop/src/main/index.ts desktop/src/preload/index.ts desktop/src/shared/types.ts desktop/src/main/workbenchStateStore.ts
git commit -m "feat: add officex task confirmation card flow"
```

## Task 4: Refactor The Renderer Into The Three-Column Workbench

**Files:**
- Create: `desktop/src/renderer/src/components/WorkbenchSidebar.tsx`
- Create: `desktop/src/renderer/src/components/WorkbenchCenter.tsx`
- Create: `desktop/src/renderer/src/components/ChatDock.tsx`
- Create: `desktop/src/renderer/src/components/TaskConfirmationCardView.tsx`
- Create: `desktop/src/tests/rendererMarkup.test.tsx`
- Modify: `desktop/src/renderer/src/App.tsx`
- Modify: `desktop/src/renderer/src/styles.css`

- [ ] **Step 1: Write the failing renderer-markup test**

```tsx
import { describe, expect, it } from 'bun:test'
import { renderToStaticMarkup } from 'react-dom/server'

import { WorkbenchCenter } from '../renderer/src/components/WorkbenchCenter'
import { TaskConfirmationCardView } from '../renderer/src/components/TaskConfirmationCardView'

describe('renderer workbench markup', () => {
  it('renders the intake empty state copy', () => {
    const html = renderToStaticMarkup(
      <WorkbenchCenter
        mode="intake"
        logoLabel="OfficeX"
        headline="今天想要处理什么文档任务？"
        supportingCopy="从任务开始，而不是从编辑器开始。"
      />,
    )

    expect(html).toContain('OfficeX')
    expect(html).toContain('今天想要处理什么文档任务？')
    expect(html).toContain('从任务开始，而不是从编辑器开始。')
  })

  it('renders the confirmation card sections', () => {
    const html = renderToStaticMarkup(
      <TaskConfirmationCardView
        card={{
          id: 'card-1',
          createdAt: '2026-04-21T00:00:00.000Z',
          requestText: '按 rubric 审查这份文档',
          understanding: '按 rubric 审查这份文档',
          classification: 'review',
          selectedChoiceId: null,
          customDescription: null,
          basisStatus: {
            template: 'optional',
            writing_requirements: 'optional',
            review_rubric: 'missing',
            source_document: 'present',
          },
          proposedFirstStep: '先确认审查目标，再补充 rubric。',
          missingInputs: ['review_rubric'],
          readyToTransition: false,
          summary: '按 rubric 审查这份文档',
          taskType: 'review',
          recommendedChoices: [
            { id: 'review', label: '按 rubric 审查文档', description: '输出问题与复检项' },
          ],
          basisPrompts: ['补充审核规则 / rubric'],
          nextStepSummary: '确认任务类型后，再补充 rubric。',
        }}
      />,
    )

    expect(html).toContain('OfficeX 对需求的理解')
    expect(html).toContain('按 rubric 审查这份文档')
    expect(html).toContain('补充审核规则 / rubric')
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/nihao/Documents/Playground/document-ops-system/desktop && bun test src/tests/rendererMarkup.test.tsx`

Expected: FAIL because the renderer components do not exist yet.

- [ ] **Step 3: Build the workbench components**

```tsx
export function WorkbenchSidebar(props: {
  workspaces: OfficeXWorkspaceSummary[]
  activeWorkspaceId: string
  threads: OfficeXThreadSummary[]
  activeThreadId: string | null
  onCreateThread: () => void
  onSelectThread: (workspaceId: string, threadId: string) => void
}) {
  return (
    <aside className="workbench-sidebar">
      <div className="sidebar-brand">
        <span className="sidebar-brand-mark">OfficeX</span>
        <button onClick={props.onCreateThread}>新建线程</button>
      </div>
      {props.workspaces.map((workspace) => (
        <section key={workspace.id} className="workspace-group">
          <header>{workspace.title}</header>
          {props.threads.map((thread) => (
            <button
              key={thread.id}
              className={thread.id === props.activeThreadId ? 'thread-row thread-row-active' : 'thread-row'}
              onClick={() => props.onSelectThread(workspace.id, thread.id)}
            >
              {thread.title}
            </button>
          ))}
        </section>
      ))}
    </aside>
  )
}
```

```tsx
export function WorkbenchCenter(props: {
  mode: 'intake' | 'workbench'
  logoLabel: string
  headline: string
  supportingCopy: string
}) {
  if (props.mode === 'intake') {
    return (
      <section className="workbench-center workbench-center-intake">
        <div className="intake-empty-state">
          <div className="intake-logo">{props.logoLabel}</div>
          <h1>{props.headline}</h1>
          <p>{props.supportingCopy}</p>
        </div>
      </section>
    )
  }
  return <section className="workbench-center workbench-center-document">文档工作区</section>
}
```

```tsx
export function ChatDock(props: {
  controls: OfficeXChatControls
  confirmationCard: OfficeXTaskConfirmationCard | null
  onSubmit: (value: string) => void
}) {
  return (
    <aside className="chat-dock">
      <header className="chat-dock-header">
        <select value={props.controls.selectedModelId}>
          {props.controls.models.map((item) => (
            <option key={item.id} value={item.id}>{item.label}</option>
          ))}
        </select>
        <select value={props.controls.selectedReasoningId}>
          {props.controls.reasoningChoices.map((item) => (
            <option key={item.id} value={item.id}>{item.label}</option>
          ))}
        </select>
        <button type="button">语音输入</button>
      </header>
      {props.confirmationCard ? <TaskConfirmationCardView card={props.confirmationCard} /> : null}
      <textarea placeholder={props.controls.placeholder} />
      <button type="button">发送</button>
    </aside>
  )
}
```

- [ ] **Step 4: Replace the old single-screen app with the new shell**

```tsx
return (
  <main className="workbench-shell">
    <WorkbenchSidebar
      workspaces={bootstrap.navigation.workspaces}
      activeWorkspaceId={bootstrap.navigation.activeWorkspaceId}
      threads={bootstrap.navigation.threads}
      activeThreadId={bootstrap.navigation.activeThreadId}
      onCreateThread={() => void handleCreateThread()}
      onSelectThread={(workspaceId, threadId) => void handleSelectThread(workspaceId, threadId)}
    />
    <WorkbenchCenter
      mode={bootstrap.shell.mode}
      logoLabel="OfficeX"
      headline="今天想要处理什么文档任务？"
      supportingCopy="从任务开始，而不是从编辑器开始。"
    />
    <ChatDock
      controls={bootstrap.chatControls}
      confirmationCard={
        bootstrap.navigation.threads.find((thread) => thread.id === bootstrap.navigation.activeThreadId)
          ?.confirmationCard ?? null
      }
      onSubmit={(value) => void handleSubmitIntake(value)}
    />
  </main>
)
```

- [ ] **Step 5: Run the renderer tests and typecheck**

Run: `cd /Users/nihao/Documents/Playground/document-ops-system/desktop && bun test src/tests/rendererMarkup.test.tsx && bun run typecheck`

Expected: PASS

- [ ] **Step 6: Commit**

```bash
cd /Users/nihao/Documents/Playground/document-ops-system
git add desktop/src/renderer/src/App.tsx desktop/src/renderer/src/components/WorkbenchSidebar.tsx desktop/src/renderer/src/components/WorkbenchCenter.tsx desktop/src/renderer/src/components/ChatDock.tsx desktop/src/renderer/src/components/TaskConfirmationCardView.tsx desktop/src/renderer/src/styles.css desktop/src/tests/rendererMarkup.test.tsx
git commit -m "feat: render officex three-column intake workbench"
```

## Task 5: Rehome Utility Actions And Execution Feedback Inside The Workbench

**Files:**
- Create: `desktop/src/renderer/src/components/RunArtifactsPanel.tsx`
- Modify: `desktop/src/renderer/src/App.tsx`
- Modify: `desktop/src/shared/types.ts`
- Modify: `desktop/src/tests/rendererMarkup.test.tsx`
- Modify: `desktop/src/tests/sidecar.test.ts`

- [ ] **Step 1: Write the failing utility-panel test**

```tsx
it('renders utility actions and execution artifacts in the chat dock', () => {
  const html = renderToStaticMarkup(
    <RunArtifactsPanel
      actions={[
        { id: 'doctor', label: '检查这台 Mac', description: '运行环境自检' },
        { id: 'render-boundary', label: '验证 Word 输出', description: '验证渲染边界' },
      ]}
      execution={{
        executionId: 'run-1',
        actionId: 'doctor',
        status: 'pass',
        message: 'doctor 完成',
        artifactPaths: ['/tmp/report.md'],
      }}
    />,
  )

  expect(html).toContain('检查这台 Mac')
  expect(html).toContain('验证 Word 输出')
  expect(html).toContain('/tmp/report.md')
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/nihao/Documents/Playground/document-ops-system/desktop && bun test src/tests/rendererMarkup.test.tsx`

Expected: FAIL because `RunArtifactsPanel` does not exist yet.

- [ ] **Step 3: Implement the utility panel and keep runtime actions unchanged**

```tsx
export function RunArtifactsPanel(props: {
  actions: OfficeXDesktopActionSummary[]
  execution: Pick<OfficeXActionExecution, 'executionId' | 'actionId' | 'status' | 'message' | 'artifactPaths'> | null
  onRunAction?: (actionId: OfficeXActionId) => void
  onOpenArtifact?: (targetPath: string) => void
}) {
  return (
    <section className="run-artifacts-panel">
      <div className="utility-actions">
        {props.actions.map((action) => (
          <button key={action.id} onClick={() => props.onRunAction?.(action.id)}>
            {action.label}
          </button>
        ))}
      </div>
      {props.execution ? (
        <div className="execution-summary">
          <p>{props.execution.message}</p>
          {props.execution.artifactPaths.map((artifactPath) => (
            <button key={artifactPath} onClick={() => props.onOpenArtifact?.(artifactPath)}>
              {artifactPath}
            </button>
          ))}
        </div>
      ) : null}
    </section>
  )
}
```

```tsx
<ChatDock
  controls={bootstrap.chatControls}
  confirmationCard={
    bootstrap.navigation.threads.find((thread) => thread.id === bootstrap.navigation.activeThreadId)
      ?.confirmationCard ?? null
  }
  onSubmit={(value) => void handleSubmitIntake(value)}
>
  <RunArtifactsPanel
    actions={bootstrap.utilityActions}
    execution={execution}
    onRunAction={(actionId) => void handleRunAction(actionId)}
    onOpenArtifact={(targetPath) => void getDesktopApi()?.openPath(targetPath)}
  />
</ChatDock>
```

- [ ] **Step 4: Re-run execution-history and utility tests**

```ts
expect(execution.artifactPaths).toEqual(
  expect.arrayContaining([
    '/tmp/officex-workspace/report.md',
  ]),
)
```

Run: `cd /Users/nihao/Documents/Playground/document-ops-system/desktop && bun test src/tests/rendererMarkup.test.tsx src/tests/sidecar.test.ts`

Expected: PASS

- [ ] **Step 5: Run the full desktop check**

Run: `cd /Users/nihao/Documents/Playground/document-ops-system/desktop && bun run check`

Expected: PASS

- [ ] **Step 6: Commit**

```bash
cd /Users/nihao/Documents/Playground/document-ops-system
git add desktop/src/renderer/src/components/RunArtifactsPanel.tsx desktop/src/renderer/src/App.tsx desktop/src/tests/rendererMarkup.test.tsx desktop/src/tests/sidecar.test.ts desktop/src/shared/types.ts
git commit -m "feat: keep officex utility actions inside workbench"
```

## Task 6: Update Architecture And Trace For The Frontstage Shift

**Files:**
- Modify: `docs/ARCHITECTURE.md`
- Modify: `docs/blueprints/DESKTOP_RUNTIME_CONTRACT.md`
- Add: `trace/CHECKPOINT_26.md`
- Modify: `trace/CURRENT_STATE.md`
- Modify: `trace/SESSION_LOG.md`

- [ ] **Step 1: Write the docs first as the failing source-of-truth check**

```md
- first app shell shape: intake-first desktop workbench
- workbench layout: left navigation, center document surface, right chat/control dock
- initial thread state: blank intake with confirmation card before execution
```

```md
## Frontstage Transition

The current desktop shell is no longer described as readiness-first home only.

The active shape is:

- left workspace and thread rail
- center intake/document surface
- right chat and utility dock
```

- [ ] **Step 2: Update `docs/ARCHITECTURE.md`**

```md
## Current Architectural Frame

- active output type: `docx`
- target compatibility: Microsoft Word
- truth model: `platform truth + Office mirror`
- collaboration mode: human-first with scoped adaptive autonomy
- top product entry: `officex`
- first app shell shape: intake-first macOS desktop workbench
- initial thread state: blank chat intake followed by task confirmation card
```

- [ ] **Step 3: Update `docs/blueprints/DESKTOP_RUNTIME_CONTRACT.md`**

```md
## First App MVP Shape

The active frontstage shell now opens in an intake-first workbench state.

The initial center surface remains empty until the user describes a document
task and confirms the generated task card.

The current shell therefore prioritizes:

- workspace/thread navigation
- chat-based task intake
- task confirmation card
- utility actions for `doctor`, `render-boundary`, and controlled task runs
- candidate/report viewing inside the workbench flow
```

- [ ] **Step 4: Record the checkpoint and current state**

```md
# CHECKPOINT_26

date: 2026-04-21

## Title

OfficeX intake-first workbench shell

## Summary

- the desktop frontstage no longer presents readiness cards as the primary home
- OfficeX now opens into a workspace/thread workbench shell
- new threads begin as blank intake surfaces
- task execution starts only after a confirmation card is shown
- existing `doctor`, `render-boundary`, and controlled `docx` runs remain routed through the same bounded runtime commands
```

```md
- Current desktop-shell posture: the Electron+Bun macOS app now opens as an
  intake-first three-column OfficeX workbench with machine-local workspace/thread
  state, confirmation-card intake, and in-shell utility actions
```

- [ ] **Step 5: Run the consistency checks**

Run: `cd /Users/nihao/Documents/Playground/document-ops-system && rg -n "readiness-first home|intake-first macOS desktop workbench|confirmation card" docs trace`

Expected:
- `docs/ARCHITECTURE.md` contains `intake-first macOS desktop workbench`
- `docs/blueprints/DESKTOP_RUNTIME_CONTRACT.md` contains `task confirmation card`
- `trace/CHECKPOINT_26.md` exists

- [ ] **Step 6: Commit**

```bash
cd /Users/nihao/Documents/Playground/document-ops-system
git add docs/ARCHITECTURE.md docs/blueprints/DESKTOP_RUNTIME_CONTRACT.md trace/CHECKPOINT_26.md trace/CURRENT_STATE.md trace/SESSION_LOG.md
git commit -m "docs: record officex frontstage workbench shift"
```

## Task 7: Smoke The New Product Entry End-To-End

**Files:**
- Modify: `desktop/src/tests/rendererMarkup.test.tsx`
- Modify: `trace/SESSION_LOG.md`

- [ ] **Step 1: Run the full automated desktop suite**

Run: `cd /Users/nihao/Documents/Playground/document-ops-system/desktop && bun run check`

Expected: PASS

- [ ] **Step 2: Run the live desktop shell**

Run: `cd /Users/nihao/Documents/Playground/document-ops-system/desktop && ELECTRON_ENABLE_LOGGING=1 ELECTRON_ENABLE_STACK_DUMPING=1 bun run app`

Expected:
- Electron window opens with left / center / right workbench layout
- center shows `OfficeX` logo and intake copy
- right chat dock shows model selector, reasoning selector, and voice-input button
- `检查这台 Mac` still runs
- `验证 Word 输出` still runs

- [ ] **Step 3: Verify `officex` still opens the app without extra arguments**

Run: `cd /Users/nihao/Documents/Playground/document-ops-system && .venv/bin/python -m tools.report_scaffold_v3.product_entry`

Expected: desktop shell launches

- [ ] **Step 4: Append the smoke result to `trace/SESSION_LOG.md`**

```md
- 2026-04-21: completed intake-first workbench smoke verification
  - desktop check: `cd desktop && bun run check`
  - live shell check: `cd desktop && ELECTRON_ENABLE_LOGGING=1 ELECTRON_ENABLE_STACK_DUMPING=1 bun run app`
  - product entry launch: `.venv/bin/python -m tools.report_scaffold_v3.product_entry`
```

- [ ] **Step 5: Final commit**

```bash
cd /Users/nihao/Documents/Playground/document-ops-system
git add trace/SESSION_LOG.md
git commit -m "test: smoke officex intake-first workbench"
```

## Self-Review

### Spec Coverage

- Product layering is implemented through bootstrap, workbench store, and task intake tasks.
- Three-column workbench layout is implemented in the renderer task.
- Blank intake state is implemented in the renderer task.
- Confirmation-card flow is implemented in the task-intake task.
- System-mapped task choices are implemented in the deterministic intake classifier.
- Utility actions remain available through the workbench utility panel.
- Docs and trace updates cover the governance and replay requirements.

### Placeholder Scan

- No `TODO`, `TBD`, or “similar to above” shortcuts remain.
- Every code-changing step includes code.
- Every verification step includes an exact command and expected result.

### Type Consistency

- `OfficeXTaskConfirmationCard` is introduced before renderer and IPC tasks rely on it.
- `OfficeXWorkbenchState` is introduced before bootstrap generation depends on it.
- `createThread`, `selectThread`, and `buildTaskConfirmationCard` are named consistently across store, IPC, and renderer tasks.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-21-officex-frontstage-workbench-mvp.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
