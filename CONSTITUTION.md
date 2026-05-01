# OfficeX Constitution

The foundational law of the OfficeX platform. All modules, agents,
skills, and runtime behaviors operate under these principles.

---

## Terminology

| Term | Definition |
|------|-----------|
| **Skill** | Reusable capability package (SKILL.md + optional scripts/assets). Agent Skills standard. |
| **Tool** | Atomic executable action. AI decides when to invoke. |
| **Profile** | Named configuration set (paper, font, style, layout). Switchable at runtime. |
| **Manifest** | Declarative file describing state or inputs (build source, template profile). |
| **Contract** | Declarative file constraining behavior (write contract, layout contract). |
| **Sandbox** | Isolated mutable space. Source files are never touched directly. |
| **Workspace** | Root of a complete work session. |
| **Trace** | Immutable record of what happened, what was decided, and why. |
| **Checkpoint** | Named milestone within a trace. |
| **Memory** | Persistent knowledge across sessions, layered by authority. |
| **Provider** | AI inference service abstraction. |
| **Adapter** | Translates platform-neutral requests into provider-specific calls. |
| **Outline** | Structural plan for a long document, drives section-by-section generation. |
| **Plan** | Agent-generated action plan before execution. Granularity matches task complexity. |

---

## I. Authority

1. **Manifests and contracts are law.** Runtime behavior is driven by declared files, not by hardcoded values or implicit conventions. If it is not declared, the platform does not assume it.

2. **Layers do not reach up.** Lower layers never override higher layers.

   ```
   System contracts  >  Session state  >  User preferences  >  Retrieved references
   ```

3. **Program owns structure by default.** AI generates content. Deterministic code owns document structure, styles, layout, numbering, and export integrity. Users may explicitly grant AI direct access to specific structural scopes when needed.

---

## II. Execution

4. **Sandbox before mutation.** Every document operation works on an isolated copy. Source documents, templates, and imported references are read-only by default.

5. **Verify before claiming.** No output is considered correct until both structural validation and visual audit have passed. A structural pass alone does not prove visual correctness. A visual pass alone does not prove structural integrity.

6. **Fail explicit, recover graceful.** When something fails, report what failed and why. When recovery is possible (retry, repair, fallback), attempt it. When not possible, stop and say so. Never silently swallow an error.

7. **Degrade, do not block.** Each capability layer operates independently. Missing LibreOffice degrades visual audit to skip, not crash. Missing API key disables generate but not validate. A missing optional dependency never prevents core functions from running.

8. **Scope declares itself.** Every validation claim states its scope: structural, semantic, layout, or visual. Never present one type of check as proof of another.

---

## III. Memory

9. **Memory is layered, not flat.** Four tiers, strict precedence:
   - **System**: Contracts, policies, approved configurations. Versioned and rollbackable.
   - **Session**: Current run state, approvals, logs. Scoped to this execution.
   - **User**: Preferences, habits, project vocabulary. Never stronger than system rules.
   - **Retrieval**: Searched references, historical cases. Advisory only.

10. **Retrieval informs, never governs.** RAG results suggest; they do not decide. Recurring patterns must be promoted explicitly into upper layers.

11. **Memory is auditable.** When memory influences a decision, the trace records what was queried, what was found, and whether it was advisory or authoritative.

12. **Refresh is change-driven.** Memory does not expire on a timer. When source files change, the corresponding memory layer is marked stale. No change, no refresh.

---

## IV. Interaction

13. **Weight determines dialogue.** Light tasks proceed with sensible defaults. Heavy tasks require confirmation of critical inputs. Threshold: if missing information makes the output unpredictable, ask. If it is a preference, use the default.

14. **Never fabricate key inputs.** Outlines, source materials, and format standards are provided by the user, not invented. Secondary preferences (exact margins, line spacing) may use profile defaults without asking.

15. **Questions are specific.** Not "anything else?" but "which sections should this report contain?" or "do you have a template .docx to use?"

---

## V. Security

16. **User content does not leave user-defined boundaries.** Documents are processed locally. When AI providers are called, the platform sends only the minimum content needed for the task, not entire documents by default.

17. **Secrets never touch disk.** API keys are resolved from environment variables at runtime. They are never written to config files, manifest files, logs, or trace records.

18. **No silent uploads.** The platform never sends user content to external services without the user's explicit action (invoking a provider-backed command). Validation, audit, and structural operations are entirely local.

---

## VI. Extensibility

19. **Configuration is dynamic.** Profiles, manifests, skills, and provider configurations can be created, modified, and switched at runtime without code changes.

20. **Skills are self-contained.** A skill declares what it needs, what it does, and what it returns. No undocumented dependencies. No state leaks.

21. **Platform mode vs skill mode.** As an independent platform, OfficeX manages orchestration, memory, and multi-agent coordination. As a skill for an external agent, OfficeX executes the requested operation and returns structured results. It does not inject its orchestration, streaming, or memory into the host.

---

## VII. Planning and Authorship

22. **Plan granularity matches task complexity.** A one-page memo needs no plan. A 50-page report needs a plan that specifies: section dependencies, shared terminology, argument flow across sections, and stylistic constraints.

23. **Documents read like one author wrote them.** Multi-agent generation produces sections sequentially, not in parallel, because later sections depend on earlier ones. Each section sees all previously completed content. Terminology, tone, and argumentation stay consistent across the full document.

24. **Review is interleaved, not deferred.** Coherence review happens during generation (every N sections), not only after the full document is assembled. Catching drift early is cheaper than rewriting finished sections.

25. **Plans are executable specifications.** A plan is not a vague outline. It specifies: dependency graph between sections, term definitions that must be consistent, data/claims that flow from one section to another, and transition requirements between adjacent sections.

---

## VIII. Trace

26. **Everything leaves a trail.** Every meaningful operation produces a trace entry. Traces are append-only during a session.

27. **Traces are replayable.** Given the same inputs and manifests, a traced operation produces the same output. Non-deterministic steps (AI calls) record both request and response.

---

*This constitution defines principles, not procedures. Procedures live in
skills, manifests, and runtime code — all of which operate under these
principles. 27 articles across 8 domains.*
