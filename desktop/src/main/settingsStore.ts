import fs from 'node:fs'
import path from 'node:path'

import type { OfficeXUserSettings } from '../shared/types'
import { buildDefaultSettings, resolveOfficeXHomePath } from './actionPlans'

function settingsPath(): string {
  return path.join(resolveOfficeXHomePath(), 'settings.json')
}

function ensureHomeDir(): void {
  fs.mkdirSync(resolveOfficeXHomePath(), { recursive: true })
}

function writeSettingsAtomically(targetPath: string, payload: OfficeXUserSettings): void {
  const tempPath = `${targetPath}.${process.pid}.${Date.now()}.tmp`
  fs.writeFileSync(tempPath, JSON.stringify(payload, null, 2), 'utf-8')
  fs.renameSync(tempPath, targetPath)
}

export function loadSettings(): OfficeXUserSettings {
  ensureHomeDir()
  const defaults = buildDefaultSettings()
  if (!fs.existsSync(settingsPath())) {
    return defaults
  }
  try {
    const raw = fs.readFileSync(settingsPath(), 'utf-8')
    const payload = JSON.parse(raw) as Partial<OfficeXUserSettings>
    return {
      workspaceRoot: payload.workspaceRoot ?? defaults.workspaceRoot,
      sandboxRoot: payload.sandboxRoot ?? defaults.sandboxRoot,
      approvalMode: payload.approvalMode ?? defaults.approvalMode,
    }
  } catch {
    return defaults
  }
}

export function saveSettings(
  partial: Partial<OfficeXUserSettings>,
): OfficeXUserSettings {
  ensureHomeDir()
  const nextSettings = {
    ...loadSettings(),
    ...partial,
  }
  writeSettingsAtomically(settingsPath(), nextSettings)
  return nextSettings
}
