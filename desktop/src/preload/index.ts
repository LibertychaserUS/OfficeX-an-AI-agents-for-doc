import { contextBridge, ipcRenderer } from 'electron'

import type {
  OfficeXActionExecution,
  OfficeXActionId,
  OfficeXDesktopAPI,
  OfficeXDesktopBootstrap,
  OfficeXUserSettings,
} from '../shared/types'

const officexApi: OfficeXDesktopAPI = {
  getBootstrap: () =>
    ipcRenderer.invoke('officex:get-bootstrap') as Promise<OfficeXDesktopBootstrap>,
  saveSettings: (settings) =>
    ipcRenderer.invoke(
      'officex:save-settings',
      settings,
    ) as Promise<OfficeXDesktopBootstrap>,
  createThread: (workspaceId?: string, title?: string) =>
    ipcRenderer.invoke(
      'officex:create-thread',
      workspaceId,
      title,
    ) as Promise<OfficeXDesktopBootstrap>,
  selectThread: (workspaceId: string, threadId: string) =>
    ipcRenderer.invoke(
      'officex:select-thread',
      workspaceId,
      threadId,
    ) as Promise<OfficeXDesktopBootstrap>,
  submitIntake: (prompt: string) =>
    ipcRenderer.invoke(
      'officex:submit-intake',
      prompt,
    ) as Promise<OfficeXDesktopBootstrap>,
  runAction: (actionId: OfficeXActionId, settings?: Partial<OfficeXUserSettings>) =>
    ipcRenderer.invoke(
      'officex:run-action',
      actionId,
      settings,
    ) as Promise<OfficeXActionExecution>,
  getExecutionHistory: (limit?: number) =>
    ipcRenderer.invoke(
      'officex:get-execution-history',
      limit,
    ) as Promise<OfficeXActionExecution[]>,
  openPath: (targetPath: string) =>
    ipcRenderer.invoke('officex:open-path', targetPath) as Promise<void>,
}

contextBridge.exposeInMainWorld('officex', officexApi)
