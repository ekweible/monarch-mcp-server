# Security Hardening Notes

Current status: implemented for this fork.

## Goal

Keep this MCP server usable for personal, project-scoped finance work while minimizing auth, token, and dependency risk with a small upstream-friendly delta.

## Current Behavior

- Manual one-time auth only via `login_setup.py`
- No `MONARCH_EMAIL` / `MONARCH_PASSWORD` login fallback
- No dependency-managed saved session usage
- Token storage prefers system keyring
- Plaintext token file fallback is disabled by default
- Plaintext fallback requires `MONARCH_ALLOW_PLAINTEXT_TOKEN_STORAGE=true`
- Write tools are disabled by default
- Write tools require `MONARCH_ENABLE_WRITES=true`
- Runtime dependencies are pinned exactly
- `uv.lock` is committed and should stay committed

## Threat Model

- Main risk is not anonymous remote access
- Main risk is any MCP-capable agent in the project being able to use the Monarch session
- Main risk is accidental exposure of long-lived tokens or insecure session persistence
- Main risk is supply-chain drift during updates

## Project Scope

- Keep this server project-scoped only
- Do not enable it globally unless intentionally accepting broader agent access
- OpenCode project-local config uses `opencode.json`
- Claude Code project-local config uses `.mcp.json`

## Authentication

- Run `uv run python login_setup.py`
- Store only the long-lived token in keychain/keyring when available
- Do not store Monarch username/password in project files
- If keyring is unavailable and you explicitly accept plaintext token storage, set `MONARCH_ALLOW_PLAINTEXT_TOKEN_STORAGE=true`

## Write Access

- Default mode is read-only
- Enable writes only for sessions where transaction mutation is intended
- Write-enabled tools:
  - `create_transaction`
  - `update_transaction`
  - `set_transaction_tags`
  - `add_transaction_tag`
  - `create_transaction_tag`
  - `categorize_transaction`
  - `create_transaction_category`
  - `refresh_accounts`

## Local Dev Commands

Install and sync:

```bash
uv sync --frozen --extra dev
```

Run tests:

```bash
uv run pytest
```

Format and import checks:

```bash
uv run black --check src tests login_setup.py
uv run isort --check-only src tests login_setup.py
```

Run server directly:

```bash
uv run mcp run src/monarch_mcp_server/server.py
```

## Dependency Audit

Full audit:

```bash
uv audit --locked
```

Runtime deps only:

```bash
uv audit --locked --no-dev
```

Dev deps only:

```bash
uv audit --locked --only-dev
```

## Dependency Updates

Transitive refresh within current direct pins:

```bash
uv lock --upgrade
uv sync --frozen --extra dev
uv run pytest
```

Direct dependency update workflow:

1. Change the exact version in `pyproject.toml`
2. Keep `requirements.txt` in sync
3. Run:

```bash
uv lock
uv sync --frozen --extra dev
uv audit --locked --no-dev
uv run pytest
```

Note: since direct dependencies are pinned with `==`, `uv lock --upgrade-package ...` is not enough by itself. Update the pin first.

## Upstream Update Workflow

For each upstream merge or rebase:

1. Inspect all code changes
2. Check auth, token, and session-storage paths
3. Review lockfile diff
4. Run `uv audit --locked --no-dev`
5. Run `uv run pytest`
6. Merge only after review passes

## Fork Policy

- Prefer small localized changes over refactors
- Prefer preserving upstream structure and file layout
- If a gap is harmless for personal use, prefer merge-friendliness over extra cleanup
