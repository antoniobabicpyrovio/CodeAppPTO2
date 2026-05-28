## Summary

<!-- One sentence: what does this PR do and why? -->

## Type of Change

- [ ] `feat` — new capability or page
- [ ] `fix` — bug fix (include Dataverse error code if applicable)
- [ ] `refactor` — restructuring without behavior change
- [ ] `chore` — dependency update, tooling, config
- [ ] `docs` — documentation only
- [ ] `test` — test additions or changes
- [ ] CI/CD workflow change (requires CI/CD checklist below)

## Risk Tier

- [ ] **High-Risk** — touches protected paths, shared hotspot files, schema registration, or CI/CD
- [ ] **Normal** — routine application feature or bug fix

## Validation Checklist

- [ ] `npx tsc -b --noEmit` — zero TypeScript errors (run from `app/`)
- [ ] `npm run build` — Vite build succeeds
- [ ] `npm run test` — all existing tests pass
- [ ] `npx power-apps push` to DEV — required for any Dataverse-touching change
- [ ] Branch rebased onto current `main` before opening PR

## High-Risk Tier Checklist (complete only if High-Risk box is checked above)

- [ ] GitHub Issue opened and assigned before branching
- [ ] `App.tsx` modified → `Sidebar.tsx` updated in the same commit
- [ ] `Sidebar.tsx` modified → `App.tsx` updated in the same commit
- [ ] `constants.ts` modified → no simultaneous open PR also modifying `constants.ts`
- [ ] `dataverseClient.ts` or `ConfigurationProvider.tsx` modified → Issue opened and assigned first
- [ ] `package.json` modified → `package-lock.json` regenerated via `npm install`
- [ ] New Dataverse table → registered in `ENTITY_SETS` (constants.ts), `DATAVERSE_SOURCES` (dataverseClient.ts), and `power.config.json`
- [ ] PR labeled `shared-file-risk` if any hotspot file is modified

## Dataverse Impact

<!-- If none, write "None" -->

- New tables:
- New option-set values:
- New custom API actions:
- Power Automate flows affected:

## CI/CD Checklist (complete only if `.github/workflows/` is modified)

- [ ] `runs-on: self-hosted` — no cloud runners
- [ ] No `shell: pwsh` — all steps use bash or python3
- [ ] All third-party actions pinned to exact version tag (not @latest or @main)
- [ ] Internal reusable workflows from `gha_workflow_actions/` preferred and checked first
- [ ] No secrets in YAML — `${{ secrets.SECRET_NAME }}` pattern used
- [ ] npm script names verified against `app/package.json` before use in workflow steps
- [ ] **Security Coverage:** Path A (internal workflow) confirmed — an actual scan job or internal reusable workflow is present and running OR Path B manual attestation below
- [ ] Do not claim automated security coverage unless an actual scan job or internal reusable workflow is present and running

**Security Coverage (Path B — complete if automated scan not available):**

Manual security review completed. Changed files reviewed for:
- [ ] Hardcoded credentials or API keys
- [ ] Plaintext tokens, passwords, or connection strings
- [ ] Exposed environment IDs or tenant-specific configuration that should be in secrets

*See Issue #______ for automated secret scanning follow-up.*

## Screenshots

<!-- Required for any UI change -->

---

**Reviewer tagging:**
- Normal Tier: @cvs-health-source-code/corp-fin-bi
- Shared hotspot files only (same PR has no protected paths): @cvs-health-source-code/corp-fin-bi; tag Platform Domain Owner when change crosses domains
- Protected paths / CI/CD / repository automation / solution / scripts: @cvs-health-source-code/corp-fin-bi-admins
- Mixed protected paths + application/source changes: @cvs-health-source-code/corp-fin-bi AND @cvs-health-source-code/corp-fin-bi-admins
