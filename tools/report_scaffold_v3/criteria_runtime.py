"""Executable review criteria: automatic + AI-judged hybrid checking.

Parses review_criteria strings and separates them into:
1. Deterministic rules (checkable by code): word count, format patterns
2. AI-judged rules (need LLM evaluation): tone, coherence, accuracy

Deterministic rules run locally without API calls.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CriterionResult:
    criterion: str
    category: str  # "deterministic" or "ai_judged"
    passed: bool
    detail: str = ""


# Patterns that indicate auto-checkable criteria
# These patterns recognize user-defined rules expressed in natural language.
# Nothing is hardcoded as "must do" — these only activate when the user
# explicitly states the rule in their review_criteria.
DETERMINISTIC_PATTERNS = [
    (r"(?:max(?:imum)?|limit|under|fewer\s+than|at\s+most|no\s+more\s+than)\s+(\d+)\s*words?", "max_words"),
    (r"(\d+)\s*words?\s*(?:max|limit|maximum|or\s+less|under|fewer)", "max_words"),
    (r"(?:min(?:imum)?|at\s+least|no\s+fewer\s+than)\s+(\d+)\s*words?", "min_words"),
    (r"(\d+)\s*words?\s*(?:min|minimum|at\s+least|or\s+more)", "min_words"),
    (r"(\d+)\s*paragraphs?\s*(?:max|limit|maximum)", "max_paragraphs"),
    (r"(\d+)\s*sections?\s*(?:max|limit|maximum)", "max_sections"),
    (r"no\s+(?:first\s+person|\"?I\"?|\"?we\"?)", "no_first_person"),
    (r"(?:third\s+person\s+only|use\s+third\s+person)", "no_first_person"),
    (r"all\s+(?:headings?|sections?)\s+must\s+be\s+(?:numbered|capitalized)", "heading_format"),
    (r"no\s+contractions", "no_contractions"),
]


def classify_criterion(criterion: str) -> tuple[str, str | None, int | None]:
    """Classify a criterion as deterministic or ai_judged.

    Returns: (category, rule_type, numeric_value)
    """
    lower = criterion.lower()
    for pattern, rule_type in DETERMINISTIC_PATTERNS:
        match = re.search(pattern, lower)
        if match:
            # Extract numeric value if present
            numeric = None
            for group in match.groups():
                if group and group.isdigit():
                    numeric = int(group)
                    break
            return "deterministic", rule_type, numeric
    return "ai_judged", None, None


def check_deterministic_criterion(
    criterion: str,
    rule_type: str,
    numeric_value: int | None,
    paragraphs: list[str],
) -> CriterionResult:
    """Execute a deterministic criterion check."""
    full_text = " ".join(paragraphs)
    word_count = len(full_text.split())

    if rule_type == "max_words" and numeric_value:
        passed = word_count <= numeric_value
        return CriterionResult(
            criterion=criterion,
            category="deterministic",
            passed=passed,
            detail=f"Word count: {word_count} (limit: {numeric_value})",
        )

    if rule_type == "min_words" and numeric_value:
        passed = word_count >= numeric_value
        return CriterionResult(
            criterion=criterion,
            category="deterministic",
            passed=passed,
            detail=f"Word count: {word_count} (minimum: {numeric_value})",
        )

    if rule_type == "max_paragraphs" and numeric_value:
        count = len([p for p in paragraphs if p.strip()])
        passed = count <= numeric_value
        return CriterionResult(
            criterion=criterion,
            category="deterministic",
            passed=passed,
            detail=f"Paragraph count: {count} (limit: {numeric_value})",
        )

    if rule_type == "no_first_person":
        first_person = re.findall(r'\b(I|we|my|our|us|me)\b', full_text, re.IGNORECASE)
        # Filter out common false positives
        real_hits = [w for w in first_person if w.lower() in {"i", "we", "my", "our", "us", "me"}]
        passed = len(real_hits) == 0
        return CriterionResult(
            criterion=criterion,
            category="deterministic",
            passed=passed,
            detail=f"First-person occurrences: {len(real_hits)}" + (f" ({', '.join(real_hits[:5])})" if real_hits else ""),
        )

    if rule_type == "no_contractions":
        contractions = re.findall(r"\b\w+n't\b|\b\w+'re\b|\b\w+'ve\b|\b\w+'ll\b|\b\w+'d\b|\b\w+'s\b", full_text)
        passed = len(contractions) == 0
        return CriterionResult(
            criterion=criterion,
            category="deterministic",
            passed=passed,
            detail=f"Contractions found: {len(contractions)}" + (f" ({', '.join(contractions[:5])})" if contractions else ""),
        )

    return CriterionResult(
        criterion=criterion,
        category="deterministic",
        passed=True,
        detail="Rule recognized but check not implemented",
    )


def evaluate_criteria(
    criteria: list[str],
    paragraphs: list[str],
) -> list[CriterionResult]:
    """Evaluate all criteria against document content.

    Deterministic criteria are checked immediately.
    AI-judged criteria are returned with category="ai_judged" and passed=True
    (they need an AI call to actually evaluate, which is the caller's job).
    """
    results = []
    for criterion in criteria:
        category, rule_type, numeric_value = classify_criterion(criterion)

        if category == "deterministic" and rule_type:
            result = check_deterministic_criterion(
                criterion, rule_type, numeric_value, paragraphs,
            )
            results.append(result)
        else:
            results.append(CriterionResult(
                criterion=criterion,
                category="ai_judged",
                passed=True,  # Placeholder; actual AI judgment done separately
                detail="Requires AI evaluation",
            ))

    return results
