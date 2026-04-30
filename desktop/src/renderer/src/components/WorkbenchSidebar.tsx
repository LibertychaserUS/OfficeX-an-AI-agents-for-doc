import type { OfficeXThreadSummary, OfficeXWorkspaceSummary } from '../../../shared/types'

interface WorkbenchSidebarProps {
  workspaces: OfficeXWorkspaceSummary[]
  activeWorkspaceId: string
  threads: OfficeXThreadSummary[]
  activeThreadId: string | null
  onCreateThread: () => void
  onSelectThread: (workspaceId: string, threadId: string) => void
}

function formatThreadStage(stage: OfficeXThreadSummary['stage']): string {
  switch (stage) {
    case 'awaiting_confirmation':
      return '等待确认'
    case 'workbench':
      return '工作台'
    case 'archived':
      return '已归档'
    default:
      return '新建'
  }
}

export function WorkbenchSidebar(props: WorkbenchSidebarProps) {
  return (
    <aside className="workbench-sidebar" aria-label="workspace and thread navigation">
      <div className="sidebar-brand">
        <div>
          <p className="sidebar-kicker">OfficeX</p>
          <h1>Workbench</h1>
        </div>
        <button type="button" className="sidebar-create-button" onClick={props.onCreateThread}>
          新建线程
        </button>
      </div>

      <nav className="sidebar-workspace-list">
        {props.workspaces.map((workspace) => {
          const isActiveWorkspace = workspace.id === props.activeWorkspaceId
          const visibleThreads = isActiveWorkspace ? props.threads : []

          return (
            <section
              key={workspace.id}
              className={isActiveWorkspace ? 'workspace-group workspace-group-active' : 'workspace-group'}
            >
              <header className="workspace-group-header">
                <div>
                  <p className="workspace-label">{workspace.title}</p>
                  <p className="workspace-meta">
                    {workspace.threadCount} 条线程 · {workspace.archivedThreadCount} 条归档
                  </p>
                </div>
                <span className="workspace-state">{isActiveWorkspace ? '当前' : '概览'}</span>
              </header>

              {visibleThreads.length > 0 ? (
                <div className="thread-list">
                  {visibleThreads.map((thread) => {
                    const isActiveThread = thread.id === props.activeThreadId

                    return (
                      <button
                        key={thread.id}
                        type="button"
                        className={isActiveThread ? 'thread-row thread-row-active' : 'thread-row'}
                        onClick={() => props.onSelectThread(workspace.id, thread.id)}
                      >
                        <div className="thread-row-title">
                          <span>{thread.title}</span>
                          <span className="thread-row-stage">{formatThreadStage(thread.stage)}</span>
                        </div>
                        <p className="thread-row-detail">
                          {thread.openingRequest ?? '等待第一条任务输入'}
                        </p>
                      </button>
                    )
                  })}
                </div>
              ) : (
                <p className="workspace-empty-state">
                  {isActiveWorkspace ? '当前工作区还没有线程。' : '当前只显示工作区概览。'}
                </p>
              )}
            </section>
          )
        })}
      </nav>
    </aside>
  )
}
