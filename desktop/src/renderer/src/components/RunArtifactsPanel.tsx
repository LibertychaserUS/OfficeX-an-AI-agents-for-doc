import type { OfficeXActionExecution, OfficeXActionId, OfficeXDesktopActionSummary } from '../../../shared/types'

interface RunArtifactsPanelProps {
  actions: OfficeXDesktopActionSummary[]
  execution: OfficeXActionExecution | null
  busyActionId?: OfficeXActionId | null
  onRunAction?: (actionId: OfficeXActionId) => void
  onOpenArtifact?: (targetPath: string) => void
}

function getExecutionStatusLabel(status: OfficeXActionExecution['status']): string {
  if (status === 'pass') {
    return '已完成'
  }
  if (status === 'warning') {
    return '有复核项'
  }
  return '执行失败'
}

export function RunArtifactsPanel(props: RunArtifactsPanelProps) {
  return (
    <section className="run-artifacts-panel" aria-label="utility actions and execution artifacts">
      <header className="run-artifacts-header">
        <div>
          <p className="run-artifacts-kicker">Workbench utilities</p>
          <h3>运行与产物</h3>
        </div>
        <p className="run-artifacts-summary">
          从这里触发桌面动作，并直接查看最近一次执行留下的文档和日志。
        </p>
      </header>

      <div className="run-artifacts-actions">
        {props.actions.map((action) => {
          const isBusy = props.busyActionId === action.id
          const actionsLocked = props.busyActionId !== null && props.busyActionId !== undefined

          return (
            <button
              key={action.id}
              type="button"
              className="run-artifact-action"
              disabled={!props.onRunAction || actionsLocked}
              onClick={() => props.onRunAction?.(action.id)}
            >
              <span className="run-artifact-action-label">
                {isBusy ? `${action.label} · 运行中` : action.label}
              </span>
              <span className="run-artifact-action-description">{action.description}</span>
            </button>
          )
        })}
      </div>

      {props.execution ? (
        <section className="run-artifacts-execution">
          <div className="run-artifacts-execution-header">
            <div>
              <p className={`run-artifacts-status status-${props.execution.status}`}>
                {getExecutionStatusLabel(props.execution.status)}
              </p>
              <h4>{props.execution.actionId}</h4>
            </div>
            <p className="run-artifacts-execution-id">{props.execution.executionId}</p>
          </div>

          <p className="run-artifacts-execution-message">{props.execution.message}</p>

          <div className="run-artifacts-file-list">
            {props.execution.artifactPaths.length > 0 ? (
              props.execution.artifactPaths.map((artifactPath) => (
                <button
                  key={artifactPath}
                  type="button"
                  className="artifact-button run-artifact-file-button"
                  disabled={!props.onOpenArtifact}
                  onClick={() => props.onOpenArtifact?.(artifactPath)}
                >
                  <span className="run-artifact-file-path">{artifactPath}</span>
                  <span className="run-artifact-file-open">打开产物</span>
                </button>
              ))
            ) : (
              <p className="run-artifacts-empty-copy">这次执行还没有生成可打开的产物路径。</p>
            )}
          </div>
        </section>
      ) : (
        <section className="run-artifacts-empty">
          <p className="run-artifacts-empty-title">等待一次运行</p>
          <p className="run-artifacts-empty-copy">运行任一工具后，最近一次执行摘要和产物会出现在这里。</p>
        </section>
      )}
    </section>
  )
}
