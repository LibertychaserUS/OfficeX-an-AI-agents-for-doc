# Document Generation Harness

Use this harness when managed sources need to become a generated candidate.

## Inputs

- managed sections, figures, citations, or snippets
- template and write contracts
- page and style contracts
- target output directory

## Outputs

- build source
- candidate document
- validation report

## Guardrails

- do not skip manifests
- do not let AI directly own final Office-structure mutation
- treat `docx` structure, styles, numbering, and layout as programmatic outputs
- state the page profile explicitly when it matters
- do not publish as a side effect
- state whether the result is structural, semantic, or mixed
