# ADR 0002: Revision Sidecar And Controlled Patch Mainline

## Status

Accepted

## Context

The platform already had:

1. a structured build/publish mainline,
2. a review verification map and issue ledger,
3. a one-off `candidate_revision.py` script for direct candidate mutation.

That left a gap between verified review issues and auditable candidate changes.
The one-off script could patch a candidate, but it did not provide:

- live anchor snapshots,
- revision patch specs,
- run-local execution reports,
- revision-specific audit semantics,
- a stable controlled patch mainline separate from build-source semantics.

## Decision

The platform adopts a dedicated revision sidecar inside the same package:

1. revision logic lives under `tools.report_scaffold_v3.revision.*`,
2. revision patch specs live under `manifests/revision/patches/`,
3. revision run artifacts live under `outputs/revision_runs/`,
4. controlled patch work follows this mainline:
   - `revision-extract-anchors`
   - `revision-build-patch`
   - `revision-apply-patch --dry-run`
   - `revision-apply-patch`
   - `revision-audit`
5. the revision sidecar does not change the contracts of:
   - `build-word`
   - `run-section-pipeline`
   - `publish-run`
   - build-candidate `check-candidate`

## Consequences

Positive:

- review feedback now becomes executable objects before document mutation,
- candidate-only revision runs are replayable and fail-closed,
- build/publish semantics remain stable,
- revision audit can reason about patch-mode candidates without pretending to be
  build-source validation.

Costs:

- the platform now owns a second sanctioned workflow,
- more contract, CLI, and test coverage is required,
- revision state and build state must remain intentionally separated.

## Current Implementation References

- [cli.py](/Users/nihao/Documents/Playground/document-ops-system/tools/report_scaffold_v3/cli.py)
- [revision](/Users/nihao/Documents/Playground/document-ops-system/tools/report_scaffold_v3/revision)
- [document_revision.md](/Users/nihao/Documents/Playground/document-ops-system/harnesses/document_revision.md)
- [WORKFLOW_OPERATING_MODEL.md](/Users/nihao/Documents/Playground/document-ops-system/docs/WORKFLOW_OPERATING_MODEL.md)
