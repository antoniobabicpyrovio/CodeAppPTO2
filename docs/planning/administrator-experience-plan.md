# Administrator Experience Plan Review

> **Generated:** 2026-04-23 | **Revised:** 2026-04-23 (redline pass)
> **Scope:** PMO CFR Solution — corp-fin-bi-pmo-cfr-solution
> **Based on:** Full codebase review of app/src, solution, and docs/planning

---

## 1. Current-State Findings

### 1.1 App Structure

The PMO app is a React/TypeScript Power Apps code-app with a `HashRouter`-based SPA. Navigation is managed by a single `Sidebar.tsx` with four hardcoded nav sections. There are 27 routes currently registered in `App.tsx`, including an existing `/admin/settings` route that renders `AdminSettingsPage.tsx`.

Runtime configuration is backed by the `pmo_appsetting` entity (key-value store). All entity type definitions, option-set values, and display constants live in `app/src/lib/constants.ts`. There is no feature-flag infrastructure and no permission enforcement anywhere in the frontend code.

### 1.2 What the Existing Admin Surface Covers

`AdminSettingsPage.tsx` already delivers meaningful admin capability across five sections:

| Section | Backed by | Admin Can Do |
|---|---|---|
| App Settings | `pmo_appsetting` (3 known keys) | Set fallback triage team, AAD user-scope group, default project template |
| Intake Workflows | `pmo_gatesettemplate` + `pmo_gatesetitem` | Full CRUD for workflow definitions, field-to-project mapping, default flag |
| Intake Stage Editor | `pmo_gatesetitem` | Per-stage required fields, artifact types, approval gates, approver AAD group |
| Project Templates | `pmo_projecttemplate` | Template CRUD: name, CFR category, JSON task payload |
| Required Artifacts | `pmo_requiredartifact` | Which artifact types are required per CFR category |

The `TeamsPage` at `/teams` also has a lightweight admin affordance: per-team default template assignment via the `pmo.team_default_template.<teamId>` app-setting key. This affordance currently has no role gate and is accessible to all users.

These are well-built admin surfaces. The `intakeValidation.ts` module, the `intakeConversion.ts` module, and the `IntakeStageEditor` component are production-quality and should serve as the pattern for all new admin sections.

### 1.3 Configuration Gaps — Hardcoded Values Requiring Code Changes

The following operational parameters have no admin surface and require a code deployment to change:

**Intake and Routing**
- `app/src/lib/intakeRoutingConfig.ts` — The entire routing table (7 team domains, keyword lists per domain, `confidenceFloor` per domain (55–70)) is static TypeScript. A PMO admin cannot adjust routing logic without a developer and a push.
- `app/src/hooks/useIntakeTriage.ts` lines 9–11 — Similarity lookback window (90 days), match score threshold (0.1), top-N results (3).

**Dashboard Display Rules**
- `app/src/pages/Dashboard/DashboardPage.tsx` line 271 — "Due soon" window is 30 days (hardcoded `setDate(+30)`).
- Lines 267, 289 — "Needs Attention" capped at 6 items, "Recent Intake" capped at 7 items.
- Lines 540–548 — Day-badge color breaks: 0 days = rose, ≤7 days = amber, else muted.

**Analytics and Prioritization**
- `app/src/hooks/usePrioritizationScoring.ts` lines 11–17 — Five scoring weights (Strategic Priority 35, Complexity 20, Health 15, Budget 15, Progress 15). These are strategic business parameters, not implementation details.
- Lines 43–46 — Budget tier thresholds: ≥$500K = 100 pts, ≥$100K = 70 pts, ≥$25K = 40 pts.

**AI and Mira**
- `app/src/components/mira/MiraPanel.tsx` lines 882–893 — The visible quick-action topic list (which actions appear, their labels) is hardcoded.
- Line 570 — Risk score band thresholds: <6 = secondary, 6–9 = outline, ≥10 = destructive.
- `app/src/ai/grounding/signals.ts` lines 66–77 — AI signal thresholds: ≤2 risks/issues = warn, >2 = critical.

**Notifications**
- `app/src/hooks/useNotifications.ts` line 14 — Poll interval is 60 seconds.
- `app/src/components/layout/NotificationCenter.tsx` lines 7–19 — Category labels and badge colors are hardcoded.

**SharePoint Integration**
- `app/src/lib/constants.ts` lines 467–471 — 13 SP document category strings are a hardcoded array.

**Initiation Readiness**
- `app/src/components/projects/InitiationWorkspace.tsx` — All 8 readiness dimensions and their logic are entirely hardcoded. Also, `GovernWorkspace.tsx` line 47 has `const initiationComplete = false` acknowledged as a stub.

**Environment-Specific Values Baked Into Source**
- `constants.ts` line 298 — `PMO_TEAM_FLAG = 'cr741_pmoteam'` with a comment that it must change before UAT/PROD. This is the most dangerous kind of hardcoding — it actively requires a manual code change during deployment.
- `constants.ts` line 306 — `TENANT_ID` (Azure AD GUID) hardcoded for Planner deep-link construction.

### 1.4 Permissions Model — A Critical Gap

There is zero permission enforcement in the application frontend. Every user who can access the app can see the Administration sidebar section, navigate to `/admin/settings`, create templates, modify workflows, and change app settings. Security is fully delegated to Dataverse row-level security and environment access, but the app itself provides no role-based surface distinction whatsoever. This means:
- A project manager can delete intake workflows.
- A read-only stakeholder could attempt to edit project templates (the Dataverse write would fail, but the UI offers no indication that they should not try).
- There is no operational boundary between the admin surface and the rest of the app.

---

## 2. Recommended Administrator Experience Vision

### 2.1 Purpose

The Administrator area exists to give designated PMO operations staff and system administrators direct in-app control over **routine operational configuration** — the parameters, reference data, and display rules that currently require a developer and a redeployment to adjust, but which contain no platform-critical or schema-level logic that warrants code ownership.

The scope is deliberately bounded. Dataverse schema, protected workflow logic, approval state machines, security model enforcement, AI topic implementations, and platform integration mechanics remain code-owned. The admin area controls runtime-safe configuration only. It is not a general management surface for the application.

Every capability added to the admin area must satisfy all three of the following conditions:
1. A trained PMO administrator can manage it safely without code access.
2. It would otherwise require a code change and redeployment to adjust.
3. Misconfiguration is either recoverable or gated by validation and simulation affordances.

### 2.2 Who the Admin Experience Is For

Two roles should have structured admin access, with distinct scopes:

| Role | Scope | Examples |
|---|---|---|
| **PMO Administrator** | Operational configuration — routing, display, scoring, reference data, Mira topics | Routing rules, dashboard thresholds, document categories, Mira topic visibility |
| **System Administrator** | Environment-level settings and integration config | Tenant ID, team field flag, feature toggles, Mira agent URL |

Today, neither role exists in the app — there is one undifferentiated admin page accessible to all users.

### 2.3 Admin Domains: Near-Term vs. Later-Wave

The following domains are candidates for admin control. They are not all equivalent in priority or urgency. The delivery plan (§6) sequences them explicitly.

| Domain | Near-Term (Phases 1–3) | Later-Wave (Phases 4+) |
|---|---|---|
| Role gating and route guard | ✓ Phase 1 — mandatory | |
| Admin audit trail | ✓ Phase 1 — mandatory | |
| Runtime config provider | ✓ Phase 1 — mandatory | |
| Dashboard display rules | ✓ Phase 2 — quick win | |
| Document categories | ✓ Phase 2 — quick win | |
| Triage similarity parameters | ✓ Phase 2 — quick win | |
| Notification poll / display | ✓ Phase 2 — quick win | |
| Environment constants (team flag, tenant ID) | ✓ Phase 2 — quick win | |
| Intake routing configuration | ✓ Phase 3 — core expansion | |
| Prioritization scoring weights | | Phase 4 — on demand |
| AI signal thresholds | | Phase 4 — on demand |
| Mira topic visibility / mode | | Phase 5 — on demand |
| Feature toggles | | Phase 5 — on demand |
| Initiation readiness dimensions | | Phase 6 — on demand |
| Notification message templates | | Phase 6 — on demand |

### 2.4 Bootstrap Model and First-Run Access

Admin role resolution is based entirely on Dataverse security roles — no user ID lists are stored in the app. This means the bootstrap problem is simpler: a user with the Dataverse built-in **System Administrator** role automatically has `system_admin` access the moment the solution is deployed. No additional seeding of user identities is required.

**Bootstrap approach:**

**Layer 1 (primary): Dataverse security role assignment.** Assign the built-in System Administrator role or the custom PMO Administrator role to the appropriate users in the Power Platform Admin Center (or via environment-level role assignment). This is the standard Power Platform administrative action — no app-specific step required.

**Layer 2: Solution import deploys the custom PMO Administrator role.** The `scripts/seed-env-settings.js` deployment script seeds only environment-specific app settings (`pmo.pmo_team_field`, `pmo.tenant_id`). It does not manage user role assignments — those are done through Power Platform Admin Center.

```
node scripts/seed-env-settings.js \
  --environment <environment-url> \
  --tenantId <azure-ad-tenant-guid> \
  --pmoTeamField <field-logical-name>
```

**Layer 3 (no-config state): Graceful inaccessibility.** If the current user has neither the built-in System Administrator role nor the custom PMO Administrator role, the admin area is hidden. No error is shown — the app functions normally. Access is granted by assigning the appropriate Dataverse security role in Power Platform Admin Center.

**Bootstrap sequence for a new environment:**
1. Run `pac solution import` to deploy the solution (including the custom PMO Administrator security role definition).
2. Run `scripts/seed-env-settings.js` to seed environment-specific app settings.
3. In Power Platform Admin Center, assign the PMO Administrator role to the relevant users. Environment admins already have System Administrator — they have immediate access.
4. A System Administrator user opens the app and navigates to the System tab.
5. Verify environment settings are present and correct.

### 2.5 Graph Prerequisite Validation

> **Gate 1 — COMPLETE (2026-04-23). Result: BLOCKED by CSP.**

The Power Apps host sets `Content-Security-Policy: connect-src 'none'` on code app iframes. A probe was deployed and tested in the live environment. Browser console output:

```
Connecting to 'https://graph.microsoft.com/v1.0/me/memberOf?...' violates the following
Content Security Policy directive: "connect-src 'none'". The action has been blocked.
```

**Graph API calls from client-side code app JavaScript are impossible.** This is not a permissions issue — it is a hard platform constraint. No Graph endpoints are reachable via `fetch()` or `XMLHttpRequest` from inside a Power Apps code app iframe.

**Resolved role-resolution approach: Dataverse security roles only (no Graph, no user ID lists).**

`useCurrentUserRole()` resolves admin role entirely from the current user's Dataverse security role assignments. No user identity lists are stored or managed in the app.

Role mapping:
- Dataverse built-in **System Administrator** security role → `userAdminRole = 'system_admin'`
- Custom **PMO Administrator** security role (defined in the solution) → `userAdminRole = 'pmo_admin'`
- No matching role → `userAdminRole = 'none'`

Resolution uses the Dataverse OData API (through `@microsoft/power-apps/data` — not blocked by CSP):
```typescript
// Query the current user's security role assignments
// systemuserroles_association navigation property on systemuser
dv.list('roles', {
  $filter: `systemuserroles_association/any(u: u/systemuserid eq ${currentUserId})`,
  $select: 'name,roleid',
})
// Map name to userAdminRole:
//   'System Administrator' → 'system_admin'
//   'PMO Administrator'    → 'pmo_admin'
//   (else)                 → 'none'
```

If `system_admin` and `pmo_admin` both match (user has both roles), resolve to `'system_admin'`.

**Consequence for solution:** The custom "PMO Administrator" security role must be defined in the solution and deployed with it. Role assignment is performed in Power Platform Admin Center — not in the app.

`pmo.admin_group_ids_json`, `pmo.admin_access_json`, `AdminGroupConfig`, and `AdminAccessConfig` are all **cancelled**. No user identity data of any kind is stored in the application or its settings.

---

## 3. Candidate Admin-Managed Capabilities

### Capability Classification

Before the detailed entries, the full capability set is classified into two groups. This distinction matters for sequencing and risk tolerance.

**Quick wins** — low complexity, low risk, purely data-driven, no behavioral impact beyond display or parameter tuning. Hardcoded values that have no logical reason to be in source code.

| Capability | Section | Phase |
|---|---|---|
| Dashboard display rules (windows, limits, day-badge thresholds) | §3.3 | 2 |
| SharePoint document categories | §3.8 | 2 |
| Intake triage similarity parameters | §3.4 | 2 |
| Notification poll interval and display labels | §3.7 | 2 |
| Environment constants (PMO team flag, tenant ID) | §3.10 | 2 |

**Strategic governance controls** — higher behavioral impact, shape operational outputs, require simulation affordances or tighter audit discipline.

| Capability | Section | Phase |
|---|---|---|
| Role-based surface gating (full-app) | §3.12 | 1 (mandatory) |
| Admin change audit log | §3.13 | 1 (mandatory) |
| Intake routing configuration | §3.1 | 3 |
| Prioritization scoring weights and budget tiers | §3.2 | 4 |
| AI signal thresholds and Mira risk score bands | §3.6 | 4 |
| Mira quick action visibility and mode | §3.5 | 5 |
| Feature toggles | §3.11 | 5 |
| Initiation readiness dimensions | §3.9 | 6 |
| Notification message templates | §3.7 | 6 |

---

### 3.1 Intake Routing Configuration

**Current state:** `app/src/lib/intakeRoutingConfig.ts` exports a hardcoded `INTAKE_ROUTING_CONFIG` constant — an array of 7 team domain objects, each with a `domainName`, `teamId` (Dataverse GUID), `keywords` array, and `confidenceFloor` integer. The runtime routing logic in `useIntakeTriage.ts` reads this constant directly. Changing routing behavior requires modifying TypeScript source and redeploying.

**Why admin-managed:** Routing keyword lists need tuning as intake patterns evolve, teams split or merge, and new subject matter areas emerge. This is the most operationally significant configuration gap in the codebase — routing errors directly cause intake requests to reach the wrong team. A PMO administrator should be able to adjust keywords and confidence floors without filing a developer ticket.

**Recommended design:** Add an **Intake Routing Rules** section to `AdminSettingsPage`. Each domain is a record displayed as an accordion — expand to see and edit the keyword list (tag input), confidence floor (slider 30–90), and mapped team (team picker). A "Test Route" affordance accepts a free-text description and shows which domain it would route to at current confidence settings.

**Data/storage approach:** Store the full routing config as a single JSON blob in `pmo_appsetting` key `pmo.intake_routing_config_json`. No schema change required. The `intakeRoutingConfig.ts` module is replaced by a `useIntakeRoutingConfig()` hook that reads the setting from `ConfigurationProvider` and falls back to the hardcoded constant if the setting is absent or fails validation.

A more complex relational entity (`pmo_intakeroutingdomain`) is explicitly deferred — the JSON blob approach satisfies the operational requirement without a schema change.

**Security/permissions:** PMO Administrator role only. Routing config changes affect all intake triage results — this is high-impact configuration.

**Audit needs:** Every save writes a timestamped entry to the admin audit log (§3.13).

**Implementation complexity:** Medium. The runtime hook swap from static import to dynamic fetch is straightforward. The UI is a form with tag inputs, a slider, and a Dataverse team picker — all patterns already present in the codebase.

**Dependencies:** `useAppSettings` hook, `upsertSetting` API, Dataverse team picker (already in `WorkflowForm`). Validation: `validateRoutingConfig()` in `intakeValidation.ts` pattern.

**Risks:** The fallback to the hardcoded constant is non-negotiable — if the setting is malformed JSON, routing must not break. Add a "Last validated: [timestamp]" display in the routing section.

---

### 3.2 Prioritization Scoring Weights and Budget Tiers

**Current state:** `app/src/hooks/usePrioritizationScoring.ts` lines 11–17 define five hardcoded weights (Strategic Priority: 35, Complexity: 20, Health: 15, Budget: 15, Progress: 15). Budget tier breakpoints are at lines 43–46 ($500K, $100K, $25K). These weights directly control the prioritization rank order shown in `AnalyticsPrioritizationPage` and influence the `ScenarioPage` analysis.

**Why admin-managed:** These are strategic business parameters — leadership may decide to weight strategic priority higher during planning cycles or reduce the health weighting during operational stability periods. They are not code.

**Recommended design:** Add a **Scoring Configuration** sub-section in the admin area. Display five weight sliders (values 0–100 with live sum shown; must total 100 to save). Display three budget tier threshold inputs ($USD). A live preview table shows how the current top 10 projects would re-rank under the new weights before saving.

**Data/storage approach:** Two `pmo_appsetting` keys: `pmo.prioritization_weights_json` and `pmo.prioritization_budget_tiers_json`. These are intentionally kept as separate keys because they are independently validated and independently defaulted. The hook reads these on load, falls back to hardcoded defaults.

**Security/permissions:** PMO Administrator.

**Audit needs:** Changes logged with before/after values. Strategic weights should not change silently.

**Implementation complexity:** Low. Hook modification is trivial. UI is sliders and number inputs.

**Risks:** Weights must sum to exactly 100 — enforce client-side before save. Budget tiers must be sorted descending and non-overlapping — validate on save. Live preview before save strongly recommended.

---

### 3.3 Dashboard Display Rules

**Current state:** `DashboardPage.tsx` hardcodes:
- Line 271: 30-day "due soon" window
- Line 267: 6 items in "Needs Attention"
- Line 289: 7 items in "Recent Intake"
- Lines 540–548: day-badge color thresholds (0 days = rose, ≤7 days = amber)

**Why admin-managed:** These are operational display preferences with no principled reason to be compile-time constants.

**Recommended design:** A **Dashboard Display** settings sub-section with integer inputs for: Due Soon window (days), Needs Attention limit, Recent Intake limit, Day badge urgent threshold, Day badge warning threshold.

**Data/storage approach:** Single `pmo_appsetting` key `pmo.dashboard_display_config_json`. See §4.6 for the full interface definition.

**Security/permissions:** PMO Administrator.

**Audit needs:** Low-risk cosmetic config — log changes.

**Implementation complexity:** Low. Pure read from `ConfigurationProvider`, fallback to current defaults.

**Risks:** Validate ranges client-side (no negatives, limits ≤ 50). `urgentDayThreshold` must be strictly less than `warningDayThreshold` — if violated, warn the user but do not block save (matches §4.6 invariant).

---

### 3.4 Intake Triage Similarity Parameters

**Current state:** `app/src/hooks/useIntakeTriage.ts` lines 9–11: `SIMILAR_DAYS = 90`, `SIMILAR_THRESHOLD = 0.1`, `SIMILAR_TOP_N = 3`. These affect whether the triage panel surfaces existing similar requests before a new one is submitted.

**Why admin-managed:** As intake volume grows, the lookback window and threshold need tuning to keep results relevant.

**Recommended design:** Three settings: lookback days (integer), minimum match score (0.0–1.0 slider), maximum similar results shown (1–10 integer).

**Data/storage approach:** `pmo.intake_triage_similarity_config_json`. See §4.6 for interface.

**Security/permissions:** PMO Administrator.

**Audit needs:** Log changes.

**Implementation complexity:** Very low. Three values read from `ConfigurationProvider` in the hook.

**Risks:** Incorrect values degrade UX but don't break functionality. No simulation affordance needed.

---

### 3.5 Mira Quick Action Configuration

**Current state:** `MiraPanel.tsx` lines 882–893 hardcode the topic list. The `VITE_MIRA_AGENT_URL` env var activates iframe mode with no admin surface.

**Why admin-managed:** Topics should be activatable/deactivatable by configuration as the catalog grows. The env-var toggle for Copilot Studio mode is operationally unsafe — it requires a build-time change for a runtime switch.

**Recommended design:**
1. **Topic Visibility Toggle:** A table of all registered Mira topics with an enabled/disabled toggle per topic. The topic list comes from `MIRA_TOPIC_REGISTRY` (code-defined constant); the enabled state comes from `pmo.mira_topic_visibility_json`. The topic logic in `ai/topics/` is not configurable — only which registered topics surface in the panel.
2. **Mira Mode and URL:** A single `pmo.mira_config_json` setting containing both `mode` and `agentUrl`. Replaces `VITE_MIRA_AGENT_URL` env var.

**Data/storage approach:** `pmo.mira_topic_visibility_json` (PMO Admin scope), `pmo.mira_config_json` (System Admin scope). These are kept separate because they have different role-scopes. See §4.6 for interfaces.

**Security/permissions:** System Administrator for `pmo.mira_config_json`. PMO Administrator for `pmo.mira_topic_visibility_json`.

**Audit needs:** Mode changes must be audited — switching from app to Copilot Studio is a significant behavioral shift.

**Implementation complexity:** Medium. `MiraPanel.tsx` is complex; the topic rendering loop must filter against visibility settings. The env-var elimination requires moving the startup read to `ConfigurationProvider`.

**Risks:** If topic visibility setting is absent or malformed, default to all topics visible. Never allow Mira to go dark silently.

---

### 3.6 AI Signal Thresholds

**Current state:** `app/src/ai/grounding/signals.ts` lines 66–77: risks/issues ≤2 = warn, >2 = critical. `MiraPanel.tsx` line 570: risk score <6 = secondary, 6–9 = outline, ≥10 = destructive.

**Why admin-managed:** Portfolio-norm calibration. Hardcoded thresholds of 2 will flood large portfolios with "critical" AI signals, eroding signal value. These are display calibration parameters, not topic logic.

**Recommended design:** Four threshold inputs: risk count warn, risk count critical, risk score warn, risk score critical. Validate that critical > warn for each pair.

**Data/storage approach:** `pmo.mira_signal_thresholds_json`. See §4.6 for interface.

**Security/permissions:** PMO Administrator.

**Implementation complexity:** Low. Replace magic numbers with `ConfigurationProvider` reads. Topic computation logic in `ai/topics/` is not affected.

---

### 3.7 Notification Configuration

**Current state:** Poll interval is 60 seconds (`useNotifications.ts` line 14). Category labels and badge colors are hardcoded inline in `NotificationCenter.tsx`. No message template system exists.

**Why admin-managed:** Poll interval is a resource cost tuning parameter. Category labels should be customizable to match organizational terminology.

**Recommended design:**
1. **Notification Display Config (Phase 2):** Poll interval, category label overrides, badge color overrides — all stored in a single `pmo.notification_display_config_json` object. The `pollIntervalMs` field in this object replaces what would have been a standalone key.
2. **Notification Templates (Phase 6 — later wave):** Named templates with `{{projectName}}` and `{{gateName}}` placeholder syntax. Deferred because placeholder substitution requires additional infrastructure and multiple callsite changes.

**Data/storage approach:** `pmo.notification_display_config_json` for all Phase 2 notification settings (including poll interval — see §4.6). Notification templates stored as `pmo.notification_template.<templateKey>` keys in Phase 6. There is no standalone `pmo.notification_poll_interval_ms` key — the poll interval is a field inside the display config object.

**Security/permissions:** PMO Administrator.

**Audit needs:** Template changes logged. Display config changes logged.

**Implementation complexity:** Display config is low (Phase 2). Template system is medium (Phase 6).

---

### 3.8 SharePoint Document Categories

**Current state:** `app/src/lib/constants.ts` lines 467–471 define `SP_DOCUMENT_CATEGORIES` as a hardcoded array of 13 string values.

**Why admin-managed:** Pure reference data. Document taxonomy evolves; this has no reason to be in source code.

**Recommended design:** A **Document Categories** sub-section with add/remove/reorder capability. Runtime reads from `pmo.sp_document_categories_json`, falling back to the hardcoded constant.

**Data/storage approach:** `pmo.sp_document_categories_json` — ordered string array. See §4.6.

**Security/permissions:** PMO Administrator.

**Implementation complexity:** Very low. The simplest admin capability on this list.

---

### 3.9 Initiation Readiness Dimensions

**Current state:** `InitiationWorkspace.tsx` computes 8 hardcoded readiness dimensions. `GovernWorkspace.tsx` line 47 has `const initiationComplete = false` as an acknowledged stub.

**Why admin-managed:** Governance configuration, not application behavior. The PMO may evolve what constitutes initiation readiness.

**Recommended design:** Each dimension can be toggled required/optional and given a custom label. The underlying computation logic per dimension remains code-owned. Administrators cannot create new dimension logic — the dimension ID set is closed and defined in code.

**Data/storage approach:** `pmo.initiation_readiness_config_json` — array of `{dimensionId, label, required, weight}`. See §4.6 for interface.

**Security/permissions:** PMO Administrator.

**Audit needs:** Medium — changes affect all project initiation assessments.

**Implementation complexity:** Medium. `InitiationWorkspace.tsx` requires targeted refactoring to read dimension config from `ConfigurationProvider`. Computation logic per dimension remains code-locked. Requires regression testing of all 8 dimensions.

---

### 3.10 Environment-Specific Constants (PMO Team Flag, Tenant ID)

**Current state:**
- `constants.ts` line 298: `PMO_TEAM_FLAG = 'cr741_pmoteam'` — must change before UAT/PROD.
- `constants.ts` line 306: `TENANT_ID` hardcoded for Planner deep-link construction.

**Why admin-managed:** Environment topology values. Currently require a code edit at every environment promotion — a deployment footgun.

**Recommended design (System Admin only):** An **Environment Settings** section. At startup, `ConfigurationProvider` reads `pmo.pmo_team_field` and `pmo.tenant_id` and overrides the compile-time constants before any component renders. Compile-time values remain as fallback.

These settings are seeded by the `scripts/seed-env-settings.js` deployment script (§2.4, §6 Phase 2). The System Admin UI allows viewing and overriding them post-deploy.

**Data/storage approach:** Plain string values (not JSON): `pmo.pmo_team_field`, `pmo.tenant_id`.

**Security/permissions:** System Administrator only.

**Audit needs:** Full audit trail.

**Implementation complexity:** Low for storage. Medium for `ConfigurationProvider` startup override — must happen before any component using `PMO_TEAM_FLAG` or `TENANT_ID` renders.

---

### 3.11 Feature Toggles

**Current state:** Zero feature toggle infrastructure. `VITE_MIRA_AGENT_URL` is the only behavioral toggle.

**Why admin-managed:** Controlled rollout infrastructure as the app matures. Not a near-term operational need.

**Recommended design:** `FEATURE_FLAG_REGISTRY` constant defines the closed set of flag IDs. The System Admin UI shows a toggle table. Each flag is globally on or globally off. Scoped rollout (by user or group) is deferred — AAD group scoping is unavailable (CSP blocks Graph, §2.5) and per-user ID lists are not an acceptable security model.

**Data/storage approach:** `pmo.feature_flags_json`. See §4.6.

**Security/permissions:** System Administrator.

**Implementation complexity:** Medium. Requires `FEATURE_FLAG_REGISTRY`, `useFeatureFlag(flagId)` hook, and admin UI.

---

### 3.12 Role-Based Surface Gating (Mandatory — Full-App Scope)

**Current state:** Zero role gating. Every user reaches the admin surface and all admin affordances.

**Why this must be addressed first:** Without surface gating, expanding admin capabilities is operationally unsafe.

**Full-app gating rule — implementation invariant:**
This is not limited to hiding the sidebar section and guarding `/admin/settings`. The gating requirement applies to **every admin-only write affordance in the application**, wherever it appears. The implementation must enforce this as an invariant:

> Any React component that renders a UI affordance that writes to an admin-owned entity must gate that affordance on `userAdminRole`. Admin-owned entities are: `pmo_appsetting`, `pmo_gatesettemplate`, `pmo_gatesetitem`, `pmo_projecttemplate`, `pmo_requiredartifact`, `pmo_telemetryevent` (admin audit writes only — via `useAdminAudit()`).

**Known out-of-admin-area admin affordances (must be gated):**
- `TeamsPage.tsx` — the per-team default template assignment calls `upsertSetting()` against `pmo_appsetting`. This affordance must be hidden for `userAdminRole = 'none'`. PMO Admin is the minimum required role for this action.

**Implementation:**
1. `useCurrentUserRole()` hook — resolves `userAdminRole: 'none' | 'pmo_admin' | 'system_admin'` by querying the current user's Dataverse security role assignments at startup (§2.5). Built-in System Administrator role → `'system_admin'`; custom PMO Administrator role → `'pmo_admin'`. No user ID lists. Graph is not available (CSP blocks all external fetch).
2. `useRequireAdminRole(requiredRole: 'pmo_admin' | 'system_admin'): boolean` — convenience hook that returns true if the current user meets or exceeds the required role. Components use this to conditionally render admin affordances.
3. **Sidebar:** Administration section hidden for `userAdminRole = 'none'`.
4. **Route `/admin/settings`:** Redirects to `/dashboard` for `userAdminRole = 'none'`.
5. **Admin page tabs:** System tab rendered only for `userAdminRole = 'system_admin'`.
6. **TeamsPage:** Per-team template assignment affordance hidden for `userAdminRole = 'none'`.
7. **Any future admin affordance** outside `/admin/settings` must use `useRequireAdminRole()` before rendering.

**Data/storage approach:** No app-level storage for admin role assignment. Role resolution reads Dataverse security role assignments for the current user at startup via `systemuserroles_association`. Role assignment is managed entirely in Power Platform Admin Center.

**Solution artifact required:** The custom **PMO Administrator** security role must be defined in the solution and deployed with `pac solution import`. This is a solution component, not an app setting.

**Security model:** The app's role gating is a display gate only. Dataverse row-level security is the enforcement layer. If a user bypasses the UI and calls the API directly, Dataverse security must reject unauthorized writes.

**Risks:** If the security role query fails (e.g., Dataverse unavailable at startup), default to `userAdminRole = 'none'` — never to elevated access on query failure.

---

### 3.13 Admin Change Audit Log (Mandatory)

> **Gate 2 — COMPLETE (2026-04-23).** Schema assessed. Decision: **extend `pmo_telemetryevent`. No new entity. No new columns. No solution schema change required.**

**Current state:** No admin audit trail exists. Changes to templates, workflows, app settings, and routing rules leave no record.

**Why required:** As admin capabilities expand, traceability is essential. When a routing change breaks triage behavior, administrators need to know what changed, when, and by whom.

**Assessment result — `pmo_telemetryevent` supports admin audit without schema changes:**

The existing entity fields cover all audit requirements:

| Audit requirement | `pmo_telemetryevent` field | Value for admin audit |
|---|---|---|
| Who changed it | `_createdby_value` (Dataverse system field, auto-populated) | The admin user's system user ID |
| When | `createdon` (Dataverse system field) | Timestamp of the write |
| What was changed | `pmo_source` (free-text string) | Setting key or entity name (e.g., `pmo.intake_routing_config_json`) |
| Domain/category | `pmo_eventtype` (free-text string) | `'AdminChange'` |
| Before/after state | `pmo_payload` (existing JSON blob field) | `{ settingKey, oldValue, newValue }` |
| Severity | `pmo_severity` (option-set) | `TELEMETRY_SEVERITY.Info` (893460140) |

No new columns needed. No schema change to the solution. `pmo_adminchangelog` is cancelled.

**Field mapping for `useAdminAudit()` writes:**
```typescript
createTelemetryEvent({
  pmo_eventtype: 'AdminChange',
  pmo_severity: TELEMETRY_SEVERITY.Info,
  pmo_source: settingKey,           // e.g. 'pmo.intake_routing_config_json'
  pmo_payload: JSON.stringify({ settingKey, oldValue, newValue }),
});
// _createdby_value and createdon are auto-populated by Dataverse
```

**Querying admin change history:**
```typescript
listTelemetryEvents(`pmo_eventtype eq 'AdminChange' and statecode eq 0`)
```
Expand `_createdby_value` to get display name for changed-by column.

**Admin surface:** `/admin/change-history` page — filtered log view with date range picker, domain filter (from `pmo_source`), changed-by filter. Rows expand to show human-readable before/after diff.

**Implementation:** `useAdminAudit()` hook that wraps `createTelemetryEvent()`. Called in every admin section save handler — built into the shared save pattern from the start, not added per-section later.

**Security/permissions:** Readable by all admin roles. Not writable through any admin UI — write path is exclusively through `useAdminAudit()`.

---

## 4. Architecture and Data Model Changes

### 4.1 What to Extend vs. Introduce New

**Extend `pmo_appsetting` (existing):**
All JSON-blob configuration settings route through this entity. New settings require only a new constant key in `constants.ts` and a new accordion section in `AdminSettingsPage.tsx`. No solution schema change is required for any setting added as a JSON blob.

New `pmo_appsetting` keys required, normalized by domain:

| Key | Domain | Phase | Notes |
|---|---|---|---|
| `pmo.dashboard_display_config_json` | Dashboard display rules | 2 | |
| `pmo.intake_triage_similarity_config_json` | Triage similarity params | 2 | |
| `pmo.notification_display_config_json` | Notification display config | 2 | Includes poll interval — no separate poll key |
| `pmo.pmo_team_field` | PMO team entity field name | 2 | Plain string, not JSON |
| `pmo.tenant_id` | Azure AD tenant ID | 2 | Plain string, not JSON |
| `pmo.sp_document_categories_json` | SP document categories | 2 | |
| `pmo.intake_routing_config_json` | Intake routing rules | 3 | |
| `pmo.prioritization_weights_json` | Scoring weights | 4 | |
| `pmo.prioritization_budget_tiers_json` | Budget tier thresholds | 4 | Kept separate from weights — different validation |
| `pmo.mira_signal_thresholds_json` | AI signal thresholds | 4 | |
| `pmo.mira_topic_visibility_json` | Mira topic toggles | 5 | PMO Admin scope |
| `pmo.mira_config_json` | Mira mode + agent URL | 5 | System Admin scope; replaces `pmo.mira_mode` + `pmo.mira_agent_url` |
| `pmo.feature_flags_json` | Feature toggles | 5 | |
| `pmo.initiation_readiness_config_json` | Initiation readiness dimensions | 6 | |
| `pmo.notification_template.<key>` | Notification message templates | 6 | Per-template keys |

**No new Dataverse entities.** `pmo_adminchangelog` is cancelled — Gate 2 confirmed `pmo_telemetryevent` covers all admin audit requirements without schema changes. No new Dataverse tables for routing config, scoring, dashboard, or any other setting in this plan.

### 4.2 Runtime Configuration Loading

Introduce a `ConfigurationProvider` React context at the app root level (`App.tsx`, wrapping routes). This provider:
1. Calls `listSettings()` on mount (already available in `appSettings.api.ts`).
2. Resolves user admin role by querying the current user's Dataverse security role assignments (built-in System Administrator → `'system_admin'`; custom PMO Administrator → `'pmo_admin'`). Graph blocked by CSP — §2.5.
3. Makes all config values available via typed `useConfig()` hooks to any component.
4. Falls back gracefully to compile-time defaults if any setting is absent or unparseable.
5. Overrides `PMO_TEAM_FLAG` and `TENANT_ID` compile-time constants before any routing component renders.

This replaces the current pattern where individual hooks each fetch their own settings independently.

### 4.3 Files Requiring Targeted Refactoring

| File | Change Required | Phase |
|---|---|---|
| `app/src/App.tsx` | Wrap with `ConfigurationProvider`; gate `/admin/settings` route | 1 |
| `app/src/components/layout/Sidebar.tsx` | Read admin role from context; gate Administration section | 1 |
| `app/src/pages/Teams/TeamsPage.tsx` | Gate per-team template assignment affordance on `userAdminRole !== 'none'` | 1 |
| `app/src/pages/Dashboard/DashboardPage.tsx` | Read display config from `ConfigurationProvider` | 2 |
| `app/src/hooks/useIntakeTriage.ts` | Read similarity params from `ConfigurationProvider` | 2 |
| `app/src/hooks/useNotifications.ts` | Read `pollIntervalMs` from `ConfigurationProvider` | 2 |
| `app/src/components/layout/NotificationCenter.tsx` | Read category labels/colors from `ConfigurationProvider` | 2 |
| `app/src/lib/constants.ts` | Mark `PMO_TEAM_FLAG` and `TENANT_ID` as compile-time defaults, overrideable by `ConfigurationProvider` | 2 |
| `app/src/lib/intakeRoutingConfig.ts` | Replace static export with hook reading from `ConfigurationProvider`; keep static as fallback | 3 |
| `app/src/hooks/usePrioritizationScoring.ts` | Read weights and tiers from `ConfigurationProvider` | 4 |
| `app/src/ai/grounding/signals.ts` | Read signal thresholds from `ConfigurationProvider` | 4 |
| `app/src/components/mira/MiraPanel.tsx` | Read topic visibility and Mira config from `ConfigurationProvider`; eliminate `VITE_MIRA_AGENT_URL` | 5 |

### 4.4 Validation Architecture

The existing `intakeValidation.ts` pattern is the right model. Each new admin config domain should have a parallel `validate<Domain>Config(json)` function:
- Called client-side before saving (user gets immediate feedback).
- Called by `ConfigurationProvider` on load — malformed settings are rejected, defaults are used, and a diagnostic warning is logged.

Never let the app render with unparseable configuration. This is the contract for all configuration reads.

### 4.5 ConfigurationProvider Runtime Behavior Contract

The following runtime behavior is required. These are implementation rules, not suggestions.

**Initial load:**
- `ConfigurationProvider` fetches all `pmo_appsetting` records once on mount via `listSettings()`.
- The app must not render route components until this fetch completes. A loading state or spinner is acceptable during this window (consistent with the existing loading patterns in the app).
- Failed initial fetch (network error, Dataverse unavailable): log the error, proceed with all compile-time defaults, show a global diagnostic banner. The app must not crash or stall.

**Parsing:**
- Each known setting key is parsed individually. A parse failure on one key does not affect others.
- Parse failures: log a `console.warn` with the key and error, use the compile-time default for that key.
- Keys unknown to the provider (not in the defined registry) are silently ignored.

**Malformed config UX:**
- If the `ConfigurationProvider` is using a compile-time default because a Dataverse setting exists but failed parsing, the admin section for that setting shows an inline warning: **"The saved value for [Setting] is invalid. Default values are in use. Save this section to reset to defaults and fix."**
- This is visible only in the admin UI, not to end users.

**Post-save refresh:**
- After any admin save calls `upsertSetting()` successfully, the implementing component must call `queryClient.invalidateQueries(['pmoSettings'])` (or equivalent React Query invalidation) to trigger a refetch of the full settings slice.
- The updated value propagates to all `ConfigurationProvider` consumers within one React render cycle.
- **No page reload is required.** All config consumers read from context; context updates propagate normally.

**In-session consistency:**
- Config changes made in the admin area take effect immediately in the current session for the admin user (via React Query invalidation and context re-render).
- Other logged-in users will see the updated config on their next full app load. `ConfigurationProvider` fetches settings once on mount — there is no background settings poll. This is acceptable: configuration changes are infrequent, and the next load picks up the new state automatically. No broadcast or push mechanism is needed.

**Concurrency:**
- Last write wins. No optimistic locking. Given the low frequency of admin saves and the audit log providing recovery visibility, this is acceptable.
- If two System Admins simultaneously edit different settings, both writes succeed independently. If they edit the same setting, one will overwrite the other — the audit log records both changes.

### 4.6 Final Settings Contract

This section defines the authoritative TypeScript interface for each `pmo_appsetting` configuration key. Implementations must match these interfaces exactly. Validation functions must enforce the stated invariants. The `ConfigurationProvider` must use these interfaces for its typed context values.

```typescript
// ─── Phase 1 ───────────────────────────────────────────────────────────────
// Admin role resolution uses Dataverse security role queries — no pmo_appsetting key.
// Built-in 'System Administrator' role → 'system_admin'
// Custom 'PMO Administrator' role (solution component) → 'pmo_admin'
// No AdminAccessConfig interface. No pmo.admin_access_json key.

// ─── Phase 2 ───────────────────────────────────────────────────────────────

// pmo.dashboard_display_config_json
interface DashboardDisplayConfig {
  dueSoonDays: number;          // default: 30; valid: 1–365
  needsAttentionLimit: number;  // default: 6; valid: 1–50
  recentIntakeLimit: number;    // default: 7; valid: 1–50
  urgentDayThreshold: number;   // default: 0; days ≤ this → rose badge
  warningDayThreshold: number;  // default: 7; days ≤ this → amber badge
  // invariant: urgentDayThreshold < warningDayThreshold (warn if violated, do not block)
}

// pmo.intake_triage_similarity_config_json
interface IntakeTriageSimilarityConfig {
  lookbackDays: number; // default: 90; valid: 1–365
  minScore: number;     // default: 0.1; valid: 0.01–1.0
  topN: number;         // default: 3; valid: 1–10
}

// pmo.notification_display_config_json
// NOTE: pollIntervalMs is included here — there is no standalone pmo.notification_poll_interval_ms key
interface NotificationDisplayConfig {
  pollIntervalMs: number;                  // default: 60000; valid: 30000–300000 (30s–5m)
  categoryLabels: Record<string, string>;  // keyed by NOTIF_CATEGORY numeric value as string; optional per-category overrides
  categoryColors: Record<string, string>;  // keyed by NOTIF_CATEGORY numeric value as string; CSS color or Tailwind class
}

// pmo.sp_document_categories_json
type SpDocumentCategories = string[];
// default: SP_DOCUMENT_CATEGORIES from constants.ts
// invariant: each entry is a non-empty string; array is non-empty

// pmo.pmo_team_field — plain string, not JSON
// default: 'cr741_pmoteam'
// e.g., 'pmo_pmoteam' in UAT/PROD

// pmo.tenant_id — plain string, not JSON
// default: compile-time TENANT_ID constant
// Azure AD tenant GUID for Planner deep-link construction

// ─── Phase 3 ───────────────────────────────────────────────────────────────

// pmo.intake_routing_config_json
interface RoutingDomain {
  domainName: string;      // display name; non-empty
  teamId: string;          // Dataverse team GUID; must be non-empty
  keywords: string[];      // non-empty array of non-empty strings
  confidenceFloor: number; // integer 30–90 inclusive
}
type IntakeRoutingConfig = RoutingDomain[];
// default: INTAKE_ROUTING_CONFIG from intakeRoutingConfig.ts
// invariant: array non-empty; each domain has non-empty keywords; confidenceFloor in range

// ─── Phase 4 ───────────────────────────────────────────────────────────────

// pmo.prioritization_weights_json
interface PrioritizationWeights {
  strategicPriority: number; // default: 35
  complexity: number;        // default: 20
  health: number;            // default: 15
  budget: number;            // default: 15
  progress: number;          // default: 15
  // invariant: sum of all five values === 100
}

// pmo.prioritization_budget_tiers_json
interface BudgetTier {
  minAmount: number; // USD; non-negative integer
  score: number;     // 0–100
}
type PrioritizationBudgetTiers = BudgetTier[];
// default: [{minAmount:500000,score:100},{minAmount:100000,score:70},{minAmount:25000,score:40}]
// invariant: sorted descending by minAmount; no duplicate minAmount; scores 0–100

// pmo.mira_signal_thresholds_json
interface MiraSignalThresholds {
  riskCountWarn: number;      // default: 2; risks at or above → warn
  riskCountCritical: number;  // default: 4; risks above → critical; must be > riskCountWarn
  riskScoreWarn: number;      // default: 6; score at or above → outline badge
  riskScoreCritical: number;  // default: 10; score at or above → destructive badge; must be > riskScoreWarn
}

// ─── Phase 5 ───────────────────────────────────────────────────────────────

// pmo.mira_topic_visibility_json
type MiraTopicVisibility = Record<string, boolean>;
// Map of topicId → enabled; absent key defaults to true (visible)
// Only topicIds present in MIRA_TOPIC_REGISTRY are respected; others are ignored

// pmo.mira_config_json  (REPLACES separate pmo.mira_mode + pmo.mira_agent_url keys)
interface MiraConfig {
  mode: 'app' | 'copilot_studio'; // default: 'app'
  agentUrl?: string;               // required when mode = 'copilot_studio'; ignored otherwise
}

// pmo.feature_flags_json
interface FeatureFlag {
  enabled: boolean;
  // Scoped rollout: not supported in Phase 5 — enabled is global (on/off only)
  // Reason: AAD group scoping unavailable (CSP blocks Graph §2.5); per-user ID lists
  // are not an acceptable model. Add role-scoped flag support in a later phase if needed.
}
type FeatureFlagConfig = Record<string, FeatureFlag>;
// Keys are from FEATURE_FLAG_REGISTRY; unknown keys are ignored

// ─── Phase 6 ───────────────────────────────────────────────────────────────

// pmo.initiation_readiness_config_json
interface InitiationReadinessDimension {
  dimensionId: string; // must be in the closed code-defined set of 8 dimension IDs
  label: string;       // display name; max 50 chars
  required: boolean;
  weight: number;      // 0–100
  // invariant (across all required=true dimensions): weights sum to 100
}
type InitiationReadinessConfig = InitiationReadinessDimension[];

// pmo.notification_template.<templateKey>
// One pmo_appsetting record per template; templateKey values are a code-defined closed set
interface NotificationTemplate {
  title: string; // supports {{projectName}}, {{gateName}}, {{artifactType}} placeholders
  body: string;
}
```

### 4.7 No-Regression Constraint

The following existing admin capabilities are production-quality and must continue to function correctly after all Phase 1 and Phase 2 changes. Any change that touches the file paths below must explicitly verify that existing admin behavior is preserved:

| Existing capability | Key files | What must not break |
|---|---|---|
| App Settings (3 known keys) | `AdminSettingsPage.tsx`, `appSettings.api.ts`, `useAppSettings.ts` | Read, display, and save of the 3 existing settings |
| Intake Workflows | `IntakeWorkflowConfigSection`, `WorkflowForm`, `pmo_gatesettemplate` | Full CRUD, default flag, ConversionRuleMapper |
| Intake Stage Editor | `IntakeStageEditor.tsx` | Per-stage field config, artifact config, approval config, reorder |
| Project Templates | `TemplateManagementSection`, `pmo_projecttemplate` | Full CRUD, prefill from category default |
| Required Artifacts | `ArtifactDefinitionSection`, `pmo_requiredartifact` | Full CRUD, per-category, required/optional flag |
| TeamsPage template assignment | `TeamsPage.tsx`, `SETTING_TEAM_DEFAULT_TEMPLATE_PREFIX` | Template assignment still works for users with admin role after gating is applied |

**Regression testing requirement:** After Phase 1 and Phase 2 are implemented, manually verify each of the above capabilities against the existing behavior before releasing. Introduce role-gating changes to `TeamsPage.tsx` last to reduce the window of breakage risk.

---

## 5. UX / Navigation Plan

### 5.1 Admin Page Structure — Full-State Target

The following tab structure represents the complete admin surface after all planned phases. Phases 1–3 deliver the foundation and a subset of the Operations tab. Later phases fill in the remaining sections.

**Tab 1: Operations** (PMO Administrator scope)
- Dashboard Display Rules (Phase 2)
- Document Categories (Phase 2)
- Intake Triage Similarity (Phase 2)
- Notification Display Config — including poll interval (Phase 2)
- Intake Routing Rules (Phase 3)
- Prioritization Scoring (Phase 4)
- Initiation Readiness (Phase 6)
- Notification Templates (Phase 6)

**Tab 2: Workflows & Templates** (existing, preserved unchanged)
- Intake Workflows (existing — `IntakeWorkflowConfigSection`)
- Intake Stage Editor (existing — `IntakeStageEditor`)
- Project Templates (existing — `TemplateManagementSection`)
- Required Artifacts (existing — `ArtifactDefinitionSection`)

**Tab 3: AI & Mira** (PMO Administrator + System Administrator)
- AI Signal Thresholds (Phase 4 — PMO Admin)
- Mira Risk Score Bands (Phase 4 — PMO Admin)
- Quick Action Visibility (Phase 5 — PMO Admin)
- Mira Mode & Agent URL (Phase 5 — System Admin only, via `pmo.mira_config_json`)

**Tab 4: System** (System Administrator only — hidden from PMO Admin and non-admins)
- Environment Settings: PMO Team Flag, Tenant ID (Phase 2)
- Feature Toggles (Phase 5)
- Note: Admin role assignment is performed in Power Platform Admin Center, not in the app. No user list UI is required.

### 5.2 Admin Gating Rules

The following rules apply across the entire application, not just within the admin page:

- **Sidebar Administration section:** hidden for `userAdminRole = 'none'`
- **Route `/admin/settings`:** redirects to `/dashboard` for `userAdminRole = 'none'`
- **System tab:** rendered only for `userAdminRole = 'system_admin'`
- **TeamsPage per-team template assignment:** hidden for `userAdminRole = 'none'`; requires at minimum PMO Admin role
- **Any new admin affordance added outside `/admin/settings`:** must use `useRequireAdminRole()` before rendering — this is an implementation invariant, not a suggestion
- **Destructive actions (delete workflow, remove template):** use existing `ConfirmDialog` with impact count statement

### 5.3 Change History Page (`/admin/change-history`)

A filtered log view: date range picker, domain filter, changed-by filter. Rows expand to show human-readable before/after property diff. Backed by `pmo_telemetryevent` filtered to `pmo_eventtype eq 'AdminChange'`. Added as part of Phase 1.

---

## 6. Delivery Plan

The delivery plan has three structural tiers: mandatory foundation, minimum viable admin expansion, and optional later waves. The foundation is non-negotiable. Later waves are demand-driven.

---

### Mandatory Foundation — Phase 1

> **This phase must ship before any new high-impact admin surfaces are added.** Role gating, config centralization, and audit infrastructure are prerequisites — not optional enhancements. Any admin capability that ships before Phase 1 is complete ships to an uncontrolled surface.

**Objective:** Establish runtime configuration infrastructure, full-app role gating, audit trail, and validation pattern. Both pre-implementation gates are complete — implementation can begin immediately.

**Pre-implementation gates — BOTH COMPLETE (2026-04-23):**
1. ~~**Graph validation** (§2.5)~~ — **COMPLETE. BLOCKED.** Power Apps host CSP (`connect-src 'none'`) blocks all direct Graph calls. Role resolution uses Dataverse security role queries exclusively — no user ID lists. `AdminGroupConfig`, `pmo.admin_group_ids_json`, and `pmo.admin_access_json` cancelled.
2. ~~**Audit proof-before-entity** (§3.13)~~ — **COMPLETE. EXTEND.** `pmo_telemetryevent` supports admin audit without new columns or new entity. `pmo_adminchangelog` cancelled. Admin writes use `pmo_eventtype = 'AdminChange'` with existing `pmo_payload`, `pmo_source`, `pmo_severity` fields.

**Included capabilities:**
- `ConfigurationProvider` context at app root
- `useCurrentUserRole()` hook (Dataverse security role query — Graph blocked, §2.5)
- `useRequireAdminRole()` utility hook
- Custom **PMO Administrator** security role defined as a solution component
- Sidebar role gating for the Administration section
- Route guard for `/admin/settings`
- TeamsPage per-team template affordance gating
- `useAdminAudit()` hook writing to `pmo_telemetryevent` (no new entity — Gate 2 confirmed)
- `/admin/change-history` page
- `validate<Domain>Config()` utility pattern established

**Technical work:**
- New file: `scripts/seed-env-settings.js` — **must be created and available before Phase 1 validation.** Seeds environment-specific app settings (`pmo.pmo_team_field`, `pmo.tenant_id`) into Dataverse. Admin role access for testing is granted by assigning the System Administrator or PMO Administrator Dataverse security role in Power Platform Admin Center — not by this script. Full spec in Phase 2 (§6 Minimum Viable Admin Expansion).
- New file: `app/src/providers/ConfigurationProvider.tsx`
- New file: `app/src/hooks/useCurrentUserRole.ts`
- New file: `app/src/hooks/useRequireAdminRole.ts`
- New file: `app/src/hooks/useAdminAudit.ts`
- Modify: `app/src/App.tsx` — wrap with `ConfigurationProvider`, add route guard
- Modify: `app/src/components/layout/Sidebar.tsx` — consume admin role context
- Modify: `app/src/pages/Teams/TeamsPage.tsx` — gate per-team template assignment
- No solution schema change required — admin audit uses existing `pmo_telemetryevent` fields (Gate 2 confirmed)

**Dependencies:** None — self-contained. Both pre-implementation gates are complete.

**Risks:**
- ~~Graph `/me/memberOf` availability~~ — **Resolved (§2.5). Blocked by CSP. Dataverse security role query is the confirmed mechanism.**
- The Phase 1 developer must have either the built-in System Administrator role or the custom PMO Administrator role assigned in the DEV environment before Phase 1 testing can be performed. Assign via Power Platform Admin Center — no app-level setup needed.

**Regression check:** After Phase 1, all five existing admin surfaces (§4.7) must still function correctly.

**Validation:**
- Non-admin user cannot see Administration sidebar or reach `/admin/settings`.
- PMO Admin sees Operations and Workflows tabs but not System tab.
- System Admin sees all tabs.
- A user with neither System Administrator nor PMO Administrator role sees no Administration section — not an error state.
- TeamsPage template assignment is hidden for non-admin users.
- All existing admin surfaces (workflows, templates, artifacts, app settings) continue to work.

---

### Minimum Viable Admin Expansion — Phase 2 (Quick Wins) + Phase 3 (Intake Routing)

> Phases 2 and 3 together are the near-term admin expansion target. Phase 2 pays for the Phase 1 investment with immediate visible value. Phase 3 closes the highest-impact operational gap. After Phase 3, the admin area is operationally complete for routine PMO operations.

#### Phase 2: Quick Wins

**Objective:** Move pure-data, low-risk operational settings into the admin area. Eliminate the most common categories of developer tickets for minor configuration adjustments.

**Included capabilities:**
- Dashboard Display Rules (§3.3)
- SharePoint Document Categories (§3.8)
- Intake Triage Similarity Parameters (§3.4)
- Notification Display Configuration including poll interval (§3.7 — Phase 2 portion only)
- Environment Constants: PMO Team Flag and Tenant ID (§3.10 — System Admin section)

**Technical work:**
- Add settings keys to `constants.ts` per §4.6 interfaces
- Add accordion sections to `AdminSettingsPage` Operations tab and System tab
- Modify `DashboardPage.tsx`, `useIntakeTriage.ts`, `useNotifications.ts`, `NotificationCenter.tsx` to read from `ConfigurationProvider`
- Wire `ConfigurationProvider` to override `PMO_TEAM_FLAG` and `TENANT_ID` from app settings at startup
- Audit calls wired into every section save handler via `useAdminAudit()`

**Environment seeding deployment path:**
The `pmo.pmo_team_field` and `pmo.tenant_id` settings must be populated per-environment at deployment time, not manually entered after deployment. The implementation must include:

- `scripts/seed-env-settings.js` — a Node.js script that upserts the initial `pmo_appsetting` records for a target environment using the Dataverse Web API (authenticated via service principal or user credentials). Required arguments:
  ```
  node scripts/seed-env-settings.js \
    --environment <environment-url> \
    --tenantId <azure-ad-tenant-guid> \
    --pmoTeamField <field-logical-name>
  ```
- The script is idempotent — safe to re-run if values need updating.
- The script is run as a post-import step in the deployment pipeline, not as a manual step.
- The deployment runbook for UAT and PROD promotion must be updated to include this step.
- No bootstrap env var is required — environment admins have the built-in System Administrator role and can access the app's admin area immediately after solution import.

**Dependencies:** Phase 1 `ConfigurationProvider` and `useAdminAudit()`.

**Risks:** All changes are additive with compile-time defaults as fallback. Minimal risk.

**Regression check:** All five existing admin surfaces (§4.7) must still function correctly.

**Validation:** Change a dashboard setting, verify dashboard reflects it without page reload. Revert, verify default applies. Verify change appears in Change History. Set PMO Team Flag to a test value, verify Teams page reflects it.

---

#### Phase 3: Intake Routing Configuration

**Objective:** Move the highest-impact operational configuration — intake routing rules — into the admin area.

**Included capabilities:**
- Intake Routing Rules editor (§3.1) — keyword lists, confidence floors, domain-to-team mapping
- "Test Route" simulation affordance

**Technical work:**
- Replace `app/src/lib/intakeRoutingConfig.ts` static export with a hook reading from `ConfigurationProvider`; keep static as validated fallback
- New admin section: `IntakeRoutingConfigSection` component in Operations tab
- Tag input for keyword lists (shadcn `Badge` + input pattern)
- Confidence floor slider (shadcn `Slider` — already in `ui/`)
- Team picker reuse from `WorkflowForm`
- "Test Route" live simulation panel running `useIntakeTriage` logic against current config without saving

**Dependencies:** Phase 1.

**Risks:** This is the highest-impact admin change. Malformed routing config could misroute all intake. The hardcoded fallback is non-negotiable. Add "Last validated: [timestamp]" display in the routing section.

**Validation:** Create a routing domain with known keywords. Submit a test intake request. Verify it routes correctly. Change confidence floor to 100. Verify domain no longer matches. Revert. Verify audit log records all changes with before/after values.

---

### Optional / Later Waves — Phases 4–6

> These phases are demand-driven. They are not automatically sequenced after Phase 3. After Phases 1–3, the admin area is operationally sufficient for routine PMO operations. Later waves should be triggered by actual friction, not by the existence of this plan.

#### Phase 4: Analytics and Scoring Configuration

**Objective:** Make strategic scoring parameters and AI signal calibration admin-configurable.

**Capabilities:** Prioritization weights (§3.2), budget tier thresholds (§3.2), AI signal thresholds (§3.6), Mira risk score bands (§3.6).

**Technical work:**
- Modify `usePrioritizationScoring.ts` to read from `ConfigurationProvider`
- Modify `signals.ts` to read from `ConfigurationProvider`
- Modify `MiraPanel.tsx` line 570 to read thresholds from `ConfigurationProvider`
- New admin sections: `ScoringConfigSection` in Operations tab; AI Signal Thresholds in AI & Mira tab

**Risks:** Weight validation (must sum to 100) enforced client-side. Budget tiers must be sorted descending and non-overlapping. Live preview of re-ranking before save is strongly recommended.

---

#### Phase 5: Mira Configuration and Feature Toggles

**Capabilities:** Mira quick action visibility (§3.5), Mira mode and URL (§3.5), feature toggles (§3.11).

**Technical work:**
- Define `MIRA_TOPIC_REGISTRY` constant in `constants.ts`
- Modify `MiraPanel.tsx` topic rendering to filter against `pmo.mira_topic_visibility_json`
- Move Mira mode/URL from `VITE_MIRA_AGENT_URL` env var to `pmo.mira_config_json` app setting
- Define `FEATURE_FLAG_REGISTRY` constant
- New file: `app/src/hooks/useFeatureFlag.ts`
- New admin sections in AI & Mira tab and System tab

**Risks:** Toggling off all Mira topics must render a "No actions available" state — not a blank panel. Feature flags are additive only.

---

#### Phase 6: Initiation Readiness and Notification Templates

**Capabilities:** Initiation readiness dimension config (§3.9), notification message templates (§3.7).

**Technical work:**
- Refactor `InitiationWorkspace.tsx` to read dimension config from `ConfigurationProvider`
- Close `GovernWorkspace.tsx` stub (`const initiationComplete = false`)
- New admin sections in Operations tab
- `notificationTemplate` substitution utility in `utils.ts`
- Wire templates into `useCreateNotification` callsites

**Risks:** `InitiationWorkspace.tsx` refactoring is the most invasive code change in this plan. All 8 readiness dimensions require regression testing.

---

## 7. Quick Wins

Quick wins are admin-configurable settings that are currently hardcoded for no principled reason. They involve no behavioral logic, no governance implications, and no meaningful risk. All are deliverable in Phase 2 after the Phase 1 foundation is in place.

### Quick Wins (Phase 2)

1. **SharePoint Document Categories** — One setting key, one array input in admin page, one line change in the constant consumer. Eliminates the most trivial dev-ticket category.

2. **Dashboard Display Rules** — Three values in one JSON setting, three inputs in admin page, three component reads replaced. Covers the 30-day window and top-N limits that have no reason to be compile-time constants.

3. **Intake Triage Similarity Parameters** — Three values already isolated in `useIntakeTriage.ts`. One admin section, three inputs.

4. **Notification Display Config (including poll interval)** — One JSON setting covering poll interval and category label/color overrides. Operational tuning that currently requires a redeploy.

5. **PMO Team Flag and Tenant ID** — Two environment-specific values that require a code edit at every environment promotion. Moving these to `pmo_appsetting` with deployment-script seeding eliminates the most dangerous deployment-time footgun in the codebase.

### Strategic Governance Controls (Phase 3+)

6. **Intake Routing Configuration (Phase 3)** — The highest-value single item in this plan. Routing errors affect every intake request while misconfigured. Requires "Test Route" simulation before save.

7. **Prioritization Scoring Weights (Phase 4)** — Strategic calibration. Requires live re-ranking preview before save.

8. **AI Signal Thresholds (Phase 4)** — Portfolio-norm calibration. Requires critical > warn validation.

9. **Mira Topic Visibility (Phase 5)** — Value increases as the topic catalog grows.

10. **Feature Toggles (Phase 5)** — Infrastructure investment proportional to the pace of new capability development.

---

## 8. Guardrails

### What Remains Code-Owned

The following areas must not become admin-configurable. They represent platform-critical mechanics, schema-level contracts, protected workflow logic, or security enforcement.

| Area | Why Code-Owned |
|---|---|
| Dataverse entity schemas, field names, and option-set numeric values | Schema changes require solution deployments; admin UI cannot safely create or destroy schema |
| PSS scheduling API calls and task operation mechanics | Scheduling service behavior is governed by the P4W platform; misconfiguration breaks task management for all projects |
| Approval state machine logic (approve / reject / defer transitions, `pmo_approvalchain` JSON structure) | Approval workflows have compliance implications; state transitions are audited via solution change management, not runtime config |
| Security roles and Dataverse row-level security | Must be managed in Power Platform Admin Center; the app's role gating is a display gate only, not an enforcement mechanism |
| AI topic function logic and prompt implementations (`ai/topics/`) | The computations in `ai/topics/` are code; admin-configurable prompts would require a template engine introducing correctness and security risks disproportionate to the benefit |
| `intakeValidation.ts` allowlists | The set of fields permitted in conversion rules is a code-enforced safety boundary; expanding it requires developer review of Dataverse schema |
| `intakeConversion.ts` field mapping logic | Transformation functions are code; the mapping *selection* (already configurable via WorkflowForm) is distinct from transformation logic |
| Auth/identity resolution | `getCurrentUserId()` and Graph auth are platform-determined; the app does not configure these |
| Platform integration mechanics (SP document upload custom action, P4W API call shapes) | These are contracts with external systems; their shape is determined by the platform |

The admin area controls **runtime-safe operational configuration** — parameters, reference data, display rules, and soft behavioral preferences. It does not control core platform behavior and must never be used to work around schema or security model constraints.

### Safety Controls

1. **Validation before save:** Every admin section validates against the §4.6 interfaces before persisting. Invalid config is rejected with a specific error message — never silently saved.

2. **Fallback to compile-time defaults:** Every `ConfigurationProvider` read path has a typed default. A missing or unparseable setting never crashes the app — log, warn, and default.

3. **Malformed config UX:** Admin sections show an inline "saved value is invalid, defaults in use" warning when `ConfigurationProvider` is operating on a fallback for that key (§4.5).

4. **Audit log on every save:** `useAdminAudit()` is called in every admin section save handler. Built into the shared save pattern from Phase 1 — not added per-section later.

5. **Test/simulation affordances:** Intake routing and prioritization scoring must offer simulation before save. Other settings are low-risk enough not to require it.

6. **System Admin segregation:** Environment-level settings (team flag, tenant ID, feature flags, Mira mode/URL) are visible only to `userAdminRole = 'system_admin'`. PMO Administrators cannot see or reach these settings.

7. **No admin-bypasses of Dataverse security:** The app's admin surface writes through the same Dataverse client as all other operations. Dataverse security is the enforcement layer.

8. **Role resolution failure is always deny:** If the Dataverse security role query fails at startup (network error, timeout), `userAdminRole` defaults to `'none'`. Access is never elevated on query failure.

---

## 9. Final Recommendation

### Is the Codebase Well-Positioned?

Yes. The team has already built meaningful infrastructure that makes this expansion an extension exercise:

- `pmo_appsetting` as a runtime config store with clean CRUD hooks
- A real admin page at `/admin/settings` with production-quality workflow and template editors
- Well-isolated constants in `constants.ts` that are straightforward to make overrideable
- A clean validation pattern in `intakeValidation.ts` that serves as the model for all new config domains
- `pmo_notification` and `pmo_telemetryevent` entities ready for extension
- Dataverse SDK (`@microsoft/power-apps/data`) confirmed available and CSP-exempt — all data access routes through it

The codebase does not need a foundational rewrite. The specific work required is:
1. A `ConfigurationProvider` to centralize config resolution at app startup.
2. Targeted refactoring of 8–10 components to consume config from `ConfigurationProvider`.
3. Admin audit via `pmo_telemetryevent` extension (no schema change — Gate 2 confirmed).
4. Role gating across the full app surface before admin capabilities expand.
5. An environment seed script to eliminate deployment-time code changes.
6. A first meaningful new admin capability (intake routing) that closes the highest-impact operational gap.

### Recommended Path

**Foundation first — non-negotiable.** Both pre-implementation gates are complete (§2.5, §3.13). Phase 1 implementation can begin immediately. Phase 1 delivers role gating, `ConfigurationProvider`, and the audit infrastructure. Nothing else ships before Phase 1 is complete.

**Quick wins immediately after foundation.** Phase 2 delivers visible value with minimal risk. The environment seeding script is part of Phase 2 — it eliminates the deployment footgun alongside the admin settings that expose those values.

**Intake routing is the highest-value single capability.** Phase 3 closes the gap that generates the most developer requests. After Phase 3, the PMO team can manage the most common intake operations without developer involvement.

**Later waves are demand-driven.** Phases 4–6 contain real value but are not required for an operationally useful admin experience. Prioritize based on what is generating actual friction. Do not bundle them into one program.

**Estimated implementation effort:**
- Phase 1: ~1–2 sprint-weeks
- Phase 2: ~1 sprint-week
- Phase 3: ~1–2 sprint-weeks (Test Route simulation adds time)
- **Phases 1–3 total: ~3–5 sprint-weeks for a complete, safe, operationally useful admin experience**
- Phases 4–6: ~3–4 additional sprint-weeks if all pursued; each phase is independent
