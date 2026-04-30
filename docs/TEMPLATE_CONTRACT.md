# Template Contract

This document records the current Word template baseline used for precise font,
size, and layout control inside the document engineering platform.

Current neutral platform template source:

- [officex_docx_mvp_template.docx](/Users/nihao/Documents/Playground/document-ops-system/imports/samples/officex_docx_mvp_template.docx)

Current baseline role:

- neutral platform-owned formatting authority and reference sample for the
  `OfficeX` `docx` MVP

## Page Geometry

- Paper size: A4
- Page width: `595.3 pt`
- Page height: `841.9 pt`
- Margins:
  - top `70.9 pt`
  - bottom `70.9 pt`
  - left `70.9 pt`
  - right `70.9 pt`
- Header distance: `42.55 pt`
- Footer distance: `42.55 pt`
- Usable body width: `453.5 pt`
- Usable body height: `700.1 pt`

## Effective Style Baseline

- `Normal`
  - font: `Times New Roman`
  - size: `11 pt`
  - alignment: justify
- `Plain Text`
  - based on `Normal`
  - font: `Times New Roman`
  - size inherits from `Normal`
- `Heading 1`
  - based on `Normal`
  - size: `14 pt`
  - bold
  - center aligned
  - uses theme-major heading font mapping
- `Heading 2`
  - based on `Normal`
  - size: `13 pt`
  - bold
  - left aligned
- `Subtitle`
  - based on `Normal`
  - size: `14 pt`
  - not forced bold by default
  - left aligned
  - `3 pt` space after
- `Indented Body`
  - based on `Normal`
  - size: `11 pt`
  - first-line indent: `24 pt`
  - line spacing: `1.5`

## Precision Notes

- Some template properties are inherited instead of stored directly on every
  style.
- Reliable enforcement must resolve:
  - direct style properties
  - `basedOn` style inheritance
  - document defaults
  - theme font mapping
  - paragraph/run overrides
- `python-docx` is useful for high-level access, but exact effective values may
  require OOXML inspection when a value appears as `None`.

## Platform Implication

The platform should not only check text content. It should also eventually
validate:

- font family
- font size
- paragraph alignment
- indentation
- spacing
- page geometry
- image fit against usable body area
- image-caption proximity and page safety
- sandbox-copy integrity before promoting edited candidates
