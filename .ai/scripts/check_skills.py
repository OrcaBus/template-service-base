#!/usr/bin/env python3
"""Check that every skill in .ai/skills/ has a matching stub for each supported AI tool.

A stub is `<tool dir>/<skill>/SKILL.md` with the same `name` and `description` as the real
skill, and a body that points at `.ai/skills/<skill>/SKILL.md`. See .ai/README.md.

Frontmatter values must be single-line `key: value` pairs.
Standard library only. Exit code 1 when a problem is found.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / '.ai' / 'skills'
TOOL_DIRS = ['.kiro/skills']  # add another tool's skills folder here to support it
POINTER_RE = re.compile(r'\.ai/skills/([A-Za-z0-9_-]+)/SKILL\.md')
FRONTMATTER_RE = re.compile(r'^---\r?\n(.*?)\r?\n---\r?\n(.*)$', re.DOTALL)


def read(path: Path) -> str:
    with open(path, encoding='utf-8', newline='') as handle:
        return handle.read()


def parse(path: Path):
    match = FRONTMATTER_RE.match(read(path))
    if not match:
        return None
    fields = {}
    for line in match.group(1).splitlines():
        if ':' in line:
            key, _, value = line.partition(':')
            fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields, match.group(2)


def main() -> int:
    errors = []
    skills = sorted(SKILLS_DIR.glob('*/SKILL.md')) if SKILLS_DIR.exists() else []

    for skill_file in skills:
        name = skill_file.parent.name
        parsed = parse(skill_file)
        if parsed is None:
            errors.append(f'.ai/skills/{name}/SKILL.md: missing frontmatter')
            continue
        fields = parsed[0]
        if fields.get('name') != name:
            errors.append(f'.ai/skills/{name}/SKILL.md: frontmatter name must be "{name}"')
        if not fields.get('description'):
            errors.append(f'.ai/skills/{name}/SKILL.md: description is empty')
            continue

        for tool_dir in TOOL_DIRS:
            stub = REPO_ROOT / tool_dir / name / 'SKILL.md'
            label = f'{tool_dir}/{name}/SKILL.md'
            if not stub.exists():
                errors.append(f'{label}: stub is missing')
                continue
            stub_parsed = parse(stub)
            if stub_parsed is None:
                errors.append(f'{label}: missing frontmatter')
                continue
            stub_fields, body = stub_parsed
            for key in ('name', 'description'):
                if stub_fields.get(key) != fields.get(key):
                    errors.append(f'{label}: {key} differs from .ai/skills/{name}/SKILL.md')
            if f'.ai/skills/{name}/SKILL.md' not in body:
                errors.append(f'{label}: body must point at .ai/skills/{name}/SKILL.md')

    known = {p.parent.name for p in skills}
    for tool_dir in TOOL_DIRS:
        for stub in sorted((REPO_ROOT / tool_dir).glob('*/SKILL.md')):
            parsed = parse(stub)
            if parsed is None:
                continue
            pointer = POINTER_RE.search(parsed[1])
            if pointer and pointer.group(1) not in known:
                label = stub.relative_to(REPO_ROOT).as_posix()
                errors.append(f'{label}: points at .ai/skills/{pointer.group(1)}, which does not exist')

    if errors:
        print('Skill check failed:')
        for error in errors:
            print(f'  - {error}')
        return 1
    print(f'Skill check OK ({len(skills)} skill(s), {len(TOOL_DIRS)} tool folder(s)).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
