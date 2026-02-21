# Markdown-First Application Framework

A Markdown-first CMS and Application Framework built with FastHTML and HTMX.

> **Philosophy**: Everything is a file. Everything is Markdown. Markdown is declarative UI, Python is behavior.

---

## What Is This?

`markdown-cms` is a Python web framework where you build complete web applications by writing Markdown files — not just documentation sites.

Pages, layouts, navigation, forms, interactive calculators, data tables, component libraries, admin panels — all driven by Markdown and a file-based structure. Python handles behavior; Markdown handles structure and intent.

Think of it as the intersection of **Obsidian's file-first philosophy**, **WordPress's template system**, and **Django's project structure** — but lighter, faster, and Markdown-native.

### Real-World Reference: TechArya

[TechArya.net](https://techarya.net) — an electronics and embedded systems learning platform — was built and migrated using this framework. It demonstrates the framework's capability beyond documentation:

- **25+ structured electronics lessons** with diagrams, formulas, and categorized navigation
- **Live HTMX calculators** (Ohm's Law, RC filter, power) — form submission returns parsed Markdown responses
- **Nested subject navigation** with auto-generated sidebar trees from the file structure
- **Multi-theme switching** (Bootstrap, Bulma, Tailwind, Materialize) at runtime
- **Image galleries, tables, alerts, carousels** — all from Markdown

TechArya is proof that this framework handles real content-heavy, interactive applications — not just static docs.

---

## What Can You Build With It?

This is **not** a documentation generator. It is a full application framework. You can build:

| Use Case | How |
|---|---|
| Documentation sites | pages/ + markdown content |
| Learning platforms | Nested subject folders + sidebar auto-navigation |
| Company portals | Template parts (header/footer/nav) + themes |
| Technical blogs | File-based routing + metadata |
| Interactive tools | HTMX endpoints + Python API handlers in api.py |
| Admin dashboards | Built-in admin routes + SQLite database |
| Product landing pages | Cards, heroes, stats, columns — all in Markdown |
| Form-driven apps | `:::form` blocks + Python POST handlers |

---

## Philosophy

> Markdown describes structure and intent. Python executes behavior and truth.

This framework enforces a strict separation:

- **Markdown** = pages, layout, content, UI structure, forms, components
- **Python** = business logic, database queries, API responses, authentication

If a feature requires putting Python logic inside a Markdown file — it does not belong here.

### Pure Text Syntax

The framework extends Markdown with a clean, readable syntax for UI elements:

```
=> Click Me              ->  <button class="btn btn-primary">
=> Save (success)        ->  <button class="btn btn-success">
=> Delete (danger)       ->  <button class="btn btn-danger">

? Your Name (text)       ->  <input type="text">
?? Your Message          ->  <textarea>

> [!SUCCESS] Saved!      ->  styled success alert
> [!WARNING] Review      ->  styled warning alert

:::card
# Title
Content here
=> Learn More
:::
```

No HTML required. No YAML. No JSON. Just text that reads like what it means.

---

## Quick Start

```bash
pip install markdown-cms

# Create a new project
markdown-cms create my-project
cd my-project

# Run development server
markdown-cms run
```

Open `http://localhost:8000` — your site is live with auto-reload.

---

## Features

- **File-based routing** — `pages/about.md` becomes `/about`, `pages/docs/intro.md` becomes `/docs/intro`
- **Template parts** — WordPress-style `header.md`, `footer.md`, `navbar.md`, `sidenav.md`
- **Multi-theme system** — Switch between Bootstrap, Bulma, Tailwind, Materialize with one command
- **HTMX-native** — Components load via HTMX fragments; no page refresh needed
- **Component library** — 3-level hierarchy: Elements, Containers, Layout
- **Plugin system** — Drop Python plugins into `plugins/` directory
- **Admin panel** — Built-in content management at `/admin`
- **Authentication** — JWT-based auth, user management
- **Database** — SQLite via SQLAlchemy, with CLI commands (`markdown-cms db init/seed/reset`)
- **Auto-reload** — Watches `pages/`, `templates/`, `static/` for changes
- **API routes** — Drop an `api.py` in your project root; the framework auto-loads it
- **Agents** — Built-in orchestrator, implementation, and testing agents for development assistance

---

## Project Structure

```
my-project/
├── pages/           # Markdown content -> URL routes
├── templates/       # header.md, footer.md, navbar.md, sidenav.md
├── static/          # CSS, JS, images
├── components/      # Reusable HTMX-loadable markdown fragments
│   ├── elements/    # Buttons, inputs, dropdowns
│   ├── containers/  # Cards, panels, tabs
│   └── layout/      # Navbar, sidebar, header, footer
├── themes/          # bootstrap/, bulma/, tailwind/, materialize/
├── apps/            # Custom Django-style applications
├── plugins/         # Custom plugins
└── api.py           # Your HTMX API endpoints (auto-loaded)
```

---

## CLI Commands

```bash
markdown-cms create <name>          # Scaffold new project
markdown-cms run                    # Development server (auto-reload)
markdown-cms run --port 3000        # Custom port
markdown-cms build                  # Validate project structure
markdown-cms theme bootstrap        # Switch to Bootstrap theme
markdown-cms theme tailwind         # Switch to Tailwind theme
markdown-cms db init                # Create database tables
markdown-cms db seed                # Seed with sample data
markdown-cms db reset               # Drop and recreate (with confirmation)
markdown-cms db info                # Show database info
markdown-cms agent orchestrator     # Run development orchestrator agent
```

---

## Writing HTMX API Routes

Create `api.py` in your project root — the framework loads it automatically:

```python
from markdown_cms.core.parser import MarkdownParser
from fasthtml.common import NotStr

_parser = MarkdownParser()

def render_markdown(md_text):
    return _parser.parse(md_text).get("html", "")

def setup_api_routes(app):

    @app.post("/api/calculate")
    async def calculate(request):
        form = await request.form()
        value = float(form.get("input", 0))
        result = value * 2

        # Return Markdown — the library parses it to HTML
        md = f"> [!SUCCESS] Result\n> **{result}**"
        return NotStr(render_markdown(md))
```

Then call it from any Markdown page:

```markdown
:::form /api/calculate
? Input Value (number)
=> Calculate (success)
:::
```

Zero boilerplate. No templates. Pure Markdown + Python.

---

## Limitations

The framework is at **v0.1.0 / Alpha** stage. Known limitations:

- **No built-in search** — full-text search across pages requires a custom plugin
- **SQLite only** — no PostgreSQL or MySQL support yet
- **Single-user auth** — multi-tenant or org-level permissions not implemented
- **No asset pipeline** — CSS/JS is served as-is; no bundling or minification
- **Plugin API is minimal** — the plugin scaffold exists but the hook system is early-stage
- **No live preview in admin** — content edits require a page reload to see final output
- **Python 3.12+ required** — uses modern type annotation syntax throughout
- **No i18n/l10n** — no built-in internationalisation support

---

## Roadmap / Feature Improvements

Planned for future versions:

| Feature | Priority |
|---|---|
| Full-text search across pages | High |
| PostgreSQL / MySQL support | High |
| Live admin preview panel | High |
| Image upload + media manager | Medium |
| Tag and category system | Medium |
| RSS / sitemap generation | Medium |
| Plugin hook system (before/after render) | Medium |
| Multi-language content support | Medium |
| Role-based access control | Medium |
| Static site export (SSG mode) | Low |
| CLI scaffolding for custom plugins | Low |
| VS Code / Obsidian extension | Low |

---

## Tech Stack

| Component | Technology |
|---|---|
| Web framework | [FastHTML](https://fastht.ml) |
| Interactivity | [HTMX](https://htmx.org) |
| Markdown parsing | [markdown-it-py](https://markdown-it-py.readthedocs.io) |
| Database ORM | [SQLAlchemy](https://sqlalchemy.org) |
| Auth | python-jose + passlib |
| Build | [Hatchling](https://hatch.pypa.io) |

---

## Development

```bash
git clone https://github.com/rakeshpatil1983/markdown-cms
cd markdown-cms
pip install -e ".[dev]"
pre-commit install
pytest
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Contributing

Contributions welcome. Please open an issue before submitting large changes.

> Markdown describes structure and intent. Python executes behavior and truth.
