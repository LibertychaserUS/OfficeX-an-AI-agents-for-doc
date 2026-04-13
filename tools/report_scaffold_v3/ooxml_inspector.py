from __future__ import annotations

from pathlib import Path
from typing import Optional
from zipfile import ZipFile

from docx import Document
from lxml import etree

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
FONT_ALIASES = {
    "SimSun": "宋体",
    "SimHei": "黑体",
    "DengXian Light": "等线 Light",
    "DengXianLight": "等线 Light",
}
STYLE_ALIASES = {
    "heading 1": "Heading 1",
    "heading 2": "Heading 2",
    "heading 3": "Heading 3",
    "heading 4": "Heading 4",
    "normal": "Normal",
    "plain text": "Plain Text",
    "subtitle": "Subtitle",
}


def normalize_font_name(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return FONT_ALIASES.get(value, value)


def normalize_style_name(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return STYLE_ALIASES.get(value.strip().lower(), value)


def half_points_to_pt(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    return int(value) / 2.0


def twips_to_pt(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    return int(value) / 20.0


def first_or_none(values: list[str]) -> Optional[str]:
    return values[0] if values else None


def normalize_font_name(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = value.strip()
    aliases = {
        "宋体": "SimSun",
        "黑体": "SimHei",
        "等线 Light": "DengXian Light",
    }
    return aliases.get(normalized, normalized)


def parse_on_off(element, xpath: str) -> Optional[bool]:
    nodes = element.xpath(xpath, namespaces=NS)
    if not nodes:
        return None
    node = nodes[0]
    raw = node.get(f"{W_NS}val")
    if raw is None:
        return True
    if raw.lower() in {"0", "false", "off"}:
        return False
    return True


def load_styles_root(docx_path: Path):
    with ZipFile(docx_path) as archive:
        return etree.fromstring(archive.read("word/styles.xml"))


def parse_doc_defaults(root) -> dict:
    rpr_nodes = root.xpath("./w:docDefaults/w:rPrDefault/w:rPr", namespaces=NS)
    if not rpr_nodes:
        return {}
    rpr = rpr_nodes[0]
    return {
        "ascii_font": normalize_font_name(first_or_none(rpr.xpath("./w:rFonts/@w:ascii", namespaces=NS))),
        "hansi_font": normalize_font_name(first_or_none(rpr.xpath("./w:rFonts/@w:hAnsi", namespaces=NS))),
        "east_asia_font": normalize_font_name(first_or_none(rpr.xpath("./w:rFonts/@w:eastAsia", namespaces=NS))),
        "size_pt": half_points_to_pt(first_or_none(rpr.xpath("./w:sz/@w:val", namespaces=NS))),
        "complex_size_pt": half_points_to_pt(
            first_or_none(rpr.xpath("./w:szCs/@w:val", namespaces=NS))
        ),
        "bold": parse_on_off(rpr, "./w:b"),
    }


def parse_style_catalog(root) -> tuple[dict, dict]:
    styles_by_id = {}
    style_ids_by_name = {}
    for style in root.xpath("./w:style[@w:type='paragraph']", namespaces=NS):
        style_id = style.get(f"{W_NS}styleId")
        name = first_or_none(style.xpath("./w:name/@w:val", namespaces=NS))
        based_on = first_or_none(style.xpath("./w:basedOn/@w:val", namespaces=NS))
        rpr_nodes = style.xpath("./w:rPr", namespaces=NS)
        ppr_nodes = style.xpath("./w:pPr", namespaces=NS)
        rpr = rpr_nodes[0] if rpr_nodes else None
        ppr = ppr_nodes[0] if ppr_nodes else None

        styles_by_id[style_id] = {
            "style_id": style_id,
            "name": name or style_id,
            "based_on": based_on,
            "raw": {
                "ascii_font": None
                if rpr is None
                else normalize_font_name(first_or_none(rpr.xpath("./w:rFonts/@w:ascii", namespaces=NS))),
                "hansi_font": None
                if rpr is None
                else normalize_font_name(first_or_none(rpr.xpath("./w:rFonts/@w:hAnsi", namespaces=NS))),
                "east_asia_font": None
                if rpr is None
                else normalize_font_name(first_or_none(rpr.xpath("./w:rFonts/@w:eastAsia", namespaces=NS))),
                "size_pt": None
                if rpr is None
                else half_points_to_pt(first_or_none(rpr.xpath("./w:sz/@w:val", namespaces=NS))),
                "complex_size_pt": None
                if rpr is None
                else half_points_to_pt(
                    first_or_none(rpr.xpath("./w:szCs/@w:val", namespaces=NS))
                ),
                "bold": None if rpr is None else parse_on_off(rpr, "./w:b"),
                "alignment": None
                if ppr is None
                else first_or_none(ppr.xpath("./w:jc/@w:val", namespaces=NS)),
                "left_indent_pt": None
                if ppr is None
                else twips_to_pt(first_or_none(ppr.xpath("./w:ind/@w:left", namespaces=NS))),
                "right_indent_pt": None
                if ppr is None
                else twips_to_pt(first_or_none(ppr.xpath("./w:ind/@w:right", namespaces=NS))),
                "first_line_indent_pt": None
                if ppr is None
                else twips_to_pt(
                    first_or_none(ppr.xpath("./w:ind/@w:firstLine", namespaces=NS))
                ),
                "first_line_chars": None
                if ppr is None
                else first_or_none(ppr.xpath("./w:ind/@w:firstLineChars", namespaces=NS)),
                "space_before_pt": None
                if ppr is None
                else twips_to_pt(
                    first_or_none(ppr.xpath("./w:spacing/@w:before", namespaces=NS))
                ),
                "space_after_pt": None
                if ppr is None
                else twips_to_pt(
                    first_or_none(ppr.xpath("./w:spacing/@w:after", namespaces=NS))
                ),
                "line_spacing_raw": None
                if ppr is None
                else first_or_none(ppr.xpath("./w:spacing/@w:line", namespaces=NS)),
                "line_rule": None
                if ppr is None
                else first_or_none(ppr.xpath("./w:spacing/@w:lineRule", namespaces=NS)),
            },
        }
        if name:
            style_ids_by_name[normalize_style_name(name)] = style_id
    return styles_by_id, style_ids_by_name


def resolve_effective_style(style_id: str, styles_by_id: dict, doc_defaults: dict, cache: dict) -> dict:
    if style_id in cache:
        return cache[style_id]

    style = styles_by_id[style_id]
    raw = style["raw"]
    parent = (
        resolve_effective_style(style["based_on"], styles_by_id, doc_defaults, cache)
        if style["based_on"] and style["based_on"] in styles_by_id
        else {}
    )

    line_spacing_multiple = None
    if raw["line_spacing_raw"] is not None and raw["line_rule"] == "auto":
        line_spacing_multiple = int(raw["line_spacing_raw"]) / 240.0

    effective = {
        "style_id": style["style_id"],
        "name": style["name"],
        "based_on": style["based_on"],
        "ascii_font": raw["ascii_font"]
        or parent.get("ascii_font")
        or doc_defaults.get("ascii_font"),
        "hansi_font": raw["hansi_font"]
        or parent.get("hansi_font")
        or doc_defaults.get("hansi_font"),
        "east_asia_font": raw["east_asia_font"]
        or parent.get("east_asia_font")
        or doc_defaults.get("east_asia_font"),
        "size_pt": raw["size_pt"] if raw["size_pt"] is not None else parent.get("size_pt"),
        "complex_size_pt": raw["complex_size_pt"]
        if raw["complex_size_pt"] is not None
        else parent.get("complex_size_pt", doc_defaults.get("complex_size_pt")),
        "bold": raw["bold"] if raw["bold"] is not None else parent.get("bold", False),
        "alignment": raw["alignment"] if raw["alignment"] is not None else parent.get("alignment"),
        "left_indent_pt": raw["left_indent_pt"]
        if raw["left_indent_pt"] is not None
        else parent.get("left_indent_pt", 0.0),
        "right_indent_pt": raw["right_indent_pt"]
        if raw["right_indent_pt"] is not None
        else parent.get("right_indent_pt", 0.0),
        "first_line_indent_pt": raw["first_line_indent_pt"]
        if raw["first_line_indent_pt"] is not None
        else parent.get("first_line_indent_pt", 0.0),
        "first_line_chars": raw["first_line_chars"]
        if raw["first_line_chars"] is not None
        else parent.get("first_line_chars"),
        "space_before_pt": raw["space_before_pt"]
        if raw["space_before_pt"] is not None
        else parent.get("space_before_pt", 0.0),
        "space_after_pt": raw["space_after_pt"]
        if raw["space_after_pt"] is not None
        else parent.get("space_after_pt", 0.0),
        "line_rule": raw["line_rule"] if raw["line_rule"] is not None else parent.get("line_rule"),
        "line_spacing_multiple": line_spacing_multiple
        if line_spacing_multiple is not None
        else parent.get("line_spacing_multiple", 1.0),
    }
    cache[style_id] = effective
    return effective


def inspect_effective_styles(docx_path: Path) -> dict:
    root = load_styles_root(docx_path)
    doc_defaults = parse_doc_defaults(root)
    styles_by_id, style_ids_by_name = parse_style_catalog(root)
    cache = {}
    effective_by_name = {}
    for style_name, style_id in style_ids_by_name.items():
        effective_by_name[normalize_style_name(style_name)] = resolve_effective_style(
            style_id, styles_by_id, doc_defaults, cache
        )
    return {"document_defaults": doc_defaults, "styles": effective_by_name}


def extract_effective_style_inventory(docx_path: Path) -> dict:
    return inspect_effective_styles(docx_path)


def inspect_section_page_setup(docx_path: Path) -> list[dict]:
    document = Document(str(docx_path))
    sections = []
    for index, section in enumerate(document.sections):
        sections.append(
            {
                "index": index,
                "page_width_pt": round(section.page_width.pt, 2),
                "page_height_pt": round(section.page_height.pt, 2),
                "top_margin_pt": round(section.top_margin.pt, 2),
                "bottom_margin_pt": round(section.bottom_margin.pt, 2),
                "left_margin_pt": round(section.left_margin.pt, 2),
                "right_margin_pt": round(section.right_margin.pt, 2),
                "header_distance_pt": round(section.header_distance.pt, 2),
                "footer_distance_pt": round(section.footer_distance.pt, 2),
            }
        )
    return sections
