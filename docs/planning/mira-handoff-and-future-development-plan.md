# Mira Handoff And Future Development Plan

> Planning-agent handoff document. This file captures the completed Mira baseline, confirmed architectural decisions, future feature candidates, and explicit anti-rediscovery guidance so future planning work does not waste premium credits re-discovering already settled facts.

---

## 1. Purpose

Use this document as the starting point for any future Mira planning work in this repository.

Primary goals:

- Preserve the implemented baseline from Waves 0-3.
- Preserve post-Wave-3 hardening updates already completed in the app codebase.
- Prevent planning agents from re-planning already completed work.
- Surface known product gaps and future feature candidates.
- Reduce redundant premium credit usage by defining a minimal authoritative read set.

---

## 2. Current Delivery Status

### Completed waves

| Wave | Status | Delivered outcome |
| --- | --- | --- |
| Wave 0 | Complete | App-side advisory and draft engine in `app/src/ai/` with typed contracts and deterministic grounding |
| Wave 1 | Complete | Mira deployed as a real Copilot Studio agent with packaged topic/action botcomponents, solution import, and publish flow |
| Wave 2 | Complete | Expanded advisory and draft topics added to the contract surface and mirrored in Copilot Studio assets |
| Wave 3 | Complete | Approval-gated mutation paths for `report-bug` and `suggest-enhancement` plus app-side submission handling |
| Wave 3 Hardening Increment 1 | Complete | Approval-gate UX polish, centralized mutation failure telemetry sink, deterministic retry payload helper, and focused Vitest coverage |

### Validation state

- Solution import and Copilot publish succeeded in Nexus RCM DEV.
- Contextual queries and action execution tested successfully.
- Connection reference is confirmed working in DEV.
- Targeted hardening test suites pass:
   - `app/src/ai/mutations.test.ts`
   - `app/src/components/mira/MiraPanel.ui.test.tsx`
   - `app/src/lib/telemetry.test.ts`
- Type-check and build pass locally (`npx tsc -b --noEmit`, `npm run build`).
- App push completed successfully to the configured DEV environment with `npx power-apps push`.
- Deployment operator note: if the shell session has inherited `IS_PAC_CLI=true`, clear it before running standalone npm CLI commands (`Remove-Item Env:IS_PAC_CLI -ErrorAction SilentlyContinue`) and keep telemetry opt-out enabled for this CLI session (`POWERAPPS_CLI_TELEMETRY=0`, `PAC_CLI_TELEMETRY_OPTOUT=1`).

### Important reality

- Mira now exists both as:
  - A Copilot Studio agent runtime
  - An app-side governed experience in `MiraPanel.tsx`
- The current product has two distinct interaction modes:
  - **Iframe chat mode**: freeform webchat when `VITE_MIRA_AGENT_URL` is set
  - **App fallback mode**: route-aware, preset quick actions backed by app-side context loaders

---

## 3. Authoritative Sources

Future planning agents should read the smallest possible authoritative set before proposing anything.

### Minimal read set

1. `app/src/ai/contracts.ts`
2. `copilot-studio/CONTRACTS.md`
3. `app/src/components/mira/MiraPanel.tsx`
4. `copilot-studio/mira-template.yml`
5. `solution/src/botcomponents/` for current deployed action/topic source artifacts
6. `docs/planning/mira-handoff-and-future-development-plan.md` (this file)

### Why this is enough

- `contracts.ts` defines the real output surface.
- `CONTRACTS.md` maps the Copilot layer to the app contract layer.
- `MiraPanel.tsx` defines the actual UX and current product behavior.
- `mira-template.yml` and `solution/src/botcomponents/` define the real deployed agent shape.
- This document captures post-delivery decisions and known future direction.

### Files planning agents should not treat as the primary truth

- `plan-miraInPmoAppFinal.prompt.md`

Reason:

- It was the execution plan before the waves were completed.
- It is useful historical context, but no longer reflects the fully implemented state.

---

## 4. Implemented Product Shape

### 4.1 Current app-side contextual capabilities

The app currently supports explicit, route-aware quick actions for these topics:

- `explain-project-health`
- `explain-program-health`
- `draft-weekly-status-report`
- `what-are-my-open-tasks`
- `what-needs-my-attention`
- `what-changed-since-last-status-report`
- `what-is-blocking-this-project-right-now`
- `draft-wbs-task-plan`
- `assess-project-risk`
- `improve-status-report-draft`
- `identify-blockers-overdue-work`
- `pmo-triage-needs-attention`
- `report-bug`
- `suggest-enhancement`

These are driven by route-aware context loading in the app and are intentionally bounded.

### 4.2 Current freeform capability

Freeform user-authored questions exist only through the embedded Copilot Studio iframe/webchat path.

Important limitation:

- The iframe chat is not currently app-context-aware.
- It does not automatically inherit route context such as active `projectId` or `programId` from the host app.

### 4.3 Important UX decision already made

Do **not** implement a classifier shim that takes arbitrary user text and forces it into the existing preset actions.

Reason:

- It degrades trust and user experience.
- It creates a false promise of open-ended questioning while only supporting a narrow intent catalog.
- Users will ask questions like "what are my open tasks?" or "what needs my attention?" that deserve first-class capabilities, not hidden mapping into unrelated shortcuts.

This decision is settled unless future product direction changes materially.

### 4.4 Current mutation and telemetry behavior

- `report-bug` and `suggest-enhancement` use explicit approval-gated mutation confirmation.
- Failure outcomes now include structured mutation metadata (`failureReason`, `failureCode`, `telemetryId`).
- Mutation failures are routed to a centralized sink in `app/src/lib/telemetry.ts` and emitted as browser event `mira-mutation-failure`.
- Retry uses a dedicated reset helper (`prepareRetryMutation`) to clear prior failure metadata before re-confirmation.
- Dataverse create operations are still mocked in `app/src/ai/mutations.ts`; production write adapters remain future scope.

---

## 5. Confirmed Architectural Decisions

### Decision A — `app/src/ai/` remains the contract authority

- Contracts, thresholds, grounding rules, and advisory/draft semantics remain authoritative in `app/src/ai/`.
- Copilot Studio must mirror or invoke these contracts, not redefine them.

### Decision B — bounded contextual actions are a valid product mode

- The app-side quick-action experience is intentionally explicit and governed.
- It is not a degraded fallback from a UX perspective; it is a curated interaction model.

### Decision C — iframe freeform and contextual quick actions are separate modes today

- Freeform exists, but without host context injection.
- Context exists, but only for bounded actions.
- A combined contextual freeform mode is not yet implemented.

### Decision D — fake freeform classification is out of scope

- Do not plan or recommend a "type anything and we will map it to a button" feature.
- If users need new questions answered, those questions should become first-class capabilities.

---

## 6. Known Needed Future Features

These are the highest-value future Mira capability gaps based on current product reality.

### Tier 1 — productionizing mutation paths and telemetry

1. **Replace mock mutation writes with real Dataverse create adapters**
   - `createBugReportRecord` and `createEnhancementSuggestionRecord` currently use mock IDs.
   - Requires final entity mapping, error handling policy, and auth/session integration.

2. **Persist mutation failure telemetry beyond browser event emission**
   - Current sink logs to console and dispatches browser event.
   - Next step is routing to durable telemetry transport/dashboard.

3. **Operational mutation observability and support workflow**
   - Define correlation between `telemetryId` and support runbook.
   - Add operator guidance for retry vs escalation.

### Tier 2 — real contextual freeform questioning in the app

This is a legitimate future feature, but only if designed as a real contextual chat experience.

Requirements for pursuing it:

- A supported host-to-chat context bridge
- Explicit route context injection into the conversational runtime
- Tool-awareness or capability-awareness inside the chat surface
- Clear unsupported-scope behavior

Do not pursue this as a text classifier over the existing button set.

### Tier 3 — UX refinement around existing two-mode experience

Potential future improvements:

- Make the difference between "guided actions" and "open chat" legible in the UI
- Add clearer language about when users should use guided actions versus freeform chat
- Add suggested prompts in iframe mode without pretending they are the full capability set
- Expand UI-level integration tests for full panel flows (beyond component-level behavior tests)

---

## 7. Recommended Future Delivery Sequence

### Recommendation

Prefer productionizing mutation write-path reliability and telemetry observability before attempting true contextual freeform chat.

### Proposed sequence

1. Implement real Dataverse write adapters for `report-bug` and `suggest-enhancement`.
2. Integrate centralized telemetry sink with durable transport/monitoring.
3. Add panel-level integration tests for end-to-end retry and submission flows.
4. Reassess whether true contextual freeform chat still delivers enough value to justify the integration complexity.

### Why this order is preferred

- It improves user value immediately.
- It closes the remaining gap between approval-gated UX and real write-path reliability.
- It avoids building a misleading pseudo-chat layer.
- It keeps future scope additive and testable.
- It reduces premium credit waste by focusing planning on concrete, bounded capabilities instead of speculative orchestration.

---

## 8. Planning-Agent Guardrails To Reduce Premium Credit Usage

Any future planning agent working on Mira should follow these rules.

### 8.1 Do not rediscover already settled facts

Do not spend cycles re-evaluating:

- Whether Waves 0-3 are complete
- Whether Wave 3 Hardening Increment 1 is complete
- Whether Mira exists as a deployed agent
- Whether action format discovery is still blocked
- Whether the connection reference works in DEV
- Whether contextual user-language capability expansion already landed (`open tasks`, `needs attention`, `changes since status`, `blocking now`)
- Whether focused hardening tests already pass locally

These are settled.

### 8.2 Do not regenerate an implementation inventory from scratch

Do not perform broad repository re-indexing if the planning task is only about future work.

Instead, use the minimal read set in Section 3.

### 8.3 Do not propose the classifier-shim idea again

This has already been rejected on product grounds.

Rejected idea:

- User types arbitrary question
- App classifies it into an existing preset action

Reason for rejection:

- It degrades UX and weakens trust.

### 8.4 Prefer bounded planning increments

Planning agents should frame future work as one of:

- new contextual capability
- new context loader
- new contract
- new agent topic/action pair
- new host integration capability

Avoid broad “make Mira smarter” plans.

### 8.5 Use premium analysis only for unresolved design tradeoffs

Premium analysis is justified for:

- deciding between a real host-context bridge architecture versus status quo
- designing a task-centric query model
- resolving scope and semantics for new first-class capabilities

Premium analysis is **not** justified for:

- re-reading completed wave artifacts end to end
- reconstructing current status
- re-arguing already settled product decisions

---

## 9. Suggested Planning Prompt Shape For Future Agents

When handing Mira to a planning agent, use a prompt with these constraints:

1. Start from `docs/planning/mira-handoff-and-future-development-plan.md`.
2. Treat Waves 0-3 as complete and validated.
3. Do not propose a classifier shim for arbitrary text.
4. Produce a plan for one bounded increment only.
5. Reuse current contracts and context loader patterns where possible.
6. Identify only net-new files, contracts, topics, actions, and UI changes.
7. Call out where premium-credit-intensive research is actually needed.

### Example bounded planning asks

- Plan Dataverse create adapter implementation for Wave 3 mutation topics.
- Plan telemetry transport integration for `mira-mutation-failure` browser events.
- Plan a host-context bridge for true contextual freeform chat if supported by the current Copilot Studio web integration model.

---

## 10. Future Scope Definitions

### 10.1 mutation create adapter implementation

Expected design characteristics:

- explicit Dataverse entity mapping for bug/enhancement request creation
- deterministic handling of transport/auth failures with stable failure codes
- no silent writes, preserving approval gate and explicit user confirmation behavior

Likely deliverables:

- write adapters in `app/src/ai/mutations.ts`
- finalized request payload mappings
- integration tests for success/failure write behavior
- runbook notes for support and telemetry correlation

### 10.2 telemetry transport integration

Expected design characteristics:

- preserve `telemetryId` continuity from mutation result surface to telemetry backend
- non-blocking user experience even when telemetry transport fails
- clear contract between frontend sink and downstream observability platform

### 10.3 contextual freeform chat

This is a higher-cost feature.

It should only proceed if future planning can answer yes to all of these:

- Can the host app inject route context into the chat runtime through a supported integration path?
- Can the conversational surface access explicit tools/capabilities rather than a hidden classifier trick?
- Can unsupported arbitrary questions fail gracefully without eroding trust?

If any answer is no, defer this feature and continue building first-class capabilities instead.

---

## 11. Non-Goals For The Next Planning Cycle

Unless explicitly requested, future planning should not include:

- rebuilding Waves 0-3
- rebuilding Wave 3 hardening increment 1
- replacing quick actions with a pseudo-chat router
- removing the current app-side governed experience
- broad unbounded “ask anything” promises without contextual runtime support

---

## 12. Handoff Summary

Mira is no longer a bootstrap concept. It is a delivered, tested feature set with a known product boundary and an active post-Wave-3 hardening baseline.

The next planning cycle should focus on **productionizing mutation write paths and telemetry transport** rather than re-planning already delivered contextual capabilities or disguising a bounded workflow assistant as arbitrary conversational intelligence.

If a planning agent is invoked, this document should be treated as the current source of truth for:

- what is already done
- what product decisions are already settled
- what future work is actually worth planning
- how to avoid wasting premium credits on rediscovery
