# CFR PMO Core App End-User Testing Plan

## 1. Executive Summary

This plan defines end-user testing for all currently implemented core experience surfaces in the CFR PMO app.

Scope is anchored to implemented routes, pages, and workflows in the app runtime, with emphasis on:
- Intake queue and governed intake progression
- **Project creation** (6-step wizard) and project lifecycle management
- **Program creation** (3-step wizard) and program lifecycle management
- **Core record creation workflows:** Task, Risk, Issue, Change Request, Status Report, Decision, and Gate Decision approval
- Task workspace (board, list, people, charts, timeline) and dependencies
- Document library operations and deep-link behavior
- Role gating and admin configuration
- Analytics, teams, and cross-functional operations

Primary objective: validate that all 9 core PMO record types can be created, edited, and managed reliably and safely; intake-to-project-to-execution path is fully functional; and all governance gates and workflows work as designed.

## 2. Evidence Base (Implemented Surface)

Primary implementation anchors reviewed:
- app/src/App.tsx (29 routes)
- app/src/pages/Intake/IntakeListPage.tsx, IntakeDetailPage.tsx, GovernedIntakeWizard.tsx
- app/src/pages/Projects/ProjectListPage.tsx, ProjectDetailPage.tsx, ProjectOnboardingWizard.tsx
- app/src/pages/Programs/ProgramListPage.tsx, ProgramDetailPage.tsx, ProgramOnboardingWizard.tsx
- app/src/components/scheduling/TaskWorkspace.tsx, TaskTimelineView.tsx, CreateTaskDialog.tsx
- app/src/pages/Projects/ProjectDetailPage.tsx (RiskFormDialog, IssueFormDialog, ChangeFormDialog, StatusReportFormDialog)
- app/src/components/projects/DecisionWorkspace.tsx
- app/src/components/projects/GateWorkspace.tsx
- app/src/pages/StatusReports/StatusReportListPage.tsx
- app/src/pages/Analytics/AnalyticsHubPage.tsx
- app/src/pages/Admin/AdminSettingsPage.tsx
- app/src/pages/Teams/TeamsPage.tsx
- README.md and docs/planning/deferred-feature-registry.json

All 9 core record types confirmed as implemented and fully wired to Dataverse/PSS backends.

## 3. Assumptions and Exclusions

### 3.1 Assumptions

- Test environment is connected to Dataverse and Project Scheduling Service (PSS).
- Required seed data exists for at least one active project, one active program, and multiple intake records.
- A test user matrix is available:
  - Requester (non-admin)
  - PMO Analyst (triage permissions)
  - Project Manager (project/task permissions)
  - Admin (pmo_admin scope)
- SharePoint integration and custom upload API are available in target environment.

### 3.2 Out of Scope for Core UAT (unless explicit regression impact)

- Deferred or blocked items listed in docs/planning/deferred-feature-registry.json and README known limitations, including:
  - Goal linkage (dfr-003)
  - Teams channel intake via Copilot Studio (blocked)
  - Remaining Mira freeform/context refinement workstreams
- Planner-premium attachment/comment parity explicitly documented as unsupported.
- CI pipeline behavior (this plan targets end-user runtime behavior).

### 3.3 Known Partial Areas (test with expectation of current behavior)

- Mira mutation pathways should create request records through current handlers; failures should emit mutation telemetry and user-safe outcomes.
- Some governance and analytics pages are data-driven summaries and should be validated for correctness and navigation, not advanced predictive behavior.

## 4. Personas and High-Value Journeys

| Persona | Core Goals | Must-Work Journeys |
| --- | --- | --- |
| Requester | Submit and track intake requests | Create request, upload attachment, submit, respond to clarification |
| PMO Analyst | Triage and route work correctly | Intake queue filtering, confidence review, route, approve/reject/clarify |
| Project Manager | Run project execution lifecycle | Edit project details, manage tasks, dependencies, risks/issues/changes, status report |
| Program Manager | Manage cross-project outcomes | Program updates, project rollup visibility, document operations |
| PMO Admin | Configure operational behavior safely | App settings, workflow/stage config, templates/artifacts, team default templates |

## 5. Coverage Matrix (Feature Area to Page/Component)

| Feature Area | Primary UI Surface | Priority | Coverage Target |
| --- | --- | --- | --- |
| Routing and shell | app/src/App.tsx | P0 | Route access, redirects, 404 behavior, admin route gate |
| Dashboard | app/src/pages/Dashboard/DashboardPage.tsx | P1 | KPI accuracy, drill-through navigation |
| Intake queue and detail | app/src/pages/Intake/IntakeListPage.tsx, app/src/pages/Intake/IntakeDetailPage.tsx | P0 | Full intake lifecycle and state transitions |
| Governed intake stage flow | app/src/pages/Intake/GovernedIntakeWizard.tsx, components/intake/* | P0 | Stage validation, approvals, clarification loop |
| Project creation (ProjectOnboardingWizard) | app/src/pages/Projects/ProjectOnboardingWizard.tsx | P0 | Multi-step project creation, team assignment, template bootstrapping, end-to-end intake-to-project conversion |
| Project detail lifecycle | app/src/pages/Projects/ProjectDetailPage.tsx | P0 | Core project edits, monitor/plan/govern tabs |
| Program creation (ProgramOnboardingWizard) | app/src/pages/Programs/ProgramOnboardingWizard.tsx | P0 | Multi-step program creation, manager assignment, program metadata |
| Program detail lifecycle | app/src/pages/Programs/ProgramDetailPage.tsx | P1 | Program edits, health, governance, financial tracking, project rollup |
| Risk management | app/src/pages/Projects/ProjectDetailPage.tsx (RiskFormDialog) | P0 | Risk creation, impact/probability scoring, mitigation planning, state tracking |
| Issue management | app/src/pages/Projects/ProjectDetailPage.tsx (IssueFormDialog) | P0 | Issue creation, priority tracking, resolution workflow, state management |
| Change management | app/src/pages/Projects/ProjectDetailPage.tsx (ChangeFormDialog) | P0 | Change request creation, impact/cost analysis, benefits tracking, approval workflow |
| Status reporting | app/src/pages/Projects/ProjectDetailPage.tsx, StatusReportListPage.tsx | P0 | Report creation, cross-project visibility, narrative tracking, timeline auditing |
| Decision management | app/src/components/projects/DecisionWorkspace.tsx | P0 | Decision creation, impact assessment, rationale capture, audit trail |
| Gate approval workflow | app/src/components/projects/GateWorkspace.tsx | P0 | Gate decision approval (Approve/Reject/Defer), readiness validation, governance gating |
| Task workspace | app/src/components/scheduling/TaskWorkspace.tsx and related components | P0 | Task CRUD, assignment, dependencies, labels, checklists, views |
| Timeline view | app/src/components/scheduling/TaskTimelineView.tsx | P1 | Date bar rendering and dependency line coherence |
| Status reports hub | app/src/pages/StatusReports/StatusReportListPage.tsx | P1 | Report listing, search, navigation to project |
| Analytics hub/pages | app/src/pages/Analytics/* | P1 | Data aggregation consistency and navigation |
| Teams page | app/src/pages/Teams/TeamsPage.tsx | P1 | Team membership visibility, template assignment controls |
| Admin settings | app/src/pages/Admin/AdminSettingsPage.tsx | P0 | Critical settings write/read, template/artifact management |
| Documents | app/src/components/projects/DocumentLibrary.tsx | P0 | Upload/list/link/delete and ownership filtering |
| Mira mutation entry points | app/src/ai/mutations.ts | P1 | Confirmed write path behavior and failure handling |

## 6. Detailed End-User Scenarios

Priority scale: P0 critical, P1 high, P2 medium.
Type: Smoke, Regression, Functional, Negative, Cross-functional.

| ID | Workflow | Objective | Preconditions | Steps | Expected Result | Priority | Type |
| --- | --- | --- | --- | --- | --- | --- | --- |
| UAT-001 | App shell and default route | Validate app boot and default redirect | User authenticated; app loads | Open root app URL | User lands on Dashboard route; no blocking error | P0 | Smoke |
| UAT-002 | Admin route gating | Verify non-admin cannot access admin pages | Non-admin user session | Navigate to admin/settings and admin/change-history | User is redirected to dashboard; no admin data exposed | P0 | Negative |
| UAT-003 | Intake queue search/filter | Confirm request discovery and filtering | At least 10 requests with mixed status/priority | Open Intake Queue, search by title/team, filter status and priority | Table narrows correctly; row count and badges align | P0 | Functional |
| UAT-004 | New intake creation with attachments | Validate requester intake creation path | Requester user; optional test files | Open New Request, fill required fields, attach files, proceed to review/open | Draft request created, attachments associated, request detail opens | P0 | Smoke |
| UAT-005 | Submit for review and transition | Validate draft to submitted transition | Existing draft intake request | Open draft request and submit for review | Status changes from Draft to Submitted; action history/state reflects change | P0 | Functional |
| UAT-006 | Clarification cycle | Validate request clarification loop | Submitted/In Triage request | Trigger clarification request, respond as requester, resolve clarification | Status transitions to Awaiting Clarification then back to active flow | P0 | Regression |
| UAT-007 | Intake approval and project conversion path | Validate triage to project lifecycle entry with project wizard | Approved candidate request | Approve request and execute conversion path | Request reaches Converted state; ProjectOnboardingWizard opens with prefilled intake data; name/description are locked | P0 | Regression |
| UAT-007a | Project creation (Basics step) | Validate project basics form and validation | User with project creation access | Open ProjectOnboardingWizard, fill Basics step (name required, description optional, scheduled start optional, CFR category) | Preconditions met; Step 1 indicator shows complete; can proceed to Ownership step | P0 | Functional |
| UAT-007b | Project creation (Ownership step) | Validate project manager/sponsor/team assignment | Basics completed, users available in scope | Fill Ownership step (search and select PM, Sponsor, Primary Team); verify user search filters by scope group | Ownership fields populated; proceed to Template step | P0 | Functional |
| UAT-007c | Project creation (Template and Team steps) | Validate template and team management | Ownership completed, teams and templates exist | Select template (or let team/system default resolve); add primary team; add contributing teams | Primary team persisted with Primary role; contributing teams added and displayed | P0 | Functional |
| UAT-007d | Project creation (Classification and Review steps) | Validate complexity, priority, health, budget fields | Team step completed | Fill Classification (Complexity, Strategic Priority, Health, Budget); review summary | All values display correctly in review; can submit to create | P0 | Functional |
| UAT-007e | Project creation with template and team bootstrapping | Validate end-to-end project creation with template tasks and roles | All wizard steps preconditions met | Complete wizard steps 0-5 and submit | Project created; team records created with correct roles; template tasks applied to project; confirmation toast shown; navigation to project detail | P0 | Smoke |
| UAT-008 | Intake rejection and redirect | Confirm controlled rejection/redirect behavior | Submitted request | Reject request with reason; test redirect action with destination notes | Status/notes persist correctly; queue reflects new terminal/routed state | P1 | Functional |
| UAT-009 | Governed intake stage validation | Verify stage-level required fields and gating | Workflow-backed request with stage config | Progress through stages with missing then valid required fields | Missing fields block progression; valid fields allow stage advance | P0 | Regression |
| UAT-010 | Project summary edit | Validate project core field updates | Existing active project | Edit project metadata, health, financial fields; save | Saved values persist and reload correctly | P0 | Smoke |
| UAT-011 | Project monitor records (risk/issue/change) | Validate monitor tab CRUD | Existing project | Add/edit/delete one risk, one issue, one change | Records persist and update list counts and details | P0 | Regression |
| UAT-012 | Project status report create/update | Validate report authoring from project | Existing project | Create status report, edit narrative fields, save | Report appears in project and in status report list page | P0 | Functional |
| UAT-013 | Task create and edit core fields | Validate task lifecycle edits | Project with task workspace access | Create task; edit name, dates, progress, effort, milestone | Task updates persist and render across selected view | P0 | Smoke |
| UAT-014 | Task dependencies add/remove | Validate dependency management | Multiple tasks in project | Add predecessor link, verify, then remove | Dependency list and visual relationships update correctly | P0 | Regression |
| UAT-015 | Task assignment and people view | Validate assignment mapping and workload view | Team members available | Assign/unassign members; switch to People view | Task ownership and people columns/stats reflect updates | P0 | Regression |
| UAT-016 | Task labels and checklist | Validate label and checklist interactions | Existing task | Assign label, rename label, remove label, add/toggle/delete checklist item | Label chips and checklist state persist correctly | P1 | Functional |
| UAT-017 | Task filters, group-by, and search | Validate discoverability tools | Project with mixed tasks | Apply assignee/priority/progress/date/label filters and group-by modes | Resulting task sets match filter criteria and hierarchy rules | P1 | Regression |
| UAT-018 | Timeline rendering | Validate timeline and dependency display | Tasks with start/end and dependencies | Open timeline view; inspect bars, overdue colors, dependency lines | Bars map to dates; milestones flagged; dependency lines connect correctly | P1 | Functional |
| UAT-019 | Program creation (Basics step) | Validate program basics form and validation | User with program creation access | Open ProgramOnboardingWizard, fill Basics step (name required, description optional, program type/goals/business unit optional, date fields optional) | Step indicator shows complete; can proceed to Ownership step | P0 | Functional |
| UAT-019a | Program creation (Ownership step) | Validate program manager assignment | Basics completed, users available in scope | Fill Ownership step (search and select Manager); verify user search filters by scope group | Manager field populated; proceed to Review step | P0 | Functional |
| UAT-019b | Program creation end-to-end | Validate end-to-end program creation with manager assignment | All wizard steps preconditions met | Complete wizard steps 0-2 and submit | Program created; manager assigned; confirmation toast shown; navigation to program detail | P0 | Smoke |
| UAT-020 | Risk creation and lifecycle | Validate risk record creation and full field coverage | Existing project, Risks tab access | Create risk: fill name, subject, description, category, impact (1-5), probability (1-5), mitigation plan, contingency plan; save | Risk record created, appears in risks list with calculated risk score | P0 | Functional |
| UAT-021 | Issue creation and lifecycle | Validate issue record creation with priority and tracking | Existing project, Issues tab access | Create issue: fill title, description, category, priority, due date; save | Issue record created, appears in issues list; can assign to user | P0 | Functional |
| UAT-022 | Change request creation and workflow | Validate change request with business case fields | Existing project, Changes tab access | Create change: fill title, description, change type, impact, priority, cost impact, benefits, change plan; save | Change record created, appears in changes list; ready for approval gate | P0 | Functional |
| UAT-023 | Status Report creation from project | Validate status report authoring and cross-project visibility | Existing project | Create status report: fill report title, accomplished activities, planned activities, comments; save | Report created, appears in ProjectDetailPage reports tab AND in StatusReportListPage for cross-project view | P0 | Functional |
| UAT-024 | Decision creation and capture | Validate decision logging and impact tracking | Existing project with DecisionWorkspace accessible | Create decision: fill title, description, rationale, status (Proposed→Approved), impact level, owner; save | Decision logged in project workspace; audit trail shows creator and timestamp | P0 | Functional |
| UAT-025 | Gate Decision approval (project gate workflow) | Validate project gate governance decision (Approve/Reject/Defer) | Project with gate milestone active | Open gate, review readiness conditions and prerequisite artifacts; approve gate with rationale | Gate state transitions to Approved; downstream gates become available for triage; project continues execution | P0 | Functional |
| UAT-026 | Program detail edit | Validate program lifecycle edits | Existing program | Edit details, governance, health, financial values; save | Values persist and reflect in program page and related summaries | P1 | Functional |
| UAT-027 | Documents upload/link/delete across entities | Validate document operations | Intake/project/program record exists | Upload file, add external link, open/download, delete | Document appears filtered to owner record; delete removes from active list | P0 | Smoke |
| UAT-021 | Analytics navigation and counts | Validate analytics page integrity | Existing requests/projects | Open analytics hub and each linked analytics page | All pages load; aggregate counts are internally consistent | P1 | Regression |
| UAT-022 | Teams membership and default template | Validate team ops and template assignment | Admin user, teams and templates exist | Search team, expand details, assign default template | Team detail displays members/owner; template setting persists | P1 | Functional |
| UAT-023 | Admin settings and template/artifact management | Validate PMO configuration controls | Admin user | Update key app settings, create/edit/deactivate template, artifact config updates | Changes persist and are reflected in dependent workflows | P0 | Regression |
| UAT-024 | Not-found and deep-link behavior | Validate navigation fallback safety | Any user | Open invalid route; open valid deep-link route with params | Invalid route redirects to dashboard; deep-link lands on target context | P2 | Functional |
| UAT-025 | Mira mutation safety path | Validate mutation request creation and failure safety | User with Mira action access | Trigger bug/enhancement action, confirm create; test failure path | On success record created; on failure safe user feedback and telemetry event | P1 | Cross-functional |

## 7. Edge and Negative Test Set

| ID | Edge/Negative Case | Expected Behavior | Priority |
| --- | --- | --- | --- |
| NEG-001 | Submit intake with empty required description | Validation blocks submit and shows actionable error | P0 |
| NEG-001a | Create project with empty name | Form blocks submission; validation error shown on Basics step | P0 |
| NEG-001b | Create project without team assignment | Wizard allows completion without primary team; project created but team record omitted | P0 |
| NEG-002 | Attempt stage progression with missing required governed fields | Stage remains blocked; required field guidance shown | P0 |
| NEG-002a | Select unavailable or deleted user as PM/Sponsor in project creation | User search excludes disabled users; selection fails gracefully or shows updated list | P1 |
| NEG-002b | Create program without manager assignment | Wizard allows completion without manager; program created but manager record omitted | P1 |
| NEG-003 | Non-admin attempts admin URL direct access | Redirect to dashboard without admin content | P0 |
| NEG-003a | Create risk with impact/probability missing | Validation error or form blocks submission on required scored fields | P1 |
| NEG-003b | Create issue with missing title | Form blocks submission; title is required | P0 |
| NEG-003c | Create change request without change type | Form expects category; allows creation but fields persist as empty/null if allowed | P1 |
| NEG-004 | Duplicate/similar intake submission | Warning is shown; user can still choose controlled path | P1 |
| NEG-004a | Create two projects with identical name | System allows duplicate names; both records created; no conflict error expected | P2 |
| NEG-004b | Create two programs with identical name | System allows duplicate names; both records created; no conflict error expected | P2 |
| NEG-004c | Create two risks in same project with identical title | System allows duplicate titles; both records created | P2 |
| NEG-005 | Assign dependency predecessor to invalid/self scenario | UI prevents invalid relation or returns handled error | P1 |
| NEG-005a | Create risk with probability 0 or impact 0 | Risk score calculated correctly (0 values handled); risk still logged | P1 |
| NEG-005b | Delete approved decision without deactivation warning | Warning/confirmation dialog shown; user decision required | P1 |
| NEG-006 | Upload unsupported or over-limit file to documents | Upload blocked with clear message; no partial broken state | P1 |
| NEG-006a | Create status report without body/activities | Validation blocks submit or allows empty report; behavior consistent | P1 |
| NEG-007 | Delete in-use template/artifact where warning applies | Warning prompt shown; user decision required | P1 |
| NEG-007a | Create task without name | Form blocks submission; name is required | P0 |
| NEG-007b | Create gate decision with missing rationale in Reject path | Reject action requires rationale; blocks without reason | P0 |
| NEG-008 | Open timeline with no task dates | Timeline handles gracefully with empty/neutral state | P2 |
| NEG-008a | Create risk/issue/change with future-only dates (no due date) | Records created; no validation error on optional date fields | P2 |
| NEG-009 | Search/filter producing no rows | Clear empty state with no console/runtime breakage | P2 |
| NEG-009a | Create decision without owner assignment | Decision created; owner defaults to creator or remains unassigned per design | P2 |

## 8. Cross-Functional Considerations

### 8.1 Data Integrity and Consistency

- Verify list and detail pages reflect same underlying status and ownership values.
- Confirm PSS-backed task writes reconcile correctly after expected persistence delay.
- Validate count widgets and summary strips against table data on same screen.

### 8.2 Role and Access Controls

- Confirm admin-gated pages and settings are inaccessible to non-admin users.
- Confirm team/template assignment controls appear only for authorized users.

### 8.3 Performance and Usability

- Intake queue, project task board, and analytics pages should remain responsive under realistic data volume.
- Task filtering/grouping should complete without visible lock-up or stale rendering.

### 8.4 Reliability and Error Handling

- ErrorBanner and loading states should be visible and non-blocking where applicable.
- Failures in mutation operations should not produce silent writes or data corruption.

### 8.5 Integration Touchpoints

- Dataverse CRUD paths for intake/projects/programs/tasks.
- PSS create/update/delete paths for schedule entities.
- SharePoint document upload/list/delete proxy path.
- Mira mutation creation path to project request records.

## 9. Recommended Smoke Suite (Release Gate, 45-60 Minutes)

Execute in this order. This suite validates all critical record creation workflows and core project lifecycle:
1. UAT-001 app boot and redirect
2. UAT-003 intake queue search/filter
3. UAT-004 new intake creation with attachments
4. UAT-005 submit for review transition
5. UAT-007e project creation end-to-end (intake → project, wizard 6 steps, team/template bootstrap)
6. UAT-019b program creation end-to-end (3-step wizard)
7. UAT-013 task create/edit core fields
8. UAT-020 risk creation and lifecycle
9. UAT-021 issue creation and lifecycle
10. UAT-022 change request creation and workflow
11. UAT-023 status report creation from project
12. UAT-024 decision creation and capture
13. UAT-027 document upload/link/delete
14. UAT-002 admin route gating check (non-admin)

Exit criteria:
- No P0 failures
- No data-loss defects
- Core end-to-end workflows fully functional: Intake → Project → Task, Risk, Issue, Change, Decision, Report
- All core record types successfully created and persisted
- Team/template provisioning working correctly

## 10. Recommended Regression Suite (Pre-release or Weekly)

Core regression pack (all P0 workflows):
- **Intake workflow:** UAT-003 through UAT-009 (intake queue, creation, submission, clarification, approval, conversion)
- **Project lifecycle:** UAT-007, UAT-007a-e (project creation), UAT-010-018 (project detail, tasks, timeline)
- **Program lifecycle:** UAT-019, UAT-019a-b, UAT-026 (program creation and edits)
- **Governance records:** UAT-020 (risk), UAT-021 (issue), UAT-022 (change), UAT-024 (decision), UAT-025 (gate approval)
- **Reporting:** UAT-023 (status report), UAT-027 (documents)
- **Cross-functional:** UAT-012 (project status reports), UAT-015 (task assignment), UAT-022 (teams), UAT-023 (admin), UAT-025 (Mira)
- **All edge/negative cases:** NEG-001 through NEG-009*

Risk-based expansion triggers:
- If **record creation paths** change (intake, project, program, task, risk, issue, change, status report, decision): run UAT-007, UAT-007a-e, UAT-019, UAT-019a-b, UAT-013, UAT-020-024 plus NEG-001*
- If **project/program/task lifecycle** changed: emphasize UAT-010-018 plus UAT-026, NEG-005-008
- If **intake workflow/governance** changed: emphasize UAT-003-009 plus gates, NEG-001-004
- If **gate/approval workflows** changed: emphasize UAT-025, project detail Govern tab
- If **admin/template/artifact settings** changed: emphasize UAT-023, UST-019a, UAT-007b, UAT-007c

## 11. Gaps, Ambiguities, and Testability Notes

### 11.1 Gaps to Track

- Deferred features in registry should stay explicitly excluded from pass/fail for core UAT unless they regress currently implemented workflows.
- Some advanced Mira capabilities remain roadmap/deferred and should be validated only for current implemented behavior.

### 11.2 Ambiguities to Resolve Before Formal Sign-off

- Confirm expected SLA/timing tolerance for PSS persistence in each test environment.
- Confirm whether specific intake statuses are mandatory in each operational workflow variant.
- Confirm document size/type constraints and expected validation messages per environment policy.

### 11.3 Test Data Requirements

**Intake & Conversion:**
- At least 10 intake requests across Draft, Submitted, In Triage, Approved, Converted states (UAT-004 through UAT-009)

**Projects & Programs:**
- At least 1 existing active project with:
  - 15+ tasks across multiple buckets, mixed status/progress (for UAT-013-018)
  - At least 2 risks with varied impact/probability scores (for UAT-020)
  - At least 2 issues with different priorities (for UAT-021)
  - At least 1 change request (for UAT-022)
  - At least 1 status report (for UAT-023)
  - At least 1 decision logged (for UAT-024)
  - At least 1 gate in Pending state (for UAT-025)
- At least 1 existing program with linked projects and mixed health states (for UAT-026)

**Admin & Configuration:**
- At least 2 PMO teams with members
- At least 2 active project templates with varied task payloads
- Required artifact definitions configured
- Intake stage workflow configured with at least 2 stages

**User Accounts:**
- Requester user (non-admin, can create intake/submit)
- PMO Analyst user (can triage, approve intake, create projects)
- Project Manager user (can edit projects, create tasks, risks, issues, changes, decisions, approve gates)
- Program Manager user (can edit programs, view rollups)
- PMO Admin user (can access admin settings, manage templates, modify workflow config)

## 12. Execution and Reporting Template

For each executed case, capture:
- Test Case ID
- Environment and build identifier
- User role used
- Pass/Fail/Blocked
- Defect ID if failed
- Notes and screenshots

Recommended defect severity mapping:
- Sev-1: blocks intake-project-task flow or causes data loss
- Sev-2: major function works inconsistently with workaround
- Sev-3: non-blocking UI/UX or edge-case issue

---

Plan owner suggestion: PMO QA lead with PMO product manager sign-off.
Last updated: 2026-04-27.
