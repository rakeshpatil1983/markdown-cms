"""Markdown parser with AST support and component processing."""

import re
from typing import Any

import markdown_it

# Import pure text parser
try:
    from .pure_text_parser import parse_pure_text_syntax
except ImportError:
    # Fallback if import fails
    def parse_pure_text_syntax(text):
        return text


class MarkdownParser:
    """Parse markdown files with metadata and component support."""

    def __init__(self):
        self.md = markdown_it.MarkdownIt(
            "gfm-like",  # GitHub Flavored Markdown for tables, strikethrough, etc.
            {
                "html": True,
                "breaks": True,
                "linkify": False,  # Disabled - requires linkify-it-py package
                "typographer": True,
            },
        ).enable(["table", "strikethrough"])

    def parse(self, content: str) -> dict[str, Any]:
        """Parse markdown content and extract metadata and HTML."""

        # Extract metadata blocks
        metadata, content_without_meta = self.extract_metadata(content)

        # Process pure text syntax BEFORE markdown rendering
        content_with_components = parse_pure_text_syntax(content_without_meta)

        # Convert to HTML
        html = self.md.render(content_with_components)

        # Convert mermaid code blocks to mermaid divs for client-side rendering
        html = self._render_mermaid_blocks(html)

        # Add id attributes to h2/h3 tags for TOC anchor links
        html = self._add_heading_ids(html)

        return {
            "metadata": metadata,
            "html": html,
            "raw_content": content_without_meta,
        }

    def extract_metadata(self, content: str) -> tuple[dict[str, Any], str]:
        """Extract metadata from YAML frontmatter and :::meta blocks."""

        metadata = {}
        content_without_meta = content

        # 1. Parse YAML frontmatter (--- delimited block at start of file)
        frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n?"
        fm_match = re.match(frontmatter_pattern, content_without_meta, re.DOTALL)
        if fm_match:
            fm_text = fm_match.group(1)
            for line in fm_text.strip().split("\n"):
                line = line.strip()
                if ":" in line and not line.startswith("#"):
                    key, value = line.split(":", 1)
                    value = value.strip().strip('"').strip("'")
                    metadata[key.strip().lower()] = value
            # Remove frontmatter from content
            content_without_meta = content_without_meta[fm_match.end() :]

        # 2. Parse :::meta blocks (CMS native format)
        meta_pattern = r":::meta\s*\n(.*?)\n:::"
        matches = re.findall(meta_pattern, content_without_meta, re.DOTALL)

        for match in matches:
            lines = match.strip().split("\n")
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip().lower()] = value.strip()

        # Remove meta blocks from content
        content_without_meta = re.sub(
            meta_pattern, "", content_without_meta, flags=re.DOTALL
        )

        return metadata, content_without_meta.strip()

    def process_components(self, content: str) -> str:
        """Process component blocks using pure text parser."""
        return parse_pure_text_syntax(content)

    def extract_components(self, content: str) -> list[dict[str, Any]]:
        """Extract component blocks for processing."""

        components = []

        # Find all component blocks
        component_pattern = r":::(\w+)\s*\n(.*?)\n:::"
        matches = re.findall(component_pattern, content, re.DOTALL)

        for component_type, component_content in matches:
            # Parse component parameters
            params = {}
            lines = component_content.strip().split("\n")
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    params[key.strip()] = value.strip()

            components.append(
                {
                    "type": component_type,
                    "params": params,
                    "raw_content": component_content,
                }
            )

        return components

    def extract_headings(self, content: str) -> list[dict[str, Any]]:
        """Extract ## and ### headings for table of contents."""
        headings = []
        for match in re.finditer(r"^(#{2,3})\s+(.+)$", content, re.MULTILINE):
            level = len(match.group(1))  # 2 or 3
            text = match.group(2).strip()
            slug = self._make_slug(text)
            headings.append({"level": level, "text": text, "slug": slug})
        return headings

    @staticmethod
    def _make_slug(text: str) -> str:
        """Generate a URL-safe slug from heading text."""
        slug = re.sub(r"[^\w\s-]", "", text.lower())
        slug = re.sub(r"[\s]+", "-", slug).strip("-")
        return slug

    def _render_mermaid_blocks(self, html: str) -> str:
        """Replace <pre><code class="language-mermaid">...</code></pre> with <div class="mermaid">."""
        import html as html_module

        def replace_block(match):
            encoded = match.group(1)
            # markdown-it HTML-encodes the content inside <code>; decode it back
            decoded = html_module.unescape(encoded)
            return f'<div class="mermaid">{decoded}</div>'

        return re.sub(
            r'<pre><code class="language-mermaid">(.*?)</code></pre>',
            replace_block,
            html,
            flags=re.DOTALL,
        )

    def _add_heading_ids(self, html: str) -> str:
        """Add id attributes to h2 and h3 tags for TOC anchor links."""

        def _replace(match):
            tag = match.group(1)  # h2 or h3
            inner = match.group(2)
            # Strip HTML tags to get plain text for slug
            plain = re.sub(r"<[^>]+>", "", inner)
            slug = self._make_slug(plain)
            return f'<{tag} id="{slug}">{inner}</{tag}>'

        return re.sub(r"<(h[23])>(.*?)</\1>", _replace, html)
