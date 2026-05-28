# CFR Project Management — Deployment Runbook

## Environment Map

| Branch | Environment | URL | Environment ID |
|--------|-------------|-----|----------------|
| `main` | Nexus RCM - DEV | https://nexusrcm-dev.crm.dynamics.com | `731e4975-10cd-4535-b82f-1ff016e59b6c` |
| `uat` | Nexus RCM - UAT | https://nexusrcm-uat.crm.dynamics.com | `69a4a130-ad3b-491e-8dac-7ce7a41a7934` |
| `prod` | Nexus - CVS Finance RevCycle | https://rcm.crm.dynamics.com | `7a0a0d77-0433-4d7e-9480-604d1d24cc6f` |

Env-pinned files are protected by `merge=ours` in `.gitattributes`. Run `git config merge.ours.driver true` once per clone or the merge strategy won't activate.

---

## Prod P4W GUIDs (hardcoded in flow JSON)

| Value | GUID |
|-------|------|
| Work hours template | `6038f6d6-f570-ef11-a670-0022482c38a9` |
| Calendar | `6138f6d6-f570-ef11-a670-0022482c38a9` |
| Org unit | `5638f6d6-f570-ef11-a670-0022482c38a9` |

UAT equivalents: `501397da` / `592d1cba` / `381c82d4` (all `-cf31-f111-88b4-000d3a1d26fa` suffix family).

---

## Pre-deployment Checklist

- [ ] Ensure you are on the correct branch (`uat` or `prod`)
- [ ] Verify env-pinned files have the correct environment values
- [ ] Run `pac auth list` and confirm the correct environment is active (`*`)
- [ ] Run `git config merge.ours.driver true` if working from a fresh clone

---

## Step 1 — Dataverse Solution

### Source of truth — `solution/src/` on `main` only

The full unpacked solution lives in `solution/src/` on the **`main`** branch.
That is the only authoritative copy. Refresh it from DEV with `pac solution
export` + `pac solution unpack` whenever the schema changes.

On `uat` and `prod` the `solution/src/` tree is **pinned to `merge=ours`** in
`.gitattributes`. The copy on those branches is a stale snapshot used only for
diffing/inspection — it is *not* the deploy artifact. The actual deploy uses
a managed zip exported from DEV and patched per-env by
`scripts/patch-managed-solution-for-prod.py`. Stale snapshots on uat/prod
are safe to ignore.

Every table the app reads must be a member of the `CFRProjectManagement`
solution in DEV and appear under `solution/src/Entities/` on `main`. Tables
created in DEV via the maker portal are *not* members automatically — you
must add them, otherwise they will not migrate to UAT/PROD and the app will
hit `Resource not found for the segment '<entity_set>'` errors after migration.

To add a freshly-created DEV table to source:

```powershell
pac auth select --index 1   # switch to DEV profile
pac solution add-solution-component `
  --solutionUniqueName CFRProjectManagement `
  --component <logical_name> `
  --componentType 1 `
  --AddRequiredComponents

# Then re-export + unpack + commit (see "Refresh solution/src/ from DEV" below)
```

### Refresh `solution/src/` from DEV (run on `main` only)

After any schema change in DEV (new table, new column, new flow, new bot
component), refresh the source on **`main`**. Do not run this on `uat` or
`prod` — those branches treat `solution/src/` as a snapshot, not as input
to the deploy.

```powershell
$tmp = "$env:TEMP\CFRUnmanaged.zip"
git checkout main
pac auth select --index 1
pac solution export --name CFRProjectManagement --path $tmp
pac solution unpack --zipfile $tmp --folder solution/src --packagetype Unmanaged
```

### Deploy to UAT / PROD

**DO NOT use `pac solution pack` for deployments that include cloud flows.** pac does not embed modern Power Automate flow definitions when packing from source — `<Workflows />` ends up empty in the zip. Always export from DEV.

```powershell
# 1. Export managed solution from DEV
pac auth select --index 1   # switch to DEV profile
pac solution export --name CFRProjectManagement --path "$env:TEMP\CFRManaged.zip" --managed

# 2. Patch the zip for the target environment (run the patch script below)

# 3. Switch to target and import
pac auth select --name "Nexus-PROD"   # or Nexus RCM - UAT
pac solution import --path "$env:TEMP\CFRPatched.zip" --async --activate-plugins
```

### Patch Script (PowerShell)

Updates the Mira bot URL and P4W GUIDs in-memory before import. Adjust the substitution pairs for UAT vs prod.

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.IO.Compression

$srcZip = "$env:TEMP\CFRManaged.zip"
$dstZip = "$env:TEMP\CFRPatched.zip"
Copy-Item $srcZip $dstZip -Force

$zip = [System.IO.Compression.ZipFile]::Open($dstZip, 'Update')

function Update-ZipEntry($zip, $entryName, $transform) {
    $entry = $zip.Entries | Where-Object { $_.FullName -eq $entryName }
    if (-not $entry) { "⚠ Not found: $entryName"; return }
    $reader = [System.IO.StreamReader]::new($entry.Open())
    $content = $reader.ReadToEnd()
    $reader.Dispose()
    $newContent = & $transform $content
    $entry.Delete()
    $newEntry = $zip.CreateEntry($entryName)
    $writer = [System.IO.StreamWriter]::new($newEntry.Open())
    $writer.Write($newContent)
    $writer.Dispose()
    "✓ Updated: $entryName"
}

# Mira bot URL
Update-ZipEntry $zip "botcomponents/pmo_mira.action.CreateIntakeRecord/data" {
    param($c) $c -replace 'https://nexusrcm-dev\.crm\.dynamics\.com/', 'https://rcm.crm.dynamics.com/'
}

# Flow P4W GUIDs (DEV → prod)
$flowEntry = ($zip.Entries | Where-Object { $_.FullName -like "*CFRIntaketo*" }).FullName
Update-ZipEntry $zip $flowEntry {
    param($c)
    $c = $c -replace '75f05144-1cb0-f011-bbd3-6045bdeb6f62', '6138f6d6-f570-ef11-a670-0022482c38a9'  # calendar
    $c = $c -replace '71f05144-1cb0-f011-bbd3-6045bdeb6f62', '6038f6d6-f570-ef11-a670-0022482c38a9'  # work hours
    $c = $c -replace '67f05144-1cb0-f011-bbd3-6045bdeb6f62', '5638f6d6-f570-ef11-a670-0022482c38a9'  # org unit (bare GUID, no @odata.bind)
    # Remove fields the prod connector no longer accepts
    $c = $c -replace ',\s*"item/msdyn_schedulemode":\s*\d+', ''
    $c = $c -replace ',\s*"item/msdyn_copy_teammembers_options":\s*\d+', ''
    $c = $c -replace ',\s*"item/pmo_convertedproject@odata\.bind":[^,}]+', ''
    $c
}

# Strip msdyn_project LocalizedNames (prod P4W version has IsRenameable=0)
$custEntry = $zip.Entries | Where-Object { $_.FullName -eq "customizations.xml" }
$reader = [System.IO.StreamReader]::new($custEntry.Open())
$content = $reader.ReadToEnd()
$reader.Dispose()
$opts = [System.Text.RegularExpressions.RegexOptions]::Singleline
$pattern = '(<entity Name="msdyn_project">)\s*(<LocalizedNames>.*?</LocalizedNames>)?\s*(<LocalizedCollectionNames>.*?</LocalizedCollectionNames>)?\s*(<Descriptions>.*?</Descriptions>)?\s*(<attributes>)'
$newContent = [System.Text.RegularExpressions.Regex]::Replace($content, $pattern, '$1$5', $opts)
$custEntry.Delete()
$newEntry = $zip.CreateEntry("customizations.xml")
$writer = [System.IO.StreamWriter]::new($newEntry.Open())
$writer.Write($newContent)
$writer.Dispose()
"✓ Stripped msdyn_project LocalizedNames"

$zip.Dispose()
"Done — patched zip at $dstZip"
```

### Managed vs Unmanaged

- **Prod always uses managed.** If prod already has a managed solution installed, re-importing a newer managed version works fine (upgrade in place).
- If prod has an **unmanaged** solution and you need to switch to managed: `pac solution delete --solution-name CFRProjectManagement` first (components stay, only the solution container is removed), then import managed.
- DEV and UAT can stay unmanaged. UAT solution packs with `pac solution pack` work fine for non-flow components.

---

## Step 2 — Code App

```powershell
# From the app/ directory, on the correct branch
cd app
npm run build
pac code push
```

`pac code push` writes the `appId` back to `power.config.json` automatically. Commit that change after push.

---

## Step 3 — After Import (Manual)

### 3a. Wire the flow connection

After every managed import that includes the flow:

1. Go to [make.powerautomate.com](https://make.powerautomate.com) → select the target environment
2. Find **PMO CFR Intake to Project Conversion**
3. Edit → fix the Dataverse connection reference → Save
4. Turn the flow **On**

### 3b. Enable schedule mode override in Project Parameters

After every fresh managed install (only needed if the environment is brand new or the record was reset):

1. Go to [make.powerapps.com](https://make.powerapps.com) → select the target environment
2. **Tables → Project Parameters → Data**
3. Open the single record and set **Allow Schedule Mode Override = Yes**
4. Save

This is already `True` in DEV and was set in prod on 2026-05-19. A managed solution import will not reset it, so this step is only needed on a fresh environment.

### 3c. Flag PMO teams

In the maker portal → **Tables → Team → Data**, set **PMO Team = Yes** on:

- Business Intelligence
- Systems Improvement
- Process & Project
- Payer Initiatives
- Training
- Risk Management
- Business Excellence

These teams must exist in the environment first. If they don't, create them before flagging.

---

## Known Gotchas

### `pac solution pack` drops cloud flows
`pac solution pack` produces `<Workflows />` (empty) regardless of what's in `solution/src/Workflows/`. Always export from DEV with `pac solution export --managed` to get a zip that actually contains the flow definitions.

### msdyn_project "Entity Display Name cannot be modified"
The prod (and UAT) P4W installation has `IsRenameable=0` on `msdyn_project`. Any solution zip that includes `<LocalizedNames>` inside the `msdyn_project` entity block will fail. The patch script above strips these automatically.

### Type-29 RootComponent "not in the target system" (unmanaged)
Cloud flows (type 29) cannot be injected into a new environment via an **unmanaged** solution import. They must arrive via a managed solution. If you see this error on an unmanaged import, it is expected — switch to the managed export+import flow described above.

### Managed over unmanaged conflict
Dataverse refuses to import a managed solution if the same solution is already installed as unmanaged. Delete the unmanaged solution first (`pac solution delete`), then import managed.

### OData filter breaks on team names with `&`
Teams like "Process & Project" will break a `$filter=name eq '...'` query because `&` is a URL delimiter. Fetch all teams and filter client-side in PowerShell instead:
```powershell
$allTeams = (Invoke-RestMethod "$base/teams?`$select=teamid,name&`$filter=teamtype eq 0&`$top=500" -Headers $hdr).value
$match = $allTeams | Where-Object { $_.name -eq "Process & Project" }
```

### "Schedule Mode must match Project Parameters" on project create
Prod P4W has `AllowScheduleModeOverride = false`. Any solution zip that passes `item/msdyn_schedulemode` in the flow's Create Project action will fail with a 400 from `PreValidateProjectCreate`. The patch script strips this field automatically — do not re-add it.

### MSAL token cache
pac CLI tokens live in `C:\Users\<you>\AppData\Local\Microsoft\PowerAppsCLI\tokencache_msalv3.dat` (DPAPI-encrypted). Tokens from the cache give 401 against the Dataverse Web API when obtained via a v1 refresh token exchange — use the cached access token directly (check `expires_on` first), or just run a pac command to force a fresh token into the cache before scripting.

---

## One-off record patches via pac MSAL cache (no SPN secret)

When you need to PATCH a single Dataverse record (e.g. backfilling `pmo_currentstagenumber` after a bugfix) and don't want to use the SPN client-credentials pattern, use `scripts/pac-patch-record.py`. It reads pac's DPAPI-encrypted MSAL cache and calls the Web API as you.

Prerequisites (one-time): `pip install pywin32`

Procedure:

```powershell
# 1. Force a fresh token for the target env into the pac cache
pac auth select --name "Nexus-PROD"     # or --index 1 for DEV
pac org who                             # any pac command triggers a refresh

# 2. Look up the record id. Reuse the same token-loading helper inside
#    pac-patch-record.py to issue a GET. Example filter:
#      GET /api/data/v9.2/pmo_projectrequests
#          ?$select=pmo_projectrequestid,pmo_currentstagenumber
#          &$filter=pmo_autonumber eq 'REQ-2026-1016'

# 3. Run the patch. NOTE the JSON has NO spaces — cmd.exe treats unquoted
#    whitespace as an argument separator and the script will print --help.
python scripts/pac-patch-record.py `
    https://rcm.crm.dynamics.com `
    pmo_projectrequests `
    <record_guid> `
    '{"pmo_currentstagenumber":4}'
```

Gotchas:
- **JSON quoting on Windows.** From cmd.exe / Git Bash, escape inner double-quotes (`"{\"pmo_currentstagenumber\":4}"`) and keep no spaces in the JSON. From PowerShell, single-quote the whole JSON arg.
- **URL encoding for GETs.** Run filter strings through `urllib.parse.quote(q, safe="?$=&',")` — `$` and `'` must survive, spaces must not.
- **Token must be fresh.** The helper rejects tokens within 30s of expiry. If you see "NO TOKEN for ...", re-run `pac auth select` + `pac org who` for the env you need. Each env has its own cache entry.
- **`If-Match: *` is set.** PATCH-only, never insert — wrong GUID returns 404 instead of creating a phantom record.
- **One user only.** DPAPI ties the cache to the Windows account that ran pac. Don't try to read it as another user or from WSL.

Logged uses:
- 2026-05-26 — backfilled REQ-2026-1016 in PROD (`pmo_currentstagenumber 5 → 4`) after deploying the off-by-one fix (commit 522768d). DEV's record with the same autonumber was a different unaffected record (already at stage 1).

---

## Deployment Sequence Summary

```
1. git checkout prod (or uat)
2. Merge feature branch from main
3. pac auth select --name "Nexus-PROD"
4. Export managed from DEV → patch zip → import to prod   (~10 min)
5. cd app && npm run build && pac code push                (~2 min)
6. git add app/power.config.json && git commit             (appId updated by pac)
7. [Manual] Wire flow connection in Power Automate
8. [Manual] Enable Allow Schedule Mode Override in Project Parameters (fresh env only)
9. [Manual] Flag PMO teams in maker portal
```
