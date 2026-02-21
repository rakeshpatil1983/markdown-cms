"""Router setup for Markdown CMS."""

from pathlib import Path
from typing import Any
from urllib.parse import quote

from fasthtml.common import *

from .admin_routes import setup_admin_routes
from .auth_routes import setup_auth_routes
from .config import get_config
from .parser import MarkdownParser
from .sidebar import build_sidebar_tree, render_left_sidebar, render_toc


def setup_routes(app):
    """Setup all application routes."""

    # Setup authentication routes
    setup_auth_routes(app)

    # Setup admin routes
    setup_admin_routes(app)

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

    @app.get("/components/{component_path:path}")
    def component_part(component_path: str):
        """HTMX endpoint for component parts - supports nested paths like elements/button."""
        config = get_config()
        # Components path is at project_path / "components"
        components_path = config.project_path / "components"
        component_file = components_path / f"{component_path}.md"

        if not component_file.exists():
            return Response("", status_code=200)  # Return empty for missing components

        try:
            content = component_file.read_text(encoding="utf-8")
            parsed = parser.parse(content)
            return NotStr(parsed.get("html", ""))
        except Exception:
            return Response("", status_code=200)

    @app.get("/leftsidebar")
    def left_sidebar(path: str = ""):
        """HTMX endpoint for the left navigation sidebar."""
        config = get_config()
        tree = build_sidebar_tree(config.pages_path)
        html = render_left_sidebar(tree, path)
        return NotStr(html)

    @app.get("/rightsidebar")
    def right_sidebar(path: str = ""):
        """HTMX endpoint for the right sidebar (TOC + quick links)."""
        config = get_config()
        site_config = config.get_site_config()

        # Part 1: Page TOC from headings (respect show_toc config)
        toc_html = ""
        show_toc = site_config.get("show_toc", "true").lower() == "true"
        if show_toc and path:
            md_path = config.pages_path / f"{path}.md"
            if md_path.exists():
                content = md_path.read_text(encoding="utf-8")
                _, content_body = parser.extract_metadata(content)
                headings = parser.extract_headings(content_body)
                toc_html = render_toc(headings)

        # Part 2: Static links from _rightnav.md
        static_html = ""
        rightnav_file = config.templates_path / "_rightnav.md"
        if rightnav_file.exists():
            try:
                content = rightnav_file.read_text(encoding="utf-8")
                parsed_nav = parser.parse(content)
                static_html = parsed_nav.get("html", "")
            except Exception:
                pass

        return NotStr(toc_html + static_html)

    # Image/asset file extensions to serve from pages/ directories
    ASSET_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg",
        ".webp",
        ".ico",
        ".pdf",
        ".css",
        ".js",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
    }

    @app.get("/{page_path:path}")
    def dynamic_page(page_path: str):
        """Dynamic page route - serves .md files and static assets from pages/."""
        # Skip templates and components routes
        if page_path.startswith(("templates/", "components/")):
            return Response("Not found", status_code=404)
        if page_path in ("leftsidebar", "rightsidebar"):
            return Response("Not found", status_code=404)

        config = get_config()

        # Serve static files from static/ directory
        if page_path.startswith("static/"):
            rel = page_path[len("static/") :]
            static_file = config.static_path / rel
            if static_file.exists():
                return FileResponse(str(static_file))
            return Response("Not found", status_code=404)

        # Serve static assets (images, etc.) from pages/ subdirectories
        ext = Path(page_path).suffix.lower()
        if ext in ASSET_EXTENSIONS:
            asset_path = config.pages_path / page_path
            if asset_path.exists():
                return FileResponse(str(asset_path))
            return Response("Not found", status_code=404)

        # Handle pages with or without .md extension
        if not page_path.endswith(".md"):
            page_path = f"{page_path}.md"
        return render_markdown_page(page_path, parser)

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

            # Derive page_path (without .md) for sidebar context
            page_path = file_path
            if page_path.endswith(".md"):
                page_path = page_path[:-3]

            # Render with layout (template parts loaded via HTMX)
            return render_with_layout(html_content, metadata, layout, page_path)

        except Exception as e:
            return Response(f"Error rendering page: {str(e)}", status_code=500)


def _build_head(title: str, css_content: str, theme_config: dict):
    """Build the common <head> section for all layouts.

    Loads CSS/JS based on theme configuration - supports Bootstrap, Bulma,
    Materialize, Tailwind, or no framework (custom CSS only).
    """
    head_elements = [
        Title(title),
        Meta(charset="utf-8"),
        Meta(name="viewport", content="width=device-width, initial-scale=1"),
    ]

    # Load framework CSS if specified
    framework_css = theme_config.get("framework_css", "")
    if framework_css:
        head_elements.append(Link(rel="stylesheet", href=framework_css))

    # Load custom theme CSS
    head_elements.append(Style(css_content))

    # HTMX is always loaded
    head_elements.append(Script(src="https://unpkg.com/htmx.org@1.9.10"))

    # Load framework JS if specified
    framework_js = theme_config.get("framework_js", "")
    if framework_js:
        head_elements.append(Script(src=framework_js))

    # MathJax for LaTeX math rendering
    head_elements.append(
        Script(
            """
        MathJax = {
            tex: {
                inlineMath: [['\\\\(', '\\\\)']],
                displayMath: [['$$', '$$']],
            },
            options: {
                skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
            }
        };
    """
        )
    )
    head_elements.append(
        Script(
            src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js",
            async_="true",
        )
    )

    # Mobile sidebar toggle script
    head_elements.append(
        Script(
            """
        document.addEventListener('DOMContentLoaded', function() {
            // Close sidebars when clicking outside
            document.addEventListener('click', function(e) {
                var leftOpen = document.body.classList.contains('sidebar-left-open');
                var rightOpen = document.body.classList.contains('sidebar-right-open');

                if (!leftOpen && !rightOpen) return;

                var leftSidebar = document.querySelector('.sidebar-left');
                var rightSidebar = document.querySelector('.sidebar-right');
                var toggleBtns = document.querySelectorAll('.mobile-toggle');

                var clickedInsideSidebar = (leftSidebar && leftSidebar.contains(e.target)) ||
                                            (rightSidebar && rightSidebar.contains(e.target));
                var clickedToggle = Array.from(toggleBtns).some(function(btn) { return btn.contains(e.target); });

                // Close if clicked outside sidebar and not on toggle buttons
                if (!clickedInsideSidebar && !clickedToggle) {
                    document.body.classList.remove('sidebar-left-open', 'sidebar-right-open');
                }
            });

            // Close sidebars on escape key
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') {
                    document.body.classList.remove('sidebar-left-open', 'sidebar-right-open');
                }
            });

            // Handle dropdown toggle on mobile (touch devices)
            var dropdowns = document.querySelectorAll('.nav-dropdown > a');
            dropdowns.forEach(function(dropdown) {
                dropdown.addEventListener('click', function(e) {
                    if (window.innerWidth <= 768) {
                        e.preventDefault();
                        this.parentElement.classList.toggle('open');
                    }
                });
            });
        });
    """
        )
    )

    return Head(*head_elements)


def _build_header():
    """Build the common header section for all layouts."""
    return Header(cls="header")(
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
    )


def _build_mobile_toggles():
    """Build the fixed mobile toggle buttons for sidebars."""
    # Using a fragment-like approach - buttons are fixed position so they don't need a wrapper
    return (
        Button(
            type="button",
            cls="mobile-toggle mobile-toggle-left",
            onclick="document.body.classList.toggle('sidebar-left-open'); return false;",
            aria_label="Toggle navigation menu",
        )(
            Span(cls="toggle-icon")("☰"),
            Span(cls="toggle-label")("Menu"),
        ),
        Button(
            type="button",
            cls="mobile-toggle mobile-toggle-right",
            onclick="document.body.classList.toggle('sidebar-right-open'); return false;",
            aria_label="Toggle table of contents",
        )(
            Span(cls="toggle-icon")("≡"),
            Span(cls="toggle-label")("TOC"),
        ),
    )


def _build_footer():
    """Build the common footer section for all layouts."""
    return Footer(
        cls="footer",
        hx_get="/templates/footer",
        hx_trigger="load",
        hx_swap="innerHTML",
    )("Loading footer...")


def _build_breadcrumbs(page_path: str) -> str:
    """Build breadcrumb navigation from page path.

    Example: electronics/Fundamentals/02-ohms-law
    Becomes: Home > Electronics > Fundamentals > Ohm's Law
    """
    if not page_path or page_path == "index":
        return ""

    parts = page_path.split("/")
    crumbs = ['<nav class="breadcrumbs" aria-label="Breadcrumb">']
    crumbs.append('<ol class="breadcrumb">')

    # Home link
    crumbs.append('<li class="breadcrumb-item"><a href="/">Home</a></li>')

    # Build path progressively
    current_path = ""
    for i, part in enumerate(parts):
        current_path = f"{current_path}/{part}" if current_path else part

        # Clean up the label (remove numbers, dashes, make readable)
        label = part
        # Remove leading numbers like "01-", "02-"
        if len(label) > 3 and label[2] == "-" and label[:2].isdigit():
            label = label[3:]
        # Replace dashes with spaces and title case
        label = label.replace("-", " ").replace("_", " ").title()

        is_last = i == len(parts) - 1
        if is_last:
            crumbs.append(
                f'<li class="breadcrumb-item active" aria-current="page">{label}</li>'
            )
        else:
            crumbs.append(
                f'<li class="breadcrumb-item"><a href="/{current_path}">{label}</a></li>'
            )

    crumbs.append("</ol>")
    crumbs.append("</nav>")
    return "".join(crumbs)


def render_with_layout(
    content: str, metadata: dict[str, Any], layout: str, page_path: str = ""
):
    """Render content with the specified layout using HTMX partials.

    Layout types:
    - 'docs' (default): 3-column layout with left nav sidebar and right TOC
    - 'landing': Full-width layout for homepage/marketing pages, no sidebars
    - 'page': Centered content layout for simple pages, no sidebars

    Theme system:
    - Loads CSS/JS from themes/<theme-name>/ directory
    - Theme config in _theme.md specifies framework (bootstrap, bulma, etc.)
    - Falls back to static/css/styles.css if theme not found
    """
    title = metadata.get("title", "Markdown CMS")
    config = get_config()
    site_config = config.get_site_config()

    # Load theme configuration
    theme_config = config.get_theme_config()

    # Build breadcrumbs if enabled
    show_breadcrumbs = site_config.get("show_breadcrumbs", "true").lower() == "true"
    breadcrumbs_html = _build_breadcrumbs(page_path) if show_breadcrumbs else ""

    # Load theme CSS (fallback to static/css/styles.css)
    theme_css_path = config.theme_path / theme_config.get("custom_css", "styles.css")
    if theme_css_path.exists():
        css_content = theme_css_path.read_text(encoding="utf-8")
    else:
        # Fallback to static/css/styles.css
        css_path = config.static_path / "css" / "styles.css"
        css_content = css_path.read_text(encoding="utf-8") if css_path.exists() else ""

    encoded_path = quote(page_path, safe="")

    # Build layout-specific main content
    if layout == "landing":
        # Landing page: full-width, no sidebars
        main_content = Main(cls="main main-landing")(
            Div(NotStr(content), cls="landing-content"),
        )
    elif layout == "page":
        # Simple page: centered content, no sidebars
        main_content = Main(cls="main main-page")(
            Div(cls="container")(
                Div(NotStr(content), cls="page-content"),
            )
        )
    else:
        # Default 'docs' layout: 3-column with sidebars
        # Combine breadcrumbs with content
        content_with_breadcrumbs = (
            breadcrumbs_html + content if breadcrumbs_html else content
        )
        main_content = Main(cls="main main-docs")(
            Div(cls="container")(
                Div(cls="main-layout")(
                    Aside(
                        cls="sidebar-left",
                        hx_get=f"/leftsidebar?path={encoded_path}",
                        hx_trigger="load",
                        hx_swap="innerHTML",
                    )("Loading..."),
                    Div(NotStr(content_with_breadcrumbs), cls="content"),
                    Aside(
                        cls="sidebar-right",
                        hx_get=f"/rightsidebar?path={encoded_path}",
                        hx_trigger="load",
                        hx_swap="innerHTML",
                    )("Loading..."),
                )
            )
        )

    mobile_toggles = _build_mobile_toggles()
    return Html(
        _build_head(title, css_content, theme_config),
        Body(
            _build_header(),
            mobile_toggles[0],  # Left toggle
            mobile_toggles[1],  # Right toggle
            main_content,
            _build_footer(),
        ),
    )
