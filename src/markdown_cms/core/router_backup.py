"""Router setup for Markdown CMS."""

from typing import Any

from fasthtml.common import *

from .config import get_config
from .parser import MarkdownParser


def setup_routes(app):
    """Setup all application routes."""

    parser = MarkdownParser()

    @app.get("/")
    def home():
        """Home page route."""
        return render_markdown_page("index.md", parser)

    @app.get("/templates/{template_name}")
    def template_part(template_name: str):
        """HTMX endpoint for template parts - returns HTML fragments."""
        config = get_config()
        template_file = config.templates_path / f"{template_name}.md"

        if not template_file.exists():
            return Response("", status_code=200)  # Return empty for missing templates

        try:
            content = template_file.read_text(encoding="utf-8")
            parsed = parser.parse(content)
            return NotStr(parsed.get("html", ""))
        except Exception:
            return Response("", status_code=200)

    @app.get("/components/{component_name}")
    def component_part(component_name: str):
        """HTMX endpoint for component parts - returns HTML fragments."""
        config = get_config()
        # Components path is at project_path / "components"
        components_path = config.project_path / "components"
        component_file = components_path / f"{component_name}.md"

        if not component_file.exists():
            return Response("", status_code=200)  # Return empty for missing components

        try:
            content = component_file.read_text(encoding="utf-8")
            parsed = parser.parse(content)
            return NotStr(parsed.get("html", ""))
        except Exception:
            return Response("", status_code=200)

    @app.get("/{page_path:path}")
    def dynamic_page(page_path: str):
        """Dynamic page route - serves any .md file from pages/ folder."""
        # Skip static, templates, and components routes
        if page_path.startswith(("static/", "templates/", "components/")):
            return Response("Not found", status_code=404)

        # Handle pages with or without .md extension
        if not page_path.endswith(".md"):
            page_path = f"{page_path}.md"
        return render_markdown_page(page_path, parser)

    @app.get("/static/{path:path}")
    def static_files(path: str):
        """Static files route."""
        config = get_config()
        static_path = config.static_path / path
        if static_path.exists():
            return FileResponse(static_path)
        return Response("Not found", status_code=404)

    def render_markdown_page(file_path: str, parser: MarkdownParser):
        """Render a markdown page to HTML."""
        config = get_config()
        full_path = config.pages_path / file_path

        if not full_path.exists():
            return Response("Page not found", status_code=404)

        try:
            # Parse the markdown file
            content = full_path.read_text(encoding="utf-8")
            parsed = parser.parse(content)

            # Get metadata and content
            metadata = parsed.get("metadata", {})
            html_content = parsed.get("html", "")

            # Get layout
            layout = metadata.get("layout", "default")

            # Render with layout (template parts loaded via HTMX)
            return render_with_layout(html_content, metadata, layout)

        except Exception as e:
            return Response(f"Error rendering page: {str(e)}", status_code=500)


def render_with_layout(content: str, metadata: dict[str, Any], layout: str):
    """Render content with the specified layout using HTMX partials."""

    title = metadata.get("title", "Markdown CMS")
    config = get_config()

    # Load CSS from static folder
    css_path = config.static_path / "css" / "styles.css"
    css_content = css_path.read_text() if css_path.exists() else ""

    # Build layout with HTMX partials for template parts
    return Html(
        Head(
            Title(title),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Style(css_content),
            Script(src="https://unpkg.com/htmx.org@1.9.10"),
        ),
        Body(
            # Header section - loaded via HTMX
            Header(cls="header")(
                Div(cls="container")(
                    Div(
                        cls="header-content",
                        hx_get="/templates/header",
                        hx_trigger="load",
                        hx_swap="innerHTML",
                    )("Loading header..."),
                    Nav(
                        cls="navbar",
                        hx_get="/templates/navbar",
                        hx_trigger="load",
                        hx_swap="innerHTML",
                    )("Loading navigation..."),
                )
            ),
            # Main content with sidebar
            Main(cls="main")(
                Div(cls="container")(
                    Div(cls="main-layout")(
                        # Sidebar (left) - loaded via HTMX
                        Aside(
                            cls="sidebar",
                            hx_get="/templates/sidenav",
                            hx_trigger="load",
                            hx_swap="innerHTML",
                        )("Loading sidebar..."),
                        # Page content (right)
                        Div(NotStr(content), cls="content"),
                    )
                )
            ),
            # Footer section - loaded via HTMX
            Footer(
                cls="footer",
                hx_get="/templates/footer",
                hx_trigger="load",
                hx_swap="innerHTML",
            )("Loading footer..."),
        ),
    )
