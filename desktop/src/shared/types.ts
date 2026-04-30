export type OfficeXApprovalMode =
  | 'review_only'
  | 'ask_every_conflict'
  | 'scoped_auto_low_medium'
  | 'full_auto_in_sandbox'

export type OfficeXActionId = 'doctor' | 'render-boundary' | 'run-docx-demo'
export type OfficeXActionKind = 'python-cli' | 'stub'
export type OfficeXActionStatus = 'pass' | 'warning' | 'fail'
export type OfficeXCheckStatus = 'pass' | 'warning' | 'fail' | 'skipped' | 'unknown'
export type OfficeXVerificationScope = 'structural' | 'semantic' | 'layout' | 'mixed'
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

export interface OfficeXUserSettings {
  workspaceRoot: string
  sandboxRoot: string
  approvalMode: OfficeXApprovalMode
}

export interface OfficeXRuntimeStatus {
  ready: boolean
  pythonExecutable: string | null
  wordDetected: boolean
  bunDetected: boolean
  providerConfigured: boolean
  doctorStatus: OfficeXCheckStatus
  doctorReportPath: string | null
  doctorSummary: string
  summary: string
}

export interface OfficeXDesktopActionSummary {
  id: OfficeXActionId
  label: string
  description: string
}

export interface OfficeXModelChoice {
  id: string
  label: string
}

export interface OfficeXReasoningChoice {
  id: 'low' | 'medium' | 'high'
  label: string
}

export interface OfficeXTaskChoice {
  id: OfficeXTaskChoiceId
  label: string
  description: string
}

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

export interface OfficeXActionPlan {
  id: OfficeXActionId
  traceId: string
  createdAt: string
  requestedBy: string
  kind: OfficeXActionKind
  cwd: string
  pythonExecutable: string | null
  commandLabel: string
  summary: string
  args: string[]
}

export interface OfficeXActionExecution {
  executionId: string
  actionId: OfficeXActionId
  plan: OfficeXActionPlan
  status: OfficeXActionStatus
  startedAt: string
  finishedAt: string
  durationMs: number
  verificationScope: OfficeXVerificationScope
  executedBy: string
  message: string
  stdout: string
  stderr: string
  executionRecordPath: string | null
  stdoutLogPath: string | null
  stderrLogPath: string | null
  payload?: unknown
  artifactPaths: string[]
}

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
