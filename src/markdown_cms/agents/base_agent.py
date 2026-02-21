"""Base agent class for all development agents."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class AgentTask:
    """Represents a task for an agent."""

    id: str
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed
    assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None

    def start(self):
        """Mark task as started."""
        self.status = "in_progress"
        self.started_at = datetime.utcnow()

    def complete(self, result: Optional[dict[str, Any]] = None):
        """Mark task as completed."""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        self.result = result

    def fail(self, error: str):
        """Mark task as failed."""
        self.status = "failed"
        self.completed_at = datetime.utcnow()
        self.error = error


class BaseAgent:
    """Base class for all agents."""

    def __init__(self, name: str, role: str, project_root: Optional[Path] = None):
        """
        Initialize agent.

        Args:
            name: Agent name
            role: Agent role/responsibility
            project_root: Project root directory (defaults to current directory)
        """
        self.name = name
        self.role = role
        self.project_root = project_root or Path.cwd()
        self.tasks: list[AgentTask] = []
        self.logs: list[str] = []

    def log(self, message: str, level: str = "INFO"):
        """
        Log a message.

        Args:
            message: Log message
            level: Log level (INFO, WARNING, ERROR)
        """
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{self.name}] [{level}] {message}"
        self.logs.append(log_entry)
        print(log_entry)

    def add_task(self, task: AgentTask):
        """Add a task to the agent's task list."""
        task.assigned_to = self.name
        self.tasks.append(task)
        self.log(f"Task added: {task.description}")

    def get_task(self, task_id: str) -> Optional[AgentTask]:
        """Get a task by ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_pending_tasks(self) -> list[AgentTask]:
        """Get all pending tasks."""
        return [t for t in self.tasks if t.status == "pending"]

    def get_completed_tasks(self) -> list[AgentTask]:
        """Get all completed tasks."""
        return [t for t in self.tasks if t.status == "completed"]

    def get_failed_tasks(self) -> list[AgentTask]:
        """Get all failed tasks."""
        return [t for t in self.tasks if t.status == "failed"]

    def get_stats(self) -> dict[str, int]:
        """Get task statistics."""
        return {
            "total": len(self.tasks),
            "pending": len([t for t in self.tasks if t.status == "pending"]),
            "in_progress": len([t for t in self.tasks if t.status == "in_progress"]),
            "completed": len([t for t in self.tasks if t.status == "completed"]),
            "failed": len([t for t in self.tasks if t.status == "failed"]),
        }

    def read_file(self, path: str) -> str:
        """
        Read a file from the project.

        Args:
            path: Relative path to file from project root

        Returns:
            File contents
        """
        file_path = self.project_root / path
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        return file_path.read_text(encoding="utf-8")

    def write_file(self, path: str, content: str):
        """
        Write content to a file.

        Args:
            path: Relative path to file from project root
            content: Content to write
        """
        file_path = self.project_root / path

        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_path.write_text(content, encoding="utf-8")
        self.log(f"File written: {path}")

    def file_exists(self, path: str) -> bool:
        """Check if a file exists."""
        file_path = self.project_root / path
        return file_path.exists()

    def run(self):
        """Run the agent - must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement run()")

    def __repr__(self):
        stats = self.get_stats()
        return f"<{self.__class__.__name__} name={self.name} tasks={stats['total']} completed={stats['completed']}>"
