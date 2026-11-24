#!/usr/bin/env python3
"""Rename the Hello World template identifiers to a real service name.

Usage (from anywhere):
  python3 rename.py <kebab-name> [--repo <github-repo>] [--pascal <PascalName>] [--stateful] [--apply]

Without --apply it only prints the plan. Standard library only, works on macOS, Linux and Windows.
What it changes and what it leaves alone is documented in references/naming.md.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
STACK_FILE = REPO_ROOT / 'infrastructure' / 'stage' / 'deployment-stack.ts'
TEMPLATE_MODULE_DIR = REPO_ROOT / 'app' / 'hello_world'

SKIP_DIRS = {
    '.git', 'node_modules', 'cdk.out', '.cdk.staging', '.ai', '.kiro', 'ai-context',
    '__pycache__', '.venv', '.pytest_cache', '.ruff_cache', '.mypy_cache', 'coverage',
}  # fmt: skip
SKIP_FILES = {'pnpm-lock.yaml', 'AGENTS.md'}
TEXT_SUFFIXES = {'.ts', '.js', '.mjs', '.json', '.py', '.md', '.yml', '.yaml', '.txt'}
TEXT_NAMES = {'Makefile'}

HELLO_RE = re.compile(r'hello[ _-]?world', re.IGNORECASE)
NAME_RE = re.compile(r'^[a-z][a-z0-9]*(-[a-z0-9]+)*$')
PASCAL_RE = re.compile(r'^[A-Z][A-Za-z0-9]*$')
REPO_RE = re.compile(r'^[A-Za-z0-9._-]+$')


@dataclass(frozen=True)
class Names:
    kebab: str
    snake: str
    pascal: str
    repo: str


def fail(message: str, code: int = 1) -> None:
    print(f'ERROR: {message}', file=sys.stderr)
    sys.exit(code)


def derive(kebab: str, repo: str | None, pascal: str | None) -> Names:
    parts = kebab.split('-')
    return Names(
        kebab=kebab,
        snake='_'.join(parts),
        pascal=pascal or ''.join(part.capitalize() for part in parts),
        repo=repo or f'service-{kebab}',
    )


def read(path: Path) -> str:
    with open(path, encoding='utf-8', newline='') as handle:
        return handle.read()


def write(path: Path, text: str) -> None:
    with open(path, 'w', encoding='utf-8', newline='') as handle:
        handle.write(text)


def iter_text_files():
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for filename in sorted(filenames):
            if filename in SKIP_FILES:
                continue
            path = Path(dirpath) / filename
            if path.suffix in TEXT_SUFFIXES or filename in TEXT_NAMES:
                yield path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('name', help='service name in kebab-case, without a service- prefix')
    parser.add_argument('--repo', help='GitHub repository name (default: service-<name>)')
    parser.add_argument('--pascal', help='override the derived PascalCase name, e.g. FastqSync')
    parser.add_argument('--stateful', action='store_true',
                        help='the service needs a stateful stack: fill in its placeholder names')  # fmt: skip
    parser.add_argument('--apply', action='store_true', help='write the changes (default: dry run)')
    args = parser.parse_args()

    if not NAME_RE.match(args.name):
        fail('name must be kebab-case: lowercase letters, digits, single hyphens, starting with a letter.')
    if args.name.startswith('service-'):
        fail(f'drop the "service-" prefix: use "{args.name[len("service-"):]}" (the repo name gets it).')
    if args.name == 'hello-world':
        fail('name must differ from the template name.')
    if args.pascal and not PASCAL_RE.match(args.pascal):
        fail('--pascal must start with an uppercase letter and contain only letters and digits.')
    if args.repo and not REPO_RE.match(args.repo):
        fail('--repo contains characters that are not valid in a GitHub repository name.')

    if not STACK_FILE.exists() or 'HelloWorld' not in read(STACK_FILE):
        fail('this does not look like the unmodified template (HelloWorldStack not found). '
             'It may already be bootstrapped.', code=2)  # fmt: skip

    names = derive(args.name, args.repo, args.pascal)
    replacements = [
        # Deployment-side names only. The example app (events, event source, Lambda construct
        # names such as HelloWorldFunction) is app logic and is left for the developer.
        ('hello_world', names.snake),  # Python module directory and its imports
        ('HelloWorldStack', f'{names.pascal}Stack'),  # stage stack, props, toolchain stack id
        ('OrcaBus-StatelessHelloWorld', f'OrcaBus-Stateless{names.pascal}'),  # pipeline name
        ('hello-world-stack', f'{names.kebab}-stack'),  # test label
    ]
    file_specific = [
        ('infrastructure/toolchain/stateless-stack.ts',
         "githubRepo: 'template-service-base'", f"githubRepo: '{names.repo}'"),
        ('package.json', '"name": "template-service-base"', f'"name": "{names.repo}"'),
    ]  # fmt: skip

    # Only with --stateful: fill the name placeholders of the stateful pipeline. The `stack:`
    # placeholder is left, because it needs a real stateful stack class (app side).
    regex_specific = []
    if args.stateful:
        stateful_file = 'infrastructure/toolchain/stateful-stack.ts'
        regex_specific = [
            (stateful_file, r"githubRepo: /\*\*[^*]*\*/ 'service-microservice-manager'",
             f"githubRepo: '{names.repo}'"),
            (stateful_file, r"stackName: /\*\*[^*]*\*/ 'StatefulMicroserviceManager'",
             f"stackName: 'Stateful{names.pascal}Stack'"),
            (stateful_file, r"pipelineName: /\*\*[^*]*\*/ 'OrcaBus-StatefulMicroservice'",
             f"pipelineName: 'OrcaBus-Stateful{names.pascal}'"),
            ('bin/deploy.ts',
             r"/\* TODO: Replace with string\. Example: \*/ 'OrcaBusStateful\{ServiceName\}Stack'",
             f"'OrcaBusStateful{names.pascal}Stack'"),
        ]  # fmt: skip

    new_module_dir = REPO_ROOT / 'app' / names.snake
    if TEMPLATE_MODULE_DIR.exists() and new_module_dir.exists():
        fail(f'{new_module_dir.relative_to(REPO_ROOT).as_posix()} already exists.')

    changes = []
    matched_specific = set()
    for path in iter_text_files():
        try:
            text = read(path)
        except UnicodeDecodeError:
            continue
        updated, counts = text, {}
        for old, new in replacements:
            count = updated.count(old)
            if count:
                counts[old] = count
                updated = updated.replace(old, new)
        rel = path.relative_to(REPO_ROOT).as_posix()
        for target, old, new in file_specific:
            if rel == target and old in updated:
                counts[old] = updated.count(old)
                updated = updated.replace(old, new)
                matched_specific.add((target, old))
        for target, pattern, new in regex_specific:
            if rel == target:
                updated, found = re.subn(pattern, lambda _match, new=new: new, updated)
                if found:
                    counts['stateful placeholder'] = counts.get('stateful placeholder', 0) + found
                    matched_specific.add((target, pattern))
        if updated != text:
            changes.append((path, updated, counts))

    print(f'Service: {names.kebab}  (snake={names.snake}, Pascal={names.pascal}, repo={names.repo})')
    print(f'{"Applying" if args.apply else "Plan (dry run)"}:')
    for path, _, counts in changes:
        summary = ', '.join(f'{old} x{count}' for old, count in counts.items())
        print(f'  edit   {path.relative_to(REPO_ROOT).as_posix()}  [{summary}]')
    if TEMPLATE_MODULE_DIR.exists():
        print(f'  rename app/hello_world -> app/{names.snake}')
    for target, old, _ in file_specific + regex_specific:
        if (target, old) not in matched_specific:
            print(f'  warn   {target}: expected text not found: {old}')

    if not args.apply:
        print('\nDry run only. Re-run with --apply to write these changes.')
        return

    for path, updated, _ in changes:
        write(path, updated)
    if TEMPLATE_MODULE_DIR.exists():
        TEMPLATE_MODULE_DIR.rename(new_module_dir)

    print('\nDone.')
    report_remaining()


def report_remaining() -> None:
    """List what the developer still has to fill in after the rename."""
    todos, mentions = [], {}
    for path in iter_text_files():
        try:
            lines = read(path).splitlines()
        except UnicodeDecodeError:
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        for number, line in enumerate(lines, start=1):
            if path.suffix != '.md' and 'TODO:' in line:
                todos.append(f'  {rel}:{number}: {line.strip()[:90]}')
            if HELLO_RE.search(line):
                mentions[rel] = mentions.get(rel, 0) + 1

    print('\nPlaceholders for the developer to fill in (TODO:):')
    print('\n'.join(todos) if todos else '  none')
    print('\nFiles that still mention "hello-world" (workflow name or wording):')
    if mentions:
        for rel, count in mentions.items():
            print(f'  {rel} ({count})')
    else:
        print('  none')


if __name__ == '__main__':
    main()
