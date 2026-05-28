### Project: PMO CFR Solution
PlanType: ImplementationPlan
Status: Active
Authority: This document
Standards: corp-fin-bi-standards (multi-root workspace, always open)
Publisher: Business Intelligence / prefix `pmo_` (approved PMO boundary exception)
Revised: 2026-04-21

---

## PMO CFR Solution — Implementation Plan

Single execution authority for all PMO CFR Solution work. Supersedes all prior planning artifacts.

### Scope & Objectives

The CFR Project Management application is the unified PMO surface for Coram Finance RevCycle. Users should not leave the app for normal project work. The app consolidates:

- Guided project and program onboarding with template-driven initialization
- Project request intake with AI-assisted triage routing
- Project and program lifecycle management with shared multi-team execution
- Full in-app task management with Planner parity
- In-app document management with SharePoint-integrated library experience
- In-app meeting management with Graph-integrated scheduling
- Lifecycle governance through configured gate sets and readiness rules
- Governed decision log linked to project, program, and meeting context
- Structured initiation and closeout workspaces
- AI-powered contextual advisory through Mira
- Portfolio health analytics and PMO administration

### Locked Decisions

#### Automation Model
- All work is agent-executable unless a real platform limitation exists
- No human-dependency language, approval checkpoints, or "confirm/evaluate later" phrasing
- All tenant, admin, and deployment access needed for approved work is available

#### Product Control Model
- The PMO app is the primary command-center experience — users do not leave the app for normal work
- New capabilities deepen the in-app experience rather than redirect users to external tools
- Existing tables are extended first; add new tables only where the lifecycle object is materially distinct
- Projects are collaborative by design — the multi-team model (`pmo_projectteam` junction with Primary/Contributing roles) is implemented and is the default execution pattern

#### Project Template Hierarchy
Precedence (highest to lowest):
1. User-selected template during onboarding
2. Team default template from the project's Primary Team (stored in `pmo_appsettings` via `pmo.team_default_template.{teamId}`)
3. System default template from `pmo_appsettings` (`pmo.default_project_template_id`)
4. Category fallback from `projectTemplates.ts`

Template application creates WBS tasks via `applyProjectTemplate()` in `schedulingClient.ts`. Every project gets a template applied.

#### Teams Strategy
Selected: **Meeting Integration** — in-app scheduling, meeting prep, contextual side panel, action capture, summary integration via Microsoft Graph Calendar API.

#### Document Management Strategy
Selected: **SharePoint-Integrated In-App Library** — SharePoint as storage substrate accessed through SharePoint REST API. PMO app provides inline browsing, drag-and-drop upload, categorized views, and required artifact readiness overlay. Users work with documents inside the app.

#### Notification Strategy
Selected: **Hybrid** — ephemeral toasts for immediate feedback, durable in-app notification center for actionable PM signals.

### Agent Execution Rules

1. Do not ask for clarification where this plan has already made a decision
2. Do not add "human required" language unless a real technical platform blocker exists
3. Do not leave narrative TODOs in place of implementation decisions
4. Every feature must include: objective, scope, UI definition, schema impact, file paths, dependencies, acceptance criteria, automated validation
5. Reuse existing schema and components first
6. If a new table is required, document purpose, ownership model, and column structure
7. All Dataverse schema creation follows `dataverse-agent-behavior-standard.md`
8. All new tables use `pmo_` prefix within this solution boundary
9. All code changes follow: `npx tsc -b --noEmit` → `npm run build` → `npx power-apps push`
10. Multi-team execution is the default — never design features that assume single-team ownership

### Validated Current State

All items below are complete and deployed.

#### Core Platform ✅
- PSS API validation, persistence lag calibration (~20–22s), PSS wrappers in `schedulingClient.ts`
- In-app task workspace: Kanban board, WBS hierarchy, bucket/task CRUD, optimistic UI
- Program oversight signals, WBS task template definitions, F2S dependency management
- Team member lifecycle, resource assignment, per-task assignment management
- Planner parity: detail panel, search, filter bar, group-by, list view, charts, people/workload, labels, checklist, sprint
- Mira AI: advisory engine, Copilot Studio deployment, context loaders, contracts, panel, mutation framework, telemetry sink
- Intake: conversational intake, routing, confidence scoring, list/detail/triage, conversion flow, submission notification
- Project & program detail pages, status reporting, risk/issue/change tracking (Accelerator entities)
- Multi-team model: `pmo_projectteam` junction with Primary (893460040) / Contributing (893460041) roles, team CRUD on ProjectDetailPage
- Analytics: portfolio health, intake pipeline, by-team, schedule, routing QA
- Admin settings with `pmo_appsettings` key-value store

#### Onboarding & Templates ✅
- `pmo_projecttemplate` table with name, description, cfrcategory, taskpayload (JSON), issystemdefault
- Template CRUD in Admin Settings with JSON task editor and category prefill
- Team default template via namespaced `pmo_appsettings` keys (no schema change to `team` entity)
- System default template setting in Admin Settings
- 6-step Project Onboarding Wizard: Basics → Ownership → Template → Team → Classification → Review
- 3-step Program Onboarding Wizard: Basics → Ownership → Review
- Intake-to-Project conversion with prefilled wizard
- Template precedence: Selected > Team Default > System Default > Category Fallback

#### Data Layer (schema + models + APIs + hooks) ✅
All Dataverse tables exist in DEV, registered in `ENTITY_SETS`, `DATAVERSE_SOURCES`, and `power.config.json`:
- `pmo_projecttemplate`, `pmo_documentlink`, `pmo_projectgate`, `pmo_projectgatedecision`
- `pmo_requiredartifact`, `pmo_projectartifactstatus`, `pmo_projectcloseout`
- `pmo_notification`, `pmo_telemetryevent`, `pmo_projectdecision`, `pmo_projectmeetinglink`, `pmo_projectbaseline`

TypeScript models, OData API functions, and TanStack Query hooks exist for all tables. Toast service and notification center are deployed.

#### Analytics Pages ✅
- Governance dashboard, Capacity planning, Prioritization scoring, Scenario comparison, Financials, Variance reporting, Portfolio roadmap with cross-project dependency visibility
- All pages routed and in sidebar navigation

---

## Remaining Work — Lifecycle Workspace Upgrades

The following features replace the current generic CRUD tab implementations with structured lifecycle workspaces. Existing Dataverse tables, models, APIs, and hooks are reused — the work is primarily component-level UI redesign with targeted schema extensions where the current model is insufficient.

---

## FEAT-INIT-100 — Initiation Workspace

**Objective:** Replace the passive read-only InitiationWorkspace with a guided startup workspace that actively drives project readiness across all initiation dimensions.

**Purpose in lifecycle:** The Initiation tab is the first workspace a PM uses after project creation. It must surface every unresolved startup condition and provide inline actions to resolve them — not just display readiness percentages.

**UI definition — top-level sections:**

1. **Readiness Dashboard** (top card, always visible)
   - Overall readiness percentage bar
   - Per-dimension status pills: Metadata | Ownership | Teams | Governance | Artifacts | Template | Execution Structure
   - Each pill: green (complete), amber (partial), red (missing/blocked)
   - Click any pill to scroll to that section below

2. **Metadata Readiness Card**
   - Shows: project name, description, scheduled start, CFR category, complexity, strategic priority
   - Missing fields highlighted with amber indicator
   - Action: "Edit Project" button opens ProjectEditDialog directly to the relevant tab

3. **Ownership Readiness Card**
   - Shows: PM, Executive Sponsor, Manager — each with name or "Not assigned" in amber
   - Action: "Assign" button per role opens SearchableSelect inline (not a separate dialog)

4. **Team Participation Card**
   - Shows: Primary Team (name + member count), Contributing Teams (list)
   - "No primary team" = red blocker
   - Action: "Set Primary Team" / "Add Contributing Team" inline

5. **Governance Readiness Card**
   - Shows: initiation gate status (if configured), health indicators set/unset
   - Links to Gates tab for gate management
   - Action: "Set Health Indicators" opens edit dialog

6. **Startup Artifacts Card**
   - Shows: required artifacts for this project's CFR category (filtered by `pmo_cfrcategory` match or null = all categories)
   - Per artifact: status icon + name + action button
   - Actions per artifact:
     - "Mark Complete" — sets `pmo_status = Complete`, `pmo_completeddate = today`
     - "Link Document" — opens document picker, sets `pmo_DocumentLink@odata.bind`
     - "Waive" — sets `pmo_status = Waived`
     - "In Progress" — sets `pmo_status = InProgress`
   - If no `pmo_projectartifactstatus` records exist for this project, auto-create them from matching `pmo_requiredartifact` definitions on first render

7. **Template & Execution Card**
   - Shows: which template was applied (name + source: "Team default" / "System default" / "User selected" / "Category fallback")
   - Task count created from template
   - Link to Tasks tab
   - If no tasks exist: amber "No execution structure" with "Apply Template" action

**Schema impact:** None — uses existing tables. Fix: `useArtifactReadiness` hook must filter artifact definitions by project's `pmo_cfrcategory` (currently shows all). Add auto-provisioning of `pmo_projectartifactstatus` records.

**File paths:**
- `app/src/components/projects/InitiationWorkspace.tsx` — full rewrite
- `app/src/hooks/useRequiredArtifacts.ts` — add category filtering, add auto-provision mutation

**Dependencies:** Existing schema

**Acceptance criteria:**
- Every readiness dimension is visible with current state
- Every unresolved condition has an inline action to resolve it
- Artifact statuses are auto-provisioned from category-matched definitions
- Artifact status updates happen inline (no modal)
- Readiness bar reflects all dimensions, not just artifacts

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Open project with missing metadata → verify amber indicators and action buttons
- Mark artifact complete → verify readiness bar updates
- Verify category filtering: project with category X only shows artifacts for category X or null

---

## FEAT-GOV-100 — Governance Gate Workspace

**Objective:** Replace the manual gate-creation tab with a lifecycle governance workspace driven by admin-configured gate sets and readiness rules.

**Purpose in lifecycle:** Gates are governance checkpoints that enforce readiness before a project advances to the next phase. The project UX focuses on gate readiness, conditions, and approvals — not gate definition.

**Admin configuration surface (Admin Settings page):**

1. **Gate Set Templates** section in Admin Settings
   - A gate set is a named collection of gate definitions (e.g., "Standard Lifecycle", "Compliance-Heavy")
   - Each gate set contains ordered gates with: name, type (Initiation/Planning/Execution/Closeout), order, default readiness conditions
   - Admin can create/edit/deactivate gate sets
   - Gate sets can be associated to CFR categories or used as a system default

2. **Auto-provisioning:** When a project is created via the onboarding wizard, the matching gate set is instantiated as `pmo_projectgate` records for that project (similar to artifact auto-provisioning)

**Project UI definition — Gates tab:**

1. **Gate Timeline** (top section, always visible)
   - Horizontal progression bar showing all gates in order
   - Each gate node: colored by status (grey=not started, blue=in progress, green=passed, red=failed, muted=waived)
   - Current active gate highlighted

2. **Active Gate Card** (expanded view of the current/next unpassed gate)
   - Gate name, type, order, owner, target date, due status (on-time / overdue)
   - **Readiness Conditions** checklist:
     - Predecessor gate passed (auto-computed)
     - Required artifacts for this phase complete (cross-referenced from `pmo_projectartifactstatus`)
     - Custom conditions (from gate notes/configuration)
   - **Blockers** section: any unmet readiness condition displayed as a red blocker with link to resolve
   - **Approval Actions:**
     - "Approve" button → opens inline approval form with: rationale (required textarea), notes (optional), decision date (defaults today)
     - "Reject" button → opens inline rejection form with: reason (required textarea)
     - "Defer" button → sets gate to deferred with reason
     - All decisions create `pmo_projectgatedecision` records with notes/rationale
   - **Decision History** accordion: shows all decisions for this gate (who, when, decision, rationale)

3. **All Gates List** (below active gate)
   - Collapsible cards per gate with summary: name, type, status badge, owner, target date
   - Expand any gate to see its readiness conditions and decision history

**Schema impact:**
- New table: `pmo_gatesettemplate` — admin gate set definitions (name, description, cfrcategory, isdefault)
- New table: `pmo_gatesetitem` — items within a gate set (name, gatetype, gateorder, conditions JSON)
- Extend `pmo_projectgate`: add `pmo_rationale` (Memo) column for approval/rejection rationale on the gate itself
- Extend `pmo_projectgatedecision`: `pmo_notes` already exists — ensure it is exposed in UI as rationale

**File paths:**
- `app/src/pages/Projects/ProjectDetailPage.tsx` — rewrite Gates TabsContent
- `app/src/components/projects/GateWorkspace.tsx` — new component
- `app/src/pages/Admin/AdminSettingsPage.tsx` — add Gate Set Templates section
- `app/src/models/gateSetTemplate.model.ts` — new
- `app/src/api/gateSetTemplates.api.ts` — new
- `app/src/hooks/useGateSetTemplates.ts` — new
- `app/src/hooks/useProjectGates.ts` — extend with readiness computation

**Admin-configurable:** Gate set templates (name, ordered gates, conditions, category association)

**Dependencies:** FEAT-INIT-100 (artifact readiness feeds gate conditions)

**Acceptance criteria:**
- Gates auto-provisioned from gate set when project is created
- Gate readiness shows predecessor gate status and artifact completion
- Approval captures rationale (not instant click)
- Decision history visible per gate
- Admin can define gate set templates by category
- Gate timeline renders horizontal progression

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Create project → verify gates auto-provisioned from matching gate set
- Approve gate with rationale → verify decision record created with notes
- Verify readiness: block approval when predecessor gate not passed

---

## FEAT-DEC-100 — Decision Log Workspace

**Objective:** Replace the thin create/delete modal with a governed decision log workspace showing structured metadata, edit capability, and meeting context linkage.

**Purpose in lifecycle:** Decisions are distinct lifecycle objects capturing what was decided, by whom, when, why, and what impact it has. They link to meetings and inform governance.

**UI definition — Decisions tab:**

1. **Decision List** (default view)
   - Sortable/filterable table or card list
   - Per decision: title, status badge (Proposed/Approved/Rejected/Deferred), impact badge (High/Medium/Low), owner name, decision date, linked meeting (if any)
   - Click to expand inline detail view

2. **Decision Detail** (inline expandable, not a separate page)
   - Full description with markdown-safe rendering
   - Rationale field (why this decision was made)
   - Impact assessment (High/Medium/Low + impact description text)
   - Decision owner (resolved name)
   - Linked meeting (clickable, shows meeting subject + date)
   - Linked program (if applicable)
   - Decision history: created date, status changes
   - Edit button opens inline edit mode (not a modal) for all fields

3. **Add Decision** (slide-out panel or inline form, not a minimal modal)
   - Fields: Title (required), Description (required), Rationale (textarea), Status (select), Impact (select), Impact Description (textarea), Owner (SearchableSelect), Meeting Link (select from project meetings), Date (defaults today, editable)

**Schema impact:**
- Extend `pmo_projectdecision`: add `pmo_rationale` (Memo), `pmo_impactdescription` (Memo)
- Existing fields to expose in UI: `pmo_impact`, `_pmo_decisionowner_value`, `_pmo_meetinglink_value` (all exist in model, not in current UI)

**File paths:**
- `app/src/pages/Projects/ProjectDetailPage.tsx` — rewrite Decisions TabsContent
- `app/src/components/projects/DecisionWorkspace.tsx` — new component
- `app/src/models/projectDecision.model.ts` — extend with rationale, impactdescription
- `app/src/hooks/useProjectDecisions.ts` — add update mutation (currently missing edit)

**Dependencies:** FEAT-MTG-100 (meeting link selection requires meeting data)

**Acceptance criteria:**
- All model fields exposed in UI (impact, owner, meeting link, rationale)
- Edit capability exists (not just create/delete)
- Decision cards show full structured metadata
- Meeting linkage is visible and clickable
- MeetingActionCapture component wired into meeting cards to create decisions from meeting context

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Create decision with all fields → verify all display correctly
- Edit decision → verify changes persist
- Create decision from meeting action capture → verify meeting link set

---

## FEAT-DOC-100 — In-App Document Library

**Objective:** Replace the flat document link list with a SharePoint-integrated in-app document library experience. Users browse, upload, and manage documents without leaving the PMO app.

**Purpose in lifecycle:** Documents are the artifacts that prove work — charters, SOWs, budgets, status reports. The document hub must behave like a SharePoint library inside the app, not a list of external links.

**UI definition — Documents tab:**

1. **Library Browser** (primary section)
   - Renders SharePoint folder/file tree for the project's document library via SharePoint REST API (`/_api/web/GetFolderByServerRelativeUrl`)
   - Folder navigation with breadcrumb trail
   - File list with columns: Name, Type icon, Modified date, Modified by, Size
   - Click file → opens in SharePoint Online viewer (new tab) or downloads
   - Click folder → navigates into folder

2. **Upload Zone** (top of library browser)
   - Drag-and-drop zone accepting files
   - "Upload" button as alternative
   - Uploads via SharePoint REST API (`/_api/web/GetFolderByServerRelativeUrl/Files/add`)
   - Creates corresponding `pmo_documentlink` metadata record automatically
   - Progress indicator during upload

3. **Categorized View** (toggle between Library and Category views)
   - Groups documents by `pmo_category` (Charter, SOW, Budget, Status Report, Meeting Notes, Other)
   - Each category section: collapsed by default, shows count badge, expand to see files
   - "Uncategorized" section for documents without category

4. **Required Artifacts Overlay** (sidebar or top banner)
   - Shows required artifacts for this project's category
   - Per artifact: status (Complete/In Progress/Not Started/Waived), linked document (if any)
   - "Link Document" action connects an artifact status record to a document in the library
   - Visual: green check for complete, amber circle for in progress, red dot for not started

5. **Recent/Key Documents** (quick-access section)
   - Last 5 modified documents
   - Pinned/key documents (documents linked to required artifacts)

6. **New Document Actions**
   - "Link External Document" — manual URL entry (existing flow, retained)
   - "Upload Document" — drag-and-drop or file picker
   - "Create Folder" — creates subfolder in SharePoint library

**Schema impact:**
- Extend `pmo_documentlink`: add `pmo_sharepointitemid` (String, nullable — SharePoint item ID for uploaded files), `pmo_filesize` (Integer, nullable), `pmo_modifiedby` (String, nullable)
- No new tables — `pmo_documentlink` is the metadata layer on top of SharePoint storage

**Technical implementation:**
- `app/src/lib/sharePointClient.ts` — SharePoint REST API wrapper (list folders, list files, upload file, create folder, get file metadata)
- SharePoint REST API authentication: uses the same OAuth token from the Power Apps host (delegated user context)
- Project document library path convention: `{siteUrl}/Shared Documents/Projects/{projectName}` — auto-created on first upload if not exists

**File paths:**
- `app/src/pages/Projects/ProjectDetailPage.tsx` — rewrite Documents TabsContent
- `app/src/components/projects/DocumentLibrary.tsx` — new component (library browser)
- `app/src/components/projects/DocumentUploadZone.tsx` — new component (drag-and-drop)
- `app/src/components/projects/ArtifactReadinessOverlay.tsx` — new component
- `app/src/lib/sharePointClient.ts` — extend with folder/file operations
- `app/src/hooks/useSharePointLibrary.ts` — new hook for library content queries

**Admin-configurable:** Document category option set values (already in schema as `pmo_category` picklist)

**Dependencies:** None (SharePoint REST API available in Power Apps host context)

**Acceptance criteria:**
- Users can browse project document folders inline without leaving the app
- Drag-and-drop upload creates file in SharePoint and metadata record in Dataverse
- Category view groups documents by type
- Required artifact overlay shows completion status with link-to-document action
- Breadcrumb navigation works for folder hierarchy
- Meetings tab is NOT part of Documents — it is a separate tab

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Upload file → verify it appears in SharePoint library and in categorized view
- Link document to artifact → verify artifact readiness updates
- Navigate folders → verify breadcrumb updates

---

## FEAT-MTG-100 — In-App Meeting Management Workspace

**Objective:** Replace meeting link cards with a full in-app meeting management workspace using Microsoft Graph Calendar API. Users schedule, manage, and capture meeting outcomes without leaving the PMO app.

**Purpose in lifecycle:** Meetings drive decisions and actions. The meeting workspace provides Outlook-like scheduling, attendee management, and structured action capture — all linked to project context.

**UI definition — Meetings tab (distinct from Documents):**

1. **Meeting Calendar View** (primary section)
   - Month/week/agenda toggle (agenda is default for project context)
   - Shows all meetings linked to this project
   - Each meeting entry: subject, date/time, duration, attendee count, Teams link icon
   - Click meeting → expands inline detail panel

2. **Schedule Meeting** (primary action button)
   - Opens scheduling form (slide-out panel):
     - Subject (required)
     - Date + Start Time + End Time (datetime pickers)
     - Location (text, optional — auto-fills with Teams meeting if "Add Teams link" checked)
     - Attendees (multi-select SearchableSelect from project team members + free-text email entry)
     - "Suggest Team Members" — pre-populates attendees from project PM, sponsor, manager, and contributing team members
     - Agenda / Notes (textarea)
     - "Add Teams Link" checkbox — creates online meeting via Graph
   - On save: creates calendar event via Microsoft Graph Calendar API (`POST /me/events`), creates `pmo_projectmeetinglink` record with event ID, subject, datetime, attendees JSON, Teams URL

3. **Meeting Detail Panel** (inline expandable)
   - Subject, date/time, location, Teams join link
   - Attendee list with names and response status (accepted/tentative/declined — from Graph)
   - Agenda / prep notes
   - **Action Capture Section:**
     - "Capture Action" button per meeting
     - Action form: action text, type (Decision / Task / Risk / Issue), assignee
     - Creates the corresponding PMO record (`pmo_projectdecision`, `msdyn_projecttask` via PSS, `msdyn_projectrisk`, `msdyn_projectissue`) with meeting link reference
   - **Meeting Summary** section: editable textarea for post-meeting summary (stored in `pmo_notes` on meeting link record)
   - **Actions Taken** section: list of decisions/tasks/risks/issues created from this meeting (queried by `_pmo_meetinglink_value`)

4. **Edit / Reschedule Meeting**
   - From meeting detail panel: "Edit" button opens scheduling form pre-populated
   - Updates via Graph API (`PATCH /me/events/{eventId}`)
   - Updates `pmo_projectmeetinglink` record

5. **Upcoming / Past Toggle**
   - Default: upcoming meetings first
   - Past meetings section: collapsed, shows last 10

**Schema impact:**
- Extend `pmo_projectmeetinglink`: add `pmo_grapheventid` (String — Graph event ID for API operations), `pmo_attendeesjson` (Memo — JSON array of attendee email/name/response), `pmo_duration` (Integer — minutes), `pmo_location` (String), `pmo_summary` (Memo — post-meeting summary), `pmo_agendanotes` (Memo — pre-meeting agenda)
- Extend `pmo_projectdecision`: `_pmo_meetinglink_value` already exists — no change needed
- Extend `msdyn_projectrisk`, `msdyn_projectissue`: add `pmo_MeetingSource` lookup to `pmo_projectmeetinglink` (optional — for traceability of meeting-originated items)

**Technical implementation:**
- `app/src/lib/graphClient.ts` — new Microsoft Graph API wrapper (create event, update event, list events, get event details, get attendee responses)
- Graph API authentication: uses the same OAuth token from Power Apps host with Calendar.ReadWrite scope
- If Calendar.ReadWrite scope is not available in the current host context, fall back to manual meeting entry (existing pattern) with a "Graph not available" indicator

**File paths:**
- `app/src/pages/Projects/ProjectDetailPage.tsx` — add Meetings tab (separate from Documents)
- `app/src/components/projects/MeetingWorkspace.tsx` — new component
- `app/src/components/projects/MeetingScheduleForm.tsx` — new component
- `app/src/components/projects/MeetingDetailPanel.tsx` — new component
- `app/src/components/projects/MeetingActionCapture.tsx` — rewrite from existing orphaned component
- `app/src/lib/graphClient.ts` — new
- `app/src/hooks/useGraphCalendar.ts` — new hook for Graph Calendar operations
- `app/src/hooks/useProjectMeetingLinks.ts` — extend with Graph event sync

**Dependencies:** None (Graph API available in Power Apps host context; graceful fallback if not)

**Acceptance criteria:**
- Users can schedule meetings from within the PMO app
- Meeting creates a Graph calendar event and a `pmo_projectmeetinglink` record
- Attendee management suggests project team members
- Edit/reschedule updates the Graph event
- Action capture creates the correct PMO record type with meeting link
- Meeting summary is editable and persisted
- Actions originated from a meeting are listed on the meeting detail
- Meetings tab is distinct from Documents tab

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Schedule meeting → verify Graph event created and PMO record created
- Capture action as Decision → verify `pmo_projectdecision` created with meeting link
- Edit meeting → verify Graph event updated

---

## FEAT-CLO-100 — Closeout Workspace

**Objective:** Replace the freeform checklist with a structured closeout workspace that drives closure readiness through required items, artifacts, approvals, lessons learned, and archival disposition.

**Purpose in lifecycle:** Closeout is the governed completion phase. Projects cannot be fully closed until all required closeout conditions are met. The workspace makes closure readiness visible and actionable.

**UI definition — Closeout tab:**

1. **Closeout Readiness Banner** (top, always visible)
   - Overall readiness: percentage bar + "Ready to Close" / "X items remaining"
   - Per-dimension pills: Required Items | Artifacts | Approvals | Lessons Learned | Outcome Summary
   - Each pill: green (complete), amber (partial), red (missing)

2. **Required Completion Items** section
   - Driven by admin-configured closeout checklist templates (similar to gate sets)
   - Auto-provisioned from closeout template when project enters closeout phase
   - Per item: checkbox toggle, item description, completed by (name), completed date
   - Items cannot be manually deleted (only admin can modify the template)
   - Additional custom items can be added by PM

3. **Closeout Artifacts** section
   - Shows required artifacts with `pmo_artifacttype` in closeout category (CloseoutReport, LessonsLearned)
   - Same artifact readiness pattern as Initiation: status icon + link document + mark complete
   - Cross-linked to Documents tab for upload/attachment

4. **Closeout Gate** section
   - Shows the Closeout-type gate from the project's gate set (if configured)
   - Gate readiness conditions: all required items complete, all closeout artifacts complete
   - Approval action (same pattern as gate workspace — with rationale)

5. **Lessons Learned** section
   - Structured text capture stored on a dedicated `pmo_projectcloseout` record with `pmo_checklistitem = '__LESSONS_LEARNED__'` sentinel or on a project-level extension column
   - Rich textarea with prompt: "What went well? What could be improved? What would you do differently?"
   - Auto-saved on blur

6. **Outcome Summary** section
   - Structured text capture: "What was delivered? What is the final state? Who owns ongoing operations?"
   - Auto-saved on blur

7. **Archival Disposition** section
   - Status select: Active → Closing → Archived
   - "Archive Project" action: sets archival state, deactivates project record (`statecode = 1`)
   - Blocked if readiness is not complete (all required items, artifacts, gate)
   - Confirmation dialog before archival

**Schema impact:**
- Add `pmo_archivalstate` (Choice: Active/Closing/Archived) to `msdyn_project` via `pmo_` extension column
- Move lessons learned and outcome summary from `pmo_projectcloseout[0]` to dedicated columns: `pmo_lessonslearned` and `pmo_outcomesummary` on `msdyn_project` (or keep on a single "closeout summary" record with a known sentinel key — either approach works, but storing on the project avoids the fragile `[0]` indexing)
- New table: `pmo_closeouttemplate` — admin closeout item definitions (name, description, isdefault, cfrcategory)
- Or reuse `pmo_requiredartifact` with a phase/stage discriminator column — evaluate simplicity vs clarity

**File paths:**
- `app/src/pages/Projects/ProjectDetailPage.tsx` — rewrite Closeout TabsContent
- `app/src/components/projects/CloseoutWorkspace.tsx` — new component
- `app/src/pages/Admin/AdminSettingsPage.tsx` — add Closeout Template section (if separate table)
- `app/src/hooks/useProjectCloseout.ts` — extend with readiness dimensions
- `app/src/models/projectCloseout.model.ts` — extend if needed

**Admin-configurable:** Closeout checklist template items (name, description, category association)

**Dependencies:** FEAT-GOV-100 (closeout gate), FEAT-DOC-100 (closeout artifacts), FEAT-INIT-100 (artifact readiness pattern)

**Acceptance criteria:**
- Closeout readiness banner shows all dimensions
- Required items auto-provisioned from template
- Lessons learned and outcome summary stored reliably (not on first checklist item)
- Archival disposition enforced: cannot archive until readiness is complete
- Closeout gate approval integrates with governance workspace

**Automated validation:**
- `npx tsc -b --noEmit && npm run build` passes
- Complete all required items → verify readiness bar reaches 100%
- Attempt archive with incomplete items → verify blocked
- Save lessons learned → verify persistence across page reload

---

## Retained Features — No Revision Needed

The following features are implemented and require no workspace-level revision:

### Onboarding & Templates
- FEAT-ONBOARD-001 — 6-step Project Onboarding Wizard ✅
- FEAT-ONBOARD-002 — 3-step Program Onboarding Wizard ✅
- FEAT-ONBOARD-003 — Intake Conversion Onboarding ✅
- FEAT-TMPL-001 — Project Template Model ✅
- FEAT-TMPL-002 — Team Default Template (pmo_appsettings) ✅
- FEAT-TMPL-003 — System Default Template Setting ✅

### Analytics & Portfolio
- FEAT-GOV-003 — Governance Dashboard ✅
- FEAT-CAP-001 — Capacity Planning Workspace ✅
- FEAT-CAP-002 — Resource Optimization Recommendations ✅
- FEAT-PORT-001 — Portfolio Prioritization Model ✅
- FEAT-PORT-002 — Scenario Comparison Workspace ✅
- FEAT-FIN-001 — Project Financial Tracking ✅
- FEAT-FIN-002 — Portfolio Cost Visibility ✅
- FEAT-CTRL-001 — Baseline Capture ✅
- FEAT-CTRL-002 — Variance / Trend Reporting ✅
- FEAT-ROAD-001 — Portfolio Roadmap ✅
- FEAT-ROAD-002 — Cross-Project Dependency Visibility ✅

### Infrastructure
- FEAT-AUTO-001 — Plan Normalization ✅
- FEAT-AUTO-002 — CI/CD Pipeline ⏸️ DEFERRED (dfr-017)
- FEAT-AUTO-003 — Schema / Environment Snapshot ✅
- FEAT-DOC-001 — SharePoint Document Service (base layer) ✅
- FEAT-NOTIF-001 — Unified Toast Service ✅
- FEAT-NOTIF-002 — Durable In-App Notification Center ✅
- FEAT-NOTIF-003 — Telemetry-to-Notification Bridge ✅

---

## Tier 4 — Deferred

- Goal linkage (schema not discovered for `msdyn_projectgoal`)
- Timeline / Gantt view (blocked on library selection)
- Drag-and-drop between buckets
- Additional dependency types (FF / SS / SF)
- SPA URL routing / browser refresh state
- Mira open tasks refinement
- Mira "what needs attention" refinement
- True contextual freeform Mira chat
- Teams channel intake

### Permanently Blocked / Out of Scope
- Planner-synced task attachments
- Planner-synced task comments / conversation
- PMO-native chat as messaging system
- Dataverse file storage for project documents
- Team-per-program / channel-per-project automation

---

## Delivery Sequence

### Wave F — Lifecycle Workspace Upgrades
Execute in dependency order:

1. FEAT-INIT-100 (Initiation Workspace) — no external dependencies
2. FEAT-GOV-100 (Governance Gate Workspace) — depends on FEAT-INIT-100
3. FEAT-DEC-100 (Decision Log Workspace) — depends on FEAT-MTG-100
4. FEAT-DOC-100 (In-App Document Library) — no external dependencies
5. FEAT-MTG-100 (In-App Meeting Management) — no external dependencies
6. FEAT-CLO-100 (Closeout Workspace) — depends on FEAT-GOV-100, FEAT-DOC-100, FEAT-INIT-100

Parallelizable: FEAT-INIT-100, FEAT-DOC-100, and FEAT-MTG-100 can execute in parallel. FEAT-GOV-100 follows FEAT-INIT-100. FEAT-DEC-100 follows FEAT-MTG-100. FEAT-CLO-100 follows all others.

**Wave gate:** `npx tsc -b --noEmit && npm run build` passes. `npx power-apps push` deploys to DEV. Manual validation: each workspace renders with correct sections, actions work, readiness computation is accurate.

---

## Technical Architecture Reference

### Mandatory Build Sequence
```bash
cd app
npx tsc -b --noEmit
npm run build
npx power-apps push
```

### Key Entry Points
- `app/src/pages/Projects/ProjectDetailPage.tsx` — tab shell for all workspaces
- `app/src/components/projects/` — workspace components
- `app/src/lib/sharePointClient.ts` — SharePoint REST API
- `app/src/lib/graphClient.ts` — Microsoft Graph Calendar API
- `app/src/lib/schedulingClient.ts` — PSS client
- `app/src/lib/dataverseClient.ts` — Dataverse SDK wrapper
- `app/src/lib/constants.ts` — entity sets, option sets, settings keys
- `app/src/hooks/` — TanStack Query hooks
- `app/src/models/` — TypeScript entity interfaces
- `app/src/api/` — OData API functions

### Multi-Team Execution Model (Implemented)
- Primary Team via `pmo_PrimaryTeam@odata.bind` on `msdyn_project`
- Contributing Teams via `pmo_projectteam` junction with `TEAM_ROLE.Contributing`
- Onboarding wizard initializes both in a single create flow
- All project data is project-scoped, not team-scoped — cross-team visibility by default
- `PMO_TEAM_FLAG` (`cr741_pmoteam` in DEV → `pmo_pmoteam` in UAT/PROD) filters team dropdowns

### Governance
- Standards authority: `corp-fin-bi-standards` (live, always open in workspace)
- Publisher prefix: `pmo_` within this solution boundary
- All Dataverse schema creation follows `dataverse-agent-behavior-standard.md`
- All code app operations follow `power-apps-code-app-operating-standard.md`
- No direct commits to `main`

### Final Rule for Agents
This document is the execution authority. Do not reinterpret it as a research brief. Do not ask for architectural choices already made here. Produce implementation steps that assume autopilot execution, preserve the PMO app as the primary command center, and implement the workspaces as defined above. Each workspace must be a structured operational experience — not a CRUD tab with a modal.
