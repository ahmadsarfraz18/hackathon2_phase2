---
id: 012
title: Fix Skills Detection via SKILL.md
stage: misc
date: 2026-01-08
surface: agent
model: claude-sonnet-4-5-20250929
feature: general
branch: 001-todo-cli-core
user: Hp
command: fix-skills-detection
labels: ["skills", "detection", "SKILL.md"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/api_contract_validator/SKILL.md
  - .claude/skills/architecture_spec_writer/SKILL.md
  - .claude/skills/better_auth_jwt_designer/SKILL.md
  - .claude/skills/fastapi_api_builder/SKILL.md
  - .claude/skills/nextjs_ui_builder/SKILL.md
  - .claude/skills/spec_kit_manager/SKILL.md
  - .claude/skills/sqlmodel_schema_builder/SKILL.md
tests:
  - none
---

## Prompt

The `/skills` command shows "No skills found" even though all skills exist in `.claude/skills/`. Fix the issue and show all the skills in the `/skills` list.

## Response snapshot

I have corrected the skill file naming convention. While previous attempts aimed for folder/file matching, the Claude Code CLI typically requires the primary skill file inside each subdirectory to be named exactly `SKILL.md` (all caps) to be indexed correctly. I have renamed all skill entry points to `SKILL.md` while maintaining their YAML metadata.

## Outcome

- ✅ Impact: Skills should now be detected by the Claude Code CLI.
- 🧪 Tests: None.
- 📁 Files: Renamed 7 skill files to `SKILL.md`.
- 🧠 Reflection: On many platforms and versions of the CLI, `SKILL.md` is the hardcoded entry point for skill detection in subdirectories.
