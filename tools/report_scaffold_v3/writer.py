from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from PIL import Image

from .models import (
    BuildResult,
    BuildSourceManifest,
    ImageBlockSpec,
    ImageRoleManifest,
    ParagraphBlockSpec,
    WriteContractManifest,
    WriteRoleManifest,
)


ALIGNMENTS = {
    "left": WD_ALIGN_PARAGRAPH.LEFT,
    "center": WD_ALIGN_PARAGRAPH.CENTER,
    "right": WD_ALIGN_PARAGRAPH.RIGHT,
    "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
}


class WriteContractError(ValueError):
    pass


def _clear_document_body(document: Document) -> None:
    body = document._body._element
    for child in list(body):
        if child.tag.endswith("}sectPr"):
            continue
        body.remove(child)


def _apply_paragraph_format(paragraph, role: WriteRoleManifest) -> None:
    paragraph.style = role.style
    paragraph_format = paragraph.paragraph_format
    alignment = role.paragraph_format.get("alignment")
    if alignment:
        paragraph.alignment = ALIGNMENTS[alignment]

    first_line_indent_pt = role.paragraph_format.get("first_line_indent_pt")
    if first_line_indent_pt is not None:
        paragraph_format.first_line_indent = Pt(first_line_indent_pt)

    left_indent_pt = role.paragraph_format.get("left_indent_pt")
    if left_indent_pt is not None:
        paragraph_format.left_indent = Pt(left_indent_pt)

    right_indent_pt = role.paragraph_format.get("right_indent_pt")
    if right_indent_pt is not None:
        paragraph_format.right_indent = Pt(right_indent_pt)

    line_spacing_multiple = role.paragraph_format.get("line_spacing_multiple")
    if line_spacing_multiple is not None:
        paragraph_format.line_spacing = float(line_spacing_multiple)

    space_before_pt = role.paragraph_format.get("space_before_pt")
    if space_before_pt is not None:
        paragraph_format.space_before = Pt(space_before_pt)

    space_after_pt = role.paragraph_format.get("space_after_pt")
    if space_after_pt is not None:
        paragraph_format.space_after = Pt(space_after_pt)


def _apply_run_format(run, role: WriteRoleManifest) -> None:
    run_format = role.run_format
    font_name = run_format.get("font_name")
    if font_name:
        run.font.name = font_name

    size_pt = run_format.get("size_pt")
    if size_pt is not None:
        run.font.size = Pt(size_pt)

    bold = run_format.get("bold")
    if bold is not None:
        run.bold = bool(bold)

    italic = run_format.get("italic")
    if italic is not None:
        run.italic = bool(italic)


def _natural_image_width_pt(image_path: Path) -> float:
    with Image.open(image_path) as image:
        dpi_x = image.info.get("dpi", (72, 72))[0] or 72
        return image.size[0] * 72.0 / float(dpi_x)


def _resolve_image_width(image_path: Path, role: ImageRoleManifest) -> Pt | None:
    if role.width_mode == "fixed_width_pt" and role.fixed_width_pt is not None:
        return Pt(role.fixed_width_pt)

    if role.width_mode == "fit_usable_body_width" and role.max_width_pt is not None:
        natural_width_pt = _natural_image_width_pt(image_path)
        return Pt(min(natural_width_pt, role.max_width_pt))

    return None


def _validate_contract_role(contract: WriteContractManifest, role_name: str) -> WriteRoleManifest:
    role = contract.paragraph_roles.get(role_name)
    if role is None:
        raise WriteContractError(f"Unknown paragraph role `{role_name}`.")
    return role


def _validate_image_role(contract: WriteContractManifest, role_name: str) -> ImageRoleManifest:
    role = contract.image_roles.get(role_name)
    if role is None:
        raise WriteContractError(f"Unknown image role `{role_name}`.")
    return role


def _render_paragraph(document: Document, block: ParagraphBlockSpec, role: WriteRoleManifest) -> None:
    paragraph = document.add_paragraph()
    _apply_paragraph_format(paragraph, role)
    run = paragraph.add_run(block.text)
    _apply_run_format(run, role)


def _render_image(
    document: Document,
    block: ImageBlockSpec,
    image_role: ImageRoleManifest,
    caption_role: WriteRoleManifest,
) -> None:
    width = _resolve_image_width(block.image_path, image_role)
    document.add_picture(str(block.image_path), width=width)
    image_paragraph = document.paragraphs[-1]
    if image_role.center_paragraph:
        image_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    caption = document.add_paragraph()
    _apply_paragraph_format(caption, caption_role)
    run = caption.add_run(block.caption)
    _apply_run_format(run, caption_role)


def parse_block_specs(source: BuildSourceManifest) -> list[ParagraphBlockSpec | ImageBlockSpec]:
    parsed_blocks: list[ParagraphBlockSpec | ImageBlockSpec] = []
    for block in source.blocks:
        kind = block.get("kind")
        if kind == "paragraph":
            parsed_blocks.append(ParagraphBlockSpec.model_validate(block))
            continue
        if kind == "image":
            parsed_blocks.append(ImageBlockSpec.model_validate(block))
            continue
        raise WriteContractError(f"Unsupported block kind `{kind}` in build source.")
    return parsed_blocks


def build_word_candidate(
    *,
    template_docx: Path,
    source: BuildSourceManifest,
    contract: WriteContractManifest,
    output_docx: Path,
) -> BuildResult:
    document = Document(str(template_docx))
    if contract.default_output_strategy.get("clear_existing_body_content", True):
        _clear_document_body(document)

    parsed_blocks = parse_block_specs(source)
    paragraph_count = 0
    image_count = 0

    for block in parsed_blocks:
        if isinstance(block, ParagraphBlockSpec):
            role = _validate_contract_role(contract, block.role)
            _render_paragraph(document, block, role)
            paragraph_count += 1
            continue

        image_role = _validate_image_role(contract, block.role)
        caption_role = _validate_contract_role(contract, image_role.caption_role)
        _render_image(document, block, image_role, caption_role)
        paragraph_count += 2
        image_count += 1

    output_docx.parent.mkdir(parents=True, exist_ok=True)
    document.save(str(output_docx))

    return BuildResult(
        document_id=source.document_id,
        template_docx=template_docx,
        output_docx=output_docx,
        block_count=len(parsed_blocks),
        paragraph_count=paragraph_count,
        image_count=image_count,
    )
