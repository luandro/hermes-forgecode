"""Tests for the .skill package build process and contents.

Verifies that:
1. The .skill package can be rebuilt from source
2. The package contains the expected files
3. The package contents match the current source files
"""

import os
import subprocess
import zipfile

import pytest

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_PACKAGE = os.path.join(SKILL_ROOT, "hermes-forgecode.skill")


class TestSkillPackageExists:
    """Verify the .skill package exists and is a valid zip."""

    def test_skill_package_exists(self) -> None:
        assert os.path.isfile(SKILL_PACKAGE), (
            f"hermes-forgecode.skill not found at {SKILL_PACKAGE}. "
            "Run: cd hermes-forgecode && zip -r ./hermes-forgecode.skill SKILL.md references/"
        )

    def test_skill_package_is_valid_zip(self) -> None:
        if not os.path.isfile(SKILL_PACKAGE):
            pytest.skip("hermes-forgecode.skill not built yet")
        assert zipfile.is_zipfile(SKILL_PACKAGE), (
            "hermes-forgecode.skill is not a valid zip file"
        )


class TestSkillPackageContents:
    """Verify the .skill package contains the expected files."""

    EXPECTED_FILES = [
        "SKILL.md",
        "references/cli-reference.md",
        "references/agent-patterns.md",
    ]

    def test_package_contains_all_expected_files(self) -> None:
        if not os.path.isfile(SKILL_PACKAGE):
            pytest.skip("hermes-forgecode.skill not built yet")

        with zipfile.ZipFile(SKILL_PACKAGE, "r") as zf:
            names = zf.namelist()

        missing = []
        for expected in self.EXPECTED_FILES:
            if expected not in names:
                missing.append(expected)

        assert not missing, (
            f"Files missing from hermes-forgecode.skill: {missing}. "
            "Run: cd hermes-forgecode && zip -r ./hermes-forgecode.skill SKILL.md references/"
        )

    def test_no_unexpected_files(self) -> None:
        """Verify the package doesn't contain extraneous files."""
        if not os.path.isfile(SKILL_PACKAGE):
            pytest.skip("hermes-forgecode.skill not built yet")

        with zipfile.ZipFile(SKILL_PACKAGE, "r") as zf:
            names = zf.namelist()

        unexpected = []
        for name in names:
            # Allow the expected files and directory entries
            if name in self.EXPECTED_FILES:
                continue
            if name.endswith("/"):
                continue  # directory entries are fine
            unexpected.append(name)

        assert not unexpected, (
            f"Unexpected files in hermes-forgecode.skill: {unexpected}"
        )


class TestSkillPackageMatchesSource:
    """Verify the .skill package contents match the current source files."""

    def test_skill_md_matches(self) -> None:
        if not os.path.isfile(SKILL_PACKAGE):
            pytest.skip("hermes-forgecode.skill not built yet")

        source_path = os.path.join(SKILL_ROOT, "SKILL.md")
        with open(source_path, "r") as f:
            source_content = f.read()

        with zipfile.ZipFile(SKILL_PACKAGE, "r") as zf:
            pkg_content = zf.read("SKILL.md").decode("utf-8")

        assert source_content == pkg_content, (
            "SKILL.md in the package differs from the source. Rebuild: "
            "cd hermes-forgecode && zip -r ./hermes-forgecode.skill SKILL.md references/"
        )

    def test_cli_reference_matches(self) -> None:
        if not os.path.isfile(SKILL_PACKAGE):
            pytest.skip("hermes-forgecode.skill not built yet")

        source_path = os.path.join(SKILL_ROOT, "references", "cli-reference.md")
        with open(source_path, "r") as f:
            source_content = f.read()

        with zipfile.ZipFile(SKILL_PACKAGE, "r") as zf:
            pkg_content = zf.read("references/cli-reference.md").decode("utf-8")

        assert source_content == pkg_content, (
            "references/cli-reference.md in the package differs from source. Rebuild the package."
        )

    def test_agent_patterns_matches(self) -> None:
        if not os.path.isfile(SKILL_PACKAGE):
            pytest.skip("hermes-forgecode.skill not built yet")

        source_path = os.path.join(SKILL_ROOT, "references", "agent-patterns.md")
        with open(source_path, "r") as f:
            source_content = f.read()

        with zipfile.ZipFile(SKILL_PACKAGE, "r") as zf:
            pkg_content = zf.read("references/agent-patterns.md").decode("utf-8")

        assert source_content == pkg_content, (
            "references/agent-patterns.md in the package differs from source. Rebuild the package."
        )


class TestSkillPackageRebuild:
    """Verify the rebuild command from AGENTS.md works."""

    def test_rebuild_produces_valid_package(self, tmp_path) -> None:
        """Run the documented rebuild command and verify the output."""
        output_file = tmp_path / "hermes-forgecode.skill"

        # The documented rebuild command from AGENTS.md:
        # cd hermes-forgecode && zip -r ../hermes-forgecode.skill SKILL.md references/
        result = subprocess.run(
            ["zip", "-r", str(output_file), "SKILL.md", "references/"],
            cwd=SKILL_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"zip failed: {result.stderr}"
        assert output_file.exists(), "zip did not create the output file"
        assert zipfile.is_zipfile(output_file), "zip output is not a valid zip"

        with zipfile.ZipFile(output_file, "r") as zf:
            names = zf.namelist()
        for expected in TestSkillPackageContents.EXPECTED_FILES:
            assert expected in names, f"Rebuilt package missing {expected}"
