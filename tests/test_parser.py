"""Test the markdown parser functionality."""

from markdown_cms.core.parser import MarkdownParser


class TestMarkdownParser:
    """Test cases for MarkdownParser class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = MarkdownParser()

    def test_parse_simple_markdown(self):
        """Test parsing simple markdown without metadata."""
        content = "# Hello World\n\nThis is a test."
        result = self.parser.parse(content)

        assert "metadata" in result
        assert "html" in result
        assert "raw_content" in result
        assert result["metadata"] == {}
        assert "<h1>Hello World</h1>" in result["html"]
        assert "<p>This is a test.</p>" in result["html"]

    def test_parse_with_metadata(self):
        """Test parsing markdown with metadata block."""
        content = """:::meta
Title: Test Page
Layout: default
:::

# Content

This is content with metadata."""

        result = self.parser.parse(content)

        assert result["metadata"]["title"] == "Test Page"
        assert result["metadata"]["layout"] == "default"
        assert "<h1>Content</h1>" in result["html"]
        assert "<p>This is content with metadata.</p>" in result["html"]

    def test_extract_components(self):
        """Test extracting component blocks."""
        content = """
# Page

:::table
Source: users
Columns: name, email
:::

:::stat
Label: Total Users
Source: user_count
:::
"""

        components = self.parser.extract_components(content)

        assert len(components) == 2

        # Check table component
        table_comp = next(c for c in components if c["type"] == "table")
        assert table_comp["params"]["Source"] == "users"
        assert table_comp["params"]["Columns"] == "name, email"

        # Check stat component
        stat_comp = next(c for c in components if c["type"] == "stat")
        assert stat_comp["params"]["Label"] == "Total Users"
        assert stat_comp["params"]["Source"] == "user_count"

    def test_extract_metadata_empty(self):
        """Test metadata extraction with no metadata blocks."""
        content = "# Just content\n\nNo metadata here."
        metadata, content_without_meta = self.parser.extract_metadata(content)

        assert metadata == {}
        assert content_without_meta.strip() == content.strip()

    def test_extract_metadata_multiple_blocks(self):
        """Test metadata extraction with multiple meta blocks."""
        content = """:::meta
Title: First
:::

Some content

:::meta
Author: Second
:::

More content"""

        metadata, content_without_meta = self.parser.extract_metadata(content)

        assert metadata["title"] == "First"
        assert metadata["author"] == "Second"
        assert ":::meta" not in content_without_meta
