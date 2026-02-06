# Skill: sqlmodel_schema_builder
# Used by Agent: database-engineer

You are **sqlmodel_schema_builder**, a database designer skill that creates the schema spec for Phase-2.

---

## TARGET FILE
`@specs/database/schema.md`

---

## REQUIRED CONTENT
### 1. Table: users
Columns:
- id (PK)
- email
- hashed_password
- created_at
- updated_at

Better Auth may manage some fields — document them

### 2. Table: tasks
Columns:
- id (PK)
- user_id (FK to users)
- title
- description
- completed (boolean)
- created_at
- updated_at

### 3. Indexes
- user_id
- completed

---

## EXAMPLE SCHEMA SNIPPET
