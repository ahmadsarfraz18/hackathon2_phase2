
<!--
SYNC IMPACT REPORT
==================
Version change: Initial → 1.0.0

Modified principles:
  - N/A (initial constitution)

Added sections:
  - Introduction and Principles
  - Project Architecture Overview
  - Feature Specifications
  - Phase-Wise Implementation Guidelines
  - Technology Stack and Integrations
  - Constraints and Best Practices
  - Bonus Features
  - Deployment Blueprints
  - References and Research Notes
  - Core Principles (6 new principles)
  - Development Workflow
  - Governance

Removed sections:
  - N/A (initial constitution)

Templates requiring updates:
  - ✅ spec-template.md (reviewed - aligned with principles)
  - ✅ plan-template.md (reviewed - Constitution Check section exists)
  - ✅ tasks-template.md (reviewed - test-first principle supported)
  - ✅ phr-template.prompt.md (reviewed - compatible)

Follow-up TODOs:
  - None - all placeholders filled
-->

# The Evolution of Todo – Mastering Spec-Driven Development & Cloud Native AI Constitution

## Introduction and Principles

This Constitution serves as the high-level guiding document for the Hackathon II project: "The Evolution of Todo – Mastering Spec-Driven Development & Cloud Native AI." It establishes the principles, constraints, architecture, feature progression, phase-wise requirements, technology stack, and development workflow for building progressively complex software using AI-driven Spec-Driven Development (SDD).

### Core Principles

#### I. Spec-Driven Development (NON-NEGOTIABLE)

Every feature and phase MUST begin with a comprehensive Markdown specification. Spec-Kit Plus and Claude Code are used to generate all implementations without manual boilerplate code. The workflow is immutable: Write Spec → Generate Plan → Break into Tasks → Implement via Claude Code. Specifications reference lower-level details and serve as the single source of truth for implementation decisions.

**Rationale**: Enforces clear requirements before implementation, prevents scope creep, ensures AI-driven code generation produces consistent, testable, and maintainable solutions.

#### II. Incremental Evolution

The project evolves in five progressive phases, each building upon the previous while maintaining independence for validation and demonstration. Phase I starts as a simple in-memory CLI and evolves through full-stack web, AI-powered chatbot, local Kubernetes, and distributed cloud-native architecture. Each phase MUST deliver working, testable functionality before proceeding.

**Rationale**: Enables progressive complexity management, validates architectural decisions incrementally, allows demonstration at each milestone, and reduces integration risk.

#### III. AI-First Development

Claude Code and Spec-Kit Plus are primary development tools. All code generation, testing, and implementation leverage AI capabilities. Manual boilerplate code is prohibited. Reusable Intelligence via Claude Code Subagents and Agent Skills MUST be utilized where appropriate.

**Rationale**: Maximizes development velocity, enforces consistency through AI patterns, reduces human error, and demonstrates agentic development capabilities.

#### IV. User Isolation and Security

Phases II+ MUST implement user isolation via Better Auth with JWT tokens. All API endpoints filter data by user_id. Authentication and authorization are non-negotiable. Secure cookie patterns (httpOnly, secure flags) MUST be used. Server Actions MUST include proper validation (Zod, Yup) and CSRF protection.

**Rationale**: Prevents data leakage between users, ensures multi-tenancy from Phase II onward, demonstrates enterprise-grade security practices, and prevents authentication vulnerabilities.

#### V. Full-Stack Separation

Frontend and backend maintain strict separation with clear API contracts. Frontend uses Next.js 16+ with App Router and Server Components. Backend uses FastAPI with SQLModel. Communication occurs via typed REST APIs. OpenAPI specifications MUST be generated and maintained.

**Rationale**: Enables independent deployment and scaling, clear API contracts for testing, leverages platform-specific optimizations (RSC on frontend, async Python on backend), and supports eventual microservices evolution.

#### VI. Cloud-Native Readiness

From Phase I, code and architecture consider cloud deployment. Phase IV targets local Minikube with Docker, Helm, and kubectl-ai. Phase V deploys to DigitalOcean Kubernetes (DOKS) with Kafka and Dapr. Infrastructure MUST follow cloud-native patterns (stateless services, external configuration, graceful degradation).

**Rationale**: Prevents architectural rewrites when moving to cloud, demonstrates production readiness, supports eventual multi-region deployment, and aligns with modern DevOps practices.

## Project Architecture Overview

### Monorepo Structure

```text
hatkathon2-todo-app/
├── .spec-kit/
│   └── config.yaml                    # Spec-Kit Plus configuration
├── .specify/
│   ├── memory/
│   │   └── constitution.md            # This file
│   ├── templates/
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   ├── tasks-template.md
│   │   ├── adr-template.md
│   │   └── phr-template.prompt.md
│   └── history/
│       ├── prompts/                   # Prompt History Records (PHRs)
│       └── adr/                       # Architecture Decision Records
├── specs/
│   ├── overview.md
│   ├── architecture.md
│   ├── features/                      # Feature specifications
│   ├── api/                           # API contracts
│   ├── database/                     # Database schemas
│   └── ui/                            # UI/UX specifications
├── frontend/                          # Next.js application
│   ├── src/
│   ├── tests/
│   └── CLAUDE.md                      # Frontend-specific AI guidance
├── backend/                           # FastAPI application
│   ├── src/
│   ├── tests/
│   └── CLAUDE.md                      # Backend-specific AI guidance
├── docker-compose.yml
├── README.md                          # Setup instructions
└── CLAUDE.md                          # Root AI instructions
```

### Architecture Evolution

- **Phase I**: Single-file Python CLI with in-memory storage
- **Phase II**: Monorepo with Next.js frontend + FastAPI backend + Neon PostgreSQL
- **Phase III**: Adds AI chatbot component with OpenAI ChatKit and MCP integration
- **Phase IV**: Containerized deployment on local Minikube with Helm charts
- **Phase V**: Distributed event-driven system with Kafka, Dapr, and DOKS

## Feature Specifications

Feature specifications reside in `specs/features/` following Spec-Kit Plus conventions. Each feature includes:

- **spec.md**: User stories, acceptance criteria, functional requirements, success criteria
- **plan.md**: Technical architecture, data model, API contracts, implementation approach
- **tasks.md**: Testable, dependency-ordered implementation tasks

Reference feature specifications for detailed requirements, API contracts, and implementation guidance.

### Todo App Feature Progression

#### Basic Level (Core Essentials – All Phases)

1. Add Task – Create new items with title/description
2. Delete Task – Remove by ID
3. Update Task – Modify details
4. View Task List – Display all with status
5. Mark as Complete – Toggle completion status

#### Intermediate Level (Organization & Usability – Phases II+)

1. Priorities & Tags/Categories – High/Medium/Low priority, labels like Work/Home
2. Search & Filter – By keyword, status, priority, date
3. Sort Tasks – By due date, priority, alphabetically

#### Advanced Level (Intelligent Features – Phases III+)

1. Recurring Tasks – Auto-reschedule (e.g., weekly)
2. Due Dates & Time Reminders – Date/time pickers, browser notifications

## Phase-Wise Implementation Guidelines

| Phase | Description | Technology Stack | Points | Due Date |
|-------|-------------|------------------|--------|----------|
| I | In-Memory Python Console App | Python 3.13+, UV, Claude Code, Spec-Kit Plus | 100 | Dec 7, 2025 |
| II | Full-Stack Web App | Next.js 16+ (App Router), FastAPI, SQLModel, Neon Serverless PostgreSQL, Better Auth | 150 | Dec 14, 2025 |
| III | AI-Powered Todo Chatbot | OpenAI ChatKit, Agents SDK, Official MCP SDK | 200 | Dec 21, 2025 |
| IV | Local Kubernetes Deployment | Docker, Minikube, Helm, kubectl-ai, kagent | 250 | Jan 4, 2026 |
| V | Advanced Cloud Deployment | Kafka, Dapr, DigitalOcean DOKS | 300 | Jan 18, 2026 |

**Total**: 1000 points. **Bonus**: Up to +600.

### Phase I: In-Memory Console App

- Python 3.13+ with UV package manager
- In-memory data structures (no persistence)
- CLI interface with command parsing
- Basic Todo CRUD operations
- Spec-driven implementation using Claude Code
- No external dependencies beyond Python standard library

### Phase II: Full-Stack Web App

- **Frontend**: Next.js 16+ with App Router, Server Components, Tailwind CSS
- **Backend**: FastAPI with SQLModel and Pydantic
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth with JWT tokens
- **API**: RESTful endpoints with OpenAPI documentation
- **Testing**: Pytest for backend, Playwright for E2E
- User isolation on all endpoints (e.g., GET /api/{user_id}/tasks)

### Phase III: AI-Powered Todo Chatbot

- **AI Integration**: OpenAI ChatKit for natural language understanding
- **Agents**: Claude Agents SDK for task orchestration
- **MCP**: Official MCP SDK for tool integration
- **Capabilities**: Natural language commands (e.g., "Reschedule my morning meetings to 2 PM")
- **Intelligence**: Context-aware task management, scheduling, prioritization
- **Optional Bonus**: Multi-language support (Urdu), Voice Commands

### Phase IV: Local Kubernetes Deployment

- **Containerization**: Docker multi-stage builds for frontend/backend
- **Orchestration**: Minikube for local Kubernetes cluster
- **Packaging**: Helm charts for deployment manifests
- **AI Tools**: kubectl-ai and kagent for cluster management
- **CI/CD**: Basic GitHub Actions for build and push
- **Monitoring**: Prometheus/Grafana setup (optional)

### Phase V: Advanced Cloud Deployment

- **Platform**: DigitalOcean Kubernetes (DOKS)
- **Messaging**: Apache Kafka for event-driven architecture
- **Runtime**: Dapr for service-to-service communication and state management
- **Architecture**: Microservices with eventual consistency
- **Observability**: Distributed tracing, centralized logging
- **High Availability**: Multi-zone deployment, auto-scaling

## Technology Stack and Integrations

### Frontend Stack (Phase II+)

- **Framework**: Next.js 16+ with App Router
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui, Radix UI (preferred)
- **State Management**: Server Components by default, React Context for client state
- **Forms**: Server Actions with progressive enhancement
- **Deployment**: Vercel (for web phases)

### Backend Stack (Phase II+)

- **Framework**: FastAPI (Python 3.13+)
- **ORM**: SQLModel
- **Validation**: Pydantic v2
- **Authentication**: Better Auth with JWT
- **Testing**: Pytest with pytest-asyncio
- **API Documentation**: Auto-generated OpenAPI (Swagger UI)

### Infrastructure Stack

- **Package Manager**: UV (Python), npm/pnpm (Node.js)
- **Database**: Neon Serverless PostgreSQL
- **Containerization**: Docker
- **Orchestration**: Kubernetes (Minikube → DOKS)
- **Event Streaming**: Apache Kafka
- **Runtime**: Dapr
- **Helm**: Package management for Kubernetes

### AI Stack (Phase III+)

- **LLM**: OpenAI GPT-4/o1 via official API
- **Chat Framework**: OpenAI ChatKit
- **Agents**: Claude Agents SDK
- **Protocol**: Model Context Protocol (MCP) via Official MCP SDK

## Constraints and Best Practices

### Development Constraints

- **Spec-Driven**: No implementation without specification approval
- **AI-Generated**: All code MUST be generated by Claude Code
- **No Manual Boilerplate**: Use AI tools for repetitive code
- **Windows Users**: MUST use WSL 2 with Ubuntu-22.04
- **Monorepo**: Follow defined directory structure strictly
- **Version Control**: Clear commit messages linked to specs

### Code Quality Standards

- **Type Safety**: Strict TypeScript (frontend), mypy (backend)
- **Linting**: ESLint (frontend), Ruff (backend)
- **Formatting**: Prettier (frontend), Black (backend)
- **Testing**: Unit tests for critical logic, integration tests for API contracts
- **Documentation**: Inline comments only for "why", not "what"

### Architecture Principles

- **Separation of Concerns**: Clear boundaries between frontend/backend
- **API-First**: API contracts defined before implementation
- **Stateless Services**: No in-memory state across requests
- **Fail-Safe Design**: Graceful degradation for all failure modes
- **Observability**: Structured logging, metrics, tracing

### Security Requirements

- **Authentication**: JWT tokens with expiration
- **Authorization**: User-scoped data access
- **Input Validation**: Zod/Yup schemas on all inputs
- **CSRF Protection**: CSRF tokens on all mutations
- **Secrets Management**: Environment variables only, never in code

### Performance Goals

- **Frontend**: Core Web Vitals (LCP < 2.5s, CLS < 0.1)
- **Backend**: p95 latency < 500ms for API endpoints
- **Database**: Query optimization with indexes
- **Caching**: Strategic caching for read-heavy operations
- **Bundle Size**: Minimize client-side JavaScript

## Bonus Features

### Reusable Intelligence via Claude Code Subagents and Agent Skills (+200)

- Define reusable subagents for common tasks (e.g., database migration, API endpoint creation)
- Create agent skills for project-specific patterns
- Document skill usage in `.claude/skills/`
- Demonstrate skill composition and reuse across phases

### Cloud-Native Blueprints via Agent Skills (+200)

- Create Helm chart templates via agent skills
- Generate Kubernetes manifests as code
- Implement GitOps workflows with Flux/ArgoCD
- Document deployment blueprints for reuse

### Multi-Language Support (Urdu in chatbot) (+100)

- Add Urdu language support in AI chatbot
- Implement bilingual UI where applicable
- Use translation APIs or models
- Test language switching functionality

### Voice Commands for Todo (+200)

- Integrate Web Speech API for voice input
- Support natural language voice commands
- Add audio feedback for confirmations
- Test across browsers with voice API support

## Deployment Blueprints

### Local Development

- **Phase I**: Direct Python execution (`uv run main.py`)
- **Phase II+**: Docker Compose for local development stack
- **Phase III**: Add AI service containers to compose file
- **Phase IV**: Minikube with local registry

### Deployment Environments

- **Development**: Local Docker Compose / Minikube
- **Staging**: Vercel Preview deployments (frontend) + Test server (backend)
- **Production**: DigitalOcean Kubernetes with managed services

### CI/CD Pipeline

```yaml
# High-level CI/CD flow
1. Commit triggers GitHub Actions
2. Run tests (unit, integration, E2E)
3. Build Docker images (frontend, backend)
4. Push to container registry
5. Deploy to preview environment
6. On merge to main: Deploy to production
```

### Monitoring and Observability

- **Logging**: Structured JSON logs with correlation IDs
- **Metrics**: Prometheus for system metrics
- **Tracing**: OpenTelemetry for distributed tracing
- **Alerting**: Critical errors trigger notifications
- **Dashboards**: Grafana for real-time monitoring

## Development Workflow (Agentic Dev Stack)

### Spec-Driven Development Cycle

1. **Write Spec** (`/sp.specify`): Create feature specification with user stories, acceptance criteria
2. **Generate Plan** (`/sp.plan`): Research architecture, create data model, define API contracts
3. **Break into Tasks** (`/sp.tasks`): Generate dependency-ordered implementation tasks
4. **Implement** (`/sp.implement`): Execute tasks via Claude Code with AI assistance
5. **Test**: Run tests, validate against acceptance criteria
6. **Demo**: Create <90 second demo video
7. **Deploy**: Push to Vercel (web phases) or Kubernetes (cloud phases)
8. **Submit**: Via Google Form for each phase

### API Development Process

For Phase II+, secure REST API endpoints MUST include:

- `GET /api/{user_id}/tasks` – List all tasks for user (with optional filters)
- `POST /api/{user_id}/tasks` – Create new task
- `GET /api/{user_id}/tasks/{task_id}` – Get specific task
- `PUT /api/{user_id}/tasks/{task_id}` – Update task
- `DELETE /api/{user_id}/tasks/{task_id}` – Delete task

All endpoints MUST validate user ownership via JWT token and return appropriate HTTP status codes.

### Testing Strategy

- **Unit Tests**: Business logic, utilities, model validation
- **Integration Tests**: API contracts, database operations
- **E2E Tests**: Critical user journeys with Playwright
- **Contract Tests**: API endpoint validation
- **Performance Tests**: Load testing for production readiness

## Governance

### Amendment Procedure

- Constitution amendments require explicit documentation
- Changes MUST update version following semantic versioning:
  - **MAJOR**: Backward-incompatible principle removals or redefinitions
  - **MINOR**: New principle or section added
  - **PATCH**: Clarifications, wording, non-semantic refinements
- All amendments MUST propagate to dependent templates
- Changes require Sync Impact Report at top of constitution

### Compliance Review

- All plans MUST pass Constitution Check before implementation
- Pull requests MUST verify compliance with principles
- Complexity violations MUST be justified in Complexity Tracking table
- Use `.specify/templates/plan-template.md` for runtime development guidance

### Versioning Policy

- Current version: **1.0.0** (Initial ratification)
- Ratified: **2025-12-07** (Project start)
- Last amended: **2025-12-07**
- Version history maintained in Sync Impact Report

### Documentation Requirements

- **Public GitHub Repo**: Constitution.md, specs history folder, /src, README.md
- **README.md**: Setup instructions for all platforms (Linux, macOS, Windows WSL2)
- **CLAUDE.md**: Root and frontend/backend directories with AI-specific guidance
- **PHRs**: Prompt History Records in `history/prompts/` for all major decisions
- **ADRs**: Architecture Decision Records in `history/adr/` for significant choices

### Deliverables Per Phase

1. **Code Changes**: Updated codebase with phase-specific features
2. **Documentation**: Updated specs, plans, README.md if needed
3. **Demo Video**: <90 seconds showing phase functionality
4. **Published App**: Vercel link for web phases (II+)
5. **Submission**: Via Google Form with required fields filled

## References and Research Notes

### Spec-Driven Development Resources

- **Spec-Kit Plus**: Framework for spec-driven development and artifact generation
- **Spec-Driven Infrastructure Automation**: Research on automated infrastructure provisioning from specs
- **Claude Code**: Anthropic's CLI for AI-assisted development

### AI and Agent Research

- **ChatGPT Progressive Learning**: Techniques for context accumulation and improvement
- **Governing AI Agents with Claude Code**: Best practices for agentic development
- **Model Context Protocol (MCP)**: Open protocol for AI tool integration

### Technology Documentation

- **Next.js Documentation**: App Router, Server Components, Server Actions
- **FastAPI Documentation**: Async Python web framework, dependency injection
- **SQLModel Documentation**: Pydantic models for SQLAlchemy
- **Better Auth Documentation**: Next.js authentication with JWT
- **Dapr Documentation**: Distributed application runtime for microservices

### Cloud-Native Resources

- **Kubernetes Documentation**: Container orchestration, Helm charts
- **Apache Kafka Documentation**: Event streaming, topic management
- **DigitalOcean DOKS**: Managed Kubernetes service
- **Helm**: Package manager for Kubernetes

---

**Version**: 1.0.0 | **Ratified**: 2025-12-07 | **Last Amended**: 2025-12-07
