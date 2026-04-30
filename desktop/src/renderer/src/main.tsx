import React from 'react'
import ReactDOM from 'react-dom/client'

import App from './App'
import './styles.css'

interface RendererErrorBoundaryState {
  error: Error | null
}

class RendererErrorBoundary extends React.Component<
  React.PropsWithChildren,
  RendererErrorBoundaryState
> {
  state: RendererErrorBoundaryState = {
    error: null,
  }

  static getDerivedStateFromError(error: Error): RendererErrorBoundaryState {
    return {
      error,
    }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error('OfficeX renderer failed to render.', error, errorInfo)
  }

  render() {
    if (this.state.error) {
      return (
        <main className="app-shell loading-shell">
          <section className="hero-panel">
            <div>
              <p className="eyebrow">OfficeX</p>
              <h1>桌面入口渲染失败</h1>
              <p>渲染树抛出了未捕获错误，当前窗口不会再默默显示成空壳。</p>
              <p className="error-message">{this.state.error.message}</p>
              {this.state.error.stack && (
                <pre className="json-view">{this.state.error.stack}</pre>
              )}
            </div>
          </section>
        </main>
      )
    }

    return this.props.children
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RendererErrorBoundary>
      <App />
    </RendererErrorBoundary>
  </React.StrictMode>,
)
