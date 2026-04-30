from __future__ import annotations

import os
import plistlib
import shutil
import subprocess
from pathlib import Path

from .paths import DEFAULT_OFFICEX_DESKTOP_SHELL_DIR


def default_machine_settings_dir() -> Path:
    override = os.environ.get("OFFICEX_SETTINGS_DIR")
    if override:
        return Path(override).expanduser().resolve()
    return (Path.home() / "Library" / "Application Support" / "OfficeX").resolve()


def resolve_desktop_shell_dir(explicit_dir: Path | None = None) -> Path:
    if explicit_dir is not None:
        return explicit_dir.expanduser().resolve()
    return DEFAULT_OFFICEX_DESKTOP_SHELL_DIR.expanduser().resolve()


def detect_bun_binary() -> str | None:
    return shutil.which("bun")


def detect_word_app() -> Path | None:
    override = os.environ.get("OFFICEX_WORD_APP_PATH")
    candidates = [
        Path(override).expanduser().resolve() if override else None,
        Path("/Applications/Microsoft Word.app"),
        Path.home() / "Applications" / "Microsoft Word.app",
    ]
    for candidate in candidates:
        if candidate is not None and candidate.exists():
            return candidate
    return None


def read_macos_app_version(app_path: Path | None) -> str | None:
    if app_path is None:
        return None
    info_plist = app_path / "Contents" / "Info.plist"
    if not info_plist.exists():
        return None
    try:
        with info_plist.open("rb") as handle:
            payload = plistlib.load(handle)
    except Exception:
        return None
    version = payload.get("CFBundleShortVersionString") or payload.get("CFBundleVersion")
    return str(version) if version is not None else None


def detect_provider_config_state() -> dict[str, object]:
    configured_sources: list[str] = []
    if os.environ.get("OPENAI_API_KEY"):
        configured_sources.append("OPENAI_API_KEY")
    if os.environ.get("ANTHROPIC_API_KEY"):
        configured_sources.append("ANTHROPIC_API_KEY")
    return {
        "configured": bool(configured_sources),
        "sources": configured_sources,
    }


def find_packaged_app_bundle(desktop_shell_dir: Path) -> Path | None:
    candidates = [
        desktop_shell_dir / "dist" / "OfficeX.app",
        desktop_shell_dir / "out" / "OfficeX.app",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def find_built_shell_entry(desktop_shell_dir: Path) -> Path | None:
    required_paths = [
        desktop_shell_dir / "out" / "main" / "index.js",
        desktop_shell_dir / "out" / "preload" / "index.cjs",
        desktop_shell_dir / "out" / "renderer" / "index.html",
    ]
    if all(candidate.exists() for candidate in required_paths):
        return required_paths[0]
    return None


def find_electron_binary(desktop_shell_dir: Path) -> Path | None:
    candidates = [
        desktop_shell_dir / "node_modules" / ".bin" / "electron",
        desktop_shell_dir
        / "node_modules"
        / "electron"
        / "dist"
        / "Electron.app"
        / "Contents"
        / "MacOS"
        / "Electron",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def ensure_built_shell(desktop_shell_dir: Path, bun_binary: str) -> Path:
    built_entry = find_built_shell_entry(desktop_shell_dir)
    if built_entry is not None:
        return built_entry

    subprocess.run(
        [bun_binary, "run", "build"],
        cwd=desktop_shell_dir,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    built_entry = find_built_shell_entry(desktop_shell_dir)
    if built_entry is None:
        raise RuntimeError(
            "OfficeX desktop build completed but the built shell entry is still missing."
        )
    return built_entry


def launch_desktop_shell(desktop_shell_dir: Path) -> Path:
    packaged_bundle = find_packaged_app_bundle(desktop_shell_dir)
    if packaged_bundle is not None:
        subprocess.Popen(
            ["open", str(packaged_bundle)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return packaged_bundle

    package_json = desktop_shell_dir / "package.json"
    if not package_json.exists():
        raise RuntimeError(
            f"OfficeX desktop shell is missing package.json at `{desktop_shell_dir}`."
        )

    electron_binary = find_electron_binary(desktop_shell_dir)
    if electron_binary is None:
        raise RuntimeError(
            "OfficeX desktop dependencies are incomplete. Run `bun install` inside the desktop shell first."
        )

    bun_binary = detect_bun_binary()
    if bun_binary is None:
        raise RuntimeError("Bun is not available. Install Bun before launching OfficeX.")

    built_entry = ensure_built_shell(desktop_shell_dir, bun_binary)

    subprocess.Popen(
        [str(electron_binary), str(built_entry)],
        cwd=desktop_shell_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    return built_entry
