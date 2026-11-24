# AGENTS.md

Guidance for AI coding agents working in this repository. Detail lives in `.ai/`.
Read `.ai/context/repo-overview.md` before changing anything.

## Template status

This repository is still the unmodified OrcaBus "Hello World" service template.
If the user wants to start a new service, use the `use-template` skill
(`.ai/skills/use-template/SKILL.md`) before making other changes.

## What this is

An OrcaBus microservice deployed through a CDK pipeline. The application is in `app/`.
Infrastructure is TypeScript CDK (`infrastructure/`, `bin/`, `test/`). What the service does is
up to its developers, so read the code instead of assuming.

## Commands

- `make install` installs Node dependencies.
- `make check-all` runs lint and format checks (this is what CI runs).
- `make fix-all` auto-fixes formatting and lint.
- `pnpm test` type-checks and runs CDK tests. Docker must be running.
- `cd app && make install && make test` runs the app unit tests.

`app/Makefile` must keep the targets `install`, `check`, `test` and `fix`.
CI and the deployment pipeline call them.

## Rules

- Work on a branch. Pre-commit blocks commits to `main`.
- Do not change the Lambda runtime or version, CDK versions or the pnpm version unless asked.
  The `update-dependencies` skill counts as being asked.
- `cdk-nag` must report no errors or warnings. Suppressions need a specific reason.
- Platform rules (event naming, event design, testing) live in the private `OrcaBus/ai-context`
  repo. `.ai/context/platform-rules.md` says how to read them with `gh`.
- Never commit secrets, tokens or account-specific values.

## Skills

To update out-of-date dependencies, use the `update-dependencies` skill
(`.ai/skills/update-dependencies/SKILL.md`). Run it with the `dep-updater` agent
(`.kiro/agents/dep-updater.md`), which holds the command and file permissions the skill needs.

Skills live in `.ai/skills/`. `.kiro/skills/` holds stubs that point there.
Run `python3 .ai/scripts/check_skills.py` after adding or changing a skill.
