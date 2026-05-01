"""Profile management: list, switch, and create document profiles.

Profiles are named directories under manifests/profiles/ containing
template_profile.yml, write_contract.yml, and layout_contract.yml.
The active profile's manifests are symlinked (or copied) to the
manifests/ root for the current session.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from .paths import PACKAGE_DIR

logger = logging.getLogger(__name__)

MANIFESTS_DIR = PACKAGE_DIR.parent.parent / "manifests"
PROFILES_DIR = MANIFESTS_DIR / "profiles"
PROFILE_MANIFESTS = ["template_profile.yml", "write_contract.yml", "layout_contract.yml"]


def list_profiles() -> list[dict]:
    """List all available profiles with their key attributes."""
    profiles = []
    if not PROFILES_DIR.is_dir():
        return profiles

    for profile_dir in sorted(PROFILES_DIR.iterdir()):
        if not profile_dir.is_dir():
            continue
        tp_path = profile_dir / "template_profile.yml"
        info: dict = {
            "profile_id": profile_dir.name,
            "path": str(profile_dir),
            "has_template_profile": tp_path.exists(),
            "has_write_contract": (profile_dir / "write_contract.yml").exists(),
            "has_layout_contract": (profile_dir / "layout_contract.yml").exists(),
        }

        # Read key attributes from template_profile if available
        if tp_path.exists():
            import yaml
            try:
                data = yaml.safe_load(tp_path.read_text(encoding="utf-8")) or {}
                page = data.get("page_setup", {})
                defaults = data.get("document_defaults", {})
                info["page_width_pt"] = page.get("page_width_pt")
                info["page_height_pt"] = page.get("page_height_pt")
                info["default_font"] = defaults.get("ascii_font", "")
                info["template_id"] = data.get("template_id", "")
            except Exception:
                pass

        profiles.append(info)

    return profiles


def get_active_profile_id() -> str | None:
    """Detect which profile is currently active by comparing manifest content."""
    tp_root = MANIFESTS_DIR / "template_profile.yml"
    if not tp_root.exists():
        return None

    root_content = tp_root.read_text(encoding="utf-8")
    for profile_dir in PROFILES_DIR.iterdir():
        if not profile_dir.is_dir():
            continue
        tp_profile = profile_dir / "template_profile.yml"
        if tp_profile.exists() and tp_profile.read_text(encoding="utf-8") == root_content:
            return profile_dir.name
    return None


def activate_profile(profile_id: str) -> dict:
    """Activate a profile by copying its manifests to the root manifests/ dir.

    Returns a dict with the profile info and which files were updated.
    """
    profile_dir = PROFILES_DIR / profile_id
    if not profile_dir.is_dir():
        available = [p.name for p in PROFILES_DIR.iterdir() if p.is_dir()]
        raise ValueError(
            f"Profile `{profile_id}` not found. "
            f"Available: {', '.join(available) if available else 'none'}"
        )

    updated_files = []
    for manifest_name in PROFILE_MANIFESTS:
        src = profile_dir / manifest_name
        dst = MANIFESTS_DIR / manifest_name
        if src.exists():
            shutil.copy2(str(src), str(dst))
            updated_files.append(manifest_name)

    return {
        "profile_id": profile_id,
        "path": str(profile_dir),
        "updated_files": updated_files,
    }


def create_profile(
    profile_id: str,
    *,
    page_width_pt: float,
    page_height_pt: float,
    margin_pt: float = 72.0,
    font: str = "Arial",
    font_size_pt: float = 11.0,
    line_spacing: float = 1.08,
) -> dict:
    """Create a new profile from parameters.

    This is the self-evolution entry point: users or AI can create new
    profiles at runtime without editing existing files.
    """
    import yaml

    profile_dir = PROFILES_DIR / profile_id
    if profile_dir.exists():
        raise FileExistsError(f"Profile `{profile_id}` already exists at {profile_dir}")

    profile_dir.mkdir(parents=True)

    usable_width = round(page_width_pt - 2 * margin_pt, 1)
    usable_height = round(page_height_pt - 2 * margin_pt, 1)

    template_profile = {
        "schema_version": 1,
        "template_id": f"officex-{profile_id}",
        "source_template_docx": None,
        "page_setup": {
            "page_width_pt": page_width_pt,
            "page_height_pt": page_height_pt,
            "top_margin_pt": margin_pt,
            "bottom_margin_pt": margin_pt,
            "left_margin_pt": margin_pt,
            "right_margin_pt": margin_pt,
            "header_distance_pt": round(margin_pt / 2, 2),
            "footer_distance_pt": round(margin_pt / 2, 2),
            "usable_body_width_pt": usable_width,
            "usable_body_height_pt": usable_height,
        },
        "document_defaults": {
            "ascii_font": font,
            "hansi_font": font,
            "east_asia_font": font,
            "explicit_default_size_pt": font_size_pt,
        },
        "style_contract": {
            "Normal": {
                "based_on": None,
                "effective_font": {"ascii": font, "east_asia": font},
                "effective_size_pt": font_size_pt,
                "bold": False,
                "alignment": "justify",
                "first_line_indent_pt": 0,
                "line_spacing_multiple": line_spacing,
                "space_before_pt": 0,
                "space_after_pt": round(font_size_pt * 0.5, 1),
            },
            "Heading 1": {
                "based_on": "Normal",
                "effective_font": {"ascii": font, "east_asia": font},
                "effective_size_pt": round(font_size_pt * 1.45, 1),
                "bold": True,
                "alignment": "left",
                "space_before_pt": round(font_size_pt * 1.1, 1),
                "space_after_pt": round(font_size_pt * 0.5, 1),
            },
            "Heading 2": {
                "based_on": "Normal",
                "effective_font": {"ascii": font, "east_asia": font},
                "effective_size_pt": round(font_size_pt * 1.27, 1),
                "bold": True,
                "alignment": "left",
                "space_before_pt": round(font_size_pt * 0.9, 1),
                "space_after_pt": round(font_size_pt * 0.36, 1),
            },
        },
    }

    write_contract = {
        "schema_version": 1,
        "template_id": f"officex-{profile_id}",
        "default_output_strategy": {
            "base_document": "format_authority_docx",
            "preserve_template_sections": True,
            "clear_existing_body_content": True,
        },
        "paragraph_roles": {
            "heading_1": {
                "style": "Heading 1",
                "paragraph_format": {"alignment": "left"},
                "run_format": {},
                "allow_mixed_runs": False,
            },
            "heading_2": {
                "style": "Heading 2",
                "paragraph_format": {"alignment": "left"},
                "run_format": {},
                "allow_mixed_runs": False,
            },
            "body": {
                "style": "Normal",
                "paragraph_format": {"alignment": "justify"},
                "run_format": {},
            },
            "figure_caption": {
                "style": "Normal",
                "paragraph_format": {"alignment": "center"},
                "run_format": {"size_pt": round(font_size_pt * 0.9, 1)},
                "allow_mixed_runs": False,
            },
        },
        "image_roles": {
            "figure": {
                "caption_role": "figure_caption",
                "width_mode": "fit_usable_body_width",
                "max_width_pt": usable_width,
                "center_paragraph": True,
            },
        },
        "guardrails": {
            "reject_unknown_roles": True,
            "strip_template_body_content_before_write": True,
            "write_from_rules_not_from_sample_fit": True,
        },
    }

    layout_contract = {
        "schema_version": 1,
        "template_id": f"officex-{profile_id}",
        "image_layout_rules": {
            "usable_body_width_pt": usable_width,
            "usable_body_height_pt": usable_height,
            "reserve_caption_space_pt": 48.0,
            "reserve_bottom_buffer_pt": 24.0,
        },
    }

    for filename, data in [
        ("template_profile.yml", template_profile),
        ("write_contract.yml", write_contract),
        ("layout_contract.yml", layout_contract),
    ]:
        (profile_dir / filename).write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )

    # ---- Validate the newly created profile ----
    validation_issues = validate_profile(profile_id)
    if validation_issues:
        logger.warning("New profile `%s` has validation issues: %s", profile_id, validation_issues)

    return {
        "profile_id": profile_id,
        "path": str(profile_dir),
        "page_size": f"{page_width_pt}x{page_height_pt}pt",
        "font": font,
        "font_size_pt": font_size_pt,
        "files_created": PROFILE_MANIFESTS,
        "validation_issues": validation_issues,
    }


def validate_profile(profile_id: str) -> list[str]:
    """Validate a profile's manifests for structural correctness.

    Returns a list of issue descriptions. Empty list = valid.
    """
    profile_dir = PROFILES_DIR / profile_id
    issues: list[str] = []

    if not profile_dir.is_dir():
        return [f"Profile directory not found: {profile_dir}"]

    # Check all required files exist
    for manifest_name in PROFILE_MANIFESTS:
        if not (profile_dir / manifest_name).exists():
            issues.append(f"Missing {manifest_name}")

    # Validate template_profile
    tp_path = profile_dir / "template_profile.yml"
    if tp_path.exists():
        import yaml
        try:
            data = yaml.safe_load(tp_path.read_text(encoding="utf-8")) or {}
            page = data.get("page_setup", {})

            # Page dimensions must be positive
            for key in ("page_width_pt", "page_height_pt"):
                val = page.get(key)
                if val is None or val <= 0:
                    issues.append(f"template_profile: {key} must be positive, got {val}")

            # Margins must not exceed page dimensions
            width = page.get("page_width_pt", 0)
            height = page.get("page_height_pt", 0)
            left = page.get("left_margin_pt", 0)
            right = page.get("right_margin_pt", 0)
            top = page.get("top_margin_pt", 0)
            bottom = page.get("bottom_margin_pt", 0)
            if left + right >= width:
                issues.append(f"template_profile: horizontal margins ({left}+{right}) >= page width ({width})")
            if top + bottom >= height:
                issues.append(f"template_profile: vertical margins ({top}+{bottom}) >= page height ({height})")

            # Must have at least Normal style
            styles = data.get("style_contract", {})
            if "Normal" not in styles:
                issues.append("template_profile: style_contract must define Normal style")

        except Exception as exc:
            issues.append(f"template_profile: parse error: {exc}")

    # Validate write_contract
    wc_path = profile_dir / "write_contract.yml"
    if wc_path.exists():
        import yaml
        try:
            data = yaml.safe_load(wc_path.read_text(encoding="utf-8")) or {}
            roles = data.get("paragraph_roles", {})
            if not roles:
                issues.append("write_contract: no paragraph_roles defined")
            if "body" not in roles and "heading_1" not in roles:
                issues.append("write_contract: should define at least body or heading_1 role")
        except Exception as exc:
            issues.append(f"write_contract: parse error: {exc}")

    return issues
