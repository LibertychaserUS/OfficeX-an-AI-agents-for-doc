import { describe, expect, it } from 'bun:test'
import type { ReactElement, ReactNode } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'

import { openArtifactWithFeedback } from '../renderer/src/App'
import { ChatDock } from '../renderer/src/components/ChatDock'
import { RunArtifactsPanel } from '../renderer/src/components/RunArtifactsPanel'
import { TaskConfirmationCardView } from '../renderer/src/components/TaskConfirmationCardView'
import { WorkbenchCenter } from '../renderer/src/components/WorkbenchCenter'
import { WorkbenchSidebar } from '../renderer/src/components/WorkbenchSidebar'

function findElementsByType(node: ReactNode, type: string): ReactElement[] {
  if (node === null || node === undefined || typeof node === 'boolean') {
    return []
  }

  if (Array.isArray(node)) {
    return node.flatMap((child) => findElementsByType(child, type))
  }

  if (typeof node !== 'object' || !('type' in node) || !('props' in node)) {
    return []
  }

  const element = node as ReactElement<{ children?: ReactNode }>
  const matches = element.type === type ? [element] : []

  return matches.concat(findElementsByType(element.props.children, type))
}

describe('renderer workbench markup', () => {
  it('renders the intake empty state copy', () => {
    const html = renderToStaticMarkup(
      <WorkbenchCenter
        mode="intake"
        logoLabel="OfficeX"
        headline="今天想要处理什么文档任务？"
        supportingCopy="从任务开始，而不是从编辑器开始。"
      />,
    )

    expect(html).toContain('OfficeX')
    expect(html).toContain('今天想要处理什么文档任务？')
    expect(html).toContain('从任务开始，而不是从编辑器开始。')
  })

  it('renders the confirmation card sections', () => {
    const html = renderToStaticMarkup(
      <TaskConfirmationCardView
        card={{
          id: 'card-1',
          createdAt: '2026-04-21T00:00:00.000Z',
          requestText: '按 rubric 审查这份文档',
          understanding: '按 rubric 审查这份文档',
          classification: 'review',
          selectedChoiceId: null,
          customDescription: null,
          basisStatus: {
            template: 'optional',
            writing_requirements: 'optional',
            review_rubric: 'missing',
            source_document: 'present',
          },
          proposedFirstStep: '先确认审查目标，再补充 rubric。',
          missingInputs: ['review_rubric'],
          readyToTransition: false,
          summary: '按 rubric 审查这份文档',
          taskType: 'review',
          recommendedChoices: [
            { id: 'review', label: '按 rubric 审查文档', description: '输出问题与复检项' },
          ],
          basisPrompts: ['补充审核规则 / rubric'],
          nextStepSummary: '确认任务类型后，再补充 rubric。',
        }}
      />,
    )

    expect(html).toContain('OfficeX 对需求的理解')
    expect(html).toContain('按 rubric 审查这份文档')
    expect(html).toContain('补充审核规则 / rubric')
  })

  it('renders inactive workspaces as overview instead of switchable state', () => {
    const html = renderToStaticMarkup(
      <WorkbenchSidebar
        workspaces={[
          { id: 'workspace-a', title: '默认工作区', threadCount: 1, archivedThreadCount: 0 },
          { id: 'workspace-b', title: '第二工作区', threadCount: 0, archivedThreadCount: 0 },
        ]}
        activeWorkspaceId="workspace-a"
        threads={[
          {
            id: 'thread-a',
            title: '新线程',
            stage: 'intake',
            openingRequest: null,
            confirmationCard: null,
            taskRecord: null,
          },
        ]}
        activeThreadId="thread-a"
        onCreateThread={() => undefined}
        onSelectThread={() => undefined}
      />,
    )

    expect(html).toContain('当前')
    expect(html).toContain('概览')
    expect(html).not.toContain('可切换')
  })

  it('wires model and reasoning controls to the provided callbacks', () => {
    let nextModelId = 'gpt-5.4'
    let nextReasoningId = 'medium'

    const tree = ChatDock({
      controls: {
        placeholder: '今天想要处理什么',
        models: [
          { id: 'gpt-5.4', label: 'GPT-5.4' },
          { id: 'gpt-5.4-mini', label: 'GPT-5.4 Mini' },
        ],
        selectedModelId: 'gpt-5.4',
        reasoningChoices: [
          { id: 'low', label: 'Low' },
          { id: 'medium', label: 'Medium' },
          { id: 'high', label: 'High' },
        ],
        selectedReasoningId: 'medium',
        voiceInputEnabled: true,
      },
      confirmationCard: null,
      draftValue: '',
      onDraftChange: () => undefined,
      onSubmit: () => undefined,
      onModelChange: (value) => {
        nextModelId = value
      },
      onReasoningChange: (value) => {
        nextReasoningId = value
      },
    })

    const selects = findElementsByType(tree, 'select')

    expect(selects).toHaveLength(2)
    selects[0]?.props.onChange({ target: { value: 'gpt-5.4-mini' } })
    selects[1]?.props.onChange({ target: { value: 'high' } })

    expect(nextModelId).toBe('gpt-5.4-mini')
    expect(nextReasoningId).toBe('high')
  })

  it('renders utility actions and execution artifacts in the workbench dock', () => {
    const html = renderToStaticMarkup(
      <RunArtifactsPanel
        actions={[
          { id: 'doctor', label: '检查这台 Mac', description: '运行环境自检' },
          { id: 'render-boundary', label: '验证 Word 输出', description: '验证渲染边界' },
        ]}
        execution={{
          executionId: 'run-1',
          actionId: 'doctor',
          status: 'pass',
          message: 'doctor 完成',
          artifactPaths: ['/tmp/report.md'],
        }}
      />,
    )

    expect(html).toContain('检查这台 Mac')
    expect(html).toContain('验证 Word 输出')
    expect(html).toContain('doctor 完成')
    expect(html).toContain('/tmp/report.md')
  })

  it('disables all utility actions while a run is active', () => {
    const html = renderToStaticMarkup(
      <RunArtifactsPanel
        actions={[
          { id: 'doctor', label: '检查这台 Mac', description: '运行环境自检' },
          { id: 'render-boundary', label: '验证 Word 输出', description: '验证渲染边界' },
        ]}
        execution={null}
        busyActionId="doctor"
      />,
    )

    expect(html).toContain('检查这台 Mac · 运行中')
    expect((html.match(/disabled=""/g) ?? [])).toHaveLength(2)
  })

  it('surfaces artifact-open failures through the shared error handler', async () => {
    let errorMessage: string | null = null

    await openArtifactWithFeedback(
      async () => {
        throw new Error('artifact blocked')
      },
      '/tmp/report.md',
      (nextError) => {
        errorMessage = nextError
      },
    )

    expect(errorMessage).toBe('artifact blocked')
  })
})
