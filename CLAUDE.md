# PTO Manager — Claude Code Instructions

## Instructions for Claude Code

When a new developer opens this project, proactively check whether their machine has everything it needs. Run the checks below, then install anything missing without waiting to be asked. Walk the user through each step.

### Step 1 — Check required software

Run these to see what's installed:

```powershell
node --version    # need v18 or higher
npm --version
pac help          # need Power Platform CLI
git --version
```

### Step 2 — Install anything missing

**Node.js missing:**
Direct the user to https://nodejs.org to download the LTS installer. After they install it, verify with `node --version`.

**pac missing:**
```powershell
winget install Microsoft.PowerAppsCLI
```
If `winget` is unavailable, direct them to https://aka.ms/PowerAppsCLI for the installer. After install, restart the terminal and verify with `pac help`.

**Git missing:**
```powershell
winget install Git.Git
```
Or direct them to https://git-scm.com. Verify with `git --version`.

### Step 3 — Install npm dependencies

```powershell
cd "<path-to-this-folder>\app"
npm install
```

### Step 4 — Authenticate with pac

```powershell
pac auth create --url https://org4844a7cc.crm.dynamics.com/
```

A browser window will open. The user signs in with their `@PyrovioSandbox.onmicrosoft.com` account. After redirect, confirm the profile appears in `pac auth list` with `https://org4844a7cc.crm.dynamics.com/`.

Make sure the Sandbox profile is the active one (`*` in `pac auth list`). If not:
```powershell
pac auth select --index N   # N = index of the Sandbox profile
```

### Step 5 — Build and deploy

```powershell
# from the app/ folder
npm run build
pac code push
```

A successful push prints "App pushed successfully" and a play URL.

---

## What this project is

A Power Platform Code App (React + TypeScript + Vite) built for Pyrovio as an internal PTO / time-off request management tool. It is deployed via `pac code push` from the `app/` subfolder.

The app was adapted from an existing PMO project management app. The Dataverse data layer is being replaced with SharePoint lists via Microsoft Graph API.

---

## Project layout

```
antonio-pto-solution/
├── app/                   ← all source and deployment config
│   ├── src/               ← React/TypeScript source
│   ├── dist/              ← Vite build output (gitignored)
│   ├── node_modules/      ← npm dependencies (gitignored)
│   ├── power.config.json  ← pac deployment config
│   └── package.json
├── docs/
├── solution/
├── ONBOARDING.md          ← human onboarding guide
└── CLAUDE.md              ← this file
```

---

## Build

Always run from the `app/` folder:

```powershell
npm run build
```

This produces `app/dist/`. The build must succeed before deploying.

---

## Deploy

Also run from the `app/` folder:

```powershell
pac code push
```

`pac` reads `app/power.config.json` for the environment and appId. The active `pac` auth profile must match the target environment (see below).

---

## Environments

### Pyrovio Sandbox — PRIMARY (use for all development and testing)

| Field | Value |
|---|---|
| Display name | Pyrovio Sandbox (default) |
| Instance URL | `https://org4844a7cc.crm.dynamics.com/` |
| Environment ID | `Default-1b4e0c69-9f47-4349-b384-3445e56fa363` |
| Account | `{user}@PyrovioSandbox.onmicrosoft.com` |
| Code Apps enabled | YES |
| Deployed appId | `f5c17ed7-2e10-475c-9234-e4910d6af4be` |
| Play URL | `https://apps.powerapps.com/play/e/default-1b4e0c69-9f47-4349-b384-3445e56fa363/app/f5c17ed7-2e10-475c-9234-e4910d6af4be` |

### Pyrovio Production — NOT READY

| Field | Value |
|---|---|
| Display name | Enovio, LLC (Upgrade) |
| Instance URL | `https://org080891e6.crm.dynamics.com/` |
| Environment ID | `Default-add0151d-6436-4f59-a424-e401b0363d09` |
| Account | `{user}@pyrovio.com` |
| Code Apps enabled | NO — IT must enable before this environment can be used |

---

## pac auth setup (first time on a new machine)

```powershell
# Sandbox
pac auth create --url https://org4844a7cc.crm.dynamics.com/
# sign in with your @PyrovioSandbox.onmicrosoft.com account in the browser

# Production (for future use)
pac auth create --url https://org080891e6.crm.dynamics.com/
# sign in with your @pyrovio.com account
```

Check active profile:
```powershell
pac auth list
```

Switch profile:
```powershell
pac auth select --index N   # N = index from pac auth list
```

---

## Typical iteration loop

```powershell
cd "<OneDrive - Pyrovio>\Documents\antonio-pto-solution\app"
# edit src/ ...
npm run build
pac code push
# open play URL to test
```

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `CodeAppOperationNotAllowedInEnvironment` (403) | Code Apps not enabled in that environment | Use Sandbox; contact IT for Production |
| `non-recoverable error` / `ExchangeTokenSilentAsync` crash | Stale cached auth token | `pac auth delete --index N` then `pac auth create --url ...` |
| `EAI_AGAIN` | Transient DNS failure | Wait 30s, retry |
| `power.config.json is required` | Wrong working directory | Must run `pac code push` from inside `app/` |

---

## Current app state (as of 2026-06-03)

- Deployed to Sandbox, confirmed working
- `appId` is set in `power.config.json` — pushes update the existing app
- Data layer is still Dataverse (legacy references remain in `power.config.json`)
- Planned: replace Dataverse with SharePoint lists via Microsoft Graph API
- Planned: strip unused pages (Analytics, Programs, Projects, StatusReports, Teams)
- Keep: Dashboard, Intake/request queue, Admin tabs
