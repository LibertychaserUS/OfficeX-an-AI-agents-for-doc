import crypto from 'node:crypto'

import type {
  OfficeXBasisInputId,
  OfficeXBasisInputStatus,
  OfficeXTaskChoice,
  OfficeXTaskConfirmationCard,
  OfficeXTaskClassification,
} from '../shared/types'

const TASK_CHOICES: OfficeXTaskChoice[] = [
  {
    id: 'draft',
    label: '起草一份新文档',
    description: '从零开始生成第一版内容',
  },
  {
    id: 'modify',
    label: '基于现有文档修改',
    description: '沿着已有文档做定向改写',
  },
  {
    id: 'review',
    label: '按 rubric 审查文档',
    description: '输出问题、风险和复检项',
  },
  {
    id: 'rewrite',
    label: '按模板重写/重排',
    description: '重新组织结构与章节',
  },
  {
    id: 'repair',
    label: '修复格式与版式',
    description: '优先处理样式、编号和版面',
  },
  {
    id: 'custom',
    label: '自定义描述',
    description: '由用户进一步说明特殊目标',
  },
]

const DETERMINISTIC_CREATED_AT = '2026-04-21T00:00:00.000Z'
const BASIS_PROMPTS_BY_KEY: Record<OfficeXBasisInputId, string> = {
  template: '补充书写模板（如有）',
  writing_requirements: '补充写作要求（如有）',
  review_rubric: '补充审核规则 / rubric',
  source_document: '提供现有基础文档',
}

function normalizeInput(input: string): string {
  return input.trim().replace(/\s+/g, ' ')
}

function buildStableId(normalizedInput: string): string {
  const hash = crypto.createHash('sha256').update(normalizedInput).digest('hex').slice(0, 16)
  return `task-card-${hash}`
}

function buildStableCreatedAt(normalizedInput: string): string {
  const hash = crypto.createHash('sha256').update(`createdAt:${normalizedInput}`).digest('hex')
  const offsetSeconds = Number.parseInt(hash.slice(0, 8), 16) % (365 * 24 * 60 * 60)
  return new Date(Date.parse(DETERMINISTIC_CREATED_AT) + offsetSeconds * 1000).toISOString()
}

function classifyTask(normalizedInput: string): OfficeXTaskClassification {
  const lowerInput = normalizedInput.toLowerCase()
  const matches: OfficeXTaskClassification[] = []

  if (/审查|review|rubric|检查|audit/.test(normalizedInput) || /review|rubric|audit/.test(lowerInput)) {
    matches.push('review')
  }

  if (/修改|改写|修订|update|revise|modify/.test(normalizedInput) || /update|revise|modify/.test(lowerInput)) {
    matches.push('modification')
  }

  if (/重写|重排|rewrite|restructure/.test(normalizedInput) || /rewrite|restructure/.test(lowerInput)) {
    matches.push('rewrite')
  }

  if (/格式|版式|编号|字体|分页|layout|format/.test(normalizedInput) || /layout|format/.test(lowerInput)) {
    matches.push('repair')
  }

  if (
    /起草|生成|写一份/.test(normalizedInput) ||
    /\bdraft\b|\bwrite\b|\bcreate\b|new document/.test(lowerInput)
  ) {
    matches.push('generation')
  }

  if (matches.length !== 1) {
    return 'mixed'
  }

  return matches[0]
}

function buildBasisStatus(
  taskType: OfficeXTaskClassification,
  normalizedInput: string,
): Record<OfficeXBasisInputId, OfficeXBasisInputStatus> {
  const lowerInput = normalizedInput.toLowerCase()
  const hasTemplateSignal =
    /模板|template/.test(normalizedInput) || /template/.test(lowerInput)
  const hasRequirementsSignal =
    /要求|风格|口吻|requirements|style|tone/.test(normalizedInput) ||
    /requirements|style|tone/.test(lowerInput)

  if (taskType === 'review') {
    return {
      template: 'optional',
      writing_requirements: hasRequirementsSignal ? 'present' : 'optional',
      review_rubric: 'missing',
      source_document: 'present',
    }
  }

  if (taskType === 'modification') {
    return {
      template: 'optional',
      writing_requirements: hasRequirementsSignal ? 'present' : 'optional',
      review_rubric: 'optional',
      source_document: 'missing',
    }
  }

  if (taskType === 'rewrite') {
    return {
      template: hasTemplateSignal ? 'present' : 'missing',
      writing_requirements: hasRequirementsSignal ? 'present' : 'optional',
      review_rubric: 'optional',
      source_document: 'present',
    }
  }

  if (taskType === 'repair') {
    return {
      template: 'optional',
      writing_requirements: hasRequirementsSignal ? 'present' : 'optional',
      review_rubric: 'optional',
      source_document: 'present',
    }
  }

  if (taskType === 'generation') {
    return {
      template: hasTemplateSignal ? 'present' : 'missing',
      writing_requirements: hasRequirementsSignal ? 'present' : 'missing',
      review_rubric: 'optional',
      source_document: 'optional',
    }
  }

  return {
    template: hasTemplateSignal ? 'present' : 'optional',
    writing_requirements: hasRequirementsSignal ? 'present' : 'optional',
    review_rubric: 'optional',
    source_document: 'missing',
  }
}

function buildBasisPrompts(basisStatus: Record<OfficeXBasisInputId, OfficeXBasisInputStatus>): string[] {
  return Object.entries(basisStatus)
    .filter(([, status]) => status === 'missing')
    .map(([key]) => BASIS_PROMPTS_BY_KEY[key as OfficeXBasisInputId])
}

function buildRecommendedChoices(taskType: OfficeXTaskClassification): OfficeXTaskChoice[] {
  if (taskType === 'mixed') {
    return [
      ...TASK_CHOICES.filter((choice) => choice.id !== 'custom'),
      TASK_CHOICES.find((choice) => choice.id === 'custom') ?? TASK_CHOICES[TASK_CHOICES.length - 1]!,
    ]
  }

  const priorityId =
    taskType === 'modification'
      ? 'modify'
      : taskType === 'review'
        ? 'review'
        : taskType === 'rewrite'
          ? 'rewrite'
          : taskType === 'repair'
            ? 'repair'
            : 'draft'
  const priorityChoice = TASK_CHOICES.find((choice) => choice.id === priorityId) ?? TASK_CHOICES[0]!
  const remainingChoices = TASK_CHOICES.filter((choice) => choice.id !== priorityChoice.id)
  return [priorityChoice, ...remainingChoices]
}

function buildNextStepSummary(taskType: OfficeXTaskClassification, basisPrompts: string[]): string {
  void taskType
  return basisPrompts.length === 0
    ? '已具备进入正式工作台的基础信息。'
    : `确认任务类型后，再补充 ${basisPrompts[0]}。`
}

function buildProposedFirstStep(taskType: OfficeXTaskClassification): string {
  switch (taskType) {
    case 'review':
      return '先确认审查目标与 rubric，再进入正式工作台。'
    case 'modification':
      return '先确认现有文档和修改范围，再开始工作。'
    case 'rewrite':
      return '先确认重写模板和章节顺序，再开始工作。'
    case 'repair':
      return '先确认需要修复的版式问题，再开始工作。'
    case 'generation':
      return '先确认生成目标和文档范围，再开始起草。'
    default:
      return '先确认任务类型，再补充缺失 basis。'
  }
}

export function buildTaskConfirmationCard(input: string): OfficeXTaskConfirmationCard {
  const normalizedInput = normalizeInput(input)
  const taskType = classifyTask(normalizedInput)
  const basisStatus = buildBasisStatus(taskType, normalizedInput)
  const basisPrompts = buildBasisPrompts(basisStatus)
  const missingInputs = Object.entries(basisStatus)
    .filter(([, status]) => status === 'missing')
    .map(([key]) => key as OfficeXBasisInputId)

  return {
    id: buildStableId(normalizedInput),
    createdAt: buildStableCreatedAt(normalizedInput),
    requestText: normalizedInput,
    understanding: normalizedInput || '请先描述你想处理的文档任务。',
    classification: taskType,
    selectedChoiceId: null,
    customDescription: null,
    basisStatus,
    proposedFirstStep: buildProposedFirstStep(taskType),
    missingInputs,
    readyToTransition: missingInputs.length === 0,
    summary: normalizedInput || '请先描述你想处理的文档任务。',
    taskType,
    recommendedChoices: buildRecommendedChoices(taskType),
    basisPrompts,
    nextStepSummary: buildNextStepSummary(taskType, basisPrompts),
  }
}
