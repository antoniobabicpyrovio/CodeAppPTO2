# Mira Copilot Studio Agent in PMO App — Implementation Plan

> **Handoff-ready plan.** This document is written for autonomous coding-agent execution. Every section distinguishes what is already implemented from what must still be built. Human intervention is required only where explicitly called out. All other steps are coding-agent executable.

---

## 1. Implemented Reality — What Exists Today

> [!IMPORTANT]
> Wave 0 delivered an **app-side advisory/draft module only**. It is NOT a Copilot Studio agent. No agent artifact, no deployed bot, no Copilot Studio topic, no YAML definition, and no `botcomponent` entry in the solution exists anywhere in this repository. The four Wave 1 topic functions that exist in `app/src/ai/topics/` are TypeScript modules that run inside the React app — they are not agent topics and they are not deployed to any agent runtime.
> **Wave 1 is the first wave that creates Mira as a real, deployed Copilot Studio agent artifact.**

### Implemented artifacts (coding agent must treat these as COMPLETE — do not recreate)

| Artifact | Path | State |
|---|---|---|
| App-side advisory/draft module | `app/src/ai/` | ✅ COMPLETE |
| Output contracts (typed) | `app/src/ai/contracts.ts` | ✅ COMPLETE |
| Barrel export | `app/src/ai/index.ts` | ✅ COMPLETE |
| Project context loader | `app/src/ai/context/projectContext.ts` | ✅ COMPLETE |
| Program context loader | `app/src/ai/context/programContext.ts` | ✅ COMPLETE |
| Status context loader | `app/src/ai/context/statusContext.ts` | ✅ COMPLETE |
| Triage context loader | `app/src/ai/context/triageContext.ts` | ✅ COMPLETE |
| Deterministic health signals | `app/src/ai/grounding/signals.ts` | ✅ COMPLETE |
| explain-project-health topic fn | `app/src/ai/topics/explainProjectHealth.ts` | ✅ COMPLETE |
| explain-program-health topic fn | `app/src/ai/topics/explainProgramHealth.ts` | ✅ COMPLETE |
| draft-weekly-status-report topic fn | `app/src/ai/topics/draftWeeklyStatusReport.ts` | ✅ COMPLETE |
| pmo-triage-needs-attention topic fn | `app/src/ai/topics/pmoTriageNeedsAttention.ts` | ✅ COMPLETE |
| Route-aware Mira panel | `app/src/components/mira/MiraPanel.tsx` | ✅ COMPLETE |
| AppShell Ask Mira button + Sheet | `app/src/components/layout/AppShell.tsx` | ✅ COMPLETE |
| Dataverse solution (unmanaged) | `solution/` | ✅ COMPLETE |
| TypeScript build | `app/` | ✅ CLEAN |

### Confirmed absent (coding agent must create these in Wave 1)

- No `copilot-studio/` directory anywhere in the repository
- No `.bot` file anywhere in the repository
- No YAML topic or action definitions
- No `botcomponent` entry in `solution/src/Other/Solution.xml`
- No agent record registered in any Power Platform environment
- No Copilot Studio connection reference in the solution

---

## 2. Logic Ownership Rule — `app/src/ai/` Is the Authoritative Contract Source

> [!IMPORTANT]
> **`app/src/ai/` is the authoritative source for:**
> - Output contracts and typed schemas (`contracts.ts`)
> - Deterministic scoring logic (signal builders, threshold rules, ranking algorithms in `grounding/signals.ts` and topic functions)
> - Grounding expectations (what context is required per topic, what fields are load-required vs. optional)
> - Safety rules (advisory-only mode enforcement, no silent writes, approval-gate requirements)
>
> **Copilot Studio topics and actions must mirror or invoke these rules — they must NOT create competing logic definitions.**
>
> If a scoring threshold, health label mapping, or grounding requirement changes, the change must originate in `app/src/ai/` and be reflected in the corresponding Copilot Studio topic/action YAML. The agent layer is a delivery surface, not a logic authority.

---

## 3. App-Side Fallback Rule

> [!IMPORTANT]
> The app-side advisory layer in `app/src/components/mira/MiraPanel.tsx` (backed by `app/src/ai/`) **remains a governed fallback path** unless and until the Copilot Studio agent reaches full Wave 1 functional parity AND operational reliability.
>
> - "Functional parity" means all four Wave 1 topics (explain-project-health, explain-program-health, draft-weekly-status-report, pmo-triage-needs-attention) are deployed, tested, and returning correct outputs from the agent runtime.
> - "Operational reliability" means the agent has been validated in the target environment with no data-loss or silent-failure modes.
> - Until both conditions are met, the MiraPanel app-side path must remain active and reachable.
> - Do NOT remove, disable, or hide the MiraPanel app-side fallback during Wave 1 build.

---

## 4. Deployment Verification Rule

> [!IMPORTANT]
> **Before authoring any Copilot Studio YAML, folder structure, or solution packaging steps, the coding agent must verify:**
>
> 1. The exact supported source-control model for Copilot Studio artifacts in the current environment and toolchain (check PAC CLI help, Power Platform Build Tools docs, and any environment-specific guidance in `docs/` or repo memory).
> 2. The exact supported packaging format — whether Copilot Studio topics/actions export as `.bot` ZIP, YAML directory, solution component YAML, or another format.
> 3. The most automation-friendly supported deployment path available (PAC solution export/import, pipeline task, or npm script) and confirm it works end-to-end in the target environment before committing the full file structure.
> 4. Whether a `copilot-studio/` source directory is the correct export target or whether artifacts must live inside `solution/src/` as Dataverse solution components.
>
> **Do NOT invent a folder structure or packaging approach. Evidence-first: inspect local tooling output and authoritative help docs before proposing file paths or deployment commands.**
> This verification step requires human confirmation of environment access. See Section 8 for ordered next actions.

---

## 5. What Is NOT Yet Implemented

### Missing code artifacts (coding agent must create all of these in Wave 1)

> [!NOTE]
> All paths in this table are **provisional**, pending Section 4 / Step 2 toolchain verification. If authoritative tooling evidence shows that Copilot Studio artifacts must live inside `solution/src/` rather than a separate `copilot-studio/` directory, **all paths in this table shift accordingly**. Do not treat any path here as final until Step 2 is complete.

| Artifact | Target Path | Notes |
|---|---|---|
| Copilot Studio source directory | `copilot-studio/` | Verify structure per deployment verification rule (Section 4) |
| Agent manifest / bot definition | `copilot-studio/agent.yml` or equivalent | Exact format depends on toolchain verification |
| explain-project-health topic YAML | `copilot-studio/topics/explain-project-health.yml` | Must mirror `app/src/ai/topics/explainProjectHealth.ts` contracts |
| explain-program-health topic YAML | `copilot-studio/topics/explain-program-health.yml` | Must mirror `app/src/ai/topics/explainProgramHealth.ts` contracts |
| draft-weekly-status-report topic YAML | `copilot-studio/topics/draft-weekly-status-report.yml` | Must mirror `app/src/ai/topics/draftWeeklyStatusReport.ts` contracts |
| pmo-triage-needs-attention topic YAML | `copilot-studio/topics/pmo-triage-needs-attention.yml` | Must mirror `app/src/ai/topics/pmoTriageNeedsAttention.ts` contracts |
| load-project-context action YAML | `copilot-studio/actions/load-project-context.yml` | Dataverse read action — **action definition format must be confirmed in Step 2 before authoring; do not assume format** |
| load-program-context-enriched action YAML | `copilot-studio/actions/load-program-context-enriched.yml` | Dataverse read action; record-level + related project composition — **format confirmed in Step 2** |
| load-status-context action YAML | `copilot-studio/actions/load-status-context.yml` | Dataverse read action — **format confirmed in Step 2** |
| load-portfolio-triage-context action YAML | `copilot-studio/actions/load-portfolio-triage-context.yml` | Dataverse read action — **format confirmed in Step 2** |
| `botcomponent` entry in Solution.xml | `solution/src/Other/Solution.xml` | Add after agent is registered; bump solution version to `1.1.0.0` — **coding agent must look up the correct Dataverse solution component type code for `botcomponent` from an authoritative Power Platform solution schema or PAC help reference before editing; do not assume the type code** |
| Copilot Studio connection reference | `solution/src/` | Add as solution component if required by toolchain |
| Solution export script | `scripts/export-solution.ps1` | PAC CLI export command; include `--include-customizations` |
| Solution import script | `scripts/import-solution.ps1` | PAC CLI import command for Dev/Test/Prod |
| MiraPanel agent entry point | `app/src/components/mira/MiraPanel.tsx` | **Coding agent must first verify the supported Copilot Studio web integration method available in the target environment (e.g., supported web channel / SDK / embed approach) as part of Step 2. Do not scaffold the agent entry point until that method is confirmed.** Existing fallback panel remains active alongside it. |

### Human prerequisites (environment/licensing/access/connection only, where platform requires)

Initial agent registration policy:

- Initial Mira agent record creation is not assumed to be manual by default.
- The coding agent must first verify the supported PAC CLI creation path for the target environment/toolchain.
- If `pac copilot create` is supported for the intended source model, the coding agent creates the initial agent record programmatically and captures the agent ID automatically.
- Human intervention is limited to prerequisite environment/licensing/access/connection setup only where required by the platform.
- If automation is blocked, the plan must name the exact blocker and the smallest required human action.

| # | Required Human Action | Blocks |
|---|---|---|
| H-1 | Confirm Copilot Studio environment access, licensing, and any required connection setup in the target Power Platform environment (covers environment access, licensing, and PAC CLI agent creation prerequisites) | Everything in Wave 1 |
| H-3 | If PAC CLI creation is blocked, perform only the smallest required manual action identified by the coding agent and return resulting agent ID | `botcomponent` entry, agent manifest |
| H-4 | Confirm Dataverse entity permissions for the agent's service identity (only where platform requires human setup) | Action YAML authoring |
| H-5 | Confirm approved deployment pipeline (PAC CLI, Power Platform Build Tools, or other) | Scripts |

---

## 6. Primary Deliverable and Delivery Framing

- The primary deliverable is the **Copilot Studio agent Mira**. The PMO app is a secondary workstream used as a launch surface, context source, and integration target.
- `app/src/ai/` is **the contract specification** for all Mira behavior. It is **not the agent**. The agent must be built to satisfy these contracts — it does not replace them.
- The PMO app's MiraPanel is the **launch surface** and **governed fallback**. It is not the agent runtime.
- Program must remain first-class. `app/src/api/programs.api.ts` encodes a deliberate rule: list queries exclude rollups; `getProgram()` fetches the full record. Mira must use record-level enrichment and related-project/status composition for all Program answers.
- Advisory and draft outputs never produce mutation payloads. Action-ready outputs require explicit user approval before any write path executes.

---

## 7. Wave Model

| Wave | State | Scope |
|---|---|---|
| Wave 0 | ✅ COMPLETE | App-side advisory/draft module (`app/src/ai/`), route-aware MiraPanel, AppShell integration |
| Wave 1 | ❌ NOT STARTED | **Creates Mira as a real deployed Copilot Studio agent** — four topics, four read actions, solution packaging, deployment scripts, MiraPanel agent entry point |
| Wave 2 | ❌ NOT STARTED | Enhancement — additional topics (draft-wbs-task-plan, assess-project-risk, improve-status-report-draft, identify-blockers-overdue-work, **report-bug**, **suggest-enhancement**), grounding quality improvements |
| Wave 3 | ❌ NOT STARTED | Write-intent — controlled write-intent payload builders, app handoff/deep-link integration, approval-gated mutation paths; report-bug and suggest-enhancement may evolve into approval-gated submission paths that create records after explicit user confirmation (no silent submission) |

### Wave 2 topic detail — report-bug and suggest-enhancement

Both topics are **draft-only in Wave 2**. No record creation, no silent submission.

| Topic | Output contract | Wave 2 behaviour | Wave 3 follow-on |
|---|---|---|---|
| `report-bug` | `BugReportDraft` | Captures current page/route and entity context (when available); structures user feedback into a reviewable draft; hands off draft to the approved app feedback/intake path | May evolve into an approval-gated submission path that creates a record only after explicit user confirmation |
| `suggest-enhancement` | `EnhancementSuggestionDraft` | Same route-aware prefill as above; structures the enhancement suggestion into a reviewable draft; hands off to the same feedback/intake path | Same Wave 3 follow-on as above — no silent submission in any wave |

**New output contracts required in `app/src/ai/contracts.ts` before Wave 2 topics are authored:**

- `BugReportDraft` — must include at minimum: `sourceRoute`, `sourceEntityId` (optional), `sourceEntityType` (optional), `userDescription`, `structuredDraft`, `mode: 'draft'`.
- `EnhancementSuggestionDraft` — must include at minimum: `sourceRoute`, `sourceEntityId` (optional), `sourceEntityType` (optional), `userDescription`, `structuredDraft`, `mode: 'draft'`.

Both contracts must be added to `app/src/ai/contracts.ts` and re-exported from `app/src/ai/index.ts` before any Copilot Studio topic YAML or `CONTRACTS.md` mapping is authored for Wave 2.

---

## 8. Definition of Done for Wave 1 (all conditions must be true)

1. `copilot-studio/` directory exists in the repository with all four topic YAMLs and four action YAMLs committed.
2. Agent manifest/bot definition is committed and matches the initial agent ID created programmatically via supported PAC CLI path, or the fallback ID obtained after documented automation blocker handling.
3. `solution/src/Other/Solution.xml` contains a `botcomponent` entry for the Mira agent using the **verified correct Dataverse solution component type code** (looked up from authoritative Power Platform solution schema / PAC help reference, not assumed); solution version is `1.1.0.0`.
4. All four topics return outputs that match the typed contracts in `app/src/ai/contracts.ts` — no schema divergence.
5. Scoring thresholds and health label mappings in the Copilot Studio topics exactly mirror the values in `app/src/ai/grounding/signals.ts`.
6. `scripts/export-solution.ps1` and `scripts/import-solution.ps1` exist and have been validated in the target environment.
7. MiraPanel (`app/src/components/mira/MiraPanel.tsx`) has been updated using the **verified supported Copilot Studio web integration method** confirmed in Step 2; the app-side fallback remains active alongside it.
8. `copilot-studio/CONTRACTS.md` (or equivalent contract-fidelity mapping document) is committed, mapping each Copilot Studio output field to its corresponding TypeScript contract in `app/src/ai/contracts.ts` and each scoring threshold to its matching value in `app/src/ai/grounding/signals.ts`.
9. `dist/` artifacts have been regenerated or explicitly archived so no pre-existing ZIPs from a prior solution version silently coexist with the new `1.1.0.0` solution version.
10. TypeScript build passes clean: `npx tsc -b --noEmit` exits 0 with no errors.

---

## 9. Ordered Next Actions for Wave 1

> Coding agent executes steps marked **[AUTO]**. Steps marked **[HUMAN-IF-REQUIRED]** require human action only when platform prerequisites cannot be automated.

| # | Action | Type | Dependency |
|---|---|---|---|
| 1 | Confirm Copilot Studio environment access, licensing, and connection setup (H-1) | **[HUMAN-IF-REQUIRED]** | None |
| 2 | Verify PAC CLI creation path, supported source/deployment model, supported Copilot Studio web integration method, and action definition format per Section 4 (evidence-first from local help/tooling) | **[AUTO]** | None |
| 3 | Create initial Mira agent record programmatically via supported PAC CLI path (prefer `pac copilot create` when supported) and capture agent ID automatically | **[AUTO]** | Step 2 |
| 4 | If Step 3 is blocked, document exact blocker and request the smallest required human setup action; capture resulting agent ID after action | **[AUTO + HUMAN-IF-REQUIRED]** | Step 3 |
| 5 | Confirm approved deployment pipeline | **[HUMAN-IF-REQUIRED]** | Step 2 |
| 6 | Create `copilot-studio/` directory structure (verified layout from Step 2) | **[AUTO]** | Step 2 |
| 7 | Author agent manifest/bot definition YAML | **[AUTO]** | Steps 3/4, 6 |
| 8 | Author four topic YAMLs (mirroring `app/src/ai/topics/` contracts exactly) and produce + commit `copilot-studio/CONTRACTS.md` mapping each Copilot Studio output field → `app/src/ai/contracts.ts` type and each scoring threshold → `app/src/ai/grounding/signals.ts` value | **[AUTO]** | Steps 3/4, 6 |
| 9 | Author four action YAMLs (Dataverse read actions, matching context loaders) using the **action definition format confirmed in Step 2** — do not author before format is confirmed | **[AUTO]** | Step 2, Steps 3/4, 6 |
| 10 | Add `botcomponent` to `solution/src/Other/Solution.xml`; bump version to `1.1.0.0` — **look up correct Dataverse solution component type code from authoritative Power Platform solution schema / PAC help reference before editing; do not assume** | **[AUTO]** | Step 3/4 |
| 11 | Create `scripts/export-solution.ps1` and `scripts/import-solution.ps1` | **[AUTO]** | Step 5 |
| 12 | Update `app/src/components/mira/MiraPanel.tsx` with agent entry point using the **supported Copilot Studio web integration method confirmed in Step 2** — do not scaffold until confirmed; keep fallback active | **[AUTO]** | Step 2, Step 7 |
| 13 | Run `npx tsc -b --noEmit` and confirm clean | **[AUTO]** | Step 12 |
| 14 | Run `npx power-apps push` from `app/` to deploy updated MiraPanel to Power Apps | **[AUTO]** | Step 13 |
| 15 | Validate Wave 1 Definition of Done (Section 8) — all 10 conditions | **[AUTO + HUMAN-IF-REQUIRED]** | Steps 6–14 |

---

## 10. Non-Negotiable Architectural Rules

1. **Advisory-only in Wave 1.** No write-intent payloads, no mutation paths, no action-ready outputs until Wave 3.
2. **Logic ownership.** `app/src/ai/` owns all contracts, scoring rules, thresholds, and safety constraints. Copilot Studio mirrors — it does not redefine.
3. **Fallback always active.** MiraPanel app-side advisory layer remains live until the Copilot Studio agent reaches full Wave 1 functional parity and operational reliability.
4. **No silent writes.** All agent outputs are shown to the user before any Dataverse operation. This rule applies in all waves.
5. **Approval gates mandatory.** No action-ready output may progress to execution without explicit user approval. This rule applies in all waves.
6. **Program enrichment mandatory.** Program topics always use record-level `getProgram()` + related project/status composition. List rollups must never be the sole grounding source for Program answers.
7. **Evidence-first deployment.** No folder structure, packaging format, or deployment command is invented. All must be verified from local tooling help output or authoritative docs before implementation.
8. **TypeScript build gate.** `npx tsc -b --noEmit` must pass clean before any `npx power-apps push`. This gate is mandatory after every MiraPanel change.
9. **Source-control first.** All Copilot Studio artifacts (topics, actions, agent manifest) live in the repository as committed files. No configuration exists only in the portal.
10. **Wave discipline.** Wave 2 work does not begin until all Wave 1 Definition of Done conditions are met and validated.
