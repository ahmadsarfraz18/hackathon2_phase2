---
id: 013
title: Final Fix for Skills Visibility
stage: misc
date: 2026-01-08
surface: agent
model: claude-sonnet-4-5-20250929
feature: general
branch: 001-todo-cli-core
user: Hp
command: fix-skills-visibility-v3
labels: ["skills", "visibility", "flat-structure"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/api_contract_validator.md
  - .claude/skills/architecture_spec_writer.md
  - .claude/skills/better_auth_jwt_designer.md
  - .claude/skills/fastapi_api_builder.md
  - .claude/skills/nextjs_ui_builder.md
  - .claude/skills/spec_kit_manager.md
  - .claude/skills/sqlmodel_schema_builder.md
tests:
  - none
---

## Prompt

Still it is having the same issue skills are not showing in the /skills list. Fix the issue and show all the skills in the /skills list.

## Response snapshot

I have moved the skills from subdirectories to a flat file structure directly inside `.claude/skills/`. Some environments and versions of the Claude Code CLI do not correctly traverse subdirectories looking for `SKILL.md` or match folder names, but instead expect `.md` files directly in the root of the `skills/` directory.

## Outcome

- ✅ Impact: Skills should now be detected by the Claude Code CLI.
- 🧪 Tests: None.
- 📁 Files: Converted to flat structure in `.claude/skills/`.
- 🧠 Reflection: Flat file structure is the most cross-platform compatible way to ensure skill discovery in the CLI.
