# hermes-forgecode

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Spec%20Compliant-blue)](https://agentskills.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An [Agent Skills](https://agentskills.io)-compatible skill that teaches AI agents how to delegate coding tasks to [Forge](https://forgecode.dev) -- an open-source terminal AI coding environment supporting 300+ LLMs.

## Why This Skill?

Forge is a powerful coding agent, but it has non-obvious conventions that trip up automated orchestration:

- It's a **TUI app** -- running `forge` without `-p` opens interactive mode and blocks the shell
- The **ZSH `:` prefix** doesn't work in non-interactive shells -- you must use `forge -p "..."`
- There's **no `--model` CLI flag** -- models are set via config or environment variables
- **Three specialized agents** (forge, sage, muse) have distinct capabilities worth orchestrating as a pipeline

This skill packages all of that knowledge so any Agent Skills-compatible AI can delegate to Forge effectively.

## What You Get

| Capability | Description |
|---|---|
| **One-shot execution** | `forge -p "..."` for non-interactive, scriptable tasks |
| **Interactive TUI sessions** | tmux-based multi-turn conversation when needed |
| **Research agent** | `--agent sage` for read-only codebase analysis |
| **Planning agent** | `--agent muse` for architecture plans written to `plans/` |
| **Implementation agent** | Default `forge` agent that writes code, runs tests, commits |
| **Parallel work** | Git worktree patterns for concurrent independent tasks |
| **Sandboxed experiments** | `--sandbox` for isolated branches with automatic cleanup |

## Quick Start

```bash
# Install the skill
git clone https://github.com/luandro/hermes-forgecode ~/hermes/skills/hermes-forgecode

# Or for Forge itself
git clone https://github.com/luandro/hermes-forgecode .forge/skills/hermes-forgecode

# Or for Claude Code
git clone https://github.com/luandro/hermes-forgecode ~/.claude/skills/hermes-forgecode
```

**Requirements:**

- [Forge CLI](https://forgecode.dev) -- `curl -fsSL https://forgecode.dev/cli | sh`
- `tmux` (optional) -- for interactive multi-turn sessions
- `git` (optional) -- for worktree-based parallel patterns

## Usage Examples

### Build a Feature

```python
result = computer(
    action="bash",
    command='forge -p "Add rate limiting on /api/login using a Redis sliding window."',
    workdir="/path/to/repo"
)
```

### Research, Plan, Then Implement

The recommended pipeline for non-trivial tasks:

```python
# 1. Research (read-only, safe)
research = computer(
    action="bash",
    command='forge --agent sage -p "How does session management work? Trace login to expiry."',
    workdir="/path/to/repo"
)

# 2. Plan (writes to plans/, no source code changes)
plan = computer(
    action="bash",
    command='forge --agent muse -p "Design OAuth2 integration based on the current session system."',
    workdir="/path/to/repo"
)

# 3. Implement (executes the plan)
result = computer(
    action="bash",
    command='forge -p "Execute the plan in plans/plan.md"',
    workdir="/path/to/repo"
)
```

### Run Parallel Tasks

```python
import subprocess

# Create isolated worktrees
subprocess.run(['git', 'worktree', 'add', '/tmp/feat-auth', '-b', 'feat/auth'], cwd='/repo')
subprocess.run(['git', 'worktree', 'add', '/tmp/feat-api', '-b', 'feat/api'], cwd='/repo')

# Launch parallel agents
p1 = subprocess.Popen(['forge', '-p', 'Implement OAuth2 authentication'], cwd='/tmp/feat-auth')
p2 = subprocess.Popen(['forge', '-p', 'Design REST API endpoints for users'], cwd='/tmp/feat-api')

p1.wait(); p2.wait()
```

## Files

```
hermes-forgecode/
├── SKILL.md                    # Core skill -- execution modes, agents, workflows, rules
└── references/
    ├── cli-reference.md        # Full CLI flags, subcommands, env vars, config
    └── agent-patterns.md       # sage→muse→forge pipeline, parallel workers, validation loops
```

The skill uses [progressive disclosure](https://agentskills.io/specification#progressive-disclosure): agents load `SKILL.md` on activation, then read reference files only when the task calls for them.

## Built-In Agents

| Agent | CLI Flag | Purpose | Modifies Files? |
|---|---|---|---|
| `forge` | *(default)* | Implementation: builds features, fixes bugs, runs tests | Yes |
| `sage` | `--agent sage` | Research: maps architecture, traces data flow | No |
| `muse` | `--agent muse` | Planning: analyzes structure, writes plans to `plans/` | No |

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
```

**Key environment variables:**

```bash
FORGE_TOOL_TIMEOUT=300          # Max seconds per tool call
FORGE_HTTP_READ_TIMEOUT=900     # Increase for long implementations
FORGE_RETRY_MAX_ATTEMPTS=3      # API retry count
FORGE_TRACKER=false             # Disable telemetry
FORGE_SESSION__MODEL_ID=haiku   # Override model
FORGE_SESSION__PROVIDER_ID=open_router  # Override provider
```

## Related Skills

- [claude-code](https://github.com/NousResearch/hermes-agent/tree/main/skills/autonomous-ai-agents/claude-code) -- delegate to Claude Code CLI
- [codex](https://github.com/NousResearch/hermes-agent/tree/main/skills/autonomous-ai-agents/codex) -- delegate to OpenAI Codex CLI
- [opencode](https://github.com/NousResearch/hermes-agent/tree/main/skills/autonomous-ai-agents/opencode) -- delegate to OpenCode CLI

## License

MIT
