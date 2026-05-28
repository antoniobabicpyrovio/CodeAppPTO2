# Copilot Instructions — corp-fin-bi-pmo-cfr-solution

> **This file is a thin downstream bootstrap.** All canonical behavior policy, standards, and guardrails are defined in [`corp-fin-bi-standards`](https://github.com/cvs-health-source-code/corp-fin-bi-standards). This file does not duplicate or override central rules — it provides repository-specific context only.

---

## Central Authority

All Copilot behavior in this repository follows the standards defined in:

- **Policy and behavior:** `corp-fin-bi-standards/.github/copilot-instructions.md`
- **Agent routing:** `corp-fin-bi-standards/AGENTS.md`
- **Standards catalog:** `corp-fin-bi-standards/docs/standards/README.md`
- **Power Platform standards:** `corp-fin-bi-standards/docs/standards/power-platform/`

---

## Repository-Specific Context

**Repository:** `corp-fin-bi-pmo-cfr-solution`
**Application:** CFR Project Management — Coram Finance RevCycle unified PMO application
**Platform:** Power Apps Code App (React/TypeScript) + Dataverse + Copilot Studio (Mira agent)
**Environment:** Nexus RCM DEV (`731e4975-10cd-4535-b82f-1ff016e59b6c`)
**Publisher prefix:** `pmo` / `pmo_` (exception boundary approved for this solution only)

### Key entry points

- `app/src/` — React/TypeScript application source
- `solution/src/` — Dataverse solution source (botcomponents, workflows, entities)
- `copilot-studio/` — Mira agent topic/action specs and contract fidelity mapping
- `docs/planning/` — Active planning artifacts and deferred feature registry

### Technology stack

- React 19, TypeScript, Vite, Tailwind CSS
- TanStack Query v5, Recharts, Lucide React
- Dataverse Web API (OData) + PSS (Project Scheduling Service)
- `npx power-apps push` — app deployment (never `pac code push`)
- Vitest — unit and integration testing

### Mandatory build sequence

Always run in order before pushing: `npx tsc -b --noEmit` → `npm run build` → `npx power-apps push`

### Planning documents

- `docs/planning/mira-handoff-and-future-development-plan.md` — authoritative Mira current state
- `docs/planning/deferred-feature-registry.json` — tracked deferred and implemented features

### Known publisher exception

The publisher prefix `pmo` / `pmo_` is used in this solution per an approved exception boundary documented in `corp-fin-bi-standards/docs/standards/power-platform/power-platform-publisher-and-prefix-standard.md`. New net-new components outside this solution must use the standard `rcm` prefix.
