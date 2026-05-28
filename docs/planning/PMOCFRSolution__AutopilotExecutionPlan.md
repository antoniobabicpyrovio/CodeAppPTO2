### Project: PMO CFR Solution
PlanType: AutopilotExecutionPlan
Status: Active
Authority: This document
Standards: corp-fin-bi-standards (multi-root workspace, always open)
Publisher: Business Intelligence / prefix `pmo_` (approved PMO boundary exception)
Created: 2026-04-21

---

## PMO CFR Solution — Autopilot Execution Plan

Single execution authority for all remaining PMO CFR Solution work. Supersedes all prior planning artifacts.

### Scope & Objectives

The CFR Project Management application is the unified PMO surface for Coram Finance RevCycle. It consolidates:

- Guided project and program onboarding with template-driven initialization
- Project request intake with AI-assisted triage routing
- Project and program lifecycle management with shared multi-team execution
- Full in-app task management with Planner parity
- AI-powered contextual advisory through Mira
- Portfolio health analytics and PMO administration

### Locked Decisions

#### Automation Model
- All work is agent-executable unless a real platform limitation exists
- No human-dependency language, approval checkpoints, or "confirm/evaluate later" phrasing
- All tenant, admin, and deployment access needed for approved work is available
- Planning and coding agents proceed using the defaults in this document

#### Product Control Model
- The PMO app remains the primary command-center experience
- New capabilities deepen the in-app experience rather than shift users out of the app
- Existing tables are extended first; add new tables only where the lifecycle object is materially distinct
- Projects are collaborative by design — the multi-team model (`pmo_projectteam` junction with Primary/Contributing roles) is the default execution pattern, not an exception

#### Project Template Hierarchy
- Templates define the initial execution structure for a project: metadata defaults, WBS tasks, bucket structure
- Precedence rule (highest to lowest):
  1. **User-selected template** during onboarding
  2. **Team default template** from the project's Primary Team record
  3. **System default template** from `pmo_appsettings`
- Template application creates WBS tasks via `applyProjectTemplate()` in `schedulingClient.ts`
- Every project gets a template applied — if the user skips selection and no team/system default exists, the category-based template from `projectTemplates.ts` is used as the final fallback

#### Teams Strategy
Selected: **Teams Option B — Meeting Integration**
- Project-linked meeting preparation, in-meeting contextual side panel, meeting-linked action capture, meeting summary integration

#### Document Management Strategy
Selected: **Document Management Option C — SharePoint Document Service Abstraction**
- SharePoint as storage substrate, PMO-controlled metadata, project/program document hubs, required artifact tracking

#### Notification Strategy
Selected: **Hybrid notification model**
- Unified ephemeral toast notifications for immediate feedback
- Durable in-app notification center for actionable PM signals

### Agent Execution Rules

Mandatory for any agent working this repo:

1. Do not ask for clarification where this plan has already made a decision
2. Do not add "human required" language unless there is a real technical platform blocker
3. Do not leave narrative TODOs in place of implementation decisions
4. Every feature must include: objective, scope, schema impact, file paths, dependencies, acceptance criteria, automated validation
5. Reuse existing schema and components first
6. If a new table is required, it must represent a distinct lifecycle object with documented purpose, ownership, and column structure
7. All Dataverse schema creation follows `dataverse-agent-behavior-standard.md` automation decision table — do not gate automatable operations
8. All new tables use `pmo_` prefix within this solution boundary
9. All code changes follow the mandatory validation sequence: `npx tsc -b --noEmit` → `npm run build` → `npx power-apps push`
10. Multi-team execution is the default — never design features that assume single-team project ownership

### Validated Current State

All items below are complete and deployed.

#### Phase 0 — PSS API Validation ✅
PSS OperationSet pattern validated. Persistence lag calibrated at ~20–22s. PSS wrappers in `app/src/lib/schedulingClient.ts`.

#### Phase 1 — Project Task Workspace ✅
Kanban board, WBS hierarchy, bucket/task CRUD, optimistic UI, async save pattern.

#### Phase 2 — Program Oversight, WBS Templates, Dependencies ✅
Program oversight signals, WBS task template definitions in `app/src/lib/projectTemplates.ts`, F2S dependency management.

#### Phase 3 — Resource Assignment & Advanced Scheduling ✅
Team member lifecycle, resource assignment, per-task assignment management.

#### Planner Task Parity Sprint ✅
Detail panel, search, filter bar, group-by, list view, charts, people/workload view. Description, priority, progress, effort, labels, checklist, sprint assignment.

#### Mira AI Assistant (Waves 0–3) ✅
Advisory and draft engine, Copilot Studio deployment, context loaders, contracts, panel, mutation framework, telemetry event sink.

#### Intake & Demand Management ✅
Conversational intake (2-step), routing and confidence scoring, intake list/detail/triage, intake-to-project conversion via server-side flow (`pmo_CFR_IntakeToProject`), submission notification.

#### Project & Program Management ✅
Project and program detail pages, status reporting, risk/issue/change tracking (Accelerator entities), project team management (`pmo_projectteam` junction with Primary/Contributing roles), server-side user search with AAD group scoping, actionable alerts and governance shortcuts.

#### Analytics & Administration ✅
Portfolio health, intake pipeline, by-team, schedule, routing QA analytics. Admin settings with `pmo_appsettings` key-value store.

#### Multi-Team Project Model ✅
`pmo_projectteam` junction table links `msdyn_project` ↔ `team` with `TEAM_ROLE.Primary` (893460040) and `TEAM_ROLE.Contributing` (893460041). API: `app/src/api/projectTeams.api.ts`. Hook: `app/src/hooks/useProjectTeams.ts`. Primary team set via `pmo_PrimaryTeam@odata.bind` on project record. Contributing teams managed via junction CRUD on ProjectDetailPage TEAMS section.

### Resolved Open Items

#### Mira real Dataverse writes
Use `pmo_projectrequest` as the storage target. Add explicit request type classification for bug reports and enhancement suggestions.

#### Telemetry durable sink
Implement `pmo_telemetryevent` table. Do not overload notes or request records with telemetry payloads.

#### Approval workflow
Required. Implemented as part of the stage-gate model. No "evaluate whether needed" language.

---

## Remaining Work

---

## Tier 0 — Foundational Delivery Infrastructure

### FEAT-AUTO-001 — Plan Normalization ✅
**Objective:** Remove ambiguous execution language from planning artifacts.

**Scope:**
- Replace vague "confirm/evaluate/determine later" language in all active planning docs
- Normalize all open items to explicit implementation decisions

**File paths:**
- `docs/planning/*.md` — scan and revise

**Schema impact:** None

**Dependencies:** None

**Acceptance criteria:**
- No active work item contains ambiguity language (evaluate, determine later, confirm whether, consider if)
- All active work is directly implementable

**Automated validation:**
- `grep -ri "evaluate\|determine later\|confirm whether\|consider if" docs/planning/*.md` returns zero matches

---

### FEAT-AUTO-002 — CI/CD and Validation Pipeline ⏸️ DEFERRED
**Status:** Deferred — requires GitHub Enterprise Actions runner infrastructure outside coding agent boundary.
**Registry:** `docs/planning/deferred-feature-registry.json` → `ci-cd-validation-pipeline` (dfr-017)
**Interim gate:** Manual validation sequence (`npx tsc -b --noEmit` → `npm run build` → `npx power-apps push`) enforced by agent execution rules.

---

### FEAT-AUTO-003 — Schema / Environment Snapshot ✅
**Objective:** Maintain repo-local reference artifacts for critical schema and environment assumptions.

**Scope:**
- Snapshot critical tables, fields, and environment-specific mappings used by the app
- Include `PMO_TEAM_FLAG` column name mapping (`cr741_pmoteam` in DEV → `pmo_pmoteam` in UAT/PROD)

**File paths:**
- `docs/schema-snapshot.md` — new

**Schema impact:** None to runtime

**Dependencies:** None

**Acceptance criteria:**
- Snapshot artifact exists with all entity sets from `constants.ts`, their key fields, and environment-specific mappings

**Automated validation:**
- CI verifies file exists and is valid markdown

---

### FEAT-TMPL-001 — Project Template Model ✅
**Objective:** Create a Dataverse-backed project template model that supports selection during onboarding and hierarchical defaulting.

**Scope:**
- New `pmo_projecttemplate` table storing template metadata and WBS task definitions
- Template contains: name, description, target CFR category, task payload, active/inactive state
- WBS tasks stored as structured JSON in a memo column on the template record (same `TemplateTask[]` format used by `applyProjectTemplate()`)
- Admin UI for template CRUD on the Admin Settings page
- Migrate existing code-defined templates from `projectTemplates.ts` into seed records

**File paths:**
- `app/src/models/projectTemplate.model.ts` — new model interface
- `app/src/api/projectTemplates.api.ts` — new API (list, get, create, update, deactivate)
- `app/src/hooks/useProjectTemplates.ts` — new query + mutation hooks
- `app/src/pages/Admin/AdminSettingsPage.tsx` — add template management section
- `app/src/lib/projectTemplates.ts` — retain as fallback seed data; add export function to convert to template records
- `app/src/lib/constants.ts` — add `ENTITY_SETS.projectTemplate: 'pmo_projecttemplates'`

**Schema impact:**
New table: `pmo_projecttemplate`

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| `pmo_projecttemplateid` | PK (GUID) | Yes | Auto |
| `pmo_name` | String(200) | Yes | Template display name |
| `pmo_description` | Memo | No | Template description |
| `pmo_cfrcategory` | Choice | No | Maps to `CFR_CATEGORY` option set; null = any category |
| `pmo_taskpayload` | Memo | Yes | JSON array of `TemplateTask` objects |
| `pmo_issystemdefault` | Boolean | No | At most one record may be `true` |
| `statecode` | State | Yes | 0=Active, 1=Inactive |

Web API creation payload:
```json
{
  "@odata.type": "Microsoft.Dynamics.CRM.pmo_projecttemplate",
  "SchemaName": "pmo_ProjectTemplate",
  "DisplayName": { "LocalizedLabels": [{ "Label": "Project Template", "LanguageCode": 1033 }] },
  "DisplayCollectionName": { "LocalizedLabels": [{ "Label": "Project Templates", "LanguageCode": 1033 }] },
  "HasNotes": false,
  "HasActivities": false,
  "OwnershipType": "OrganizationOwned"
}
```
After creation: `POST PublishAllXml` → add to `CFRProjectManagement` unmanaged solution.

**Dependencies:** None

**Acceptance criteria:**
- `pmo_projecttemplate` table exists in DEV with all columns
- Admin Settings page shows template list with create/edit/deactivate actions
- Existing 6 category templates from `projectTemplates.ts` are seeded as records
- Exactly one template can be marked as system default at a time (toggling one off when another is set)
- `pmo_taskpayload` is valid JSON parseable as `TemplateTask[]`

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Template CRUD operations work in browser
- `applyProjectTemplate(projectId, JSON.parse(template.pmo_taskpayload))` creates tasks successfully

---

### FEAT-TMPL-002 — Team Default Template ✅
**Objective:** Allow each PMO team to have a default project template that auto-applies when the team is the Primary Team.

**Scope:**
- Store team-specific default template in `pmo_appsettings` using namespaced key pattern `pmo.team_default_template.{teamId}` with the template GUID as the value
- Display and edit team default template on the Teams admin page via `SearchableSelect` populated from active `pmo_projecttemplate` records
- Read/write uses existing `useAppSettings` / `useUpsertSetting` hooks — no new Dataverse schema required
- Onboarding wizard reads the setting for the selected Primary Team to resolve the team default template

**File paths:**
- `app/src/pages/Teams/TeamsPage.tsx` — add "Default Template" column with inline edit via `SearchableSelect`
- `app/src/lib/constants.ts` — add `SETTING_TEAM_DEFAULT_TEMPLATE_PREFIX = 'pmo.team_default_template.'`
- `app/src/hooks/useAppSettings.ts` — reuse existing; no changes needed

**Schema impact:** None — uses existing `pmo_appsettings` key-value table. No modification to the system `team` entity.

**Design rationale:** The `team` entity is a Dataverse system table. Adding a lookup column requires solution XML changes, `PublishAllXml`, and carries ALM risk across environments. Using `pmo_appsettings` with namespaced keys keeps everything within the custom solution boundary. The PMO team count is small (under 20), and the app already loads all settings into memory, so the lack of Dataverse-enforced FK and single-query reverse lookup is not a practical concern.

**Dependencies:**
- FEAT-TMPL-001

**Acceptance criteria:**
- Teams page shows "Default Template" column per team
- Team default template is editable via SearchableSelect with active template options
- Setting persists as `pmo.team_default_template.{teamId}` in `pmo_appsettings`
- Setting is clearable (save with empty value removes the team default)
- When a project's Primary Team has a default template setting and no user-selected template is provided, the team default is used during onboarding

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Set team default → create project with that Primary Team → verify template auto-applied
- Clear team default → create project → verify falls through to system default

---

### FEAT-TMPL-003 — System Default Template Setting ✅
**Objective:** Allow administrators to set a system-wide default project template via admin settings.

**Scope:**
- Add `pmo.default_project_template_id` key to `pmo_appsettings`
- Add template selector row to Admin Settings page using `SearchableSelect` with template options
- Onboarding wizard reads this value as final fallback when no user selection and no team default exist

**File paths:**
- `app/src/pages/Admin/AdminSettingsPage.tsx` — add new `KNOWN_SETTINGS` entry with `type: 'template-lookup'`
- `app/src/lib/constants.ts` — add `SETTING_DEFAULT_PROJECT_TEMPLATE = 'pmo.default_project_template_id'`

**Schema impact:** None (uses existing `pmo_appsettings` key-value table)

**Dependencies:**
- FEAT-TMPL-001

**Acceptance criteria:**
- Admin Settings page shows "Default Project Template" setting with template dropdown
- Setting stores template GUID as the value
- Setting is clearable (save with empty value)

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Set and clear the setting in browser

---

### FEAT-ONBOARD-001 — Guided Project Onboarding Wizard ✅
**Objective:** Add a step-driven onboarding experience for manual project creation that ensures consistent setup of metadata, ownership, team participation, governance, template application, and initial execution structure.

**Scope:**
A multi-step wizard dialog accessible from `ProjectListPage`. The wizard creates a project via PSS, sets all governance fields via OData PATCH, establishes team participation via `pmo_projectteam` junction, selects and applies a template, and navigates to the new project detail page.

Steps:
1. **Basics** — Project name (required), description, scheduled start date, CFR category, line of business
2. **Ownership** — Project Manager (server-side SearchableSelect), Executive Sponsor, Primary Team (SearchableSelect with PMO teams)
3. **Template** — Select from active `pmo_projecttemplate` records. Pre-populated with resolved default using precedence: team default (from step 2's Primary Team) → system default → category fallback. User can override or accept default. Shows template description and task count preview.
4. **Team & Collaboration** — Manager (restricted to Primary Team membership via `teammembership_association/any()` pattern), Contributing Teams (multi-add from PMO teams). Initializes shared execution: contributing teams get junction records with `TEAM_ROLE.Contributing`.
5. **Classification & Governance** — Complexity, strategic priority, overall health defaults. Budget/forecast/benefits fields (optional).
6. **Review & Create** — Summary of all selections. Single "Create Project" action.

Create sequence (all automated, no human gates):
1. Create `msdyn_project` via `schedulingClient.ts` `createProjectTask` pattern — use `msdyn_PssCreateV1` action on `msdyn_project` entity with required fields (`msdyn_subject`, `msdyn_scheduledstart`, `msdyn_calendarid` from organization)
2. PATCH governance/classification fields onto the new project via `dv.update()` with PascalCase `@odata.bind` syntax for lookups
3. Create `pmo_projectteam` junction records for Primary Team (role=Primary) and each Contributing Team (role=Contributing) via `projectTeams.api.ts`
4. Parse selected template's `pmo_taskpayload` and call `applyProjectTemplate(newProjectId, tasks)` — waits `SCHEDULING_PERSIST_DELAY_MS` before proceeding
5. Navigate to `/projects/{newProjectId}`

**File paths:**
- `app/src/pages/Projects/ProjectListPage.tsx` — add "New Project" button triggering wizard dialog
- `app/src/pages/Projects/ProjectOnboardingWizard.tsx` — new component (multi-step dialog)
- `app/src/api/projects.api.ts` — add `createProject()` function
- `app/src/hooks/useProjects.ts` — add `useCreateProject()` mutation hook
- `app/src/lib/schedulingClient.ts` — add `createProjectViaScheduling()` if PSS is required for project creation, or use direct OData `dv.create()` if the P4W plugin allows it (test: if direct `POST msdyn_projects` succeeds without `PreValidate` rejection, use direct; otherwise use PSS `msdyn_PssCreateV1`)
- `app/src/hooks/useProjectTemplates.ts` — reuse for template loading
- `app/src/components/common/SearchableSelect.tsx` — reuse for all user/team/template selects

**Schema impact:** None — uses existing `msdyn_project`, `pmo_projectteam`, `pmo_projecttemplate` tables

**Dependencies:**
- FEAT-TMPL-001 (template model must exist for step 3)
- FEAT-TMPL-002 (team default template lookup for auto-population)
- FEAT-TMPL-003 (system default template for fallback)

**Acceptance criteria:**
- "New Project" button on ProjectListPage opens the wizard
- All 6 steps render with appropriate controls
- Template step pre-populates using precedence: user-selected > team default > system default > category fallback
- Create action produces a valid `msdyn_project` record with all governance fields set
- Primary and Contributing team junction records are created
- Template WBS tasks are auto-created via PSS
- User lands on the new project's detail page after creation
- Multi-team initialization is correct — contributing teams have junction records from creation, not added later
- All user dropdowns use server-side search with AAD group scoping and noise filter

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Create a project via the wizard → verify in Dataverse: project record exists, team junctions exist, WBS tasks exist
- Verify template precedence: set team default, create project with that team, verify team template applied
- Verify template precedence: clear team default, set system default, create project, verify system template applied

---

### FEAT-ONBOARD-002 — Guided Program Onboarding Wizard ✅
**Objective:** Add a step-driven onboarding experience for manual program creation.

**Scope:**
A multi-step wizard dialog accessible from `ProgramListPage`.

Steps:
1. **Basics** — Program name (required), description, program type, program goals, business unit
2. **Ownership** — Program Manager (server-side SearchableSelect), Executive Sponsor
3. **Review & Create** — Summary. Single "Create Program" action.

Create sequence:
1. Create `msdyn_projectprogram` via `dv.create()` (programs are not PSS-managed)
2. PATCH ownership lookups via PascalCase `@odata.bind` syntax
3. Navigate to `/programs/{newProgramId}`

**File paths:**
- `app/src/pages/Programs/ProgramListPage.tsx` — add "New Program" button
- `app/src/pages/Programs/ProgramOnboardingWizard.tsx` — new component
- `app/src/api/programs.api.ts` — add `createProgram()` function
- `app/src/hooks/usePrograms.ts` — add `useCreateProgram()` mutation hook

**Schema impact:** None — uses existing `msdyn_projectprogram` table

**Dependencies:** None

**Acceptance criteria:**
- "New Program" button on ProgramListPage opens the wizard
- Create action produces a valid `msdyn_projectprogram` record
- User lands on the new program's detail page
- All user dropdowns use server-side search

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Create a program via wizard → verify record in Dataverse

---

### FEAT-ONBOARD-003 — Intake Conversion Onboarding ✅
**Objective:** Replace the blind server-side intake-to-project conversion with a guided in-app onboarding experience that pre-populates from the intake request.

**Scope:**
When an approved request is ready for conversion, the PMO user clicks "Convert to Project" on `IntakeDetailPage`. This opens the Project Onboarding Wizard (FEAT-ONBOARD-001) pre-populated with data from the `pmo_projectrequest` record:

| Request field | Wizard field |
|---------------|-------------|
| `pmo_name` | Project name |
| `pmo_submissiontext` | Project description |
| `_pmo_targetteam_value` | Primary Team |
| `pmo_lineofbusiness` | Line of business |
| `_pmo_affectedsystem_value` | (reference, not mapped to project) |
| `pmo_extractedfieldsjson` | Pre-populate CFR category if AI extracted it |

After project creation, the wizard:
1. Sets `pmo_ConvertedProject@odata.bind` on the request record pointing to the new project
2. Updates request status to `REQUEST_STATUS.Converted` (893460025)
3. Navigates to the new project detail page

If conversion target is a program (rare case), the wizard opens FEAT-ONBOARD-002 instead with relevant pre-population.

**File paths:**
- `app/src/pages/Intake/IntakeDetailPage.tsx` — replace current "Approve" action with "Convert to Project" button (available when status = Approved); add "Convert to Program" secondary action
- `app/src/pages/Projects/ProjectOnboardingWizard.tsx` — add `prefill?: Partial<ProjectCreate>` prop for pre-population
- `app/src/api/projectRequests.api.ts` — add `convertRequest(requestId, projectId)` function that sets the converted project lookup and status

**Schema impact:** None — uses existing fields on `pmo_projectrequest`

**Dependencies:**
- FEAT-ONBOARD-001
- FEAT-ONBOARD-002 (for program conversion path)

**Acceptance criteria:**
- "Convert to Project" button appears on approved intake requests
- Wizard opens pre-populated with request data
- After creation, the request record has `_pmo_convertedproject_value` set and status = Converted
- Request detail page shows the linked project after conversion
- Existing server-side `pmo_CFR_IntakeToProject` flow remains as a fallback for bulk/automated conversions but is no longer the primary path

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Submit request → approve → convert via wizard → verify request linked to project, project has correct metadata

---

### FEAT-DOC-001 — SharePoint Document Service ✅
**Objective:** Implement the app-side document abstraction using SharePoint as storage.

**Scope:**
- Shared document service layer for SharePoint REST API interactions
- Dataverse `pmo_documentlink` metadata table linking project/program records to SharePoint locations
- File upload, download, metadata tagging
- SharePoint folder resolution by project/program

**File paths:**
- `app/src/lib/sharePointClient.ts` — new SharePoint REST API wrapper
- `app/src/models/documentLink.model.ts` — new model
- `app/src/api/documentLinks.api.ts` — new API
- `app/src/hooks/useDocumentLinks.ts` — new hooks
- `app/src/lib/constants.ts` — add `ENTITY_SETS.documentLink: 'pmo_documentlinks'`

**Schema impact:**
New table: `pmo_documentlink`

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| `pmo_documentlinkid` | PK | Yes | Auto |
| `pmo_name` | String(200) | Yes | Document display name |
| `pmo_sharepointurl` | String(2000) | Yes | Full SharePoint URL |
| `pmo_category` | Choice | No | Document category (Charter, SOW, Budget, Status, etc.) |
| `pmo_description` | Memo | No | |
| `pmo_Project` | Lookup → `msdyn_project` | No | |
| `pmo_Program` | Lookup → `msdyn_projectprogram` | No | |
| `statecode` | State | Yes | 0=Active, 1=Inactive |

**Dependencies:** None

**Acceptance criteria:**
- Documents linked to projects/programs via Dataverse metadata
- SharePoint folder resolution works for project and program records
- Upload and download functions work through the service layer

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- API tests for metadata CRUD

---

### FEAT-NOTIF-001 — Unified Toast Service ✅
**Objective:** Standardize ephemeral user feedback across the app.

**Scope:**
- Single toast context provider wrapping the app
- `useToast()` hook returning `{ success, error, info, warning }` functions
- All new feature work uses this service for user feedback
- Reuse `sonner` if already in dependencies, otherwise implement via React context + CSS animation

**File paths:**
- `app/src/components/common/ToastProvider.tsx` — new provider
- `app/src/hooks/useToast.ts` — new hook
- `app/src/App.tsx` — wrap with `<ToastProvider>`

**Schema impact:** None

**Dependencies:** None

**Acceptance criteria:**
- All new mutations show success/error toasts
- Toasts auto-dismiss after 5 seconds
- Error toasts include actionable message text

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Component tests for toast behavior

---

## Tier 1 — Highest-Priority Enterprise PM/PPM Gaps

### FEAT-GOV-001 — Stage-Gate Framework ✅
**Objective:** Add formal lifecycle gates for project governance.

**Scope:**
- Gate model in Dataverse
- Gate readiness rendering on project detail page (new "Governance" tab or section)
- Gate progression rules (warn or block based on gate status)
- Governance analytics integration

**File paths:**
- `app/src/models/projectGate.model.ts` — new model
- `app/src/api/projectGates.api.ts` — new API
- `app/src/hooks/useProjectGates.ts` — new query + mutation hooks
- `app/src/pages/Projects/ProjectDetailPage.tsx` — add gates section to project detail
- `app/src/lib/constants.ts` — add `ENTITY_SETS.projectGate: 'pmo_projectgates'`, `ENTITY_SETS.projectGateDecision: 'pmo_projectgatedecisions'`, gate status/type option set constants

**Schema impact:**
New tables:

`pmo_projectgate`:

| Column | Type | Required |
|--------|------|----------|
| `pmo_projectgateid` | PK | Yes |
| `pmo_name` | String(200) | Yes |
| `pmo_gatetype` | Choice | Yes |
| `pmo_gateorder` | Integer | Yes |
| `pmo_status` | Choice | Yes |
| `pmo_targetdate` | DateTime | No |
| `pmo_completeddate` | DateTime | No |
| `pmo_notes` | Memo | No |
| `pmo_Project` | Lookup → `msdyn_project` | Yes |
| `pmo_Owner` | Lookup → `systemuser` | No |
| `statecode` | State | Yes |

`pmo_projectgatedecision`:

| Column | Type | Required |
|--------|------|----------|
| `pmo_projectgatedecisionid` | PK | Yes |
| `pmo_decision` | Choice | Yes |
| `pmo_decisiondate` | DateTime | Yes |
| `pmo_notes` | Memo | No |
| `pmo_Gate` | Lookup → `pmo_projectgate` | Yes |
| `pmo_DecidedBy` | Lookup → `systemuser` | Yes |
| `statecode` | State | Yes |

**Dependencies:**
- FEAT-AUTO-001

**Acceptance criteria:**
- Projects display lifecycle gates on detail page
- Each gate has status, decision state, owner, target date, notes, completion state
- Gate readiness visible in project detail
- Stage progression warns or blocks based on gate status

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Gate CRUD in browser; verify decision records persist

---

### FEAT-GOV-002 — Gate Approval Workflow ✅
**Objective:** Add approval flow for governance decisions.

**Scope:**
- Submit/approve/reject actions on gate decisions
- Approval state persistence via `pmo_projectgatedecision`
- Notification integration (uses FEAT-NOTIF-001 for toasts; FEAT-NOTIF-002 for durable notifications when available)

**File paths:**
- `app/src/pages/Projects/ProjectDetailPage.tsx` — gate decision action buttons
- `app/src/hooks/useProjectGates.ts` — add decision mutation

**Schema impact:** Uses gate tables from FEAT-GOV-001

**Dependencies:**
- FEAT-GOV-001

**Acceptance criteria:**
- Gate decisions can be submitted, approved, or rejected from project detail
- Approval outcomes update gate state
- Toast notifications on approval actions

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Submit → approve → verify gate status updated

---

### FEAT-GOV-003 — Governance Dashboard ✅
**Objective:** Give PMO a portfolio-level governance view.

**Scope:**
- New analytics page showing overdue gates, pending approvals, governance exceptions, missing readiness conditions
- Filterable by team, program, date range

**File paths:**
- `app/src/pages/Analytics/GovernancePage.tsx` — new page
- `app/src/App.tsx` — add route `/analytics/governance`
- `app/src/components/layout/Sidebar.tsx` — add nav link under Analytics

**Schema impact:** Uses gate model from FEAT-GOV-001

**Dependencies:**
- FEAT-GOV-001

**Acceptance criteria:**
- PMO can filter and review governance readiness across the portfolio
- Overdue gates and missing conditions are highlighted

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Page renders with gate data

---

### FEAT-INIT-001 — Required Initiation Artifact Framework ✅
**Objective:** Define and track required initiation artifacts by project type/category.

**Scope:**
- Artifact definition records (what artifacts are required for each CFR category)
- Project-specific artifact status tracking
- Readiness visibility on project detail and onboarding wizard

**File paths:**
- `app/src/models/requiredArtifact.model.ts` — new model
- `app/src/api/requiredArtifacts.api.ts` — new API
- `app/src/hooks/useRequiredArtifacts.ts` — new hooks
- `app/src/pages/Projects/ProjectDetailPage.tsx` — add initiation readiness section
- `app/src/pages/Admin/AdminSettingsPage.tsx` — artifact definition management
- `app/src/lib/constants.ts` — add entity set constants

**Schema impact:**
New tables:

`pmo_requiredartifact` (definition — what's required):

| Column | Type | Required |
|--------|------|----------|
| `pmo_requiredartifactid` | PK | Yes |
| `pmo_name` | String(200) | Yes |
| `pmo_cfrcategory` | Choice | No |
| `pmo_artifacttype` | Choice | Yes |
| `pmo_isrequired` | Boolean | Yes |
| `pmo_description` | Memo | No |
| `statecode` | State | Yes |

`pmo_projectartifactstatus` (instance — per project):

| Column | Type | Required |
|--------|------|----------|
| `pmo_projectartifactstatusid` | PK | Yes |
| `pmo_status` | Choice | Yes |
| `pmo_completeddate` | DateTime | No |
| `pmo_notes` | Memo | No |
| `pmo_Project` | Lookup → `msdyn_project` | Yes |
| `pmo_RequiredArtifact` | Lookup → `pmo_requiredartifact` | Yes |
| `pmo_DocumentLink` | Lookup → `pmo_documentlink` | No |
| `statecode` | State | Yes |

**Dependencies:**
- FEAT-GOV-001
- FEAT-DOC-001

**Acceptance criteria:**
- Required artifacts defined by CFR category in admin settings
- Projects display artifact readiness (complete/incomplete/missing)
- Missing artifacts visible as exceptions

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Define required artifacts for a category → create project with that category → verify artifact status records auto-generated

---

### FEAT-INIT-002 — Business Case / Charter / Startup Deliverables Tracking ✅
**Objective:** Make business case, charter, and core startup deliverables first-class tracked artifacts.

**Scope:**
- Seed `pmo_requiredartifact` definition records for standard startup deliverables: Business Case, Project Charter, RACI Matrix, Communication Plan, Risk Register
- Link initiation deliverables to governance gate readiness (gate cannot pass if required startup artifacts incomplete)

**File paths:**
- `app/src/pages/Projects/ProjectDetailPage.tsx` — deliverable status display in initiation section
- `app/src/hooks/useRequiredArtifacts.ts` — readiness aggregation

**Schema impact:** Uses artifact model from FEAT-INIT-001

**Dependencies:**
- FEAT-INIT-001

**Acceptance criteria:**
- Standard startup deliverables are seeded as `pmo_requiredartifact` records
- Project detail shows deliverable completion status
- Gate readiness considers required deliverable status

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Verify seed records exist; verify gate readiness reflects deliverable status

---

### FEAT-INIT-003 — Initiation Workspace ✅
**Objective:** Create a dedicated initiation experience on the project detail page.

**Scope:**
- New tab or section on ProjectDetailPage: "Initiation"
- Shows: startup artifact summary, open initiation actions, gate readiness for initiation gate
- Links to document hub for artifact uploads
- Integrated with onboarding wizard output (template tasks tagged as initiation phase are surfaced here)

**File paths:**
- `app/src/pages/Projects/ProjectDetailPage.tsx` — add Initiation tab
- `app/src/components/projects/InitiationWorkspace.tsx` — new component

**Schema impact:** Uses existing and artifact models

**Dependencies:**
- FEAT-INIT-001
- FEAT-INIT-002

**Acceptance criteria:**
- Users manage initiation readiness from a dedicated workspace
- Artifact status, gate readiness, and initiation tasks visible in one view

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Navigate to project → Initiation tab → verify all sections render

---

### FEAT-CLOSE-001 — Project Closeout Workflow ✅
**Objective:** Add governed project closeout.

**Scope:**
- Closeout checklist model
- Closure readiness logic (all required closeout items complete → project can close)
- Closeout state enforcement on project status transitions

**File paths:**
- `app/src/models/projectCloseout.model.ts` — new model
- `app/src/api/projectCloseouts.api.ts` — new API
- `app/src/hooks/useProjectCloseout.ts` — new hooks
- `app/src/pages/Projects/ProjectDetailPage.tsx` — add closeout section
- `app/src/lib/constants.ts` — add entity set, status constants

**Schema impact:**
New table: `pmo_projectcloseout`

| Column | Type | Required |
|--------|------|----------|
| `pmo_projectcloseoutid` | PK | Yes |
| `pmo_name` | String(200) | Yes |
| `pmo_checklistitem` | String(500) | Yes |
| `pmo_iscomplete` | Boolean | Yes |
| `pmo_completeddate` | DateTime | No |
| `pmo_completedby` | Lookup → `systemuser` | No |
| `pmo_notes` | Memo | No |
| `pmo_Project` | Lookup → `msdyn_project` | Yes |
| `statecode` | State | Yes |

**Dependencies:**
- FEAT-DOC-001

**Acceptance criteria:**
- Projects display closeout checklist
- Projects cannot be fully closed until required closeout items are complete
- Closeout status is visible and actionable

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Create closeout items → mark complete → verify closure readiness changes

---

### FEAT-CLOSE-002 — Lessons Learned / Outcome Capture ✅
**Objective:** Capture final outcomes, lessons learned, and handoff notes.

**Scope:**
- Structured closeout summary fields on `pmo_projectcloseout` or as extension columns on `msdyn_project`
- Lessons learned text capture
- Final outcome reporting

**File paths:**
- `app/src/pages/Projects/ProjectDetailPage.tsx` — closeout summary section
- `app/src/models/projectCloseout.model.ts` — extend if needed

**Schema impact:** Extend `pmo_projectcloseout` with summary columns or add columns to `msdyn_project`

**Dependencies:**
- FEAT-CLOSE-001

**Acceptance criteria:**
- Closeout summary stored and retrievable
- Lessons learned available for reporting

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Save and retrieve closeout summary

---

### FEAT-CLOSE-003 — Closeout Governance / Artifact Completion ✅
**Objective:** Tie closeout readiness to required deliverables, approvals, and artifact completion.

**Scope:**
- Document readiness integration with closeout checklist
- Final governance checks (all closeout-phase required artifacts complete)
- Archival disposition logic

**File paths:**
- `app/src/pages/Projects/ProjectDetailPage.tsx` — closeout readiness display
- `app/src/hooks/useProjectCloseout.ts` — readiness aggregation incorporating artifact status

**Schema impact:** Uses closeout + artifact + document models

**Dependencies:**
- FEAT-CLOSE-001
- FEAT-DOC-001
- FEAT-INIT-001

**Acceptance criteria:**
- Closeout readiness reflects missing documents and incomplete required steps
- Archival state tracked

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Readiness calculation with/without complete artifacts

---

### FEAT-CAP-001 — Capacity Planning Workspace ✅
**Objective:** Add a portfolio-level demand vs. capacity view.

**Scope:**
- Resource capacity by role/team/time horizon using existing `msdyn_resourceassignment` and `bookableresource` data
- Over-allocation detection (assigned hours > available hours per period)
- Capacity visibility across projects/programs

**File paths:**
- `app/src/pages/Analytics/CapacityPage.tsx` — new page
- `app/src/App.tsx` — add route `/analytics/capacity`
- `app/src/components/layout/Sidebar.tsx` — add nav link
- `app/src/hooks/useCapacityData.ts` — new aggregation hook

**Schema impact:** None — computed from existing assignment data

**Dependencies:** Existing resource assignment data

**Acceptance criteria:**
- PMO can see resource demand vs. capacity across projects
- Over-allocated resources highlighted

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Page renders with assignment data; overload detection fires correctly

---

### FEAT-CAP-002 — Resource Optimization Recommendations ✅
**Objective:** Recommend rebalance candidates where overload or underutilization exists.

**Scope:**
- Recommendation logic based on capacity calculations
- PMO review surface with accept/dismiss actions
- Optional Mira advisory integration later

**File paths:**
- `app/src/pages/Analytics/CapacityPage.tsx` — recommendations section
- `app/src/hooks/useCapacityData.ts` — add recommendation computation

**Schema impact:** None initially

**Dependencies:**
- FEAT-CAP-001

**Acceptance criteria:**
- Capacity issues generate visible rebalance recommendations
- Recommendations are actionable (link to project/resource)

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Rule tests for recommendation scenarios

---

## Tier 2 — Collaboration, Document, and Notification Expansion

### FEAT-DOC-002 — Project / Program Document Hub ✅
**Objective:** Add first-class document hubs in the PMO app.

**Scope:**
- Categorized document view on project and program detail pages
- Key/recent documents surface
- Missing required artifact visibility from FEAT-INIT-001
- Upload action linking to SharePoint via FEAT-DOC-001

**File paths:**
- `app/src/components/projects/DocumentHub.tsx` — new shared component
- `app/src/pages/Projects/ProjectDetailPage.tsx` — add Documents tab
- `app/src/pages/Programs/ProgramDetailPage.tsx` — add Documents tab

**Schema impact:** Uses `pmo_documentlink` from FEAT-DOC-001

**Dependencies:**
- FEAT-DOC-001

**Acceptance criteria:**
- Categorized project/program documents visible in-app
- Missing artifact states visible from the hub

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Document CRUD and category filtering in browser

---

### FEAT-DOC-003 — Artifact Readiness Integration ✅
**Objective:** Tie document readiness to initiation, governance, and closeout.

**Scope:**
- Required artifact state participates in lifecycle readiness rules
- Gate readiness checks include artifact completion
- Closeout readiness checks include required document completion

**File paths:**
- `app/src/hooks/useRequiredArtifacts.ts` — cross-lifecycle readiness aggregation
- `app/src/hooks/useProjectGates.ts` — gate readiness incorporates artifact status
- `app/src/hooks/useProjectCloseout.ts` — closeout readiness incorporates artifact status

**Schema impact:** Uses existing document and artifact models

**Dependencies:**
- FEAT-DOC-001
- FEAT-INIT-001
- FEAT-CLOSE-001
- FEAT-GOV-001

**Acceptance criteria:**
- Lifecycle workspaces rely on document/artifact readiness
- Missing documents block or warn gate progression

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Readiness calculation with/without documents

---

### FEAT-NOTIF-002 — Durable In-App Notification Center ✅
**Objective:** Add persistent actionable notification capability.

**Scope:**
- `pmo_notification` table for user-targeted durable notifications
- Notification center UI (bell icon in AppShell header, slide-out panel)
- Create/dismiss/mark-read workflow

**File paths:**
- `app/src/models/notification.model.ts` — new model
- `app/src/api/notifications.api.ts` — new API
- `app/src/hooks/useNotifications.ts` — new hooks
- `app/src/components/layout/NotificationCenter.tsx` — new component
- `app/src/components/layout/AppShell.tsx` — add notification bell trigger
- `app/src/lib/constants.ts` — add entity set

**Schema impact:**
New table: `pmo_notification`

| Column | Type | Required |
|--------|------|----------|
| `pmo_notificationid` | PK | Yes |
| `pmo_title` | String(200) | Yes |
| `pmo_body` | Memo | No |
| `pmo_category` | Choice | Yes |
| `pmo_isread` | Boolean | Yes |
| `pmo_actionurl` | String(500) | No |
| `pmo_TargetUser` | Lookup → `systemuser` | Yes |
| `pmo_Project` | Lookup → `msdyn_project` | No |
| `pmo_Program` | Lookup → `msdyn_projectprogram` | No |
| `statecode` | State | Yes |

**Dependencies:**
- FEAT-NOTIF-001

**Acceptance criteria:**
- Users receive durable notifications for stage gates, missing artifacts, closeout steps
- Notification center accessible from app header
- Notifications dismissable and markable as read

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Create/dismiss/read tests

---

### FEAT-NOTIF-003 — Telemetry-to-Notification Bridge ✅
**Objective:** Convert major workflow failures into durable PM-visible alerts.

**Scope:**
- `pmo_telemetryevent` table for telemetry persistence
- Event sink bridge: major errors create notification records
- Notification rule routing (which errors → which users)

**File paths:**
- `app/src/models/telemetryEvent.model.ts` — new model
- `app/src/api/telemetryEvents.api.ts` — new API
- `app/src/hooks/useTelemetryEvents.ts` — new hooks
- `app/src/lib/telemetry.ts` — extend to write to Dataverse in addition to console
- `app/src/lib/constants.ts` — add entity set

**Schema impact:**
New table: `pmo_telemetryevent`

| Column | Type | Required |
|--------|------|----------|
| `pmo_telemetryeventid` | PK | Yes |
| `pmo_eventtype` | String(100) | Yes |
| `pmo_severity` | Choice | Yes |
| `pmo_payload` | Memo | Yes |
| `pmo_source` | String(200) | No |
| `pmo_Project` | Lookup → `msdyn_project` | No |
| `statecode` | State | Yes |

**Dependencies:**
- FEAT-NOTIF-002

**Acceptance criteria:**
- Important errors create durable notification rows
- Telemetry events persisted to Dataverse

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Event-to-notification tests

---

### FEAT-TEAMS-001 — Meeting-Linked Project Context ✅
**Objective:** Link Teams meetings to project/program context in the PMO app.

**Scope:**
- `pmo_projectmeetinglink` table for meeting ↔ project/program linkage
- Meeting prep surface on project detail (upcoming meetings, agenda items)
- In-meeting contextual side panel experience

**File paths:**
- `app/src/models/projectMeetingLink.model.ts` — new model
- `app/src/api/projectMeetingLinks.api.ts` — new API
- `app/src/hooks/useProjectMeetingLinks.ts` — new hooks
- `app/src/pages/Projects/ProjectDetailPage.tsx` — add meetings section
- `app/src/lib/constants.ts` — add entity set

**Schema impact:**
New table: `pmo_projectmeetinglink`

| Column | Type | Required |
|--------|------|----------|
| `pmo_projectmeetinglinkid` | PK | Yes |
| `pmo_name` | String(200) | Yes |
| `pmo_meetingsubject` | String(500) | Yes |
| `pmo_meetingdatetime` | DateTime | Yes |
| `pmo_meetingurl` | String(2000) | No |
| `pmo_notes` | Memo | No |
| `pmo_Project` | Lookup → `msdyn_project` | No |
| `pmo_Program` | Lookup → `msdyn_projectprogram` | No |
| `statecode` | State | Yes |

**Dependencies:**
- FEAT-DOC-001
- FEAT-NOTIF-002

**Acceptance criteria:**
- Meetings can be linked to project/program context
- Project detail shows linked meetings with prep context

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Meeting link CRUD in browser

---

### FEAT-TEAMS-002 — Meeting Action Capture ✅
**Objective:** Capture meeting follow-ups directly into PMO work objects.

**Scope:**
- Action item capture from meeting context
- Conversion into task (`msdyn_projecttask` via PSS), risk (`msdyn_projectrisk`), issue (`msdyn_projectissue`), change (`msdyn_projectchange`), or decision (`pmo_projectdecision`)
- Meeting-to-record linkage

**File paths:**
- `app/src/components/meetings/MeetingActionCapture.tsx` — new component
- `app/src/pages/Projects/ProjectDetailPage.tsx` — integrate into meetings section

**Schema impact:** Reuse existing work object tables + FEAT-PMO-001 decision log

**Dependencies:**
- FEAT-TEAMS-001
- FEAT-PMO-001

**Acceptance criteria:**
- Meeting action items persist into governed PMO records
- Each action item creates the correct entity type

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Conversion-path tests for each target entity type

---

### FEAT-TEAMS-003 — Meeting Summary / Communications Hub Integration ✅
**Objective:** Surface meeting context, summaries, and follow-ups from project context.

**Scope:**
- Project-linked meeting list with summary cards
- Latest follow-up visibility
- Integration with communications hub (FEAT-PMO-002)

**File paths:**
- `app/src/pages/Projects/ProjectDetailPage.tsx` — meeting summary cards in meetings section
- `app/src/components/meetings/MeetingSummaryCard.tsx` — new component

**Schema impact:** Uses meeting linkage model from FEAT-TEAMS-001

**Dependencies:**
- FEAT-TEAMS-001
- FEAT-PMO-002

**Acceptance criteria:**
- Project detail shows linked meetings and current follow-up state

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Meeting summary rendering with follow-up status

---

### FEAT-PMO-001 — Decision Log ✅
**Objective:** Add a first-class decision log as a distinct lifecycle object.

**Scope:**
- Decision CRUD on project detail page
- Linking to projects, programs, and meetings
- Decision reporting in analytics

**File paths:**
- `app/src/models/projectDecision.model.ts` — new model
- `app/src/api/projectDecisions.api.ts` — new API
- `app/src/hooks/useProjectDecisions.ts` — new hooks
- `app/src/pages/Projects/ProjectDetailPage.tsx` — add decisions section/tab
- `app/src/lib/constants.ts` — add entity set, status constants

**Schema impact:**
New table: `pmo_projectdecision`

| Column | Type | Required |
|--------|------|----------|
| `pmo_projectdecisionid` | PK | Yes |
| `pmo_name` | String(200) | Yes |
| `pmo_description` | Memo | Yes |
| `pmo_decisiondate` | DateTime | Yes |
| `pmo_decisionowner` | Lookup → `systemuser` | No |
| `pmo_status` | Choice | Yes |
| `pmo_impact` | Choice | No |
| `pmo_Project` | Lookup → `msdyn_project` | No |
| `pmo_Program` | Lookup → `msdyn_projectprogram` | No |
| `pmo_MeetingLink` | Lookup → `pmo_projectmeetinglink` | No |
| `statecode` | State | Yes |

**Dependencies:** None

**Acceptance criteria:**
- Decisions are distinct from risks, issues, and changes
- Decisions linkable to projects, programs, and meeting outcomes
- Decision CRUD works on project detail page

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- CRUD and linkage tests

---

### FEAT-PMO-002 — Communications Hub ✅
**Objective:** Create one consolidated collaboration/workflow surface in the app.

**Scope:**
- New section/tab on project detail: linked meetings, documents, durable notifications, recent follow-up actions
- Aggregates FEAT-DOC-002, FEAT-NOTIF-002, FEAT-TEAMS-003

**File paths:**
- `app/src/components/projects/CommunicationsHub.tsx` — new component
- `app/src/pages/Projects/ProjectDetailPage.tsx` — add as tab/section

**Schema impact:** Uses linked models from dependencies

**Dependencies:**
- FEAT-DOC-002
- FEAT-NOTIF-002
- FEAT-TEAMS-003

**Acceptance criteria:**
- Communications, documents, meetings, and follow-ups surfaced together on project context

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- UI composition renders all sub-sections

---

## Tier 3 — Remaining Enterprise PM/PPM Benchmark Gaps

### FEAT-PORT-001 — Portfolio Prioritization Model ✅
**Objective:** Add formal prioritization and scoring beyond intake routing.

**Scope:**
- Scoring model with configurable weighted factors
- Priority visibility on project list and analytics
- PMO ranking inputs

**File paths:**
- `app/src/pages/Analytics/PrioritizationPage.tsx` — new page or extend HealthPage
- `app/src/hooks/usePrioritizationScoring.ts` — new computation hook

**Schema impact:** Extend `msdyn_project` with scoring columns or use computed views

**Dependencies:**
- FEAT-INIT-002

**Acceptance criteria:**
- Projects scored and prioritized using standardized factors
- Scoring visible on project list and analytics views

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Score calculation tests

---

### FEAT-PORT-002 — Scenario Comparison Workspace ✅
**Objective:** Compare candidate work under constrained capacity/funding assumptions.

**Scope:**
- What-if comparison workspace
- Alternative portfolio views under different constraint scenarios

**File paths:**
- `app/src/pages/Analytics/ScenarioPage.tsx` — new page

**Schema impact:** Computed model preferred

**Dependencies:**
- FEAT-PORT-001
- FEAT-CAP-001

**Acceptance criteria:**
- PMO can compare competing initiatives under different scenarios

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Scenario calculation tests

---

### FEAT-FIN-001 — Project Financial Tracking Expansion ✅
**Objective:** Expand project financial visibility beyond simple budget fields.

**Scope:**
- Budget, forecast, actual tracking where data available
- Variance-ready structure

**File paths:**
- `app/src/pages/Projects/ProjectDetailPage.tsx` — expand Financials tab
- `app/src/models/project.model.ts` — extend with financial columns if needed

**Schema impact:** Extend existing project/program financial columns

**Dependencies:** None

**Acceptance criteria:**
- Project/program financial panels support richer planning and reporting
- Variance structure exists even if actuals feed is deferred

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Financial aggregation tests

---

### FEAT-FIN-002 — Portfolio Cost Visibility ✅
**Objective:** Add cross-project financial visibility for PMO decisions.

**Scope:**
- Portfolio cost/forecast summaries
- Financial filters and comparisons across projects

**File paths:**
- `app/src/pages/Analytics/FinancialPage.tsx` — new page or extend HealthPage

**Schema impact:** Uses project/program financial model

**Dependencies:**
- FEAT-FIN-001

**Acceptance criteria:**
- PMO views financial context across projects/programs

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Portfolio financial aggregation tests

---

### FEAT-CTRL-001 — Baseline Capture ✅
**Objective:** Support formal baseline snapshots for schedule/governance metrics.

**Scope:**
- Baseline capture action on project detail
- Baseline retrieval and reference in reporting

**File paths:**
- `app/src/models/projectBaseline.model.ts` — new model
- `app/src/api/projectBaselines.api.ts` — new API
- `app/src/hooks/useProjectBaselines.ts` — new hooks
- `app/src/pages/Projects/ProjectDetailPage.tsx` — baseline capture action

**Schema impact:** New `pmo_projectbaseline` table or extend project model

**Dependencies:**
- FEAT-FIN-001

**Acceptance criteria:**
- Baselines captured and retrievable
- Baseline data usable in reporting

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Baseline persistence tests

---

### FEAT-CTRL-002 — Variance / Trend Reporting ✅
**Objective:** Show movement against baseline over time.

**Scope:**
- Variance logic (current vs. baseline)
- Trend visuals (recharts)
- Status/reporting integration

**File paths:**
- `app/src/pages/Analytics/VariancePage.tsx` — new page or extend existing analytics
- `app/src/hooks/useVarianceData.ts` — computation hook

**Schema impact:** Uses baseline model

**Dependencies:**
- FEAT-CTRL-001

**Acceptance criteria:**
- Status and analytics surfaces show baseline variance where baseline exists

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Variance calculation tests

---

### FEAT-ROAD-001 — Portfolio Roadmap ✅
**Objective:** Add a cross-project/program roadmap view.

**Scope:**
- Chronological portfolio roadmap (Gantt-like or timeline)
- Executive planning view showing major initiatives and their timelines

**File paths:**
- `app/src/pages/Analytics/RoadmapPage.tsx` — new page
- `app/src/App.tsx` — add route

**Schema impact:** Computed from existing project/program scheduling data

**Dependencies:** Existing project/program scheduling data

**Acceptance criteria:**
- PMO sees a roadmap of major initiatives across programs

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- View-model tests

---

### FEAT-ROAD-002 — Cross-Project Dependency Visibility ✅
**Objective:** Surface dependency risk across initiatives.

**Scope:**
- Cross-project dependency relationships
- Roadmap dependency overlay

**File paths:**
- `app/src/pages/Analytics/RoadmapPage.tsx` — dependency overlay
- `app/src/hooks/useCrossProjectDependencies.ts` — new hook

**Schema impact:** Extend dependency view logic; add schema only if required

**Dependencies:**
- FEAT-ROAD-001

**Acceptance criteria:**
- PMO views dependency relationships across multiple initiatives

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Dependency graph calculation tests

---

## Tier 4 — Deferred Product Enhancements

These remain valid but are lower priority than the work above:

- Goal linkage (schema not yet discovered for `msdyn_projectgoal` / `msdyn_projecttasktogoal`)
- Timeline / Gantt view (data ready; blocked on library selection — frappe-gantt recommended; read-only first)
- Drag-and-drop between buckets
- Additional dependency types (FF / SS / SF)
- SPA URL routing / browser refresh state
- Mira open tasks refinement
- Mira "what needs attention" refinement
- True contextual freeform Mira chat
- Teams channel intake

### Permanently Blocked / Out of Scope

- Planner-synced task attachments as a PMO app feature path
- Planner-synced task comments / conversation as a PMO app feature path
- PMO-native chat as a messaging system
- Dataverse file storage for project documents
- Team-per-program / channel-per-project automation in this phase

---

## Delivery Sequence

### Wave A — Foundational Infrastructure
Execute in order:
1. FEAT-AUTO-001 (plan normalization) ✅
2. ~~FEAT-AUTO-002 (CI/CD pipeline)~~ — DEFERRED (dfr-017, infrastructure prerequisite)
3. FEAT-AUTO-003 (schema snapshot) ✅

**Wave gate:** `npx tsc -b --noEmit && npm run build` passes. Wave A complete (2/3 executed, 1 deferred).

### Wave B — Templates, Onboarding, and Cross-Cutting Foundations
Execute in dependency order:
1. FEAT-TMPL-001 (project template model — schema + admin UI) ✅
2. FEAT-TMPL-002 (team default template — pmo_appsettings namespaced keys) ✅
3. FEAT-TMPL-003 (system default template — admin setting) ✅
4. FEAT-ONBOARD-001 (project onboarding wizard) ✅
5. FEAT-ONBOARD-002 (program onboarding wizard) ✅
6. FEAT-ONBOARD-003 (intake conversion onboarding) ✅
7. FEAT-DOC-001 (SharePoint document service) ✅
8. FEAT-NOTIF-001 (toast service) ✅

**Wave gate:** `npx tsc -b --noEmit && npm run build` — PASSED. Wave B complete.

### Wave C — Highest-Priority Benchmark Gaps
Execute in dependency order:
1. FEAT-GOV-001 (stage-gate framework) ✅
2. FEAT-GOV-002 (gate approval workflow) ✅
3. FEAT-GOV-003 (governance dashboard) ✅
4. FEAT-INIT-001 (required artifact framework) ✅
5. FEAT-INIT-002 (startup deliverables tracking) ✅
6. FEAT-INIT-003 (initiation workspace) ✅
7. FEAT-CLOSE-001 (closeout workflow) ✅
8. FEAT-CLOSE-002 (lessons learned / outcome capture) ✅
9. FEAT-CLOSE-003 (closeout governance) ✅
10. FEAT-CAP-001 (capacity planning workspace) ✅
11. FEAT-CAP-002 (resource optimization recommendations) ✅

**Wave gate:** `npx tsc -b --noEmit && npm run build` — PASSED. `npx power-apps push` — DEPLOYED. Wave C complete.

### Wave D — Collaboration and PM Workflow Expansion
Execute in dependency order:
1. FEAT-DOC-002 (project/program document hub) ✅
2. FEAT-DOC-003 (artifact readiness integration) ✅
3. FEAT-NOTIF-002 (durable notification center) ✅
4. FEAT-NOTIF-003 (telemetry-to-notification bridge) ✅
5. FEAT-PMO-001 (decision log) ✅
6. FEAT-PMO-002 (communications hub) ✅
7. FEAT-TEAMS-001 (meeting-linked context) ✅
8. FEAT-TEAMS-002 (meeting action capture) ✅
9. FEAT-TEAMS-003 (meeting summary integration) ✅

**Wave gate:** `npx tsc -b --noEmit && npm run build` — PASSED. `npx power-apps push` — DEPLOYED. Wave D complete.

### Wave E — Remaining Benchmark Gaps
Execute in dependency order:
1. FEAT-PORT-001 (portfolio prioritization) ✅
2. FEAT-PORT-002 (scenario comparison) ✅
3. FEAT-FIN-001 (financial tracking expansion) ✅
4. FEAT-FIN-002 (portfolio cost visibility) ✅
5. FEAT-CTRL-001 (baseline capture) ✅
6. FEAT-CTRL-002 (variance / trend reporting) ✅
7. FEAT-ROAD-001 (portfolio roadmap) ✅
8. FEAT-ROAD-002 (cross-project dependency visibility) ✅

**Wave gate:** `npx tsc -b --noEmit && npm run build` — PASSED. `npx power-apps push` — DEPLOYED. Wave E complete.

### Wave F — Lifecycle Workspace Upgrades
Replaced generic CRUD tabs with structured lifecycle workspaces. Schema extended + 6 workspace components built and wired into ProjectDetailPage.

Schema changes:
- 2 new tables: `pmo_gatesettemplate`, `pmo_gatesetitem` (admin gate set configuration)
- 13 new columns across 4 existing tables: `pmo_projectgate` (+rationale), `pmo_projectdecision` (+rationale, +impactdescription), `pmo_documentlink` (+sharepointitemid, +filesize, +modifiedbyname), `pmo_projectmeetinglink` (+grapheventid, +attendeesjson, +duration, +location, +summary, +agendanotes)
- All registered in ENTITY_SETS, DATAVERSE_SOURCES, power.config.json

Features executed:
1. FEAT-INIT-100 (Initiation Workspace — 7-dimension guided readiness with inline artifact actions) ✅
2. FEAT-GOV-100 (Gate Workspace — timeline progression, readiness conditions, rationale-captured approvals) ✅
3. FEAT-DEC-100 (Decision Workspace — full metadata, edit capability, meeting linkage, owner/impact/rationale) ✅
4. FEAT-DOC-100 (Document Library — SharePoint REST API browser, drag-drop upload, category view, artifact overlay) ✅
5. FEAT-MTG-100 (Meeting Workspace — Graph Calendar scheduling, attendees, summary, action capture, separate tab) ✅
6. FEAT-CLO-100 (Closeout Workspace — 5-dimension readiness, structured lessons/summary, archive with gate) ✅

New files:
- `app/src/components/projects/GateWorkspace.tsx`
- `app/src/components/projects/DecisionWorkspace.tsx`
- `app/src/components/projects/DocumentLibrary.tsx`
- `app/src/components/projects/MeetingWorkspace.tsx`
- `app/src/components/projects/CloseoutWorkspace.tsx`
- `app/src/lib/sharePointClient.ts` (SharePoint REST API wrapper)
- `app/src/lib/graphClient.ts` (Microsoft Graph Calendar API wrapper)
- `app/src/models/gateSetTemplate.model.ts`
- `app/src/api/gateSetTemplates.api.ts`
- `app/src/hooks/useGateSetTemplates.ts`

Replaced files:
- `app/src/components/projects/InitiationWorkspace.tsx` — full rewrite from passive display to guided workspace

Removed from ProjectDetailPage:
- Inline GateForm, DecisionForm, CloseoutItemForm components
- All inline gate/decision/closeout TabsContent JSX (replaced with workspace component delegation)
- CommunicationsHub from Documents tab (replaced with DocumentLibrary; meetings moved to own tab)

ProjectDetailPage tabs (15 total): Summary, Business Case, Financials, Resources, Tasks, Risks, Issues, Changes, Status, Initiation, Gates, Decisions, Documents, Meetings, Closeout

**Wave gate:** `npx tsc -b --noEmit && npm run build` — PASSED. `npx power-apps push` — DEPLOYED. Wave F complete. All waves complete.

---

## Technical Architecture Reference

### Mandatory Build Sequence (Every Change)
```bash
cd app
npx tsc -b --noEmit
npm run build
npx power-apps push
```

### Mandatory Validation Sequence (CI/CD)
```bash
npm ci
npx tsc -b --noEmit
npm run build
npm test
```

### Reusable Patterns (Existing Code)

| Pattern | Source | Reuse for |
|---------|--------|-----------|
| OData list/get/create/update/deactivate | `app/src/lib/dataverseClient.ts` | All entity CRUD |
| PSS OperationSet (create/update/delete tasks) | `app/src/lib/schedulingClient.ts` | Task creation from templates |
| `applyProjectTemplate(projectId, tasks)` | `app/src/lib/schedulingClient.ts:620` | Template WBS task creation |
| `TemplateTask[]` interface | `app/src/lib/projectTemplates.ts` | Template task payload format |
| Server-side user search with noise filter | `ProjectDetailPage.tsx` `searchUsers` | All user SearchableSelect fields |
| `SearchableSelect` (dual-mode) | `app/src/components/common/SearchableSelect.tsx` | All dropdown selects |
| `pmo_projectteam` junction CRUD | `app/src/api/projectTeams.api.ts` | Team participation setup during onboarding |
| Team membership query | `teammembership_association/any()` filter | Manager restriction, scoped user queries |
| AAD group scope resolution | `azureactivedirectoryobjectid` on team entity | ALM-safe user scoping |
| `pmo_appsettings` key-value | `app/src/hooks/useAppSettings.ts` | System default template, user scope group |
| TanStack Query pattern | `app/src/hooks/use*.ts` | All new query/mutation hooks |
| API file pattern | `app/src/api/*.api.ts` | All new entity APIs |
| Model file pattern | `app/src/models/*.model.ts` | All new entity models |
| Option set constants | `app/src/lib/constants.ts` | All new choice field values |

### Key Entry Points
- `app/src/pages/Projects/ProjectDetailPage.tsx` — tab shell for all lifecycle workspaces (15 tabs)
- `app/src/components/projects/InitiationWorkspace.tsx` — guided startup readiness workspace
- `app/src/components/projects/GateWorkspace.tsx` — gate timeline, readiness conditions, rationale approvals
- `app/src/components/projects/DecisionWorkspace.tsx` — governed decision log with full metadata
- `app/src/components/projects/DocumentLibrary.tsx` — SharePoint-integrated in-app document library
- `app/src/components/projects/MeetingWorkspace.tsx` — Graph-integrated meeting management
- `app/src/components/projects/CloseoutWorkspace.tsx` — structured closeout with readiness dimensions
- `app/src/lib/sharePointClient.ts` — SharePoint REST API wrapper (folder/file browse, upload, create folder)
- `app/src/lib/graphClient.ts` — Microsoft Graph Calendar API wrapper (create/update/get events)
- `app/src/lib/schedulingClient.ts` — PSS client
- `app/src/lib/dataverseClient.ts` — Dataverse SDK wrapper
- `app/src/lib/constants.ts` — entity sets, option set values, settings keys
- `app/src/lib/projectTemplates.ts` — code-defined WBS template seed data
- `app/src/components/scheduling/` — task workspace components
- `app/src/pages/` — all page components
- `app/src/api/` — OData read/write functions (including gateSetTemplates.api.ts)
- `app/src/hooks/` — TanStack Query hooks (including useGateSetTemplates.ts)
- `app/src/models/` — TypeScript entity interfaces (including gateSetTemplate.model.ts)
- `app/src/ai/` — Mira advisory
- `solution/src/` — Dataverse solution XML
- `copilot-studio/` — Copilot Studio artifacts
- `docs/planning/` — planning artifacts

### Multi-Team Execution Details

The multi-team model is implemented and the following behaviors are enforced by default:

- **Primary Team** is set via `pmo_PrimaryTeam@odata.bind` on the `msdyn_project` record. The Primary Team owns the project and its WBS plan.
- **Contributing Teams** are added via `pmo_projectteam` junction records with `pmo_role = TEAM_ROLE.Contributing (893460041)`.
- **Onboarding initializes both** — the wizard creates the Primary Team binding and Contributing Team junctions in the same create flow (FEAT-ONBOARD-001 step 3).
- **Cross-team visibility** is built into the existing data model: all project data (tasks, risks, issues, changes, status reports) is project-scoped, not team-scoped. Any user with project access sees all data regardless of team affiliation.
- **Team-scoped task views** are supported via the existing `_msdyn_assignedteammembers_value` and resource assignment model — tasks can be filtered by assigned team member, enabling team-focused workstream views without data siloing.
- **Task templates initialize shared execution** — when a template is applied during onboarding, WBS tasks are created at the project level. Contributing teams can be assigned to specific tasks/buckets after creation via the existing assignment flow.
- **PMO_TEAM_FLAG** (`cr741_pmoteam` in DEV, `pmo_pmoteam` in UAT/PROD) filters the team dropdown to show only PMO-managed teams, preventing selection of system or application teams.

### Pre-UAT Promotion Gate (Human Required)
Before promoting to UAT:
1. Rename `PMO_TEAM_FLAG` from `cr741_pmoteam` to `pmo_pmoteam` in `constants.ts`
2. Add `pmo_pmoteam` (Boolean) column to `team` entity in `CFRProjectManagement` solution XML
3. Import solution to UAT and populate the flag on PMO teams
4. Update `power.config.json` target to UAT environment
5. Full validation: `npx tsc -b --noEmit && npm run build && npm test`
6. User acceptance sign-off from PMO stakeholders

### Governance
- Standards authority: `corp-fin-bi-standards` (live, always open in workspace)
- Publisher prefix: `pmo_` within this solution boundary; `rcm` for cross-solution work
- CODEOWNERS and PR approval rules in force
- No direct commits to `main`
- All Dataverse schema creation follows `dataverse-agent-behavior-standard.md`
- All code app operations follow `power-apps-code-app-operating-standard.md`

### Final Rule for Agents
This document is the execution authority. Do not reinterpret it as a research brief. Do not ask for architectural choices already made here. Produce implementation steps that assume autopilot execution, preserve the PMO app as the primary command center, and implement the roadmap in the delivery sequence defined above.

---

## Testing Plan — All Waves

### Wave A — Foundational Infrastructure

#### FEAT-AUTO-001 — Plan Normalization
1. Open `docs/planning/PMOCFRSolution__AutopilotExecutionPlan.md` and search for "evaluate", "determine later", "confirm whether", "consider if" — should only appear in the rules section that prohibits those phrases, never in feature content.

#### FEAT-AUTO-002 — CI/CD Pipeline
1. Deferred (dfr-017). No testing required.

#### FEAT-AUTO-003 — Schema Snapshot
1. Open `docs/schema-snapshot.md`. Verify it lists all entity sets from `constants.ts`, option set values, OData bind syntax, PSS reference, and environment mappings.

---

### Wave B — Templates, Onboarding, Cross-Cutting Foundations

#### FEAT-TMPL-001 — Project Template Model
1. Navigate to Admin Settings. Scroll to "Project Templates" section.
2. Click "New Template". Enter a name, select a CFR category, click "Prefill from category default" to populate tasks. Verify task count displays.
3. Click "Create". Verify toast. Verify template appears in the list with name, category, and task count.
4. Click the pencil icon to edit. Change the name. Click Save. Verify toast and updated name.
5. Click the trash icon. Verify template disappears from the list.

#### FEAT-TMPL-002 — Team Default Template
1. Navigate to Teams. Expand a team.
2. Verify "Default Project Template" dropdown appears below the members section.
3. Select a template. Verify toast: "Default template set to [name]".
4. Clear the selection. Verify toast: "Default template cleared".
5. Collapse and re-expand. Verify the selected template persists.
6. On the collapsed row, verify the template name shows as a subtle label.

#### FEAT-TMPL-003 — System Default Template
1. Navigate to Admin Settings. Verify "Default Project Template" setting row.
2. Click Edit. Select a template. Click Save. Verify toast.
3. Click Edit again. Clear the value. Click Save. Verify it saves successfully.

#### FEAT-ONBOARD-001 — Project Onboarding Wizard
1. Navigate to Projects. Verify "New Project" button appears.
2. Click "New Project". Verify 6-step wizard opens (Basics, Ownership, Template, Team, Classification, Review).
3. **Step 1 — Basics:** Enter project name. Select a CFR category. Click Next. Try clicking Next without a name — verify button is disabled.
4. **Step 2 — Ownership:** Search for a PM (type 2+ characters). Select a PM. Select a Primary Team. Click Next.
5. **Step 3 — Template:** Verify the resolved template shows with its source (User selected / Team default / System default / Category fallback). Select a different template manually — verify source changes. Verify task list preview.
6. **Step 4 — Team:** Verify Manager search works. Add a contributing team. Add a second. Remove one. Click Next.
7. **Step 5 — Classification:** Select complexity, strategic priority. Click Next.
8. **Step 6 — Review:** Verify all selections displayed. Click "Create Project".
9. Verify toast. Verify you land on the new project detail page. Verify PM, Primary Team, CFR category are set. Navigate to Tasks tab — verify template tasks created.

#### FEAT-ONBOARD-002 — Program Onboarding Wizard
1. Navigate to Programs. Verify "New Program" button.
2. Click it. Verify 3-step wizard (Basics, Ownership, Review).
3. Enter name, select type/goals. Click through to Review. Click "Create Program".
4. Verify toast and navigation to new program detail. Verify name and manager set.

#### FEAT-ONBOARD-003 — Intake Conversion
1. Open an intake request with status = Approved (no converted project yet).
2. Verify "Convert to Project" button appears.
3. Click it. Verify wizard opens pre-populated with request name, description, target team, category.
4. Complete wizard. Click "Create Project".
5. Verify toast. Verify you land on new project detail.
6. Navigate back to request. Verify status = "Converted" and "Converted Project" field shows the linked project.
7. Verify "Convert to Project" button no longer appears.

#### FEAT-DOC-001 — SharePoint Document Service
1. Tested via Documents tab (see Wave F, FEAT-DOC-100).

#### FEAT-NOTIF-001 — Toast Service
1. Perform any save action. Verify green toast appears bottom-right.
2. Verify auto-dismiss after ~5 seconds.
3. Click the X on a toast. Verify immediate dismiss.
4. Trigger an error. Verify red error toast appears.

---

### Wave C — Governance, Initiation, Closeout, Capacity

#### Initiation Tab (FEAT-INIT-100)
1. Open a project detail page. Click the **Initiation** tab.
2. Verify the **Readiness Dashboard** with percentage bar and 7 dimension pills (Metadata, Ownership, Teams, Governance, Artifacts, Template, Execution).
3. Verify pills are color-coded: green = complete, amber = partial, red = missing.
4. Click a pill — verify the corresponding card expands.
5. **Metadata card:** If missing category or start date, verify amber indicator and "Edit Project" button that opens ProjectEditDialog.
6. **Ownership card:** If PM or Sponsor missing, verify amber/red indicator and "Edit Project" button.
7. **Teams card:** Verify Primary Team name displays. If no primary team, verify red indicator.
8. **Artifacts card:** Verify only artifacts matching this project's CFR category are shown.
9. **Artifact inline actions:** Click "Complete" — verify green check. Click "In Progress" — verify blue circle. Click "Waive" — verify treated as complete.
10. Verify readiness percentage updates as dimensions are resolved.
11. **Template card:** If tasks exist, verify green. If no tasks, verify amber.

#### Gates Tab (FEAT-GOV-100)
1. Click the **Gates** tab.
2. If no gates: verify empty state message about admin-configured gate sets.
3. If gates exist: verify **gate timeline** as horizontal progression bar with numbered circles. Passed gates show green checkmarks.
4. Verify **Active Gate Card** highlights the first non-passed gate.
5. **Readiness conditions:** Verify predecessor gate status and artifact completion shown.
6. Click **Approve** — verify rationale dialog opens. Submit without text — verify disabled. Enter rationale — click Approve — verify toast, status changes to Passed, timeline advances.
7. Click **Reject** on another gate — verify rationale required, status changes to Failed.
8. Expand a gate in "All Gates" — verify **Decision History** (who, when, decision, rationale).

#### Governance Dashboard (FEAT-GOV-003)
1. Navigate to Analytics > Governance.
2. Verify summary cards: Total Gates, Overdue, Pending, Failed.
3. If overdue gates exist, verify "Overdue Gates" section with red styling.
4. Click a gate row — verify navigation to correct project.

#### Closeout Tab (FEAT-CLO-100)
1. Click the **Closeout** tab.
2. Verify **Readiness Banner** with 5 dimension pills: Required Items, Artifacts, Gate, Lessons Learned, Outcome Summary.
3. Click "Add Item" — enter checklist item — verify it appears with unchecked checkbox.
4. Click checkbox — verify toggle to complete (green checkmark, strikethrough). Verify counter updates.
5. Uncheck — verify revert.
6. **Lessons Learned** textarea: type content, click away. Verify toast. Reload page — verify persistence.
7. **Outcome Summary** textarea: same test.
8. Verify **Archive** button disabled until all readiness dimensions complete.
9. Complete all items + capture lessons + summary — verify Archive enabled. Click — verify confirmation dialog. Confirm — verify toast and project archived.

#### Capacity Page (FEAT-CAP-001/002)
1. Navigate to Analytics > Capacity.
2. Verify summary cards: Assigned Resources, Over-allocated, Recommendations.
3. Verify allocation bars with utilization percentages. Resources >160h show red.
4. Verify recommendations for overloaded (>192h) and underutilized (<48h) resources.
5. If no assignments, verify empty state message.

---

### Wave D — Documents, Notifications, Meetings, Decisions

#### Documents Tab (FEAT-DOC-100)
1. Click the **Documents** tab.
2. Verify **toolbar**: Library/By Category toggle, Upload, New Folder, Link External buttons.
3. **Library view:** If SharePoint accessible, verify folder/file tree with Name, Size, Modified columns. Click folder — verify breadcrumb updates. Click "Root" — verify navigation back.
4. **If SharePoint not accessible:** Verify graceful fallback. Previously linked documents still display.
5. **Upload:** Click Upload — select file — verify toast on success and `pmo_documentlink` record created.
6. **Drag-and-drop:** Drag file over library area — verify border highlights. Drop — verify upload and toast.
7. **New Folder:** Click — enter name — verify folder appears.
8. **Link External:** Click — enter name and URL — verify document appears with external link icon.
9. **By Category view:** Toggle — verify documents grouped by category. Uncategorized in own section.
10. **Required Artifacts Overlay:** If configured, verify colored pills (green = complete, amber = not started).

#### Notification Center (FEAT-NOTIF-002)
1. Verify bell icon in app header.
2. Click bell — verify slide-out panel.
3. No notifications — verify "No notifications" message.
4. Create a `pmo_notification` record targeting current user in Dataverse. Refresh. Click bell — verify notification with title, body, category badge, date, blue unread dot.
5. Click check icon — verify read (dot disappears).
6. Click X — verify dismissed.
7. Verify unread count badge updates.

#### Meetings Tab (FEAT-MTG-100)
1. Click the **Meetings** tab (separate from Documents).
2. Verify empty state: "No meetings linked."
3. Click **Schedule Meeting** — verify dialog: Subject, Date, Start/End Time, Location, Teams checkbox, Agenda textarea.
4. Fill in and click Schedule.
5. **If Graph accessible:** Verify toast, calendar event created, Teams URL populated.
6. **If Graph not accessible:** Verify toast "Calendar event could not be created — meeting saved locally". Record still appears.
7. Verify meeting card: subject, date/time, duration, Teams link icon.
8. Click to expand — verify: location, attendees, agenda, summary textarea, action capture button.
9. **Summary:** Type, click away — verify toast. Reload — verify persistence.
10. **Action capture:** Click "Capture Action" — enter text — click "Capture as Decision" — verify toast and action appears in meeting's "Actions" list AND in Decisions tab.
11. Verify **Upcoming/Past** split.

#### Decisions Tab (FEAT-DEC-100)
1. Click the **Decisions** tab.
2. Verify empty state.
3. Click **Add Decision** — verify dialog: Title, Description, Rationale, Status, Impact, Impact Description, Owner (SearchableSelect), Meeting Link, Date.
4. Fill in title, description, select Proposed. Click Add — verify toast.
5. Verify card: title, status badge, impact badge, owner, date, linked meeting.
6. Click card to expand — verify description, rationale, impact description.
7. Click **pencil icon** — verify pre-populated edit dialog. Change status to Approved — save — verify badge updates.
8. Click **trash icon** — verify removed.
9. Create decision from meeting action capture — verify meeting name on decision card.

#### Toast Notifications
1. Verify toasts on all save/create/error actions across all tabs.
2. Verify green = success, red = error, auto-dismiss 5s, X for manual dismiss.

---

### Wave E — Portfolio, Financials, Baselines, Roadmap

#### Prioritization Page (FEAT-PORT-001)
1. Navigate to Analytics > Prioritization.
2. Verify ranked list sorted by composite score (highest first).
3. Verify columns: rank, project name, total score, 5 factor scores.
4. Verify "Must Have" projects score higher than "Nice to Have".
5. Click row — verify navigation to project detail.

#### Scenario Comparison (FEAT-PORT-002)
1. Navigate to Analytics > Scenarios.
2. Verify all active projects ranked by score.
3. Enter budget cap — verify projects exceeding cumulative budget show as "OUT" with strikethrough.
4. Enter capacity cap — verify constraint applies cumulatively.
5. Clear both — verify all "IN".
6. Verify summary: "X/Y projects fit constraints | Total budget: $Z".

#### Financials Page (FEAT-FIN-001/002)
1. Navigate to Analytics > Financials.
2. Verify 5 summary cards: Total Budget, Forecast, Actual, Variance (green/red), Benefits.
3. Verify per-project rows: Budget, Forecast, Actual, Variance, Benefits.
4. Projects without data show dashes.
5. Click row — verify navigation.

#### Baseline Capture (FEAT-CTRL-001)
1. Open project detail. Verify "Capture Baseline" button in header.
2. Click — verify toast "Baseline captured".
3. Click again — verify second baseline created.

#### Variance Page (FEAT-CTRL-002)
1. Navigate to Analytics > Variance.
2. No baselines — verify empty state with guidance.
3. With baselines — verify table: Project, Baseline date, Schedule variance (days, arrows), Budget variance ($, colored), Effort variance (hours).
4. Click row — verify navigation.

#### Roadmap Page (FEAT-ROAD-001/002)
1. Navigate to Analytics > Roadmap.
2. Verify projects grouped by program with timeline bars.
3. Verify health badges per project.
4. Verify "Unassigned" group for unlinked projects.
5. **Schedule Overlaps:** If same-program projects overlap, verify entries with day count and risk color.
6. Click row — verify navigation.

#### Sidebar Navigation
1. Verify all analytics links: Overview, By Team, Pipeline, Health Matrix, Governance, Capacity, Prioritization, Financials, Scenarios, Variance, Roadmap.

---

### Wave F — Lifecycle Workspace Upgrades

Wave F replaced the generic CRUD tabs with structured lifecycle workspaces. These tests verify the upgraded behavior beyond what Waves C–D originally tested.

#### Initiation — upgraded
1. Verify 7-dimension pill bar (was 3-section passive display).
2. Verify each dimension expands with inline actions (was read-only).
3. Verify artifact category filtering: change project category → artifact list changes.
4. Verify artifact status updates inline (Complete/In Progress/Waive) without modal.

#### Gates — upgraded
1. Verify horizontal timeline progression bar (was flat card list).
2. Verify active gate card with readiness conditions (was instant approve/reject).
3. Verify approval requires rationale text (was instant click with no notes).
4. Verify decision history accordion shows who/when/why (was not visible).

#### Decisions — upgraded
1. Verify full metadata: impact badge, owner, meeting link, rationale (was title/status only).
2. Verify edit capability via pencil icon (was create/delete only).
3. Verify meeting linkage from action capture.
4. Verify impact description field visible when impact is set.

#### Documents — upgraded
1. Verify Library/Category view toggle (was flat link list).
2. Verify SharePoint folder browsing with breadcrumbs (was no folder navigation).
3. Verify drag-and-drop upload zone (was no upload).
4. Verify required artifact readiness overlay (was not on documents tab).
5. Verify Documents tab does NOT contain meetings (was mixed in CommunicationsHub).

#### Meetings — new tab
1. Verify Meetings is a **separate tab** from Documents.
2. Verify Schedule Meeting dialog with date/time/location/agenda/Teams checkbox.
3. Verify Graph Calendar integration attempt with graceful fallback.
4. Verify meeting expand: attendees, agenda, summary, action capture, linked decisions.
5. Verify upcoming/past split.

#### Closeout — upgraded
1. Verify 5-dimension readiness banner (was done/total counter only).
2. Verify lessons learned and outcome summary in dedicated sections (was on first checklist item).
3. Verify archive button with readiness gate (was not present).
4. Verify archive confirmation dialog and project deactivation.
