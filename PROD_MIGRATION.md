# Production Migration Checklist

Items that must be completed before the app is ready for production use on the Pyrovio tenant.

---

## 1. Enable Code Apps on the Production Environment

**Blocked by:** IT  
**Details:** Code Apps (preview) must be enabled on the "Enovio, LLC (Upgrade)" environment (`Default-add0151d-6436-4f59-a424-e401b0363d09`, `https://org080891e6.crm.dynamics.com/`).

**Steps for IT:**
1. Power Platform Admin Center → Environments → "Enovio, LLC (Upgrade)"
2. Settings → Product → Features → enable "Allow publishing of canvas apps as Code apps (preview)"
3. Save

Once enabled, deploy with:
```powershell
pac auth select --index 2   # Antonio.Babic@pyrovio.com → org080891e6
cd <project>/app
npm run build
git add . && git commit -m "deploy to production" && git push
pac code push
```

---

## 2. Replace Hardcoded Admin Emails with Dynamic Role Check

**File:** `app/src/providers/ConfigurationProvider.tsx`  
**Current state:** `HARDCODED_ADMINS` is hardcoded to `antonio.babic@pyrovio.com` and `antonio.babic@pyroviosandbox.onmicrosoft.com` because it was the only way to get admin access during Sandbox testing.

**What needs to change:** Remove the hardcoded emails. Admin access should be determined solely by whether the user's email appears in the `CodeAppPTOSupervisors` SharePoint list. Any supervisor in that list should automatically get admin access.

```typescript
// Remove this:
const HARDCODED_ADMINS = new Set([
  'antonio.babic@pyroviosandbox.onmicrosoft.com',
  'antonio.babic@pyrovio.com',
]);

// And remove the hardcoded check in resolveAdminRole:
if (HARDCODED_ADMINS.has(email)) return 'system_admin';
```

After this change, only users listed in `CodeAppPTOSupervisors` will have admin access.  
Make sure `Antonio.Babic@pyrovio.com` (and any other admins) are added to that SharePoint list before removing the hardcoded fallback.

---

## 3. Remove Demo Fallback Data

**File:** `app/src/lib/sharePointListClient.ts`  
**Current state:** `DEMO_BALANCES`, `DEMO_REQUESTS`, and `DEMO_SUPERVISORS` are returned automatically when SharePoint returns 401/403. This was added so the Sandbox demo would show data even without SharePoint access.

**What needs to change:** Once deployed to production with a `@pyrovio.com` account that has real SharePoint access, remove the demo fallback and let real errors surface.

Delete the demo data constants and the `isAccessDenied` fallback branches:

```typescript
// Remove the DEMO_* constants and isAccessDenied() helper

// Change each function from:
if (isAccessDenied(res.status)) return DEMO_BALANCES;
if (!res.ok) throw new Error(...)

// Back to just:
if (!res.ok) throw new Error(...)
```

---

## 4. Remove Dataverse References from power.config.json

**File:** `app/power.config.json`  
**Current state:** The config still has `databaseReferences` with `systemusers`, `roles`, `teams`, `organizations` — legacy from the original PMO app.

**What needs to change:** Clear the `databaseReferences` section since the app no longer uses Dataverse for any data. This will prevent misleading connection prompts when the app is imported into production.

```json
"databaseReferences": {}
```

---

## 5. Verify SharePoint Column Names Match the App

**Lists:** `CodeAppPTORequests`, `CodeAppPTOBalances`, `CodeAppPTOSupervisors`  
**Current state:** The app maps SharePoint `fields.*` to interface properties assuming column internal names match exactly (e.g., `StartDate`, `EndDate`, `EmployeeId`, etc.). These were set up in Sandbox and may need verification against the production lists.

**Action:** After first production deploy, check browser console for any field mapping errors and align `sharePointListClient.ts` field names to match the actual SharePoint column internal names.

---

## 6. User-Specific Data Filtering

**Current state:** PTO Requests and PTO Balances show ALL records for ALL employees. This was intentional during Sandbox testing ("show everything for now").

**What needs to change for production:**
- Regular users should only see their own requests and balance
- Supervisors/admins should see all employees' data

This requires filtering by the current user's identity:
- Get the user's email from Graph `/me`
- Filter `CodeAppPTORequests` by `EmployeeEmail eq '{email}'`
- Filter `CodeAppPTOBalances` by `EmployeeEmail eq '{email}'`
- Admins skip the filter and see everything
