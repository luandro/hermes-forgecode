"""Tests that forge CLI flags and subcommands match what SKILL.md and references document.

This catches drift between the skill documentation and the actual CLI.
If forge adds/removes/renames flags or subcommands, these tests will flag it.
"""

import subprocess

import pytest


def run_forge(*args: str, timeout: int = 15) -> subprocess.CompletedProcess:
    """Helper to run a forge command and return the result."""
    return subprocess.run(
        ["forge", *args], capture_output=True, text=True, timeout=timeout
    )


class TestGlobalFlags:
    """Verify all global flags documented in cli-reference.md exist."""

    DOCUMENTED_FLAGS = [
        "-p",           # --prompt (short)
        "--prompt",     # --prompt (long)
        "-e",           # --event (short)
        "--event",      # --event (long)
        "--conversation",
        "--conversation-id",
        "--agent",
        "-C",           # --directory (short)
        "--directory",  # --directory (long)
        "--sandbox",
        "--verbose",
        "--version",
        "--help",
    ]

    def test_help_lists_all_documented_flags(self) -> None:
        """Parse forge --help and verify every documented flag appears."""
        result = run_forge("--help")
        assert result.returncode == 0
        help_text = result.stdout

        missing = []
        for flag in self.DOCUMENTED_FLAGS:
            if flag not in help_text:
                missing.append(flag)

        assert not missing, (
            f"Flags documented in cli-reference.md but missing from 'forge --help': {missing}"
        )

    def test_prompt_flag_accepts_argument(self) -> None:
        """Verify -p/--prompt is a valid flag that accepts an argument.

        We test with a trivial prompt; the key assertion is that forge
        doesn't reject the flag itself. The prompt may fail for auth
        or network reasons, which is fine.
        """
        result = run_forge("-p", "echo hello", timeout=30)
        # We don't assert returncode == 0 because the prompt might fail
        # for auth/network reasons. We just check the flag is recognized.
        assert "unexpected argument" not in result.stderr.lower()
        assert "unrecognized" not in result.stderr.lower()
        assert "unknown option" not in result.stderr.lower()

    def test_directory_flag(self) -> None:
        """Verify -C flag is recognized."""
        result = run_forge("-C", "/tmp", "-p", "echo test", timeout=30)
        assert "unexpected argument" not in result.stderr.lower()
        assert "unrecognized" not in result.stderr.lower()

    def test_agent_flag(self) -> None:
        """Verify --agent flag is recognized."""
        result = run_forge("--agent", "sage", "-p", "echo test", timeout=30)
        assert "unexpected argument" not in result.stderr.lower()

    def test_sandbox_flag(self) -> None:
        """Verify --sandbox flag is recognized."""
        # Use a temp directory with a git repo for sandbox test
        import tempfile, os
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, timeout=10)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmpdir, capture_output=True, timeout=5)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=tmpdir, capture_output=True, timeout=5)
            # Create an initial commit so worktree can be created
            filepath = os.path.join(tmpdir, "README.md")
            with open(filepath, "w") as f:
                f.write("# test\n")
            subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True, timeout=5)
            subprocess.run(["git", "commit", "-m", "init"], cwd=tmpdir, capture_output=True, timeout=10)

            result = run_forge("-C", tmpdir, "--sandbox", "test-sandbox", "-p", "echo test", timeout=30)
            assert "unexpected argument" not in result.stderr.lower()


class TestSubcommands:
    """Verify all subcommands documented in cli-reference.md exist."""

    DOCUMENTED_SUBCOMMANDS = [
        "conversation",
        "commit",
        "list",
        "provider",
        "mcp",
        "workspace",
        "info",
        "doctor",
        "update",
        "setup",
        "cmd",
        "data",
        "suggest",
        "banner",
    ]

    def test_help_lists_all_documented_subcommands(self) -> None:
        """Parse forge --help and verify every documented subcommand appears."""
        result = run_forge("--help")
        assert result.returncode == 0
        help_text = result.stdout.lower()

        missing = []
        for sub in self.DOCUMENTED_SUBCOMMANDS:
            if sub not in help_text:
                missing.append(sub)

        assert not missing, (
            f"Subcommands documented in cli-reference.md but missing from 'forge --help': {missing}"
        )


class TestConversationSubcommands:
    """Verify conversation subcommands documented in cli-reference.md."""

    DOCUMENTED_CONV_SUBS = [
        "list", "resume", "new", "dump", "compact",
        "retry", "clone", "rename", "delete", "info", "stats", "show",
    ]

    def test_conversation_help_lists_all(self) -> None:
        result = run_forge("conversation", "--help")
        assert result.returncode == 0
        help_text = result.stdout.lower()

        missing = []
        for sub in self.DOCUMENTED_CONV_SUBS:
            if sub not in help_text:
                missing.append(sub)

        assert not missing, (
            f"Conversation subcommands missing from 'forge conversation --help': {missing}"
        )

    def test_conversation_list_runs(self) -> None:
        result = run_forge("conversation", "list")
        assert result.returncode == 0


class TestListSubcommands:
    """Verify 'forge list' subcommands documented in cli-reference.md."""

    DOCUMENTED_LIST_SUBS = ["agent", "model", "tool", "skill", "provider"]

    def test_list_help_lists_all(self) -> None:
        result = run_forge("list", "--help")
        assert result.returncode == 0
        help_text = result.stdout.lower()

        missing = []
        for sub in self.DOCUMENTED_LIST_SUBS:
            if sub not in help_text:
                missing.append(sub)

        assert not missing, (
            f"List subcommands missing from 'forge list --help': {missing}"
        )

    def test_list_agent_runs(self) -> None:
        result = run_forge("list", "agent")
        assert result.returncode == 0

    def test_list_model_runs(self) -> None:
        result = run_forge("list", "model")
        assert result.returncode == 0

    def test_list_provider_runs(self) -> None:
        result = run_forge("list", "provider")
        assert result.returncode == 0

    def test_list_tool_runs(self) -> None:
        result = run_forge("list", "tool", "forge")
        assert result.returncode == 0

    def test_list_skill_runs(self) -> None:
        result = run_forge("list", "skill")
        assert result.returncode == 0


class TestMcpSubcommands:
    """Verify MCP subcommands documented in cli-reference.md."""

    DOCUMENTED_MCP_SUBS = ["list", "import", "show", "remove", "reload"]

    def test_mcp_help_lists_all(self) -> None:
        result = run_forge("mcp", "--help")
        assert result.returncode == 0
        help_text = result.stdout.lower()

        missing = []
        for sub in self.DOCUMENTED_MCP_SUBS:
            if sub not in help_text:
                missing.append(sub)

        assert not missing, (
            f"MCP subcommands missing from 'forge mcp --help': {missing}"
        )

    def test_mcp_list_runs(self) -> None:
        result = run_forge("mcp", "list")
        assert result.returncode == 0


class TestWorkspaceSubcommands:
    """Verify workspace subcommands documented in cli-reference.md."""

    DOCUMENTED_WORKSPACE_SUBS = ["sync", "init", "status", "query"]

    def test_workspace_help_lists_all(self) -> None:
        result = run_forge("workspace", "--help")
        assert result.returncode == 0
        help_text = result.stdout.lower()

        missing = []
        for sub in self.DOCUMENTED_WORKSPACE_SUBS:
            if sub not in help_text:
                missing.append(sub)

        assert not missing, (
            f"Workspace subcommands missing from 'forge workspace --help': {missing}"
        )


class TestProviderSubcommands:
    """Verify provider subcommands documented in cli-reference.md."""

    DOCUMENTED_PROVIDER_SUBS = ["login", "logout", "list"]

    def test_provider_help_lists_all(self) -> None:
        result = run_forge("provider", "--help")
        assert result.returncode == 0
        help_text = result.stdout.lower()

        missing = []
        for sub in self.DOCUMENTED_PROVIDER_SUBS:
            if sub not in help_text:
                missing.append(sub)

        assert not missing, (
            f"Provider subcommands missing from 'forge provider --help': {missing}"
        )


class TestCommitSubcommand:
    """Verify forge commit subcommand."""

    def test_commit_help_runs(self) -> None:
        result = run_forge("commit", "--help")
        assert result.returncode == 0

    def test_commit_preview_flag(self) -> None:
        """Verify --preview flag is documented for forge commit."""
        result = run_forge("commit", "--help")
        assert result.returncode == 0
        assert "--preview" in result.stdout, (
            "'--preview' flag missing from 'forge commit --help'"
        )


class TestPorcelainFlag:
    """Verify --porcelain flag works for documented subcommands."""

    PORCELAIN_COMMANDS = [
        (["list", "agent"], "forge list agent --porcelain"),
        (["list", "model"], "forge list model --porcelain"),
        (["list", "skill"], "forge list skill --porcelain"),
        (["list", "provider"], "forge list provider --porcelain"),
    ]

    @pytest.mark.parametrize("cmd,desc", PORCELAIN_COMMANDS, ids=[d for _, d in PORCELAIN_COMMANDS])
    def test_porcelain_output(self, cmd: list[str], desc: str) -> None:
        result = run_forge(*cmd, "--porcelain")
        assert result.returncode == 0, f"{desc} failed: {result.stderr}"
        # Porcelain output should not contain ANSI escape codes
        assert "\x1b[" not in result.stdout, (
            f"{desc} output contains ANSI escape codes"
        )


class TestBuiltInAgents:
    """Verify the three built-in agents documented in SKILL.md exist."""

    EXPECTED_AGENTS = ["forge", "sage", "muse"]

    def test_all_agents_available(self) -> None:
        result = run_forge("list", "agent")
        assert result.returncode == 0
        output = result.stdout.lower()

        missing = []
        for agent in self.EXPECTED_AGENTS:
            if agent not in output:
                missing.append(agent)

        assert not missing, (
            f"Built-in agents documented in SKILL.md but missing from 'forge list agent': {missing}"
        )

    def test_sage_agent_flag(self) -> None:
        """Verify --agent sage is accepted."""
        result = run_forge("--agent", "sage", "-p", "echo test", timeout=30)
        assert "unknown agent" not in result.stderr.lower()
        assert "invalid value" not in result.stderr.lower()

    def test_muse_agent_flag(self) -> None:
        """Verify --agent muse is accepted."""
        result = run_forge("--agent", "muse", "-p", "echo test", timeout=30)
        assert "unknown agent" not in result.stderr.lower()
        assert "invalid value" not in result.stderr.lower()


class TestZshSubcommands:
    """Verify ZSH subcommands documented in cli-reference.md."""

    DOCUMENTED_ZSH_SUBS = ["setup", "doctor", "plugin", "theme", "rprompt"]

    def test_zsh_help_lists_all(self) -> None:
        result = run_forge("zsh", "--help")
        assert result.returncode == 0
        help_text = result.stdout.lower()

        missing = []
        for sub in self.DOCUMENTED_ZSH_SUBS:
            if sub not in help_text:
                missing.append(sub)

        assert not missing, (
            f"ZSH subcommands missing from 'forge zsh --help': {missing}"
        )


class TestConfigSubcommand:
    """Verify config subcommand exists (not explicitly in SKILL.md but in forge help)."""

    def test_config_help_runs(self) -> None:
        result = run_forge("config", "--help")
        assert result.returncode == 0

    def test_config_list_runs(self) -> None:
        result = run_forge("config", "list")
        assert result.returncode == 0


class TestEnvVars:
    """Verify documented environment variables are respected (basic check)."""

    def test_forge_log_env_var(self) -> None:
        """FORGE_LOG should be accepted without error."""
        import os
        env = os.environ.copy()
        env["FORGE_LOG"] = "forge=debug"
        result = subprocess.run(
            ["forge", "--version"], capture_output=True, text=True, timeout=10,
            env=env,
        )
        assert result.returncode == 0
