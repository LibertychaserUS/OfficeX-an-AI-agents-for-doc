# ADR 0001: Role Semantics And Canonical Publication

## Status

Accepted

## Context

The platform encountered three related process problems:

1. explicit candidate docx paths could validate under `ad_hoc` instead of
   `candidate_output`,
2. dependent stages could be replayed manually in mixed order,
3. temp-path test runs could overwrite canonical shared summaries.

These issues did not always break the validator core, but they weakened the
meaning of passing results and made fallout harder.

## Decision

The platform adopts these rules:

1. document role is an architectural input, not a cosmetic label,
2. dependent chains must be owned by sanctioned orchestration commands,
3. run-local summaries follow the artifact they describe,
4. canonical shared summaries are updated only from canonical output roots,
5. a passing result must be interpreted in the context of the document role
   that produced it.

## Consequences

Positive:

- candidate validation claims become stronger and less ambiguous,
- pipeline replay becomes easier and less operator-dependent,
- temp-path tests stop polluting canonical summaries,
- fallout can distinguish structural engine correctness from command semantics
  more precisely.

Costs:

- the CLI layer becomes more important to architectural correctness,
- more tests are needed for role inference and publication behavior,
- canonical publication should eventually become an explicit publish command.

## Current Implementation References

- [cli.py](/Users/nihao/Documents/Playground/document-ops-system/tools/report_scaffold_v3/cli.py)
- [section_pipeline.py](/Users/nihao/Documents/Playground/document-ops-system/tools/report_scaffold_v3/section_pipeline.py)
- [test_cli.py](/Users/nihao/Documents/Playground/document-ops-system/tests/test_cli.py)
- [WORKFLOW_OPERATING_MODEL.md](/Users/nihao/Documents/Playground/document-ops-system/docs/WORKFLOW_OPERATING_MODEL.md)
