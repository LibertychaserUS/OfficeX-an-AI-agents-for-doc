"""Tests for executable review criteria."""

from tools.report_scaffold_v3.criteria_runtime import (
    classify_criterion,
    evaluate_criteria,
)


def test_classify_max_words():
    cat, rule, num = classify_criterion("Maximum 500 words")
    assert cat == "deterministic"
    assert rule == "max_words"
    assert num == 500


def test_classify_no_first_person():
    cat, rule, _ = classify_criterion("Use third person only")
    assert cat == "deterministic"
    assert rule == "no_first_person"


def test_classify_no_contractions():
    cat, rule, _ = classify_criterion("No contractions")
    assert cat == "deterministic"
    assert rule == "no_contractions"


def test_classify_ai_judged():
    cat, rule, _ = classify_criterion("Professional tone throughout")
    assert cat == "ai_judged"
    assert rule is None


def test_evaluate_max_words_pass():
    results = evaluate_criteria(
        ["Maximum 100 words"],
        ["This is a short paragraph with only a few words."],
    )
    assert len(results) == 1
    assert results[0].passed is True
    assert results[0].category == "deterministic"


def test_evaluate_max_words_fail():
    long_text = " ".join(["word"] * 200)
    results = evaluate_criteria(
        ["Maximum 100 words"],
        [long_text],
    )
    assert results[0].passed is False


def test_evaluate_no_first_person_pass():
    results = evaluate_criteria(
        ["No first person"],
        ["The system processes documents efficiently."],
    )
    assert results[0].passed is True


def test_evaluate_no_first_person_fail():
    results = evaluate_criteria(
        ["No first person"],
        ["I think we should use a better approach."],
    )
    assert results[0].passed is False
    assert "first-person" in results[0].detail.lower() or "First-person" in results[0].detail


def test_evaluate_mixed_criteria():
    results = evaluate_criteria(
        ["Maximum 500 words", "Professional tone", "No contractions"],
        ["This document is concise and formal."],
    )
    deterministic = [r for r in results if r.category == "deterministic"]
    ai_judged = [r for r in results if r.category == "ai_judged"]
    assert len(deterministic) == 2
    assert len(ai_judged) == 1
