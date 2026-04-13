# CHECKPOINT_01

date: 2026-04-11

## Title

Platform extraction baseline established

## Summary

- `Document Operations System` is now the active platform identity.
- Active development has moved to `/Users/nihao/Documents/Playground/document-ops-system`.
- `LoopMart-GU2-rebuild` has been preserved as an archived product workspace at `/Users/nihao/Documents/Playground/archive/products/loopmart/LoopMart-GU2-rebuild`.
- `LoopMart-legacy-archive` has been deleted and replaced by a tombstone record.
- Root governance has been reduced to thin workspace rules; platform governance now lives under the new platform root.

## Active Development Boundary

- Edit platform code and docs only under `/Users/nihao/Documents/Playground/document-ops-system` unless a task explicitly targets an archive.
- Treat `/Users/nihao/Documents/Playground/archive/products/loopmart/LoopMart-GU2-rebuild` as historical evidence by default.
- Use `/Users/nihao/Documents/Playground/document-ops-system/docs/ACTIVE_RULES_AND_PATHS.md` as the first path and rules reference.

## Compatibility Notes

- The product name is `Document Operations System`.
- The internal package and CLI module remain `tools.report_scaffold_v3` for compatibility during the migration phase.
- Historical GU2 and LoopMart traces remain in the archived product workspace and are not merged into the platform trace.

## Follow-up

- Build the new platform-local trace index and checkpoint catalog.
- Stand up a fresh platform-local environment before running full smoke checks.
