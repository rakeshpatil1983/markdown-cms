"""Component and data source registry."""

import importlib
from collections.abc import Callable
from typing import Any, Optional

from .database import get_db_context
from .models import DataSource, User


class DataSourceRegistry:
    """Registry for data source functions."""

    def __init__(self):
        """Initialize registry."""
        self._sources: dict[str, Callable] = {}
        self._load_from_database()

    def _load_from_database(self):
        """Load data sources from database."""
        try:
            with get_db_context() as db:
                sources = db.query(DataSource).filter_by(is_active=True).all()

                for source in sources:
                    try:
                        # Import function from path
                        module_path, function_name = source.function_path.rsplit(".", 1)
                        module = importlib.import_module(module_path)
                        func = getattr(module, function_name)

                        # Register function
                        self._sources[source.name] = func
                    except Exception as e:
                        print(
                            f"Warning: Failed to load data source '{source.name}': {e}"
                        )
        except Exception:
            # Database might not be initialized yet
            pass

    def register(self, name: str, func: Callable):
        """
        Register a data source function.

        Args:
            name: Name of the data source
            func: Function that returns list of dictionaries
        """
        self._sources[name] = func

    def get(self, name: str) -> Optional[Callable]:
        """
        Get a data source function by name.

        Args:
            name: Name of the data source

        Returns:
            Function if found, None otherwise
        """
        return self._sources.get(name)

    def call(
        self, name: str, user: Optional[User] = None, **kwargs
    ) -> list[dict[str, Any]]:
        """
        Call a data source function.

        Args:
            name: Name of the data source
            user: Current user (for permission checks)
            **kwargs: Additional arguments to pass to function

        Returns:
            List of dictionaries from data source
        """
        func = self.get(name)

        if not func:
            raise ValueError(f"Data source '{name}' not found")

        # Check permissions
        if not self.check_permission(name, user):
            raise PermissionError(f"User does not have permission to access '{name}'")

        # Call function
        try:
            result = func(**kwargs)
            return result if result else []
        except Exception as e:
            raise RuntimeError(f"Error calling data source '{name}': {e}")

    def check_permission(self, name: str, user: Optional[User] = None) -> bool:
        """
        Check if user has permission to access data source.

        Args:
            name: Name of the data source
            user: Current user

        Returns:
            True if user has permission, False otherwise
        """
        try:
            with get_db_context() as db:
                source = (
                    db.query(DataSource).filter_by(name=name, is_active=True).first()
                )

                if not source:
                    return False

                # Check if auth required
                if not source.requires_auth:
                    return True

                # Check if user authenticated
                if not user:
                    return False

                # Check allowed roles
                allowed_roles = source.get_allowed_roles()

                if not allowed_roles:
                    # No specific roles required, any authenticated user can access
                    return True

                # Check if user has one of the allowed roles
                return user.role.value in allowed_roles
        except Exception:
            # If database check fails, deny access
            return False

    def list_all(self) -> list[str]:
        """List all registered data source names."""
        return list(self._sources.keys())

    def reload(self):
        """Reload data sources from database."""
        self._sources.clear()
        self._load_from_database()


# Global registry instance
_registry = None


def get_registry() -> DataSourceRegistry:
    """Get or create global data source registry."""
    global _registry

    if _registry is None:
        _registry = DataSourceRegistry()

    return _registry


def register_data_source(name: str, func: Callable):
    """
    Convenience function to register a data source.

    Usage:
        @register_data_source("my_data")
        def my_data_function(**kwargs):
            return [{"id": 1, "name": "Item 1"}]
    """
    registry = get_registry()
    registry.register(name, func)
    return func
