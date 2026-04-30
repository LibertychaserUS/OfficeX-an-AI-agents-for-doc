import { describe, expect, it } from 'bun:test'

const { buildTaskConfirmationCard } = await import('../main/taskIntake')

describe('buildTaskConfirmationCard', () => {
  it('classifies review requests and requests rubric input', () => {
    const card = buildTaskConfirmationCard('请按照学校 rubric 审查这份 docx 并指出问题')

    expect(card.taskType).toBe('review')
    expect(card.classification).toBe('review')
    expect(card.understanding).toBe('请按照学校 rubric 审查这份 docx 并指出问题')
    expect(card.recommendedChoices.map((item) => item.id)).toContain('review')
    expect(card.basisPrompts).toContain('补充审核规则 / rubric')
    expect(card.nextStepSummary).toBe('确认任务类型后，再补充 补充审核规则 / rubric。')
    expect(card.readyToTransition).toBe(false)
  })

  it('classifies modification requests and requests source-document input', () => {
    const card = buildTaskConfirmationCard('基于现有文档修改第三章的写法')

    expect(card.taskType).toBe('modification')
    expect(card.classification).toBe('modification')
    expect(card.recommendedChoices[0]?.id).toBe('modify')
    expect(card.basisPrompts).toContain('提供现有基础文档')
  })

  it('falls back to a mixed task for ambiguous requests', () => {
    const card = buildTaskConfirmationCard('帮我处理一下这个东西')

    expect(card.taskType).toBe('mixed')
    expect(card.classification).toBe('mixed')
    expect(card.recommendedChoices.at(-1)?.id).toBe('custom')
    expect(card.selectedChoiceId).toBeNull()
  })

  it('falls back to mixed when the request combines multiple task types', () => {
    const card = buildTaskConfirmationCard('请先审查这份 docx 再修改第三章')

    expect(card.taskType).toBe('mixed')
    expect(card.classification).toBe('mixed')
    expect(card.recommendedChoices.at(-1)?.id).toBe('custom')
    expect(card.selectedChoiceId).toBeNull()
  })

  it('marks the card ready when the required basis is already present', () => {
    const card = buildTaskConfirmationCard('按模板重写现有文档并按要求调整口吻')

    expect(card.taskType).toBe('rewrite')
    expect(card.missingInputs).toHaveLength(0)
    expect(card.basisPrompts).toHaveLength(0)
    expect(card.understanding).toBe('按模板重写现有文档并按要求调整口吻')
    expect(card.nextStepSummary).toBe('已具备进入正式工作台的基础信息。')
    expect(card.readyToTransition).toBe(true)
  })

  it('keeps rewrite as a single task for English rewrite prompts', () => {
    const card = buildTaskConfirmationCard('rewrite this document with the new template')

    expect(card.taskType).toBe('rewrite')
    expect(card.classification).toBe('rewrite')
    expect(card.recommendedChoices[0]?.id).toBe('rewrite')
  })

  it('uses the default understanding for whitespace-only input', () => {
    const card = buildTaskConfirmationCard('   ')

    expect(card.taskType).toBe('mixed')
    expect(card.requestText).toBe('')
    expect(card.understanding).toBe('请先描述你想处理的文档任务。')
    expect(card.selectedChoiceId).toBeNull()
  })
})
