"""Tests for SKILL.md structure, frontmatter, and reference file integrity.

Verifies:
1. SKILL.md has valid YAML frontmatter with required fields
2. All referenced files exist
3. SKILL.md content references match actual file paths
4. Reference files have substantive content
5. SKILL.md follows the Agent Skills specification conventions
"""

import os
import re

import pytest
import yaml

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_MD = os.path.join(SKILL_ROOT, "SKILL.md")


def read_skill_md() -> str:
    with open(SKILL_MD, "r") as f:
        return f.read()


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from a markdown file. Returns (metadata, body)."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    if not match:
        pytest.fail("SKILL.md has no valid YAML frontmatter (missing --- delimiters)")
    metadata = yaml.safe_load(match.group(1))
    body = match.group(2)
    return metadata, body


class TestFrontmatter:
    """Verify SKILL.md frontmatter follows the Agent Skills specification."""

    @pytest.fixture(scope="class")
    def skill_data(self):
        content = read_skill_md()
        metadata, body = parse_frontmatter(content)
        return metadata, body

    def test_has_name(self, skill_data) -> None:
        metadata, _ = skill_data
        assert "name" in metadata, "Frontmatter missing 'name' field"
        assert metadata["name"] == "hermes-forgecode"

    def test_has_description(self, skill_data) -> None:
        metadata, _ = skill_data
        assert "description" in metadata, "Frontmatter missing 'description' field"
        assert isinstance(metadata["description"], str)
        assert len(metadata["description"]) > 20, "Description is too short"

    def test_description_has_trigger_keywords(self, skill_data) -> None:
        """Description should include trigger keywords for agent discovery."""
        metadata, _ = skill_data
        desc = metadata["description"].lower()
        keywords = ["forge", "forgecode", "coding agent"]
        missing = [kw for kw in keywords if kw not in desc]
        assert not missing, f"Description missing trigger keywords: {missing}"

    def test_has_license(self, skill_data) -> None:
        metadata, _ = skill_data
        assert "license" in metadata, "Frontmatter missing 'license' field"
        assert metadata["license"] == "MIT"

    def test_has_compatibility(self, skill_data) -> None:
        metadata, _ = skill_data
        assert "compatibility" in metadata, "Frontmatter missing 'compatibility' field"

    def test_has_metadata_block(self, skill_data) -> None:
        metadata, _ = skill_data
        assert "metadata" in metadata, "Frontmatter missing 'metadata' block"
        meta = metadata["metadata"]
        assert "author" in meta, "metadata missing 'author'"
        assert "version" in meta, "metadata missing 'version'"
        assert "tags" in meta, "metadata missing 'tags'"

    def test_has_allowed_tools(self, skill_data) -> None:
        metadata, _ = skill_data
        assert "allowed-tools" in metadata, "Frontmatter missing 'allowed-tools' field"

    def test_version_is_semver(self, skill_data) -> None:
        metadata, _ = skill_data
        version = str(metadata["metadata"]["version"])
        # Basic semver check: X.Y.Z
        assert re.match(r"^\d+\.\d+\.\d+$", version), (
            f"Version '{version}' is not semver format (X.Y.Z)"
        )


class TestSkillMdStructure:
    """Verify SKILL.md has the expected sections and content."""

    @pytest.fixture(scope="class")
    def skill_body(self):
        content = read_skill_md()
        _, body = parse_frontmatter(content)
        return body

    def test_has_execution_modes_section(self, skill_body) -> None:
        assert "## Execution Modes" in skill_body, "Missing '## Execution Modes' section"

    def test_has_one_shot_mode(self, skill_body) -> None:
        assert "### Mode 1: One-Shot" in skill_body, "Missing '### Mode 1: One-Shot' section"

    def test_has_interactive_tui_mode(self, skill_body) -> None:
        assert "### Mode 2: Interactive TUI" in skill_body, "Missing '### Mode 2: Interactive TUI' section"

    def test_has_built_in_agents_section(self, skill_body) -> None:
        assert "## Built-In Agents" in skill_body, "Missing '## Built-In Agents' section"

    def test_has_workflows_section(self, skill_body) -> None:
        assert "## Common Workflows" in skill_body, "Missing '## Common Workflows' section"

    def test_has_configuration_section(self, skill_body) -> None:
        assert "## Configuration" in skill_body, "Missing '## Configuration' section"

    def test_has_reference_files_section(self, skill_body) -> None:
        assert "## Reference Files" in skill_body, "Missing '## Reference Files' section"

    def test_has_rules_section(self, skill_body) -> None:
        assert "## Rules for Hermes Agents" in skill_body, "Missing '## Rules for Hermes Agents' section"

    def test_has_gotchas_section(self, skill_body) -> None:
        assert "## Pitfalls & Gotchas" in skill_body, "Missing '## Pitfalls & Gotchas' section"

    def test_has_parallel_work_section(self, skill_body) -> None:
        assert "## Parallel Work" in skill_body or "git worktree" in skill_body.lower(), (
            "Missing parallel work / git worktree section"
        )

    def test_has_recommended_workflow(self, skill_body) -> None:
        assert "## Recommended Workflow" in skill_body, "Missing '## Recommended Workflow' section"

    def test_mentions_forge_agent(self, skill_body) -> None:
        assert "forge" in skill_body.lower()

    def test_mentions_sage_agent(self, skill_body) -> None:
        assert "sage" in skill_body.lower()

    def test_mentions_muse_agent(self, skill_body) -> None:
        assert "muse" in skill_body.lower()

    def test_mentions_forge_dash_p(self, skill_body) -> None:
        """The one-shot flag '-p' should be prominently documented."""
        assert "forge -p" in skill_body or 'forge -p "' in skill_body or "forge -p '" in skill_body

    def test_mentions_conversation_id(self, skill_body) -> None:
        assert "--conversation-id" in skill_body, "Missing --conversation-id flag documentation"

    def test_mentions_sandbox(self, skill_body) -> None:
        assert "--sandbox" in skill_body, "Missing --sandbox flag documentation"

    def test_mentions_tmux(self, skill_body) -> None:
        assert "tmux" in skill_body.lower(), "Missing tmux documentation"

    def test_mentions_forge_toml(self, skill_body) -> None:
        assert ".forge.toml" in skill_body, "Missing .forge.toml configuration reference"

    def test_mentions_agents_md(self, skill_body) -> None:
        assert "AGENTS.md" in skill_body, "Missing AGENTS.md reference"


class TestReferenceLinks:
    """Verify all file references in SKILL.md point to existing files."""

    @pytest.fixture(scope="class")
    def skill_body(self):
        content = read_skill_md()
        _, body = parse_frontmatter(content)
        return body

    def test_cli_reference_file_exists(self) -> None:
        path = os.path.join(SKILL_ROOT, "references", "cli-reference.md")
        assert os.path.isfile(path), "references/cli-reference.md not found"

    def test_agent_patterns_file_exists(self) -> None:
        path = os.path.join(SKILL_ROOT, "references", "agent-patterns.md")
        assert os.path.isfile(path), "references/agent-patterns.md not found"

    def test_skill_md_links_to_cli_reference(self, skill_body) -> None:
        assert "references/cli-reference.md" in skill_body, (
            "SKILL.md doesn't link to references/cli-reference.md"
        )

    def test_skill_md_links_to_agent_patterns(self, skill_body) -> None:
        assert "references/agent-patterns.md" in skill_body, (
            "SKILL.md doesn't link to references/agent-patterns.md"
        )


class TestReferenceFileContent:
    """Verify reference files have substantive content."""

    def test_cli_reference_has_content(self) -> None:
        path = os.path.join(SKILL_ROOT, "references", "cli-reference.md")
        with open(path, "r") as f:
            content = f.read()
        assert len(content) > 500, "cli-reference.md seems too short"
        # Should document key sections
        assert "Global Flags" in content, "cli-reference.md missing 'Global Flags' section"
        assert "Environment Variables" in content, "cli-reference.md missing 'Environment Variables' section"

    def test_agent_patterns_has_content(self) -> None:
        path = os.path.join(SKILL_ROOT, "references", "agent-patterns.md")
        with open(path, "r") as f:
            content = f.read()
        assert len(content) > 500, "agent-patterns.md seems too short"
        # Should document the key patterns
        assert "sage" in content.lower()
        assert "muse" in content.lower()
        assert "forge" in content.lower()


class TestSkillMdSize:
    """Verify SKILL.md follows the recommended size guidelines."""

    def test_skill_md_under_500_lines(self) -> None:
        with open(SKILL_MD, "r") as f:
            lines = f.readlines()
        assert len(lines) <= 500, (
            f"SKILL.md has {len(lines)} lines, exceeds recommended 500 line limit. "
            "Consider moving content to reference files."
        )

    def test_skill_md_under_5000_tokens_estimate(self) -> None:
        """Rough token estimate: ~4 chars per token."""
        with open(SKILL_MD, "r") as f:
            content = f.read()
        estimated_tokens = len(content) / 4
        assert estimated_tokens <= 5000, (
            f"SKILL.md estimated at ~{int(estimated_tokens)} tokens, exceeds recommended 5000. "
            "Consider moving content to reference files."
        )


class TestCodeExamples:
    """Verify code examples in SKILL.md use the correct syntax."""

    @pytest.fixture(scope="class")
    def skill_body(self):
        content = read_skill_md()
        _, body = parse_frontmatter(content)
        return body

    def test_python_examples_use_computer_action(self, skill_body) -> None:
        """Code examples should use computer(action="bash", ...) syntax for hermes-agent."""
        # Find all python code blocks
        python_blocks = re.findall(r"```python\n(.*?)```", skill_body, re.DOTALL)
        for block in python_blocks:
            if "forge" in block and "def " not in block:
                # Non-function blocks that reference forge should use computer(action="bash", ...)
                # or subprocess patterns — both are valid
                assert (
                    'computer(action="bash"' in block
                    or "subprocess" in block
                ), (
                    f"Python code block references forge but doesn't use "
                    f"computer(action='bash', ...) or subprocess pattern:\n{block[:200]}"
                )

    def test_forge_commit_examples(self, skill_body) -> None:
        """Verify forge commit examples use documented flags."""
        if "forge commit" in skill_body:
            assert "--preview" in skill_body, (
                "forge commit is mentioned but --preview flag is not documented"
            )
