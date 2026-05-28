# Contributing to corp-fin-bi-pmo-cfr-solution

## Before You Begin

1. Read `README.md` — every implemented capability, all architectural decisions, all limitations.
2. Read `docs/planning/mira-handoff-and-future-development-plan.md` before touching `app/src/ai/`.
3. Read `docs/planning/PMOCFRSolution__ImplementationPlan__WorkingDocument.md` before feature work.
4. Check open GitHub Issues — verify no other agent is working on overlapping scope.
5. From `app/`, run `npx tsc -b --noEmit` and `npm run test`. Both must pass before you start.

## Environment Setup

Clone the repo and open the multi-root workspace (`corp-fin-bi-standards` must be a sibling directory):

```bash
git clone https://github.com/cvs-health-source-code/corp-fin-bi-pmo-cfr-solution
code corp-fin-bi-pmo-cfr-solution.code-workspace
cd app
npm install
```

Verify the baseline — all three must succeed before beginning any work:

```bash
npx tsc -b --noEmit
npm run test
npm run build
```

## Mandatory Build Sequence (before every push)

From `app/`, in this order:

```bash
npx tsc -b --noEmit        # zero TypeScript errors — fix all errors before continuing
npm run build               # Vite production build
npx power-apps push         # deploy to Nexus RCM DEV
```

If `IS_PAC_CLI` is set from a PAC CLI session, clear it before running `power-apps push`:

```powershell
Remove-Item Env:IS_PAC_CLI -ErrorAction SilentlyContinue
$env:POWERAPPS_CLI_TELEMETRY=0
$env:PAC_CLI_TELEMETRY_OPTOUT=1
```

## CLI Preflight Requirement

Before generating any `pac`, `npm`, or Dataverse schema command, follow the evidence-first preflight pattern from the `power-platform-cli-preflight` skill:

1. Read `app/package.json` — use only script names that are actually defined in `"scripts"`. Do not invent or guess script names.
2. Run `npm --version` and `node --version` to confirm runtimes before generating npm commands.
3. For `pac` commands: run `pac --version` and the command-specific `pac [cmd] --help` before proposing any syntax.
4. Produce a Command Manifest (task, tool, detected version, authoritative source, exact command, success criteria) before executing any CLI operation.

If a required tool is missing, report the blocker and stop — do not guess alternatives.

## Risk Tiers

All work in this repo is High-Risk or Normal tier. Governance friction scales with tier.

### High-Risk Tier

Required when your PR touches any of:

- Protected paths: `.github/`, `*.yml` workflows, `solution/`, `scripts/`
- Shared hotspot files: `App.tsx`, `Sidebar.tsx`, `constants.ts`, `dataverseClient.ts`, `ConfigurationProvider.tsx`, `index.css`, `package-lock.json`
- Schema registration: new Dataverse tables, option-set values, `power.config.json`
- Cross-domain refactors spanning Platform and Application domain

Required controls:

- Open and assign a GitHub Issue **before** creating the branch.
- Label the PR `shared-file-risk` when hotspot files are modified.
- Required reviewers:
  - Protected paths, CI/CD, branch protection, repo automation, `solution/`, or `scripts/` changes: admin team review required (`@cvs-health-source-code/corp-fin-bi-admins`).
  - Shared hotspot files only (no protected paths in the same PR): dev team review required (`@cvs-health-source-code/corp-fin-bi`); tag Platform Domain Owner when change crosses domains.
  - PRs touching both protected paths and hotspot files: both admin team and dev team review required.
  - Do not require admin review for routine `App.tsx`, `Sidebar.tsx`, `constants.ts`, or `package-lock.json` changes unless the same PR also touches protected paths or repo automation.

### Normal Tier

Routine feature delivery, bug fixes, analytics pages, component creation within an owned domain. Dev team review required. No issue-first requirement.

## Branch Naming

```
{developer-shortname}/{type}-{kebab-description}
```

| Shortname | Person |
| --- | --- |
| `patrick` | Patrick Weir |
| `seth` | Seth Frosch |
| `antonio` | Antonio Babic |

Types: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`

Examples: `antonio/feat-initiation-workspace`, `patrick/fix-mira-dataverse-write-adapters`

Target branch lifetime: 1-3 working days. Rebase daily while open:

```bash
git fetch origin && git rebase origin/main
```

## Commit Messages

```
type(scope): description
```

Scopes: `intake`, `tasks`, `nav`, `flows`, `mira`, `analytics`, `admin`, `projects`, `programs`, `repo`, `ci`.

## Domain Ownership

**Current assignments:**

| Role | Person |
| --- | --- |
| Platform Domain Owner | Patrick Weir |
| Application Domain Contributor | Antonio Babic |
| Dev Team Reviewer / Team Lead | Seth Frosch (when assigned) |
| Admin Team Reviewer | `@cvs-health-source-code/corp-fin-bi-admins` |

Do not make the process dependent on named individuals. Named individuals are current assignments only.

### Platform Domain Owner

- `app/src/lib/` (all files)
- `app/src/providers/ConfigurationProvider.tsx`
- `app/src/ai/` (Mira engine)
- `app/src/components/mira/`
- `copilot-studio/`, `solution/`, `scripts/`
- `app/src/index.css` (design tokens)
- `.github/workflows/` (CI/CD)

### Dev Team Reviewer / Team Lead

- Primary reviewer for Application Domain PRs
- Issue backlog and work assignment coordination

### Application Domain Contributor

- `app/src/pages/` (all pages)
- `app/src/components/` (all except `mira/`)
- `app/src/hooks/`, `app/src/models/`, `app/src/api/`

## Shared Files — High-Risk Coordination

These files require a GitHub Issue open and assigned before any agent touches them. Only one branch may modify a given shared file at a time.

| File | Owner | Protocol |
| --- | --- | --- |
| `app/src/App.tsx` | Shared | Issue + assignment; update `Sidebar.tsx` in the same commit |
| `app/src/components/layout/Sidebar.tsx` | Shared | Issue + assignment; update `App.tsx` in the same commit |
| `app/src/lib/constants.ts` | Shared (split) | Platform Domain Owner: `ENTITY_SETS`, `SETTING_*` keys. Application Domain Contributor: option-set additions. Platform Domain Owner merges first if both need changes. |
| `app/src/lib/dataverseClient.ts` | Platform Domain Owner | Open a GitHub Issue — do not edit directly |
| `app/src/providers/ConfigurationProvider.tsx` | Platform Domain Owner | Open a GitHub Issue — do not edit directly |
| `app/package-lock.json` | Auto-generated | One agent runs `npm install` at a time |

Small shared-file changes in Application PRs are permitted when:

- The PR is labeled `shared-file-risk`.
- Platform Domain Owner (or admin team) is tagged as reviewer alongside the dev team reviewer.

## Adding a New Page (High-Risk — issue-first required)

All four changes in the same commit:

1. Create `app/src/pages/{Domain}/{PageName}.tsx`
2. Add `lazy(() => import(...))` to `app/src/App.tsx`
3. Add `<Route path="..." element={...} />` to `app/src/App.tsx`
4. Add NavItem entry to `app/src/components/layout/Sidebar.tsx`

Run before committing:

```bash
npx tsc -b --noEmit
```

## Adding a New Dataverse Table (High-Risk — issue-first required)

1. Open a GitHub Issue: proposed `pmo_` logical name, columns, relationships, feature dependency.
2. Platform Domain Owner registers it in `constants.ts`, `dataverseClient.ts`, and `power.config.json`.
3. Application Domain Contributor rebases their feature branch to pick up the registration, then adds:
   - `models/{entity}.model.ts`
   - `api/{entity}.api.ts`
   - `hooks/use{Entity}.ts`

## Code Patterns

API modules — reference `app/src/api/projectRequests.api.ts`. Use `ENTITY_SETS.entityName` from `constants.ts` — never hardcode OData entity set strings.

Query hooks — reference `app/src/hooks/useProjectRequests.ts`. `useQuery` for reads; `useMutation` with `onSuccess` invalidating related queries.

Error handling — Dataverse write errors: `serializeError()` from `app/src/lib/utils.ts`.

## Testing

```bash
npm run test           # single run
npm run test:watch     # watch mode
npm run test:coverage  # coverage report
```

New feature PRs must include:

- Unit tests for any pure utility function added to `app/src/lib/`.
- Smoke tests for any new Mira mutation in `app/src/ai/mutations.ts`.

## Agent Execution Standard

All work is agent-executable unless explicitly listed in the Governance-Required Gates table. Do not designate any action as human-required in committed documentation unless it is backed by a GitHub platform constraint (e.g., required review enforcement) or a cited permissions blocker. Do not claim that any Power Platform, Dataverse, flow, or Copilot Studio operation requires portal-only access — use PAC CLI and follow the `power-platform-cli-preflight` skill.

## Pull Request Process

1. Verify your Issue is still assigned (High-Risk work only).
2. Rebase:
   ```bash
   git fetch origin && git rebase origin/main
   ```
3. Run:
   ```bash
   npx tsc -b --noEmit && npm run build && npm run test
   ```
4. Open a PR using the PR template — fill every section including correct risk tier.
5. Tag the correct reviewers:
   - Normal Tier: `@cvs-health-source-code/corp-fin-bi` (Dev Team Reviewer is the default).
   - High-Risk / protected paths: also tag `@cvs-health-source-code/corp-fin-bi-admins`.
6. A team member (not the PR author or their agent) must approve before merge.
7. After merge: delete remote branch and close the Issue.

## Known Technical Debt

### Tier 1 — Resolve before new features

- `app/src/ai/mutations.ts`: `createBugReportRecord` and `createEnhancementSuggestionRecord` use mock IDs. Need real Dataverse write adapters. Assigned to: Platform Domain Owner (current: Patrick Weir).
- Merge `origin/antonio/quick-bugfix`: rebase, validate, merge.
- Merge `origin/renovate/configure`: apply automerge policy, merge.
- CI/CD: implement `.github/workflows/pr-validation.yml` per this CONTRIBUTING.md.

### Tier 2 — Schedule alongside feature work

- Decompose `ProjectDetailPage.tsx` (~2,163 lines) into workspace components.
- Decompose `AdminSettingsPage.tsx` (~1,596 lines) into section components.
- Document UploadedBy metadata — export affected flow via `pac flow export`, update metadata property, import via `pac flow import`. Follow `power-platform-cli-preflight` skill preflight before generating any `pac` commands. Assigned to: Platform Domain Owner (current: Patrick Weir).
- Complete secret scanning CI job once `gha_workflow_actions` access is confirmed.

### Tier 3 — When capacity allows

- Route registry refactor (eliminates `App.tsx`/`Sidebar.tsx` dual-edit coordination).
- Expand Vitest coverage: `utils.ts`, `intakeRoutingConfig.ts`, `intakeValidation.ts`.
- Decompose `MiraPanel.tsx` after Mira Tier 1 debt resolved.
