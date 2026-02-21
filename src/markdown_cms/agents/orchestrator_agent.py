"""Orchestrator Agent - Coordinates all development agents."""

from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .base_agent import BaseAgent
from .implementation_agent import ImplementationAgent
from .testing_agent import TestingAgent


class OrchestratorAgent(BaseAgent):
    """
    Orchestrator Agent - The Project Manager

    Responsibilities:
    - Coordinate Implementation and Testing agents
    - Track progress against action plan
    - Ensure spec compliance
    - Report completion status
    - Manage agent workflows
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Orchestrator Agent."""
        super().__init__(
            name="OrchestratorAgent", role="Project Manager", project_root=project_root
        )
        self.implementation_agent = ImplementationAgent(project_root)
        self.testing_agent = TestingAgent(project_root)
        self.workflow_results = []

    def get_project_status(self) -> dict[str, Any]:
        """
        Get overall project status.

        Returns:
            Project status summary
        """
        self.log("Assessing project status...")

        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "implementation": self.implementation_agent.get_stats(),
            "testing": self.testing_agent.get_stats(),
            "overall_progress": 0.0,
        }

        # Calculate overall progress
        impl_stats = status["implementation"]
        total_tasks = impl_stats["total"]

        if total_tasks > 0:
            completed = impl_stats["completed"]
            status["overall_progress"] = (completed / total_tasks) * 100

        return status

    def run_implementation_cycle(self) -> dict[str, Any]:
        """
        Run an implementation cycle.

        Workflow:
        1. Implementation agent identifies pending tasks
        2. Implementation agent implements top priority task
        3. Testing agent validates implementation
        4. Testing agent runs tests
        5. Report results

        Returns:
            Cycle results
        """
        self.log("Starting implementation cycle...")

        cycle_result = {
            "status": "in_progress",
            "phases": [],
        }

        # Phase 1: Identify tasks
        self.log("Phase 1: Identifying pending tasks...")
        impl_stats = self.implementation_agent.run()
        cycle_result["phases"].append(
            {
                "name": "Task Identification",
                "status": "completed",
                "result": impl_stats,
            }
        )

        # Get top priority pending task
        pending_tasks = self.implementation_agent.get_pending_tasks()

        if not pending_tasks:
            self.log("No pending tasks found!")
            cycle_result["status"] = "completed"
            return cycle_result

        top_task = pending_tasks[0]
        self.log(f"Selected task: {top_task.description}")

        # Phase 2: Implement task
        self.log("Phase 2: Implementing task...")
        top_task.start()

        try:
            impl_result = self.implementation_agent.implement_task(top_task.description)
            top_task.complete(impl_result)

            cycle_result["phases"].append(
                {
                    "name": "Implementation",
                    "status": "completed",
                    "result": impl_result,
                }
            )
        except Exception as e:
            self.log(f"Implementation failed: {e}", "ERROR")
            top_task.fail(str(e))

            cycle_result["phases"].append(
                {
                    "name": "Implementation",
                    "status": "failed",
                    "error": str(e),
                }
            )
            cycle_result["status"] = "failed"
            return cycle_result

        # Phase 3: Validate implementation
        self.log("Phase 3: Validating implementation...")
        validation = self.testing_agent.validate_implementation(top_task.description)

        cycle_result["phases"].append(
            {
                "name": "Validation",
                "status": validation["status"],
                "result": validation,
            }
        )

        # Phase 4: Run tests
        self.log("Phase 4: Running tests...")
        test_result = self.testing_agent.run_tests()

        cycle_result["phases"].append(
            {
                "name": "Testing",
                "status": test_result["status"],
                "result": test_result,
            }
        )

        # Overall cycle status
        if test_result["status"] == "passed" and validation["status"] == "passed":
            cycle_result["status"] = "success"
            self.log("Implementation cycle completed successfully!")
        else:
            cycle_result["status"] = "partial"
            self.log("Implementation cycle completed with issues", "WARNING")

        self.workflow_results.append(cycle_result)

        return cycle_result

    def run_continuous_integration(self, max_cycles: int = 5) -> list[dict[str, Any]]:
        """
        Run continuous integration cycles.

        Args:
            max_cycles: Maximum number of cycles to run

        Returns:
            List of cycle results
        """
        self.log(f"Starting continuous integration ({max_cycles} cycles max)...")

        results = []

        for i in range(max_cycles):
            self.log(f"=== Cycle {i + 1}/{max_cycles} ===")

            cycle_result = self.run_implementation_cycle()
            results.append(cycle_result)

            if cycle_result["status"] == "completed":
                self.log("All tasks completed!")
                break

            if cycle_result["status"] == "failed":
                self.log("Cycle failed - stopping", "ERROR")
                break

        self.log(f"Continuous integration completed: {len(results)} cycles")

        return results

    def generate_report(self) -> str:
        """
        Generate a comprehensive project report.

        Returns:
            Markdown-formatted report
        """
        self.log("Generating project report...")

        status = self.get_project_status()

        report = f"""# Markdown CMS - Development Report

**Generated:** {status['timestamp']}

## Overall Progress

- **Progress:** {status['overall_progress']:.1f}%
- **Implementation Tasks:** {status['implementation']['total']} total
  - Completed: {status['implementation']['completed']}
  - In Progress: {status['implementation']['in_progress']}
  - Pending: {status['implementation']['pending']}
  - Failed: {status['implementation']['failed']}

- **Testing Tasks:** {status['testing']['total']} total
  - Completed: {status['testing']['completed']}
  - Failed: {status['testing']['failed']}

## Implementation Agent Status

{self.implementation_agent.name} ({self.implementation_agent.role})

### Recent Tasks

"""

        # Add recent implementation tasks
        for task in self.implementation_agent.tasks[-5:]:
            status_emoji = {
                "completed": "✅",
                "failed": "❌",
                "in_progress": "🔄",
                "pending": "⏳",
            }.get(task.status, "❓")

            report += f"- {status_emoji} **{task.description}** - {task.status}\n"

        report += f"""

## Testing Agent Status

{self.testing_agent.name} ({self.testing_agent.role})

### Test Results

"""

        # Add test results
        if self.testing_agent.test_results:
            for result in self.testing_agent.test_results[-3:]:
                status_emoji = "✅" if result["status"] == "passed" else "❌"
                passed = result.get("passed_count", 0)
                failed = result.get("failed_count", 0)
                report += f"- {status_emoji} Passed: {passed}, Failed: {failed}\n"
        else:
            report += "- No test results yet\n"

        report += f"""

## Workflow Results

Total workflow cycles completed: {len(self.workflow_results)}

"""

        # Add workflow results
        for i, result in enumerate(self.workflow_results, 1):
            status_emoji = {
                "success": "✅",
                "partial": "⚠️",
                "failed": "❌",
                "completed": "✅",
            }.get(result["status"], "❓")

            report += f"### Cycle {i}\n\n"
            report += f"Status: {status_emoji} {result['status']}\n\n"

            for phase in result["phases"]:
                phase_emoji = (
                    "✅" if phase["status"] in ["completed", "passed"] else "❌"
                )
                report += f"- {phase_emoji} {phase['name']}: {phase['status']}\n"

            report += "\n"

        report += """
---

*Report generated by OrchestratorAgent*
"""

        return report

    def run(self):
        """Run the orchestrator agent."""
        self.log("Starting Orchestrator Agent...")

        # Get initial status
        status = self.get_project_status()
        self.log(f"Project progress: {status['overall_progress']:.1f}%")

        # Run a single implementation cycle
        cycle_result = self.run_implementation_cycle()

        # Generate report
        report = self.generate_report()

        # Save report
        self.write_file("dev_report.md", report)

        return {
            "status": status,
            "cycle_result": cycle_result,
            "report_path": "dev_report.md",
        }
