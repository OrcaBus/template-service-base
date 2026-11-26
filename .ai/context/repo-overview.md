# Repository overview

How this repository is organised. It does not describe what the service does. For that, read the
"Service" section of `AGENTS.md` and the code. Platform-wide rules are in
[platform-rules.md](platform-rules.md).

## What it is

One OrcaBus microservice, deployed to BETA, GAMMA and PROD through a CDK pipeline. The
infrastructure is TypeScript AWS CDK and uses the `DeploymentStackPipeline` construct from
`@orcabus/platform-cdk-constructs`.

The repository started from an example, so what the service does is up to its developers. The
trigger, the resources, the language and the shape of the app can all differ from that example.
Check `app/` and `infrastructure/stage/` instead of assuming.

## Layout

| Path                        | Purpose                                                                      |
| --------------------------- | ---------------------------------------------------------------------------- |
| `app/`                      | The application code and its tests                                           |
| `infrastructure/stage/`     | The service's own CDK stack, its constants and per-stage props (`config.ts`) |
| `infrastructure/toolchain/` | Pipelines that deploy the stage stack to each environment                    |
| `bin/deploy.ts`             | CDK entry point. Chooses stateless or stateful by `-c deployMode=`           |
| `test/`                     | Jest tests running `cdk-nag` (AwsSolutions) against the stacks               |
| `docs/`                     | Documentation                                                                |

Stateless resources are easy to redeploy. Stateful ones (database, bucket, queue) are kept and
not redeployed casually, so they have their own pipeline. A repo with no stateful resources has
no stateful stack.

## Deployment side and app side

- **Deployment side** is driven by the service name: `infrastructure/toolchain/`, `bin/deploy.ts`,
  the stage stack class name and the repo name. Change these only when the pipeline or the
  naming changes.
- **App side** is what the service does: `app/` and the resources in `infrastructure/stage/`.
  Day-to-day feature work happens here.
- A `TODO:` comment marks an unfinished placeholder. Search for `TODO:` to find them.

## The `app/` contract

CI (`.github/workflows/pr-tests.yml`) and the deployment pipeline
(`infrastructure/toolchain/stateless-stack.ts`) only touch `app/` through its Makefile.
Whatever language the app uses, `app/Makefile` must provide these targets:

| Target         | Called by                  | Purpose                           |
| -------------- | -------------------------- | --------------------------------- |
| `make install` | CI, pipeline               | Install the app's dependencies    |
| `make check`   | `make check-all`, pipeline | Lint and format check, no changes |
| `make test`    | CI, pipeline               | Unit tests                        |
| `make fix`     | `make fix-all`             | Auto-fix lint and format          |

Anything else about `app/` (layout, dependency file, test framework) is the app's own business,
except for the places listed next.

## Places tied to the app's language

If the app's language or runtime changes, check these too:

- `app/` contents and the `app/Makefile` commands
- The Lambda construct and any layer or bundling in `infrastructure/stage/`
- The language setup step in the `test-app` job of `.github/workflows/pr-tests.yml`
- The reason text of the `AwsSolutions-L1` suppression in `test/stage.test.ts`
- Docker or bundling needs for `pnpm test`

## Commands

| Command                               | What it does                                                                               |
| ------------------------------------- | ------------------------------------------------------------------------------------------ |
| `make install`                        | Install Node dependencies (frozen lockfile)                                                |
| `make check-all`                      | Lint and format checks, root and `app/`. This is what CI runs.                             |
| `make fix-all`                        | Auto-fix formatting and lint                                                               |
| `pnpm test`                           | Type-check and run CDK tests. Docker must be running if the Lambda is bundled with Docker. |
| `cd app && make install && make test` | App unit tests                                                                             |
| `pnpm cdk-stateless ls`               | List the stacks                                                                            |

## Repo constraints

- Pre-commit blocks commits to `main`, `master` and `release/*`. Work on a branch.
- Do not change the Lambda runtime or version, CDK library versions or the pnpm version unless asked.
- Never commit secrets or account-specific values. Use SSM parameters or environment variables.
