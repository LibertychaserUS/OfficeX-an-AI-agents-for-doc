import type { OfficeXTaskConfirmationCard } from '../../../shared/types'

interface TaskConfirmationCardViewProps {
  card: OfficeXTaskConfirmationCard
}

function statusLabel(status: OfficeXTaskConfirmationCard['basisStatus'][keyof OfficeXTaskConfirmationCard['basisStatus']]): string {
  switch (status) {
    case 'present':
      return '已具备'
    case 'missing':
      return '待补充'
    default:
      return '可选'
  }
}

export function TaskConfirmationCardView(props: TaskConfirmationCardViewProps) {
  const missingInputs = props.card.missingInputs.length > 0 ? props.card.missingInputs.join(' · ') : '无'

  return (
    <section className="task-confirmation-card" aria-label="task confirmation card">
      <header className="confirmation-card-header">
        <p className="confirmation-card-kicker">OfficeX 对需求的理解</p>
        <h3>{props.card.understanding}</h3>
        <p className="confirmation-card-summary">{props.card.proposedFirstStep}</p>
      </header>

      <div className="confirmation-card-section">
        <div className="confirmation-card-section-header">
          <h4>任务类型</h4>
          <span>{props.card.classification}</span>
        </div>
        <p>{props.card.summary}</p>
      </div>

      <div className="confirmation-card-section">
        <div className="confirmation-card-section-header">
          <h4>Basis 状态</h4>
          <span>{missingInputs}</span>
        </div>
        <dl className="confirmation-basis-grid">
          {(
            Object.entries(props.card.basisStatus) as Array<
              [keyof OfficeXTaskConfirmationCard['basisStatus'], OfficeXTaskConfirmationCard['basisStatus'][keyof OfficeXTaskConfirmationCard['basisStatus']]]
            >
          ).map(([key, status]) => (
            <div key={key} className="confirmation-basis-item">
              <dt>{key}</dt>
              <dd>{statusLabel(status)}</dd>
            </div>
          ))}
        </dl>
        <ul className="confirmation-note-list">
          {props.card.basisPrompts.map((prompt: string) => (
            <li key={prompt}>{prompt}</li>
          ))}
        </ul>
      </div>

      <div className="confirmation-card-section">
        <div className="confirmation-card-section-header">
          <h4>推荐选择</h4>
          <span>{props.card.readyToTransition ? '可进入工作台' : '先确认信息'}</span>
        </div>
        <ul className="confirmation-choice-list">
          {props.card.recommendedChoices.map((choice) => (
            <li key={choice.id} className="confirmation-choice-item">
              <strong>{choice.label}</strong>
              <span>{choice.description}</span>
            </li>
          ))}
        </ul>
      </div>

      <footer className="confirmation-card-footer">
        <p>{props.card.nextStepSummary}</p>
      </footer>
    </section>
  )
}
