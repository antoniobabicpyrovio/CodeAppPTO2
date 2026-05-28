# Schema & Environment Snapshot

Generated: 2026-04-21 | Source: `app/src/lib/constants.ts`, `app/src/models/*.model.ts`

This snapshot captures the Dataverse entity sets, key fields, option set values, and environment-specific mappings used by the PMO CFR Solution app. It is a reference artifact for coding agents and must be kept current with active implementation.

---

## Entity Sets

Registered in `ENTITY_SETS` at `app/src/lib/constants.ts`.

### CFR Custom Tables (`pmo_` prefix)

| Constant | Entity Set | Logical Name | Model File | Purpose |
|----------|-----------|--------------|------------|---------|
| `projectRequest` | `pmo_projectrequests` | `pmo_projectrequest` | `projectRequest.model.ts` | Universal intake / request |
| `projectTeam` | `pmo_projectteams` | `pmo_projectteam` | `projectTeam.model.ts` | Project ↔ team junction (Primary / Contributing) |
| `appSetting` | `pmo_appsettings` | `pmo_appsetting` | (inline in hook) | Administrator key-value config |

### P4W + Accelerator Tables

| Constant | Entity Set | Logical Name | Model File | Purpose |
|----------|-----------|--------------|------------|---------|
| `project` | `msdyn_projects` | `msdyn_project` | `project.model.ts` | Core project record |
| `program` | `msdyn_projectprograms` | `msdyn_projectprogram` | `program.model.ts` | Program record |
| `statusReport` | `msdyn_projectstatusreports` | `msdyn_projectstatusreport` | `statusReport.model.ts` | Status reporting |
| `projectTask` | `msdyn_projecttasks` | `msdyn_projecttask` | `projectTask.model.ts` | WBS tasks |
| `projectTaskDependency` | `msdyn_projecttaskdependencies` | `msdyn_projecttaskdependency` | `projectTaskDependency.model.ts` | F2S dependencies |
| `resourceAssignment` | `msdyn_resourceassignments` | `msdyn_resourceassignment` | `resourceAssignment.model.ts` | Task resource assignments |
| `bookableResource` | `bookableresources` | `bookableresource` | `bookableResource.model.ts` | Resource records |
| `projectBucket` | `msdyn_projectbuckets` | `msdyn_projectbucket` | `projectBucket.model.ts` | Task buckets |
| `projectTeamMember` | `msdyn_projectteams` | `msdyn_projectteam` | `projectTeamMember.model.ts` | P4W native team member records |
| `projectRisk` | `msdyn_projectrisks` | `msdyn_projectrisk` | `projectRisk.model.ts` | Risk tracking |
| `projectIssue` | `msdyn_projectissues` | `msdyn_projectissue` | `projectIssue.model.ts` | Issue tracking |
| `projectChange` | `msdyn_projectchanges` | `msdyn_projectchange` | `projectChange.model.ts` | Change tracking |
| `projectChecklist` | `msdyn_projectchecklists` | `msdyn_projectchecklist` | `projectChecklist.model.ts` | Task checklists |
| `projectLabel` | `msdyn_projectlabels` | `msdyn_projectlabel` | `projectLabel.model.ts` | Task labels (25 slots) |
| `projectTaskToLabel` | `msdyn_projecttasktolabels` | `msdyn_projecttasktolabel` | `projectLabel.model.ts` | Task ↔ label junction |
| `projectSprint` | `msdyn_projectsprints` | `msdyn_projectsprint` | `projectSprint.model.ts` | Sprint / iteration records |

### System Tables

| Constant | Entity Set | Logical Name | Purpose |
|----------|-----------|--------------|---------|
| `organization` | `organizations` | `organization` | Org settings (calendar ID, org ID) |
| `systemUser` | `systemusers` | `systemuser` | User records |
| `team` | `teams` | `team` | Dataverse system teams |
| `documentHeader` | `msdyn_documentheaders` | `msdyn_documentheader` | Document headers |
| `crSystem` | `cr87a_systems` | `cr87a_system` | Central system catalog |
| `annotation` | `annotations` | `annotation` | Notes / file attachments |

---

## Environment-Specific Mappings

### PMO Team Flag Column

| Environment | Column Name | Notes |
|-------------|------------|-------|
| DEV | `cr741_pmoteam` | Existing column, not owned by CFRProjectManagement solution |
| UAT / PROD | `pmo_pmoteam` | Must be created in solution XML before promotion |

**Code reference:** `PMO_TEAM_FLAG` constant in `app/src/lib/constants.ts`

**Pre-UAT gate:** Before deploying to UAT:
1. Add `pmo_pmoteam` (Boolean) to `team` entity in `CFRProjectManagement` solution XML
2. Import solution to UAT
3. Populate the flag on all PMO teams in UAT
4. Update `PMO_TEAM_FLAG` constant from `'cr741_pmoteam'` to `'pmo_pmoteam'`

### Tenant

| Key | Value |
|-----|-------|
| Tenant ID | `fabb61b8-3afe-4e75-b934-a47f782b8cd7` |
| Planner base URL | `https://planner.cloud.microsoft/webui/premiumplan/` |
| Planner board suffix | `/view/board` |

### Environment URLs (PAC Auth Profiles)

| Environment | Profile Pattern | URL |
|-------------|----------------|-----|
| DEV | `nexusrcm-dev-sp` | `https://nexusrcm-dev.crm.dynamics.com` |
| UAT | `nexusrcm-uat-sp` | `https://nexusrcm-uat.crm.dynamics.com` |
| SUP | `nexusrcm-sup-sp` | `https://nexusrcm-sup.crm.dynamics.com` |
| PROD | `rcm-prod-sp` | `https://rcm.crm.dynamics.com` |

---

## OData Bind Syntax Reference

All lookup binds use **NavigationPropertyName** (PascalCase schema name from solution XML), not the lowercase logical name.

### msdyn_project Lookups

| NavigationPropertyName | Target Entity Set | Usage |
|----------------------|------------------|-------|
| `msdyn_projectmanager` | `systemusers` | PM assignment |
| `msdyn_Program` | `msdyn_projectprograms` | Program linkage |
| `proj_ExecutiveSponsor` | `systemusers` | Executive sponsor |
| `proj_Manager` | `systemusers` | Functional manager |
| `pmo_PrimaryTeam` | `teams` | Primary team assignment |
| `pmo_RequestSource` | `pmo_projectrequests` | Originating intake request |

### msdyn_projectprogram Lookups

| NavigationPropertyName | Target Entity Set | Usage |
|----------------------|------------------|-------|
| `proj_Manager` | `systemusers` | Program manager |

### pmo_projectrequest Lookups

| NavigationPropertyName | Target Entity Set | Usage |
|----------------------|------------------|-------|
| `pmo_RequestedBy` | `systemusers` | Requester |
| `pmo_TargetTeam` | `teams` | Routed team |
| `pmo_ConvertedProject` | `msdyn_projects` | Linked project after conversion |
| `pmo_ApprovedBy` | `systemusers` | Approver |
| `pmo_AffectedSystem` | `cr87a_systems` | System catalog reference |
| `pmo_ParentRequest` | `pmo_projectrequests` | Self-referential duplicate/related |

### pmo_projectteam Lookups

| NavigationPropertyName | Target Entity Set | Usage |
|----------------------|------------------|-------|
| `pmo_Project` | `msdyn_projects` | Project reference |
| `pmo_Team` | `teams` | Team reference |

---

## Option Set Constants

All defined in `app/src/lib/constants.ts`.

### Task Priority (`msdyn_projecttask.msdyn_priority`)

| Label | Value | Planner equivalent |
|-------|-------|-------------------|
| Urgent | 1 | Urgent |
| Important | 3 | Important |
| Medium | 5 | Medium (default) |
| Low | 9 | Low |

### Request Type (`pmo_projectrequest.pmo_requesttype`)

| Label | Value |
|-------|-------|
| NewProject | 893460000 |
| ChangeRequest | 893460001 |
| Enhancement | 893460002 |
| Support | 893460003 |

### Request Priority (`pmo_projectrequest.pmo_priority`)

| Label | Value |
|-------|-------|
| Critical | 893460010 |
| High | 893460011 |
| Medium | 893460012 |
| Low | 893460013 |

### Request Status (`pmo_projectrequest.pmo_status`)

| Label | Value |
|-------|-------|
| Draft | 893460020 |
| Submitted | 893460021 |
| InTriage | 893460022 |
| Approved | 893460023 |
| Rejected | 893460024 |
| Converted | 893460025 |
| AwaitingClarification | 893460026 |
| RoutedOperational | 893460027 |
| Redirected | 893460028 |

### Clarification State (`pmo_projectrequest.pmo_clarificationstate`)

| Label | Value |
|-------|-------|
| None | 0 |
| PendingRequester | 1 |
| PendingPMO | 2 |
| Resolved | 3 |

### Outcome Category (`pmo_projectrequest.pmo_outcomecategory`)

| Label | Value |
|-------|-------|
| Project | 0 |
| Operational | 1 |
| Redirect | 2 |
| Declined | 3 |

### Line of Business (`pmo_projectrequest.pmo_lineofbusiness`)

| Label | Value |
|-------|-------|
| Enteral | 893460100 |
| InfusionEpic | 893460101 |
| InfusionMediAR | 893460102 |
| All | 893460103 |

### Source System (`pmo_projectrequest.pmo_sourcesystem`)

| Label | Value |
|-------|-------|
| CfrPmo | 893460030 |
| BiPmoTool | 893460031 |
| External | 893460032 |

### Team Role (`pmo_projectteam.pmo_role`)

| Label | Value |
|-------|-------|
| Primary | 893460040 |
| Contributing | 893460041 |

### CFR Category (`msdyn_project.pmo_cfrcategory`)

| Label | Value |
|-------|-------|
| ItInfrastructure | 893460050 |
| FinanceSystems | 893460051 |
| Compliance | 893460052 |
| DataAndAnalytics | 893460053 |
| Operations | 893460054 |
| Other | 893460055 |

### Complexity (`msdyn_project.pmo_complexity`)

| Label | Value |
|-------|-------|
| Low | 893460060 |
| Medium | 893460061 |
| High | 893460062 |
| Critical | 893460063 |

### Strategic Priority (`msdyn_project.pmo_strategicpriority`)

| Label | Value |
|-------|-------|
| MustHave | 893460070 |
| ShouldHave | 893460071 |
| NiceToHave | 893460072 |

### Overall Health (`proj_overallhealth`)

| Label | Value |
|-------|-------|
| OnTrack | 189330000 |
| AtRisk | 189330001 |
| OffTrack | 189330002 |

### Program Type (`msdyn_projectprogram.proj_programtype`)

| Label | Value |
|-------|-------|
| Customer | 189330000 |
| Development | 189330001 |
| Support | 189330002 |
| Enhancement | 189330003 |
| Program | 189330004 |
| Other | 189330005 |

### Program Goals (`msdyn_projectprogram.proj_programgoals`)

| Label | Value |
|-------|-------|
| CustomerSatisfaction | 189330000 |
| GrowBusiness | 189330001 |
| RunBusiness | 189330002 |
| Transformation | 189330003 |
| Other | 189330004 |

### Program Business Unit (`msdyn_projectprogram.proj_businessunit`)

| Label | Value |
|-------|-------|
| Enteral | 189330000 |
| Epic | 189330001 |
| InfusionLegacy | 189330002 |
| Medicare | 153480001 |

### Risk Category (`msdyn_projectrisk.proj_riskcategory`)

| Label | Value |
|-------|-------|
| Stakeholder | 189330000 |
| Scope | 189330001 |
| Change | 189330002 |
| Resources | 189330003 |
| Design | 189330004 |
| Technical | 189330005 |
| Other | 189330006 |

### Accelerator State (`proj_state` — shared by risk, issue, change)

| Label | Value |
|-------|-------|
| Proposed | 189330000 |
| Active | 189330001 |
| Closed | 189330002 |
| OnHold | 189330003 |

### Issue Category (`msdyn_projectissue.proj_issuecategory`)

| Label | Value |
|-------|-------|
| Issue | 189330000 |
| Task | 189330001 |
| Bug | 189330002 |
| Other | 189330003 |

### Accelerator Priority (`proj_priority` — shared by issue, change)

| Label | Value |
|-------|-------|
| Critical | 189330000 |
| High | 189330001 |
| Moderate | 189330002 |
| Low | 189330003 |

### Change Type (`msdyn_projectchange.proj_changetype`)

| Label | Value |
|-------|-------|
| Scope | 189330000 |
| Schedule | 189330001 |
| Cost | 189330002 |
| None | 189330003 |

### Change Impact (`msdyn_projectchange.proj_changeimpact`)

| Label | Value |
|-------|-------|
| High | 189330000 |
| Medium | 189330001 |
| Low | 189330002 |

### Change Risk (`msdyn_projectchange.proj_changerisk`)

| Label | Value |
|-------|-------|
| High | 189330000 |
| Moderate | 189330001 |
| Low | 189330002 |
| None | 189330003 |

### Change Approval (`msdyn_projectchange.proj_changeapproval`)

| Label | Value |
|-------|-------|
| NotYetRequested | 189330000 |
| Requested | 189330001 |
| Approved | 189330002 |
| Rejected | 189330003 |

---

## Admin Settings Keys

Stored in `pmo_appsettings` as key-value pairs.

| Key | Purpose | Value Type |
|-----|---------|------------|
| `pmo.fallback_triage_team_id` | Fallback team GUID for intake routing when confidence is low | Team GUID |
| `pmo.user_scope_aad_group_id` | AAD security group object ID for scoping user dropdowns | AAD group object ID (environment-stable) |

---

## PSS (Project Scheduling Service) Reference

All task/bucket/dependency/assignment writes go through PSS OperationSet pattern in `app/src/lib/schedulingClient.ts`.

### Supported Entity + Operation Combinations

| Entity | Create | Update | Delete |
|--------|--------|--------|--------|
| `msdyn_projecttask` | Yes | Yes | Yes |
| `msdyn_projectbucket` | Yes | Yes | Yes |
| `msdyn_projecttaskdependency` | Yes | No | Yes |
| `msdyn_resourceassignment` | Yes | No | Yes |
| `msdyn_projectteam` (member) | Yes (via `msdyn_CreateTeamMemberV1`) | No | Yes (deactivate) |
| `msdyn_projectchecklist` | Yes | Yes | Yes |
| `msdyn_projectlabel` | No | Yes (rename only) | No |
| `msdyn_projecttasktolabel` | Yes (assign) | No | Yes (remove) |
| `msdyn_projectsprint` | No | Yes (assign task) | No |
| `msdyn_project` | No | Yes (schedule fields only) | No |

### PSS Persistence Delay Calibration

| Operation | Delay (ms) | Source |
|-----------|-----------|--------|
| Task create | 14,000 | P90 from Microsoft benchmarks |
| Task update | 20,000 | P90 from Microsoft benchmarks |
| Task delete | 11,000 | P90 from Microsoft benchmarks |
| General OperationSet | ~20,000–22,000 | Observed during PSS API validation |

### Key Functions

| Function | Purpose |
|----------|---------|
| `createProjectTask(params)` | Create task via PSS |
| `updateProjectTask(params, projectId)` | Update task via PSS |
| `deleteProjectTask(taskId, projectId)` | Delete task via PSS |
| `applyProjectTemplate(projectId, tasks)` | Batch-create WBS tasks from template |
| `updateProjectSchedule(params)` | Update project schedule dates via PSS |
| `createScheduledBucket(params)` | Create bucket via PSS |
| `createProjectTaskDependency(...)` | Create F2S dependency |
| `createResourceAssignment(...)` | Assign resource to task |
| `createProjectTeamMember(...)` | Add team member via `msdyn_CreateTeamMemberV1` |

---

## Dataverse Client Functions

Registered in `app/src/lib/dataverseClient.ts`.

| Function | Signature | Purpose |
|----------|-----------|---------|
| `list<T>` | `(entitySetName, params?) → T[]` | OData list with filter/select/orderby/top |
| `get<T>` | `(entitySetName, id, select?) → T` | Single record retrieval |
| `create<T>` | `(entitySetName, payload) → T` | Create record |
| `update` | `(entitySetName, id, payload) → void` | PATCH update |
| `deactivate` | `(entitySetName, id) → void` | Set `statecode=1` |
| `remove` | `(entitySetName, id) → void` | Hard delete |
| `executeAction<TReq, TRes>` | `(entitySetName, actionName, payload) → TRes` | Bound/unbound action |
| `getOrganizationId` | `() → string` | Org ID for Planner deep links |
| `getCurrentUserId` | `() → string` | Current user GUID |

---

## User Search Configuration

### Noise Filter (Default)

Applied to all user dropdowns via `searchUsers` callback:

```
isdisabled eq false
and accessmode ne 4   (exclude Support Users)
and accessmode ne 5   (exclude Delegated Admins)
and applicationid eq null  (exclude service accounts / application IDs)
```

### AAD Group Scoping

When `pmo.user_scope_aad_group_id` is set in admin settings:
1. Resolve AAD group object ID → Dataverse team GUID via `azureactivedirectoryobjectid` column on `teams` entity
2. Filter users by `teammembership_association/any(t: t/teamid eq '{teamGuid}')`
3. This is ALM-safe — the AAD group object ID is stable across environments; only the team GUID differs

### Manager Restriction

When a Primary Team is set on a project, the Manager dropdown restricts to team membership:
- Filter: `teammembership_association/any(t: t/teamid eq '{primaryTeamId}')`
- Includes team admin/owner via same membership association
