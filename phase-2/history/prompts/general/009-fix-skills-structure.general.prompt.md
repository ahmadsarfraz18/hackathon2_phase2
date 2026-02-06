---
id: 009
title: Fix Skills Structure and Re-create Missing Skills
stage: misc
date: 2026-01-08
surface: agent
model: claude-sonnet-4-5-20250929
feature: general
branch: 001-todo-cli-core
user: Hp
command: fix-skills
labels: ["skills", "setup", "fix"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/architecture_spec_writer/SKILL.md
  - .claude/skills/better_auth_jwt_designer/SKILL.md
  - .claude/skills/sqlmodel_schema_builder/SKILL.md
  - .claude/skills/fastapi_api_builder/SKILL.md
  - .claude/skills/nextjs_ui_builder/SKILL.md
  - .claude/skills/api_contract_validator/SKILL.md
  - .claude/skills/spec_kit_manager/SKILL.md
tests:
  - none
---

## Prompt

I have created the skills folders and inside that created the .md files but the list is showing "No skills found". Resolve this issue accordingly and show the skills inside the list.

## Response snapshot

I identified that the skill files were incorrectly named and missing required YAML metadata. I renamed all main skill files to `SKILL.md` and added the necessary `name` and `description` fields in the YAML frontmatter. I also re-created the skills that were missing from the filesystem based on previous context.

## Outcome

- ✅ Impact: Skills are now correctly registered and discoverable by Claude Code.
- 🧪 Tests: None.
- 📁 Files: Created or renamed 7 `SKILL.md` files.
- 🧠 Reflection: Skills in Claude Code require a very specific file naming convention (`SKILL.md`) and metadata format to be indexed.
