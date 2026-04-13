from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Literal, Union

from .models import (
    IssueStatusRecommendation,
    LiveAnchorRecord,
    RevisionIssueLedger,
    RevisionOperation,
    RevisionPostcondition,
)


@dataclass(frozen=True)
class ParagraphAnchorRule:
    issue_id: str
    anchor_role: str
    block_kind: Literal["paragraph", "heading"]
    match_mode: Literal["exact", "prefix"]
    needle: str


@dataclass(frozen=True)
class TableCellAnchorRule:
    issue_id: str
    anchor_role: str
    block_kind: Literal["table_cell"]
    header_values: tuple[str, ...]
    row_key: str
    row_key_column: int
    target_column: int


AnchorRule = Union[ParagraphAnchorRule, TableCellAnchorRule]


@dataclass(frozen=True)
class IssueProfile:
    issue_id: str
    anchor_rules: tuple[AnchorRule, ...]
    operation_builder: Callable[[dict[str, LiveAnchorRecord], RevisionIssueLedger], list[RevisionOperation]]


def _issue_record(ledger: RevisionIssueLedger, issue_id: str):
    for issue in ledger.issues:
        if issue.issue_id == issue_id:
            return issue
    raise KeyError(f"Issue `{issue_id}` not found in ledger.")


def _evidence_refs(ledger: RevisionIssueLedger, issue_id: str) -> list[str]:
    issue = _issue_record(ledger, issue_id)
    refs = [
        str(ledger.source_review),
        str(ledger.source_map),
        f"issue:{issue_id}",
    ]
    if issue.report_area:
        refs.append(f"report_area:{issue.report_area}")
    refs.extend(f"asset:{asset}" for asset in issue.assets_required)
    return refs


def _insert_after(
    *,
    issue_id: str,
    anchor: LiveAnchorRecord,
    text: str,
    evidence_refs: list[str],
    style: str = "Normal",
    operation_suffix: str | None = None,
) -> RevisionOperation:
    operation_id = f"{issue_id}-{anchor.anchor_role}-insert"
    if operation_suffix:
        operation_id = f"{operation_id}-{operation_suffix}"
    return RevisionOperation(
        operation_id=operation_id,
        issue_id=issue_id,
        anchor_id=anchor.anchor_id,
        expected_candidate_hash=anchor.candidate_hash,
        action="insert_paragraph_after",
        payload={"text": text, "style": style},
        evidence_refs=evidence_refs,
        postconditions=[
            RevisionPostcondition(
                kind="inserted_paragraph_after_anchor",
                value=text,
                style=style,
            )
        ],
    )


def _replace_text(
    *,
    issue_id: str,
    anchor: LiveAnchorRecord,
    text: str,
    evidence_refs: list[str],
) -> RevisionOperation:
    return RevisionOperation(
        operation_id=f"{issue_id}-{anchor.anchor_role}-replace",
        issue_id=issue_id,
        anchor_id=anchor.anchor_id,
        expected_candidate_hash=anchor.candidate_hash,
        action="replace_paragraph_text",
        payload={"text": text},
        evidence_refs=evidence_refs,
        postconditions=[RevisionPostcondition(kind="paragraph_text_equals", value=text)],
    )


def _update_table_cell_text(
    *,
    issue_id: str,
    anchor: LiveAnchorRecord,
    text: str,
    evidence_refs: list[str],
) -> RevisionOperation:
    return RevisionOperation(
        operation_id=f"{issue_id}-{anchor.anchor_role}-table-update",
        issue_id=issue_id,
        anchor_id=anchor.anchor_id,
        expected_candidate_hash=anchor.candidate_hash,
        action="update_table_cell",
        payload={"table_cell_updates": [{"target": "anchor", "text": text}]},
        evidence_refs=evidence_refs,
        postconditions=[RevisionPostcondition(kind="table_cell_text_equals", value=text)],
    )


def _build_rev_007(anchors: dict[str, LiveAnchorRecord], ledger: RevisionIssueLedger) -> list[RevisionOperation]:
    text = (
        "To keep the requirements actionable during implementation, I grouped the functional requirements into "
        "coherent delivery slices rather than treating Table 1 as an isolated checklist: identity and profile "
        "(FR-01 to FR-04), discovery and listing lifecycle (FR-05 to FR-12), engagement features "
        "(FR-13 to FR-15), and governance plus platform-quality features (FR-16 to FR-23). This grouping is "
        "carried forward into the domain analysis in Section 1.12, the design artefacts in Section 1.13, the "
        "backend and UI code walkthroughs in Sections 2.1 and 2.2, and the requirement-by-requirement "
        "assessment in Section 3.1."
    )
    return [
        _insert_after(
            issue_id="REV-007",
            anchor=anchors["requirement_intro"],
            text=text,
            evidence_refs=_evidence_refs(ledger, "REV-007"),
        )
    ]


def _build_rev_008(anchors: dict[str, LiveAnchorRecord], ledger: RevisionIssueLedger) -> list[RevisionOperation]:
    user_text = (
        "This analysis was carried out from both a user perspective and a data-binding perspective. From the "
        "user perspective, the four actors identified in the use case model drive the structure of the system: "
        "guests browse discovery pages, buyers place orders and initiate inquiries, sellers manage listings and "
        "fulfil transactions, and administrators govern users, reports, announcements, and audit trails. That "
        "actor analysis explains why the later design separates public routes, buyer workflows, seller workspace "
        "screens, and admin governance surfaces instead of presenting one undifferentiated interface."
    )
    data_text = (
        "From the data-binding perspective, the same actions are anchored to explicit domain relationships. "
        "Listings bind to categories and ordered media; orders bind buyers, sellers, and listing state changes; "
        "conversations and notifications bind communication back to a specific listing or transaction; and "
        "moderation records bind reports and administrative actions back to the affected content. Those "
        "relationships are then preserved in the class diagrams in Section 1.13 and in the module slices "
        "described in Section 2.1."
    )
    anchor = anchors["system_analysis_heading"]
    refs = _evidence_refs(ledger, "REV-008")
    return [
        _insert_after(
            issue_id="REV-008",
            anchor=anchor,
            text=data_text,
            evidence_refs=refs,
            operation_suffix="data",
        ),
        _insert_after(
            issue_id="REV-008",
            anchor=anchor,
            text=user_text,
            evidence_refs=refs,
            operation_suffix="user",
        ),
    ]


def _build_rev_009(anchors: dict[str, LiveAnchorRecord], ledger: RevisionIssueLedger) -> list[RevisionOperation]:
    text = (
        "This package breakdown is a direct implementation of the domain analysis rather than an arbitrary folder "
        "structure. UserAccount and UserProfile from Section 1.12 map to the identity and profile packages; "
        "Listing, Category, and ListingMedia map to catalog, listing, and media; Order and Review map to "
        "orders and review; Conversation, Message, Favorite, Notification, and ListingReport map to inquiry, "
        "favorite, notification, and moderation; and platform-governance concerns map to admin and dashboard. "
        "The same slice boundaries are exercised by backend tests such as AuthServiceTest, "
        "ListingMediaServiceTest, ListingFlowIntegrationTest, OrderFlowIntegrationTest, "
        "InquiryFlowIntegrationTest, FavoritesDashboardIntegrationTest, CommentsReadModelsIntegrationTest, and "
        "AdminModerationIntegrationTest, so the code listing can be read as traceable implementation of the "
        "earlier design rather than as isolated source files."
    )
    return [
        _insert_after(
            issue_id="REV-009",
            anchor=anchors["backend_modules_intro"],
            text=text,
            evidence_refs=_evidence_refs(ledger, "REV-009"),
        )
    ]


def _build_rev_010(anchors: dict[str, LiveAnchorRecord], ledger: RevisionIssueLedger) -> list[RevisionOperation]:
    text = (
        "The UI code is organised to mirror the wireframe families and user journeys introduced earlier in the "
        "design sections. App.jsx groups public discovery routes (home, search, categories, listing detail, "
        "public profiles), buyer routes (orders, favorites, buyer dashboard), seller workspace routes "
        "(inventory, editor, earnings, reviews), and admin governance routes (users, listings, reports, "
        "categories, orders, reviews, audit log, announcements, settings). Within those routes, components such "
        "as AuthPage, ListingEditorPage, ProfilePage, OrdersPage, and SearchResultsPage demonstrate how the "
        "planned wireframes were translated into working screens with required fields, route-state handling, API "
        "integration, and visible feedback panels."
    )
    return [
        _insert_after(
            issue_id="REV-010",
            anchor=anchors["frontend_intro"],
            text=text,
            evidence_refs=_evidence_refs(ledger, "REV-010"),
        )
    ]


def _build_rev_011(anchors: dict[str, LiveAnchorRecord], ledger: RevisionIssueLedger) -> list[RevisionOperation]:
    text = (
        "The choice of these libraries was based on risk reduction as much as convenience. I considered staying "
        "closer to the taught baseline with more manual servlet-style wiring, hand-managed SQL changes, and a "
        "separately maintained API reference, but that would have increased repetitive infrastructure work and "
        "weakened reproducibility. The learning process therefore followed a staged pattern: I read the official "
        "documentation, built a small proof-of-concept for one slice, and only then expanded the library into "
        "the wider system. This was especially important for Spring Boot, Flyway, React Router, and SpringDoc "
        "because each introduced framework conventions that were new to me."
    )
    return [
        _insert_after(
            issue_id="REV-011",
            anchor=anchors["springdoc_intro"],
            text=text,
            evidence_refs=_evidence_refs(ledger, "REV-011"),
        )
    ]


def _build_rev_012(anchors: dict[str, LiveAnchorRecord], ledger: RevisionIssueLedger) -> list[RevisionOperation]:
    text = (
        "On the frontend, the same contract is preserved by the shared api/client.js module and the page-level "
        "error panels. parseResponse converts backend error payloads into JavaScript exceptions, handle401 "
        "redirects unauthenticated users back to /login, and pages such as AuthPage, ListingEditorPage, "
        "OrdersPage, and ProfilePage render the returned messages through consistent message-panel-error "
        "components. As a result, validation and exception handling are not confined to the business model; they "
        "are surfaced to users in a predictable way across both backend and UI layers."
    )
    return [
        _insert_after(
            issue_id="REV-012",
            anchor=anchors["error_handling_intro"],
            text=text,
            evidence_refs=_evidence_refs(ledger, "REV-012"),
        )
    ]


def _build_rev_013(anchors: dict[str, LiveAnchorRecord], ledger: RevisionIssueLedger) -> list[RevisionOperation]:
    text = (
        "The code-comment density inside src/main is lighter than in a tutorial-style codebase, so I do not "
        "claim that every class is exhaustively annotated inline. Instead, the stronger internal-documentation "
        "trail comes from the combination of descriptive package and controller names, migration history, test "
        "classes, README and DEMO_GUIDE assets, the start.sh launcher, the user manual, and the project trace "
        "and checkpoint records. This is a more accurate description of the evidence base: the project is "
        "documented, but that documentation is distributed across code structure and project artefacts rather "
        "than concentrated only in comments."
    )
    return [
        _insert_after(
            issue_id="REV-013",
            anchor=anchors["internal_docs_intro"],
            text=text,
            evidence_refs=_evidence_refs(ledger, "REV-013"),
        )
    ]


def _build_rev_014(anchors: dict[str, LiveAnchorRecord], ledger: RevisionIssueLedger) -> list[RevisionOperation]:
    strategy_text = (
        "The evidence was intentionally separated into three categories. First, automated unit tests check "
        "service-level rules such as registration/login rejection and media constraints (for example "
        "AuthServiceTest and ListingMediaServiceTest). Second, automated integration tests use MockMvc against "
        "the running Spring context to validate end-to-end backend flows such as listing publication, order "
        "lifecycle, inquiry reuse, favorites/dashboard metrics, comments read models, and admin moderation. "
        "Third, manual browser walkthrough evidence validates the visible UI workflow. This separation matters "
        "because a screenshot can demonstrate a successful screen state, but it cannot substitute for automated "
        "assertions on business rules or API contracts."
    )
    runs_text = (
        "Accordingly, the evidence below should be read in two streams. The automated stream is represented by "
        "JUnit and MockMvc outputs for AuthServiceTest, ListingFlowIntegrationTest, OrderFlowIntegrationTest, "
        "InquiryFlowIntegrationTest, FavoritesDashboardIntegrationTest, CommentsReadModelsIntegrationTest, and "
        "AdminModerationIntegrationTest. The manual stream is represented by Figures 48 to 60, which capture the "
        "visible success state of key user journeys. Together they show both internal correctness and external "
        "usability."
    )
    refs = _evidence_refs(ledger, "REV-014")
    return [
        _insert_after(
            issue_id="REV-014",
            anchor=anchors["test_strategy_intro"],
            text=strategy_text,
            evidence_refs=refs,
        ),
        _insert_after(
            issue_id="REV-014",
            anchor=anchors["test_runs_intro"],
            text=runs_text,
            evidence_refs=refs,
        ),
    ]


def _build_rev_015(anchors: dict[str, LiveAnchorRecord], ledger: RevisionIssueLedger) -> list[RevisionOperation]:
    installation_text = (
        "Prerequisites: Java 21+, Apache Maven 3.8+, Node.js 18+, and a running PostgreSQL instance for the "
        "loopmart_rebuild database. The recommended startup path is the project-root start.sh script, which "
        "checks dependencies, clears ports 8080 and 5173, starts the Spring Boot backend and Vite frontend, and "
        "prints the health-check and Swagger UI URLs. A manual two-terminal startup path is also supported by "
        "running Maven from apps/backend and npm run dev from apps/frontend."
    )
    user_manual_text = (
        "The report summary here is aligned to the real support artefacts shipped with the project: the root "
        "start.sh launcher, the bilingual USER_MANUAL.md file, and the /help route inside the application. I am "
        "therefore using the report to summarise those assets rather than inventing a separate set of "
        "instructions that diverges from the running system."
    )
    registration_text = (
        "Registration and Login: Navigate to the authentication page by clicking 'Sign in' or 'Join free' in "
        "the navigation bar. New users provide a username, display name, password, and the current math CAPTCHA "
        "answer; returning users provide username, password, and CAPTCHA verification. Password recovery is "
        "handled through the dedicated forgot-password and reset-password routes, matching the documented flow "
        "in the project user manual."
    )
    refs = _evidence_refs(ledger, "REV-015")
    return [
        _replace_text(
            issue_id="REV-015",
            anchor=anchors["installation_paragraph"],
            text=installation_text,
            evidence_refs=refs,
        ),
        _insert_after(
            issue_id="REV-015",
            anchor=anchors["user_manual_intro"],
            text=user_manual_text,
            evidence_refs=refs,
        ),
        _replace_text(
            issue_id="REV-015",
            anchor=anchors["registration_paragraph"],
            text=registration_text,
            evidence_refs=refs,
        ),
    ]


def _build_rev_016(anchors: dict[str, LiveAnchorRecord], ledger: RevisionIssueLedger) -> list[RevisionOperation]:
    traceability_text = (
        "The traceability table should be read as the integration point between planning, implementation, and "
        "validation. Each row links the requirement list from Section 1.2 to a concrete implementation "
        "entrypoint and then to a named test case or UI evidence item. In practice, the rows cluster into "
        "identity/profile, listing/catalog/media, orders/reviews, inquiry/notification/favorites, and "
        "governance slices, which matches the module boundaries described in Section 2.1 and the route groups "
        "described in Section 2.2. This makes the satisfaction claim visible rather than purely narrative."
    )
    refs = _evidence_refs(ledger, "REV-016")
    return [
        _insert_after(
            issue_id="REV-016",
            anchor=anchors["traceability_intro"],
            text=traceability_text,
            evidence_refs=refs,
        ),
        _update_table_cell_text(
            issue_id="REV-016",
            anchor=anchors["fr08_evidence_cell"],
            text="TC-18, SearchResultsPage + ListingController",
            evidence_refs=refs,
        ),
    ]


def _build_rev_017(anchors: dict[str, LiveAnchorRecord], ledger: RevisionIssueLedger) -> list[RevisionOperation]:
    strengths_text = (
        "To evaluate these results more rigorously, I ranked the outcomes by impact on delivery quality rather "
        "than by novelty alone. The highest-value strengths are the modular backend structure, reproducible "
        "Flyway-backed database evolution, and the presence of real governance surfaces instead of placeholder "
        "admin screens, because these decisions improved correctness, maintainability, and assessment coverage "
        "across the whole project. The highest-priority weaknesses are the lack of real-time communication, "
        "limited client-side validation, and the absence of browser-level end-to-end automation, because these "
        "are the gaps most likely to affect user experience and regression risk."
    )
    recommendation_text = (
        "I would prioritise these recommendations in three tiers. First priority is automated regression coverage "
        "and real-time communication because they directly reduce user-facing defects and address the most "
        "significant weaknesses identified in Section 3.2. Second priority is media optimisation and search "
        "quality because they improve performance and discovery as the marketplace grows. Lower-priority items "
        "such as native mobile apps and broader internationalisation remain worthwhile, but they sit outside the "
        "minimum baseline until the existing web workflow is more fully hardened."
    )
    modifications_text = (
        "These modifications were not random additions. Architecture changes were driven by maintainability and "
        "reproducibility, security changes by identified abuse risk, and UI changes by observed usability "
        "friction during testing. Framing the modifications this way is important because it shows the project "
        "evolved against a baseline plan rather than through untracked feature creep."
    )
    learning_text = (
        "The most valuable learning did not come from isolated syntax practice, but from understanding cause "
        "and effect between design decisions and delivered outcomes. Choosing a modular architecture improved "
        "testing and traceability; adopting Flyway changed the way I approached database evolution; and "
        "building the authentication, listing, order, and governance flows end to end made me more aware of how "
        "security, validation, and documentation must work together. These are the areas I would now develop "
        "further in future projects, particularly automated testing, real-time communication, and stronger "
        "upfront interface validation."
    )
    refs = _evidence_refs(ledger, "REV-017")
    return [
        _insert_after(
            issue_id="REV-017",
            anchor=anchors["strengths_intro"],
            text=strengths_text,
            evidence_refs=refs,
        ),
        _insert_after(
            issue_id="REV-017",
            anchor=anchors["recommendation_intro"],
            text=recommendation_text,
            evidence_refs=refs,
        ),
        _insert_after(
            issue_id="REV-017",
            anchor=anchors["modifications_intro"],
            text=modifications_text,
            evidence_refs=refs,
        ),
        _insert_after(
            issue_id="REV-017",
            anchor=anchors["learning_intro"],
            text=learning_text,
            evidence_refs=refs,
        ),
    ]


ISSUE_PROFILES: dict[str, IssueProfile] = {
    "REV-007": IssueProfile(
        issue_id="REV-007",
        anchor_rules=(
            ParagraphAnchorRule(
                issue_id="REV-007",
                anchor_role="requirement_intro",
                block_kind="paragraph",
                match_mode="prefix",
                needle="Functional requirements were derived using user story techniques",
            ),
        ),
        operation_builder=_build_rev_007,
    ),
    "REV-008": IssueProfile(
        issue_id="REV-008",
        anchor_rules=(
            ParagraphAnchorRule(
                issue_id="REV-008",
                anchor_role="system_analysis_heading",
                block_kind="paragraph",
                match_mode="exact",
                needle="Business Model Analysis",
            ),
        ),
        operation_builder=_build_rev_008,
    ),
    "REV-009": IssueProfile(
        issue_id="REV-009",
        anchor_rules=(
            ParagraphAnchorRule(
                issue_id="REV-009",
                anchor_role="backend_modules_intro",
                block_kind="paragraph",
                match_mode="prefix",
                needle="The backend source code is organised into the following domain packages:",
            ),
        ),
        operation_builder=_build_rev_009,
    ),
    "REV-010": IssueProfile(
        issue_id="REV-010",
        anchor_rules=(
            ParagraphAnchorRule(
                issue_id="REV-010",
                anchor_role="frontend_intro",
                block_kind="paragraph",
                match_mode="prefix",
                needle="This section presents the frontend implementation of the LoopMart application.",
            ),
        ),
        operation_builder=_build_rev_010,
    ),
    "REV-011": IssueProfile(
        issue_id="REV-011",
        anchor_rules=(
            ParagraphAnchorRule(
                issue_id="REV-011",
                anchor_role="springdoc_intro",
                block_kind="paragraph",
                match_mode="prefix",
                needle="SpringDoc OpenAPI:",
            ),
        ),
        operation_builder=_build_rev_011,
    ),
    "REV-012": IssueProfile(
        issue_id="REV-012",
        anchor_rules=(
            ParagraphAnchorRule(
                issue_id="REV-012",
                anchor_role="error_handling_intro",
                block_kind="paragraph",
                match_mode="prefix",
                needle="The application implements a centralised error handling strategy on the backend",
            ),
        ),
        operation_builder=_build_rev_012,
    ),
    "REV-013": IssueProfile(
        issue_id="REV-013",
        anchor_rules=(
            ParagraphAnchorRule(
                issue_id="REV-013",
                anchor_role="internal_docs_intro",
                block_kind="paragraph",
                match_mode="prefix",
                needle="The project maintains internal documentation through several mechanisms:",
            ),
        ),
        operation_builder=_build_rev_013,
    ),
    "REV-014": IssueProfile(
        issue_id="REV-014",
        anchor_rules=(
            ParagraphAnchorRule(
                issue_id="REV-014",
                anchor_role="test_strategy_intro",
                block_kind="paragraph",
                match_mode="prefix",
                needle="The test strategy employs a multi-layered approach combining unit testing",
            ),
            ParagraphAnchorRule(
                issue_id="REV-014",
                anchor_role="test_runs_intro",
                block_kind="paragraph",
                match_mode="prefix",
                needle="The following evidence demonstrates that the test cases identified in the test plan",
            ),
        ),
        operation_builder=_build_rev_014,
    ),
    "REV-015": IssueProfile(
        issue_id="REV-015",
        anchor_rules=(
            ParagraphAnchorRule(
                issue_id="REV-015",
                anchor_role="installation_paragraph",
                block_kind="paragraph",
                match_mode="prefix",
                needle="Prerequisites: Java 21",
            ),
            ParagraphAnchorRule(
                issue_id="REV-015",
                anchor_role="user_manual_intro",
                block_kind="paragraph",
                match_mode="prefix",
                needle="This section provides guidance for end users interacting with the LoopMart application.",
            ),
            ParagraphAnchorRule(
                issue_id="REV-015",
                anchor_role="registration_paragraph",
                block_kind="paragraph",
                match_mode="prefix",
                needle="Registration and Login: Navigate to the authentication page by clicking",
            ),
        ),
        operation_builder=_build_rev_015,
    ),
    "REV-016": IssueProfile(
        issue_id="REV-016",
        anchor_rules=(
            ParagraphAnchorRule(
                issue_id="REV-016",
                anchor_role="traceability_intro",
                block_kind="paragraph",
                match_mode="prefix",
                needle="To provide a structured assessment, I mapped each of the 23 functional requirements",
            ),
            TableCellAnchorRule(
                issue_id="REV-016",
                anchor_role="fr08_evidence_cell",
                block_kind="table_cell",
                header_values=("FR ID", "Requirement", "Status", "Evidence", "Notes"),
                row_key="FR-08",
                row_key_column=0,
                target_column=3,
            ),
        ),
        operation_builder=_build_rev_016,
    ),
    "REV-017": IssueProfile(
        issue_id="REV-017",
        anchor_rules=(
            ParagraphAnchorRule(
                issue_id="REV-017",
                anchor_role="strengths_intro",
                block_kind="paragraph",
                match_mode="prefix",
                needle="From a technical standpoint, several specific strengths stand out.",
            ),
            ParagraphAnchorRule(
                issue_id="REV-017",
                anchor_role="recommendation_intro",
                block_kind="paragraph",
                match_mode="prefix",
                needle="Based on the evaluation of the current prototype",
            ),
            ParagraphAnchorRule(
                issue_id="REV-017",
                anchor_role="modifications_intro",
                block_kind="paragraph",
                match_mode="prefix",
                needle="Several modifications were made to the original project plan during development",
            ),
            ParagraphAnchorRule(
                issue_id="REV-017",
                anchor_role="learning_intro",
                block_kind="paragraph",
                match_mode="prefix",
                needle="This project provided significant opportunities for learning and skill development",
            ),
        ),
        operation_builder=_build_rev_017,
    ),
}


def get_issue_profile(issue_id: str) -> IssueProfile:
    try:
        return ISSUE_PROFILES[issue_id]
    except KeyError as exc:
        raise KeyError(f"Unsupported revision issue profile: {issue_id}") from exc


def supported_issue_ids() -> list[str]:
    return list(ISSUE_PROFILES.keys())


def resolve_target_issue_ids(
    ledger: RevisionIssueLedger,
    requested_issue_ids: Union[list[str], None] = None,
) -> list[str]:
    if requested_issue_ids:
        return requested_issue_ids

    supported = set(supported_issue_ids())
    return [
        issue.issue_id
        for issue in ledger.issues
        if issue.issue_id in supported and issue.status != "fixed"
    ]


def build_issue_operations(
    issue_id: str,
    anchors: dict[str, LiveAnchorRecord],
    ledger: RevisionIssueLedger,
) -> list[RevisionOperation]:
    return get_issue_profile(issue_id).operation_builder(anchors, ledger)


def planned_status_recommendations(issue_ids: list[str]) -> list[IssueStatusRecommendation]:
    return [
        IssueStatusRecommendation(
            issue_id=issue_id,
            recommended_status="planned",
            rationale="Patch spec generated and bound to live anchors; execution has not completed yet.",
        )
        for issue_id in issue_ids
    ]
