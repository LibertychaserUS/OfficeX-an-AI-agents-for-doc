import fs from 'node:fs'
import path from 'node:path'

import { resolveOfficeXHomePath } from './actionPlans'
import type { OfficeXUserSettings } from '../shared/types'

const ALLOWED_FILE_EXTENSIONS = new Set([
  '.docx',
  '.json',
  '.md',
  '.txt',
  '.yml',
  '.yaml',
  '.log',
  '.html',
])

function isWithinRoot(targetPath: string, rootPath: string): boolean {
  const relative = path.relative(rootPath, targetPath)
  return relative === '' || (!relative.startsWith('..') && !path.isAbsolute(relative))
}

function normalizeExistingPath(targetPath: string): string {
  const resolvedPath = path.resolve(targetPath)
  if (!fs.existsSync(resolvedPath)) {
    return resolvedPath
  }
  return fs.realpathSync(resolvedPath)
}

export function validateOpenPath(
  targetPath: string,
  repoRoot: string,
  settings: OfficeXUserSettings,
): string {
  if (!targetPath || targetPath.includes('\0')) {
    throw new Error('Open path target is invalid.')
  }

  const resolvedTarget = path.resolve(targetPath)
  if (!fs.existsSync(resolvedTarget)) {
    throw new Error(`Open path target does not exist: ${resolvedTarget}`)
  }

  const realTarget = normalizeExistingPath(resolvedTarget)
  const allowedRoots = [
    normalizeExistingPath(repoRoot),
    normalizeExistingPath(settings.workspaceRoot),
    normalizeExistingPath(settings.sandboxRoot),
    normalizeExistingPath(resolveOfficeXHomePath()),
  ]

  if (!allowedRoots.some((rootPath) => isWithinRoot(realTarget, rootPath))) {
    throw new Error(`Open path target is outside the allowed OfficeX roots: ${realTarget}`)
  }

  const stats = fs.statSync(realTarget)
  if (stats.isDirectory()) {
    return realTarget
  }

  const extension = path.extname(realTarget).toLowerCase()
  if (!ALLOWED_FILE_EXTENSIONS.has(extension)) {
    throw new Error(`Open path target uses a blocked file type: ${realTarget}`)
  }

  return realTarget
}
