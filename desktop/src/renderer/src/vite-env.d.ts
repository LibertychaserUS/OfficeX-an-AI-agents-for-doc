/// <reference types="vite/client" />

import type { OfficeXDesktopAPI } from '../../shared/types'

declare global {
  interface Window {
    officex?: OfficeXDesktopAPI
  }
}

export {}
