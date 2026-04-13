# CHECKPOINT_02

date: 2026-04-12

## Title

Platform-local environment rebuilt and smoke checks passed

## Summary

- A fresh local environment was created at `/Users/nihao/Documents/Playground/document-ops-system/.venv`.
- Platform dependencies were installed into the new environment.
- Local smoke checks now pass without relying on archived runtime assets:
  - `check-package`
  - `pytest -q`
  - local wheel build

## Incidents Closed In This Stage

- Archived `.venv` Pillow native-library failure is now bypassed by policy and
  replacement.
- Homebrew Python is not required for active platform work.
- Wheel build tooling gap in a fresh environment has been corrected by adding
  `setuptools==80.9.0` and `wheel==0.45.1` to the lockfile.
- Residual legacy platform naming in tests has been removed from active smoke
  assertions.

## Active Boundary

- Use `/Users/nihao/Documents/Playground/document-ops-system/.venv` for active
  platform commands.
- Do not run smoke checks from archived virtual environments.
- Continue treating archived LoopMart paths as historical reference only.

## Follow-up

- Keep the engineering issues register current as new failures or design risks
  are discovered.
- Decide when to turn compatibility-package migration into a dedicated product
  branch.
