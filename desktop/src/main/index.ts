import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { app, BrowserWindow, ipcMain, shell } from 'electron'

import type { OfficeXActionId, OfficeXUserSettings } from '../shared/types'
import {
  buildActionPlan,
  buildDesktopBootstrap,
  inferRepoRoot,
  resolveOfficeXHomePath,
} from './actionPlans'
import { loadExecutionHistory } from './executionHistoryStore'
import { saveSettings, loadSettings } from './settingsStore'
import { buildTaskConfirmationCard } from './taskIntake'
import { executeActionPlan } from './sidecar'
import { validateOpenPath } from './openPathPolicy'
import {
  createThread as persistThread,
  loadWorkbenchState,
  saveTaskConfirmationCard,
  selectThread as persistSelectedThread,
} from './workbenchStateStore'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const repoRoot = inferRepoRoot(__dirname)

function desktopLogPath(): string {
  return path.join(resolveOfficeXHomePath(), 'logs', 'desktop.log')
}

function serializeUnknown(value: unknown): unknown {
  if (value instanceof Error) {
    return {
      name: value.name,
      message: value.message,
      stack: value.stack,
    }
  }
  return value
}

function appendDesktopLog(event: string, payload: Record<string, unknown> = {}): void {
  const entry = {
    timestamp: new Date().toISOString(),
    event,
    payload,
  }

  try {
    const targetPath = desktopLogPath()
    fs.mkdirSync(path.dirname(targetPath), { recursive: true })
    fs.appendFileSync(targetPath, `${JSON.stringify(entry)}\n`, 'utf-8')
  } catch {
    // Best-effort diagnostics only.
  }

  console.info('[officex-desktop]', event, payload)
}

function resolvePreloadPath(): string {
  const preloadCandidates = [
    path.join(__dirname, '../preload/index.cjs'),
    path.join(__dirname, '../preload/index.js'),
    path.join(__dirname, '../preload/index.mjs'),
  ]
  const matchedPath = preloadCandidates.find((candidate) => fs.existsSync(candidate))
  return matchedPath ?? preloadCandidates[0]
}

function attachWindowDiagnostics(mainWindow: BrowserWindow): void {
  mainWindow.webContents.on(
    'console-message',
    (_event, level, message, line, sourceId) => {
      appendDesktopLog('renderer.console', {
        level,
        message,
        line,
        sourceId,
      })
    },
  )

  mainWindow.webContents.on('did-finish-load', () => {
    appendDesktopLog('renderer.did-finish-load', {
      url: mainWindow.webContents.getURL(),
      title: mainWindow.getTitle(),
    })
  })

  mainWindow.webContents.on(
    'did-fail-load',
    (_event, errorCode, errorDescription, validatedURL, isMainFrame) => {
      appendDesktopLog('renderer.did-fail-load', {
        errorCode,
        errorDescription,
        validatedURL,
        isMainFrame,
      })
    },
  )

  mainWindow.webContents.on('render-process-gone', (_event, details) => {
    appendDesktopLog('renderer.render-process-gone', {
      reason: details.reason,
      exitCode: details.exitCode,
    })
  })

  mainWindow.on('unresponsive', () => {
    appendDesktopLog('window.unresponsive')
  })
}

function createWindow(): void {
  const preloadPath = resolvePreloadPath()
  const mainWindow = new BrowserWindow({
    width: 1360,
    height: 900,
    minWidth: 1100,
    minHeight: 760,
    backgroundColor: '#0b1020',
    title: 'OfficeX',
    webPreferences: {
      preload: preloadPath,
      contextIsolation: true,
      sandbox: true,
      nodeIntegration: false,
    },
  })
  attachWindowDiagnostics(mainWindow)
  appendDesktopLog('window.create', {
    preloadPath,
    rendererUrl: process.env.ELECTRON_RENDERER_URL ?? null,
  })

  if (process.env.OFFICEX_OPEN_DEVTOOLS === '1') {
    mainWindow.webContents.openDevTools({ mode: 'detach' })
  }

  if (process.env.ELECTRON_RENDERER_URL) {
    appendDesktopLog('window.load-url', {
      target: process.env.ELECTRON_RENDERER_URL,
    })
    void mainWindow.loadURL(process.env.ELECTRON_RENDERER_URL).catch((error: unknown) => {
      appendDesktopLog('window.load-url-error', {
        error: serializeUnknown(error),
      })
    })
    return
  }

  const rendererHtmlPath = path.join(__dirname, '../renderer/index.html')
  appendDesktopLog('window.load-file', {
    target: rendererHtmlPath,
  })
  void mainWindow.loadFile(rendererHtmlPath).catch((error: unknown) => {
    appendDesktopLog('window.load-file-error', {
      error: serializeUnknown(error),
    })
  })
}

function registerIpcHandlers(): void {
  ipcMain.handle('officex:get-bootstrap', async () => {
    return buildDesktopBootstrap(repoRoot, loadSettings())
  })

  ipcMain.handle(
    'officex:save-settings',
    async (_event, partial: Partial<OfficeXUserSettings>) => {
      const nextSettings = saveSettings(partial)
      return buildDesktopBootstrap(repoRoot, nextSettings)
    },
  )

  ipcMain.handle(
    'officex:create-thread',
    async (_event, workspaceId?: string, title?: string) => {
      const state = loadWorkbenchState()
      const targetWorkspaceId = workspaceId ?? state.activeWorkspaceId
      persistThread(targetWorkspaceId, title ?? '新线程')
      return buildDesktopBootstrap(repoRoot, loadSettings())
    },
  )

  ipcMain.handle(
    'officex:select-thread',
    async (_event, workspaceId: string, threadId: string) => {
      persistSelectedThread(workspaceId, threadId)
      return buildDesktopBootstrap(repoRoot, loadSettings())
    },
  )

  ipcMain.handle('officex:submit-intake', async (_event, prompt: string) => {
    const card = buildTaskConfirmationCard(prompt)
    const state = loadWorkbenchState()
    const activeWorkspaceId = state.activeWorkspaceId
    const activeThreadId =
      state.activeThreadId ??
      persistThread(activeWorkspaceId, '新线程').activeThreadId ??
      null

    if (!activeThreadId) {
      throw new Error('Unable to resolve an active thread for intake submission')
    }

    saveTaskConfirmationCard(activeThreadId, prompt, card)
    return buildDesktopBootstrap(repoRoot, loadSettings())
  })

  ipcMain.handle(
    'officex:run-action',
    async (_event, actionId: OfficeXActionId, settings?: Partial<OfficeXUserSettings>) => {
      const mergedSettings = saveSettings(settings ?? {})
      const plan = buildActionPlan(repoRoot, actionId, mergedSettings)
      return executeActionPlan(plan)
    },
  )

  ipcMain.handle('officex:get-execution-history', async (_event, limit?: number) => {
    return loadExecutionHistory(limit)
  })

  ipcMain.handle('officex:open-path', async (_event, targetPath: string) => {
    const validatedPath = validateOpenPath(targetPath, repoRoot, loadSettings())
    const errorMessage = await shell.openPath(validatedPath)
    if (errorMessage) {
      throw new Error(errorMessage)
    }
  })
}

app.whenReady().then(() => {
  appendDesktopLog('app.ready', {
    repoRoot,
  })
  registerIpcHandlers()
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  appendDesktopLog('app.window-all-closed', {
    platform: process.platform,
  })
  if (process.platform !== 'darwin') {
    app.quit()
  }
})
