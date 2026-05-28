# Enable Notes on `pmo_projectrequest`

## Symptom

Uploading a Business Case or Project Charter artifact from the intake wizard
fails with:

```
{"error":{"code":"0x80048d19","message":"...An undeclared property
'objectid_pmo_projectrequest' which only has property annotations in the
payload but no property value was found..."}}
```

## Root cause

The intake artifact upload flow creates a Dataverse `annotation` row whose
polymorphic `objectid` lookup points back at the parent `pmo_projectrequest`.
The OData payload binds via the navigation property
`objectid_pmo_projectrequest@odata.bind`. That navigation property only exists
on the annotation table **when Notes are enabled on the target table**. If the
target table has `HasRelatedNotes=False` (default), OData rejects the bind as an
"undeclared property" — which is what 0x80048d19 reports.

User Feedback (`pmo_userfeedback`) hit the exact same error and was fixed by
commit `4b1ec99` ("chore(solution): enable notes on pmo_userfeedback"). The
same fix needs to be applied to `pmo_projectrequest`.

## Fix

This is a schema change — it cannot be made from app code. The Notes toggle is
flipped in the DEV maker portal, then carried to UAT/PROD via the standard
managed-solution export / import flow.

### Step 1 — Enable Notes in DEV

1. Open the DEV environment in the maker portal:
   https://make.powerapps.com → switch environment to **CFR PMO Dev**.
2. **Tables** → search for **Project Request** (logical name `pmo_projectrequest`).
3. Click the table → **Properties** → expand **Advanced options**.
4. Check **Enable attachments (including notes and files)**.
5. **Save**.

You can verify by opening the table's metadata in your browser:

```
https://<dev-org>.crm.dynamics.com/api/data/v9.2/EntityDefinitions(LogicalName='pmo_projectrequest')?$select=HasNotes,HasActivities
```

`HasNotes` should now be `true`.

### Step 2 — Re-export + unpack into `solution/src/`

From the repo root, on `main`:

```bash
# Export unmanaged from DEV
pwsh ./scripts/export-solution.ps1

# Unpack into solution/src/ so the change is committed to git
pac solution unpack \
  --zipfile <exported.zip> \
  --folder ./solution/src \
  --packagetype Unmanaged \
  --allowDelete --allowWrite
```

Verify the change landed:

```bash
git diff solution/src/Entities/pmo_ProjectRequest/Entity.xml
# Expect to see a new line:
#   <HasRelatedNotes>True</HasRelatedNotes>
```

Commit on `main`:

```bash
git add solution/src/Entities/pmo_ProjectRequest/Entity.xml
# Plus any side-effect files pac unpack rewrites (bot data, flow casing, etc.)
git commit -m "chore(solution): enable notes on pmo_projectrequest"
```

### Step 3 — Deploy to UAT / PROD

Follow the standard managed-solution flow:

```bash
# Export managed from DEV
pwsh ./scripts/export-solution.ps1 -Managed

# Patch the managed zip for the target environment
python scripts/patch-managed-solution-for-prod.py <managed.zip>

# Import into target
pwsh ./scripts/import-solution.ps1 -ZipPath <patched.zip> -Environment prod
```

### Step 4 — Verify

In PROD, open the intake wizard for a Project / Program request, advance to a
stage that requires a Business Case or Project Charter artifact, and upload a
file. Expected:

- Toast: `<filename> uploaded`
- Annotation appears in the Attachments list
- No 0x80048d19 in the browser console

## Why this can't be done from app code

The error comes from Dataverse's OData layer rejecting the request payload
before it reaches any application logic. The polymorphic
`objectid_<logicalname>` navigation property is generated server-side from the
target table's metadata. There is no client-side workaround — the table must
declare `HasRelatedNotes=True` for the bind to be a valid OData property.

## Related files

- `app/src/api/intakeAttachments.api.ts` — defines the polymorphic bind pattern
- `solution/src/Entities/pmo_UserFeedback/Entity.xml` — reference implementation
  that already has `<HasRelatedNotes>True</HasRelatedNotes>`
- Commit `4b1ec99` — prior fix for the same error on `pmo_userfeedback`
