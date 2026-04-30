import type { ReactNode } from 'react'

import type { OfficeXChatControls, OfficeXTaskConfirmationCard } from '../../../shared/types'
import { TaskConfirmationCardView } from './TaskConfirmationCardView'

interface ChatDockProps {
  controls: OfficeXChatControls
  confirmationCard: OfficeXTaskConfirmationCard | null
  draftValue: string
  onDraftChange: (value: string) => void
  onSubmit: (value: string) => void
  onModelChange: (value: string) => void
  onReasoningChange: (value: OfficeXChatControls['selectedReasoningId']) => void
  utilityPanel?: ReactNode
}

export function ChatDock(props: ChatDockProps) {
  const canSubmit = props.draftValue.trim().length > 0

  return (
    <aside className="chat-dock" aria-label="chat dock">
      <header className="chat-dock-header">
        <div>
          <p className="chat-dock-kicker">Operator dock</p>
          <h2>任务确认与提交</h2>
        </div>
        <div className="chat-dock-controls">
          <label className="chat-control">
            <span>Model</span>
            <select
              value={props.controls.selectedModelId}
              onChange={(event) => props.onModelChange(event.target.value)}
            >
              {props.controls.models.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>
          <label className="chat-control">
            <span>Reasoning</span>
            <select
              value={props.controls.selectedReasoningId}
              onChange={(event) =>
                props.onReasoningChange(event.target.value as OfficeXChatControls['selectedReasoningId'])
              }
            >
              {props.controls.reasoningChoices.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>
        </div>
      </header>

      <div className="chat-dock-body">
        {props.confirmationCard ? (
          <TaskConfirmationCardView card={props.confirmationCard} />
        ) : (
          <section className="chat-dock-empty">
            <p className="chat-dock-empty-title">等待确认卡</p>
            <p className="chat-dock-empty-copy">提交一条任务描述后，这里会先生成理解与 basis 检查。</p>
          </section>
        )}

        <label className="chat-composer">
          <span>Intake</span>
          <textarea
            value={props.draftValue}
            placeholder={props.controls.placeholder}
            onChange={(event) => props.onDraftChange(event.target.value)}
          />
        </label>

        <div className="chat-dock-actions">
          <button
            type="button"
            className="primary-button"
            disabled={!canSubmit}
            onClick={() => props.onSubmit(props.draftValue)}
          >
            发送任务
          </button>
          <button type="button" className="secondary-button" disabled={!props.controls.voiceInputEnabled}>
            语音输入
          </button>
        </div>

        {props.utilityPanel ? <div className="chat-dock-utility-panel">{props.utilityPanel}</div> : null}
      </div>
    </aside>
  )
}
