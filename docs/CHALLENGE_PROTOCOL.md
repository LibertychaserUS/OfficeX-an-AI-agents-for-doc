# Challenge Protocol

## Purpose

This protocol extends normal engineering review.

It is not enough to challenge correctness only. The platform should also
challenge feasibility, precedent, alternatives, and tooling before claiming a
path is mature.

## The Five Challenge Axes

### 1. Correctness

Ask:

- Is the implementation logically correct?
- Is the validation path checking the right thing?
- Are we overstating confidence?

### 2. Feasibility

Ask:

- Is the target actually achievable with the current constraints?
- Does Word, OOXML, `python-docx`, or the local renderer make this practical?
- Is the plan too expensive, brittle, or manual for sustained use?

### 3. Precedent

Ask:

- Have similar systems or projects used a comparable approach?
- Is there an established pattern we can adapt instead of inventing from
  scratch?

### 4. Alternatives

Ask:

- Is there a simpler architecture?
- Can the responsibility move one layer earlier, such as from writer to
  assembler?
- Can we replace repeated manual commands with a sanctioned pipeline?

### 5. Tooling

Ask:

- Is the current tool the right level of abstraction?
- Would a software catalog, ADR, reusable workflow, code owner model, or
  stronger publication step reduce future drift?

## Mandatory Challenge Questions

Before approving a non-trivial approach, ask:

1. Is the goal feasible?
2. Has something similar been done before?
3. Is there a better architecture?
4. Is there a better tool?
5. Is there a lower-risk staged version?
6. What would make the current plan fail in practice?

## When External Research Is Worthwhile

Use external research when:

- the problem looks like a known software process pattern,
- a documentation architecture question is involved,
- publication/governance rules are under discussion,
- tooling choices may lock in future complexity,
- there is doubt about feasibility or precedent.

## How To Record The Result

A challenge result should state:

- the challenged assumption,
- the competing option,
- the verdict,
- the residual risk,
- whether an ADR or operating-model update is needed.

## Why This Matters

This protocol turns mistakes into better architecture rather than only local
fixes.

It complements the evaluation-flywheel idea: every failure or weak assumption
should tighten the next decision rule.

## References

- AWS ADR process:
  [https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html)
- OpenAI Cookbook, evaluation flywheel:
  [https://cookbook.openai.com/examples/evaluation/use-cases/building_resilient_prompts_using_an_evaluation_flywheel](https://cookbook.openai.com/examples/evaluation/use-cases/building_resilient_prompts_using_an_evaluation_flywheel)
