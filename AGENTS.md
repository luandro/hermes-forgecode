# Project: hermes-forgecode

Agent Skills-compatible skill for delegating coding tasks to the Forge CLI.

## Architecture

- `SKILL.md` -- Agent-facing instructions (execution modes, agents, workflows, rules, gotchas). Loaded on skill activation.
- `references/cli-reference.md` -- Full CLI flags, subcommands, config. Loaded on demand.
- `references/agent-patterns.md` -- Multi-agent orchestration patterns (sage→muse→forge, parallel workers, validation loops). Loaded on demand.
- `hermes-forgecode.skill` -- Zip package bundling SKILL.md + references for distribution.
- `README.md` -- Human-facing overview (not loaded by agents).

## Conventions

- Frontmatter in SKILL.md follows the [Agent Skills specification](https://agentskills.io/specification): `name`, `description`, `license`, `compatibility`, `metadata` in YAML.
- Description includes trigger keywords for agent discovery (forge, forgecode, coding agent, sage, muse).
- Code examples use Python `computer(action="bash", ...)` syntax for hermes-agent compatibility.
- Gotchas section is the highest-value content -- every non-obvious behavior forge exhibits in non-interactive mode.

## Key Commands

```bash
# Validate skill against spec
skills-ref validate ./hermes-forgecode

# Rebuild .skill package
cd hermes-forgecode && zip -r ../hermes-forgecode.skill SKILL.md references/

# Check package contents
unzip -l hermes-forgecode.skill
```

## Skill Writing Best Practices (from agentskills.io)

These apply to this and all sibling skills:

1. **Frontmatter in YAML, not body** -- `license`, `compatibility`, `metadata` belong in frontmatter per spec.
2. **Description triggers discovery** -- Include specific keywords agents use to match tasks to skills.
3. **Gotchas are highest-value** -- Environment-specific facts that defy reasonable assumptions.
4. **Procedures over declarations** -- Teach *how to approach* a class of problems, not *what to produce* for one instance.
5. **Defaults, not menus** -- Pick a default tool/approach; mention alternatives briefly.
6. **Aim for moderate detail** -- SKILL.md under 500 lines / 5000 tokens. Move deep reference to `references/`.
7. **Progressive disclosure** -- Tell the agent *when* to load each reference file, not just "see references/".
8. **Add what the agent lacks, omit what it knows** -- Skip generic knowledge; focus on project-specific conventions and non-obvious edge cases.
9. **Refine with real execution** -- Run the skill against real tasks, feed results back, iterate.
10. **Match specificity to fragility** -- Be prescriptive for fragile operations; give freedom where multiple approaches work.
