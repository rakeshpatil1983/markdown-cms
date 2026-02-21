"""Configuration management for Markdown CMS."""

import os
from pathlib import Path


class Config:
    """Application configuration."""

    def __init__(self):
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///database.db")
        self.theme = os.getenv("THEME", "default")

        # Project root is current working directory
        self.project_path = Path.cwd()

        # New Django-like structure
        self.templates_path = self.project_path / "templates"
        self.static_path = self.project_path / "static"
        self.pages_path = self.project_path / "pages"
        self.apps_path = self.project_path / "apps"
        self.plugins_path = self.project_path / "plugins"
        self.themes_path = self.project_path / "themes"

        # Load site configuration
        self._site_config = None

    @property
    def theme_path(self) -> Path:
        """Get the current theme directory path."""
        return self.themes_path / self.theme

    def get_site_config(self) -> dict:
        """Load site configuration from _site.md or return defaults.

        Site config file (_site.md) supports these options:

        ```
        # Site Configuration
        title: My Website
        description: A markdown-powered website

        # Sidebar Settings
        sidebar_mode: subjects    # Options: tree, subjects, flat
        sidebar_title: Subjects   # Title shown at root level

        # Navigation Settings
        show_breadcrumbs: true
        show_toc: true
        ```

        Sidebar modes:
        - tree: Show full expandable tree (default)
        - subjects: Show only top-level categories at root, filter when inside
        - flat: Show all pages in a flat list
        """
        if self._site_config is not None:
            return self._site_config

        # Default site configuration
        self._site_config = {
            "title": "Markdown CMS",
            "description": "",
            "sidebar_mode": "tree",  # tree, subjects, flat
            "sidebar_title": "Navigation",
            "show_breadcrumbs": "true",
            "show_toc": "true",
        }

        site_config_file = self.project_path / "_site.md"
        if site_config_file.exists():
            content = site_config_file.read_text(encoding="utf-8")
            # Parse simple key: value format (skip comments and empty lines)
            for line in content.split("\n"):
                line = line.strip()
                if ":" in line and not line.startswith("#"):
                    key, value = line.split(":", 1)
                    key = key.strip().lower().replace(" ", "_")
                    value = value.strip()
                    self._site_config[key] = value

        return self._site_config

    def get_theme_config(self) -> dict:
        """Load theme configuration from _theme.md or return defaults."""
        theme_config_file = self.theme_path / "_theme.md"
        config = {
            "name": self.theme,
            "framework": "none",  # none, bootstrap, bulma, materialize, tailwind
            "framework_css": "",
            "framework_js": "",
            "custom_css": "styles.css",
        }

        if theme_config_file.exists():
            content = theme_config_file.read_text(encoding="utf-8")
            # Parse simple key: value format
            for line in content.split("\n"):
                line = line.strip()
                if ":" in line and not line.startswith("#"):
                    key, value = line.split(":", 1)
                    config[key.strip().lower().replace(" ", "_")] = value.strip()

        return config

    @property
    def database_path(self) -> Path:
        """Get the database file path."""
        if self.database_url.startswith("sqlite:///"):
            return Path(self.database_url[10:])
        return Path("database.db")


# Global configuration instance
_config: Config | None = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def set_config(config: Config) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config
