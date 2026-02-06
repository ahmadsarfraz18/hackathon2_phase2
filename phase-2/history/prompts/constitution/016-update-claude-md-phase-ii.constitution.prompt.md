---
id: 016
title: Update CLAUDE.md with Phase II Requirements
stage: constitution
date: 2026-01-09
surface: agent
model: claude-sonnet-4.5-20250929
feature: none
branch: 001-todo-cli-core
user: Hp
command: Update CLAUDE.md for Phase II
labels: ["configuration", "phase-2", "agents"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - CLAUDE.md
tests:
  - Manual verification
---

## Prompt

**Update the "claude.md" file based on my project requirement.
In this file:**
- Use Auth Agnet for authentication
- Use Frontend Agent for frontend development (e.g., Next.js)
- Use DB Agent for database desing and operations
- Use Backend Agnet for FastAPI development.

BELOW are my project requirements:

""Phase II: Todo Full-Stack Web Application
Basic Level Functionality
Objective: Using Claude Code and Spec-Kit Plus transform the console app into a modern
multi-user web application with persistent storage.
💡Development Approach: Use the Agentic Dev Stack workflow: Write spec → Generate
plan → Break into tasks → Implement via Claude Code. No manual coding allowed. We will
review the process, prompts, and iterations to judge each phase and project.
Requirements
• Implement all 5 Basic Level features as a web application
• Create RESTful API endpoints
• Build responsive frontend interface
• Store data in Neon Serverless PostgreSQL database
• Authentication – Implement user signup/signin using Better Auth
Technology Stack
Layer Technology
Frontend Next.js 16+ (App Router)
Backend Python FastAPI
ORM SQLModel
Database Neon Serverless PostgreSQL
Spec-Driven Claude Code + Spec-Kit Plus
Authentication Better Auth
Better Auth can be configured to issue JWT (JSON Web Token) tokens when users log in.
These tokens are self-contained credentials that include user information and can be verified
by any service that knows the secret key.
How It Works
● User logs in on Frontend

## Response snapshot

I have updated `CLAUDE.md` to include the Phase II project requirements and specialized agent delegation instructions. The file now explicitly guides the assistant to use:
- **Auth Agent** for authentication and user isolation.
- **Frontend Engineer** for Next.js development.
- **Database Engineer** for SQLModel and Neon PostgreSQL.
- **Backend Engineer** for FastAPI development.

## Outcome

- ✅ Impact: Project instructions now reflect Phase II requirements and agentic workflow.
- 🧪 Tests: Manual verification of file content.
- 📁 Files: Updated `CLAUDE.md`.
- 🔁 Next prompts: None.
- 🧠 Reflection: Aligned the system instructions with the user's specific project phase and architectural needs.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
