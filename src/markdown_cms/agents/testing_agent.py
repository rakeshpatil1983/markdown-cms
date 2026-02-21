"""Testing Agent - Validates implementations and writes tests."""

import subprocess
from pathlib import Path
from typing import Any, Optional

from .base_agent import AgentTask, BaseAgent


class TestingAgent(BaseAgent):
    """
    Testing Agent - The QA Engineer

    Responsibilities:
    - Validate implementations against design spec
    - Write pytest test cases
    - Run tests and report results
    - Check code quality
    - Ensure spec compliance
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Testing Agent."""
        super().__init__(
            name="TestingAgent", role="QA Engineer", project_root=project_root
        )
        self.test_results = []

    def discover_tests(self) -> list[str]:
        """
        Discover all test files in the project.

        Returns:
            List of test file paths
        """
        self.log("Discovering tests...")

        test_dir = self.project_root / "tests"
        if not test_dir.exists():
            self.log("Tests directory not found", "WARNING")
            return []

        test_files = list(test_dir.glob("test_*.py"))
        self.log(f"Found {len(test_files)} test files")

        return [str(f.relative_to(self.project_root)) for f in test_files]

    def run_tests(self, test_path: Optional[str] = None) -> dict[str, Any]:
        """
        Run tests using pytest.

        Args:
            test_path: Specific test file/directory to run (None = all tests)

        Returns:
            Test results
        """
        self.log("Running tests...")

        try:
            # Run pytest
            cmd = ["pytest", "-v", "--tb=short"]
            if test_path:
                cmd.append(test_path)

            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            test_result = {
                "status": "passed" if result.returncode == 0 else "failed",
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

            # Parse pytest output for stats
            output = result.stdout + result.stderr
            if "passed" in output:
                # Extract test counts
                import re

                match = re.search(r"(\d+) passed", output)
                if match:
                    test_result["passed_count"] = int(match.group(1))

                match = re.search(r"(\d+) failed", output)
                if match:
                    test_result["failed_count"] = int(match.group(1))

            self.test_results.append(test_result)

            if test_result["status"] == "passed":
                self.log(
                    f"Tests passed: {test_result.get('passed_count', 'unknown')} tests"
                )
            else:
                self.log(
                    f"Tests failed: {test_result.get('failed_count', 'unknown')} failures",
                    "ERROR",
                )

            return test_result

        except subprocess.TimeoutExpired:
            self.log("Tests timed out after 5 minutes", "ERROR")
            return {
                "status": "timeout",
                "error": "Tests took longer than 5 minutes",
            }
        except Exception as e:
            self.log(f"Error running tests: {e}", "ERROR")
            return {
                "status": "error",
                "error": str(e),
            }

    def validate_implementation(self, feature: str) -> dict[str, Any]:
        """
        Validate that a feature is correctly implemented.

        Args:
            feature: Feature name to validate

        Returns:
            Validation results
        """
        self.log(f"Validating implementation: {feature}")

        validation = {
            "feature": feature,
            "checks": [],
            "status": "unknown",
        }

        # Check 1: Files exist
        if "database" in feature.lower():
            checks = [
                self.file_exists("src/markdown_cms/core/models.py"),
                self.file_exists("src/markdown_cms/core/database.py"),
            ]
            validation["checks"].append(
                {
                    "name": "Database files exist",
                    "passed": all(checks),
                }
            )

        elif "auth" in feature.lower():
            checks = [
                self.file_exists("src/markdown_cms/core/auth.py"),
                self.file_exists("src/markdown_cms/core/auth_routes.py"),
            ]
            validation["checks"].append(
                {
                    "name": "Auth files exist",
                    "passed": all(checks),
                }
            )

        elif "table" in feature.lower():
            checks = [
                self.file_exists("src/markdown_cms/components/table.py"),
            ]
            validation["checks"].append(
                {
                    "name": "Table component exists",
                    "passed": all(checks),
                }
            )

        # Check 2: Tests exist
        test_file = f"tests/test_{feature.lower().replace(' ', '_')}.py"
        has_tests = self.file_exists(test_file)
        validation["checks"].append(
            {
                "name": "Tests exist",
                "passed": has_tests,
            }
        )

        # Overall status
        all_passed = all(check["passed"] for check in validation["checks"])
        validation["status"] = "passed" if all_passed else "failed"

        return validation

    def generate_test_template(self, module_path: str) -> str:
        """
        Generate a pytest test template for a module.

        Args:
            module_path: Path to module to test (e.g., "core/models.py")

        Returns:
            Test template code
        """
        module_name = Path(module_path).stem
        test_code = f'''"""Tests for {module_path}."""

import pytest
from markdown_cms.{module_path.replace('/', '.').replace('.py', '')} import *


class Test{module_name.title()}:
    """Test suite for {module_name}."""

    def test_import(self):
        """Test that module can be imported."""
        # This test validates that the module imports without errors
        assert True

    def test_placeholder(self):
        """Placeholder test - replace with actual tests."""
        # TODO: Add real test cases
        pytest.skip("Test not implemented yet")


# Add more test classes and functions as needed
'''
        return test_code

    def create_test_file(self, module_path: str) -> str:
        """
        Create a test file for a module.

        Args:
            module_path: Path to module to test

        Returns:
            Path to created test file
        """
        module_name = Path(module_path).stem
        test_file = f"tests/test_{module_name}.py"

        if self.file_exists(test_file):
            self.log(f"Test file already exists: {test_file}", "WARNING")
            return test_file

        # Generate test template
        test_code = self.generate_test_template(module_path)

        # Write test file
        self.write_file(test_file, test_code)
        self.log(f"Created test file: {test_file}")

        return test_file

    def check_code_quality(self, file_path: str) -> dict[str, Any]:
        """
        Check code quality using ruff.

        Args:
            file_path: Path to file to check

        Returns:
            Code quality results
        """
        self.log(f"Checking code quality: {file_path}")

        try:
            result = subprocess.run(
                ["ruff", "check", file_path],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=30,
            )

            quality = {
                "file": file_path,
                "status": "passed" if result.returncode == 0 else "failed",
                "issues": [],
            }

            if result.stdout:
                quality["issues"] = result.stdout.strip().split("\n")

            return quality

        except Exception as e:
            self.log(f"Error checking code quality: {e}", "ERROR")
            return {
                "file": file_path,
                "status": "error",
                "error": str(e),
            }

    def run(self):
        """Run the testing agent."""
        self.log("Starting Testing Agent...")

        # Discover tests
        test_files = self.discover_tests()

        if not test_files:
            self.log("No tests found - creating test templates", "WARNING")
            # Would create test templates here
        else:
            self.log(f"Found {len(test_files)} test files")

        # Run all tests
        test_result = self.run_tests()

        # Create agent task for test run
        task = AgentTask(
            id="test_run_1",
            description="Run all tests",
        )
        task.start()

        if test_result["status"] == "passed":
            task.complete(test_result)
        else:
            task.fail(f"Tests failed: {test_result.get('stderr', 'Unknown error')}")

        self.add_task(task)

        return self.get_stats()
