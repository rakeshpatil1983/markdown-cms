"""
Custom Markdown Syntax Parser
Pure text-based semantic syntax (NO CSS, NO HTML in markdown)

Philosophy:
- Write WHAT you want, not HOW it looks
- Semantic markers: =>, ?, :::
- Intent words: success, danger, warning, info
- No CSS classes in user's markdown
"""

import re


def parse_custom_syntax(markdown_text: str) -> str:
    """
    Convert pure text markdown syntax to HTML.

    Examples:
        => Click Me → <button class="btn btn-primary">Click Me</button>
        => Save (success) → <button class="btn btn-success">Save</button>
        :::card ... ::: → Full card HTML
    """

    # Process in order: blocks first, then inline elements
    text = markdown_text

    # BLOCK LEVEL (process first)
    # 1. Process Columns/Grid
    text = parse_columns(text)

    # 2. Process Card blocks
    text = parse_card_blocks(text)

    # 3. Process Panel blocks
    text = parse_panel_blocks(text)

    # 4. Process Section blocks
    text = parse_section_blocks(text)

    # 5. Process Stats blocks
    text = parse_stats_blocks(text)

    # 6. Process Tabs blocks
    text = parse_tabs_blocks(text)

    # 7. Process Navbar blocks
    text = parse_navbar_blocks(text)

    # 8. Process Sidenav blocks
    text = parse_sidenav_blocks(text)

    # 9. Process Header blocks
    text = parse_header_blocks(text)

    # 10. Process Footer blocks
    text = parse_footer_blocks(text)

    # INLINE LEVEL (process after blocks)
    # 11. Process Alerts (callout style)
    text = parse_callout_alerts(text)

    # 12. Process Buttons (=> syntax)
    text = parse_button_syntax(text)

    # 13. Process Button Links (standard link + (button))
    text = parse_button_links(text)

    # 14. Process Inputs (? syntax)
    text = parse_input_syntax(text)

    # 15. Process Textarea (?? syntax)
    text = parse_textarea_syntax(text)

    # 16. Process Dropdown (Select: syntax)
    text = parse_select_syntax(text)

    return text


# ============ BLOCK PARSERS ============


def parse_card_blocks(text: str) -> str:
    """Parse {{{card ...}}} blocks

    Uses semantic class names - styling provided by theme CSS.
    """

    # Pattern: {{{card\ntitle: Title\nheader: Header\nfooter: Footer\n---\nContent\n}}}
    pattern = r"\{\{\{card\n(.*?)\n---\n(.*?)\n\}\}\}"

    def replace_card(match):
        metadata = match.group(1)
        content = match.group(2)

        # Parse metadata
        meta = {}
        for line in metadata.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip()

        # Build card HTML with semantic classes
        html = '<div class="card">\n'

        if "header" in meta:
            html += (
                f'<div class="card-header"><strong>{meta["header"]}</strong></div>\n'
            )

        html += '<div class="card-body">\n'

        if "title" in meta:
            html += f'<h3 class="card-title">{meta["title"]}</h3>\n'

        html += content + "\n"
        html += "</div>\n"

        if "footer" in meta:
            html += f'<div class="card-footer">{meta["footer"]}</div>\n'

        html += "</div>\n"

        return html

    return re.sub(pattern, replace_card, text, flags=re.DOTALL)


def parse_panel_blocks(text: str) -> str:
    """Parse {{{panel ...}}} blocks

    Uses semantic class names - styling provided by theme CSS.
    """
    pattern = r"\{\{\{panel\n(.*?)\n---\n(.*?)\n\}\}\}"

    def replace_panel(match):
        metadata = match.group(1)
        content = match.group(2)

        meta = {}
        for line in metadata.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip()

        html = '<div class="panel">\n'

        if "title" in meta:
            html += f'<h3>{meta["title"]}</h3>\n'

        html += content + "\n"
        html += "</div>\n"

        return html

    return re.sub(pattern, replace_panel, text, flags=re.DOTALL)


def parse_section_blocks(text: str) -> str:
    """Parse {{{section ...}}} blocks

    Uses semantic class names - styling provided by theme CSS.
    """
    pattern = r"\{\{\{section\n(.*?)\n---\n(.*?)\n\}\}\}"

    def replace_section(match):
        metadata = match.group(1)
        content = match.group(2)

        meta = {}
        for line in metadata.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip()

        html = '<section class="section">\n'

        if "title" in meta:
            html += f'<h3>{meta["title"]}</h3>\n'

        html += content + "\n"
        html += "</section>\n"

        return html

    return re.sub(pattern, replace_section, text, flags=re.DOTALL)


def parse_stats_blocks(text: str) -> str:
    """Parse {{{stats ...}}} blocks"""
    # Pattern: {{{stats\n1,234 | Title | Description\n567 | Title | Description\n}}}
    pattern = r"\{\{\{stats\n(.*?)\n\}\}\}"

    def replace_stats(match):
        content = match.group(1)
        stats_items = content.strip().split("\n")

        html = '<div class="stats">\n'

        for item in stats_items:
            if "|" in item:
                parts = [p.strip() for p in item.split("|")]
                if len(parts) >= 2:
                    value = parts[0]
                    label = parts[1]
                    desc = parts[2] if len(parts) > 2 else ""

                    html += '<div class="stat">\n'
                    html += f"<h3>{value}</h3>\n"
                    html += f"<p><strong>{label}</strong>"
                    if desc:
                        html += f"<br>{desc}"
                    html += "</p>\n"
                    html += "</div>\n"

        html += "</div>\n"

        return html

    return re.sub(pattern, replace_stats, text, flags=re.DOTALL)


def parse_tabs_blocks(text: str) -> str:
    """Parse {{{tabs ...}}} blocks"""
    # For now, return a simple implementation
    pattern = r"\{\{\{tabs\n(.*?)\n\}\}\}"

    def replace_tabs(match):
        html = '<div class="tabs-placeholder">\n'
        html += "<p><em>Tabs implementation coming soon</em></p>\n"
        html += "</div>\n"
        return html

    return re.sub(pattern, replace_tabs, text, flags=re.DOTALL)


def parse_navbar_blocks(text: str) -> str:
    """Parse {{{navbar ...}}} blocks

    Uses semantic class names - styling provided by theme CSS.
    """
    pattern = r"\{\{\{navbar\n(.*?)\n---\n(.*?)\n\}\}\}"

    def replace_navbar(match):
        metadata = match.group(1)
        links = match.group(2)

        brand = "Brand"
        for line in metadata.split("\n"):
            if "brand:" in line:
                brand = line.split(":", 1)[1].strip()

        html = '<nav class="navbar">\n'
        html += '<div class="container">\n'
        html += f'<a class="navbar-brand" href="/">{brand}</a>\n'
        html += '<ul class="nav-list">\n'

        # Parse links
        for line in links.strip().split("\n"):
            if "[Link]" in line:
                # Extract URL and text
                # [Link](/url): Text
                html += (
                    '<li class="nav-item"><a class="nav-link" href="#">Link</a></li>\n'
                )

        html += "</ul>\n"
        html += "</div>\n"
        html += "</nav>\n"

        return html

    return re.sub(pattern, replace_navbar, text, flags=re.DOTALL)


def parse_sidenav_blocks(text: str) -> str:
    """Parse {{{sidenav ...}}} blocks

    Uses semantic class names - styling provided by theme CSS.
    """
    pattern = r"\{\{\{sidenav (left|right)\n(.*?)\n---\n(.*?)\n\}\}\}"

    def replace_sidenav(match):
        side = match.group(1)
        metadata = match.group(2)
        links = match.group(3)

        html = f'<nav class="sidenav sidenav-{side}">\n'

        # Parse links
        for line in links.strip().split("\n"):
            if line.startswith("[Link]"):
                html += '<a href="#" class="sidenav-link">Link</a>\n'
            elif line.startswith("- "):
                link_text = line[2:]
                html += f'<a href="#" class="sidenav-link">{link_text}</a>\n'

        html += "</nav>\n"

        return html

    return re.sub(pattern, replace_sidenav, text, flags=re.DOTALL)


def parse_header_blocks(text: str) -> str:
    """Parse {{{header ...}}} blocks

    Uses semantic class names - styling provided by theme CSS.
    """
    pattern = r"\{\{\{header\n(.*?)\n\}\}\}"

    def replace_header(match):
        content = match.group(1)

        title = ""
        subtitle = ""

        for line in content.split("\n"):
            if "title:" in line:
                title = line.split(":", 1)[1].strip()
            elif "subtitle:" in line:
                subtitle = line.split(":", 1)[1].strip()

        html = '<header class="page-header">\n'
        if title:
            html += f"<h1>{title}</h1>\n"
        if subtitle:
            html += f'<p class="subtitle">{subtitle}</p>\n'
        html += "</header>\n"

        return html

    return re.sub(pattern, replace_header, text, flags=re.DOTALL)


def parse_footer_blocks(text: str) -> str:
    """Parse {{{footer ...}}} blocks

    Uses semantic class names - styling provided by theme CSS.
    """
    pattern = r"\{\{\{footer\n---\n(.*?)\n\}\}\}"

    def replace_footer(match):
        content = match.group(1)

        html = '<footer class="page-footer">\n'
        html += '<div class="container">\n'
        html += content + "\n"
        html += "</div>\n"
        html += "</footer>\n"

        return html

    return re.sub(pattern, replace_footer, text, flags=re.DOTALL)


# ============ INLINE PARSERS ============


def parse_alerts(text: str) -> str:
    """Parse [Alert type][Message]

    Uses semantic class names - styling provided by theme CSS.
    """
    # Map danger to error for semantic consistency
    alert_map = {"danger": "error"}
    pattern = r"\[Alert (info|success|warning|danger)\]\[(.*?)\]"

    def replace_alert(match):
        alert_type = match.group(1)
        message = match.group(2)
        semantic_type = alert_map.get(alert_type, alert_type)
        return f'<div class="alert alert-{semantic_type}">{message}</div>'

    return re.sub(pattern, replace_alert, text)


def parse_buttons(text: str) -> str:
    """Parse [Button type][Text]

    Uses semantic class names - styling provided by theme CSS.
    """
    pattern = r"\[Button (primary|secondary|success|danger|warning|info|light|dark)\]\[(.*?)\]"

    def replace_button(match):
        btn_type = match.group(1)
        btn_text = match.group(2)
        return f'<button class="btn btn-{btn_type}">{btn_text}</button>'

    return re.sub(pattern, replace_button, text)


def parse_links(text: str) -> str:
    """Parse [Link][Text](url) and [Link button type][Text](url)

    Uses semantic class names - styling provided by theme CSS.
    """
    # Link button: [Link button primary][Text](url)
    pattern1 = r"\[Link button (primary|secondary|success|danger|warning|info)\]\[(.*?)\]\((.*?)\)"

    def replace_link_button(match):
        btn_type = match.group(1)
        link_text = match.group(2)
        url = match.group(3)
        return f'<a href="{url}" class="btn btn-{btn_type}">{link_text}</a>'

    text = re.sub(pattern1, replace_link_button, text)

    # Regular link: [Link][Text](url)
    pattern2 = r"\[Link\]\[(.*?)\]\((.*?)\)"

    def replace_link(match):
        link_text = match.group(1)
        url = match.group(2)
        return f'<a href="{url}">{link_text}</a>'

    return re.sub(pattern2, replace_link, text)


def parse_inputs(text: str) -> str:
    """Parse [Input type][Label]

    Uses semantic class names - styling provided by theme CSS.
    """
    # Pattern with attributes: [Input number min=1 max=100][Label]
    pattern1 = r"\[Input (number|range) (.*?)\]\[(.*?)\]"

    def replace_input_with_attrs(match):
        input_type = match.group(1)
        attrs = match.group(2)
        label = match.group(3)

        input_class = "form-range" if input_type == "range" else "form-input"

        html = '<div class="form-group">\n'
        html += f'<label class="form-label">{label}</label>\n'
        html += f'<input type="{input_type}" class="{input_class}" {attrs}>\n'
        html += "</div>\n"

        return html

    text = re.sub(pattern1, replace_input_with_attrs, text)

    # Simple pattern: [Input type][Label]
    pattern2 = r"\[Input (text|email|password|number|range)\]\[(.*?)\]"

    def replace_input(match):
        input_type = match.group(1)
        label = match.group(2)

        input_class = "form-range" if input_type == "range" else "form-input"

        html = '<div class="form-group">\n'
        html += f'<label class="form-label">{label}</label>\n'
        html += (
            f'<input type="{input_type}" class="{input_class}" placeholder="{label}">\n'
        )
        html += "</div>\n"

        return html

    return re.sub(pattern2, replace_input, text)


def parse_textarea(text: str) -> str:
    """Parse [Textarea rows=4][Label]

    Uses semantic class names - styling provided by theme CSS.
    """
    pattern = r"\[Textarea rows=(\d+)\]\[(.*?)\]"

    def replace_textarea(match):
        rows = match.group(1)
        label = match.group(2)

        html = '<div class="form-group">\n'
        html += f'<label class="form-label">{label}</label>\n'
        html += f'<textarea class="form-textarea" rows="{rows}" placeholder="{label}"></textarea>\n'
        html += "</div>\n"

        return html

    return re.sub(pattern, replace_textarea, text)


def parse_dropdown(text: str) -> str:
    """Parse [Dropdown][Label]

    Uses semantic class names - styling provided by theme CSS.
    """
    # For now, simple implementation
    pattern = r"\[Dropdown\]\[(.*?)\]"

    def replace_dropdown(match):
        label = match.group(1)

        html = '<div class="form-group">\n'
        html += f'<label class="form-label">{label}</label>\n'
        html += '<select class="form-select">\n'
        html += "<option selected>Select one...</option>\n"
        html += "</select>\n"
        html += "</div>\n"

        return html

    return re.sub(pattern, replace_dropdown, text)


def parse_icons(text: str) -> str:
    """Parse [Icon type]"""
    icon_map = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
        "home": "🏠",
        "email": "📧",
        "phone": "📞",
        "settings": "⚙️",
        "star": "⭐",
        "heart": "❤️",
        "folder": "📁",
        "search": "🔍",
    }

    pattern = r"\[Icon (\w+)\]"

    def replace_icon(match):
        icon_type = match.group(1)
        return icon_map.get(icon_type, "❓")

    return re.sub(pattern, replace_icon, text)
