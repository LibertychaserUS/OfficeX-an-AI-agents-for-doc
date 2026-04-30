import { startTransition, useEffect, useState } from 'react'

import type {
  OfficeXActionExecution,
  OfficeXActionId,
  OfficeXDesktopAPI,
  OfficeXDesktopBootstrap,
  OfficeXUserSettings,
} from '../../shared/types'
import { ChatDock } from './components/ChatDock'
import { RunArtifactsPanel } from './components/RunArtifactsPanel'
import { WorkbenchCenter } from './components/WorkbenchCenter'
import { WorkbenchSidebar } from './components/WorkbenchSidebar'

function bridgeUnavailableMessage(): string {
  return 'OfficeX desktop bridge 不可用。preload 没有成功注入，当前窗口还没有接上主进程。'
}

function getDesktopApi(): OfficeXDesktopAPI | null {
  if (typeof window === 'undefined') {
    return null
  }
  return window.officex ?? null
}

export async function openArtifactWithFeedback(
  openPath: (targetPath: string) => Promise<void>,
  targetPath: string,
  setError: (message: string | null) => void,
): Promise<void> {
  try {
    setError(null)
    await openPath(targetPath)
  } catch (error: unknown) {
    setError(error instanceof Error ? error.message : String(error))
  }
}

function App() {
  const [bootstrap, setBootstrap] = useState<OfficeXDesktopBootstrap | null>(null)
  const [draftSettings, setDraftSettings] = useState<OfficeXUserSettings | null>(null)
  const [execution, setExecution] = useState<OfficeXActionExecution | null>(null)
  const [busyAction, setBusyAction] = useState<OfficeXActionId | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [intakeDraft, setIntakeDraft] = useState('')
  const [selectedModelId, setSelectedModelId] = useState<string | null>(null)
  const [selectedReasoningId, setSelectedReasoningId] = useState<
    OfficeXDesktopBootstrap['chatControls']['selectedReasoningId'] | null
  >(null)

  async function refreshBootstrap(): Promise<OfficeXDesktopBootstrap | null> {
    const desktopApi = getDesktopApi()
    if (!desktopApi) {
      setErrorMessage(bridgeUnavailableMessage())
      return null
    }

    const payload = await desktopApi.getBootstrap()
    startTransition(() => {
      setBootstrap(payload)
      setDraftSettings(payload.settings)
    })
    return payload
  }

  useEffect(() => {
    const desktopApi = getDesktopApi()
    if (!desktopApi) {
      setErrorMessage(bridgeUnavailableMessage())
      return
    }

    refreshBootstrap().catch((error: unknown) => {
      setErrorMessage(error instanceof Error ? error.message : String(error))
    })
  }, [])

  const activeThread =
    bootstrap?.navigation.threads.find((thread) => thread.id === bootstrap.navigation.activeThreadId) ??
    bootstrap?.navigation.threads[0] ??
    null
  const activeConfirmationCard = activeThread?.confirmationCard ?? null
  const centerHeadline =
    bootstrap?.shell.mode === 'workbench'
      ? activeConfirmationCard?.understanding ?? activeThread?.title ?? '当前线程'
      : '今天想要处理什么文档任务？'
  const centerSupportingCopy =
    bootstrap?.shell.mode === 'workbench'
      ? activeConfirmationCard?.nextStepSummary ??
        activeThread?.openingRequest ??
        '当前线程已经进入工作台，可以继续推进文档任务。'
      : '从任务开始，而不是从编辑器开始。'

  useEffect(() => {
    setIntakeDraft(activeThread?.openingRequest ?? '')
  }, [activeThread?.id])

  useEffect(() => {
    if (!bootstrap) {
      return
    }

    setSelectedModelId((current) =>
      current && bootstrap.chatControls.models.some((item) => item.id === current)
        ? current
        : bootstrap.chatControls.selectedModelId,
    )
    setSelectedReasoningId((current) =>
      current &&
      bootstrap.chatControls.reasoningChoices.some((item) => item.id === current)
        ? current
        : bootstrap.chatControls.selectedReasoningId,
    )
  }, [bootstrap])

  async function handleSaveSettings(): Promise<void> {
    const desktopApi = getDesktopApi()
    if (!desktopApi || !draftSettings) {
      if (!desktopApi) {
        setErrorMessage(bridgeUnavailableMessage())
      }
      return
    }

    setErrorMessage(null)
    try {
      const nextBootstrap = await desktopApi.saveSettings(draftSettings)
      startTransition(() => {
        setBootstrap(nextBootstrap)
        setDraftSettings(nextBootstrap.settings)
      })
    } catch (error: unknown) {
      setErrorMessage(error instanceof Error ? error.message : String(error))
    }
  }

  async function handleCreateThread(): Promise<void> {
    const desktopApi = getDesktopApi()
    if (!desktopApi || !bootstrap) {
      if (!desktopApi) {
        setErrorMessage(bridgeUnavailableMessage())
      }
      return
    }

    setErrorMessage(null)
    try {
      const nextBootstrap = await desktopApi.createThread(bootstrap.navigation.activeWorkspaceId)
      startTransition(() => {
        setBootstrap(nextBootstrap)
        setDraftSettings(nextBootstrap.settings)
      })
    } catch (error: unknown) {
      setErrorMessage(error instanceof Error ? error.message : String(error))
    }
  }

  async function handleSelectThread(workspaceId: string, threadId: string): Promise<void> {
    const desktopApi = getDesktopApi()
    if (!desktopApi) {
      setErrorMessage(bridgeUnavailableMessage())
      return
    }

    setErrorMessage(null)
    try {
      const nextBootstrap = await desktopApi.selectThread(workspaceId, threadId)
      startTransition(() => {
        setBootstrap(nextBootstrap)
        setDraftSettings(nextBootstrap.settings)
      })
    } catch (error: unknown) {
      setErrorMessage(error instanceof Error ? error.message : String(error))
    }
  }

  async function handleSubmitIntake(prompt: string): Promise<void> {
    const desktopApi = getDesktopApi()
    const trimmedPrompt = prompt.trim()

    if (!desktopApi || trimmedPrompt.length === 0) {
      if (!desktopApi) {
        setErrorMessage(bridgeUnavailableMessage())
      }
      return
    }

    setErrorMessage(null)
    try {
      const nextBootstrap = await desktopApi.submitIntake(trimmedPrompt)
      startTransition(() => {
        setBootstrap(nextBootstrap)
        setDraftSettings(nextBootstrap.settings)
      })
      setIntakeDraft('')
    } catch (error: unknown) {
      setErrorMessage(error instanceof Error ? error.message : String(error))
    }
  }

  async function handleRunAction(actionId: OfficeXActionId): Promise<void> {
    const desktopApi = getDesktopApi()
    if (!desktopApi || !draftSettings) {
      if (!desktopApi) {
        setErrorMessage(bridgeUnavailableMessage())
      }
      return
    }

    setBusyAction(actionId)
    setErrorMessage(null)
    try {
      const nextBootstrap = await desktopApi.saveSettings(draftSettings)
      startTransition(() => {
        setBootstrap(nextBootstrap)
        setDraftSettings(nextBootstrap.settings)
      })
      const result = await desktopApi.runAction(actionId, nextBootstrap.settings)
      const refreshedBootstrap = await desktopApi.getBootstrap()
      startTransition(() => {
        setBootstrap(refreshedBootstrap)
        setDraftSettings(refreshedBootstrap.settings)
        setExecution(result)
      })
    } catch (error: unknown) {
      setErrorMessage(error instanceof Error ? error.message : String(error))
    } finally {
      setBusyAction(null)
    }
  }

  if (!getDesktopApi()) {
    return (
      <main className="workbench-shell workbench-shell-unavailable">
        <section className="shell-status-surface">
          <p className="shell-status-kicker">OfficeX</p>
          <h1>桌面入口没有接上主进程</h1>
          <p>{bridgeUnavailableMessage()}</p>
          {errorMessage && <p className="shell-status-error">{errorMessage}</p>}
        </section>
      </main>
    )
  }

  if (!bootstrap || !draftSettings) {
    return (
      <main className="workbench-shell workbench-shell-loading">
        <section className="shell-status-surface">
          <p className="shell-status-kicker">OfficeX</p>
          <h1>正在读取工作区和线程</h1>
          <p>桌面壳已经起来了，正在从主进程取回本地工作台状态。</p>
          {errorMessage && <p className="shell-status-error">{errorMessage}</p>}
        </section>
      </main>
    )
  }

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
        headline={centerHeadline}
        supportingCopy={centerSupportingCopy}
      />

      <ChatDock
        controls={{
          ...bootstrap.chatControls,
          selectedModelId: selectedModelId ?? bootstrap.chatControls.selectedModelId,
          selectedReasoningId: selectedReasoningId ?? bootstrap.chatControls.selectedReasoningId,
        }}
        confirmationCard={activeConfirmationCard}
        draftValue={intakeDraft}
        onDraftChange={setIntakeDraft}
        onSubmit={(value) => void handleSubmitIntake(value)}
        onModelChange={setSelectedModelId}
        onReasoningChange={setSelectedReasoningId}
        utilityPanel={
          <RunArtifactsPanel
            actions={bootstrap.utilityActions}
            execution={execution}
            busyActionId={busyAction}
            onRunAction={(actionId) => void handleRunAction(actionId)}
            onOpenArtifact={(targetPath) =>
              openArtifactWithFeedback(
                async (resolvedTargetPath) => {
                  const desktopApi = getDesktopApi()
                  if (!desktopApi) {
                    throw new Error(bridgeUnavailableMessage())
                  }
                  await desktopApi.openPath(resolvedTargetPath)
                },
                targetPath,
                setErrorMessage,
              )
            }
          />
        }
      />

      {errorMessage && <p className="workbench-toast">{errorMessage}</p>}
    </main>
  )
}

export default App
