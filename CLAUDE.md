# corp-fin-bi-pmo-cfr-solution — Claude Code Instructions

This repository uses `corp-fin-bi-standards` as the authoritative source for shared Claude Code behavior. This file is a thin bootstrap only.

## Required Startup Order

1. Read `c:\Users\z232630\Documents\GitHub\corp-fin-bi-standards\CLAUDE.md`.
2. Read `c:\Users\z232630\Documents\GitHub\corp-fin-bi-standards\.github\copilot-instructions.md`.
3. Read `c:\Users\z232630\Documents\GitHub\corp-fin-bi-standards\AGENTS.md`.
4. Read `c:\Users\z232630\Documents\GitHub\corp-fin-bi-standards\docs\copilot\skills-catalog.md` and `c:\Users\z232630\Documents\GitHub\corp-fin-bi-standards\docs\copilot\agents-catalog.md`.

## Skill Routing Rule

- Check the central standards library and shared skills under `c:\Users\z232630\Documents\GitHub\corp-fin-bi-standards\.github\skills\` before using built-in skill search or enterprise preset skills.
- Prefer corp-fin-bi shared skills and shared agents first.
- Use enterprise preset skills only when no central shared asset or local overlay asset matches the request.
- For repo-specific workflows, inspect local `.claude/commands/` and local overlays only after central guardrails are loaded.