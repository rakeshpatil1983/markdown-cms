"""Main application entry point for Markdown-First Application Framework."""

import importlib.util
import os
import sys
from pathlib import Path

from fasthtml.common import *
from starlette.staticfiles import StaticFiles

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from markdown_cms.core.database import init_db
from markdown_cms.core.router import setup_routes


def load_application_routes(app):
    """
    Auto-load application-specific API routes from api.py in the project directory.

    This allows applications to define their own HTMX endpoints (calculators,
    form handlers, etc.) without modifying the core library.
    """
    api_file = Path("api.py")
    if api_file.exists():
        try:
            # Load the module dynamically
            spec = importlib.util.spec_from_file_location("app_api", api_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Call setup_api_routes if it exists
            if hasattr(module, "setup_api_routes"):
                module.setup_api_routes(app)
        except Exception as e:
            print(f"Warning: Failed to load application routes from api.py: {e}")


def create_app():
    """Create and configure the FastHTML application."""

    # Initialize database (creates tables if they don't exist)
    init_db()

    # Create FastHTML app with minimal headers
    # CSS is loaded in render_with_layout from static/ folder
    app = FastHTML(
        hdrs=(
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Script(src="https://unpkg.com/htmx.org@1.9.10"),
            # Bootstrap JS for carousel and other interactive components
            Script(
                src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js",
                integrity="sha384-geWF76RCwLtnZ8qwWowPQNguL3RmwHVBC9FhGdlKrxdiJJigb/j/68SIy3Te4Bkz",
                crossorigin="anonymous",
            ),
            # MathJax for rendering $...$ inline and $$...$$ display math
            Script(
                "window.MathJax = { tex: { inlineMath: [['$','$']], displayMath: [['$$','$$']] } };",
                type="text/javascript",
            ),
            Script(
                src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js",
                id="MathJax-script",
                **{"async": True},
            ),
        ),
    )

    # Mount static files directory (FastHTML doesn't auto-mount static files)
    static_dir = Path("static")
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Setup core library routes
    setup_routes(app)

    # Load application-specific API routes (from api.py in project directory)
    load_application_routes(app)

    return app


def main():
    """Main entry point for running the application."""
    import uvicorn

    app = create_app()

    # Run the application
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))

    # Check if we're in a project directory
    reload_dirs = []
    if Path("pages").exists():
        reload_dirs.append("pages")
    if Path("templates").exists():
        reload_dirs.append("templates")
    if Path("static").exists():
        reload_dirs.append("static")

    # If no project directories found, use current directory
    if not reload_dirs:
        reload_dirs = ["."]

    uvicorn.run(
        "markdown_cms.app:create_app",
        host=host,
        port=port,
        reload=True,  # Always enable auto-reload for development
        reload_dirs=reload_dirs,  # Watch project files for changes
        factory=True,
    )


if __name__ == "__main__":
    main()
