from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile

from lxml import etree

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

FONT_ALIASES = {
    "SimSun": "宋体",
    "SimHei": "黑体",
    "DengXian Light": "等线 Light",
}

STYLE_NAME_ALIASES = {
    "heading 1": "Heading 1",
    "heading 2": "Heading 2",
    "heading 3": "Heading 3",
    "heading 4": "Heading 4",
    "normal": "Normal",
    "plain text": "Plain Text",
    "subtitle": "Subtitle",
}


def canonical_font_name(name: str | None) -> str | None:
    if name is None:
        return None
    return FONT_ALIASES.get(name, name)


def canonical_style_name(name: str | None) -> str | None:
    if name is None:
        return None
    return STYLE_NAME_ALIASES.get(name.strip().lower(), name)


def _first(values: list[str]) -> str | None:
    return values[0] if values else None


def half_points_to_pt(value: str | None) -> float | None:
    if value is None:
        return None
    return int(value) / 2.0


def twips_to_pt(value: str | None) -> float | None:
    if value is None:
        return None
    return int(value) / 20.0


def _normalize_alignment(value: str | None) -> str | None:
    if value == "both":
        return "justify"
    return value


def _parse_bool(nodes) -> bool | None:
    if not nodes:
        return None
    node = nodes[0]
    value = node.get(f"{{{NS['w']}}}val")
    if value in {"0", "false", "off"}:
        return False
    return True


def _read_styles_root(docx_path: Path):
    with ZipFile(docx_path) as archive:
        return etree.fromstring(archive.read("word/styles.xml"))


def _parse_document_defaults(root) -> dict:
    default_rpr = root.xpath("./w:docDefaults/w:rPrDefault/w:rPr", namespaces=NS)
    if not default_rpr:
        return {}
    rpr = default_rpr[0]
    return {
        "ascii_font": canonical_font_name(_first(rpr.xpath("./w:rFonts/@w:ascii", namespaces=NS))),
        "hansi_font": canonical_font_name(_first(rpr.xpath("./w:rFonts/@w:hAnsi", namespaces=NS))),
        "east_asia_font": canonical_font_name(
            _first(rpr.xpath("./w:rFonts/@w:eastAsia", namespaces=NS))
        ),
        "size_pt": half_points_to_pt(_first(rpr.xpath("./w:sz/@w:val", namespaces=NS))),
        "size_cs_pt": half_points_to_pt(_first(rpr.xpath("./w:szCs/@w:val", namespaces=NS))),
    }


def _parse_raw_styles(root) -> dict[str, dict]:
    styles: dict[str, dict] = {}
    for style in root.xpath("./w:style", namespaces=NS):
        style_id = style.get(f"{{{NS['w']}}}styleId")
        name = canonical_style_name(_first(style.xpath("./w:name/@w:val", namespaces=NS)) or style_id)
        based_on = _first(style.xpath("./w:basedOn/@w:val", namespaces=NS))
        ppr = _first(style.xpath("./w:pPr", namespaces=NS))
        rpr = _first(style.xpath("./w:rPr", namespaces=NS))

        line_raw = _first(ppr.xpath("./w:spacing/@w:line", namespaces=NS)) if ppr is not None else None
        line_rule = _first(ppr.xpath("./w:spacing/@w:lineRule", namespaces=NS)) if ppr is not None else None
        line_spacing_multiple = None
        line_spacing_pt = None
        if line_raw is not None:
            if line_rule in {None, "auto"}:
                line_spacing_multiple = int(line_raw) / 240.0
            else:
                line_spacing_pt = twips_to_pt(line_raw)

        styles[style_id] = {
            "style_id": style_id,
            "name": name,
            "based_on": based_on,
            "ascii_font": canonical_font_name(
                _first(rpr.xpath("./w:rFonts/@w:ascii", namespaces=NS)) if rpr is not None else None
            ),
            "hansi_font": canonical_font_name(
                _first(rpr.xpath("./w:rFonts/@w:hAnsi", namespaces=NS)) if rpr is not None else None
            ),
            "east_asia_font": canonical_font_name(
                _first(rpr.xpath("./w:rFonts/@w:eastAsia", namespaces=NS)) if rpr is not None else None
            ),
            "size_pt": half_points_to_pt(
                _first(rpr.xpath("./w:sz/@w:val", namespaces=NS)) if rpr is not None else None
            ),
            "size_cs_pt": half_points_to_pt(
                _first(rpr.xpath("./w:szCs/@w:val", namespaces=NS)) if rpr is not None else None
            ),
            "bold": _parse_bool(rpr.xpath("./w:b", namespaces=NS) if rpr is not None else []),
            "alignment": _normalize_alignment(
                _first(ppr.xpath("./w:jc/@w:val", namespaces=NS)) if ppr is not None else None
            ),
            "left_indent_pt": twips_to_pt(
                _first(ppr.xpath("./w:ind/@w:left", namespaces=NS)) if ppr is not None else None
            ),
            "right_indent_pt": twips_to_pt(
                _first(ppr.xpath("./w:ind/@w:right", namespaces=NS)) if ppr is not None else None
            ),
            "first_line_indent_pt": twips_to_pt(
                _first(ppr.xpath("./w:ind/@w:firstLine", namespaces=NS)) if ppr is not None else None
            ),
            "first_line_chars": _first(
                ppr.xpath("./w:ind/@w:firstLineChars", namespaces=NS) if ppr is not None else []
            ),
            "space_before_pt": twips_to_pt(
                _first(ppr.xpath("./w:spacing/@w:before", namespaces=NS)) if ppr is not None else None
            ),
            "space_after_pt": twips_to_pt(
                _first(ppr.xpath("./w:spacing/@w:after", namespaces=NS)) if ppr is not None else None
            ),
            "line_spacing_multiple": line_spacing_multiple,
            "line_spacing_pt": line_spacing_pt,
        }
    return styles


def _merge_effective_value(raw: dict, parent: dict, key: str):
    if raw.get(key) is not None:
        return raw[key]
    return parent.get(key)


def _resolve_effective_styles(raw_styles: dict[str, dict], doc_defaults: dict) -> dict[str, dict]:
    resolved_by_id: dict[str, dict] = {}

    def resolve(style_id: str | None) -> dict:
        if not style_id:
            return {}
        if style_id in resolved_by_id:
            return resolved_by_id[style_id]

        raw = raw_styles[style_id]
        parent = resolve(raw["based_on"]) if raw.get("based_on") in raw_styles else {}

        effective = {
            "style_id": raw["style_id"],
            "name": raw["name"],
            "based_on": raw["based_on"],
            "ascii_font": _merge_effective_value(
                raw, parent or doc_defaults, "ascii_font"
            )
            or doc_defaults.get("ascii_font"),
            "hansi_font": _merge_effective_value(
                raw, parent or doc_defaults, "hansi_font"
            )
            or doc_defaults.get("hansi_font"),
            "east_asia_font": _merge_effective_value(
                raw, parent or doc_defaults, "east_asia_font"
            )
            or doc_defaults.get("east_asia_font"),
            "size_pt": _merge_effective_value(raw, parent or doc_defaults, "size_pt")
            or doc_defaults.get("size_pt"),
            "size_cs_pt": _merge_effective_value(raw, parent or doc_defaults, "size_cs_pt")
            or doc_defaults.get("size_cs_pt"),
            "bold": _merge_effective_value(raw, parent or {}, "bold"),
            "alignment": _merge_effective_value(raw, parent or {}, "alignment"),
            "left_indent_pt": _merge_effective_value(raw, parent or {}, "left_indent_pt"),
            "right_indent_pt": _merge_effective_value(raw, parent or {}, "right_indent_pt"),
            "first_line_indent_pt": _merge_effective_value(
                raw, parent or {}, "first_line_indent_pt"
            ),
            "first_line_chars": _merge_effective_value(raw, parent or {}, "first_line_chars"),
            "space_before_pt": _merge_effective_value(raw, parent or {}, "space_before_pt"),
            "space_after_pt": _merge_effective_value(raw, parent or {}, "space_after_pt"),
            "line_spacing_multiple": _merge_effective_value(
                raw, parent or {}, "line_spacing_multiple"
            ),
            "line_spacing_pt": _merge_effective_value(raw, parent or {}, "line_spacing_pt"),
        }
        resolved_by_id[style_id] = effective
        return effective

    for style_id in raw_styles:
        resolve(style_id)

    return {style["name"]: style for style in resolved_by_id.values()}


def build_style_inventory(docx_path: Path) -> dict:
    root = _read_styles_root(docx_path)
    doc_defaults = _parse_document_defaults(root)
    raw_styles = _parse_raw_styles(root)
    resolved_styles = _resolve_effective_styles(raw_styles, doc_defaults)
    return {
        "document_defaults": doc_defaults,
        "styles_by_name": resolved_styles,
        "styles_by_id": {style_id: resolved_styles[raw["name"]] for style_id, raw in raw_styles.items()},
    }
