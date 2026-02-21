"""Test the configuration module."""

import os

from markdown_cms.core.config import Config, get_config, set_config


class TestConfig:
    """Test cases for Config class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()

        assert config.debug is False
        assert config.secret_key == "dev-secret-key-change-in-production"
        assert config.database_url == "sqlite:///database.db"
        assert config.theme == "default"

    def test_config_from_env(self):
        """Test configuration from environment variables."""
        os.environ["DEBUG"] = "true"
        os.environ["SECRET_KEY"] = "test-secret"
        os.environ["THEME"] = "custom"

        try:
            config = Config()
            assert config.debug is True
            assert config.secret_key == "test-secret"
            assert config.theme == "custom"
        finally:
            # Clean up environment
            os.environ.pop("DEBUG", None)
            os.environ.pop("SECRET_KEY", None)
            os.environ.pop("THEME", None)

    def test_database_path(self):
        """Test database path extraction."""
        config = Config()
        db_path = config.database_path

        assert db_path.name == "database.db"

    def test_get_config_singleton(self):
        """Test that get_config returns the same instance."""
        config1 = get_config()
        config2 = get_config()

        assert config1 is config2

    def test_set_config(self):
        """Test setting a custom configuration."""
        custom_config = Config()
        custom_config.secret_key = "custom-key"

        set_config(custom_config)
        retrieved_config = get_config()

        assert retrieved_config.secret_key == "custom-key"
