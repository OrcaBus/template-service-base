# `.ai/` - AI guidance for this repository

This folder is the single home for AI guidance for this repository. It is written once
and is not tied to any AI tool. Tool-specific folders only point here.

```
.ai/
  context/                   Plain markdown knowledge about this repo
  skills/<skill-name>/       One folder per skill (the real instructions)
    SKILL.md                 Frontmatter (name, description) + the procedure
    references/              Optional: longer material the skill reads on demand
    scripts/                 Optional: deterministic helpers (Python only, see below)
  scripts/check_skills.py    Verifies the tool stubs match the skills
  logs/<skill-name>/         Output written by skills. Committed. Not prettier-checked.
    SUMMARY.md               High level status, rewritten on every run. Read this first.
    runs/<UTC time>.md       One full log per run, for example runs/2026-11-24T031500Z.md
```

## What `context/` is for

Knowledge about this repository that any agent needs for day-to-day work, whichever tool
it runs in. `AGENTS.md` points to it. Keep it to facts about this repo (layout, commands,
contracts). Platform-wide rules belong in the shared `ai-context` repository;
`context/platform-rules.md` is a small hand-copied extract of them.

## How Kiro finds a skill

Kiro scans `.kiro/skills/` for skills. That folder holds a **stub** for each skill:
a tiny `SKILL.md` that repeats the skill's `name` and `description` (so Kiro knows when to
activate it) and tells the agent to read the real file under `.ai/skills/`.

```
.ai/skills/<skill-name>/SKILL.md      <- real instructions
.kiro/skills/<skill-name>/SKILL.md    <- stub
```

The stub layer exists so the real content is not tied to one tool. To support another tool
later, add its skills folder to `TOOL_DIRS` in `.ai/scripts/check_skills.py` and add one stub
per skill. We use stubs instead of symlinks because symlinks break on Windows checkouts that
do not have `core.symlinks` enabled.

## Adding a skill

1. Create `.ai/skills/<name>/SKILL.md`. The folder name must equal `name` in the frontmatter.
   Keep `name` and `description` each on a single line.
2. Create the stub `.kiro/skills/<name>/SKILL.md`, copying the pattern above (same `name` and
   `description`).
3. Run `python3 .ai/scripts/check_skills.py`. It also runs as part of `make check`.

Write the `description` as "what it does. Use when ..." with the phrases a developer
would actually type. The description is the only part Kiro sees before activation.

## Conventions for skills

- Helper scripts are Python 3 with the standard library only. Do not add `.sh` scripts,
  they do not run on Windows. (This is about the tooling, not the service's own runtime.)
- Use forward slashes in paths inside skill text.
- Put long reference text in `references/`, not in `SKILL.md`, so activation stays cheap.
- Skills must not commit, push, deploy, or create remote resources unless the user asks.

## Skills

| Skill | Purpose |
| ----- | ------- |
| `use-template` | Interviews the developer and converts this template into a real service. Removes itself when done. |
| `update-dependencies` | Updates Node and Python dependencies. Minor and patch directly, major one version at a time after a breaking-change review, reverts and asks when unsure. Safe to re-run. |
