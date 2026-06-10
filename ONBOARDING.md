# PTO Manager App — Developer Onboarding

This is a Power Platform Code App (React + TypeScript + Vite) deployed to the Pyrovio Power Platform environment. This guide covers everything you need to set up, build, and deploy it.

---

## 1. Required Software

Install all of the following before starting.

### Node.js (v18 LTS or newer)
Download from https://nodejs.org — choose the **LTS** version. Verify after install:
```powershell
node --version   # should print v18.x.x or higher
npm --version
```

### Power Platform CLI (pac)
```powershell
winget install Microsoft.PowerAppsCLI
```
Or download the installer from https://aka.ms/PowerAppsCLI. Verify:
```powershell
pac help
```
If you see the command list, you're good. If `pac` is not recognized, restart your terminal.

### Git
Download from https://git-scm.com. Verify:
```powershell
git --version
```

### Claude Code
You already have this. Verify with `claude` in your terminal.

---

## 2. Project Location

The project lives in your **OneDrive - Pyrovio** sync folder:

```
OneDrive - Pyrovio\Documents\antonio-pto-solution\
```

Full path example (replace `YourUsername` with your Windows username):
```
C:\Users\YourUsername\OneDrive - Pyrovio\Documents\antonio-pto-solution\
```

### Folder structure
```
antonio-pto-solution/
├── app/                        ← All work happens here
│   ├── src/                    ← React/TypeScript source code
│   ├── public/                 ← Static assets
│   ├── dist/                   ← Build output (auto-generated, do not edit)
│   ├── node_modules/           ← Dependencies (auto-generated)
│   ├── power.config.json       ← pac deployment config (environment, appId)
│   ├── package.json
│   └── vite.config.ts
├── docs/
├── solution/
├── CLAUDE.md                   ← Instructions for Claude Code
└── ONBOARDING.md               ← This file
```

---

## 3. First-Time Setup

Do this once after getting access to the project folder.

```powershell
# Navigate to the app folder
cd "C:\Users\YourUsername\OneDrive - Pyrovio\Documents\antonio-pto-solution\app"

# Install dependencies
npm install
```

---

## 4. Authenticate with Power Platform

You need a `pac` auth profile for each environment you deploy to. Do this once per machine.

### Pyrovio Sandbox (development — use this for all testing)

```powershell
pac auth create --url https://org4844a7cc.crm.dynamics.com/
```

A browser window will open. Sign in with your **Pyrovio Sandbox** account (`YourName@PyrovioSandbox.onmicrosoft.com`). After sign-in the terminal will confirm the profile was created.

Verify it was added:
```powershell
pac auth list
```

You should see an entry with `https://org4844a7cc.crm.dynamics.com/` and your account.

---

## 5. Build and Deploy

Every time you make code changes, you must **build** before **deploying**.

```powershell
# From the app/ folder:

# Step 1 — build the React app
npm run build

# Step 2 — deploy to Power Platform
pac code push
```

`pac code push` reads `power.config.json` to know which environment and app to update. It will update the existing app in-place (not create a new one) because `appId` is already set.

**Play the app after deploying:**
```
https://apps.powerapps.com/play/e/default-1b4e0c69-9f47-4349-b384-3445e56fa363/app/f5c17ed7-2e10-475c-9234-e4910d6af4be
```

---

## 6. Environments

| Environment | Purpose | Instance URL | Environment ID | Account |
|---|---|---|---|---|
| **Pyrovio Sandbox** | Development & testing | `https://org4844a7cc.crm.dynamics.com/` | `Default-1b4e0c69-9f47-4349-b384-3445e56fa363` | `YourName@PyrovioSandbox.onmicrosoft.com` |
| **Pyrovio Production** | Live (not ready yet) | `https://org080891e6.crm.dynamics.com/` | `Default-add0151d-6436-4f59-a424-e401b0363d09` | `YourName@pyrovio.com` |

> **Note:** Code Apps are currently only enabled on **Pyrovio Sandbox**. Production deployment is blocked until IT enables the feature there. Do all development and testing against Sandbox.

---

## 7. Switching Environments

If you ever need to switch which environment `pac` targets:

```powershell
# See all profiles
pac auth list

# Switch by index number shown in the list
pac auth select --index 3
```

Make sure `power.config.json`'s `environmentId` matches the environment you're deploying to.

---

## 8. Typical Day-to-Day Workflow

```powershell
cd "C:\Users\YourUsername\OneDrive - Pyrovio\Documents\antonio-pto-solution\app"

# Make your code changes in src/ ...

# Build
npm run build

# Deploy
pac code push

# Open the play URL in your browser to test
```

Or just tell Claude Code what you want to change — it knows the project structure and can run build and deploy steps for you.

---

## 9. Troubleshooting

### `pac` not found after install
Restart your terminal. If still missing, add the pac install location to your PATH:
```powershell
$env:PATH += ";$env:LOCALAPPDATA\Microsoft\PowerAppsCLI"
```

### Auth token expired / `non-recoverable error`
Delete the stale profile and re-authenticate:
```powershell
pac auth list                  # note the index of the broken profile
pac auth delete --index N      # replace N with the index
pac auth create --url https://org4844a7cc.crm.dynamics.com/
```

### `CodeAppOperationNotAllowedInEnvironment` (403)
Code Apps are not enabled in that environment. For Sandbox this should already be on — contact Antonio Babic if you see this.

### `EAI_AGAIN` DNS error
Transient network issue. Wait 30 seconds and retry `pac code push`.

### `power.config.json is required`
You ran `pac code push` from the wrong directory. You must be inside the `app/` folder.

### Build errors
```powershell
npm run build 2>&1
```
Read the TypeScript/Vite error output. Common cause: type errors in `src/`. Fix the error, then rebuild.
