interface WorkbenchCenterProps {
  mode: 'intake' | 'workbench'
  logoLabel: string
  headline: string
  supportingCopy: string
}

export function WorkbenchCenter(props: WorkbenchCenterProps) {
  if (props.mode === 'intake') {
    return (
      <section className="workbench-center workbench-center-intake" aria-label="intake empty state">
        <div className="intake-empty-state">
          <div className="intake-logo">{props.logoLabel}</div>
          <p className="intake-kicker">Intake first</p>
          <h1>{props.headline}</h1>
          <p className="intake-supporting-copy">{props.supportingCopy}</p>
          <div className="intake-state-band">
            <span>先描述任务</span>
            <span>再生成确认卡</span>
            <span>最后进入工作台</span>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section className="workbench-center workbench-center-workbench" aria-label="active workbench">
      <div className="workbench-document-surface">
        <p className="workbench-document-kicker">Current thread</p>
        <h2>{props.headline}</h2>
        <p className="workbench-document-copy">{props.supportingCopy}</p>
      </div>
    </section>
  )
}
