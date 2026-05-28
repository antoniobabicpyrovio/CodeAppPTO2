# corp-fin-bi-pmo-cfr-solution

> CFR Project Management — Coram Finance RevCycle unified PMO application

<img alt="Team" src="https://img.shields.io/badge/Team-corp--fin--bi-0A66C2?style=for-the-badge" />
<img alt="Function" src="https://img.shields.io/badge/Function-PMO%20%7C%20Project%20Management-4C9A2A?style=for-the-badge" />
<img alt="Focus" src="https://img.shields.io/badge/Focus-Intake%20%7C%20Projects%20%7C%20Tasks%20%7C%20Documents%20%7C%20AI-6F42C1?style=for-the-badge" />
<img alt="Access" src="https://img.shields.io/badge/Access-Team--Based-F59E0B?style=for-the-badge" />
<img alt="Governance" src="https://img.shields.io/badge/Governance-Standardized-111827?style=for-the-badge" />

---

> [!IMPORTANT]
> This repository is owned and maintained by the **corp-fin-bi** team. Access is managed through team membership — contact the team lead for access requests. Standards and governance follow [`corp-fin-bi-standards`](https://github.com/cvs-health-source-code/corp-fin-bi-standards) as the authoritative source. The publisher prefix `pmo`/`pmo_` is an approved exception boundary for this solution only.

---

## Purpose

The **CFR Project Management** application is the primary unified PMO surface for Coram Finance RevCycle. It consolidates project request intake, project and program lifecycle management, task execution, document management, and AI-assisted advisory into a single Power Apps Code App backed by Dataverse and the Microsoft Project Scheduling Service (PSS).

The application replaces fragmented tool usage (standalone Microsoft Planner, spreadsheet tracking, email-based intake) with a governed, integrated experience that:

- Routes and tracks project requests through a configurable multi-stage intake pipeline
- Surfaces project and program health signals for PMO leadership
- Provides a full task management surface that matches Microsoft Planner capabilities without requiring users to leave the app
- Centralizes all project documents in a single SharePoint library with metadata-driven ownership
- Delivers AI-powered contextual advisory through **Mira**, a Copilot Studio agent embedded in the application

---

## Start Here

- **Application planning and feature registry:** [`docs/planning/`](docs/planning/)
- **Mira agent current state:** [`docs/planning/mira-handoff-and-future-development-plan.md`](docs/planning/mira-handoff-and-future-development-plan.md)
- **Copilot Studio specs and contracts:** [`copilot-studio/`](copilot-studio/)
- **Solution source (botcomponents, workflows):** [`solution/src/`](solution/src/)
- **Application source:** [`app/src/`](app/src/)
- **Deferred feature registry:** [`docs/planning/deferred-feature-registry.json`](docs/planning/deferred-feature-registry.json)

---

## Quick Links

| Destination | Purpose |
|---|---|
| [`app/src/pages/`](app/src/pages/) | Application page components (routes) |
| [`app/src/components/scheduling/`](app/src/components/scheduling/) | Task workspace components |
| [`app/src/components/admin/`](app/src/components/admin/) | Admin intake workflow and stage editors |
| [`app/src/api/`](app/src/api/) | Dataverse OData API layer |
| [`app/src/lib/schedulingClient.ts`](app/src/lib/schedulingClient.ts) | PSS write wrappers (task CRUD, checklist, sprint, dependency) |
| [`app/src/lib/sharePointClient.ts`](app/src/lib/sharePointClient.ts) | SharePoint document upload/list/delete via Dataverse custom API |
| [`app/src/lib/deepLink.ts`](app/src/lib/deepLink.ts) | Deep link builder + startup reader (`buildDeepLink`, `readDeepLinkParams`, `initDeepLinkContext`) |
| [`app/src/hooks/useUrlState.ts`](app/src/hooks/useUrlState.ts) | URL search param state hook for in-session back/forward navigation |
| [`app/src/providers/`](app/src/providers/) | `ConfigurationProvider` — runtime config context, admin role resolution, typed config hooks |
| [`app/src/ai/`](app/src/ai/) | Mira contract authority (advisory engine, draft engine, mutations) |
| [`copilot-studio/CONTRACTS.md`](copilot-studio/CONTRACTS.md) | Copilot Studio ↔ app contract fidelity mapping |
| [`solution/src/botcomponents/`](solution/src/botcomponents/) | Deployed Mira topic and action botcomponents |
| [`solution/src/Workflows/`](solution/src/Workflows/) | Deployed Power Automate flows |
| [`scripts/`](scripts/) | Solution management and Dataverse provisioning scripts |

---

## Implemented Capabilities

### Governed Intake Pipeline

| Capability | Notes |
|---|---|
| Intake request submission | Configurable multi-stage wizard; each stage renders only its assigned fields |
| Stage field configuration | Admin-configured per stage via `pmo_requiredfieldsjson`; no hardcoded field lists |
| Stage navigation | Forward and back navigation; completed stages summarized as read-only panels |
| Intake routing | Configurable category routing in `app/src/lib/intakeRoutingConfig.ts` with AI triage scoring |
| Intake record management | List and detail views with status tracking and document attachments |
| Power Automate: `pmo_CreateIntakeRecord` | Creates `pmo_projectrequest` Dataverse record when Mira intake fires |
| Power Automate: `pmo_CFRIntakeToProject` | Converts approved intake record to `msdyn_project` |
| Power Automate: `pmo_CFRIntakeSubmissionNotification` | Sends notification on intake submission |

### Project and Program Management

| Capability | Notes |
|---|---|
| Project list and detail views | Full lifecycle with status, health, team, and budget fields |
| Program list and detail views | Aggregated project rollup with health signals |
| Status report authoring | Draft and publish weekly status reports |
| Risk register | Create, track, and close project risks |
| Issue log | Create, track, and close project issues |
| Change log | Create and track change requests per project |
| Decision log | Record and track project decisions |
| WBS task plan templates | Apply a structured task hierarchy template to a new project |
| Project team management | Add and remove team members with resource assignment |
| Document management | Compact document panel on Project, Program, Intake, and Task surfaces |

### Document Management

All documents are stored in a single flat SharePoint library (`AppDocuments` in the `Nexus-PMO` site) with metadata columns for ownership. No folder hierarchy — documents are filtered client-side by indexed metadata columns.

| Capability | Notes |
|---|---|
| Upload | Drag-drop zone and file-input button with category picker |
| Category tagging | 13 standard categories (Business Case, Charter, RACI, SOW, Budget, etc.) |
| Document listing | Per-record filtered view; category grouping toggle |
| Download | Direct link to SharePoint file; opens in new tab |
| Delete | Soft-delete to SharePoint Recycle Bin |
| Link external | Create a Dataverse `pmo_documentlink` reference without SP upload |
| Ownership metadata | Title, IntakeID, ProgramID, ProjectID, TaskID, DocumentCategory columns |
| Upload proxy | `pmo_UploadDocumentToSharePoint` unbound Dataverse custom API → Power Automate → SharePoint |
| Power Automate: `PMO: Upload Document to SharePoint` | Triggered by `BusinessEventsTrigger` on custom API invocation; writes file and metadata to `AppDocuments` |

### Task Workspace (Full Planner Parity)

All task operations use the Microsoft Project Scheduling Service (PSS) API to ensure Dataverse and Planner stay in sync.

| Capability | Notes |
|---|---|
| **Board (Kanban) view** | Bucket columns with collapsible WBS hierarchy |
| **List/grid view** | Sortable table with all task fields |
| **Charts view** | Completion donut, by-priority and by-bucket bar charts |
| **People/workload view** | Column-per-person layout with Incomplete/Late stats |
| **Task detail panel** | Full slide-in editing surface with compact document attachment |
| Task CRUD (create, rename, delete) | Via PSS `PssCreateV1` / `PssUpdateV1` / `PssDeleteV1` |
| Bucket CRUD | Create, rename, delete buckets via PSS |
| Priority editing | Urgent / Important / Medium / Low |
| Progress slider | 0–100% with snap points; drives `msdyn_progress` via `msdyn_effortcompleted` |
| Effort hours editing | Total effort (`msdyn_effort`) editable via PSS |
| Description / notes editing | `msdyn_description` via PSS |
| Date editing | Start and due date via PSS |
| Milestone toggle | `msdyn_ismilestone` via PSS |
| Assignment management | Add/remove team member assignments per task |
| Dependency management | Finish-to-Start, Finish-to-Finish, Start-to-Start, Start-to-Finish via PSS |
| Labels | Assign, rename, remove; 25 Planner color palette |
| Label chips on task cards | Named pill chips with Planner colors on board and list rows |
| Checklist items | Create, toggle complete, delete per task |
| Sprint assignment | Assign task to project sprint |
| Task search | Substring match on task subject |
| Filter bar | Assignee, priority, progress, due date, labels |
| Group-by picker | Bucket, assignee, priority, progress |
| WBS hierarchy | Parent-child task tree with rollup summary rows |
| **Timeline view** | Custom SVG Gantt renderer — month/week grid, color-coded bars, progress overlay, amber milestone diamonds, SVG dependency arrows for all 4 link types (FS/FF/SS/SF); click bar or task name opens detail panel |
| **Drag-and-drop between buckets** | Native HTML5 DnD — no external library; board view with bucket grouping; optimistic cache update; leaf tasks only |
| **URL-stateful view/task selection** | Active tab, monitor sub-tab, task selection, and view mode synced to HashRouter search params; browser back/forward button works within session |

### Deep Linking and Navigation

Shareable URLs that survive session boundaries — users can copy a link to a specific project/tab/task and send it to a colleague.

| Capability | Notes |
|---|---|
| **Cross-session deep links** | `deepLink.ts` reads `getContext().app.queryParams` on startup; navigates to `page/id?tab=&subtab=&task=&view=` when params present |
| **Shareable player URL construction** | `buildDeepLink()` assembles Power Apps player URLs using runtime `environmentId`, `appId`, `tenantId` from SDK — no hardcoded environment values |
| **Copy Link button** | Available on Project, Program, and Intake detail pages; hidden in dev mode (`isDeepLinkAvailable()` false at localhost) |
| **In-session URL state** | `useUrlState` hook syncs active tab, monitor sub-tab, task selection, and task view to HashRouter search params; browser back/forward works within session |
| **Catch-all 404 route** | Invalid hash routes show "Page not found" with 4-second auto-redirect to dashboard |
| **Dev mode behaviour** | `getContext()` fails silently in localhost — `buildDeepLink` returns null, Copy Link is hidden; HashRouter URLs work natively |

### Mira AI Assistant (Copilot Studio + App-side Engine)

Mira is a deployed Copilot Studio agent (Waves 0–3 complete, hardening complete) with both a freeform webchat mode and a governed contextual quick-action mode in the application.

**Deployed contextual capabilities (14 topics):**

| Topic | Mode |
|---|---|
| Explain project health | Advisory |
| Explain program health | Advisory |
| Draft weekly status report | Draft |
| PMO triage — what needs attention | Advisory |
| Draft WBS task plan | Draft |
| Assess project risk | Advisory |
| Improve status report draft | Draft |
| Identify blockers and overdue work | Advisory |
| What are my open tasks | Advisory |
| What needs my attention | Advisory |
| What changed since last status report | Advisory |
| What is blocking this project right now | Advisory |
| Report a bug | Approval-gated mutation |
| Suggest an enhancement | Approval-gated mutation |

**Deployed Copilot actions (5):**
`load-project-context`, `load-status-context`, `load-program-context-enriched`, `load-portfolio-triage-context`, `load-project-open-tasks-context`

**Mutation telemetry:** Centralized failure sink in `app/src/lib/telemetry.ts`; emits `mira-mutation-failure` browser event with structured `telemetryId`, `failureReason`, and `failureCode`.

### Analytics and Administration

| Capability | Notes |
|---|---|
| Portfolio health analytics | Health signals across all projects |
| Pipeline view | Intake pipeline and conversion tracking |
| By-team analytics | Resource and delivery analytics by team |
| Schedule analytics | Cross-project schedule health |
| Routing QA | Intake routing confidence review |
| Admin settings | Application-level configuration via `pmo_appsetting` |
| **Runtime configuration panel** | Tabbed admin settings UI for 10 runtime config categories: dashboard display, intake triage, notifications, SP document categories, PMO team field, tenant ID, intake routing domains, prioritization weights/budget tiers, Mira signal thresholds |
| **Admin role-based nav gating** | Sidebar Administration section and `/admin/*` routes only visible to `pmo_admin` / `system_admin` Dataverse security roles; anonymous users see no admin nav and are redirected on direct access |
| **Change history audit log** | Admin-visible log of setting changes; requires `pmo_admin` or `system_admin` role |
| Intake workflow configuration | Visual multi-stage workflow builder; no JSON or field logical names exposed to admins |
| Stage field mapper | Two-column dropdown UI; serializes to `ConversionRule[]` JSON for `intakeValidation.ts` |
| Approver group picker | AAD-synced team dropdown (teamtype=2); resolves to `azureactivedirectoryobjectid` |
| Quick Setup | Seeds a standard 3-stage intake workflow when none exists |
| Artifact definition management | Create, edit, and delete required artifact definitions with project-count warning before delete |
| **Admin-editable intake routing** | Routing domain config stored in `pmo_appsetting` as JSON; `scoreAgainstDomains()` scores against admin-managed keyword lists; editable in Runtime Configuration panel |
| **Configurable prioritization scoring** | Weights and budget tier thresholds are runtime-configurable via admin settings; `usePrioritizationWeights()` + `usePrioritizationBudgetTiers()` read from `ConfigurationProvider` |
| **Configurable Mira signal thresholds** | Risk/issue count warn and critical thresholds configurable at runtime; `projectHealthSignals()` reads from `MiraSignalThresholds` config |

---

## Known Limitations and Open Workstreams

### Active gaps (not yet implemented)

| ID | Feature | Status | Notes |
|---|---|---|---|
| — | Mira real Dataverse write adapters | Not started | `createBugReportRecord` and `createEnhancementSuggestionRecord` in `app/src/ai/mutations.ts` use mock IDs. Tier 1 priority per Mira handoff plan. |
| — | Document UploadedBy metadata | Not started | `UserEmail` flows through the custom API and is available in trigger outputs. Person/Group column population requires adding a SharePoint PatchItem step in the flow designer using the correct field schema name. |
| dfr-003 | Goal linkage | Deferred | `msdyn_projectgoal` / `msdyn_projecttasktogoal` schema not yet discovered; no UI |
| dfr-013 | Mira open tasks — refined first-class capability | Deferred | Basic capability shipped; refinement deferred |
| dfr-014 | Mira "what needs attention" — user-language refinement | Deferred | Basic capability shipped; refinement deferred |
| dfr-015 | True contextual freeform Mira chat | Deferred | Requires evidence-first feasibility review; host-context bridge not validated |
| dfr-016 | Teams channel intake via Copilot Studio | Blocked | Requires M365 admin Teams app registration |
| — | CI/CD PR-gated validation pipeline | Deferred | TypeScript type-check and build not yet automated on PR |

### Permanently out of scope (through supported technical means)

| Feature | Reason |
|---|---|
| Task attachments (Planner-synced) | Planner stores references via Graph API only; Graph Planner API does not support premium plans |
| Task comments / conversation (Planner-synced) | Planner uses Exchange Group mailbox; no Dataverse entity, no PSS path |

> PMO-native workarounds (custom Dataverse tables for attachments and comments, not synced to Planner) are architecturally possible but require solution architect coordination and are not scheduled.

### Architectural notes

- **PSS persistence lag:** The Project Scheduling Service takes approximately 20–22 seconds to propagate writes to Dataverse after a successful `OperationSet` response. Optimistic UI patterns with calibrated `PSS_DELAY` constants handle this in the application.
- **Document upload proxy:** SharePoint REST API is blocked by the Power Apps iframe host (cross-origin). All document writes go through a Dataverse unbound custom API (`pmo_UploadDocumentToSharePoint`) which triggers a Power Automate cloud flow (`BusinessEventsTrigger`) that calls the SharePoint connector with the service connection's credentials.
- **Custom API SDK registration:** Every Dataverse unbound custom API called from the app must be declared in the `apis` map of a `DATAVERSE_SOURCES` entry in `dataverseClient.ts` with its OData path and parameter definitions. The SDK executor looks up operations there — an undeclared operation throws "not found in data source."
- **Mira interaction modes:** Mira has two distinct modes — a governed contextual quick-action surface (route-aware, bounded to 14 capabilities) and a freeform webchat via embedded Copilot Studio iframe. The iframe mode does not currently inherit app route context (no `projectId`/`programId` injection).

---

## Ownership and Support

| Field | Value |
|---|---|
| **Owner team** | corp-fin-bi |
| **Support contact** | corp-fin-bi team |
| **Dataverse environment** | Nexus RCM DEV — `731e4975-10cd-4535-b82f-1ff016e59b6c` |
| **Power Apps app ID** | `41df5d3f-bdcd-4148-8ee6-74a88e76deb0` |
| **Copilot Studio agent** | Mira — Dataverse Copilot ID `bee26fa0-bf3e-43e0-836f-4df459d1c00c` |
| **Solution name** | `CFRProjectManagement` |
| **Publisher prefix** | `pmo` / `pmo_` (approved exception boundary for this solution) |
| **SharePoint document library** | `https://aetnao365.sharepoint.com/sites/Nexus-PMO/AppDocuments` |
| **Standards authority** | [`corp-fin-bi-standards`](https://github.com/cvs-health-source-code/corp-fin-bi-standards) |

---

## Technology Stack and Deployment

### Application

| Layer | Technology |
|---|---|
| Framework | React 19, TypeScript, Vite |
| Styling | Tailwind CSS, shadcn/ui |
| Data fetching | TanStack Query v5 |
| Charts | Recharts |
| Icons | Lucide React |
| Testing | Vitest |
| Deployment | `npx power-apps push` (Power Apps CLI npm package) |

### Platform

| Layer | Technology |
|---|---|
| Data platform | Microsoft Dataverse (Nexus RCM environment) |
| Task scheduling writes | Project Scheduling Service (PSS) — `PssCreateV1`, `PssUpdateV1`, `PssDeleteV1` |
| Document storage | SharePoint Online — `Nexus-PMO/AppDocuments` flat library with metadata columns |
| Document upload proxy | Dataverse custom API → Power Automate (`BusinessEventsTrigger`) → SharePoint connector |
| AI agent | Copilot Studio (Mira agent) |
| Automation | Power Automate (3 flows in solution source + 1 document upload flow deployed to CFRProjectManagement) |
| Solution management | PAC CLI (`pac solution pack / import / export`) |

### Mandatory build sequence

```
cd app
npx tsc -b --noEmit      # Type-check — must be zero errors
npm run build             # Vite production build
npx power-apps push       # Deploy to configured Dataverse environment
```

### Solution management

```powershell
# Export from DEV
./scripts/export-solution.ps1

# Import to DEV
./scripts/import-solution.ps1
```

---

## Phase and Roadmap Status

| Phase | Description | Status |
|---|---|---|
| Phase 0 | PSS API validation — OperationSet pattern, persistence lag calibration | Complete |
| Phase 1 | Project Task Workspace — Kanban, WBS hierarchy, task/bucket CRUD | Complete |
| Phase 2 | Program oversight, WBS templates, dependency management | Complete |
| Phase 3 | Resource assignment, team member lifecycle, advanced scheduling | Complete |
| Planner Parity Sprint | Task detail panel, search, filters, list/charts/people views, labels, checklists, sprints, all dependency types (FS/FF/SS/SF) | Complete |
| Mira Wave 0 | App-side advisory and draft engine, typed contracts, MiraPanel | Complete |
| Mira Wave 1 | Copilot Studio agent deployed — 4 topics, 4 actions, botcomponents, solution import | Complete |
| Mira Wave 2 | Expanded advisory topics (WBS plan, risk, blockers, open tasks, needs attention, changes, blocking now) | Complete |
| Mira Wave 3 | Approval-gated mutations (report-bug, suggest-enhancement), telemetry sink, Vitest coverage | Complete |
| Governed Intake (G1) | `intakeValidation.ts` schema, `GovernedIntakeWizard` staged multi-step form, stage-scoped field rendering, back navigation | Complete |
| Governed Intake (G2) | Visual admin workflow builder — field mapper, approver group picker, Quick Setup; artifact definition edit/delete | Complete |
| Document Integration | `pmo_UploadDocumentToSharePoint` custom API + catalog/category, Power Automate cloud flow, `DocumentLibrary` component across all record surfaces | Complete |
| Runtime Configuration | `ConfigurationProvider` wrapping app; 10 runtime config keys backed by `pmo_appsetting`; tabbed admin settings panel for all configurable parameters | Complete |
| Administrator Experience | Role-based nav gating (`pmo_admin`/`system_admin`), `AdminRoute` guards on `/admin/*` routes, Change History audit log, `roles` entity set fix in `power.config.json` | Complete |
| Timeline View (dfr-004) | Custom SVG Gantt renderer in `TaskTimelineView.tsx` — zero external dependencies; dependency arrows (FS/FF/SS/SF), milestone markers, progress overlay, today marker | Complete |
| Drag-and-Drop (dfr-007) | Native HTML5 DnD between Kanban buckets — no library; leaf-task only; optimistic cache update; 20s PSS lag handled | Complete |
| Deep Linking (dfr-012) | `useUrlState` in-session URL state + `deepLink.ts` cross-session player URLs + Copy Link buttons (Project/Program/Intake) + catch-all 404 | Complete |
| **Next** | Mira real Dataverse write adapters (replace mock mutations) | Not started |
| **Next** | Telemetry transport integration (durable sink for `mira-mutation-failure`) | Not started |
| **Next** | Document UploadedBy — add Person/Group population to upload flow in designer | Not started |
| Later | Goal linkage (`msdyn_projectgoal` schema not yet discovered) | Deferred |
| Later | Mira contextual freeform chat (host-context bridge) | Deferred — feasibility review required |
| Blocked | Teams channel intake | M365 admin action required |

---

## Governance

- Standards authority: [`corp-fin-bi-standards`](https://github.com/cvs-health-source-code/corp-fin-bi-standards)
- CODEOWNERS: [`.github/CODEOWNERS`](.github/CODEOWNERS)
- Copilot instructions: [`.github/copilot-instructions.md`](.github/copilot-instructions.md)
- All changes via pull request — minimum 1 approval required
- No direct commits to `main`
- Publisher prefix `pmo`/`pmo_` is an approved exception for this solution only; all other net-new corp-fin-bi components use the `rcm` prefix

---

*Maintained by the corp-fin-bi team. For questions, contact the team through standard internal channels.*
