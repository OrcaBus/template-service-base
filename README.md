Hello World Service
================================================================================

- [New Here? Start Here](#new-here-start-here)
- [Service Description](#service-description)
  - [Name \& responsibility](#name--responsibility)
  - [Description](#description)
  - [API Endpoints](#api-endpoints)
  - [Consumed Events](#consumed-events)
  - [Published Events](#published-events)
  - [(Internal) Data states \& persistence model](#internal-data-states--persistence-model)
  - [Major Business Rules](#major-business-rules)
  - [Permissions \& Access Control](#permissions--access-control)
  - [Change Management](#change-management)
    - [Versioning strategy](#versioning-strategy)
    - [Release management](#release-management)
- [Infrastructure \& Deployment](#infrastructure--deployment)
  - [Stateful](#stateful)
  - [Stateless](#stateless)
  - [CDK Commands](#cdk-commands)
  - [Stacks](#stacks)
- [Development](#development)
  - [Project Structure](#project-structure)
  - [Setup](#setup)
    - [Requirements](#requirements)
    - [Install Dependencies](#install-dependencies)
    - [First Steps](#first-steps)
  - [Conventions](#conventions)
  - [Linting \& Formatting](#linting--formatting)
  - [Testing](#testing)
- [Glossary \& References](#glossary--references)


New Here? Start Here
--------------------------------------------------------------------------------

If you are not familiar with AWS, Lambda, EventBridge, or CDK, read the beginner guide first:

- [`docs/beginner-guide.md`](docs/beginner-guide.md)

That guide explains:

- what this service does in plain language
- what "stack" means in this repository
- how Lambda, EventBridge, IAM, and CDK fit together
- how deployment works across toolchain and environment stacks
- which files to read first


Service Description
--------------------------------------------------------------------------------

### Name & responsibility

**Hello World** — a minimal Lambda service template for the OrcaBus platform.

### Description

This service demonstrates the canonical pattern for an event-driven Lambda microservice on OrcaBus:

1. An EventBridge rule filters `WorkflowRunStateChange` events from `orcabus.workflowmanager` for the `hello-world` workflow.
2. The matching events trigger a Python Lambda function.
3. The Lambda parses the incoming event using Pydantic models, extracts key fields, and emits a `HelloWorldEvent` back onto the `OrcaBusMain` event bus.

Use this repository as a starting point when building a new auxiliary service that reacts to OrcaBus events.

### API Endpoints

This service does not expose any API endpoints. It is purely event-driven.

### Consumed Events

| Name / DetailType            | Source                    | Schema Link | Description                                                                                   |
|------------------------------|---------------------------|-------------|-----------------------------------------------------------------------------------------------|
| `WorkflowRunStateChange`     | `orcabus.workflowmanager` |             | Fired on every state transition of a workflow run. Filtered to `workflow.name = hello-world`. |

### Published Events

| Name / DetailType   | Source                | Schema Link | Description                                         |
|---------------------|-----------------------|-------------|-----------------------------------------------------|
| `HelloWorldEvent`   | `orcabus.helloworld`  |             | Emitted after successfully processing a WRSC event. |

### (Internal) Data states & persistence model

This service is stateless. No data is persisted.

### Major Business Rules

- The Lambda only processes events for the `hello-world` workflow (enforced at the EventBridge rule level).
- A failed `put_events` call (non-zero `FailedEntryCount`) raises a `RuntimeError`, causing the Lambda to fail and triggering the standard retry/DLQ behaviour.

### Permissions & Access Control

No authentication or authorisation controls apply. The service is triggered exclusively via EventBridge rules and does not expose any user-facing interface.

### Change Management

#### Versioning strategy

Manual tagging of git commits following Semantic Versioning (semver) guidelines.

#### Release management

The service employs a fully automated CI/CD pipeline that automatically builds and releases all changes to the `main` branch across `beta`, `gamma`, and `prod` environments.


Infrastructure & Deployment
--------------------------------------------------------------------------------

Infrastructure is managed via CDK. This template provides two types of CDK entry points: `cdk-stateless` and `cdk-stateful`.

### Stateful

This service has no stateful resources.

### Stateless

- **`HelloWorldFunction`** — Python 3.12 ARM64 Lambda, bundled via `PythonLayerVersion` from `app/requirements.txt`.
- **`WorkflowRunStateChangeRule`** — EventBridge rule on `OrcaBusMain` that matches `WorkflowRunStateChange` events where `detail.workflow.name = hello-world`.

### CDK Commands

You can access CDK commands using the `pnpm` wrapper script.

- **`cdk-stateless`**: Used to deploy stacks containing stateless resources (e.g., AWS Lambda), which can be easily redeployed without side effects.
- **`cdk-stateful`**: Used to deploy stacks containing stateful resources (e.g., AWS DynamoDB, AWS RDS), where redeployment may not be ideal due to potential side effects.

The type of stack to deploy is determined by the context set in the `./bin/deploy.ts` file.

Pattern:
```sh
# Deploy a stateless stack
pnpm cdk-stateless deploy -e <stackname>
```

Examples:
```sh
# Deploy the BuildPipeline stack
pnpm cdk-stateless deploy -e OrcaBusStatelessHelloWorldStack

# Manually deploy the development stack
pnpm cdk-stateless deploy -e OrcaBusStatelessHelloWorldStack/DeploymentPipeline/OrcaBusBeta/HelloWorldStack
```

### Stacks

This CDK project manages multiple stacks. The root stack (the only one that does not include `DeploymentPipeline` in its stack ID) is deployed in the toolchain account and sets up a CodePipeline for cross-environment deployments to `beta`, `gamma`, and `prod`.

To list all available stacks, run:

```sh
pnpm cdk-stateless ls
```

Example output:

```sh
OrcaBusStatelessHelloWorldStack
OrcaBusStatelessHelloWorldStack/DeploymentPipeline/OrcaBusBeta/HelloWorldStack  (OrcaBusBeta-HelloWorldStack)
OrcaBusStatelessHelloWorldStack/DeploymentPipeline/OrcaBusGamma/HelloWorldStack (OrcaBusGamma-HelloWorldStack)
OrcaBusStatelessHelloWorldStack/DeploymentPipeline/OrcaBusProd/HelloWorldStack  (OrcaBusProd-HelloWorldStack)
```


Development
--------------------------------------------------------------------------------

### Project Structure

The root of the project is an AWS CDK project where the main application logic lives inside the `./app` folder.

The project is organized into the following key directories:

- **`./app`**: Contains the main application logic. You can open the code editor directly in this folder, and the application should run independently.

- **`./bin/deploy.ts`**: Serves as the entry point of the application. It initializes two root stacks: `stateless` and `stateful`. You can remove one of these if your service does not require it.

- **`./infrastructure`**: Contains the infrastructure code for the project:
  - **`./infrastructure/toolchain`**: Includes stacks for the stateless and stateful resources deployed in the toolchain account. These stacks primarily set up the CodePipeline for cross-environment deployments.
  - **`./infrastructure/stage`**: Defines the stage stacks for different environments:
    - **`./infrastructure/stage/config.ts`**: Contains environment-specific configuration files (e.g., `beta`, `gamma`, `prod`).
    - **`./infrastructure/stage/deployment-stack.ts`**: The CDK stack entry point for provisioning resources required by the application in `./app`.

- **`.github/workflows/pr-tests.yml`**: Configures GitHub Actions to run tests for `make check` (linting and code style), tests defined in `./test`, and `make test` for the `./app` directory. Modify this file as needed to ensure the tests are properly configured for your environment.

- **`./test`**: Contains tests for CDK code compliance against `cdk-nag`. You should modify these test files to match the resources defined in the `./infrastructure` folder.

### Setup

#### Requirements

```sh
node --version
v22.9.0

# Update Corepack (if necessary, as per pnpm documentation)
npm install --global corepack@latest

# Enable Corepack to use pnpm
corepack enable pnpm
```

#### Install Dependencies

To install all required dependencies, run:

```sh
make install
```

#### First Steps

Before using this template, search for all instances of `TODO:` comments in the codebase and update them as appropriate for your service. This includes replacing placeholder values (such as stack names, GitHub repo, and pipeline names).

### Conventions

### Linting & Formatting

Automated checks are enforced via pre-commit hooks, ensuring only checked code is committed. For details consult the `.pre-commit-config.yaml` file.

Manual, on-demand checking is also available via `make` targets. For details consult the `Makefile` in the root of the project.

To run linting and formatting checks on the root project, use:

```sh
make check
```

To automatically fix issues with ESLint and Prettier, run:

```sh
make fix
```

### Testing

Unit tests are available for the Lambda handler and Pydantic models. Test code is hosted alongside business logic in `./app/tests/`.

```sh
make test
```


Glossary & References
--------------------------------------------------------------------------------

For general terms and expressions used across OrcaBus services, please see the platform [documentation](https://github.com/OrcaBus/wiki/blob/main/orcabus-platform/README.md#glossary--references).

Service specific terms:

| Term           | Description                                                                                        |
|----------------|----------------------------------------------------------------------------------------------------|
| WRSC           | `WorkflowRunStateChange` — OrcaBus event emitted by the Workflow Manager on every state transition |
| `portalRunId`  | Unique identifier for a workflow run, used to correlate events across services                     |
| `OrcaBusMain`  | The shared AWS EventBridge event bus used by all OrcaBus services                                  |
