from __future__ import annotations

import subprocess
from pathlib import Path

from tools.report_scaffold_v3 import product_common


def test_launch_desktop_shell_prefers_packaged_bundle(monkeypatch):
    desktop_dir = Path("/tmp/officex-desktop")
    packaged_bundle = desktop_dir / "dist" / "OfficeX.app"
    launched: list[list[str]] = []

    monkeypatch.setattr(product_common, "find_packaged_app_bundle", lambda _: packaged_bundle)
    monkeypatch.setattr(
        product_common.subprocess,
        "Popen",
        lambda argv, **kwargs: launched.append([str(arg) for arg in argv]),
    )

    result = product_common.launch_desktop_shell(desktop_dir)

    assert result == packaged_bundle
    assert launched == [["open", str(packaged_bundle)]]


def test_launch_desktop_shell_launches_built_shell_with_local_electron(
    monkeypatch,
    tmp_path: Path,
):
    desktop_dir = tmp_path / "desktop"
    built_entry = desktop_dir / "out" / "main" / "index.js"
    preload_entry = desktop_dir / "out" / "preload" / "index.cjs"
    renderer_entry = desktop_dir / "out" / "renderer" / "index.html"
    electron_binary = desktop_dir / "node_modules" / ".bin" / "electron"
    package_json = desktop_dir / "package.json"

    for target in [built_entry, preload_entry, renderer_entry, electron_binary, package_json]:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("", encoding="utf-8")

    launched: list[list[str]] = []

    monkeypatch.setattr(product_common, "find_packaged_app_bundle", lambda _: None)
    monkeypatch.setattr(
        product_common.subprocess,
        "Popen",
        lambda argv, **kwargs: launched.append([str(arg) for arg in argv]),
    )
    monkeypatch.setattr(product_common, "detect_bun_binary", lambda: "/opt/homebrew/bin/bun")

    result = product_common.launch_desktop_shell(desktop_dir)

    assert result == built_entry
    assert launched == [[str(electron_binary), str(built_entry)]]


def test_launch_desktop_shell_builds_missing_shell_before_launch(
    monkeypatch,
    tmp_path: Path,
):
    desktop_dir = tmp_path / "desktop"
    electron_binary = desktop_dir / "node_modules" / ".bin" / "electron"
    package_json = desktop_dir / "package.json"

    for target in [electron_binary, package_json]:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("", encoding="utf-8")

    build_calls: list[list[str]] = []
    launched: list[list[str]] = []

    def fake_run(argv, **kwargs):
        build_calls.append([str(arg) for arg in argv])
        built_entry = desktop_dir / "out" / "main" / "index.js"
        preload_entry = desktop_dir / "out" / "preload" / "index.cjs"
        renderer_entry = desktop_dir / "out" / "renderer" / "index.html"
        for target in [built_entry, preload_entry, renderer_entry]:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("", encoding="utf-8")
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setattr(product_common, "find_packaged_app_bundle", lambda _: None)
    monkeypatch.setattr(product_common, "detect_bun_binary", lambda: "/opt/homebrew/bin/bun")
    monkeypatch.setattr(product_common.subprocess, "run", fake_run)
    monkeypatch.setattr(
        product_common.subprocess,
        "Popen",
        lambda argv, **kwargs: launched.append([str(arg) for arg in argv]),
    )

    result = product_common.launch_desktop_shell(desktop_dir)

    assert result == desktop_dir / "out" / "main" / "index.js"
    assert build_calls == [["/opt/homebrew/bin/bun", "run", "build"]]
    assert launched == [[str(electron_binary), str(result)]]


def test_launch_desktop_shell_requires_installed_electron(monkeypatch, tmp_path: Path):
    desktop_dir = tmp_path / "desktop"
    package_json = desktop_dir / "package.json"
    package_json.parent.mkdir(parents=True, exist_ok=True)
    package_json.write_text("", encoding="utf-8")

    monkeypatch.setattr(product_common, "find_packaged_app_bundle", lambda _: None)

    try:
        product_common.launch_desktop_shell(desktop_dir)
    except RuntimeError as exc:
        assert "bun install" in str(exc)
    else:
        raise AssertionError("Expected launch_desktop_shell to require Electron dependencies")
