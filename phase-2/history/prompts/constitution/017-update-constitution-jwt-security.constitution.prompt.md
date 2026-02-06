---
id: 017
title: Update Constitution with JWT Security Layer
stage: constitution
date: 2026-01-09
surface: agent
model: claude-sonnet-4.5-20250929
feature: none
branch: 001-todo-cli-core
user: Hp
command: /sp.constitution
labels: ["constitution", "security", "jwt", "isolation"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - Manual verification
---

## Prompt

/sp.constitution

Project: Todo Full-Stack Web Application
Spec-1: Authentication, Identity, and JWT Security Layer

Core principles:
- Cryptographic identity assurance through signed JWTs
- Zero-trust backend architecture
- Strict user isolation across all API operations
- Stateless authentication across distributed services
- Deterministic and auditable authorization

Key standards:
- All backend API requests must include a valid Authorization: Bearer <JWT> header
- JWTs must be issued exclusively by Better Auth
- JWTs must be signed using the shared secret defined in BETTER_AUTH_SECRET
- Tokens must include verifiable user identity claims (user_id, email)
- FastAPI must validate JWT signature, expiration, and integrity on every request
- User identity must be extracted from the token, not from request parameters
- The authenticated user_id from the JWT must match the user_id in the API route
- Requests without a valid JWT must return HTTP 401 Unauthorized
- Requests with a mismatched or forged identity must return HTTP 403 Forbidden

Constraints:
- Better Auth is the sole authentication provider
- Session-based or cookie-based authentication is [interrupted]

## Response snapshot

I have updated the project constitution (`.specify/memory/constitution.md`) to integrate the **Authentication, Identity, and JWT Security Layer** principles and standards. The update defines a zero-trust backend architecture with strict user isolation, mandatory JWT verification via Better Auth, and stateless authentication across services.

## Outcome

- ✅ Impact: Project principles now mandate strict JWT-based security and user isolation.
- 🧪 Tests: Manual verification of the updated `constitution.md`.
- 📁 Files: Updated `.specify/memory/constitution.md`.
- 🔁 Next prompts: None.
- 🧠 Reflection: Aligned the foundational project governance with the required security model for Phase II.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
