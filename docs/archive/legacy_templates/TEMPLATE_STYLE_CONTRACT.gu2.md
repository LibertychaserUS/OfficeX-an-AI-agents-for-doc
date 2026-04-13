# Template Style Contract

Source template:

- [QUT-SQA-HP2R48-GU2-2023CSX-学号-姓名.docx](/Users/nihao/Desktop/LoopMart_Presentation/QUT-SQA-HP2R48-GU2-2023CSX-学号-姓名.docx)

This is a legacy imported sample template from the archived GU2 line. It is a
useful style reference, not a universal product default.

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
- East Asian font: `宋体`
- Font size: `10.5 pt`
- Alignment: `JUSTIFY`

### `Heading 1`

- Font size: `24 pt`
- Bold: `true`
- Alignment: `CENTER`
- Used for stage-level titles such as `Stage 1 Planning`

### `Heading 2`

- Font size: `16 pt`
- Bold: `true`
- Used for part-level headings such as `Part A — Inception phase planning`

### `Subtitle`

- Font size: `14 pt`
- Bold: `true`
- Alignment: `LEFT`
- Space after: `3 pt`
- Used for numbered subsection headings such as `1.1 Project Description`

### `正文缩进1`

- Based on: `Normal`
- Font size: `12 pt`
- First-line indent: `24 pt`
- Line spacing: `1.5`
- Used for bracketed template guidance and indented body paragraphs

### `Plain Text`

- Based on: `Normal`
- Overrides Latin font to `宋体`
- Size is not explicit in the direct style record and should be resolved
  through inheritance from `Normal`
- Used on the cover/title page

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
the current final report does not exhibit overflow problems.

Minimum generic rules:

- Image width must not exceed usable page width
- Image + caption block must fit the remaining page area, or be flagged
- Caption should remain adjacent to the image block
- `keepWithNext` and `keepLines` policies should be available when patching
- Full-resolution diagrams should have an appendix-safe layout policy
