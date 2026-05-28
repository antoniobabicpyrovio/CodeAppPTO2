# Prod Unmanaged Layers Log

Any time someone manually edits a component in the Nexus - CVS Finance RevCycle environment
(outside of a solution import), it creates an unmanaged customization layer on top of the
managed solution. These need to be tracked so they can be folded back into source control
and redeployed properly in the next cycle.

An unmanaged layer means: if the managed solution is ever deleted, that component is
deleted too — but the unmanaged edits are lost. It also means future managed imports
of that component won't overwrite the unmanaged layer automatically.

---

## Active Unmanaged Layers

| Date | Component | Type | Who | What Changed | Resolution |
|------|-----------|------|-----|--------------|------------|
| 2026-05-19 | `PMO CFR Intake to Project Conversion` (flow) | Cloud Flow | Antonio Babic | Wired Dataverse connection reference; removed 3 stale connector fields (`msdyn_contractorganizationalunitid@odata.bind`, `msdyn_copy_teammembers_options`, `pmo_convertedproject@odata.bind`); removed `msdyn_schedulemode` (prod P4W requires override to be disabled — field must be dropped from connector call). Turned flow On. | Flow JSON + patch script updated on `antonio/quick-bugfix` branch. DEV flow must be updated to match before next export. |
| 2026-05-19 | `pmo_projectrequest.pmo_stagedatajson` (column) | Table Column | Claude (automated) | Created Memo (ntext, MaxLength=1048576) column directly in prod via metadata API — existed in DEV as unmanaged, not in the managed solution export. | Column definition added to `solution/src/Entities/pmo_ProjectRequest/Entity.xml` on `antonio/quick-bugfix`. Must also be added to DEV solution in maker portal (Tables → Project Request → Columns → Add existing → pmo_stagedatajson → Save to solution). Then re-export managed. |
| 2026-05-19 | `msdyn_projectparameter` (Project Parameters) | Config Record | Claude (automated) | Set `msdyn_allowschedulemodeoverride = True` directly in prod. DEV already has this set to True. Not part of the managed solution — must be set manually per environment after each fresh deploy. | Add to Step 3 (post-deploy manual steps) in runbook. No code change needed. |

---

## How to Clear an Unmanaged Layer

1. Make the equivalent change in DEV (update the flow/component there).
2. Export managed from DEV, patch for prod, import to prod — this overwrites the unmanaged layer with a managed one.
3. Remove the row from this table once the managed deploy has landed.

---

## Resolved Layers

| Date | Component | Resolution |
|------|-----------|------------|
| 2026-05-20 | `pmo_telemetryevent` + `pmo_userfeedback` (tables) — never members of the `CFRProjectManagement` solution in DEV, so they never migrated to PROD. PROD app crashed with `Resource not found for the segment 'pmo_telemetryevents'` / `'cr741_pmo_userfeedbacks'`. | Added both tables to the DEV solution via `pac solution add-solution-component`. Re-exported + unpacked the full DEV solution into `solution/src/`. Committed on `prod` branch. Next prod managed import will create the tables and entity sets, fixing the change-history and user-feedback pages without any code change. |
