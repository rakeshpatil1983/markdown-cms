"""Sidebar tree builder and HTML renderer for Docusaurus-style navigation.

Supports configurable sidebar modes via _site.md:
- tree: Full expandable tree (default)
- subjects: Top-level categories at root, filtered view inside
- flat: All pages in a flat list
"""

import json
import os
import re
from pathlib import Path
from typing import Any

from .config import get_config

# Module-level cache
_sidebar_cache: dict[str, Any] = {"tree": None, "mtime": 0.0}


def _read_category_json(folder: Path) -> dict[str, Any]:
    """Read _category_.json from a folder if it exists."""
    cat_file = folder / "_category_.json"
    if cat_file.exists():
        try:
            data = json.loads(cat_file.read_text(encoding="utf-8"))
            return {
                "label": data.get("label", ""),
                "position": data.get("position", 999),
            }
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _label_from_name(name: str) -> str:
    """Derive a display label from a folder or file name.

    Strips leading number prefixes like '01-', replaces hyphens with spaces,
    and title-cases the result.
    """
    # Strip leading number prefix (e.g. '01-', '02-')
    label = re.sub(r"^\d+-", "", name)
    # Replace hyphens and underscores with spaces
    label = label.replace("-", " ").replace("_", " ")
    return label.strip().title()


def _extract_frontmatter(file_path: Path) -> dict[str, str]:
    """Read the first portion of a markdown file to extract YAML frontmatter.

    Only reads the beginning of the file for performance.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = []
            for i, line in enumerate(f):
                lines.append(line)
                if i >= 30:  # Read up to 30 lines for frontmatter
                    break

        text = "".join(lines)
        fm_match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        if not fm_match:
            return {}

        metadata = {}
        for line in fm_match.group(1).strip().split("\n"):
            line = line.strip()
            if ":" in line and not line.startswith("#"):
                key, value = line.split(":", 1)
                value = value.strip().strip('"').strip("'")
                metadata[key.strip()] = value
        return metadata
    except OSError:
        return {}


def _should_skip_file(name: str) -> bool:
    """Check if a markdown file should be skipped in sidebar."""
    if not name.endswith(".md"):
        return True
    if name.startswith("_"):
        return True
    if name.endswith(".bak"):
        return True
    if name == "index.md":
        return True
    return False


def _build_tree_recursive(folder: Path, base_path: Path) -> list[dict[str, Any]]:
    """Recursively build the sidebar tree from a folder."""
    children: list[dict[str, Any]] = []

    if not folder.is_dir():
        return children

    for entry in sorted(folder.iterdir()):
        if entry.name.startswith(".") or entry.name.startswith("_"):
            continue

        if entry.is_dir():
            # Skip 'images' directories
            if entry.name.lower() == "images":
                continue

            # Read category metadata
            cat_info = _read_category_json(entry)
            label = cat_info.get("label") or _label_from_name(entry.name)
            position = cat_info.get("position", 999)

            # Build children recursively
            sub_children = _build_tree_recursive(entry, base_path)

            # Only add category if it has children
            if sub_children:
                rel_path = entry.relative_to(base_path).as_posix()
                children.append(
                    {
                        "type": "category",
                        "label": label,
                        "position": position,
                        "path": rel_path,
                        "children": sub_children,
                    }
                )

        elif entry.is_file() and entry.suffix == ".md":
            if _should_skip_file(entry.name):
                continue

            # Extract frontmatter
            fm = _extract_frontmatter(entry)
            title = fm.get("title", "")
            sidebar_pos = fm.get("sidebar_position", "")

            # Derive label from title or filename
            if not title:
                # Strip .md extension, then derive label
                title = _label_from_name(entry.stem)

            # Parse position
            try:
                position = int(sidebar_pos)
            except (ValueError, TypeError):
                position = 9999  # No position = sort to end

            # URL path = relative path without .md
            rel_path = entry.relative_to(base_path).with_suffix("").as_posix()

            children.append(
                {
                    "type": "page",
                    "label": title,
                    "position": position,
                    "path": rel_path,
                }
            )

    # Sort: by position first, then alphabetically by label for ties
    children.sort(key=lambda x: (x["position"], x["label"]))
    return children


def build_sidebar_tree(pages_path: Path) -> list[dict[str, Any]]:
    """Build the full sidebar navigation tree from the pages directory.

    Uses caching based on directory modification time to avoid
    re-scanning on every request.
    """
    global _sidebar_cache

    # Check cache validity using directory walk mtime
    try:
        current_mtime = os.path.getmtime(pages_path)
    except OSError:
        current_mtime = 0.0

    if _sidebar_cache["tree"] is not None and _sidebar_cache["mtime"] == current_mtime:
        return _sidebar_cache["tree"]

    tree: list[dict[str, Any]] = []

    if not pages_path.is_dir():
        return tree

    # Only include top-level directories (categories), not top-level .md files
    for entry in sorted(pages_path.iterdir()):
        if entry.name.startswith(".") or entry.name.startswith("_"):
            continue

        if entry.is_dir():
            # Skip 'images' directory
            if entry.name.lower() == "images":
                continue

            cat_info = _read_category_json(entry)
            label = cat_info.get("label") or _label_from_name(entry.name)
            position = cat_info.get("position", 999)

            sub_children = _build_tree_recursive(entry, pages_path)

            if sub_children:
                rel_path = entry.relative_to(pages_path).as_posix()
                tree.append(
                    {
                        "type": "category",
                        "label": label,
                        "position": position,
                        "path": rel_path,
                        "children": sub_children,
                    }
                )

    # Sort top-level categories
    tree.sort(key=lambda x: (x["position"], x["label"]))

    # Update cache
    _sidebar_cache["tree"] = tree
    _sidebar_cache["mtime"] = current_mtime

    return tree


def _is_ancestor(category_path: str, current_path: str) -> bool:
    """Check if a category path is an ancestor of the current page path."""
    if not current_path:
        return False
    # Normalize to forward slashes for comparison
    return current_path.startswith(category_path + "/") or current_path == category_path


def render_left_sidebar(tree: list[dict[str, Any]], current_path: str) -> str:
    """Render the sidebar tree as HTML with collapsible categories.

    Uses <details>/<summary> for pure-HTML collapsible sections.
    Ancestors of the current page are expanded, and the current page
    link gets an 'active' class.

    Sidebar mode is configurable via _site.md:
    - tree: Full expandable tree (default)
    - subjects: Top-level categories at root, filtered view inside
    - flat: All pages in a flat list
    """
    if not tree:
        return '<div class="sidebar-empty">No pages found</div>'

    # Get sidebar mode from config
    config = get_config()
    site_config = config.get_site_config()
    sidebar_mode = site_config.get("sidebar_mode", "tree")
    sidebar_title = site_config.get("sidebar_title", "Navigation")

    html_parts = ['<nav class="sidebar-nav">']

    if sidebar_mode == "subjects":
        # SUBJECTS MODE: Show subjects at root, filtered view inside
        html_parts.append(_render_subjects_mode(tree, current_path, sidebar_title))
    elif sidebar_mode == "flat":
        # FLAT MODE: Show all pages in a flat list
        html_parts.append(_render_flat_mode(tree, current_path, sidebar_title))
    else:
        # TREE MODE (default): Full expandable tree
        html_parts.append(
            f'<div class="nav-tree-title">{_escape_html(sidebar_title)}</div>'
        )
        html_parts.append(_render_tree_level(tree, current_path))

    html_parts.append("</nav>")
    return "".join(html_parts)


def _get_first_page(category: dict[str, Any]) -> str:
    """Get the path of the first page in a category (recursive)."""
    children = category.get("children", [])
    for child in children:
        if child["type"] == "page":
            return f"/{child['path']}"
        elif child["type"] == "category":
            result = _get_first_page(child)
            if result:
                return result
    return ""


def _render_subjects_mode(
    tree: list[dict[str, Any]], current_path: str, title: str
) -> str:
    """Render sidebar in subjects mode.

    At root level: Show only subject names as clickable links
    Inside a subject: Show "back to all subjects" + subject's chapters/topics
    """
    parts: list[str] = []

    if not current_path:
        # ROOT LEVEL: Show only subject names as links
        parts.append('<div class="nav-subjects-list">')
        parts.append(f'<div class="nav-subjects-title">{_escape_html(title)}</div>')
        for item in tree:
            if item["type"] == "category":
                label_html = _escape_html(item["label"])
                # Link to first page in the subject, or just the subject path
                first_page = _get_first_page(item)
                link_path = first_page if first_page else f"/{item['path']}"
                parts.append(
                    f'<a href="{link_path}" class="nav-subject-link">{label_html}</a>'
                )
        parts.append("</div>")
    else:
        # INSIDE A SUBJECT: Show subject content with back link
        path_parts = current_path.split("/")
        subject_path = path_parts[0] if path_parts else ""
        current_subject = None
        filtered_tree = tree

        # Find matching subject in tree
        for item in tree:
            if item["type"] == "category" and item["path"] == subject_path:
                current_subject = item
                filtered_tree = item.get("children", [])
                break

        if current_subject:
            parts.append('<div class="nav-subject-header">')
            parts.append('<a href="/" class="nav-back-link">← All Subjects</a>')
            parts.append(
                f'<div class="nav-subject-title">{_escape_html(current_subject["label"])}</div>'
            )
            parts.append("</div>")

        parts.append(_render_tree_level(filtered_tree, current_path))

    return "".join(parts)


def _render_flat_mode(tree: list[dict[str, Any]], current_path: str, title: str) -> str:
    """Render sidebar in flat mode - all pages in a flat list."""
    parts: list[str] = []
    parts.append(f'<div class="nav-flat-title">{_escape_html(title)}</div>')
    parts.append('<div class="nav-flat-list">')

    # Collect all pages recursively
    all_pages = _collect_all_pages(tree)

    for page in all_pages:
        active_cls = " active" if page["path"] == current_path else ""
        label_html = _escape_html(page["label"])
        parts.append(
            f'<a href="/{page["path"]}" class="nav-page{active_cls}">{label_html}</a>'
        )

    parts.append("</div>")
    return "".join(parts)


def _collect_all_pages(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Recursively collect all pages from the tree."""
    pages: list[dict[str, Any]] = []
    for item in items:
        if item["type"] == "page":
            pages.append(item)
        elif item["type"] == "category" and item.get("children"):
            pages.extend(_collect_all_pages(item["children"]))
    return pages


def _render_tree_level(items: list[dict[str, Any]], current_path: str) -> str:
    """Render one level of the sidebar tree."""
    parts: list[str] = []

    for item in items:
        if item["type"] == "category":
            # Check if this category should be open
            is_open = _is_ancestor(item["path"], current_path)
            open_attr = " open" if is_open else ""

            label_html = _escape_html(item["label"])
            parts.append(f"<details{open_attr}>")
            parts.append(f"<summary>{label_html}</summary>")
            parts.append('<div class="nav-children">')

            if item.get("children"):
                parts.append(_render_tree_level(item["children"], current_path))

            parts.append("</div>")
            parts.append("</details>")

        elif item["type"] == "page":
            active_cls = " active" if item["path"] == current_path else ""
            label_html = _escape_html(item["label"])
            parts.append(
                f'<a href="/{item["path"]}" class="nav-page{active_cls}">'
                f"{label_html}</a>"
            )

    return "".join(parts)


def _escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_toc(headings: list[dict[str, Any]]) -> str:
    """Render a table-of-contents HTML block from extracted headings."""
    if not headings:
        return ""

    parts = ['<div class="toc">']
    parts.append('<div class="toc-title">On this page</div>')
    parts.append('<ul class="toc-list">')

    for h in headings:
        level_cls = f"toc-h{h['level']}"
        text_html = _escape_html(h["text"])
        parts.append(
            f'<li><a href="#{h["slug"]}" class="{level_cls}">{text_html}</a></li>'
        )

    parts.append("</ul>")
    parts.append("</div>")
    return "".join(parts)
