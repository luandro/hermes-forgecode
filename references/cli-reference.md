# Forge CLI Reference

## Global Flags

| Flag | Description |
|------|-------------|
| `-p, --prompt <PROMPT>` | One-shot prompt, exits after completion |
| `-e, --event <EVENT>` | Dispatch a JSON event to the workflow |
| `--conversation <FILE>` | Load conversation from a JSON file |
| `--conversation-id <ID>` | Resume an existing conversation by ID |
| `--agent <AGENT>` | Specify agent ID for the session (`forge`, `sage`, `muse`, or custom) |
| `-C, --directory <DIR>` | Change to this directory before starting |
| `--sandbox <NAME>` | Create isolated git worktree + branch for experimentation |
| `--model <MODEL>` | Override the default model for this session |
| `--verbose` | Enable verbose logging |

## Subcommands

### Conversation Management

```bash
forge conversation list                    # List all conversations
forge conversation resume <id>             # Resume by ID
forge conversation new                     # Start fresh conversation
forge conversation dump <id>               # Dump conversation to JSON
forge conversation compact <id>            # Compress conversation history
forge conversation retry <id>              # Retry the last message
forge conversation clone <id>              # Clone a conversation
forge conversation rename <id> <name>      # Rename a conversation
forge conversation delete <id>             # Delete a conversation
forge conversation info <id>               # Show conversation metadata
forge conversation stats                   # Show usage statistics
forge conversation show <id>               # Show conversation messages
```

### Git Integration

```bash
forge commit                               # AI-generated commit message
forge commit --preview                     # Preview commit message before committing
forge commit "context hint"                # Pass context to guide commit message
forge suggest "find large log files"       # Suggest shell command for a task
```

### Agent & Provider Management

```bash
forge list model                           # List available models
forge list agent                           # List available agents (built-in + custom)
forge list tool --agent <id>               # List tools/skills available to an agent
forge provider login                       # Authenticate a provider
forge provider logout                      # Remove provider credentials
forge provider list                        # List configured providers
```

### MCP Servers

```bash
forge mcp list                             # List connected MCP servers
forge mcp import <file>                    # Import MCP config from file
forge mcp show <name>                      # Show server details
forge mcp remove <name>                    # Remove a server
forge mcp reload                           # Reload all servers
```

### Workspace (Semantic Search)

```bash
forge workspace sync                       # Sync codebase for semantic search
forge workspace init                       # Initialize workspace index
forge workspace status                     # Show indexing status
forge workspace query "search term"        # Run semantic search
```

### Diagnostics

```bash
forge info                                 # Show forge version and config
forge doctor                               # Check installation health
forge update                               # Update forge to latest version
forge setup                                # Install ZSH plugin
```

## ZSH Plugin (Interactive Shell Only)

Once installed via `forge setup`, these shortcuts work at the ZSH prompt:

| Shortcut | Equivalent | Description |
|----------|------------|-------------|
| `: <prompt>` | `forge -p "<prompt>"` | Run default (forge) agent |
| `:ask <prompt>` | `forge --agent sage -p "<prompt>"` | Research with sage |
| `:plan <prompt>` | `forge --agent muse -p "<prompt>"` | Plan with muse |
| `:commit` | `forge commit` | AI git commit |
| `:suggest <desc>` | `forge suggest "<desc>"` | Suggest shell command |
| `:new` | `forge conversation new` | Start fresh conversation |
| `:agent <name>` | Switch active agent (fzf picker if no name) |
| `:skill` | List available skills |

**Note**: ZSH plugin does NOT work in non-interactive shells or scripts — use full `forge` commands instead.

## Custom Agents

Define custom agents as `.md` files with YAML front-matter:

**Location (highest precedence first):**
1. `.forge/agents/<name>.md` — project-local
2. `~/forge/agents/<name>.md` — global

**Format:**
```markdown
---
name: reviewer
description: Code reviewer focused on security and performance
model: claude-3.7-sonnet
---

You are a strict code reviewer. Focus on:
- Security vulnerabilities
- Performance bottlenecks  
- Missing error handling
- Test coverage gaps

Always provide specific line references and suggest concrete fixes.
```

**Use custom agent:**
```bash
forge --agent reviewer -p "Review the changes in src/auth/"
```

## Skills

Skills are reusable workflows the AI can invoke as tools.

**Built-in skills:**
- `create-skill` — scaffold a new custom skill
- `execute-plan` — execute a plan file from `plans/`
- `github-pr-description` — generate PR description from diff

**Skill locations (highest precedence first):**
1. `.forge/skills/<name>/SKILL.md` — project-local
2. `~/forge/skills/<name>/SKILL.md` — global
3. Built-in (embedded in binary)

**Invoke a skill explicitly:**
```
: generate a PR description using the github-pr-description skill
```

## forge.yaml Configuration

Full reference for `forge.yaml` (project root or `~/.forge/forge.yaml`):

```yaml
model: "claude-3.7-sonnet"              # Default model
temperature: 0.7                         # Response creativity (0.0-1.0)
max_walker_depth: 3                      # Directory traversal depth
max_tool_failure_per_turn: 3             # Failures before forcing turn completion
max_requests_per_turn: 50               # Max LLM requests per turn (then prompts to continue)
custom_rules: |                          # Persistent instructions for all agents
  1. Always add error handling.
  2. Use conventional commits.
  3. Run tests after changes.
commands:                                # CLI shortcuts
  - name: "review"
    description: "Review current changes"
    prompt: "Review the staged changes for bugs, security issues, and style."
```

## MCP Configuration (.mcp.json)

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "ghp_..." }
    },
    "http_service": {
      "url": "http://localhost:3000/events"
    }
  }
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FORGE_TOOL_TIMEOUT` | 60 | Max seconds a tool runs before termination |
| `FORGE_HTTP_READ_TIMEOUT` | 900 | HTTP read timeout (15min — good for long tasks) |
| `FORGE_RETRY_MAX_ATTEMPTS` | 3 | API retry count on transient errors |
| `FORGE_MAX_REQUESTS_PER_TURN` | 50 | Max LLM requests per turn (mirrors yaml) |
| `FORGE_WORKSPACE_SERVER_URL` | — | Self-hosted semantic search server URL |
| `FORGE_TRACKER` | true | Set to `false` to disable telemetry |
| `FORGE_LOG` | — | Log verbosity (e.g., `forge=info`, `forge=debug`) |
