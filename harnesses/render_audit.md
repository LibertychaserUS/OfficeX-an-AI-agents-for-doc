# Render Audit Harness

Use this harness when the main risk is visual readability, pagination, blank
pages, caption splitting, abnormal whitespace, paper-size drift, or
renderer-specific layout drift.

## Inputs

- generated or revised candidate
- target page profile
- renderer or screenshot outputs when available

## Checks

- A4 or other required paper-size conformance
- figure and caption same-page binding
- heading and table-title adjacency
- abnormal whitespace or invisible-character artifacts
- font fallback or overflow risk
- renderer-specific drift between structural intent and visual result

## Outputs

- render findings
- residual risk note
- repair plan
