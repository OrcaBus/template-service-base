---
name: update-dependencies
description: Update the root dependencies of this repo (CDK, pnpm and tooling). Applies minor and patch updates directly, upgrades major versions one step at a time after checking the release notes for breaking changes, and reverts the package and records it in a log when unsure. Does not touch app/. Runs without asking questions, so it can be scheduled. Use when the user asks to update, upgrade, bump or refresh dependencies, packages or libraries, or says the repo is out of date.
---

# Update dependencies

Safe to run repeatedly. Each run brings the root dependencies as current as it can get, and
reports what it could not upgrade.

## Scope

- In scope: the root CDK (TypeScript) project. That is `package.json`, `pnpm-workspace.yaml` and
  `pnpm-lock.yaml`, plus the tool and runtime versions listed below.
- Out of scope for now: everything under `app/`. Do not read its dependency files for updates,
  do not edit anything there, and do not run `pip` or other app package managers. If an upgrade
  can only work by changing `app/`, revert that package and record it under "Needs a person".
- GitHub Action versions and `.pre-commit-config.yaml` `rev:` values are in scope only if the
  user asks. Mention them in the report as "not checked".

### Update level

The user can choose how far to go. Read it from their request. Do not ask if they did not say.

| Level   | When the user says                                     | What is upgraded               |
| ------- | ------------------------------------------------------ | ------------------------------ |
| `all`   | nothing, "all versions", "include major" (**default**) | patch, minor and major         |
| `minor` | "minor", "minor and patch", "no major", "safe only"    | patch and minor, no major      |
| `patch` | "patch only"                                           | patch only, no minor, no major |

Packages above the chosen level are not touched. List them in the report under
"Skipped (above chosen level)" with current and latest versions, so the user can see what a
higher level would do. Step 3 runs only at level `all`. Security fixes are the exception:
if `pnpm audit` names a fix that needs a higher level, do not apply it. List it under "Skipped"
and mark it as a security fix.

### Pinned versions are upgraded like any other

Exact pins (no `^` or `>=`) and fixed tool or runtime versions are upgraded like any other
dependency: patch and minor directly, major one hop at a time. Do not skip a package because
it is pinned. Keep the pin style (an exact pin stays exact). The packages below need extra care
because they must move together.

- `aws-cdk`, `aws-cdk-lib`, `@aws-cdk/aws-lambda-python-alpha`: keep them in step. `aws-cdk`
  (CLI) must be at least as new as `aws-cdk-lib`. The alpha package version must match
  `aws-cdk-lib` (`<version>-alpha.0`) and is pinned exactly, not with `^`.
- `@orcabus/platform-cdk-constructs`: it depends on a CDK version. Check its peer dependencies
  and upgrade it with the CDK packages.
- the `packageManager` pnpm version: update it with `corepack use pnpm@latest` (or edit the
  field including the hash). Check that CI installs the same version.
- the Python version in CI (`.github/workflows/pr-tests.yml`) and the Lambda runtime in
  `infrastructure/`: upgrade only to a version AWS Lambda supports, and keep CI, the Lambda
  runtime, and the bundling image on the same Python version. Check the Lambda runtimes page
  for support and the Python release notes for removed features. `app/` is out of scope, so if
  the new version needs changes there, revert it and record it under "Needs a person".

Also keep the pnpm `overrides` (in `pnpm-workspace.yaml` for pnpm 11 and later, in the `pnpm`
block of `package.json` for earlier versions). Those entries exist for security fixes. Only
remove an override if the package it patches is no longer in the tree, and say so in the report.

## Rules

- This skill runs unattended, for example on a schedule. Never stop to ask the user a question
  and never wait for input. When you hit a decision you cannot make safely, take the
  conservative action (revert that package, skip that part) and record it in the run log and
  the summary.
- Work on a branch. If on `main`, change nothing and say so in the output. The user or the
  scheduler must start the run on a branch. Do not create one.
- Do not commit, push, or deploy.
- Do not use `--frozen-lockfile`. Updating the lockfile is the point here.
- Use your file tools to read, search, create and edit files. Use forward slashes in paths.
- A refused or unlisted command is a boundary, not a puzzle. Do not do the same thing another
  way (for example `sed -i` or `python3 -c` instead of the file tools or the helper script,
  or `mv`, `cp`, `mkdir` and scratch files in `/tmp` to get around a check). Skip that step,
  revert the package if it depends on it, and record the refusal in the run log so a person
  can add a rule if it is legitimate.
- Never weaken a security or quality gate to get an upgrade through. Do not delete or loosen
  assertions, tests, `cdk-nag` checks or suppressions, lint rules, or audit settings
  (`--ignore`, `--audit-level`). If an upgrade can only pass by changing what such a check
  asserts, revert the package and record it under "Needs a person". Repo rule: `cdk-nag` must
  report no errors or warnings.
- Do not create scratch files, throwaway tests or directories, and do not write outside the
  repository. Do not move, rename or delete `app/.venv` or any other environment folder.
- Read release notes and changelogs with web fetch (for example
  `https://github.com/<owner>/<repo>/releases` or
  `https://api.github.com/repos/<owner>/<repo>/releases`), not with `gh`. Read versions and
  peer dependencies with `pnpm view <pkg>`, `pnpm why <pkg>` and `pnpm peers check`.
- Run each command on its own, exactly as written in this skill. Do not pipe it through
  `tail`, `head` or `grep`, and do not chain commands with `;`. A pipe replaces the command's
  exit code with the pipe's, so a failed check looks like a pass. Read the exit code and the
  full output of each command. For slow commands such as `pnpm test`, set a long timeout
  (10 minutes or more) instead of cutting the output.

## Checks

"The check set" in this skill means these commands, each run on its own:

```
make check-all
pnpm test          # Docker must be running
```

`make check-all` also runs the lint check for `app/`. That part only reads. A failure there is
not caused by a root upgrade. Note it and carry on. If you cannot run something (for example
Docker is off or `pre-commit` is missing), say so, report that check as "not run", and report
the upgrades as unverified for it.

There is no baseline run before the upgrades. A check can fail because of an upgrade or
because it was already failing. Tell them apart by reverting the suspected package and
re-running the failed check. If it still fails, the failure was already there: report it,
leave the package upgraded, and carry on. `make check-all` starts with `pnpm audit`, which
fails while vulnerable packages are still installed. That is expected before the upgrades. Do
not treat it as a failure to investigate.

## Steps

### 1. Find what is outdated

- `pnpm outdated --format json`.
- Security: `pnpm audit`. Security fixes go first.

Build one table: package, current, latest, kind (patch, minor, major), and the file that
declares it. Include the tool and runtime versions from the Scope list.

### 2. Minor and patch updates

Do these first, as a batch, because they should not break anything.

1. Update the ranges in `package.json` to the latest minor or patch. Keep the existing range
   style (`^x.y.z` stays `^`). Do not add upper bounds.
2. Run `pnpm install` to refresh the lockfile.
3. Run the check set. `make check-all` may still fail on `pnpm audit` here if a
   vulnerability has no fix. Note it and move on.
4. If everything passes, move on.
5. If something fails, read the error output and work out which package caused it (the stack
   trace, the failing import, the deprecation or peer-dependency message). Confirm the guess
   by reverting only that package and re-running the failed check. Keep the packages that
   pass. Treat the failing one as a major upgrade for the purposes of step 3 (read its
   changelog, try to fix, otherwise revert and report). If the check still fails after the
   revert, it was already failing (see "Checks"). Only if the error does not point to a
   package, revert half the batch and halve again until you find it.

### 3. Major updates

Skip this step unless the level is `all`. In step 2 touch only the kinds the level allows
(`patch` level: patch only).

Attempt every package, even if it needs several hops, touches CI, or changes install behaviour.
Stop only when a peer dependency blocks the next hop or a breaking change can't be resolved.
When you stop, report the version you ended on and the reason. Never report "not attempted"
without a reason.

Handle one package at a time. Order: dev tooling first (linters, test runners), then runtime
libraries. Run the check set after each one so a failure points to one package.

For each package:

1. **Plan the path.** List the major versions between current and latest. If the jump is more
   than one major version, upgrade through each major in turn (for example 2.x to 3.x, then
   3.x to 4.x). Use the latest minor of each intermediate major as the stepping stone. Run the
   whole of items 2 to 7 below for every hop.
2. **Read the breaking changes.** Use the official changelog, release notes, or migration guide
   for that hop (web search and fetch). Prefer the project's own docs over blog posts. Cite the
   source link in the report. Note the Node and peer-dependency requirements too.
3. **Check them against this repo.** For each breaking change, search the code for the removed
   or renamed API, option, config key or default that changed. Look in `bin/`,
   `infrastructure/`, `test/`, and config files such as `eslint.config.*`, `tsconfig.json`,
   `jest.config.*`, `.prettierrc.json`, `pnpm-workspace.yaml` and the root `Makefile`. Decide
   for each: applies, does not apply, or unsure.
4. **If none apply**, bump the version and continue.
5. **If some apply**, make the smallest change that follows the migration guide. Do not
   refactor beyond it. Do not silence errors with suppressions, `any`, or `ignore` entries to
   get green.
6. **Install and verify.** Run `pnpm install`, then the check set. Also run
   `pnpm exec tsc --noEmit`. Read the whole install output. A warning that a setting is
   ignored, removed or deprecated means a breaking change applies to this repo even when every
   check passes. Fix it (for example move the setting to its new location) or revert the
   package. Never keep an upgrade with such a warning unhandled.
7. **Decide.**
   - Everything passes and you are confident in each breaking-change decision: keep the
     upgrade. Write a breaking-change summary only if you had to modify code or config to
     get there. If nothing applied and nothing was modified, write no summary.
   - Anything fails you cannot fix with the documented migration, a breaking change is
     unclear, the docs are missing or contradict each other, a peer dependency conflicts, or
     you are in doubt: **revert that package** (see below) and leave it out. Do not ask anyone.
     Always write a summary here, even when the docs mention no breaking change that explains
     the failure: what broke, what you tried, and why it failed, so a person can pick it up
     without redoing the investigation.

**Revert** means restoring the exact previous state for that package: put back the old range in
`package.json`, undo any code changes you made for it, and re-run `pnpm install` so the
lockfile and `node_modules` match. Re-run the checks to confirm you are back to the state
before this package. Do not use `git reset --hard` or `git checkout .`, since they would remove
unrelated work. Undo only your own edits (use `git diff` to see them, and edit the files back).

If a hop in a multi-step path fails, keep the earlier hops that passed and revert only the
failing one. Report where it stopped.

### 4. Final check

Run `pnpm audit`. If it reports vulnerabilities, fix them in this order, running `pnpm audit`
again after each:

1. `pnpm audit --fix=update`, then `pnpm install`. This moves vulnerable packages to patched
   versions inside the lockfile.
2. If vulnerabilities remain, `pnpm audit --fix`. This is the same as `--fix=override`. It
   writes overrides that force patched versions, so the pinned versions may not suit the
   packages that depend on them. Then `pnpm install` and the check set. If a check now fails,
   remove the overrides you just added and report the vulnerability as unresolved.
3. If vulnerabilities remain, report them. Do not hand-edit overrides.

Add every override this step creates to the run log, with the package and advisory ID. Check
where `--fix` wrote them (`package.json` or `pnpm-workspace.yaml`, depending on the pnpm
version) and that pnpm reads that location without a warning.

Then run the check set once more on the end state. If `make check-all` fails because
`check_skills.py` or `pre-commit` is missing, say so. Do not skip it silently.

### 5. Report

Keep it short. Use this shape:

```
## Dependency update <date>

**Upgraded (minor/patch):** pkg a.b.c -> a.b.d, ...
**Upgraded (major):** pkg 2.x -> 4.x (via 3.x)
**Skipped (above chosen level):** pkg current -> latest (omit when the level is `all`)
**Not upgraded, needs your decision:** pkg (reason, link to the migration guide)
**Checks:** make check-all <result>, pnpm test <result> (say "not run" if so)

### Breaking changes handled
- pkg 3.x -> 4.x ([release notes](url)): <what changed>. Fix: <what you changed>.

### Breaking changes not resolved
- pkg 3.x -> 4.x ([release notes](url)): <what changed or what broke>. Tried: <what you
  attempted>. Failed because: <error or doubt>. Reverted. Needs a decision: <what a person
  has to decide>.
```

Write an entry only in these two cases:

- **Handled:** a breaking change applied to this repo, you changed code or config to handle it,
  and the upgrade is kept.
- **Not resolved:** the upgrade failed or you were in doubt, and you reverted the package. This
  includes failures the docs do not explain. Do not ask anyone. The entry, and the summary in
  step 7, are how a person finds out.

If no breaking change applied and you changed no code or config, list the package under
"Upgraded (major)" and write nothing more. Omit a section if it would be empty.
Minor and patch upgrades get an entry only if one of them failed and went through step 3.

Show the report in the chat too, so it can go into the PR description.

### 6. Write the run log

Save the same report as a log file, so the team can see what happened on each run. The skill
does not read these logs. Every run scans for outdated packages from scratch.

Layout of `.ai/logs/update-dependencies/`:

```
SUMMARY.md                  High level, rewritten every run (step 7)
runs/2026-11-24T031500Z.md  One full log per run, never edited afterwards
```

- Folder: `.ai/logs/update-dependencies/runs/` (the write tool creates it if missing).
- File name: the UTC time the run started, as `YYYY-MM-DDTHHMMSSZ.md`, for example
  `2026-11-24T031500Z.md`. No colons, so it works on Windows. Get the time from
  `python3 .ai/scripts/utc_timestamp.py` and do not guess it. Never overwrite or edit an
  earlier log. Each run adds a new file.
- Content: the report from step 5, with the UTC timestamp and the current git branch at the top.
- Write a log even when nothing was upgraded, so the history shows the run happened.
- Do not put secrets, tokens or account IDs in it. Log files are committed, but do not commit
  them yourself. Leave them for the user.

### 7. Update the summary

Overwrite `.ai/logs/update-dependencies/SUMMARY.md` on every run, even when nothing changed.
It is the one file a person reads to see whether anything needs them. Keep it to one screen.
Build it from this run only. Do not read earlier logs or the previous summary. Use this shape:

```
# Dependency update summary

**Last run:** <UTC timestamp> on branch <branch>, level <level>
**Result:** <n> upgraded, <n> need a person
**Checks:** make check-all <result>, pnpm test <result>
**Full log:** [runs/<file name>](runs/<file name>)

## Needs a person

| Item | What happened | What to decide |
| ---- | ------------- | -------------- |
| pkg 3.x -> 4.x | Reverted. <one line reason> | <one line> |

Write "Nothing." instead of the table when there is nothing to decide.
```

An item goes under "Needs a person" when any of these is true: a package is under "Breaking
changes not resolved", a check failed that you could not trace to an upgrade, a check was
"not run", or `pnpm audit` still reports a vulnerability. Packages skipped only because of the
chosen level do not go here. Link each row to the run log for detail instead of repeating it.
