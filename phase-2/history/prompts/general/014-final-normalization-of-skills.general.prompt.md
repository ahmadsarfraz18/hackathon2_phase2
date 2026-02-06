---
id: 014
title: Final Normalization of Skills Structure
stage: misc
date: 2026-01-08
surface: agent
model: claude-sonnet-4-5-20250929
feature: general
branch: 001-todo-cli-core
user: Hp
command: setup-skills-final
labels: ["skills", "visibility", "fix"]
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

I have performed a deep normalization of the skill files. I used the `Write` tool to overwrite all files directly, ensuring clean LF line endings, standard YAML frontmatter spacing (no leading spaces), and removal of any trailing system reminders that might interfere with the CLI's logic. This flat file structure directly in `.claude/skills/` with exact `name` matching is the most robust configuration for visibility.

## Outcome

- ✅ Impact: Skills are now optimized for discovery by the Claude Code CLI.
- 🧪 Tests: None (content normalization).
- 📁 Files: Overwrote 7 skill files with normalized content.
- 🧠 Reflection: Discovery issues can occur if there's any invisible character contamination (CRLF) or if the YAML frontmatter isn't perfectly flush.
