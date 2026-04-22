# hermes-forgecode

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-Spec%20Compliant-blue)](https://agentskills.io)

An [Agent Skills](https://agentskills.io)-compatible skill that teaches [Hermes Agent](https://github.com/NousResearch/hermes-agent) (and any compatible AI agent) how to delegate coding tasks to [Forge](https://forgecode.dev) — an open-source terminal AI coding environment supporting 300+ LLMs.

## What this skill provides

- **Two execution modes**: one-shot (`forge -p "..."`, preferred for automation) and interactive TUI via tmux
- **Three built-in agents**: `forge` (implementation), `sage` (read-only research), `muse` (planning)
- **sage → muse → forge pipeline**: research before planning before implementing
- **Parallel work patterns**: git worktrees for independent concurrent tasks
- **Complete CLI reference**: flags, subcommands, conversation management, custom agents, MCP
- **5 orchestration patterns** with runnable Python code examples

## Files

```
hermes-forgecode/
├── SKILL.md                    # Main skill — execution modes, workflows, rules, pitfalls
└── references/
    ├── cli-reference.md        # Full CLI flags, subcommands, forge.yaml, env vars
    └── agent-patterns.md       # sage→muse→forge, parallel workers, validation loop, etc.
```

## Install

Copy or symlink this skill into your agent's skills directory:

```bash
# Hermes Agent (global)
git clone https://github.com/luandro/hermes-forgecode ~/hermes/skills/hermes-forgecode

# Forge (project-local)
git clone https://github.com/luandro/hermes-forgecode .forge/skills/hermes-forgecode

# Claude Code (global)
git clone https://github.com/luandro/hermes-forgecode ~/.claude/skills/hermes-forgecode
```

## Requirements

- [forge CLI](https://forgecode.dev) — `curl -fsSL https://forgecode.dev/cli | sh`
- `tmux` (optional) — for interactive multi-turn sessions
- `git` (optional) — for worktree-based parallel agent patterns

## Related skills

- [claude-code](https://github.com/NousResearch/hermes-agent/tree/main/skills/autonomous-ai-agents/claude-code) — delegate to Claude Code CLI
- [codex](https://github.com/NousResearch/hermes-agent/tree/main/skills/autonomous-ai-agents/codex) — delegate to OpenAI Codex CLI
- [opencode](https://github.com/NousResearch/hermes-agent/tree/main/skills/autonomous-ai-agents/opencode) — delegate to OpenCode CLI

## License

MIT
