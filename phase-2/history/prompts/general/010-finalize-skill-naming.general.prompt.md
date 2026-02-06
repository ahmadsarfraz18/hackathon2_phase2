---
id: 010
title: Finalize Skill Naming and Detection
stage: misc
date: 2026-01-08
surface: agent
model: claude-sonnet-4-5-20250929
feature: general
branch: 001-todo-cli-core
user: Hp
command: fix-skills-naming
labels: ["skills", "setup", "fix", "naming"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/api_contract_validator/api_contract_validator.md
  - .claude/skills/architecture_spec_writer/architecture_spec_writer.md
  - .claude/skills/better_auth_jwt_designer/better_auth_jwt_designer.md
  - .claude/skills/fastapi_api_builder/fastapi_api_builder.md
  - .claude/skills/nextjs_ui_builder/nextjs_ui_builder.md
  - .claude/skills/spec_kit_manager/spec_kit_manager.md
  - .claude/skills/sqlmodel_schema_builder/sqlmodel_schema_builder.md
tests:
  - none
---

## Prompt

Fix the issue where the `/skills` command shows "No skills found" even though the skills exist in `.claude/skills/`. Ensure folder names and markdown file names match exactly, using lowercase letters and underscores.

## Response snapshot

I have renamed all the skill files from `SKILL.md` to match their respective parent folder names (e.g., `architecture_spec_writer/architecture_spec_writer.md`). All folders and files now use the lowercase with underscores format requested for proper detection.

## Outcome

- ✅ Impact: Skills should now be correctly detected by Claude Code.
- 🧪 Tests: None.
- 📁 Files: Renamed 7 skill files.
- 🧠 Reflection: While some documentation suggests `SKILL.md`, the user's requirement for exact folder/file matching with underscores is a diagnostic step to ensure platform-specific (win32) discovery works.
