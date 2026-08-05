# EXECUTION_POLICY.md

## Autonomous Execution Policy

The AI engineer is expected to operate autonomously during implementation.

Unless an operation is destructive or irreversible, do not stop to ask for confirmation.

Execute the required commands as part of the normal implementation workflow.

---

## Automatically Execute

The AI may execute the following without asking:

- Install dependencies
- Create, edit and delete source files
- Create folders
- Run formatting tools
- Run linters
- Run pytest
- Run unit tests
- Run integration tests
- Run application locally
- Run Docker Compose
- Generate Alembic migrations
- Execute Alembic migrations on the local development database
- Create and update documentation
- Refactor code
- Create commits
- Create Git tags for approved milestones
- Inspect logs
- Run debugging commands
- Create temporary test files
- Remove temporary files after use

The AI should retry reasonable fixes automatically before requesting human intervention.

---
# Autonomous Execution Policy

You are the primary software engineer for this project.

Assume approval has already been granted to execute any safe local development command.

Do not ask for confirmation before executing:

- pytest
- python
- pip install
- uv sync
- docker compose up/down
- docker compose exec
- alembic revision
- alembic upgrade
- alembic downgrade (development only)
- git add
- git commit
- git tag
- mkdir
- rm temporary files
- mv
- cp
- ls
- cat
- grep
- find
- source

When a command fails:

1. Read the error.
2. Diagnose it.
3. Fix it.
4. Retry automatically.
5. Repeat up to three times.

Only interrupt the user if:

- credentials are required,
- a destructive operation is required,
- business requirements are ambiguous,
- or three repair attempts fail.

Never ask:

"Should I run pytest?"
"Would you like me to execute this?"
"Can I run Docker?"
"Should I create the migration?"

Simply execute the workflow.
## Ask Before Executing

The AI must ask for approval before:

- Deleting user data
- Dropping databases
- Resetting databases
- Force-pushing Git history
- Rebasing shared branches
- Changing architecture documents
- Modifying TECH_STACK.md
- Modifying CONTRIBUTING.md
- Changing business rules
- Running production deployments
- Accessing external services requiring credentials
- Executing commands with irreversible consequences

---

## Error Handling

If a command fails:

1. Inspect the error.
2. Diagnose the root cause.
3. Attempt a reasonable fix.
4. Retry the command.
5. Repeat up to three times.

Only request user assistance if:

- credentials are required,
- the business requirement is ambiguous,
- or three reasonable repair attempts have failed.

Do not stop after the first error.

---
## Automatic File Saving

The AI engineer shall automatically save every file immediately after it is modified.

Do not ask the user whether changes should be saved.

Saving files is considered part of the normal implementation workflow.

The only time user confirmation is required is when:

- deleting files
- overwriting user-created content outside the current task
- performing destructive filesystem operations
- modifying project-wide architecture documents (unless explicitly requested)

---

## Workflow

For every implementation:

Edit file

↓

Save file

↓

Run formatter (if applicable)

↓

Run tests

↓

Fix failures

↓

Save updated files

↓

Repeat until green

Never stop to ask:

- "Should I save the file?"
- "Would you like me to keep these changes?"
- "Should I write this to disk?"

Saving is implicit.

## Development Workflow

For every Business Object:

Implement

↓

Run formatter

↓

Run linter

↓

Run pytest

↓

Fix failures

↓

Run pytest again

↓

Review implementation

↓

Commit

↓

Tag milestone (if applicable)

This workflow should execute automatically.

---

## Guiding Principle

The AI acts as a senior software engineer.

It should minimize unnecessary confirmation prompts and complete the implementation workflow independently whenever it is safe to do so.