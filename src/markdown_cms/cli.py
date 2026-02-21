"""Command Line Interface for Markdown CMS."""

import argparse
import os
from pathlib import Path


def create_project(name: str):
    """Create a new Markdown CMS project."""

    project_path = Path(name)

    if project_path.exists():
        print(f"X Project '{name}' already exists!")
        return False

    # Create Django-like project structure
    project_path.mkdir(exist_ok=True)
    (project_path / "templates").mkdir(exist_ok=True)
    (project_path / "components").mkdir(exist_ok=True)
    (project_path / "components" / "elements").mkdir(exist_ok=True)
    (project_path / "components" / "containers").mkdir(exist_ok=True)
    (project_path / "components" / "layout").mkdir(exist_ok=True)
    (project_path / "static" / "css").mkdir(parents=True, exist_ok=True)
    (project_path / "static" / "js").mkdir(exist_ok=True)
    (project_path / "static" / "images").mkdir(exist_ok=True)
    (project_path / "pages").mkdir(exist_ok=True)
    (project_path / "apps").mkdir(exist_ok=True)
    (project_path / "plugins").mkdir(exist_ok=True)
    (project_path / "themes").mkdir(exist_ok=True)

    # Create sample content
    create_sample_content(project_path)
    create_template_parts(project_path)
    create_component_examples(project_path)
    create_theme_examples(project_path)
    create_syntax_config(project_path)

    print(f"+ Project '{name}' created successfully!")
    print(f"> Path: {project_path.absolute()}")
    print("> Structure:")
    print(f"   {name}/")
    print("   - templates/     (Template parts: header, footer, navbar, etc.)")
    print("   - static/        (CSS, JS, images)")
    print("   - pages/         (Page content .md files)")
    print("   - apps/          (Custom applications)")
    print("   - plugins/       (Custom plugins)")
    print("> Next steps:")
    print(f"   cd {name}")
    print("   markdown-cms run")

    return True


def create_sample_content(project_path: Path):
    """Create sample markdown content for new projects."""

    # Index page
    index_content = """:::meta
Title: Welcome
Layout: default
:::

# Markdown CMS

Build web pages using pure Markdown.

---

## Component Library

Components are organized in 3 levels:

### Level 1: Elements
Basic building blocks - buttons, links, inputs, dropdowns, etc.

[View Elements →](/elements)

### Level 2: Containers
Groups of elements - cards, tabs, sections, etc.

[View Containers →](/containers)

### Level 3: Layout
Page structure - navigation, sidebars, header, footer

[View Layout →](/layout)

---

## Quick Examples

### Create a Button

**Pure text syntax:**
```
=> Click Me
=> Save (success)
=> Delete (danger)
```

**Result:**

=> Click Me

=> Save (success)

=> Delete (danger)

---

### Create a Card

**Pure text syntax:**
```
:::card
# My Card

This is card content with **markdown** support.

=> Learn More
:::
```

**Result:**

:::card
# My Card

This is card content with **markdown** support.

=> Learn More
:::

---

### Create Form Inputs

**Pure text syntax:**
```
? Your Name (text)
? Your Email (email)
?? Your Message

=> Send
```

**Result:**

? Your Name (text)

? Your Email (email)

?? Your Message

=> Send
"""

    (project_path / "pages" / "index.md").write_text(index_content, encoding="utf-8")

    # Complete Components Library Page
    components_library = """:::meta
Title: Component Library
Layout: default
:::

# 📚 Complete Component Library

> **All components are loaded via HTMX** - Just copy the markdown and use it in your pages!

---

## 🎴 Cards

### Simple Card
<div hx-get="/components/card-simple" hx-trigger="load" hx-swap="innerHTML">Loading...</div>

**How to use:**
```html
<div hx-get="/components/card-simple" hx-trigger="load"></div>
```

---

### Featured Card
<div hx-get="/components/card-featured" hx-trigger="load" hx-swap="innerHTML">Loading...</div>

---

### Pricing Card
<div hx-get="/components/card-pricing" hx-trigger="load" hx-swap="innerHTML">Loading...</div>

---

### Card with Image
<div hx-get="/components/card-image" hx-trigger="load" hx-swap="innerHTML">Loading...</div>

---

## 🔔 Alerts

<div class="row">
  <div class="col-md-6">
    <div hx-get="/components/alert-info" hx-trigger="load" hx-swap="innerHTML">Loading...</div>
  </div>
  <div class="col-md-6">
    <div hx-get="/components/alert-success" hx-trigger="load" hx-swap="innerHTML">Loading...</div>
  </div>
</div>

<div class="row mt-3">
  <div class="col-md-6">
    <div hx-get="/components/alert-warning" hx-trigger="load" hx-swap="innerHTML">Loading...</div>
  </div>
  <div class="col-md-6">
    <div hx-get="/components/alert-danger" hx-trigger="load" hx-swap="innerHTML">Loading...</div>
  </div>
</div>

---

## 🔘 Buttons

<div hx-get="/components/buttons-basic" hx-trigger="load" hx-swap="innerHTML">Loading...</div>

---

## 📊 Tables

### User Table
<div hx-get="/components/table-users" hx-trigger="load" hx-swap="innerHTML">Loading...</div>

---

### Pricing Comparison Table
<div hx-get="/components/table-pricing" hx-trigger="load" hx-swap="innerHTML">Loading...</div>

---

## 📈 Statistics Dashboard

<div hx-get="/components/stats-dashboard" hx-trigger="load" hx-swap="innerHTML">Loading...</div>

---

## 🎯 Hero Sections

### Simple Hero
<div hx-get="/components/hero-simple" hx-trigger="load" hx-swap="innerHTML">Loading...</div>

---

### Gradient Hero
<div hx-get="/components/hero-gradient" hx-trigger="load" hx-swap="innerHTML">Loading...</div>

---

## ⚡ Features Grid

<div hx-get="/components/features-grid" hx-trigger="load" hx-swap="innerHTML">Loading...</div>

---

## 📝 Forms

<div hx-get="/components/form-contact" hx-trigger="load" hx-swap="innerHTML">Loading...</div>

---

## 🏷️ Badges & Labels

<div hx-get="/components/badges" hx-trigger="load" hx-swap="innerHTML">Loading...</div>

---

## ✅ Checklists

<div hx-get="/components/list-checklist" hx-trigger="load" hx-swap="innerHTML">Loading...</div>

---

## 💬 Testimonials

<div hx-get="/components/quote-testimonial" hx-trigger="load" hx-swap="innerHTML">Loading...</div>

---

## 💻 Code Examples

<div hx-get="/components/code-example" hx-trigger="load" hx-swap="innerHTML">Loading...</div>

---

## 🎨 Create Your Own Component

**Step 1:** Create a new markdown file in `components/` folder

```bash
touch components/my-component.md
```

**Step 2:** Write your component in Markdown

```markdown
<!-- components/my-component.md -->

<div class="card">
<div class="card-body">

### My Custom Component

Write content using **Markdown**!

- Lists work
- Images work
- Everything works!

[Button Link](#)

</div>
</div>
```

**Step 3:** Load it anywhere via HTMX

```html
<div hx-get="/components/my-component"
     hx-trigger="load"
     hx-swap="innerHTML">
  Loading...
</div>
```

**That's it!** The component will load dynamically. 🎉

---

## 📖 View Component Source

All component source files are in the `components/` folder:

- `card-simple.md` - Simple card
- `card-featured.md` - Featured card
- `card-pricing.md` - Pricing card
- `alert-info.md` - Info alert
- `buttons-basic.md` - Buttons
- `table-users.md` - User table
- `stats-dashboard.md` - Stats
- `hero-simple.md` - Hero section
- `features-grid.md` - Features grid
- `form-contact.md` - Contact form
- ...and many more!

**Open any file to see the markdown source and copy it!**
"""

    (project_path / "pages" / "components.md").write_text(
        components_library, encoding="utf-8"
    )

    # About page
    about_content = """:::meta
Title: About This Site
Layout: default
:::

# About This Site

This website is powered by the **Markdown-First Application Framework**.

## Technology Stack

- **FastHTML**: Modern Python web framework
- **HTMX**: Progressive enhancement
- **Markdown-it-py**: AST-based parsing
- **SQLite**: Simple file-based database

## Philosophy

> **Markdown describes structure and intent. Python executes behavior and truth.**

This framework maintains a strict separation between declarative Markdown content and imperative Python logic.

## Features

- Write everything in Markdown
- File-based organization
- Template parts (header, footer, navbar, etc.)
- Extensible plugin system
- Auto-reload in development

---

Built with love using Markdown-First Application Framework.
"""

    (project_path / "pages" / "about.md").write_text(about_content, encoding="utf-8")

    # Elements showcase page
    elements_page = """:::meta
Title: Elements
Layout: default
:::

# Level 1: Elements

Basic building blocks - write WHAT you want, not HOW it looks.

---

## Buttons

**Pure text syntax:**
```
=> Click Me
=> Save (success)
=> Delete (danger)
=> Cancel (secondary)
=> Alert (warning)
=> Info (info)
```

**Result:**

=> Click Me

=> Save (success)

=> Delete (danger)

=> Cancel (secondary)

---

## Button Links

**Pure text syntax:**
```
[Home](/) (button)
[Get Started](/start) (button success)
[Learn More](/docs) (button primary)
```

**Result:**

[Home](/) (button)

[Get Started](/start) (button success)

---

## Text Inputs

**Pure text syntax:**
```
? Your Name (text)
? Your Email (email)
? Password (password)
```

**Result:**

? Your Name (text)

? Your Email (email)

? Password (password)

---

## Number Input

**Pure text syntax:**
```
? Age (number 1-100)
? Quantity (number 1-10)
```

**Result:**

? Age (number 1-100)

---

## Range Slider

**Pure text syntax:**
```
? Volume (range 0-100)
```

**Result:**

? Volume (range 0-100)

---

## Textarea

**Pure text syntax:**
```
?? Your message here...
```

**Result:**

?? Your message here...

---

## Dropdown

**Pure text syntax:**
```
Select: Choose an option
```

**Result:**

Select: Choose an option

---

## Alerts

**Pure text syntax:**
```
> [!SUCCESS]
> Your changes saved!

> [!WARNING]
> Please review

> [!ERROR]
> Something went wrong

> [!INFO]
> Helpful information
```

**Result:**

> [!SUCCESS]
> Your changes saved!

> [!WARNING]
> Please review input

> [!ERROR]
> Something went wrong

---

## Text Formatting (Standard Markdown)

**Pure text syntax:**
```
**Bold text**
*Italic text*
***Bold and Italic***
~~Strikethrough~~
`Inline code`
```

**Result:**

**Bold text**
*Italic text*
***Bold and Italic***
~~Strikethrough~~
`Inline code`

---

## Icons (Use Emojis)

**Pure text syntax:**
```
✅ ❌ ⚠️ ℹ️ 🏠 📧 📞 ⚙️ ⭐ ❤️ 📁 🔍
```

**Result:**

✅ Success  ❌ Error  ⚠️ Warning  ℹ️ Info
🏠 Home  📧 Email  📞 Phone  ⚙️ Settings
⭐ Star  ❤️ Heart  📁 Folder  🔍 Search
"""
    (project_path / "pages" / "elements.md").write_text(elements_page, encoding="utf-8")

    # Containers showcase page
    containers_page = """:::meta
Title: Containers
Layout: default
:::

# Level 2: Containers

Components that group elements together - write WHAT you want, not HOW it looks.

---

## Card

**Pure text syntax:**
```
:::card
# Card Title

This is a card body with **markdown** content.

- List item 1
- List item 2

=> Learn More
:::
```

**Result:**

:::card
# Card Title

This is a card body with **markdown** content.

- List item 1
- List item 2

=> Learn More
:::

---

## Card with Header and Footer

**Pure text syntax:**
```
:::card
--- header ---
Featured Item

--- body ---
# Special Offer

Get 50% off today!

=> Claim Offer (success)

--- footer ---
Valid until Dec 31
:::
```

**Result:**

:::card
--- header ---
Featured Item

--- body ---
# Special Offer

Get 50% off today!

=> Claim Offer (success)

--- footer ---
Valid until Dec 31
:::

---

## Panel/Container

**Pure text syntax:**
```
:::panel
# Panel Title

This is a simple panel that groups related content together.

=> Action Button
:::
```

**Result:**

:::panel
# Panel Title

This is a simple panel that groups related content together.

=> Action Button
:::

---

## Section

**Pure text syntax:**
```
:::section
# Section Title

Sections are used to divide content into logical parts.

Each section can contain multiple elements.
:::
```

**Result:**

:::section
# Section Title

Sections are used to divide content into logical parts.

Each section can contain multiple elements.
:::

---

## Stats Dashboard

**Pure text syntax:**
```
:::stats
1,234 | Total Users | ↑ 12% growth
567 | Active Now | 🟢 Online
89% | Success Rate | ↑ 5% better
:::
```

**Result:**

:::stats
1,234 | Total Users | ↑ 12% growth
567 | Active Now | 🟢 Online
89% | Success Rate | ↑ 5% better
:::
"""
    (project_path / "pages" / "containers.md").write_text(
        containers_page, encoding="utf-8"
    )

    # Layout showcase page
    layout_page = """:::meta
Title: Layout
Layout: default
:::

# Level 3: Layout

Page structure and navigation components - write WHAT you want, not HOW it looks.

---

## Two Column Layout

**Pure text syntax:**
```
:::columns 2
### Left Column

This is the left side content.

=> Action Left

---

### Right Column

This is the right side content.

=> Action Right
:::
```

**Result:**

:::columns 2
### Left Column

This is the left side content.

=> Action Left

---

### Right Column

This is the right side content.

=> Action Right
:::

---

## Three Column Layout

**Pure text syntax:**
```
:::columns 3
:::card
# Column 1
First card
=> View
:::
---
:::card
# Column 2
Second card
=> View
:::
---
:::card
# Column 3
Third card
=> View
:::
:::
```

**Result:**

:::columns 3
:::card
# Column 1
First card
=> View
:::
---
:::card
# Column 2
Second card
=> View
:::
---
:::card
# Column 3
Third card
=> View
:::
:::

---

## Sidebar with Card

**Pure text syntax:**
```
:::card
# Quick Links

- [Documentation](#)
- [API Reference](#)
- [Support](#)

=> Learn More
:::
```

**Result:**

:::card
# Quick Links

- [Documentation](#)
- [API Reference](#)
- [Support](#)

=> Learn More
:::

---

## Header Section

**Pure text syntax:**
```
:::section
# My Website

### Tagline or description goes here

=> Get Started (success)
:::
```

**Result:**

:::section
# My Website

### Tagline or description goes here

=> Get Started (success)
:::

---

## Footer Content

**Pure text syntax:**
```
© 2026 My Website | [Privacy](#) | [Terms](#)
```

**Result:**

© 2026 My Website | [Privacy](#) | [Terms](#)

---

**Note:** Layout templates (navbar, sidenav, header, footer) are configured in the `templates/` directory using the same pure text syntax. The layout system uses HTMX to load these components dynamically.
"""
    (project_path / "pages" / "layout.md").write_text(layout_page, encoding="utf-8")

    # Default CSS theme
    css_content = """/* Default theme for Markdown-First Application Framework */

/* CSS Reset */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* Base Styles */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #fff;
}

/* Layout */
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Header */
.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.header h1 {
    font-size: 1.8rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.header nav ul {
    list-style: none;
    display: flex;
    gap: 2rem;
    flex-wrap: wrap;
}

.header nav a {
    color: white;
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    transition: all 0.2s;
}

.header nav a:hover {
    background: rgba(255,255,255,0.1);
    transform: translateY(-1px);
}

/* Main Layout */
.main-layout {
    display: grid;
    grid-template-columns: 250px 1fr;
    gap: 2rem;
    margin-top: 2rem;
}

.content {
    min-width: 0;
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.sidebar {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 12px;
    height: fit-content;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    margin-bottom: 1rem;
    font-weight: 600;
    line-height: 1.3;
}

h1 {
    font-size: 2.5rem;
    color: #2c3e50;
    margin-bottom: 1.5rem;
}
h2 {
    font-size: 2rem;
    color: #34495e;
    margin-top: 2rem;
}
h3 {
    font-size: 1.5rem;
    color: #34495e;
}
h4 { font-size: 1.25rem; }
h5 { font-size: 1.1rem; }
h6 { font-size: 1rem; }

p {
    margin-bottom: 1rem;
    color: #555;
}

a {
    color: #3498db;
    text-decoration: none;
    border-bottom: 1px solid transparent;
    transition: border-color 0.2s;
}

a:hover {
    border-bottom-color: #3498db;
}

/* Code */
code {
    background: #f1f3f5;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-family: 'Monaco', 'Menlo', monospace;
    font-size: 0.9rem;
    color: #e74c3c;
}

pre {
    background: #2c3e50;
    color: #ecf0f1;
    padding: 1.5rem;
    border-radius: 8px;
    overflow-x: auto;
    margin-bottom: 1rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

pre code {
    background: none;
    padding: 0;
    color: inherit;
}

/* Blockquotes */
blockquote {
    border-left: 4px solid #3498db;
    padding-left: 1rem;
    margin: 1rem 0;
    font-style: italic;
    color: #666;
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 0 8px 8px 0;
}

/* Lists */
ul, ol {
    margin-bottom: 1rem;
    padding-left: 2rem;
}

li {
    margin-bottom: 0.5rem;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 1rem;
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

th, td {
    padding: 1rem;
    text-align: left;
    border-bottom: 1px solid #e1e4e8;
}

th {
    background: #f6f8fa;
    font-weight: 600;
    color: #24292e;
}

/* Hero section */
.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 3rem 2rem;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 2rem;
}

.hero h1 {
    color: white;
    margin-bottom: 1rem;
}

/* Feature cards */
.features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}

.feature {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
    border-left: 4px solid #3498db;
}

/* Responsive Design */
@media (max-width: 768px) {
    .main-layout {
        grid-template-columns: 1fr;
    }

    .sidebar {
        margin-top: 2rem;
    }

    .header nav ul {
        flex-direction: column;
        gap: 0.5rem;
    }

    h1 { font-size: 2rem; }
    h2 { font-size: 1.5rem; }

    .content {
        padding: 1rem;
    }
}

/* Dark Mode Support */
@media (prefers-color-scheme: dark) {
    body {
        background-color: #1a1a1a;
        color: #e0e0e0;
    }

    .content {
        background: #2d2d2d;
        color: #e0e0e0;
    }

    .sidebar {
        background: #242424;
    }

    code {
        background: #3d3d3d;
        color: #ff6b6b;
    }

    th {
        background: #3d3d3d;
        color: #e0e0e0;
    }
}

/* ============ COMPONENT STYLES (Bootstrap-compatible) ============ */

/* Buttons */
.btn {
    display: inline-block;
    padding: 0.5rem 1rem;
    font-size: 1rem;
    font-weight: 500;
    line-height: 1.5;
    text-align: center;
    text-decoration: none;
    vertical-align: middle;
    cursor: pointer;
    user-select: none;
    border: 1px solid transparent;
    border-radius: 6px;
    transition: all 0.2s ease-in-out;
    margin: 0.25rem;
}

.btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.btn:active {
    transform: translateY(0);
}

.btn-primary {
    background-color: #3498db;
    border-color: #3498db;
    color: white;
}

.btn-primary:hover {
    background-color: #2980b9;
    border-color: #2980b9;
}

.btn-success {
    background-color: #27ae60;
    border-color: #27ae60;
    color: white;
}

.btn-success:hover {
    background-color: #229954;
    border-color: #229954;
}

.btn-danger {
    background-color: #e74c3c;
    border-color: #e74c3c;
    color: white;
}

.btn-danger:hover {
    background-color: #c0392b;
    border-color: #c0392b;
}

.btn-warning {
    background-color: #f39c12;
    border-color: #f39c12;
    color: white;
}

.btn-warning:hover {
    background-color: #e67e22;
    border-color: #e67e22;
}

.btn-info {
    background-color: #3498db;
    border-color: #3498db;
    color: white;
}

.btn-info:hover {
    background-color: #2980b9;
    border-color: #2980b9;
}

.btn-secondary {
    background-color: #95a5a6;
    border-color: #95a5a6;
    color: white;
}

.btn-secondary:hover {
    background-color: #7f8c8d;
    border-color: #7f8c8d;
}

/* Cards */
.card {
    background: white;
    border: 1px solid #e1e4e8;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    overflow: hidden;
}

.card-header {
    padding: 1rem 1.5rem;
    background: #f6f8fa;
    border-bottom: 1px solid #e1e4e8;
    font-weight: 600;
    color: #24292e;
}

.card-body {
    padding: 1.5rem;
}

.card-footer {
    padding: 1rem 1.5rem;
    background: #f6f8fa;
    border-top: 1px solid #e1e4e8;
    color: #666;
}

/* Form Controls */
.form-control {
    display: block;
    width: 100%;
    padding: 0.5rem 0.75rem;
    font-size: 1rem;
    line-height: 1.5;
    color: #333;
    background-color: #fff;
    border: 1px solid #d1d5da;
    border-radius: 6px;
    transition: border-color 0.2s;
    margin-bottom: 0.5rem;
}

.form-control:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #24292e;
}

.form-select {
    display: block;
    width: 100%;
    padding: 0.5rem 2.25rem 0.5rem 0.75rem;
    font-size: 1rem;
    line-height: 1.5;
    color: #333;
    background-color: #fff;
    border: 1px solid #d1d5da;
    border-radius: 6px;
    transition: border-color 0.2s;
}

.mb-3 {
    margin-bottom: 1rem;
}

/* Alerts */
.alert {
    padding: 1rem 1.5rem;
    margin-bottom: 1rem;
    border: 1px solid transparent;
    border-radius: 6px;
    font-size: 1rem;
}

.alert-success {
    background-color: #d4edda;
    border-color: #c3e6cb;
    color: #155724;
}

.alert-warning {
    background-color: #fff3cd;
    border-color: #ffeaa7;
    color: #856404;
}

.alert-danger {
    background-color: #f8d7da;
    border-color: #f5c6cb;
    color: #721c24;
}

.alert-info {
    background-color: #d1ecf1;
    border-color: #bee5eb;
    color: #0c5460;
}

/* Grid System */
.row {
    display: flex;
    flex-wrap: wrap;
    margin: 0 -0.75rem;
}

.col-md-6 {
    flex: 0 0 50%;
    max-width: 50%;
    padding: 0 0.75rem;
}

.col-md-4 {
    flex: 0 0 33.333333%;
    max-width: 33.333333%;
    padding: 0 0.75rem;
}

.col-md-12 {
    flex: 0 0 100%;
    max-width: 100%;
    padding: 0 0.75rem;
}

@media (max-width: 768px) {
    .col-md-6, .col-md-4 {
        flex: 0 0 100%;
        max-width: 100%;
    }
}

/* Stats Dashboard */
.stats {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    margin: 1.5rem 0;
}

.stat {
    flex: 1;
    min-width: 200px;
    padding: 1.5rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 8px;
    text-align: center;
    color: white;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.stat h3 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    color: white;
}

.stat p {
    margin: 0;
    color: rgba(255,255,255,0.9);
}

/* Panel/Container */
.panel, .container-fluid {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    border: 1px solid #e1e4e8;
}

/* Carousel */
.carousel {
    position: relative;
    margin-bottom: 2rem;
    background: #f8f9fa;
    border-radius: 8px;
    overflow: hidden;
    min-height: 300px;
}

.carousel-inner {
    position: relative;
    width: 100%;
    overflow: hidden;
    min-height: 300px;
}

.carousel-item {
    position: relative;
    display: none;
    float: left;
    width: 100%;
    margin-right: -100%;
    backface-visibility: hidden;
    transition: transform 0.6s ease-in-out;
    min-height: 300px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
}

.carousel-item.active {
    display: flex;
}

.carousel-caption {
    position: relative;
    padding: 2rem;
    color: white;
    text-align: center;
}

.carousel-caption h1,
.carousel-caption h2,
.carousel-caption h3 {
    color: white;
}

.carousel-indicators {
    position: absolute;
    right: 0;
    bottom: 0;
    left: 0;
    z-index: 2;
    display: flex;
    justify-content: center;
    padding: 0;
    margin-right: 15%;
    margin-bottom: 1rem;
    margin-left: 15%;
    list-style: none;
}

.carousel-indicators button {
    box-sizing: content-box;
    flex: 0 1 auto;
    width: 30px;
    height: 3px;
    padding: 0;
    margin-right: 3px;
    margin-left: 3px;
    text-indent: -999px;
    cursor: pointer;
    background-color: #fff;
    background-clip: padding-box;
    border: 0;
    border-top: 10px solid transparent;
    border-bottom: 10px solid transparent;
    opacity: 0.5;
    transition: opacity 0.6s ease;
}

.carousel-indicators button.active {
    opacity: 1;
}

.carousel-control-prev,
.carousel-control-next {
    position: absolute;
    top: 0;
    bottom: 0;
    z-index: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 15%;
    padding: 0;
    color: #fff;
    text-align: center;
    background: none;
    border: 0;
    opacity: 0.5;
    transition: opacity 0.15s ease;
    cursor: pointer;
}

.carousel-control-prev:hover,
.carousel-control-next:hover {
    opacity: 0.9;
}

.carousel-control-prev {
    left: 0;
}

.carousel-control-next {
    right: 0;
}

.carousel-control-prev-icon,
.carousel-control-next-icon {
    display: inline-block;
    width: 2rem;
    height: 2rem;
    background-repeat: no-repeat;
    background-position: 50%;
    background-size: 100% 100%;
}

.carousel-control-prev-icon {
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='%23fff'%3e%3cpath d='M11.354 1.646a.5.5 0 0 1 0 .708L5.707 8l5.647 5.646a.5.5 0 0 1-.708.708l-6-6a.5.5 0 0 1 0-.708l6-6a.5.5 0 0 1 .708 0z'/%3e%3c/svg%3e");
}

.carousel-control-next-icon {
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='%23fff'%3e%3cpath d='M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z'/%3e%3c/svg%3e");
}

.visually-hidden {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}
"""

    (project_path / "static" / "css" / "styles.css").write_text(
        css_content, encoding="utf-8"
    )


def create_template_parts(project_path: Path):
    """Create WordPress-like template parts."""

    # Header template
    header_content = """# Site Header

**Markdown CMS** - Your Markdown-First Framework
"""
    (project_path / "templates" / "header.md").write_text(
        header_content, encoding="utf-8"
    )

    # Navbar template
    navbar_content = """# Navigation

- [Home](/)
- [About](/about)
- [Docs](/docs)
- [Examples](/examples)
"""
    (project_path / "templates" / "navbar.md").write_text(
        navbar_content, encoding="utf-8"
    )

    # Sidebar navigation template
    sidenav_content = """# Quick Links

- [Getting Started](/docs/intro)
- [Components](/examples)
- [API Reference](/docs/api)

## Resources

- [GitHub](https://github.com/rakeshpatil1983/markdown-cms)
- [Documentation](/docs)
"""
    (project_path / "templates" / "sidenav.md").write_text(
        sidenav_content, encoding="utf-8"
    )

    # Footer template
    footer_content = """---

Made with Markdown CMS | 2026
"""
    (project_path / "templates" / "footer.md").write_text(
        footer_content, encoding="utf-8"
    )

    # Hero template
    hero_content = """# Welcome to Markdown CMS!

Build amazing websites with just Markdown
"""
    (project_path / "templates" / "hero.md").write_text(hero_content, encoding="utf-8")

    # Breadcrumb template
    breadcrumb_content = """Home > Current Page"""
    (project_path / "templates" / "breadcrumb.md").write_text(
        breadcrumb_content, encoding="utf-8"
    )


def create_component_examples(project_path: Path):
    """Create components organized in a 3-level hierarchy."""

    # ========== LEVEL 1: BASIC ELEMENTS ==========

    # Links
    elem_links = """<!-- Links Component -->

<div class="p-3">

## Links Examples

[Simple Link](#)

[Primary Button Link](#){: .btn .btn-primary}

[Secondary Button Link](#){: .btn .btn-secondary}

<a href="#" class="btn btn-success">Success Link</a>

</div>"""
    (project_path / "components" / "elements" / "links.md").write_text(
        elem_links, encoding="utf-8"
    )

    # Buttons
    elem_buttons = """<!-- Buttons Component -->

<div class="p-3">

## Button Examples

<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-success">Success</button>
<button class="btn btn-danger">Danger</button>
<button class="btn btn-warning">Warning</button>
<button class="btn btn-info">Info</button>

</div>"""
    (project_path / "components" / "elements" / "buttons.md").write_text(
        elem_buttons, encoding="utf-8"
    )

    # Text Input
    elem_input_text = """<!-- Text Input Component -->

<div class="p-3">

## Text Input

<div class="mb-3">
  <label class="form-label">Name</label>
  <input type="text" class="form-control" placeholder="Enter your name">
</div>

<div class="mb-3">
  <label class="form-label">Email</label>
  <input type="email" class="form-control" placeholder="your@email.com">
</div>

<div class="mb-3">
  <label class="form-label">Password</label>
  <input type="password" class="form-control">
</div>

</div>"""
    (project_path / "components" / "elements" / "input-text.md").write_text(
        elem_input_text, encoding="utf-8"
    )

    # Number Input
    elem_input_number = """<!-- Number Input Component -->

<div class="p-3">

## Number Input

<div class="mb-3">
  <label class="form-label">Quantity</label>
  <input type="number" class="form-control" value="1" min="1" max="100">
</div>

</div>"""
    (project_path / "components" / "elements" / "input-number.md").write_text(
        elem_input_number, encoding="utf-8"
    )

    # Range Input
    elem_input_range = """<!-- Range Slider Component -->

<div class="p-3">

## Range Slider

<div class="mb-3">
  <label class="form-label">Volume: <span id="rangeValue">50</span></label>
  <input type="range" class="form-range" min="0" max="100" value="50">
</div>

</div>"""
    (project_path / "components" / "elements" / "input-range.md").write_text(
        elem_input_range, encoding="utf-8"
    )

    # Textarea
    elem_textarea = """<!-- Textarea Component -->

<div class="p-3">

## Textarea

<div class="mb-3">
  <label class="form-label">Message</label>
  <textarea class="form-control" rows="4" placeholder="Enter your message here..."></textarea>
</div>

</div>"""
    (project_path / "components" / "elements" / "textarea.md").write_text(
        elem_textarea, encoding="utf-8"
    )

    # Paragraphs
    elem_paragraphs = """<!-- Paragraphs Component -->

<div class="p-3">

## Paragraphs

This is a regular paragraph with some **bold text** and *italic text*.

This is another paragraph with a [link](#) embedded in it.

> This is a blockquote paragraph with special formatting.

</div>"""
    (project_path / "components" / "elements" / "paragraphs.md").write_text(
        elem_paragraphs, encoding="utf-8"
    )

    # Text Formatting
    elem_text_format = """<!-- Text Formatting Component -->

<div class="p-3">

## Text Formatting

**Bold text** using markdown

*Italic text* using markdown

***Bold and Italic***

~~Strikethrough text~~

`Inline code`

</div>"""
    (project_path / "components" / "elements" / "text-format.md").write_text(
        elem_text_format, encoding="utf-8"
    )

    # Dropdown
    elem_dropdown = """<!-- Dropdown Component -->

<div class="p-3">

## Dropdown Select

<div class="mb-3">
  <label class="form-label">Choose an option</label>
  <select class="form-select">
    <option selected>Select one...</option>
    <option value="1">Option 1</option>
    <option value="2">Option 2</option>
    <option value="3">Option 3</option>
  </select>
</div>

</div>"""
    (project_path / "components" / "elements" / "dropdown.md").write_text(
        elem_dropdown, encoding="utf-8"
    )

    # Icons (using emojis for simplicity)
    elem_icons = """<!-- Icons Component -->

<div class="p-3">

## Icons (Using Emojis)

✅ Success  ❌ Error  ⚠️ Warning  ℹ️ Info

🏠 Home  📧 Email  📞 Phone  ⚙️ Settings

⭐ Star  ❤️ Heart  📁 Folder  🔍 Search

</div>"""
    (project_path / "components" / "elements" / "icons.md").write_text(
        elem_icons, encoding="utf-8"
    )

    # ========== LEVEL 2: CONTAINERS ==========

    # Card
    cont_card = """<!-- Card Container -->

<div class="card">
<div class="card-header">
### Card Header
</div>
<div class="card-body">

## Card Title

This is a card body with **markdown** content.

- List item 1
- List item 2
- List item 3

[Button](#){: .btn .btn-primary}

</div>
<div class="card-footer text-muted">
Card footer
</div>
</div>"""
    (project_path / "components" / "containers" / "card.md").write_text(
        cont_card, encoding="utf-8"
    )

    # Container/Panel
    cont_container = """<!-- Container Panel -->

<div class="container p-4 bg-light rounded">

## Container Panel

This is a simple container/panel that groups related content together.

Content inside the container is organized and styled consistently.

[Action Button](#){: .btn .btn-primary}

</div>"""
    (project_path / "components" / "containers" / "container.md").write_text(
        cont_container, encoding="utf-8"
    )

    # Section
    cont_section = """<!-- Section Container -->

<section class="p-4 border-bottom">

## Section Title

Sections are used to divide content into logical parts.

Each section can contain multiple elements and maintain consistent spacing.

</section>"""
    (project_path / "components" / "containers" / "section.md").write_text(
        cont_section, encoding="utf-8"
    )

    # Tabs
    cont_tabs = """<!-- Tabs Container -->

<div class="p-3">

## Tabs Example

<ul class="nav nav-tabs" role="tablist">
  <li class="nav-item">
    <a class="nav-link active">Tab 1</a>
  </li>
  <li class="nav-item">
    <a class="nav-link">Tab 2</a>
  </li>
  <li class="nav-item">
    <a class="nav-link">Tab 3</a>
  </li>
</ul>

<div class="tab-content p-3 border border-top-0">
Content for the active tab goes here.
</div>

</div>"""
    (project_path / "components" / "containers" / "tabs.md").write_text(
        cont_tabs, encoding="utf-8"
    )

    # ========== LEVEL 3: LAYOUT/NAVIGATION ==========

    # Top Navbar
    layout_navbar = """<!-- Top Navbar Layout -->

<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
<div class="container-fluid">
<a class="navbar-brand" href="#">Brand</a>
<ul class="navbar-nav">
<li class="nav-item"><a class="nav-link active" href="/">Home</a></li>
<li class="nav-item"><a class="nav-link" href="/about">About</a></li>
<li class="nav-item"><a class="nav-link" href="/contact">Contact</a></li>
</ul>
</div>
</nav>"""
    (project_path / "components" / "layout" / "navbar-top.md").write_text(
        layout_navbar, encoding="utf-8"
    )

    # Left Sidenav
    layout_sidenav_left = """<!-- Left Sidenav Layout -->

<div class="list-group">
<a href="/" class="list-group-item list-group-item-action active">
Home
</a>
<a href="/elements" class="list-group-item list-group-item-action">
Elements
</a>
<a href="/containers" class="list-group-item list-group-item-action">
Containers
</a>
<a href="/layout" class="list-group-item list-group-item-action">
Layout
</a>
</div>"""
    (project_path / "components" / "layout" / "sidenav-left.md").write_text(
        layout_sidenav_left, encoding="utf-8"
    )

    # Right Sidebar
    layout_sidebar_right = """<!-- Right Sidebar Layout -->

<div class="card">
<div class="card-body">

### Quick Links

- [Documentation](#)
- [API Reference](#)
- [Support](#)

</div>
</div>

<div class="card mt-3">
<div class="card-body">

### Resources

- [GitHub](#)
- [Community](#)

</div>
</div>"""
    (project_path / "components" / "layout" / "sidebar-right.md").write_text(
        layout_sidebar_right, encoding="utf-8"
    )

    # Header
    layout_header = """<!-- Header Layout -->

<div class="bg-light p-4 text-center">

# My Website

### Tagline or description goes here

</div>"""
    (project_path / "components" / "layout" / "header.md").write_text(
        layout_header, encoding="utf-8"
    )

    # Footer
    layout_footer = """<!-- Footer Layout -->

<footer class="bg-dark text-white p-4 mt-5">
<div class="container text-center">

© 2026 My Website | [Privacy](#) | [Terms](#)

</div>
</footer>"""
    (project_path / "components" / "layout" / "footer.md").write_text(
        layout_footer, encoding="utf-8"
    )

    # Create README explaining the hierarchy
    readme = """# Component Library - Hierarchical Structure

Components are organized in 3 levels:

## Level 1: Elements (`components/elements/`)

Basic building blocks of your UI:

- `links.md` - Hyperlinks and link buttons
- `buttons.md` - Button elements
- `input-text.md` - Text, email, password inputs
- `input-number.md` - Number inputs
- `input-range.md` - Range sliders
- `textarea.md` - Multi-line text areas
- `paragraphs.md` - Text paragraphs
- `text-format.md` - Bold, italic, strikethrough
- `dropdown.md` - Select dropdowns
- `icons.md` - Icon examples

## Level 2: Containers (`components/containers/`)

Components that group elements:

- `card.md` - Card containers
- `container.md` - Panel containers
- `section.md` - Section dividers
- `tabs.md` - Tabbed interfaces

## Level 3: Layout (`components/layout/`)

Page structure and navigation:

- `navbar-top.md` - Top navigation bar
- `sidenav-left.md` - Left sidebar navigation
- `sidebar-right.md` - Right sidebar
- `header.md` - Page header
- `footer.md` - Page footer

## Usage

Load any component using HTMX:

```html
<div hx-get="/components/elements/buttons" hx-trigger="load"></div>
<div hx-get="/components/containers/card" hx-trigger="load"></div>
<div hx-get="/components/layout/navbar-top" hx-trigger="load"></div>
```

##Create Your Own

1. Choose the appropriate level folder
2. Create a `.md` file
3. Write your component with HTML + Markdown
4. Load it with HTMX
"""
    (project_path / "components" / "README.md").write_text(readme, encoding="utf-8")


def create_theme_examples(project_path: Path):
    """Create theme examples using Bootstrap, Materialize, Bulma, and Tailwind."""

    # Create theme directories
    for theme in ["bootstrap", "materialize", "bulma", "tailwind"]:
        (project_path / "themes" / theme / "templates").mkdir(
            parents=True, exist_ok=True
        )
        (project_path / "themes" / theme / "static" / "css").mkdir(
            parents=True, exist_ok=True
        )

    # ==================== BOOTSTRAP THEME ====================
    bootstrap_header = """# Bootstrap Site

**Powered by Markdown CMS**

<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
  <div class="container">
    <a class="navbar-brand" href="/">Markdown CMS</a>
  </div>
</nav>"""
    (project_path / "themes" / "bootstrap" / "templates" / "header.md").write_text(
        bootstrap_header, encoding="utf-8"
    )

    bootstrap_navbar = """<ul class="nav nav-pills">
  <li class="nav-item"><a class="nav-link active" href="/">Home</a></li>
  <li class="nav-item"><a class="nav-link" href="/about">About</a></li>
  <li class="nav-item"><a class="nav-link" href="/docs">Docs</a></li>
</ul>"""
    (project_path / "themes" / "bootstrap" / "templates" / "navbar.md").write_text(
        bootstrap_navbar, encoding="utf-8"
    )

    bootstrap_sidenav = """<div class="card">
<div class="card-body">

### Quick Links

- [Getting Started](/docs/intro)
- [Components](/examples)
- [API Reference](/docs/api)

</div>
</div>

<div class="card mt-3">
<div class="card-body">

### Resources

- [GitHub](https://github.com/rakeshpatil1983/markdown-cms)
- [Documentation](/docs)

</div>
</div>"""
    (project_path / "themes" / "bootstrap" / "templates" / "sidenav.md").write_text(
        bootstrap_sidenav, encoding="utf-8"
    )

    bootstrap_footer = """<footer class="bg-light py-4 mt-5">
<div class="container text-center">

Made with **Markdown CMS** | 2026

[Home](/) | [About](/about) | [Docs](/docs)

</div>
</footer>"""
    (project_path / "themes" / "bootstrap" / "templates" / "footer.md").write_text(
        bootstrap_footer, encoding="utf-8"
    )

    bootstrap_css = """/* Bootstrap Theme CSS */
@import url('https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css');

/* Layout Classes */
.header {
    background: #fff;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 2rem;
}

.main {
    min-height: calc(100vh - 300px);
}

.main-layout {
    display: grid;
    grid-template-columns: 250px 1fr;
    gap: 2rem;
}

.content {
    background: #fff;
    padding: 2rem;
    border-radius: 8px;
}

.sidebar {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    height: fit-content;
}

/* Component Classes */
.card { margin-bottom: 1rem; }
.stats { display: flex; gap: 1rem; flex-wrap: wrap; }
.stat { flex: 1; min-width: 200px; padding: 1rem; background: #f8f9fa; border-radius: 8px; text-align: center; }

/* Responsive */
@media (max-width: 768px) {
    .main-layout {
        grid-template-columns: 1fr;
    }
}"""
    (project_path / "themes" / "bootstrap" / "static" / "css" / "theme.css").write_text(
        bootstrap_css, encoding="utf-8"
    )

    # ==================== MATERIALIZE THEME ====================
    materialize_header = """# Materialize Site

**Material Design with Markdown**

<nav class="blue darken-2">
  <div class="nav-wrapper container">
    <a href="/" class="brand-logo">Markdown CMS</a>
  </div>
</nav>"""
    (project_path / "themes" / "materialize" / "templates" / "header.md").write_text(
        materialize_header, encoding="utf-8"
    )

    materialize_navbar = """<ul class="tabs">
  <li class="tab"><a class="active" href="/">Home</a></li>
  <li class="tab"><a href="/about">About</a></li>
  <li class="tab"><a href="/docs">Docs</a></li>
</ul>"""
    (project_path / "themes" / "materialize" / "templates" / "navbar.md").write_text(
        materialize_navbar, encoding="utf-8"
    )

    materialize_sidenav = """<div class="card">
<div class="card-content">

### Quick Links

- [Getting Started](/docs/intro)
- [Components](/examples)
- [API Reference](/docs/api)

</div>
</div>

<div class="card">
<div class="card-content">

### Resources

- [GitHub](https://github.com/rakeshpatil1983/markdown-cms)
- [Documentation](/docs)

</div>
</div>"""
    (project_path / "themes" / "materialize" / "templates" / "sidenav.md").write_text(
        materialize_sidenav, encoding="utf-8"
    )

    materialize_footer = """<footer class="page-footer blue">
<div class="container">
<div class="row">
<div class="col s12 center-align">

Made with **Markdown CMS** | 2026

[Home](/) | [About](/about) | [Docs](/docs)

</div>
</div>
</div>
</footer>"""
    (project_path / "themes" / "materialize" / "templates" / "footer.md").write_text(
        materialize_footer, encoding="utf-8"
    )

    materialize_css = """/* Materialize Theme CSS */
@import url('https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css');

/* Layout Classes */
.header { background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 2rem; }
.main { min-height: calc(100vh - 300px); }
.main-layout { display: grid; grid-template-columns: 250px 1fr; gap: 2rem; }
.content { background: #fff; padding: 2rem; border-radius: 4px; }
.sidebar { background: #f5f5f5; padding: 1rem; border-radius: 4px; height: fit-content; }

/* Component Classes */
.stats { display: flex; gap: 1rem; flex-wrap: wrap; }
.stat { flex: 1; min-width: 200px; padding: 1rem; background: #f5f5f5; border-radius: 4px; text-align: center; }

@media (max-width: 768px) { .main-layout { grid-template-columns: 1fr; } }"""
    (
        project_path / "themes" / "materialize" / "static" / "css" / "theme.css"
    ).write_text(materialize_css, encoding="utf-8")

    # ==================== BULMA THEME ====================
    bulma_header = """# Bulma Site

**Clean CSS Framework**

<nav class="navbar is-primary">
  <div class="navbar-brand">
    <a class="navbar-item" href="/">
      <strong>Markdown CMS</strong>
    </a>
  </div>
</nav>"""
    (project_path / "themes" / "bulma" / "templates" / "header.md").write_text(
        bulma_header, encoding="utf-8"
    )

    bulma_navbar = """<div class="tabs is-centered">
  <ul>
    <li class="is-active"><a href="/">Home</a></li>
    <li><a href="/about">About</a></li>
    <li><a href="/docs">Docs</a></li>
  </ul>
</div>"""
    (project_path / "themes" / "bulma" / "templates" / "navbar.md").write_text(
        bulma_navbar, encoding="utf-8"
    )

    bulma_sidenav = """<div class="box">

### Quick Links

- [Getting Started](/docs/intro)
- [Components](/examples)
- [API Reference](/docs/api)

</div>

<div class="box">

### Resources

- [GitHub](https://github.com/rakeshpatil1983/markdown-cms)
- [Documentation](/docs)

</div>"""
    (project_path / "themes" / "bulma" / "templates" / "sidenav.md").write_text(
        bulma_sidenav, encoding="utf-8"
    )

    bulma_footer = """<footer class="footer">
<div class="content has-text-centered">

Made with **Markdown CMS** | 2026

[Home](/) | [About](/about) | [Docs](/docs)

</div>
</footer>"""
    (project_path / "themes" / "bulma" / "templates" / "footer.md").write_text(
        bulma_footer, encoding="utf-8"
    )

    bulma_css = """/* Bulma Theme CSS */
@import url('https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css');

/* Layout Classes */
.header { background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 2rem; }
.main { min-height: calc(100vh - 300px); }
.main-layout { display: grid; grid-template-columns: 250px 1fr; gap: 2rem; }
.content { background: #fff; padding: 2rem; border-radius: 6px; }
.sidebar { background: #f5f5f5; padding: 1rem; border-radius: 6px; height: fit-content; }

/* Component Classes */
.card { margin-bottom: 1rem; }
.stats { display: flex; gap: 1rem; flex-wrap: wrap; }
.stat { flex: 1; min-width: 200px; padding: 1rem; background: #f5f5f5; border-radius: 6px; text-align: center; }

@media (max-width: 768px) { .main-layout { grid-template-columns: 1fr; } }"""
    (project_path / "themes" / "bulma" / "static" / "css" / "theme.css").write_text(
        bulma_css, encoding="utf-8"
    )

    # ==================== TAILWIND THEME ====================
    tailwind_header = """# Tailwind Site

**Utility-First CSS**

<nav class="bg-blue-600 text-white p-4">
  <div class="container mx-auto">
    <a href="/" class="text-xl font-bold">Markdown CMS</a>
  </div>
</nav>"""
    (project_path / "themes" / "tailwind" / "templates" / "header.md").write_text(
        tailwind_header, encoding="utf-8"
    )

    tailwind_navbar = """<ul class="flex space-x-4 border-b">
  <li><a href="/" class="px-4 py-2 bg-blue-500 text-white rounded-t">Home</a></li>
  <li><a href="/about" class="px-4 py-2 hover:bg-gray-100">About</a></li>
  <li><a href="/docs" class="px-4 py-2 hover:bg-gray-100">Docs</a></li>
</ul>"""
    (project_path / "themes" / "tailwind" / "templates" / "navbar.md").write_text(
        tailwind_navbar, encoding="utf-8"
    )

    tailwind_sidenav = """<div class="bg-white p-4 rounded-lg shadow mb-4">

### Quick Links

- [Getting Started](/docs/intro)
- [Components](/examples)
- [API Reference](/docs/api)

</div>

<div class="bg-white p-4 rounded-lg shadow">

### Resources

- [GitHub](https://github.com/rakeshpatil1983/markdown-cms)
- [Documentation](/docs)

</div>"""
    (project_path / "themes" / "tailwind" / "templates" / "sidenav.md").write_text(
        tailwind_sidenav, encoding="utf-8"
    )

    tailwind_footer = """<footer class="bg-gray-100 py-6 mt-8">
<div class="container mx-auto text-center">

Made with **Markdown CMS** | 2026

[Home](/) | [About](/about) | [Docs](/docs)

</div>
</footer>"""
    (project_path / "themes" / "tailwind" / "templates" / "footer.md").write_text(
        tailwind_footer, encoding="utf-8"
    )

    tailwind_css = """/* Tailwind Theme CSS */
@import url('https://cdn.tailwindcss.com');

/* Layout Classes */
.header { background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 2rem; }
.main { min-height: calc(100vh - 300px); }
.main-layout { display: grid; grid-template-columns: 250px 1fr; gap: 2rem; }
.content { background: #fff; padding: 2rem; border-radius: 8px; }
.sidebar { background: #f5f5f5; padding: 1rem; border-radius: 8px; height: fit-content; }

/* Component Classes */
.card { margin-bottom: 1rem; padding: 1rem; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.stats { display: flex; gap: 1rem; flex-wrap: wrap; }
.stat { flex: 1; min-width: 200px; padding: 1rem; background: #f3f4f6; border-radius: 8px; text-center; }

@media (max-width: 768px) { .main-layout { grid-template-columns: 1fr; } }"""
    (project_path / "themes" / "tailwind" / "static" / "css" / "theme.css").write_text(
        tailwind_css, encoding="utf-8"
    )

    # Create README explaining how to use themes
    themes_readme = """# Theme Examples

This folder contains 4 complete theme examples using popular CSS frameworks:

## 1. Bootstrap
- CDN: https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css
- Templates: `themes/bootstrap/templates/`
- CSS: `themes/bootstrap/static/css/theme.css`

## 2. Materialize
- CDN: https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css
- Templates: `themes/materialize/templates/`
- CSS: `themes/materialize/static/css/theme.css`

## 3. Bulma
- CDN: https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css
- Templates: `themes/bulma/templates/`
- CSS: `themes/bulma/static/css/theme.css`

## 4. Tailwind CSS
- CDN: https://cdn.tailwindcss.com
- Templates: `themes/tailwind/templates/`
- CSS: `themes/tailwind/static/css/theme.css`

## How to Use

1. Copy template files from `themes/<framework>/templates/` to your `templates/` folder
2. Copy CSS from `themes/<framework>/static/css/` to your `static/css/` folder
3. Update your markdown files to use framework-specific classes

## Creating Components

All components in the `components/` folder are loaded via HTMX:
- `card1.md`, `card2.md`, `card3.md` - Card examples
- `buttons.md` - Button variations
- `table1.md` - Table example
- `alert1.md` - Alert component
- `stats1.md` - Statistics display

Load them in your pages:
```html
<div hx-get="/components/card1" hx-trigger="load" hx-swap="innerHTML"></div>
```
"""
    (project_path / "themes" / "README.md").write_text(themes_readme, encoding="utf-8")


def create_syntax_config(project_path: Path):
    """
    Copy syntax-mappings.md to project root

    This markdown file documents the pure text syntax patterns
    Users can reference this to understand how syntax is converted to HTML
    """
    import shutil
    from pathlib import Path

    # Get the syntax mappings from the core module
    core_mappings = Path(__file__).parent / "core" / "syntax-mappings.md"
    project_mappings = project_path / "syntax-mappings.md"

    if core_mappings.exists():
        shutil.copy(core_mappings, project_mappings)
        print("   - syntax-mappings.md (Pure text syntax reference)")
    else:
        print("Warning: Could not find core syntax-mappings.md")


def build_project():
    """Build project (validate and prepare for deployment)."""
    print("Building project...")

    # Validate pages folder exists
    pages_path = Path("pages")
    if not pages_path.exists():
        print("X No 'pages/' directory found!")
        print("  Make sure you're in the project directory.")
        return False

    markdown_files = list(pages_path.glob("**/*.md"))
    if not markdown_files:
        print("X No markdown files found in pages/")
        return False

    print(f"+ Found {len(markdown_files)} page(s)")

    # Validate templates folder
    templates_path = Path("templates")
    if not templates_path.exists():
        print("X Templates directory not found!")
        return False

    template_files = list(templates_path.glob("*.md"))
    print(f"+ Found {len(template_files)} template part(s)")

    # Validate static folder
    static_path = Path("static")
    if not static_path.exists():
        print("X Static directory not found!")
        return False

    # Check CSS
    css_file = static_path / "css" / "styles.css"
    if not css_file.exists():
        print("X CSS file not found in static/css/!")
        return False

    print("+ CSS validation passed")

    print("+ Build successful! Ready for deployment.")
    return True


def run_project(host="127.0.0.1", port=8000):
    """Run the development server."""
    print(f"Starting server at http://{host}:{port}")
    print("Auto-reload enabled for markdown files")
    print("Press Ctrl+C to stop")

    # Set environment for development
    os.environ["DEBUG"] = "true"

    # Import and run the app
    from .app import main

    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped")


def switch_theme(theme_name: str):
    """Switch to a different CSS framework theme."""

    themes_path = Path("themes")
    if not themes_path.exists():
        print("X No 'themes/' directory found!")
        print("  Make sure you're in the project directory.")
        return False

    theme_path = themes_path / theme_name
    if not theme_path.exists():
        print(f"X Theme '{theme_name}' not found!")
        print("  Available themes:")
        for theme_dir in themes_path.iterdir():
            if theme_dir.is_dir():
                print(f"  - {theme_dir.name}")
        return False

    # Check if theme has required files
    theme_templates = theme_path / "templates"
    theme_css = theme_path / "static" / "css" / "theme.css"

    if not theme_templates.exists():
        print(f"X Theme '{theme_name}' has no templates folder!")
        return False

    if not theme_css.exists():
        print(f"X Theme '{theme_name}' has no CSS file!")
        return False

    # Copy theme files
    print(f"Switching to '{theme_name}' theme...")

    # Copy templates
    import shutil

    template_files = list(theme_templates.glob("*.md"))
    for template_file in template_files:
        dest = Path("templates") / template_file.name
        shutil.copy(template_file, dest)
        print(f"+ Copied template: {template_file.name}")

    # Copy CSS
    shutil.copy(theme_css, Path("static/css/styles.css"))
    print("+ Copied CSS: theme.css -> styles.css")

    print(f"+ Theme '{theme_name}' activated successfully!")
    print("> Restart the server to see changes")
    return True


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Markdown-First Application Framework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  markdown-cms create my-site         # Create new project
  markdown-cms build                  # Build current project
  markdown-cms run                    # Run development server
  markdown-cms run --port 3000        # Run on custom port
  markdown-cms theme bootstrap        # Switch to Bootstrap theme
  markdown-cms theme tailwind         # Switch to Tailwind theme
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new project")
    create_parser.add_argument("name", help="Project name")

    # Build command
    build_parser = subparsers.add_parser("build", help="Build the project")

    # Theme command
    theme_parser = subparsers.add_parser("theme", help="Switch CSS framework theme")
    theme_parser.add_argument(
        "name", help="Theme name (bootstrap, materialize, bulma, tailwind)"
    )

    # Run command
    run_parser = subparsers.add_parser("run", help="Run development server")
    run_parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    run_parser.add_argument("--port", type=int, default=8000, help="Port to bind to")

    # Database commands
    db_parser = subparsers.add_parser("db", help="Database management commands")
    db_subparsers = db_parser.add_subparsers(
        dest="db_command", help="Database commands"
    )

    db_init_parser = db_subparsers.add_parser(
        "init", help="Initialize database (create tables)"
    )
    db_seed_parser = db_subparsers.add_parser(
        "seed", help="Seed database with sample data"
    )
    db_reset_parser = db_subparsers.add_parser(
        "reset", help="Reset database (drop and recreate)"
    )
    db_info_parser = db_subparsers.add_parser("info", help="Show database information")

    # Agent commands
    agent_parser = subparsers.add_parser("agent", help="Run development agents")
    agent_subparsers = agent_parser.add_subparsers(
        dest="agent_command", help="Agent commands"
    )

    agent_orch_parser = agent_subparsers.add_parser(
        "orchestrator", help="Run orchestrator agent"
    )
    agent_orch_parser.add_argument(
        "-c", "--cycles", type=int, default=1, help="Number of cycles to run"
    )

    agent_impl_parser = agent_subparsers.add_parser(
        "implementation", help="Run implementation agent"
    )
    agent_test_parser = agent_subparsers.add_parser("testing", help="Run testing agent")

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    if args.command == "create":
        create_project(args.name)
    elif args.command == "build":
        build_project()
    elif args.command == "db":
        from markdown_cms.core.database import get_db_info, init_db, reset_db, seed_db

        if not args.db_command:
            db_parser.print_help()
            return

        if args.db_command == "init":
            init_db()
        elif args.db_command == "seed":
            seed_db()
        elif args.db_command == "reset":
            confirm = input(
                "[WARNING] This will delete ALL data. Are you sure? (yes/no): "
            )
            if confirm.lower() == "yes":
                reset_db()
            else:
                print("✗ Database reset cancelled")
        elif args.db_command == "info":
            info = get_db_info()
            print("\nDatabase Information:")
            print(f"  URL: {info['url']}")
            print(f"  Driver: {info['driver']}")
            print(f"  Exists: {info['exists']}")
            if "path" in info:
                print(f"  Path: {info['path']}")
            if "size" in info:
                size_mb = info["size"] / (1024 * 1024)
                print(f"  Size: {size_mb:.2f} MB")
    elif args.command == "agent":
        from markdown_cms.agents.cli import (
            run_implementation,
            run_orchestrator,
            run_testing,
        )

        if not args.agent_command:
            agent_parser.print_help()
            return

        if args.agent_command == "orchestrator":
            run_orchestrator(cycles=args.cycles)
        elif args.agent_command == "implementation":
            run_implementation()
        elif args.agent_command == "testing":
            run_testing()
    elif args.command == "theme":
        switch_theme(args.name)
    elif args.command == "run":
        # Override host/port for app
        os.environ["HOST"] = args.host
        os.environ["PORT"] = str(args.port)
        run_project(args.host, args.port)


if __name__ == "__main__":
    main()
