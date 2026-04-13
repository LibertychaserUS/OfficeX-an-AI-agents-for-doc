# CHECKPOINT_16

date: 2026-04-12

## Title

Python 3.11 runtime baseline uplift

## Summary

- Rebuilt the active OfficeX .venv on Homebrew python3.11.
- Raised requires-python to >=3.11 and added .python-version.
- Corrected the lockfile click pin for typer compatibility on Python 3.11.

## Verification

- check-package passed under Python 3.11.15.
- pytest -q passed with 156 tests.
- officex task run-docx-mvp and officex provider build-request passed under the rebuilt runtime.

## Follow-up

- Replace legacy-heavy revision regression coverage with OfficeX-native runtime tests.
