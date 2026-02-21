"""Implementation Agent - Implements features from design specification."""

import re
from pathlib import Path
from typing import Any, Optional

from .base_agent import AgentTask, BaseAgent


class ImplementationAgent(BaseAgent):
    """
    Implementation Agent - The Developer

    Responsibilities:
    - Read design specification and action plan
    - Implement missing features
    - Write code following project conventions
    - Update documentation
    - Follow Python best practices
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Implementation Agent."""
        super().__init__(
            name="ImplementationAgent",
            role="Software Developer",
            project_root=project_root,
        )
        self.spec_file = "design-specification.md"
        self.action_plan_file = "action-plan.md"
        self.current_phase = None

    def load_specifications(self) -> dict[str, str]:
        """
        Load design specification and action plan.

        Returns:
            Dictionary with spec and action plan contents
        """
        self.log("Loading specifications...")

        specs = {}

        try:
            specs["design_spec"] = self.read_file(self.spec_file)
            self.log(f"Loaded design specification: {self.spec_file}")
        except FileNotFoundError:
            self.log(f"Design specification not found: {self.spec_file}", "WARNING")
            specs["design_spec"] = ""

        try:
            specs["action_plan"] = self.read_file(self.action_plan_file)
            self.log(f"Loaded action plan: {self.action_plan_file}")
        except FileNotFoundError:
            self.log(f"Action plan not found: {self.action_plan_file}", "WARNING")
            specs["action_plan"] = ""

        return specs

    def parse_action_plan(self, action_plan: str) -> dict[str, list[str]]:
        """
        Parse action plan to extract phases and tasks.

        Args:
            action_plan: Action plan markdown content

        Returns:
            Dictionary mapping phase names to lists of tasks
        """
        phases = {}
        current_phase = None
        current_tasks = []

        for line in action_plan.split("\n"):
            # Phase header: ## Phase N: Name
            phase_match = re.match(r"^##\s+Phase\s+\d+[:\s]+(.+?)(?:\s+\(Week|$)", line)
            if phase_match:
                # Save previous phase
                if current_phase and current_tasks:
                    phases[current_phase] = current_tasks

                # Start new phase
                current_phase = phase_match.group(1).strip()
                current_tasks = []
                continue

            # Task line: - [ ] Task description
            task_match = re.match(r"^-\s+\[\s*[x ]\s*\]\s+(.+)", line)
            if task_match and current_phase:
                task = task_match.group(1).strip()
                current_tasks.append(task)

        # Save last phase
        if current_phase and current_tasks:
            phases[current_phase] = current_tasks

        return phases

    def identify_pending_tasks(self) -> list[dict[str, Any]]:
        """
        Identify tasks that are not yet implemented.

        Returns:
            List of pending tasks with metadata
        """
        self.log("Identifying pending tasks...")

        specs = self.load_specifications()
        action_plan = specs.get("action_plan", "")

        if not action_plan:
            self.log("No action plan found", "WARNING")
            return []

        phases = self.parse_action_plan(action_plan)
        pending = []

        for phase_name, tasks in phases.items():
            for task in tasks:
                # Simple heuristic: check if related files exist
                # This is simplified - in reality, would use Claude Code agents
                pending.append(
                    {
                        "phase": phase_name,
                        "description": task,
                        "priority": self._estimate_priority(phase_name, task),
                    }
                )

        self.log(f"Found {len(pending)} pending tasks across {len(phases)} phases")
        return pending

    def _estimate_priority(self, phase: str, task: str) -> int:
        """
        Estimate task priority (1-5, 1 is highest).

        Args:
            phase: Phase name
            task: Task description

        Returns:
            Priority score
        """
        # Foundation tasks are highest priority
        if "Phase 1" in phase or "Foundation" in phase:
            return 1

        # Core features are high priority
        if any(
            keyword in task.lower()
            for keyword in ["database", "auth", "user", "session"]
        ):
            return 2

        # Advanced features are medium priority
        if any(keyword in task.lower() for keyword in ["admin", "crud", "form"]):
            return 3

        # Polish features are lower priority
        if any(
            keyword in task.lower() for keyword in ["cache", "performance", "optimize"]
        ):
            return 4

        # Documentation is lowest priority
        if any(keyword in task.lower() for keyword in ["doc", "test", "example"]):
            return 5

        return 3  # Default medium priority

    def generate_implementation_plan(self, task: str) -> dict[str, Any]:
        """
        Generate implementation plan for a task.

        Args:
            task: Task description

        Returns:
            Implementation plan with steps
        """
        self.log(f"Generating implementation plan for: {task}")

        # This is a simplified version - in production, would use Claude Code
        # to analyze the task and generate detailed implementation steps

        plan = {
            "task": task,
            "steps": [],
            "files_to_create": [],
            "files_to_modify": [],
            "dependencies": [],
        }

        # Simple keyword-based planning
        if "table component" in task.lower():
            plan["steps"] = [
                "Parse :::table syntax from markdown",
                "Query data source registry",
                "Render HTML table with Bootstrap",
                "Add pagination support",
                "Add sorting support",
            ]
            plan["files_to_create"] = ["src/markdown_cms/components/table.py"]
            plan["files_to_modify"] = ["src/markdown_cms/core/pure_text_parser.py"]

        elif "form" in task.lower() and "processing" in task.lower():
            plan["steps"] = [
                "Create form handler base class",
                "Implement validation framework",
                "Add CSRF protection",
                "Create success/error handlers",
                "Add form submission routes",
            ]
            plan["files_to_create"] = ["src/markdown_cms/core/forms.py"]
            plan["files_to_modify"] = ["src/markdown_cms/core/router.py"]

        elif "admin" in task.lower():
            plan["steps"] = [
                "Create admin layout template",
                "Add user management pages",
                "Add content management pages",
                "Implement CRUD operations",
                "Add role-based access control",
            ]
            plan["files_to_create"] = [
                "src/markdown_cms/core/admin_routes.py",
                "src/markdown_cms/core/crud.py",
            ]

        return plan

    def implement_task(self, task_description: str) -> dict[str, Any]:
        """
        Implement a specific task.

        Args:
            task_description: Description of task to implement

        Returns:
            Implementation result
        """
        self.log(f"Implementing task: {task_description}")

        # Generate implementation plan
        plan = self.generate_implementation_plan(task_description)

        result = {
            "task": task_description,
            "status": "success",
            "plan": plan,
            "files_created": [],
            "files_modified": [],
            "message": f"Task '{task_description}' implementation planned",
        }

        # In a real implementation, this would:
        # 1. Use Claude Code to analyze the task
        # 2. Read existing code for context
        # 3. Generate new code following project conventions
        # 4. Write files
        # 5. Run tests
        # 6. Report results

        self.log(f"Implementation plan generated with {len(plan['steps'])} steps")

        return result

    def run(self):
        """Run the implementation agent."""
        self.log("Starting Implementation Agent...")

        # Load specifications
        specs = self.load_specifications()

        # Identify pending tasks
        pending_tasks = self.identify_pending_tasks()

        if not pending_tasks:
            self.log("No pending tasks found!")
            return

        # Sort by priority
        pending_tasks.sort(key=lambda t: t["priority"])

        # Log status
        self.log(f"Found {len(pending_tasks)} pending tasks")
        for i, task in enumerate(pending_tasks[:5], 1):
            self.log(
                f"  {i}. [{task['phase']}] {task['description']} (priority: {task['priority']})"
            )

        # Create agent tasks
        for i, pending in enumerate(pending_tasks[:10], 1):  # Limit to top 10
            task = AgentTask(
                id=f"impl_{i}",
                description=pending["description"],
            )
            self.add_task(task)

        self.log(f"Created {len(self.tasks)} implementation tasks")

        return self.get_stats()
