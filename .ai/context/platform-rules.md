# Platform rules

The OrcaBus platform rules (event naming, event design, testing and quality gates, language
conventions) are maintained in the private `OrcaBus/ai-context` repository. Read them from
there instead of relying on a copy, so they are always current.

## How to read a file

This needs the GitHub CLI, logged in with access to the OrcaBus organisation (`gh auth status`).
The command works on macOS, Linux and Windows:

```
gh api -H "Accept: application/vnd.github.raw" repos/OrcaBus/ai-context/contents/<path>
```

To list a folder:

```
gh api repos/OrcaBus/ai-context/contents/<folder> --jq '.[].name'
```

Useful top-level folders are `platform`, `conventions`, `patterns` and `services`. List the repo
root to see the rest.

## Which file for what

| Need                                                   | Path                            |
| ------------------------------------------------------ | ------------------------------- |
| Event naming, event design rules, existing event types | `platform/event-catalog.md`     |
| Platform design guidelines                             | `platform/design-guidelines.md` |
| Testing and quality gates (cdk-nag, pre-commit, CI)    | `conventions/testing.md`        |
| TypeScript CDK conventions                             | `conventions/typescript-cdk.md` |
| Python Lambda conventions                              | `conventions/python-lambda.md`  |
| Which services exist and what they do                  | `platform/service-inventory.md` |

Read the file when the task needs it, for example before adding or changing an event.

## If it cannot be read

If the command fails (not logged in, no access, or offline), tell the developer and ask them to
run `gh auth login`. Do not guess the rules from memory.
