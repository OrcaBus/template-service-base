---
name: use-template
description: Turn this OrcaBus Hello World template into a new service. Asks for the service name, renames the template to match, and leaves TODO placeholders where the developer writes the app logic. Use when the user is starting a new service, using this template, setting up this repo, or renaming hello-world.
---

# Use this template for a new service

Rename the Hello World template to a real service name and leave `TODO:` placeholders for the
developer's own logic. Do not write the service's business logic yourself.

## Steps

1. **Ask four questions in one message:**

   - Service name in kebab-case, without a `service-` prefix. Example: `sample-sheet-check`.
   - GitHub repository name. Default: `service-<name>`.
   - One sentence on what the service does.
   - Does the service need a **stateful** deployment? Default: no. Explain it like this:
     a _stateless_ stack holds resources that are easy to redeploy at any time with no side
     effects, such as Lambda functions and EventBridge rules. A _stateful_ stack holds resources
     that must be retained and should not be redeployed casually, such as a database, an S3
     bucket or a queue. It gets its own separate pipeline.

2. **Find Python.** Try `python3 --version`, then `python --version`, then `py -3 --version`.
   Use the first that prints Python 3.x. Call it `<PY>` below.

3. **Show the names and ask for a "yes".** Only the deployment side is named after the service.
   For `sample-sheet-check`:

   | Where                  | Name                                    |
   | ---------------------- | --------------------------------------- |
   | Toolchain stack id     | `OrcaBusStatelessSampleSheetCheckStack` |
   | Pipeline name          | `OrcaBus-StatelessSampleSheetCheck`     |
   | Stack class and name   | `SampleSheetCheckStack`                 |
   | GitHub repo            | `service-sample-sheet-check`            |
   | Python module (`app/`) | `sample_sheet_check`                    |

   If the service is stateful, add these rows. If not, say the stateful stack will be removed.

   | Where                       | Name                                   |
   | --------------------------- | -------------------------------------- |
   | Stateful toolchain stack id | `OrcaBusStatefulSampleSheetCheckStack` |
   | Stateful pipeline name      | `OrcaBus-StatefulSampleSheetCheck`     |
   | Stateful stack name         | `StatefulSampleSheetCheckStack`        |

   Events, the event source and the Lambda and rule resources are app logic. Do not ask about
   them or rename them. They stay as the Hello World example until the developer replaces them.

4. **If the service is not stateful, remove the stateful stack now** (before the rename, so
   the script's report does not list its placeholders):

   - Delete `infrastructure/toolchain/stateful-stack.ts`.
   - In `bin/deploy.ts`, remove the `StatefulStack` import and the whole `stateful` branch (the
     block that starts with `else if (deployMode === 'stateful')`). Keep the final `else` that
     throws.
   - In `package.json`, remove the `"cdk-stateful"` script.
   - In `test/toolchain.test.ts`, remove the trailing `// TODO: Add cdk-nag-stateful-...` comment.

5. **Rename.** From the repository root run:

   ```
   <PY> .ai/skills/use-template/scripts/rename.py <name> --repo <repo> --apply
   ```

   Add `--stateful` if the service is stateful. It fills in the stateful pipeline names. Leave
   out `--apply` to preview without writing. Add `--pascal <Name>` if the derived PascalCase is
   wrong (for example an acronym). If the script reports an error, show it to the developer and
   stop. Do not work around it. The script prints the `TODO:` placeholders and the files that
   still mention `hello-world`. Keep that output for the hand-over.

6. **Update the docs.**

   - `README.md`: use the sentence from step 1 under "Name & responsibility" and "Description",
     and remove the "Using This Template" section and its table-of-contents entry. Make the
     stateful text match the answer. If not stateful, say there are no stateful resources and
     drop the `cdk-stateful` mentions.
   - `AGENTS.md`: replace the whole "Template status" section with this "Service" section, so
     the repo is no longer described as a template. Fill in the values:

     ```
     ## Service

     **<name>**: <sentence>.

     - Consumes: see `INCOMING_*` in `infrastructure/stage/constants.ts`
     - Emits: see `EVENT_SOURCE` and `EVENT_DETAIL_TYPE` in `app/<snake>/lambdas/handler.py`

     When the events this service consumes or emits change, update the two lines above with
     the real event names.
     ```

7. **Check it still works.** Run `make install`, then `cd app && make install`, then
   `make fix-all`, then `cd app && make test`. Offer a virtual environment before installing
   Python packages. If you removed the stateful stack, also run `pnpm exec tsc` to confirm
   nothing still imports it. Report the real result of each. If you cannot run one, say so.

8. **Hand over.** Tell the developer, in a short list:

   - the `TODO:` placeholders they must fill in (the script's output). This is the app logic:
     the app stack resources, the events consumed and emitted, the event models and the handler
   - that the Hello World example is still in place. It listens for the `hello-world` workflow
     and emits `HelloWorldEvent` from `orcabus.helloworld` until they replace it
   - stateful: either "removed, since the service has none", or "pipeline names are filled in,
     but `stack: this` in `stateful-stack.ts` and the stateful test in `test/toolchain.test.ts`
     need a real stateful stack class holding the database, bucket or queue"
   - that creating the GitHub repository, pushing, and the first pipeline deploy are theirs to do

   Then offer to remove this skill: delete `.ai/skills/use-template/` and
   `.kiro/skills/use-template/`, remove its row from the Skills table in `.ai/README.md` (if it
   was the only row, replace the table with "No skills yet."), and run
   `<PY> .ai/scripts/check_skills.py`.

## Rules

- Do not commit, push, create a GitHub repository, or deploy.
- Pre-commit blocks commits to `main`. If the current branch is `main`, mention it and suggest a
  branch. Do not create one unless asked.
- Use your file tools, not `rm` or `mv`, to delete or move files. Use forward slashes in paths.
