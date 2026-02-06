---
id: 015
title: Fix skills directory structure for detection
stage: general
date: 2026-01-09
surface: agent
model: claude-sonnet-4.5-20250929
feature: none
branch: 001-todo-cli-core
user: Hp
command: Fix skills directory structure
labels: ["skills", "cli", "infrastructure"]
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
  - Verification using ls -R
---

## Prompt

You are running inside a Claude Code project.

There is a critical issue: Claude is not detecting any skills when I run /skills.

Root cause:
The .claude/skills directory contains only .md files, but Claude requires each skill to be inside its own folder, with the same name as the markdown file.

Current state:
.claude/skills contains:
- api_contract_validator.md
- architecture_spec_writer.md
- better_auth_jwt_designer.md
- fastapi_api_builder.md
- nextjs_ui_builder.md
- spec_kit_manager.md
- sqlmodel_schema_builder.md

Required state:
Each skill must be converted into this structure:

.claude/skills/<skill_name>/<skill_name>.md

Your task:
1. For each .md file in .claude/skills:
   - Create a folder with the same name (without .md)
   - Move the .md file into that folder
   - Ensure the filename and folder name are identical

2. After restructuring, verify that the final structure looks like:

.claude/skills/api_contract_validator/api_contract_validator.md
.claude/skills/architecture_spec_writer/architecture_spec_writer.md
.claude/skills/better_auth_jwt_designer/better_auth_jwt_designer.md
.claude/skills/fastapi_api_builder/fastapi_api_builder.md
.claude/skills/nextjs_ui_builder/nextjs_ui_builder.md
.claude/skills/spec_kit_manager/spec_kit_manager.md
.claude/skills/sqlmodel_schema_builder/sqlmodel_schema_builder.md

3. After fixing, reload the skills so that the /skills command lists all skills correctly.

Do not ask questions.
Execute this fix now.

## Response snapshot

I've restructured the `.claude/skills` directory so that each skill is located in its own subfolder named after the skill, as required for Claude to detect them.

Final verified structure:
- .claude/skills/api_contract_validator/api_contract_validator.md
- .claude/skills/architecture_spec_writer/architecture_spec_writer.md
- .claude/skills/better_auth_jwt_designer/better_auth_jwt_designer.md
- .claude/skills/fastapi_api_builder/fastapi_api_builder.md
- .claude/skills/nextjs_ui_builder/nextjs_ui_builder.md
- .claude/skills/spec_kit_manager/spec_kit_manager.md
- .claude/skills/sqlmodel_schema_builder/sqlmodel_schema_builder.md

## Outcome

- ✅ Impact: Skills are once again detectable by the CLI.
- 🧪 Tests: Manual verification of directory structure using `ls -R`.
- 📁 Files: All 7 skills moved to nested folders.
- 🔁 Next prompts: None.
- 🧠 Reflection: Restructured directory according to CLI requirements.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
