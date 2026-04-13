# Template Style Contract

Current source template:

- [officex_docx_mvp_template.docx](/Users/nihao/Documents/Playground/document-ops-system/imports/samples/officex_docx_mvp_template.docx)

Legacy case-specific style records were archived to:

- [TEMPLATE_STYLE_CONTRACT.gu2.md](/Users/nihao/Documents/Playground/document-ops-system/docs/archive/legacy_templates/TEMPLATE_STYLE_CONTRACT.gu2.md)

## Purpose

This contract records the effective page, style, font, size, alignment, and
paragraph-position rules that the platform should enforce when template
compliance matters.

## Page Geometry

- Page size: A4
- Width: `595.3 pt`
- Height: `841.9 pt`
- Top margin: `70.9 pt`
- Bottom margin: `70.9 pt`
- Left margin: `70.9 pt`
- Right margin: `70.9 pt`
- Header distance: `42.55 pt`
- Footer distance: `42.55 pt`

## Style Baseline

### `Normal`

- Latin font: `Times New Roman`
- East Asian font: `Times New Roman`
- Font size: `11 pt`
- Alignment: `JUSTIFY`

### `Heading 1`

- Font size: `14 pt`
- Bold: `true`
- Alignment: `CENTER`
- Used for primary document headings in the neutral MVP sample

### `Heading 2`

- Font size: `13 pt`
- Bold: `true`
- Used for second-level document headings in the neutral MVP sample

### `Subtitle`

- Font size: `14 pt`
- Bold: `false`
- Alignment: `LEFT`
- Space after: `3 pt`
- Used for optional subsection or contextual heading blocks

### `Indented Body`

- Based on: `Normal`
- Font size: `11 pt`
- First-line indent: `24 pt`
- Line spacing: `1.5`
- Used for indented body paragraphs and controlled dense prose blocks

### `Plain Text`

- Based on: `Normal`
- Keeps `Times New Roman`
- Size is not explicit in the direct style record and should be resolved
  through inheritance from `Normal`
- Used for structure-preserving plain body text

## Exactness Caveats

The platform should not trust `python-docx` alone for final style compliance,
because some values are inherited or theme-driven. Exact validation needs these
layers resolved in order:

1. Direct paragraph/run formatting
2. Paragraph style
3. Base style via `basedOn`
4. `docDefaults`
5. Theme font mapping
6. East Asian font fallback rules

## Required Scaffold Checks

- Effective font family, not only direct style font
- Effective font size, not only direct style size
- Paragraph alignment
- First-line indent / left indent
- Space before / after
- Line spacing
- Page geometry and margin compliance
- Section-specific page settings
- Image width and height against usable page area
- Caption placement relative to image paragraph

## Image/Layout Rule Direction

The platform must support precise image size and placement control even when
the current MVP sample does not exhibit overflow problems.

Minimum generic rules:

- Image width must not exceed usable page width
- Image + caption block must fit the remaining page area, or be flagged
- Caption should remain adjacent to the image block
- `keepWithNext` and `keepLines` policies should be available when patching
- Full-resolution diagrams should have an appendix-safe layout policy
