---
id: 011
title: Fix Skills Identification and Naming
stage: misc
date: 2026-01-08
surface: agent
model: claude-sonnet-4-5-20250929
feature: general
branch: 001-todo-cli-core
user: Hp
command: setup-skills
labels: ["skills", "detection", "fix"]
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

Fix the issue where running `/skills` shows "No skills found" even though all skills exist in `.claude/skills/`. Ensure each skill has its own folder and a single markdown file inside named exactly the same as the folder. Use lowercase and underscores only. Ensure proper YAML frontmatter with the correct name.

## Response snapshot

I have updated all relevant skill folders and files in `.claude/skills/` to ensure they follow the strict naming convention of lowercase with underscores (e.g., `skill_name/skill_name.md`). I also verified and updated the YAML frontmatter `name` field in each file to match the folder/file name exactly, which is required for proper detection by the `/skills` command.

## Outcome

- ✅ Impact: Skills are now correctly named and configured for CLI detection.
- 🧪 Tests: None (configuration fix).
- 📁 Files: Updated 7 skill markdown files.
- 🧠 Reflection: Discovery of skills in this environment is highly sensitive to the consistency between the folder name, filename, and the `name` property in the YAML frontmatter.
