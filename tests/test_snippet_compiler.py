from pathlib import Path

import pytest

from tools.report_scaffold_v3.models import ManagedSnippetManifest, SnippetsManifest
from tools.report_scaffold_v3.snippet_compiler import (
    SnippetCompilationError,
    compile_snippets_for_section,
    extract_snippet_text,
    render_snippet_label,
    resolve_snippet_source_path,
)


def test_extract_snippet_text_literal_text_strips_outer_newlines():
    snippet = ManagedSnippetManifest(
        snippet_id="SNIP-LIT-01",
        title="Literal Demo",
        language="text",
        source_path=Path("unused.txt"),
        target_section_id="section-a",
        extract_mode="literal_text",
        literal_text="\nalpha\nbeta\n",
    )

    assert extract_snippet_text(snippet) == "alpha\nbeta"


def test_extract_snippet_text_line_range_reads_expected_lines(tmp_path: Path):
    source_path = tmp_path / "snippet_source.py"
    source_path.write_text("line 1\nline 2\nline 3\nline 4\n", encoding="utf-8")
    snippet = ManagedSnippetManifest(
        snippet_id="SNIP-LINE-01",
        title="Line Range Demo",
        language="python",
        source_path=source_path,
        target_section_id="section-a",
        extract_mode="line_range",
        start_line=2,
        end_line=3,
    )

    assert resolve_snippet_source_path(source_path) == source_path
    assert extract_snippet_text(snippet) == "line 2\nline 3"


@pytest.mark.parametrize(
    ("start_line", "end_line"),
    [
        (4, 3),
        (0, 2),
    ],
)
def test_extract_snippet_text_rejects_bad_line_ranges(tmp_path: Path, start_line: int, end_line: int):
    source_path = tmp_path / "snippet_source.py"
    source_path.write_text("line 1\nline 2\nline 3\n", encoding="utf-8")
    snippet = ManagedSnippetManifest(
        snippet_id="SNIP-BAD-01",
        title="Bad Range Demo",
        language="python",
        source_path=source_path,
        target_section_id="section-a",
        extract_mode="line_range",
        start_line=start_line,
        end_line=end_line,
    )

    with pytest.raises(SnippetCompilationError, match="invalid line range"):
        extract_snippet_text(snippet)


def test_compile_snippets_for_section_filters_and_orders_matching_snippets():
    manifest = SnippetsManifest(
        managed_snippets=[
            ManagedSnippetManifest(
                snippet_id="SNIP-Z",
                title="Zulu",
                language="python",
                source_path=Path("unused-z.py"),
                target_section_id="section-b",
                extract_mode="literal_text",
                literal_text="zulu",
                order=1,
            ),
            ManagedSnippetManifest(
                snippet_id="SNIP-B",
                title="Beta",
                language="python",
                source_path=Path("unused-b.py"),
                target_section_id="section-a",
                extract_mode="literal_text",
                literal_text="beta",
                order=2,
            ),
            ManagedSnippetManifest(
                snippet_id="SNIP-A",
                title="Alpha",
                language="python",
                source_path=Path("unused-a.py"),
                target_section_id="section-a",
                extract_mode="literal_text",
                literal_text="alpha",
                order=1,
            ),
        ]
    )

    blocks = compile_snippets_for_section(manifest, section_id="section-a")

    assert [block["text"] for block in blocks] == [
        "Snippet SNIP-A - Alpha (python)",
        "alpha",
        "Snippet SNIP-B - Beta (python)",
        "beta",
    ]
    assert [block["role"] for block in blocks] == ["subtitle", "body", "subtitle", "body"]


def test_render_snippet_label_includes_language():
    snippet = ManagedSnippetManifest(
        snippet_id="SNIP-LABEL-01",
        title="Label Demo",
        language="python",
        source_path=Path("unused.py"),
        target_section_id="section-a",
        extract_mode="literal_text",
        literal_text="demo",
    )

    assert render_snippet_label(snippet) == "Snippet SNIP-LABEL-01 - Label Demo (python)"
