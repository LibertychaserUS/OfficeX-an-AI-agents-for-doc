---
doc_id: officex_workbench_frontstage_mvp_spec
layer: product_spec
authority: active
status: draft
owner: product_architecture
last_updated: 2026-04-21
---

# OfficeX Workbench Frontstage MVP Spec

## 1. Purpose

This spec defines the first real frontstage product shape for `OfficeX`.

The goal is not to keep extending a readiness launcher shell. The goal is to
define the first user-facing workbench shape that can later sit on top of the
general agent platform while still making sense as a standalone Office product.

This spec only fixes:

- frontstage product structure
- workspace and thread model
- intake and confirmation flow
- document-task mapping logic
- initial chat-entry behavior

This spec does not yet define:

- full renderer embedding implementation
- final visual design system
- full plugin marketplace behavior
- final generalized platform packaging

## 2. Product Layering

`OfficeX` must be treated as a vertical product built on top of a more general
agent platform.

The product split is:

1. general agent platform layer
2. `OfficeX` domain product layer

The platform layer owns:

- threads
- agents
- plugins
- tools
- memory
- execution runtime
- audit primitives
- extensibility surfaces

The `OfficeX` product layer owns:

- Office-domain task intake
- document-task interpretation
- document basis management
- document review and generation workflow
- Office-first workbench UX
- Office-domain reporting and audit presentation

This split is intentional.

If `OfficeX` succeeds, it may later be:

- packaged as its own product
- and also reintroduced into the general platform as a plugin/tool bundle

## 3. Frontstage Principle

The frontstage must not look like a coding shell, raw runtime console, or
governance dashboard.

The user-facing experience should present:

- a task-oriented Office product
- a guided document workspace
- a human-readable agent collaboration surface

The following must stay behind the frontstage boundary unless needed for audit
or debugging:

- raw runtime terms
- provider plumbing
- prompt assembly details
- trace internals
- harness selection logic
- low-level tool execution details

## 4. Frontstage Shape

The recommended frontstage shape for the first real `OfficeX` workbench is a
hybrid of the previously discussed `A` and `C` directions.

The shape is:

- intake behaves like `A`
- working state behaves like `C`

This means:

1. users enter a workspace and create or open a thread
2. the initial thread state opens as a blank intake surface
3. the user expresses the task in the chat entry
4. `OfficeX` produces a confirmation card instead of executing immediately
5. after confirmation, the product transitions into the document workbench

This is the active recommendation for MVP.

## 5. Core Layout

The long-lived workbench layout should be a three-column structure.

### Left Column

The left column is navigation and ownership, not generic "context".

It should hold:

- workspaces or projects
- thread list inside each workspace
- create thread action
- expand historical threads
- archive thread action
- base product navigation
- settings entry

The left column should follow the logic of a conversation-and-project product,
not the logic of a file tree IDE.

### Center Column

The center column is the document surface.

For the intake state, it should initially remain empty instead of opening a
document immediately.

In the empty state, the center should show:

- `OfficeX` logo
- one short guiding sentence

Example tone:

- "What document task do you want to handle today?"

After task confirmation, the center becomes the document work surface and may
later host:

- embedded `ONLYOFFICE`
- review canvas
- patch previews
- document state comparison views

### Right Column

The right column is the active agent interaction surface.

It is not only a transcript panel.

It should include:

- chat input
- model selection
- reasoning-depth selection
- voice input entry
- later attachment and quoting entry
- task confirmation cards
- plan and review feedback
- run and audit feedback

The right column is the primary control surface during intake.

## 6. Initial Empty-State Behavior

When a new thread is created, the center column should stay empty and not open a
document by default.

The initial state should communicate:

- no document session is active yet
- the user should first describe the task
- `OfficeX` will help translate that task into a document workflow

This is intentional.

The product should not assume that the correct first move is opening a document
editor.

## 7. Thread Model

An `OfficeX` thread is not just a generic chat thread.

It is a document-task thread.

A thread should eventually bind or reference:

- current task intent
- source document if present
- template if present
- personal writing requirements if present
- review rubric if present
- current head artifact
- sandbox state
- run history
- audit outputs
- recovery and provenance record

The thread therefore acts as the user-facing handle for a governed document
workflow.

## 8. Basis Model

For document work, the core basis inputs are:

- template
- personal writing requirements
- review rubric or review rules
- source/base document

These inputs must be treated as first-class task basis, not informal chat
context.

They may be incomplete at intake time.

The system should detect what is missing and surface it during confirmation
rather than forcing all basis inputs to exist before the user can start.

## 9. Intake Flow

The intake flow should work like this:

1. user enters a natural-language request in the right-side chat
2. `OfficeX` interprets the request
3. `OfficeX` does not execute immediately
4. `OfficeX` generates a task confirmation card
5. user confirms or adjusts the task
6. only then does the system create the formal working state for that thread

This behavior is modeled after the useful part of plan-confirmation interaction,
but adapted for document work rather than coding tasks.

## 10. Task Confirmation Card

The first response to a new request should be a task confirmation card.

That card should include four sections.

### 10.1 Task Understanding

The system should restate, in one short sentence, what it believes the user is
trying to do.

It should also classify the task as one of:

- generation
- modification
- review
- rewrite or restructure
- formatting or layout repair
- mixed

### 10.2 Recommended Task Choices

The first fixed recommended choices for MVP are:

- `Draft a new document`
- `Modify an existing document`
- `Review against a rubric`
- `Rewrite or re-structure from a template`
- `Repair formatting and layout`
- `Custom description`

These should be shown as task-type options, not workflow-template names.

### 10.3 Basis Prompt

The card should surface which basis inputs seem relevant or missing, including:

- template
- personal writing requirements
- review rubric
- source document

### 10.4 Execution Gate

Before formal thread execution begins, the card should summarize:

- what the system proposes to do first
- what the user still needs to provide
- whether the system is ready to transition into the workbench state

## 11. Mapping Rule

The user should choose task intent in product language.

The system should map that choice to an internal execution path automatically.

This is an explicit product rule.

The user should not be forced to choose:

- runtime route
- harness path
- internal workflow id
- patch pipeline
- audit plan identifier

Those belong to the internal system-mapping layer.

The system should make those decisions after the user confirms the task type and
available basis inputs.

## 12. Document Workbench Transition

Once the user confirms the task confirmation card, `OfficeX` should transition
from intake state into a document-task work state.

That transition may create:

- thread task record
- bound basis record
- initial sandbox or working copy
- run preparation state
- initial audit expectations

The document surface should only become active after this transition.

## 13. Editing and Renderer Principle

The embedded document surface should be treated as:

- a work surface
- a mirror surface
- a review surface

It should not be treated as the sole truth source.

For the near-term UI direction:

- `ONLYOFFICE` is the likely embedded document surface
- Microsoft Word remains the acceptance renderer and external validation target

This avoids tying the frontstage to Microsoft product embedding assumptions.

## 14. Interaction Controls In Chat Entry

The right-side chat entry should support the following controls from the start:

- model selection
- reasoning-depth selection
- voice-input trigger

Later additions may include:

- document attachment
- quote or selection insertion
- basis binding actions
- review-item injection

## 15. Out-Of-Scope For This Spec

This spec does not yet finalize:

- detailed visual style
- final iconography
- exact animation system
- full document review panel design
- final multi-renderer capability matrix UI
- full plugin-discovery UI
- final cross-platform packaging behavior

## 16. Active Recommendation

The active recommendation for the first real `OfficeX` product workbench is:

- keep `officex` as the unified entry
- use a blank intake thread as the first visible state
- use a right-side chat surface as the primary intake controller
- use a task confirmation card before execution
- keep recommended options in task-language
- let the system map user intent to internal workflow automatically
- transition into a three-column workbench only after confirmation

This is the approved direction to carry forward into planning.
