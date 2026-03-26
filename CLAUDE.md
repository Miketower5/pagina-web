# CLAUDE.md — AI Assistant Guide for `pagina-web`

This file provides context, conventions, and workflows for AI assistants (e.g. Claude Code) working in this repository.

---

## Repository Overview

**Name:** `pagina-web`
**Owner:** `miketower5`
**Purpose:** Web project repository. Update this section once the project purpose is established.

---

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Production-ready code |
| `claude/<description>` | AI-assisted feature or documentation branches |

**Development rule:** Always develop on the branch specified at session start. Never push directly to `main` without explicit permission.

---

## Git Workflow

```bash
# Start work on a feature
git checkout -b claude/<short-description>

# Stage only relevant files (avoid secrets, binaries)
git add <specific-files>

# Commit with a descriptive message
git commit -m "feat: brief description of what changed and why"

# Push and set upstream
git push -u origin <branch-name>
```

### Commit Message Conventions

Use the [Conventional Commits](https://www.conventionalcommits.org/) format:

| Prefix | When to use |
|---|---|
| `feat:` | New feature or capability |
| `fix:` | Bug fix |
| `docs:` | Documentation only |
| `refactor:` | Code restructure without behavior change |
| `style:` | Formatting, whitespace |
| `test:` | Adding or updating tests |
| `chore:` | Maintenance, dependency updates |

---

## AI Assistant Rules

1. **Read before editing.** Always read a file before modifying it.
2. **Minimal changes.** Only change what is necessary. Do not refactor surrounding code unless asked.
3. **No unnecessary files.** Do not create README, docs, or helper files unless explicitly requested.
4. **No force-push.** Never use `git push --force` or `git reset --hard` without explicit user approval.
5. **No auto-PR.** Do not open a pull request unless the user explicitly requests it.
6. **Confirm before destructive actions.** Deleting files, dropping data, or modifying CI/CD requires user confirmation.
7. **No secrets in commits.** Never commit `.env` files, API keys, passwords, or tokens.
8. **Security first.** Do not introduce SQL injection, XSS, command injection, or other OWASP Top 10 vulnerabilities.

---

## Project Structure

> This section should be updated as the project grows.

```
pagina-web/
├── CLAUDE.md          # This file
└── ...                # Project files to be added
```

---

## Development Setup

> Populate this section once the tech stack is established.

```bash
# Install dependencies (example — update for actual stack)
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

---

## Environment Variables

> List required environment variables here. Never commit actual values.

```
# Example — replace with real vars
# API_URL=
# DATABASE_URL=
```

Store secrets in `.env` (gitignored). Provide an `.env.example` with placeholder values.

---

## Testing

- Run tests before committing changes.
- Do not skip or suppress failing tests to make a build pass.
- If a test framework has not been set up, note it here and propose one before writing tests.

---

## Key Conventions

- Prefer editing existing files over creating new ones.
- Do not add unnecessary abstractions, helpers, or utilities for one-time use.
- Do not add error handling for scenarios that cannot occur.
- Keep functions and components focused and small.
- Match the code style of the surrounding file (indentation, naming, etc.).

---

*Last updated: 2026-03-26. Update this file whenever the project structure, stack, or conventions change significantly.*
