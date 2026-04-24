---
name: hermes-forgecode
description: "Delegate coding tasks to Forge (Forgecode) CLI agent. Use when you need to build features, fix bugs, refactor code, perform code reviews, or do architecture research. Triggers: forge, forgecode, coding agent, multi-agent pipeline, sage, muse. Requires forge CLI installed."
license: MIT
compatibility: "Requires forge CLI (curl -fsSL https://forgecode.dev/cli | sh). Designed for hermes-agent; compatible with any agent skills implementation. Optional: tmux for interactive sessions, git for worktree patterns."
metadata:
  author: luandro
  version: "1.0.0"
  tags: [Coding-Agent, Forge, Forgecode, Code-Review, Refactoring, Multi-Agent, TailCallHQ, Autonomous]
  related_skills: [claude-code, codex, hermes-agent, opencode]
---

# Forge (Forgecode) Agent

Forge is an open-source terminal AI coding environment. It reads files, writes patches, executes shell commands, runs tests, and performs semantic code search.

## Execution Modes

### Mode 1: One-Shot (Preferred)

Non-interactive, no PTY required — ideal for automation and scripting:

```python
result = computer(action="bash", command='forge -p "Add error handling to src/auth.rs"', workdir="/path/to/repo")
```

Pipe context in:
```python
result = computer(action="bash", command='cat src/auth.rs | forge -p "Review this for security issues"', workdir="/path/to/repo")
```

Change directory and run:
```python
result = computer(action="bash", command='forge -C /path/to/repo -p "Fix the failing tests"')
```

Resume a conversation:
```python
result = computer(action="bash", command='forge --conversation-id abc123 -p "Continue the auth module implementation"', workdir="/path/to/repo")  # get IDs from: forge conversation list
```

### Mode 2: Interactive TUI via tmux

Use when multi-turn conversation or real-time monitoring is needed.

**Start session:**
```python
computer(action="bash", command="tmux new-session -d -s forge_session -x 220 -y 50")
computer(action="bash", command="tmux send-keys -t forge_session 'cd /path/to/repo && forge' Enter")
import time; time.sleep(3)
```

**Send prompts:**
```python
computer(action="bash", command="tmux send-keys -t forge_session 'Fix the authentication bug in auth.rs' Enter")
time.sleep(2)
output = computer(action="bash", command="tmux capture-pane -t forge_session -p")
```

**Clean up:**
```python
computer(action="bash", command="tmux kill-session -t forge_session")
```

## Built-In Agents

| Agent | CLI flag | Purpose | Modifies files? |
|-------|----------|---------|-----------------|
| `forge` | (default) | Implementation: builds features, fixes bugs, runs tests | Yes |
| `sage` | `--agent sage` | Research: maps architecture, traces data flow — read-only | No |
| `muse` | `--agent muse` | Planning: analyzes structure, writes plans to `plans/` | No |

**Use a specific agent:**
```python
# Research only — safe, no file modifications
result = computer(action="bash", command='forge --agent sage -p "Explain the auth flow in src/"', workdir="/path/to/repo")

# Planning only — writes to plans/ dir, no source code changes
result = computer(action="bash", command='forge --agent muse -p "Design a caching strategy for the API"', workdir="/path/to/repo")
```

## Common Workflows

### Feature Implementation

```python
result = computer(action="bash", command='forge -p "Implement rate limiting on /api/login using a Redis sliding window."', workdir="/path/to/repo")
```

### Research → Plan → Implement Pipeline

```python
# 1. Research (read-only)
research = computer(action="bash", command='forge --agent sage -p "How does session management work? Trace login to expiry."', workdir="/path/to/repo")

# 2. Plan (writes plans/plan.md)
plan = computer(action="bash", command='forge --agent muse -p "Design OAuth2 integration based on the current session system."', workdir="/path/to/repo")

# 3. Implement (executes the plan)
result = computer(action="bash", command='forge -p "Execute the plan in plans/plan.md"', workdir="/path/to/repo")
```

### AI Git Commit

```python
# Preview first
computer(action="bash", command='forge commit --preview', workdir="/path/to/repo")
# Commit
computer(action="bash", command='forge commit', workdir="/path/to/repo")
```

### Sandboxed Experimentation

Creates an isolated git worktree + branch automatically:
```python
result = computer(action="bash", command='forge --sandbox experiment-refactor -p "Refactor the database layer to use the repository pattern"', workdir="/path/to/repo")
```

## Parallel Work with Git Worktrees

Run multiple forge agents on independent tasks simultaneously:

```python
import subprocess

# Create worktrees
subprocess.run(['git', 'worktree', 'add', '/tmp/feat-auth', '-b', 'feat/auth'], cwd='/repo')
subprocess.run(['git', 'worktree', 'add', '/tmp/feat-api', '-b', 'feat/api'], cwd='/repo')

# Launch parallel agents (non-blocking)
p1 = subprocess.Popen(['forge', '-p', 'Implement OAuth2 authentication'], cwd='/tmp/feat-auth')
p2 = subprocess.Popen(['forge', '-p', 'Design REST API endpoints for users'], cwd='/tmp/feat-api')

p1.wait(); p2.wait()

# Note: parallel agents share the same API key and rate limit.
# With >2 workers, expect 429 retries — tune FORGE_RETRY_MAX_ATTEMPTS accordingly.
# Capture stderr separately: stderr=subprocess.PIPE or stderr=subprocess.STDOUT

# Clean up
subprocess.run(['git', 'worktree', 'remove', '/tmp/feat-auth'])
subprocess.run(['git', 'worktree', 'remove', '/tmp/feat-api'])
```

## Configuration

**`.forge.toml`** (project root or `~/forge/.forge.toml`):
```toml
[session]
model = "claude-3.7-sonnet"

[agent]
custom_instructions = """
Always add error handling.
Use conventional commits.
Run tests after changes.
"""
max_tool_failure_per_turn = 3
max_requests_per_turn = 100
```

**`AGENTS.md`** (project root): Persistent instructions injected into every agent session — use for project conventions, commit style, constraints.

**Key environment variables:**
```bash
FORGE_TOOL_TIMEOUT=300          # Max seconds per tool call (default: 300)
FORGE_HTTP_READ_TIMEOUT=900     # Timeout for long tasks; increase for long implementations (e.g. 900 for large tasks)
FORGE_RETRY_MAX_ATTEMPTS=3      # API retry count
FORGE_TRACKER=false             # Disable telemetry
FORGE_SESSION__MODEL_ID=haiku   # Override model (e.g. haiku, sonnet, gpt-4o)
FORGE_SESSION__PROVIDER_ID=open_router  # Override provider (e.g. open_router, anthropic)
FORGE_LOG=forge=debug        # Enable debug logging for troubleshooting
```

## Reference Files

- **[cli-reference.md](references/cli-reference.md)** — Full CLI flags, subcommands, conversation management.
- **[agent-patterns.md](references/agent-patterns.md)** — Multi-agent orchestration, sage→muse→forge pipeline, parallel patterns.

## Recommended Workflow (Plan-First)

For non-trivial tasks, plan before implementing. This decouples strategic thinking from coding pressure and produces better architectural decisions.

**1. Research with sage** — understand the codebase without risk:
```python
research = computer(action="bash", command='forge --agent sage -p "Map the auth flow from login to session expiry"', workdir="/path/to/repo")
```

**2. Plan with muse** — create a structured plan, then ask muse to critique its own gaps:
```python
plan = computer(action="bash", command='forge --agent muse -p "Design OAuth2 integration. Include scope, integration points, error handling, and edge cases. Then identify gaps or risks in your own plan."', workdir="/path/to/repo")
# Review plans/plan.md before proceeding
```

**3. Implement with forge** — reference the plan, commit frequently:
```python
result = computer(action="bash", command='forge -p "Execute plans/plan.md. Commit after each logical unit of work."', workdir="/path/to/repo")
```

**Key principles:**
- **Minimize agent switching** — each switch loses context and degrades cache performance. Batch all planning into one muse session, all implementation into one forge session.
- **Self-critique the plan** — explicitly ask muse to find flaws in its own output before handing off to forge.
- **Commit frequently** — forge should commit after each logical unit; makes review and rollback tractable.
- **Treat forge output as junior dev code** — review diffs before merging; don't blindly trust completeness.

## Rules for Hermes Agents

1. **Prefer one-shot mode** (`forge -p "..."`) for single tasks — no PTY, cleaner output.
2. **Always set `workdir`** — forge operates relative to the current directory; wrong directory produces garbage.
3. **Use `--agent sage`** for research — it is read-only and cannot modify files.
4. **Use `--agent muse`** for planning — it writes to `plans/` without touching source code.
5. **Set `FORGE_HTTP_READ_TIMEOUT`** for long implementations — increase for long implementations (e.g. 900 for large tasks).
6. **Use `--sandbox`** for experimental changes — automatic isolated worktree + branch.
7. **For parallel tasks**, use git worktrees and separate forge processes per worktree.
8. **Use tmux only for multi-turn sessions** that genuinely require back-and-forth conversation.
9. **Monitor TUI sessions** with `tmux capture-pane` — do not blindly sleep and assume completion.
10. **Always clean up tmux sessions** — `tmux kill-session -t forge_session`.

## Pitfalls & Gotchas

1. **Forge is a TUI app** — running `forge` without `-p` opens interactive mode and blocks the shell.
2. **ZSH plugin (`:` prefix) does NOT work in non-interactive shells** — always use `forge -p "..."` in scripts.
3. **`plans/` directory** — muse writes plans here; it creates the directory if needed.
4. **Session resume** — `--conversation-id` resumes an existing conversation; omit to start fresh.
5. **`--sandbox` creates a branch** — branch name is derived from the sandbox name; verify with `git branch`.
6. **Rate limits** — forge respects API rate limits; long tasks may pause; tune with `FORGE_RETRY_MAX_ATTEMPTS`.
7. **Model default** — forge uses the model in `.forge.toml` unless `FORGE_SESSION__MODEL_ID`/`FORGE_SESSION__PROVIDER_ID` env vars are set. There is no `--model` CLI flag.
