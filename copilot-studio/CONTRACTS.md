# Mira Wave 1 — Contract Fidelity Mapping

This document maps every Copilot Studio output field and scoring threshold to its
authoritative source in `app/src/ai/`. Copilot Studio topics and actions must mirror
these definitions exactly. If a value changes, the change originates here.

---

## 1. Output Contract Field Mapping

### explain-project-health → `ProjectHealthAdvisory`

| Copilot Studio Output Field | TypeScript Contract Field | Source File | Notes |
|---|---|---|---|
| `topicId` | `topicId: 'explain-project-health'` | `contracts.ts` | Literal — must not vary |
| `mode` | `mode: 'advisory'` | `contracts.ts` | Literal — advisory only in Wave 1 |
| `projectId` | `projectId: string` | `contracts.ts` | From topic input variable |
| `projectName` | `projectName: string` | `contracts.ts` | From `msdyn_project.msdyn_subject` |
| `overallHealth` | `overallHealth: HealthLabel` | `contracts.ts` | Resolved via `resolveHealthLabel()` |
| `healthSignals` | `healthSignals: HealthSignal[]` | `contracts.ts` | 7 signals — see signals table below |
| `summary` | `summary: string` | `contracts.ts` | Specific narrative, must name project |
| `attentionItems` | `attentionItems: string[]` | `contracts.ts` | Array not empty string |
| `sourceStatus` | `sourceStatus: SourceStatus[]` | `contracts.ts` | One entry per data source |
| `confidence` | `confidence: Confidence` | `contracts.ts` | `'high' \| 'medium' \| 'low'` |
| `generatedAt` | `generatedAt: string` | `contracts.ts` | ISO timestamp |

### explain-program-health → `ProgramHealthAdvisory`

| Copilot Studio Output Field | TypeScript Contract Field | Source File | Notes |
|---|---|---|---|
| `topicId` | `topicId: 'explain-program-health'` | `contracts.ts` | Literal |
| `mode` | `mode: 'advisory'` | `contracts.ts` | Literal |
| `programId` | `programId: string` | `contracts.ts` | From topic input |
| `programName` | `programName: string` | `contracts.ts` | From `msdyn_projectprogram.msdyn_name` |
| `overallHealth` | `overallHealth: HealthLabel` | `contracts.ts` | Via `resolveHealthLabel()` |
| `healthSignals` | `healthSignals: HealthSignal[]` | `contracts.ts` | 5 signals — see signals table |
| `projectRollup` | `projectRollup: ProgramProjectRollup` | `contracts.ts` | `{ total, onTrack, atRisk, offTrack }` |
| `summary` | `summary: string` | `contracts.ts` | Must name program |
| `attentionItems` | `attentionItems: string[]` | `contracts.ts` | Array |
| `sourceStatus` | `sourceStatus: SourceStatus[]` | `contracts.ts` | Per source |
| `confidence` | `confidence: Confidence` | `contracts.ts` | |
| `generatedAt` | `generatedAt: string` | `contracts.ts` | |

### draft-weekly-status-report → `StatusReportDraft`

| Copilot Studio Output Field | TypeScript Contract Field | Source File | Notes |
|---|---|---|---|
| `topicId` | `topicId: 'draft-weekly-status-report'` | `contracts.ts` | Literal |
| `mode` | `mode: 'draft'` | `contracts.ts` | Literal — draft, not advisory |
| `projectId` | `projectId: string` | `contracts.ts` | From topic input |
| `projectName` | `projectName: string` | `contracts.ts` | |
| `reportingPeriod` | `reportingPeriod: string` | `contracts.ts` | Current week ISO range |
| `accomplishedActivities` | `accomplishedActivities: string` | `contracts.ts` | Editable — see draft rules |
| `plannedActivities` | `plannedActivities: string` | `contracts.ts` | Editable |
| `additionalComments` | `additionalComments: string` | `contracts.ts` | Editable |
| `sourceSignals` | `sourceSignals: string[]` | `contracts.ts` | Human-readable data source summary |
| `sourceStatus` | `sourceStatus: SourceStatus[]` | `contracts.ts` | |
| `confidence` | `confidence: Confidence` | `contracts.ts` | 4-factor scoring (see below) |
| `generatedAt` | `generatedAt: string` | `contracts.ts` | |

### pmo-triage-needs-attention → `TriageSummary`

| Copilot Studio Output Field | TypeScript Contract Field | Source File | Notes |
|---|---|---|---|
| `topicId` | `topicId: 'pmo-triage-needs-attention'` | `contracts.ts` | Literal |
| `mode` | `mode: 'advisory'` | `contracts.ts` | Literal |
| `scope` | `scope: 'project' \| 'program' \| 'portfolio'` | `contracts.ts` | From channel data |
| `summary` | `summary: string` | `contracts.ts` | 1 sentence |
| `rankedAttentionItems` | `rankedAttentionItems: TriageAttentionItem[]` | `contracts.ts` | Max 8 |
| `sourceStatus` | `sourceStatus: SourceStatus[]` | `contracts.ts` | |
| `confidence` | `confidence: Confidence` | `contracts.ts` | |
| `generatedAt` | `generatedAt: string` | `contracts.ts` | |

### report-bug → `BugReportDraft`

| Copilot Studio Output Field | TypeScript Contract Field | Source File | Notes |
|---|---|---|---|
| `topicId` | `topicId: 'report-bug'` | `contracts.ts` | Literal |
| `mode` | `mode: 'draft'` | `contracts.ts` | Draft only |
| `sourceRoute` | `sourceRoute: string` | `contracts.ts` | From route/channel data |
| `sourceEntityId` | `sourceEntityId?: string` | `contracts.ts` | Optional context |
| `sourceEntityType` | `sourceEntityType?: 'project' \| 'program' \| 'other'` | `contracts.ts` | Optional context |
| `userDescription` | `userDescription: string` | `contracts.ts` | User-provided bug details |
| `structuredDraft` | `structuredDraft: string` | `contracts.ts` | Reviewable draft text |
| `sourceStatus` | `sourceStatus: SourceStatus[]` | `contracts.ts` | Route context status |
| `confidence` | `confidence: Confidence` | `contracts.ts` | Description richness-driven |
| `generatedAt` | `generatedAt: string` | `contracts.ts` | ISO timestamp |

### suggest-enhancement → `EnhancementSuggestionDraft`

| Copilot Studio Output Field | TypeScript Contract Field | Source File | Notes |
|---|---|---|---|
| `topicId` | `topicId: 'suggest-enhancement'` | `contracts.ts` | Literal |
| `mode` | `mode: 'draft'` | `contracts.ts` | Draft only |
| `sourceRoute` | `sourceRoute: string` | `contracts.ts` | From route/channel data |
| `sourceEntityId` | `sourceEntityId?: string` | `contracts.ts` | Optional context |
| `sourceEntityType` | `sourceEntityType?: 'project' \| 'program' \| 'other'` | `contracts.ts` | Optional context |
| `userDescription` | `userDescription: string` | `contracts.ts` | User-provided enhancement details |
| `structuredDraft` | `structuredDraft: string` | `contracts.ts` | Reviewable draft text |
| `sourceStatus` | `sourceStatus: SourceStatus[]` | `contracts.ts` | Route context status |
| `confidence` | `confidence: Confidence` | `contracts.ts` | Description richness-driven |
| `generatedAt` | `generatedAt: string` | `contracts.ts` | ISO timestamp |

### draft-wbs-task-plan → `WbsTaskPlanDraft`

| Copilot Studio Output Field | TypeScript Contract Field | Source File | Notes |
|---|---|---|---|
| `topicId` | `topicId: 'draft-wbs-task-plan'` | `contracts.ts` | Literal |
| `mode` | `mode: 'draft'` | `contracts.ts` | Draft only |
| `projectId` | `projectId: string` | `contracts.ts` | From project context |
| `projectName` | `projectName: string` | `contracts.ts` | From project context |
| `planningAssumptions` | `planningAssumptions: string[]` | `contracts.ts` | Assumption bullets |
| `draftTasks` | `draftTasks: string` | `contracts.ts` | WBS-formatted draft text |
| `sourceStatus` | `sourceStatus: SourceStatus[]` | `contracts.ts` | Context load status |
| `confidence` | `confidence: Confidence` | `contracts.ts` | Source-status driven |
| `generatedAt` | `generatedAt: string` | `contracts.ts` | ISO timestamp |

### assess-project-risk → `ProjectRiskAssessmentAdvisory`

| Copilot Studio Output Field | TypeScript Contract Field | Source File | Notes |
|---|---|---|---|
| `topicId` | `topicId: 'assess-project-risk'` | `contracts.ts` | Literal |
| `mode` | `mode: 'advisory'` | `contracts.ts` | Advisory only |
| `projectId` | `projectId: string` | `contracts.ts` | From project context |
| `projectName` | `projectName: string` | `contracts.ts` | From project context |
| `riskScore` | `riskScore: number` | `contracts.ts` | 0-15 scale |
| `topRisks` | `topRisks: string[]` | `contracts.ts` | Deterministic risk bullets |
| `mitigationRecommendations` | `mitigationRecommendations: string[]` | `contracts.ts` | Actionable mitigations |
| `sourceStatus` | `sourceStatus: SourceStatus[]` | `contracts.ts` | Context load status |
| `confidence` | `confidence: Confidence` | `contracts.ts` | Source-status driven |
| `generatedAt` | `generatedAt: string` | `contracts.ts` | ISO timestamp |

### improve-status-report-draft → `ImprovedStatusReportDraft`

| Copilot Studio Output Field | TypeScript Contract Field | Source File | Notes |
|---|---|---|---|
| `topicId` | `topicId: 'improve-status-report-draft'` | `contracts.ts` | Literal |
| `mode` | `mode: 'draft'` | `contracts.ts` | Draft only |
| `projectId` | `projectId?: string` | `contracts.ts` | Optional project context |
| `projectName` | `projectName?: string` | `contracts.ts` | Optional project context |
| `originalDraft` | `originalDraft: string` | `contracts.ts` | User-provided text |
| `improvedDraft` | `improvedDraft: string` | `contracts.ts` | Improved PMO draft text |
| `improvementNotes` | `improvementNotes: string[]` | `contracts.ts` | Explanation bullets |
| `sourceStatus` | `sourceStatus: SourceStatus[]` | `contracts.ts` | User-draft status |
| `confidence` | `confidence: Confidence` | `contracts.ts` | Input-richness driven |
| `generatedAt` | `generatedAt: string` | `contracts.ts` | ISO timestamp |

### identify-blockers-overdue-work → `BlockersOverdueWorkAdvisory`

| Copilot Studio Output Field | TypeScript Contract Field | Source File | Notes |
|---|---|---|---|
| `topicId` | `topicId: 'identify-blockers-overdue-work'` | `contracts.ts` | Literal |
| `mode` | `mode: 'advisory'` | `contracts.ts` | Advisory only |
| `scope` | `scope: 'project' \| 'program' \| 'portfolio'` | `contracts.ts` | Channel/context scoped |
| `summary` | `summary: string` | `contracts.ts` | Blocker and overdue narrative |
| `blockers` | `blockers: string[]` | `contracts.ts` | Blocker list |
| `overdueItems` | `overdueItems: string[]` | `contracts.ts` | Overdue list |
| `recommendedActions` | `recommendedActions: string[]` | `contracts.ts` | Action guidance |
| `sourceStatus` | `sourceStatus: SourceStatus[]` | `contracts.ts` | Context load status |
| `confidence` | `confidence: Confidence` | `contracts.ts` | Source-status driven |
| `generatedAt` | `generatedAt: string` | `contracts.ts` | ISO timestamp |

### what-are-my-open-tasks → `OpenTasksAdvisory`

| Copilot Studio Output Field | TypeScript Contract Field | Source File | Notes |
|---|---|---|---|
| `topicId` | `topicId: 'what-are-my-open-tasks'` | `contracts.ts` | Literal |
| `mode` | `mode: 'advisory'` | `contracts.ts` | Advisory only |
| `projectId` | `projectId: string` | `contracts.ts` | From project route context |
| `projectName` | `projectName: string` | `contracts.ts` | From `msdyn_project.msdyn_subject` |
| `summary` | `summary: string` | `contracts.ts` | Deterministic task summary |
| `openTaskCount` | `openTaskCount: number` | `contracts.ts` | Count of active leaf tasks |
| `overdueTaskCount` | `overdueTaskCount: number` | `contracts.ts` | Count of tasks with due date before today |
| `dueSoonTaskCount` | `dueSoonTaskCount: number` | `contracts.ts` | Count of tasks due within 7 days |
| `unassignedTaskCount` | `unassignedTaskCount: number` | `contracts.ts` | Count of tasks with no active assignments |
| `tasks` | `tasks: OpenTaskItem[]` | `contracts.ts` | Ordered open task items |
| `sourceStatus` | `sourceStatus: SourceStatus[]` | `contracts.ts` | Per-source load status |
| `confidence` | `confidence: Confidence` | `contracts.ts` | Failed source = low; missing source = medium |
| `generatedAt` | `generatedAt: string` | `contracts.ts` | ISO timestamp |

### what-needs-my-attention → `NeedsAttentionAdvisory`

| Copilot Studio Output Field | TypeScript Contract Field | Source File | Notes |
|---|---|---|---|
| `topicId` | `topicId: 'what-needs-my-attention'` | `contracts.ts` | Literal |
| `mode` | `mode: 'advisory'` | `contracts.ts` | Advisory only |
| `projectId` | `projectId: string` | `contracts.ts` | From project route context |
| `projectName` | `projectName: string` | `contracts.ts` | From `msdyn_project.msdyn_subject` |
| `summary` | `summary: string` | `contracts.ts` | Deterministic direct-attention summary |
| `attentionItems` | `attentionItems: DeliveryAttentionItem[]` | `contracts.ts` | Ranked attention cards |
| `sourceStatus` | `sourceStatus: SourceStatus[]` | `contracts.ts` | Merged project/task source states |
| `confidence` | `confidence: Confidence` | `contracts.ts` | Failed source = low; multiple missing = medium |
| `generatedAt` | `generatedAt: string` | `contracts.ts` | ISO timestamp |

### what-changed-since-last-status-report → `StatusChangesAdvisory`

| Copilot Studio Output Field | TypeScript Contract Field | Source File | Notes |
|---|---|---|---|
| `topicId` | `topicId: 'what-changed-since-last-status-report'` | `contracts.ts` | Literal |
| `mode` | `mode: 'advisory'` | `contracts.ts` | Advisory only |
| `projectId` | `projectId: string` | `contracts.ts` | From project route context |
| `projectName` | `projectName: string` | `contracts.ts` | From `msdyn_project.msdyn_subject` |
| `baselineDate` | `baselineDate?: string` | `contracts.ts` | Most recent active status report date if available |
| `summary` | `summary: string` | `contracts.ts` | Deterministic baseline comparison summary |
| `changeItems` | `changeItems: StatusChangeItem[]` | `contracts.ts` | Structured delta items |
| `sourceStatus` | `sourceStatus: SourceStatus[]` | `contracts.ts` | Merged project/status/task states |
| `confidence` | `confidence: Confidence` | `contracts.ts` | No baseline or failed source = low |
| `generatedAt` | `generatedAt: string` | `contracts.ts` | ISO timestamp |

### what-is-blocking-this-project-right-now → `ProjectBlockersAdvisory`

| Copilot Studio Output Field | TypeScript Contract Field | Source File | Notes |
|---|---|---|---|
| `topicId` | `topicId: 'what-is-blocking-this-project-right-now'` | `contracts.ts` | Literal |
| `mode` | `mode: 'advisory'` | `contracts.ts` | Advisory only |
| `projectId` | `projectId: string` | `contracts.ts` | From project route context |
| `projectName` | `projectName: string` | `contracts.ts` | From `msdyn_project.msdyn_subject` |
| `summary` | `summary: string` | `contracts.ts` | Deterministic blocker summary |
| `blockerItems` | `blockerItems: DeliveryAttentionItem[]` | `contracts.ts` | Ranked blocker cards |
| `sourceStatus` | `sourceStatus: SourceStatus[]` | `contracts.ts` | Merged project/task source states |
| `confidence` | `confidence: Confidence` | `contracts.ts` | Failed source = low; multiple missing = medium |
| `generatedAt` | `generatedAt: string` | `contracts.ts` | ISO timestamp |

**OpenTaskItem fields:**

| Field | Type | Notes |
|---|---|---|
| `taskId` | `string` | `msdyn_projecttaskid` |
| `taskName` | `string` | `msdyn_subject` |
| `progressPercent` | `number` | Normalized to 0-100 |
| `dueDate` | `string \| undefined` | `msdyn_scheduledend` fallback `msdyn_finish` |
| `dueState` | `'overdue' \| 'due-soon' \| 'on-track' \| 'unscheduled'` | Deterministic due classification |
| `ownershipState` | `'assigned' \| 'unassigned'` | Based on active assignments |
| `assignees` | `string[]` | Assignment display names |
| `isMilestone` | `boolean` | Mirrors `msdyn_ismilestone` |

**DeliveryAttentionItem fields:**

| Field | Type | Notes |
|---|---|---|
| `category` | `'health' \| 'issue' \| 'risk' \| 'task' \| 'status'` | Signal family |
| `title` | `string` | Item headline |
| `detail` | `string` | Deterministic supporting explanation |
| `severity` | `'high' \| 'medium' \| 'low'` | UI priority weight |
| `recommendedAction` | `string` | Concrete follow-up step |

**StatusChangeItem fields:**

| Field | Type | Notes |
|---|---|---|
| `category` | `'risk' \| 'issue' \| 'task' \| 'status'` | Delta family |
| `summary` | `string` | Deterministic baseline-vs-current statement |

**TriageAttentionItem fields:**

| Field | Type | Notes |
|---|---|---|
| `rank` | `number` | 1-based |
| `scope` | `'project' \| 'program' \| 'portfolio'` | |
| `entityId` | `string \| undefined` | Project GUID |
| `title` | `string` | Project name |
| `whyNow` | `string` | Specific score factors cited |
| `recommendedNextStep` | `string` | Concrete action |
| `severity` | `'high' \| 'medium' \| 'low'` | score≥7=high, 4–6=medium, 1–3=low |

---

## 2. Health Signal Mapping

Source: `app/src/ai/grounding/signals.ts`

### Health Code Map (HEALTH_CODE_MAP)

| Dataverse Option Set Code | HealthLabel | SignalStatus |
|---|---|---|
| `189330000` | `On Track` | `ok` |
| `189330001` | `At Risk` | `warn` |
| `189330002` | `Off Track` | `critical` |
| `null` / `undefined` / unknown | `Unknown` | `warn` |

### Project Health Signals (7 signals, `projectHealthSignals()`)

| # | Dimension | Source Field | Status Logic |
|---|---|---|---|
| 1 | Overall Health | `proj_overallhealth` | `resolveHealthStatus(label)` |
| 2 | Schedule Health | `proj_schedulehealth` | `resolveHealthStatus(label)` |
| 3 | Effort Health | `proj_efforthealth` | `resolveHealthStatus(label)` |
| 4 | Financial Health | `proj_financialhealth` | `resolveHealthStatus(label)` |
| 5 | Progress | `msdyn_progress` (normalize ×100) | always `ok` |
| 6 | Active Risks | `risks.filter(r => r.statecode === 0).length` | 0=ok, 1–2=warn, >2=critical |
| 7 | Active Issues | `issues.filter(i => i.statecode === 0).length` | 0=ok, 1–2=warn, >2=critical |

**Progress normalization:** if `raw > 0 && raw <= 1` → multiply by 100, else round as-is.

### Program Health Signals (5 signals, `programHealthSignals()`)

| # | Dimension | Source | Status Logic |
|---|---|---|---|
| 1 | Overall Health | `proj_overallhealth` | `resolveHealthStatus(label)` |
| 2 | Schedule Health | `proj_schedulehealth` | `resolveHealthStatus(label)` |
| 3 | Financial Health | `proj_financialhealth` | `resolveHealthStatus(label)` |
| 4 | Active Projects | computed rollup — `rollup.total` | always `ok` |
| 5 | At Risk / Off Track | `rollup.atRisk` + `rollup.offTrack` | offTrack>0=critical, atRisk>0=warn, else ok |

---

## 3. Scoring Threshold Mapping

Source: `app/src/ai/topics/pmoTriageNeedsAttention.ts` — `scoreProject()`

| Condition | Points | Source Reference |
|---|---|---|
| Overall health = Off Track (code 189330002) | +5 | `scoreProject` line: `if (health === 'Off Track') score += 5` |
| Overall health = At Risk (code 189330001) | +3 | `scoreProject` line: `if (health === 'At Risk') score += 3` |
| Overdue (`msdyn_scheduledend < today`) | +2 | `scoreProject` |
| Active risks > 2 | +3 | `scoreProject` |
| Active issues > 2 | +2 | `scoreProject` |
| Last status report > 14 days ago | +2 | `scoreProject` |
| No status reports (missing) | +2 | `scoreProject` |

Exclude threshold: score must be > 0 to include in result.
Cap: top 8 items by descending score.

---

## 4. Draft Confidence Scoring

Source: `app/src/ai/topics/draftWeeklyStatusReport.ts` — `deriveConfidence()`

| Factor | Score |
|---|---|
| `msdyn_progress > 0` (progress known) | +1 |
| Prior report exists (`mostRecent !== null`) | +1 |
| Risks loaded successfully | +1 |
| Issues loaded successfully | +1 |
| **Total 4 = `high`, 2–3 = `medium`, 0–1 = `low`** | |

---

## 5. Program Stale Status Threshold

Source: `app/src/ai/context/programContext.ts` — `ProgramStatusFreshness`

| Threshold | Value |
|---|---|
| Stale (days since last report) | **14 days** |
| Classification | `< 14 days` = `fresh`, `>= 14 days` = `stale`, `no reports` = `missing` |

---

## 6. Source Status States

Source: `app/src/ai/contracts.ts` — `SourceState`

| State | Meaning |
|---|---|
| `ok` | Data loaded successfully |
| `missing` | No records found (entity has no data) |
| `failed` | API call failed (error caught) |

---

## 7. Wave 3 Mutation Payloads — Record Creation with Approval Gates

**Status:** Implemented in Wave 3 with TypeScript-driven write functions and app-side approval gates.

**Design Principle:** No silent writes. All mutation payloads are displayed to the user before Dataverse commit. User must explicitly confirm via approval dialog.

### report-bug → `BugReportMutation`

Creates a `pmo_ProjectRequest` record of type "Bug Report" in Dataverse after user confirmation.

| Mutation Output Field | Dataverse Field | TypeScript Source | Notes |
|---|---|---|---|
| `topicId` | N/A | `contracts.ts` | Literal: `'report-bug'` |
| `mode` | N/A | `contracts.ts` | Literal: `'mutation'` |
| `sourceRoute` | `pmo_sourceurl` | Derived | Current app route |
| `sourceEntityId` | Part of `pmo_affectedentity` | Derived | Project/program GUID if available |
| `sourceEntityType` | Part of `pmo_affectedentity` | Derived | Contextual scope |
| `userDescription` | `msdyn_description` | App input | User-provided detail |
| `structuredDraft` | N/A | Derived | Review-ready formatted text (for UI only) |
| `requestType` | `pmo_requesttype` | Literal | `'Bug Report'` |
| `title` | `pmo_title` | Derived | Extracted from draft title line |
| `description` | `msdyn_description` | Copied | Full user description |
| `reproductionStepsUrl` | `pmo_sourceurl` | Derived | Route reference |
| `affectedEntityRef` | `pmo_affectedentity` | Derived | `'project:ID'` or `'program:ID'` or `'other'` |
| `severity` | `pmo_severity` | Confidence-mapped | `'High' \| 'Medium' \| 'Low'` — high confidence → High severity |
| `status` | `pmo_status` | Literal | `'New'` |
| `createdBy` | `msdyn_createdby` | Session user | Current user ID |
| `createdAt` | `msdyn_createdon` | System timestamp | ISO string |
| `recordId` | Dataverse GUID | Post-creation | Populated after record creation |
| `creationResult` | N/A | `mutations.ts` | `'pending' \| 'success' \| 'failed'` |
| `sourceStatus` | N/A | Passthrough | Inherited from draft |
| `confidence` | N/A | Passthrough | Inherited from draft |
| `generatedAt` | N/A | System | ISO string |

### suggest-enhancement → `EnhancementSuggestionMutation`

Creates a `pmo_ProjectRequest` record of type "Enhancement Request" in Dataverse after user confirmation.

| Mutation Output Field | Dataverse Field | TypeScript Source | Notes |
|---|---|---|---|
| `topicId` | N/A | `contracts.ts` | Literal: `'suggest-enhancement'` |
| `mode` | N/A | `contracts.ts` | Literal: `'mutation'` |
| `sourceRoute` | `pmo_sourceurl` | Derived | Current app route |
| `sourceEntityId` | Part of `pmo_affectedentity` | Derived | Project/program GUID if available |
| `sourceEntityType` | Part of `pmo_affectedentity` | Derived | Contextual scope |
| `userDescription` | `msdyn_description` | App input | User-provided suggestion |
| `structuredDraft` | N/A | Derived | Review-ready formatted text (for UI only) |
| `requestType` | `pmo_requesttype` | Literal | `'Enhancement Request'` |
| `title` | `pmo_title` | Derived | Extracted from draft title line |
| `description` | `msdyn_description` | Copied | Full user description |
| `suggestedFeatureUrl` | `pmo_sourceurl` | Derived | Route reference |
| `affectedEntityRef` | `pmo_affectedentity` | Derived | `'project:ID'` or `'program:ID'` or `'other'` |
| `priority` | `pmo_priority` | Confidence-mapped | `'High' \| 'Medium' \| 'Low'` — high confidence → High priority |
| `status` | `pmo_status` | Literal | `'New'` |
| `createdBy` | `msdyn_createdby` | Session user | Current user ID |
| `createdAt` | `msdyn_createdon` | System timestamp | ISO string |
| `recordId` | Dataverse GUID | Post-creation | Populated after record creation |
| `creationResult` | N/A | `mutations.ts` | `'pending' \| 'success' \| 'failed'` |
| `sourceStatus` | N/A | Passthrough | Inherited from draft |
| `confidence` | N/A | Passthrough | Inherited from draft |
| `generatedAt` | N/A | System | ISO string |

### Wave 3 Approval Gate Flow

1. **Draft Generation** → User reviews `BugReportDraft` or `EnhancementSuggestionDraft` in MiraPanel
2. **User clicks "Submit for Recording"** → Triggers `submitFeedbackForRecording()` callback
3. **Mutation Preparation** → `prepareBugReportMutation()` or `prepareEnhancementSuggestionMutation()` creates mutation payload (no writes yet)
4. **Approval Dialog** → ApprovalGateDialog displays mutation details for final review
5. **User Confirms** → Triggers `confirmMutation()` callback
6. **Record Creation** → `createBugReportRecord()` or `createEnhancementSuggestionRecord()` writes to Dataverse
7. **Result Display** → MutationResultComponent shows confirmation with Dataverse record ID

**Source Functions:** `app/src/ai/mutations.ts`
