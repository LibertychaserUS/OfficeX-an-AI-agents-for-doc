# Template Contract

This document records the current Word template baseline used for precise font,
size, and layout control inside the document engineering platform.

Template source:

- [QUT-SQA-HP2R48-GU2-2023CSX-学号-姓名.docx](/Users/nihao/Desktop/LoopMart_Presentation/QUT-SQA-HP2R48-GU2-2023CSX-学号-姓名.docx)

Reference sample, not authoritative for formatting:

- [QUT-SQA-HP2R48-GU2-REPORT_final_20260330_v3(2).docx](/Users/nihao/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_2r9lp9dzjsqc22_8c54/msg/file/2026-03/QUT-SQA-HP2R48-GU2-REPORT_final_20260330_v3(2).docx)

This is a legacy imported sample template pair from the archived GU2 line.

The English template is the real formatting authority for that sample set. The
sample report remains useful for content density, figure usage, and evidence
layout patterns, but it must not be treated as the canonical product source for
page size, style hierarchy, or exact formatting rules outside that sample line.

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
  - font: `Times New Roman` / East Asia `宋体`
  - size: `10.5 pt`
  - alignment: justify
- `Plain Text`
  - based on `Normal`
  - font override: `宋体`
  - size inherits from `Normal`
- `Heading 1`
  - based on `Normal`
  - size: `24 pt`
  - bold
  - center aligned
  - East Asia font resolves to `黑体`
- `Heading 2`
  - based on `Normal`
  - size: `16 pt`
  - bold
  - left aligned
- `Subtitle`
  - based on `Normal`
  - size: `14 pt`
  - bold
  - left aligned
  - `3 pt` space after
  - East Asia font resolves to `等线 Light`
- `正文缩进1`
  - based on `Normal`
  - size: `12 pt`
  - first-line indent: `24 pt`
  - line spacing: `1.5`

## Precision Notes

- Some template properties are inherited instead of stored directly on every
  style.
- Reliable enforcement must resolve:
  - direct style properties
  - `basedOn` style inheritance
  - document defaults
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
