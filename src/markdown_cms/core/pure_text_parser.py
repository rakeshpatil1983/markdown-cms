"""
Pure Text Markdown Parser
Philosophy-driven semantic syntax - NO CSS, NO HTML in markdown

Syntax mappings are documented in: syntax-mappings.md
This file serves as both documentation and specification for the parser.

Syntax:
    # Static buttons
    => Button
    => Save (success)

    # HTMX-enabled buttons (arrow = action)
    => Submit -> /api/submit                    # POST by default
    => Load More -> /api/more (get)             # GET request
    => Delete -> /api/delete (delete, confirm)  # With confirmation
    => Save (success) -> /api/save              # Styled + action

    # Form inputs
    ? Your Name (text)
    ?? Message

    # HTMX form block (auto-wraps with hx-post)
    :::form /api/contact
    ? Name (text)
    ? Email (email)
    ?? Message
    => Submit (success)
    :::

    # Event triggers
    @load /api/content -> #target               # Load on page load
    @click /api/toggle -> #target               # Click handler
    @submit /api/form -> #result                # Form submission

    # Other blocks
    :::card ... :::
    :::columns 2 ... :::
"""

import re

from markdown_it import MarkdownIt

# Create a markdown renderer for processing content inside blocks
# Enable GFM features like tables, strikethrough, task lists
_md_renderer = MarkdownIt(
    "gfm-like",
    {
        "html": True,
        "breaks": True,
        "linkify": False,  # Disabled - requires linkify-it-py package
        "typographer": True,
    },
).enable(["table", "strikethrough"])


def render_markdown_content(text: str) -> str:
    """
    Render markdown content to HTML

    Used for processing markdown inside blocks (cards, columns, sections)
    This function processes any remaining pure text syntax BEFORE rendering markdown

    Processing order:
    1. Extract code blocks (protect from processing)
    2. Block-level syntax (cards, panels, sections, stats) - for nested structures
    3. Inline syntax (buttons, inputs, alerts) - for interactive elements
    4. Restore code blocks
    5. Standard markdown (headings, bold, lists) - final rendering
    """
    if not text or not text.strip():
        return text

    # Process block-level pure text syntax that might be nested
    # (cards inside columns, etc.)
    # Note: accordion/tabs/carousel are NOT processed here to avoid recursion
    # They should only exist at the top level, not inside other components
    text = parse_card_blocks(text)
    text = parse_panel_blocks(text)
    text = parse_section_blocks(text)
    text = parse_stats_blocks(text)
    text = parse_table_blocks(text)

    # Process inline pure text syntax
    # (buttons, inputs, alerts, etc.)
    text = parse_callout_alerts(text)
    text = parse_buttons(text)
    text = parse_button_links(text)
    text = parse_inputs(text)
    text = parse_textareas(text)
    text = parse_selects(text)
    text = parse_checkboxes(text)
    text = parse_radio_buttons(text)
    text = parse_badges(text)
    text = parse_progress_bars(text)
    text = parse_breadcrumbs(text)
    text = parse_pagination(text)

    # Finally render markdown (headings, bold, lists, etc.)
    return _md_renderer.render(text.strip())


def parse_pure_text_syntax(text: str) -> str:
    """
    Convert pure text markdown to HTML

    The syntax patterns are documented in syntax-mappings.md
    See that file for the complete specification of patterns and templates.

    Args:
        text: Markdown text to parse

    Returns:
        HTML with pure text syntax converted
    """

    # Normalize line endings (Windows \r\n -> Unix \n)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Step 1: Extract code blocks and inline code, replace with placeholders
    # (Don't process pure text syntax inside code blocks or inline code)
    # Use HTML comment placeholders that markdown won't touch
    code_blocks = []

    def save_code_block(match):
        code_blocks.append(match.group(0))
        return f"<!--CODE_BLOCK_{len(code_blocks) - 1}-->"

    # First: Match triple backtick code blocks (fenced code)
    # Use non-greedy match for content between backticks
    text = re.sub(r"```.*?```", save_code_block, text, flags=re.DOTALL)

    # Second: Match inline code (single backticks) - must protect from parsing
    # Pattern: `content` where content doesn't contain backticks
    inline_codes = []

    def save_inline_code(match):
        inline_codes.append(match.group(0))
        return f"<!--INLINE_CODE_{len(inline_codes) - 1}-->"

    text = re.sub(r"`[^`]+`", save_inline_code, text)

    # Step 2: Process blocks first (order matters!)
    # Process inner blocks BEFORE outer blocks to avoid regex nesting issues
    # Cards/panels/sections are processed first, then columns can contain them
    # Landing page components
    text = parse_hero_blocks(text)
    text = parse_feature_blocks(text)  # Individual features first
    text = parse_features_blocks(text)  # Then feature containers
    text = parse_cta_blocks(text)
    # HTMX-enabled form blocks (process before individual inputs)
    text = parse_form_blocks(text)
    # Standard components
    text = parse_card_blocks(text)
    text = parse_panel_blocks(text)
    text = parse_section_blocks(text)
    text = parse_stats_blocks(text)
    text = parse_table_blocks(text)
    text = parse_carousel_blocks(text)
    text = parse_tabs_blocks(text)
    text = parse_accordion_blocks(text)
    text = parse_navbar_blocks(text)
    text = parse_sidenav_blocks(text)
    text = parse_header_blocks(text)
    text = parse_footer_blocks(text)
    # Interactive components (modals, hidden sections, result areas, calculators)
    text = parse_modal_blocks(text)
    text = parse_hidden_blocks(text)
    text = parse_result_blocks(text)
    text = parse_calc_blocks(text)
    # Process columns LAST so nested cards are already converted to HTML
    text = parse_columns_blocks(text)

    # Step 3: Process inline elements
    text = parse_callout_alerts(text)
    # Interactive triggers (@toggle, @copy) MUST come BEFORE regular buttons
    # (they use => syntax that would otherwise be caught by parse_buttons)
    text = parse_toggle_triggers(text)
    text = parse_copy_triggers(text)
    # HTMX-enabled buttons (with -> action) BEFORE regular buttons
    text = parse_htmx_buttons(text)
    text = parse_buttons(text)
    text = parse_htmx_button_links(text)
    text = parse_button_links(text)
    # Event triggers (@load, @click, @hover for HTMX)
    text = parse_event_triggers(text)
    # Form inputs
    text = parse_inputs(text)
    text = parse_textareas(text)
    text = parse_selects(text)
    text = parse_checkboxes(text)
    text = parse_radio_buttons(text)
    text = parse_badges(text)
    text = parse_progress_bars(text)
    text = parse_breadcrumbs(text)
    text = parse_pagination(text)

    # Step 4: Restore inline code first (they might be inside code blocks conceptually)
    for i, inline_code in enumerate(inline_codes):
        text = text.replace(f"<!--INLINE_CODE_{i}-->", inline_code)

    # Step 5: Restore code blocks
    for i, code_block in enumerate(code_blocks):
        text = text.replace(f"<!--CODE_BLOCK_{i}-->", code_block)

    return text


# ============ BLOCK PARSERS ============
# These functions implement the syntax defined in syntax-config.yaml
# Users can customize the HTML output by editing syntax-config.yaml in their project


def parse_hero_blocks(text: str) -> str:
    """
    Parse :::hero
    # Main Title
    Subtitle or description text
    [Button Text](/link)
    :::

    Creates a full-width hero section with gradient background
    """
    pattern = r":::hero\n(.*?)\n:::(?!\w)"

    def replace_hero(match):
        content = match.group(1).strip()

        # Parse content - look for heading, paragraph, and link
        lines = content.split("\n")
        title = ""
        subtitle_lines = []
        cta_link = ""
        cta_text = ""

        for line in lines:
            line = line.strip()
            if line.startswith("# "):
                title = line[2:].strip()
            elif line.startswith("[") and "](" in line:
                # Extract link: [Text](url)
                import re as re_inner

                link_match = re_inner.match(r"\[(.+?)\]\((.+?)\)", line)
                if link_match:
                    cta_text = link_match.group(1)
                    cta_link = link_match.group(2)
            elif line:
                subtitle_lines.append(line)

        subtitle = " ".join(subtitle_lines)

        html = '<div class="hero">\n'
        if title:
            html += f"<h1>{title}</h1>\n"
        if subtitle:
            html += f"<p>{subtitle}</p>\n"
        if cta_link and cta_text:
            html += f'<a href="{cta_link}" class="btn-hero">{cta_text}</a>\n'
        html += "</div>\n"

        return html

    return re.sub(pattern, replace_hero, text, flags=re.DOTALL)


def parse_features_blocks(text: str) -> str:
    """
    Parse :::features
    Content with :::feature blocks inside
    :::

    Creates a feature grid container
    """
    pattern = r":::features\n(.*?)\n:::(?!\w)"

    def replace_features(match):
        content = match.group(1)
        html = '<div class="section">\n'
        html += '<div class="features">\n'
        html += content  # Feature blocks are already parsed
        html += "</div>\n"
        html += "</div>\n"
        return html

    return re.sub(pattern, replace_features, text, flags=re.DOTALL)


def parse_feature_blocks(text: str) -> str:
    """
    Parse :::feature
    ### Feature Title
    Description text
    - List item 1
    - List item 2
    [Link Text](/url)
    :::

    Creates a feature card
    """
    pattern = r":::feature\n(.*?)\n:::(?!\w)"

    def replace_feature(match):
        content = match.group(1).strip()

        # Parse content
        lines = content.split("\n")
        title = ""
        description_lines = []
        list_items = []
        link_text = ""
        link_url = ""

        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith("### "):
                title = line_stripped[4:].strip()
            elif line_stripped.startswith("- "):
                list_items.append(line_stripped[2:].strip())
            elif line_stripped.startswith("[") and "](" in line_stripped:
                import re as re_inner

                link_match = re_inner.match(r"\[(.+?)\]\((.+?)\)", line_stripped)
                if link_match:
                    link_text = link_match.group(1)
                    link_url = link_match.group(2)
            elif line_stripped and not line_stripped.startswith("#"):
                description_lines.append(line_stripped)

        description = " ".join(description_lines)

        html = '<div class="feature-card">\n'
        if title:
            html += f"<h3>{title}</h3>\n"
        if description:
            html += f"<p>{description}</p>\n"
        if list_items:
            html += "<ul>\n"
            for item in list_items:
                html += f"<li>{item}</li>\n"
            html += "</ul>\n"
        if link_url and link_text:
            html += f'<a href="{link_url}">{link_text}</a>\n'
        html += "</div>\n"

        return html

    return re.sub(pattern, replace_feature, text, flags=re.DOTALL)


def parse_cta_blocks(text: str) -> str:
    """
    Parse :::cta
    ## Call to Action Title
    Description text
    [Button Text](/link)
    :::

    Creates a call-to-action section with gradient background
    """
    pattern = r":::cta\n(.*?)\n:::(?!\w)"

    def replace_cta(match):
        content = match.group(1).strip()

        # Parse content
        lines = content.split("\n")
        title = ""
        description_lines = []
        cta_link = ""
        cta_text = ""

        for line in lines:
            line = line.strip()
            if line.startswith("## "):
                title = line[3:].strip()
            elif line.startswith("[") and "](" in line:
                import re as re_inner

                link_match = re_inner.match(r"\[(.+?)\]\((.+?)\)", line)
                if link_match:
                    cta_text = link_match.group(1)
                    cta_link = link_match.group(2)
            elif line:
                description_lines.append(line)

        description = " ".join(description_lines)

        html = '<div class="cta-section">\n'
        if title:
            html += f"<h2>{title}</h2>\n"
        if description:
            html += f"<p>{description}</p>\n"
        if cta_link and cta_text:
            html += f'<a href="{cta_link}" class="btn-hero">{cta_text}</a>\n'
        html += "</div>\n"

        return html

    return re.sub(pattern, replace_cta, text, flags=re.DOTALL)


def parse_form_blocks(text: str) -> str:
    """
    Parse HTMX-enabled form blocks

    Syntax:
        :::form /api/endpoint
        ? Name (text)
        ? Email (email)
        ?? Message
        => Submit (success)
        :::

        :::form /api/endpoint (get)           # GET instead of POST
        :::form /api/endpoint -> @result      # Named target (pure markdown)
        :::form /api/endpoint (put) -> @result  # Method + named target

    Target syntax (pure markdown, no HTML IDs):
        -> @name    References :::result name block (becomes #result-name)

    The library automatically:
    - Wraps content in <form> with hx-post/hx-get
    - Adds hx-target for response handling
    - Adds loading indicator
    - Adds hx-swap for smooth updates
    - Generates unique form ID
    - Adds name attributes to inputs based on labels
    """
    import hashlib

    # Pattern: :::form /endpoint [(method)] [-> @target]
    # Supports both @name (new) and #id (legacy) syntax
    pattern = r":::form\s+(/[^\s\(\)]+)(?:\s+\((get|post|put|delete|patch)\))?(?:\s+->\s+[@#]([\w-]+))?\n(.*?)\n:::(?!\w)"

    def replace_form(match):
        endpoint = match.group(1)
        method = match.group(2) or "post"  # Default to POST
        target_name = match.group(3)  # e.g., "result" from @result or #result
        content = match.group(4)

        # Generate unique form ID
        form_id = f"form-{hashlib.md5(endpoint.encode()).hexdigest()[:8]}"

        # Determine HTMX attribute based on method
        hx_method = f"hx-{method}"

        # Build form attributes
        attrs = f'id="{form_id}" {hx_method}="{endpoint}"'

        # Target handling
        if target_name:
            # @name or #name -> #result-name (references :::result block)
            attrs += f' hx-target="#result-{target_name}"'
            attrs += ' hx-swap="innerHTML"'
        else:
            attrs += f' hx-target="#{form_id}-result"'
            # Use innerHTML so the container persists for multiple submissions
            attrs += ' hx-swap="innerHTML"'

        # Add loading indicator class
        attrs += ' hx-indicator=".htmx-indicator"'

        # Process form content - add name attributes to inputs
        processed_content = _process_form_inputs(content, form_id)

        # Build form HTML
        html = f'<form class="htmx-form" {attrs}>\n'
        html += '<div class="htmx-indicator form-loading">Processing...</div>\n'
        html += processed_content
        html += "</form>\n"

        # Add result container if no custom target
        if not target_name:
            html += f'<div id="{form_id}-result"></div>\n'

        return html

    return re.sub(pattern, replace_form, text, flags=re.DOTALL)


def _process_form_inputs(content: str, form_id: str) -> str:
    """
    Process form content: convert markdown syntax to HTML form elements.
    Handles inputs, textareas, selects, and buttons inside form blocks.
    """
    import re as re_inner

    def make_name(label):
        """Convert label to valid input name."""
        return re_inner.sub(r"[^\w]", "_", label.lower()).strip("_")

    # Process number/range inputs with min-max: ? Label (number 0-100) [placeholder]
    # Supports optional: ? Label (number optional 0-100) [placeholder]
    # Supports negative min: ? Label (number optional -100-100) [placeholder]
    pattern_minmax = (
        r"^\? (.+?) \((number|range)(?: (optional))? (-?\d+)-(-?\d+)\)(?: \[(.+?)\])?$"
    )

    def replace_input_minmax(match):
        label = match.group(1)
        input_type = match.group(2)
        is_optional = match.group(3) == "optional"
        min_val = match.group(4)
        max_val = match.group(5)
        placeholder = match.group(6) if match.group(6) else label
        name = make_name(label)

        input_class = "form-range" if input_type == "range" else "form-input"
        required_attr = "" if is_optional else " required"
        return f"""<div class="form-group">
<label class="form-label">{label}</label>
<input type="{input_type}" name="{name}" class="{input_class}" min="{min_val}" max="{max_val}" placeholder="{placeholder}"{required_attr}>
</div>"""

    content = re_inner.sub(
        pattern_minmax, replace_input_minmax, content, flags=re_inner.MULTILINE
    )

    # Process simple inputs: ? Label (type) [placeholder]
    # Supports optional: ? Label (type optional) [placeholder]
    pattern_input = r"^\? (.+?) \((text|email|password|number|tel|url|date|time)(?: (optional))?\)(?: \[(.+?)\])?$"

    def replace_input(match):
        label = match.group(1)
        input_type = match.group(2)
        is_optional = match.group(3) == "optional"
        placeholder = match.group(4) if match.group(4) else label
        name = make_name(label)

        input_class = "form-range" if input_type == "range" else "form-input"
        required_attr = "" if is_optional else " required"
        return f"""<div class="form-group">
<label class="form-label">{label}</label>
<input type="{input_type}" name="{name}" class="{input_class}" placeholder="{placeholder}"{required_attr}>
</div>"""

    content = re_inner.sub(
        pattern_input, replace_input, content, flags=re_inner.MULTILINE
    )

    # Process textareas: ?? Label [placeholder]
    pattern_textarea = r"^\?\? (.+?)(?: \[(.+?)\])?$"

    def replace_textarea(match):
        label = match.group(1)
        placeholder = match.group(2) if match.group(2) else label
        name = make_name(label)

        return f"""<div class="form-group">
<label class="form-label">{label}</label>
<textarea name="{name}" class="form-textarea" rows="4" placeholder="{placeholder}" required></textarea>
</div>"""

    content = re_inner.sub(
        pattern_textarea, replace_textarea, content, flags=re_inner.MULTILINE
    )

    # Process selects: Select: Label | opt1 | opt2
    pattern_select = r"^Select:\s*(.+?)\s*\|\s*(.+)$"

    def replace_select(match):
        label = match.group(1)
        options_str = match.group(2)
        options = [opt.strip() for opt in options_str.split("|")]
        name = make_name(label)

        options_html = '<option value="" selected disabled>Select...</option>\n'
        for opt in options:
            val = opt.lower().replace(" ", "_")
            options_html += f'<option value="{val}">{opt}</option>\n'

        return f"""<div class="form-group">
<label class="form-label">{label}</label>
<select name="{name}" class="form-select" required>
{options_html}</select>
</div>"""

    content = re_inner.sub(
        pattern_select, replace_select, content, flags=re_inner.MULTILINE
    )

    # Process submit buttons: => Text (style)
    pattern_button_styled = (
        r"^=> (.+?) \((primary|secondary|success|danger|warning|info)\)$"
    )

    def replace_button_styled(match):
        btn_text = match.group(1)
        btn_style = match.group(2)
        return f'<button type="submit" class="btn btn-{btn_style}">{btn_text}</button>'

    content = re_inner.sub(
        pattern_button_styled, replace_button_styled, content, flags=re_inner.MULTILINE
    )

    # Process submit buttons without style: => Text
    pattern_button = r"^=> (.+)$"

    def replace_button(match):
        btn_text = match.group(1).strip()
        # Skip if already processed (has parentheses for style)
        if "(" in btn_text and ")" in btn_text:
            return match.group(0)
        return f'<button type="submit" class="btn btn-primary">{btn_text}</button>'

    content = re_inner.sub(
        pattern_button, replace_button, content, flags=re_inner.MULTILINE
    )

    return content


def parse_columns_blocks(text: str) -> str:
    """
    Parse :::columns N ... :::

    Example:
        :::columns 2
        Left content
        ---
        Right content
        :::

    Creates a responsive grid with specified number of columns.
    Uses semantic class names - styling provided by theme CSS.
    """
    # Use negative lookahead to avoid matching nested ::: blocks
    # (?!\w) ensures we don't match :::card or other ::: patterns
    pattern = r":::columns (\d+)\n(.*?)\n:::(?!\w)"

    def replace_columns(match):
        num_cols = int(match.group(1))
        content = match.group(2)

        # Split by ---
        columns = [c.strip() for c in content.split("\n---\n")]

        # Semantic class names - CSS handles the actual grid
        html = f'<div class="grid grid-{len(columns)}">\n'
        for col in columns:
            html += '<div class="grid-col">\n'
            # Render markdown inside each column
            html += render_markdown_content(col) + "\n"
            html += "</div>\n"
        html += "</div>\n"

        return html

    return re.sub(pattern, replace_columns, text, flags=re.DOTALL)


def parse_card_blocks(text: str) -> str:
    """
    Parse :::card
    Content
    :::

    Or with sections:
    :::card
    --- header ---
    Header text
    --- body ---
    Body content
    --- footer ---
    Footer text
    :::

    Uses semantic class names - styling provided by theme CSS.
    """
    # Use negative lookahead to avoid matching nested ::: blocks
    pattern = r":::card\n(.*?)\n:::(?!\w)"

    def replace_card(match):
        content = match.group(1)

        # Check for sections
        if "--- header ---" in content or "--- footer ---" in content:
            header = ""
            body = content
            footer = ""

            # Extract header
            if "--- header ---" in content:
                parts = content.split("--- header ---", 1)
                if len(parts) > 1:
                    rest = parts[1]
                    if "--- body ---" in rest:
                        h_b = rest.split("--- body ---", 1)
                        header = h_b[0].strip()
                        body = h_b[1] if len(h_b) > 1 else ""
                    else:
                        header = rest.strip()
                        body = ""

            # Extract footer from body
            if "--- footer ---" in body:
                b_f = body.split("--- footer ---", 1)
                body = b_f[0].strip()
                footer = b_f[1].strip() if len(b_f) > 1 else ""

            # Build HTML with semantic class names
            html = '<div class="card">\n'
            if header:
                html += f'<div class="card-header">{render_markdown_content(header)}</div>\n'
            html += '<div class="card-body">\n'
            html += render_markdown_content(body) + "\n"
            html += "</div>\n"
            if footer:
                html += f'<div class="card-footer">{render_markdown_content(footer)}</div>\n'
            html += "</div>\n"

            return html
        else:
            # Simple card (render markdown inside)
            return f'<div class="card"><div class="card-body">\n{render_markdown_content(content)}\n</div></div>\n'

    return re.sub(pattern, replace_card, text, flags=re.DOTALL)


def parse_panel_blocks(text: str) -> str:
    """Parse :::panel [type] ... :::

    Types: info, success, warning, danger (optional)
    Uses semantic class names - styling provided by theme CSS.
    """
    # Pattern with optional type (info, success, warning, danger)
    pattern = r":::panel(?: (info|success|warning|danger))?\n(.*?)\n:::(?!\w)"

    def replace_panel(match):
        panel_type = match.group(1)  # Can be None if no type specified
        content = match.group(2)

        # Build class list
        classes = "panel"
        if panel_type:
            classes += f" panel-{panel_type}"

        # Render markdown inside panel - semantic class name
        return f'<div class="{classes}">\n{render_markdown_content(content)}\n</div>\n'

    return re.sub(pattern, replace_panel, text, flags=re.DOTALL)


def parse_section_blocks(text: str) -> str:
    """
    Parse :::section ... ::: or :::section alt ... :::

    The 'alt' modifier adds an alternate background color
    """
    # First handle :::section alt
    pattern_alt = r":::section alt\n(.*?)\n:::(?!\w)"

    def replace_section_alt(match):
        content = match.group(1)
        return f'<div class="section section-alt">\n{render_markdown_content(content)}\n</div>\n'

    text = re.sub(pattern_alt, replace_section_alt, text, flags=re.DOTALL)

    # Then handle regular :::section
    pattern = r":::section\n(.*?)\n:::(?!\w)"

    def replace_section(match):
        content = match.group(1)
        return f'<div class="section">\n{render_markdown_content(content)}\n</div>\n'

    return re.sub(pattern, replace_section, text, flags=re.DOTALL)


def parse_stats_blocks(text: str) -> str:
    """
    Parse :::stats
    1,234 | Total Users | ↑ 12%
    567 | Active | 🟢 Online
    :::
    """
    # Use negative lookahead to avoid matching nested ::: blocks
    pattern = r":::stats\n(.*?)\n:::(?!\w)"

    def replace_stats(match):
        content = match.group(1)
        lines = [l.strip() for l in content.split("\n") if l.strip()]

        html = '<div class="stats">\n'
        for line in lines:
            if "|" in line:
                parts = [p.strip() for p in line.split("|")]
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


def parse_table_blocks(text: str) -> str:
    """
    Parse :::table
    Source: users_all
    Columns: username, email, role
    :::

    Creates a data table populated from a data source.
    Supports pagination and sorting.
    Uses semantic class names - styling provided by theme CSS.
    """
    pattern = r":::table\n(.*?)\n:::(?!\w)"

    table_counter = 0

    def replace_table(match):
        nonlocal table_counter
        table_counter += 1
        table_id = f"table{table_counter}"

        content = match.group(1)
        lines = [line.strip() for line in content.split("\n") if line.strip()]

        # Parse configuration
        source_name = None
        columns = []
        pagination = 0
        sortable = False
        striped = True
        hover = True

        for line in lines:
            if line.startswith("Source:"):
                source_name = line.split(":", 1)[1].strip()
            elif line.startswith("Columns:"):
                columns_str = line.split(":", 1)[1].strip()
                columns = [col.strip() for col in columns_str.split(",")]
            elif line.startswith("Pagination:"):
                pagination = int(line.split(":", 1)[1].strip())
            elif line.startswith("Sortable:"):
                sortable = line.split(":", 1)[1].strip().lower() == "true"
            elif line.startswith("Striped:"):
                striped = line.split(":", 1)[1].strip().lower() == "true"
            elif line.startswith("Hover:"):
                hover = line.split(":", 1)[1].strip().lower() == "true"

        # Validate required fields
        if not source_name:
            return '<div class="alert alert-danger">Error: Table source not specified</div>\n'

        # Get data from registry
        try:
            from .registry import get_registry

            registry = get_registry()

            # For now, call without user context (will add later with request context)
            # In production, this would get current user from request
            data = registry.call(source_name, user=None)

            if not data:
                return f'<div class="alert alert-info">No data available from source: {source_name}</div>\n'

            # Auto-detect columns if not specified
            if not columns and len(data) > 0:
                columns = list(data[0].keys())

        except ValueError as e:
            return f'<div class="alert alert-danger">Error: {str(e)}</div>\n'
        except PermissionError as e:
            return f'<div class="alert alert-warning">Access Denied: {str(e)}</div>\n'
        except Exception as e:
            return f'<div class="alert alert-danger">Error loading table data: {str(e)}</div>\n'

        # Build table HTML with semantic class names
        table_classes = ["table"]
        if striped:
            table_classes.append("table-striped")
        if hover:
            table_classes.append("table-hover")

        html = '<div class="table-container">\n'
        html += f'<table class="{" ".join(table_classes)}" id="{table_id}">\n'

        # Table header
        html += "<thead>\n<tr>\n"
        for col in columns:
            # Format column name (capitalize, replace underscores)
            col_display = col.replace("_", " ").title()
            if sortable:
                html += f'<th class="sortable">{col_display} <span class="sort-icon">⇅</span></th>\n'
            else:
                html += f"<th>{col_display}</th>\n"
        html += "</tr>\n</thead>\n"

        # Table body
        html += "<tbody>\n"
        for row in data:
            html += "<tr>\n"
            for col in columns:
                value = row.get(col, "")
                html += f"<td>{value}</td>\n"
            html += "</tr>\n"
        html += "</tbody>\n"

        html += "</table>\n"
        html += "</div>\n"

        # Add sortable JavaScript if needed
        if sortable:
            html += f"""
<script>
(function() {{
    const table = document.getElementById('{table_id}');
    const headers = table.querySelectorAll('th');
    let sortOrder = {{}};

    headers.forEach((header, index) => {{
        header.addEventListener('click', () => {{
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));

            // Toggle sort order
            sortOrder[index] = sortOrder[index] === 'asc' ? 'desc' : 'asc';

            rows.sort((a, b) => {{
                const aVal = a.children[index].textContent.trim();
                const bVal = b.children[index].textContent.trim();

                // Try numeric comparison first
                const aNum = parseFloat(aVal);
                const bNum = parseFloat(bVal);

                if (!isNaN(aNum) && !isNaN(bNum)) {{
                    return sortOrder[index] === 'asc' ? aNum - bNum : bNum - aNum;
                }}

                // String comparison
                return sortOrder[index] === 'asc'
                    ? aVal.localeCompare(bVal)
                    : bVal.localeCompare(aVal);
            }});

            // Reorder rows
            rows.forEach(row => tbody.appendChild(row));

            // Update sort icons
            headers.forEach((h, i) => {{
                const icon = h.querySelector('.sort-icon');
                if (i === index) {{
                    icon.textContent = sortOrder[index] === 'asc' ? '↑' : '↓';
                }} else {{
                    icon.textContent = '⇅';
                }}
            }});
        }});
    }});
}})();
</script>
"""

        return html

    return re.sub(pattern, replace_table, text, flags=re.DOTALL)


def parse_carousel_blocks(text: str) -> str:
    """
    Parse :::carousel
    Slide 1 content
    ---
    Slide 2 content
    ---
    Slide 3 content
    :::

    Creates a carousel with semantic class names.
    Uses pure CSS/JS for framework-agnostic implementation.
    """
    # Use negative lookahead to avoid matching nested ::: blocks
    pattern = r":::carousel\n(.*?)\n:::(?!\w)"

    carousel_counter = 0  # For unique IDs

    def replace_carousel(match):
        nonlocal carousel_counter
        carousel_counter += 1
        carousel_id = f"carousel{carousel_counter}"

        content = match.group(1)
        # Split by ---
        slides = [s.strip() for s in content.split("\n---\n")]

        html = f'<div id="{carousel_id}" class="carousel">\n'

        # Indicators
        html += '<div class="carousel-indicators">\n'
        for i in range(len(slides)):
            active = " active" if i == 0 else ""
            html += f'<button type="button" class="carousel-indicator{active}" data-slide="{i}"></button>\n'
        html += "</div>\n"

        # Slides
        html += '<div class="carousel-slides">\n'
        for i, slide in enumerate(slides):
            active = " active" if i == 0 else ""
            html += f'<div class="carousel-slide{active}">\n'
            # Render markdown inside each slide
            html += '<div class="carousel-content">\n'
            html += render_markdown_content(slide) + "\n"
            html += "</div>\n"
            html += "</div>\n"
        html += "</div>\n"

        # Controls
        html += '<button class="carousel-control carousel-prev" type="button" aria-label="Previous">\n'
        html += '<span class="carousel-arrow">‹</span>\n'
        html += "</button>\n"
        html += '<button class="carousel-control carousel-next" type="button" aria-label="Next">\n'
        html += '<span class="carousel-arrow">›</span>\n'
        html += "</button>\n"
        html += "</div>\n"

        # Pure JS carousel implementation
        html += f"""
<script>
(function() {{
    const carousel = document.getElementById('{carousel_id}');
    const slides = carousel.querySelectorAll('.carousel-slide');
    const indicators = carousel.querySelectorAll('.carousel-indicator');
    const prevBtn = carousel.querySelector('.carousel-prev');
    const nextBtn = carousel.querySelector('.carousel-next');
    let current = 0;

    function showSlide(index) {{
        slides.forEach((s, i) => s.classList.toggle('active', i === index));
        indicators.forEach((ind, i) => ind.classList.toggle('active', i === index));
        current = index;
    }}

    prevBtn.addEventListener('click', () => showSlide((current - 1 + slides.length) % slides.length));
    nextBtn.addEventListener('click', () => showSlide((current + 1) % slides.length));
    indicators.forEach((ind, i) => ind.addEventListener('click', () => showSlide(i)));
}})();
</script>
"""

        return html

    return re.sub(pattern, replace_carousel, text, flags=re.DOTALL)


def parse_tabs_blocks(text: str) -> str:
    """
    Parse :::tabs
    Tab 1 Title
    ---
    Content for tab 1
    ---
    Tab 2 Title
    ---
    Content for tab 2
    :::

    Creates tabs with semantic class names.
    Uses pure CSS/JS for framework-agnostic implementation.
    """
    pattern = r":::tabs\n(.*?)\n:::(?!\w)"

    tabs_counter = 0  # For unique IDs

    def replace_tabs(match):
        nonlocal tabs_counter
        tabs_counter += 1
        tabs_id = f"tabs{tabs_counter}"

        content = match.group(1)

        # Split by --- but skip --- inside code blocks
        # First extract code blocks temporarily
        temp_code_blocks = []

        def save_temp_code(m):
            temp_code_blocks.append(m.group(0))
            return f"__TEMP_CODE_{len(temp_code_blocks)-1}__"

        content_safe = re.sub(r"```.*?```", save_temp_code, content, flags=re.DOTALL)

        # Now split safely
        parts = [p.strip() for p in content_safe.split("\n---\n")]

        # Restore code blocks in each part
        for i in range(len(parts)):
            for j, code in enumerate(temp_code_blocks):
                parts[i] = parts[i].replace(f"__TEMP_CODE_{j}__", code)

        # Parse tabs: expect pairs of (title, content)
        tabs_data = []
        for i in range(0, len(parts), 2):
            if i < len(parts):
                title = parts[i] if i < len(parts) else f"Tab {i//2 + 1}"
                tab_content = parts[i + 1] if i + 1 < len(parts) else ""
                tabs_data.append({"title": title, "content": tab_content})

        # Generate tab navigation with semantic classes
        html = f'<div class="tabs" id="{tabs_id}">\n'
        html += '<div class="tabs-nav" role="tablist">\n'
        for idx, tab in enumerate(tabs_data):
            active = " active" if idx == 0 else ""
            tab_id = f"{tabs_id}-tab{idx}"
            pane_id = f"{tabs_id}-pane{idx}"

            html += f'<button class="tab-btn{active}" id="{tab_id}" '
            html += f'data-tab="{pane_id}" type="button" role="tab">'
            html += f'{tab["title"]}</button>\n'
        html += "</div>\n"

        # Generate tab content panes
        html += '<div class="tabs-content">\n'
        for idx, tab in enumerate(tabs_data):
            active = " active" if idx == 0 else ""
            pane_id = f"{tabs_id}-pane{idx}"

            html += f'<div class="tab-pane{active}" id="{pane_id}" role="tabpanel">\n'
            html += render_markdown_content(tab["content"]) + "\n"
            html += "</div>\n"
        html += "</div>\n"
        html += "</div>\n"

        # Pure JS tabs implementation
        html += f"""
<script>
(function() {{
    const tabs = document.getElementById('{tabs_id}');
    const buttons = tabs.querySelectorAll('.tab-btn');
    const panes = tabs.querySelectorAll('.tab-pane');

    buttons.forEach(btn => {{
        btn.addEventListener('click', () => {{
            const targetId = btn.getAttribute('data-tab');
            buttons.forEach(b => b.classList.remove('active'));
            panes.forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(targetId).classList.add('active');
        }});
    }});
}})();
</script>
"""

        return html

    return re.sub(pattern, replace_tabs, text, flags=re.DOTALL)


def parse_navbar_blocks(text: str) -> str:
    """
    Parse :::navbar
    Brand: My Website

    [Home](/)
    [About](/about)
    :::

    Uses semantic class names - styling provided by theme CSS.
    """
    pattern = r":::navbar\n(.*?)\n:::"

    def replace_navbar(match):
        content = match.group(1)
        lines = content.split("\n")

        brand = "Brand"
        links_html = ""

        for line in lines:
            line = line.strip()
            if line.startswith("Brand:"):
                brand = line.split(":", 1)[1].strip()
            elif line.startswith("[") and "](" in line:
                # Extract link: [Text](url)
                link_match = re.match(r"\[(.*?)\]\((.*?)\)", line)
                if link_match:
                    link_text = link_match.group(1)
                    url = link_match.group(2)
                    links_html += f'<li class="nav-item"><a class="nav-link" href="{url}">{link_text}</a></li>\n'

        html = '<nav class="navbar">\n'
        html += '<div class="container">\n'
        html += f'<a class="navbar-brand" href="/">{brand}</a>\n'
        html += '<ul class="nav-list">\n'
        html += links_html
        html += "</ul>\n"
        html += "</div>\n"
        html += "</nav>\n"

        return html

    return re.sub(pattern, replace_navbar, text, flags=re.DOTALL)


def parse_sidenav_blocks(text: str) -> str:
    """
    Parse :::sidenav left
    [Home](/)
    [Elements](/elements)
    :::

    Uses semantic class names - styling provided by theme CSS.
    """
    pattern = r":::sidenav (left|right)\n(.*?)\n:::"

    def replace_sidenav(match):
        side = match.group(1)
        content = match.group(2)
        lines = content.split("\n")

        html = f'<nav class="sidenav sidenav-{side}">\n'

        for line in lines:
            line = line.strip()
            if line.startswith("[") and "](" in line:
                # Extract link: [Text](url)
                link_match = re.match(r"\[(.*?)\]\((.*?)\)", line)
                if link_match:
                    link_text = link_match.group(1)
                    url = link_match.group(2)
                    html += f'<a href="{url}" class="sidenav-link">{link_text}</a>\n'
            elif line.startswith("- ["):
                # List item with link: - [Text](url)
                link_match = re.search(r"\[(.*?)\]\((.*?)\)", line)
                if link_match:
                    link_text = link_match.group(1)
                    url = link_match.group(2)
                    html += f'<a href="{url}" class="sidenav-link">{link_text}</a>\n'
            elif line.startswith("#"):
                # Heading
                html += f'<div class="sidenav-heading">{line[1:].strip()}</div>\n'

        html += "</nav>\n"

        return html

    return re.sub(pattern, replace_sidenav, text, flags=re.DOTALL)


def parse_header_blocks(text: str) -> str:
    """
    Parse :::header
    # Title
    Subtitle
    :::

    Uses semantic class names - styling provided by theme CSS.
    """
    pattern = r":::header\n(.*?)\n:::"

    def replace_header(match):
        content = match.group(1)
        return f'<header class="page-header">\n{content}\n</header>\n'

    return re.sub(pattern, replace_header, text, flags=re.DOTALL)


def parse_footer_blocks(text: str) -> str:
    """
    Parse :::footer
    Content
    :::

    Uses semantic class names - styling provided by theme CSS.
    """
    pattern = r":::footer\n(.*?)\n:::"

    def replace_footer(match):
        content = match.group(1)
        html = '<footer class="page-footer">\n'
        html += '<div class="container">\n'
        html += content + "\n"
        html += "</div>\n"
        html += "</footer>\n"
        return html

    return re.sub(pattern, replace_footer, text, flags=re.DOTALL)


# ============ INTERACTIVE COMPONENTS ============


def parse_modal_blocks(text: str) -> str:
    """
    Parse :::modal blocks - creates native <dialog> modals

    Syntax:
        :::modal #modal-id
        trigger: [Open Modal] (button success)
        title: Modal Title
        ---
        Modal content here (supports markdown)
        :::

    Uses native HTML <dialog> element - no framework needed.
    """
    pattern = r":::modal (#[\w-]+)\ntrigger:\s*\[(.+?)\](?:\s*\(button(?:\s+(primary|secondary|success|danger|warning|info))?\))?\ntitle:\s*(.+?)\n---\n(.*?)\n:::(?!\w)"

    def replace_modal(match):
        modal_id = match.group(1)[1:]  # Remove # prefix
        trigger_text = match.group(2)
        btn_style = match.group(3) or "primary"
        title = match.group(4)
        content = match.group(5)

        # Process content as markdown
        content_html = render_markdown_content(content)

        html = f"""<button class="btn btn-{btn_style}" onclick="document.getElementById('{modal_id}').showModal()">{trigger_text}</button>
<dialog id="{modal_id}" class="modal">
<div class="modal-content">
<div class="modal-header">
<h3 class="modal-title">{title}</h3>
<button class="modal-close" onclick="document.getElementById('{modal_id}').close()">&times;</button>
</div>
<div class="modal-body">
{content_html}
</div>
</div>
</dialog>
"""
        return html

    return re.sub(pattern, replace_modal, text, flags=re.DOTALL)


def parse_hidden_blocks(text: str) -> str:
    """
    Parse :::hidden blocks - content that can be toggled

    Syntax:
        :::hidden #section-id
        Hidden content here
        :::

    Use with @toggle trigger to show/hide.
    """
    pattern = r":::hidden (#[\w-]+)\n(.*?)\n:::(?!\w)"

    def replace_hidden(match):
        section_id = match.group(1)[1:]  # Remove # prefix
        content = match.group(2)

        # Process content as markdown
        content_html = render_markdown_content(content)

        return f'<div id="{section_id}" class="hidden-section" style="display: none;">\n{content_html}\n</div>\n'

    return re.sub(pattern, replace_hidden, text, flags=re.DOTALL)


def parse_result_blocks(text: str) -> str:
    """
    Parse :::result blocks - named target areas for HTMX responses

    Syntax:
        :::result users
        Loading users...
        :::

    Creates a named target div that can be referenced with @name syntax:
        => Load Users -> /api/users -> @users

    The @users reference gets converted to #result-users internally.
    This keeps markdown pure - no HTML IDs in content files.
    """
    pattern = r":::result\s+([\w-]+)\n(.*?)\n:::(?!\w)"

    def replace_result(match):
        result_name = match.group(1)
        content = match.group(2)

        # Process content as markdown
        content_html = render_markdown_content(content) if content.strip() else ""

        return f'<div id="result-{result_name}" class="result-area">\n{content_html}\n</div>\n'

    return re.sub(pattern, replace_result, text, flags=re.DOTALL)


def parse_calc_blocks(text: str) -> str:
    """
    Parse :::calc blocks - client-side calculations (no server needed)

    Syntax:
        :::calc #calc-id
        ? Voltage (number) -> V
        ? Current (number) -> I
        ---
        R = V / I
        ---
        > Result: Resistance = {R} Ω
        :::

    Library generates JavaScript - user never writes JS.
    Inputs with -> define variables, formula calculates, result displays.
    """
    pattern = r":::calc(?:\s+(#[\w-]+))?\n(.*?)\n---\n(.*?)\n---\n(.*?)\n:::(?!\w)"

    def replace_calc(match):
        import hashlib

        calc_id = (
            match.group(1)[1:]
            if match.group(1)
            else f"calc-{hashlib.md5(match.group(0).encode()).hexdigest()[:8]}"
        )
        # Sanitize ID for JavaScript function name (hyphens not allowed)
        js_func_name = calc_id.replace("-", "_")
        inputs_section = match.group(2)
        formula_section = match.group(3).strip()
        result_template = match.group(4).strip()

        # Parse inputs: ? Label (type) -> varname
        inputs = []
        input_pattern = (
            r"^\?\s*(.+?)\s*\((number|text)(?:\s+(\d+)-(\d+))?\)\s*->\s*(\w+)$"
        )
        for line in inputs_section.strip().split("\n"):
            m = re.match(input_pattern, line.strip())
            if m:
                inputs.append(
                    {
                        "label": m.group(1),
                        "type": m.group(2),
                        "min": m.group(3),
                        "max": m.group(4),
                        "var": m.group(5),
                    }
                )

        # Build form HTML
        html = f'<div class="calc-container" id="{calc_id}">\n'
        html += '<div class="calc-inputs">\n'

        for inp in inputs:
            min_attr = f' min="{inp["min"]}"' if inp["min"] else ""
            max_attr = f' max="{inp["max"]}"' if inp["max"] else ""
            html += f"""<div class="form-group">
<label class="form-label">{inp['label']}</label>
<input type="{inp['type']}" class="form-input calc-input" data-var="{inp['var']}"{min_attr}{max_attr} placeholder="{inp['label']}">
</div>
"""

        html += "</div>\n"
        html += f'<button class="btn btn-primary calc-btn" onclick="calculate_{js_func_name}()">Calculate</button>\n'
        html += f'<div class="calc-result" id="{calc_id}-result"></div>\n'
        html += "</div>\n"

        # Build JavaScript
        js_vars = ", ".join(
            [
                f'{inp["var"]} = parseFloat(document.querySelector("#{calc_id} [data-var={inp["var"]}]").value) || 0'
                for inp in inputs
            ]
        )

        # Parse formula (e.g., "R = V / I")
        formula_parts = formula_section.split("=")
        if len(formula_parts) == 2:
            result_var = formula_parts[0].strip()
            expression = formula_parts[1].strip()
        else:
            result_var = "result"
            expression = formula_section

        # Process result template - replace {var} with actual values
        # Convert markdown result template to display format
        result_display = result_template
        if result_display.startswith(">"):
            result_display = result_display[1:].strip()

        html += f"""<script>
function calculate_{js_func_name}() {{
    let {js_vars};
    let {result_var} = {expression};

    // Format result
    let display = {result_var};
    if (Math.abs({result_var}) >= 1000000) display = ({result_var}/1000000).toFixed(2) + ' M';
    else if (Math.abs({result_var}) >= 1000) display = ({result_var}/1000).toFixed(2) + ' k';
    else display = {result_var}.toFixed(4);

    // Update result
    let template = `{result_display}`;
    template = template.replace(/\\{{{result_var}\\}}/g, display);
    document.getElementById('{calc_id}-result').innerHTML = '<div class="alert alert-success">' + template + '</div>';
}}
</script>
"""
        return html

    return re.sub(pattern, replace_calc, text, flags=re.DOTALL)


# ============ INLINE PARSERS ============


def parse_callout_alerts(text: str) -> str:
    """
    Parse multi-line callout alerts:
    > [!INFO] Optional Title
    > Line 1
    > Line 2

    Uses semantic class names - styling provided by theme CSS.
    """
    # Map alert types to semantic classes
    alert_types = {
        "INFO": "info",
        "SUCCESS": "success",
        "WARNING": "warning",
        "ERROR": "error",
        "DANGER": "error",
    }

    # Pattern to match multi-line blockquote with alert marker
    # > [!TYPE] Optional Title
    # > Content line 1
    # > Content line 2
    # Also matches single-line alerts (no continuation lines)
    pattern = r"> \[!(INFO|SUCCESS|WARNING|ERROR|DANGER)\]([^\n]*)\n((?:> [^\n]*\n?)+)?"

    def replace_alert(match):
        alert_type_key = match.group(1)
        title = match.group(2).strip()  # Optional title after [!TYPE]
        content_lines = match.group(3)  # None for single-line alerts

        # Get semantic alert class
        alert_class = alert_types.get(alert_type_key, "info")

        content = ""
        if content_lines:
            # Remove > prefix from each line and join
            lines = []
            for line in content_lines.split("\n"):
                if line.startswith("> "):
                    lines.append(line[2:])  # Remove "> "
                elif line.strip():  # Non-empty line without >
                    lines.append(line)

            content = "\n".join(lines).strip()

        # Build alert HTML with semantic classes
        html = f'<div class="alert alert-{alert_class}" role="alert">\n'

        if title and content:
            # Has both title and body content
            html += f'<div class="alert-title">{title}</div>\n'
            content_html = _md_renderer.render(content)
            html += content_html
        elif title:
            # Single-line alert: title IS the content
            content_html = _md_renderer.render(title)
            html += content_html
        elif content:
            content_html = _md_renderer.render(content)
            html += content_html

        html += "</div>\n"

        return html

    return re.sub(pattern, replace_alert, text, flags=re.MULTILINE)


def parse_htmx_buttons(text: str) -> str:
    """
    Parse HTMX-enabled buttons with arrow syntax (action triggers)

    Syntax:
        => Submit -> /api/submit                    # POST by default
        => Load More -> /api/more (get)             # GET request
        => Delete -> /api/delete (delete)           # DELETE request
        => Delete -> /api/delete (delete, confirm)  # With confirmation
        => Save (success) -> /api/save              # Styled + action
        => Update -> /api/update (put) -> @result   # Method + named target

    Target syntax (pure markdown, no HTML IDs):
        -> @name    References :::result name block (becomes #result-name)

    Library automatically adds:
        - hx-post/hx-get/hx-delete/hx-put based on method
        - hx-target for response placement
        - hx-swap for smooth updates
        - hx-confirm for confirmation dialogs
        - Loading indicator
    """
    # Pattern: => Text [(style)] -> /endpoint [(method[, confirm])] [-> @target]
    # Examples:
    #   => Submit -> /api/submit
    #   => Save (success) -> /api/save
    #   => Delete -> /api/delete (delete, confirm)
    #   => Load -> /api/load (get) -> @content

    # Full pattern with optional style, method, confirm, and separate target
    pattern = r"^=> (.+?)(?: \((primary|secondary|success|danger|warning|info)\))? -> (/[^\s]+)(?: \(([^)]+)\))?(?: -> @([\w-]+))?$"

    def replace_htmx_button(match):
        btn_text = match.group(1).strip()
        btn_style = match.group(2) or "primary"
        endpoint = match.group(3)
        options = match.group(4)  # e.g., "delete, confirm"
        target_name = match.group(5)  # e.g., "users" from @users

        # Parse options
        method = "post"  # Default
        confirm = False

        if options:
            parts = [p.strip() for p in options.split(",")]
            for part in parts:
                if part in ("get", "post", "put", "delete", "patch"):
                    method = part
                elif part == "confirm":
                    confirm = True

        # Build HTMX attributes
        hx_attr = f'hx-{method}="{endpoint}"'

        if target_name:
            # @name syntax -> #result-name (references :::result name block)
            hx_attr += f' hx-target="#result-{target_name}"'
            hx_attr += ' hx-swap="innerHTML"'
        else:
            hx_attr += ' hx-target="this"'
            hx_attr += ' hx-swap="outerHTML"'

        hx_attr += ' hx-indicator="closest .htmx-indicator"'

        if confirm:
            confirm_msg = f"Are you sure you want to {btn_text.lower()}?"
            hx_attr += f' hx-confirm="{confirm_msg}"'

        return f'<button class="btn btn-{btn_style} htmx-request" {hx_attr}>{btn_text}</button>'

    return re.sub(pattern, replace_htmx_button, text, flags=re.MULTILINE)


def parse_htmx_button_links(text: str) -> str:
    """
    Parse HTMX-enabled button links

    Syntax:
        [Load Content](/api/content) (button) @click
        [Preview](/api/preview) (button success) @hover
        [Submit](/api/submit) (button) @click -> #result

    Triggers (REQUIRED for HTMX behavior):
        @click - Click to load
        @hover - Hover to load (mouseenter)
        @load  - Load immediately on page load

    Without a trigger, use regular button links: [Text](url) (button)
    """
    # Pattern: [Text](url) (button [style]) @trigger [-> #target]
    # Note: @trigger is REQUIRED - without it, use regular button links
    pattern = r"\[(.+?)\]\((/[^\)]+)\) \(button(?: (primary|secondary|success|danger|warning|info))?\) @(click|hover|load)(?: -> (#[^\s]+))?"

    def replace_htmx_link(match):
        link_text = match.group(1)
        endpoint = match.group(2)
        btn_style = match.group(3) or "primary"
        trigger = match.group(4)  # Now required, not optional
        target = match.group(5)

        # Map trigger to HTMX trigger
        trigger_map = {"click": "click", "hover": "mouseenter", "load": "load"}
        hx_trigger = trigger_map.get(trigger, "click")

        # Build attributes
        attrs = f'hx-get="{endpoint}" hx-trigger="{hx_trigger}"'

        if target:
            attrs += f' hx-target="{target}"'
        else:
            attrs += ' hx-target="this"'

        attrs += ' hx-swap="innerHTML"'

        return f'<a href="#" class="btn btn-{btn_style} htmx-request" {attrs}>{link_text}</a>'

    return re.sub(pattern, replace_htmx_link, text)


def parse_toggle_triggers(text: str) -> str:
    """
    Parse @toggle triggers for show/hide interactions

    Syntax:
        => Show Details @toggle -> #details         # Button that toggles visibility
        [Show More]() @toggle -> #more-content      # Link that toggles

    The library generates JavaScript - user never writes JS.
    Uses data attributes for clean, declarative markup.
    """
    # Button with toggle: => Text @toggle -> #target
    pattern_btn = r"^=> (.+?) @toggle -> (#[\w-]+)$"

    def replace_toggle_btn(match):
        btn_text = match.group(1).strip()
        target_id = match.group(2)[1:]  # Remove # prefix

        # Check for style in button text
        style = "primary"
        text = btn_text
        style_match = re.match(
            r"(.+?) \((primary|secondary|success|danger|warning|info)\)", btn_text
        )
        if style_match:
            text = style_match.group(1)
            style = style_match.group(2)

        return f"""<button class="btn btn-{style}" onclick="(function(el){{
    const target = document.getElementById('{target_id}');
    if(target) {{
        target.style.display = target.style.display === 'none' ? 'block' : 'none';
        el.textContent = target.style.display === 'none' ? '{text}' : 'Hide';
    }}
}})(this)">{text}</button>"""

    text = re.sub(pattern_btn, replace_toggle_btn, text, flags=re.MULTILINE)

    # Link with toggle: [Text]() @toggle -> #target
    pattern_link = r"\[(.+?)\]\(\) @toggle -> (#[\w-]+)"

    def replace_toggle_link(match):
        link_text = match.group(1)
        target_id = match.group(2)[1:]  # Remove # prefix

        return f"""<a href="#" class="toggle-link" onclick="(function(el, e){{
    e.preventDefault();
    const target = document.getElementById('{target_id}');
    if(target) {{
        target.style.display = target.style.display === 'none' ? 'block' : 'none';
    }}
}})(this, event)">{link_text}</a>"""

    text = re.sub(pattern_link, replace_toggle_link, text)

    return text


def parse_copy_triggers(text: str) -> str:
    """
    Parse @copy triggers for clipboard copy interactions

    Syntax:
        => Copy Code @copy -> #code-block           # Button copies content of #code-block
        => Copy @copy "Static text to copy"         # Button copies literal text
        [Copy]() @copy -> #result                   # Link that copies

    Uses modern Clipboard API - library handles browser compatibility.
    """
    # Button copying from element: => Text @copy -> #target
    pattern_btn_target = r"^=> (.+?) @copy -> (#[\w-]+)$"

    def replace_copy_btn_target(match):
        btn_text = match.group(1).strip()
        target_id = match.group(2)[1:]  # Remove # prefix

        # Check for style in button text
        style = "secondary"
        text = btn_text
        style_match = re.match(
            r"(.+?) \((primary|secondary|success|danger|warning|info)\)", btn_text
        )
        if style_match:
            text = style_match.group(1)
            style = style_match.group(2)

        return f"""<button class="btn btn-{style} copy-btn" onclick="(function(el){{
    const target = document.getElementById('{target_id}');
    if(target) {{
        const text = target.innerText || target.textContent;
        navigator.clipboard.writeText(text).then(function(){{
            const original = el.textContent;
            el.textContent = 'Copied!';
            setTimeout(function(){{ el.textContent = original; }}, 2000);
        }});
    }}
}})(this)">{text}</button>"""

    text = re.sub(pattern_btn_target, replace_copy_btn_target, text, flags=re.MULTILINE)

    # Button copying literal text: => Text @copy "content"
    pattern_btn_literal = r'^=> (.+?) @copy "([^"]+)"$'

    def replace_copy_btn_literal(match):
        btn_text = match.group(1).strip()
        copy_content = match.group(2)

        # Check for style in button text
        style = "secondary"
        text = btn_text
        style_match = re.match(
            r"(.+?) \((primary|secondary|success|danger|warning|info)\)", btn_text
        )
        if style_match:
            text = style_match.group(1)
            style = style_match.group(2)

        # Escape content for JavaScript
        escaped_content = copy_content.replace("'", "\\'").replace("\n", "\\n")

        return f"""<button class="btn btn-{style} copy-btn" onclick="(function(el){{
    navigator.clipboard.writeText('{escaped_content}').then(function(){{
        const original = el.textContent;
        el.textContent = 'Copied!';
        setTimeout(function(){{ el.textContent = original; }}, 2000);
    }});
}})(this)">{text}</button>"""

    text = re.sub(
        pattern_btn_literal, replace_copy_btn_literal, text, flags=re.MULTILINE
    )

    # Link with copy: [Text]() @copy -> #target
    pattern_link = r"\[(.+?)\]\(\) @copy -> (#[\w-]+)"

    def replace_copy_link(match):
        link_text = match.group(1)
        target_id = match.group(2)[1:]  # Remove # prefix

        return f"""<a href="#" class="copy-link" onclick="(function(el, e){{
    e.preventDefault();
    const target = document.getElementById('{target_id}');
    if(target) {{
        const text = target.innerText || target.textContent;
        navigator.clipboard.writeText(text).then(function(){{
            const original = el.textContent;
            el.textContent = 'Copied!';
            setTimeout(function(){{ el.textContent = original; }}, 2000);
        }});
    }}
}})(this, event)">{link_text}</a>"""

    text = re.sub(pattern_link, replace_copy_link, text)

    return text


def parse_event_triggers(text: str) -> str:
    """
    Parse standalone event triggers for HTMX content loading

    Syntax:
        @load /api/content -> #target               # Load on page load
        @click /api/toggle -> #target               # Click handler (needs element)
        @interval /api/refresh -> #target (5s)      # Polling every 5s
        @revealed /api/lazy -> #target              # Load when scrolled into view

    These create invisible trigger elements or can be attached to the next element.
    """
    # Pattern: @trigger /endpoint -> #target [(interval)]
    pattern = (
        r"^@(load|revealed|intersect)(?: (/[^\s]+))?(?: -> (#[^\s]+))?(?: \((\d+s)\))?$"
    )

    def replace_trigger(match):
        trigger_type = match.group(1)
        endpoint = match.group(2)
        target = match.group(3)
        interval = match.group(4)

        if not endpoint:
            return match.group(0)

        # Build HTMX trigger element
        trigger_event = trigger_type
        if trigger_type == "intersect":
            trigger_event = "intersect once"

        attrs = f'hx-get="{endpoint}" hx-trigger="{trigger_event}"'

        if target:
            attrs += f' hx-target="{target}"'

        attrs += ' hx-swap="innerHTML"'

        if interval:
            attrs = attrs.replace(
                f'hx-trigger="{trigger_event}"', f'hx-trigger="every {interval}"'
            )

        # Invisible trigger element
        return f'<div class="htmx-trigger" {attrs} style="display:none;"></div>'

    return re.sub(pattern, replace_trigger, text, flags=re.MULTILINE)


def parse_buttons(text: str) -> str:
    """
    Parse => Button Text
    Parse => Button Text (success)
    Parse => Button Text (danger)

    Uses semantic class names - styling provided by theme CSS.
    """
    # With type: => Text (type)
    pattern1 = (
        r"^=> (.+?) \((primary|secondary|success|danger|warning|info|light|dark)\)$"
    )

    def replace_button_typed(match):
        btn_text = match.group(1)
        btn_type = match.group(2)
        return f'<button class="btn btn-{btn_type}">{btn_text}</button>'

    text = re.sub(pattern1, replace_button_typed, text, flags=re.MULTILINE)

    # Without type (default primary): => Text
    pattern2 = r"^=> (.+)$"

    def replace_button(match):
        btn_text = match.group(1).strip()
        # Skip if it already has parentheses (was processed above)
        if "(" in btn_text and ")" in btn_text:
            return match.group(0)
        return f'<button class="btn btn-primary">{btn_text}</button>'

    text = re.sub(pattern2, replace_button, text, flags=re.MULTILINE)

    return text


def parse_button_links(text: str) -> str:
    """
    Parse [Text](url) (button)
    Parse [Text](url) (button success)

    Uses semantic class names - styling provided by theme CSS.
    """
    # With button type
    pattern1 = (
        r"\[(.+?)\]\((.+?)\) \(button (primary|secondary|success|danger|warning|info)\)"
    )

    def replace_button_link_typed(match):
        link_text = match.group(1)
        url = match.group(2)
        btn_type = match.group(3)
        return f'<a href="{url}" class="btn btn-{btn_type}">{link_text}</a>'

    text = re.sub(pattern1, replace_button_link_typed, text)

    # Just (button) - default primary
    pattern2 = r"\[(.+?)\]\((.+?)\) \(button\)"

    def replace_button_link(match):
        link_text = match.group(1)
        url = match.group(2)
        return f'<a href="{url}" class="btn btn-primary">{link_text}</a>'

    text = re.sub(pattern2, replace_button_link, text)

    return text


def parse_inputs(text: str) -> str:
    """
    Parse ? Label (text)
    Parse ? Label (email)
    Parse ? Label (number 1-100)
    Parse ? Label (text) [Custom placeholder]
    Parse ? Label (text) [name:field_name]  # From form blocks

    Uses semantic class names - styling provided by theme CSS.
    """

    # Helper to extract name attribute from placeholder/options
    def extract_name(placeholder_or_options):
        """Extract [name:xxx] and return (name_attr, clean_text)"""
        if not placeholder_or_options:
            return "", placeholder_or_options

        name_match = re.search(r"\[name:(\w+)\]", placeholder_or_options)
        if name_match:
            name = name_match.group(1)
            clean = re.sub(r"\s*\[name:\w+\]", "", placeholder_or_options).strip()
            return f' name="{name}"', clean if clean else None
        return "", placeholder_or_options

    # Number/range with min-max and optional placeholder/name
    pattern1 = (
        r"^\? (.+?) \((number|range) (\d+)-(\d+)\)(?: \[(.+?)\])?(?: \[name:(\w+)\])?$"
    )

    def replace_input_minmax(match):
        label = match.group(1)
        input_type = match.group(2)
        min_val = match.group(3)
        max_val = match.group(4)
        placeholder_raw = match.group(5)
        explicit_name = match.group(6)

        # Handle name from either explicit [name:] or embedded in placeholder
        name_attr = ""
        placeholder = label

        if explicit_name:
            name_attr = f' name="{explicit_name}"'
            placeholder = placeholder_raw if placeholder_raw else label
        elif placeholder_raw:
            name_attr, placeholder = extract_name(placeholder_raw)
            if not placeholder:
                placeholder = label

        input_class = "form-range" if input_type == "range" else "form-input"

        html = '<div class="form-group">\n'
        html += f'<label class="form-label">{label}</label>\n'
        html += f'<input type="{input_type}" class="{input_class}"{name_attr} min="{min_val}" max="{max_val}" placeholder="{placeholder}">\n'
        html += "</div>\n"

        return html

    text = re.sub(pattern1, replace_input_minmax, text, flags=re.MULTILINE)

    # Simple inputs with optional placeholder and/or name
    pattern2 = r"^\? (.+?) \((text|email|password|number|range|tel|url|date|time)\)(?: \[(.+?)\])?(?: \[name:(\w+)\])?$"

    def replace_input(match):
        label = match.group(1)
        input_type = match.group(2)
        placeholder_raw = match.group(3)
        explicit_name = match.group(4)

        # Handle name from either explicit [name:] or embedded in placeholder
        name_attr = ""
        placeholder = label

        if explicit_name:
            name_attr = f' name="{explicit_name}"'
            placeholder = placeholder_raw if placeholder_raw else label
        elif placeholder_raw:
            name_attr, placeholder = extract_name(placeholder_raw)
            if not placeholder:
                placeholder = label

        input_class = "form-range" if input_type == "range" else "form-input"

        html = '<div class="form-group">\n'
        html += f'<label class="form-label">{label}</label>\n'
        html += f'<input type="{input_type}" class="{input_class}"{name_attr} placeholder="{placeholder}">\n'
        html += "</div>\n"

        return html

    text = re.sub(pattern2, replace_input, text, flags=re.MULTILINE)

    return text


def parse_textareas(text: str) -> str:
    """
    Parse ?? Label
    Parse ?? Label [Custom placeholder]
    Parse ?? Label [name:field_name]  # From form blocks

    Uses semantic class names - styling provided by theme CSS.
    """
    # Pattern with optional placeholder and/or name
    pattern = r"^\?\? (.+?)(?: \[([^\]]+)\])?(?: \[name:(\w+)\])?$"

    def replace_textarea(match):
        label = match.group(1)
        placeholder_raw = match.group(2)
        explicit_name = match.group(3)

        # Handle name attribute
        name_attr = ""
        placeholder = label

        if explicit_name:
            name_attr = f' name="{explicit_name}"'
            placeholder = placeholder_raw if placeholder_raw else label
        elif placeholder_raw:
            # Check if placeholder contains [name:xxx]
            name_match = re.search(r"name:(\w+)", placeholder_raw)
            if name_match:
                name_attr = f' name="{name_match.group(1)}"'
                placeholder = (
                    re.sub(r"\s*name:\w+", "", placeholder_raw).strip() or label
                )
            else:
                placeholder = placeholder_raw

        html = '<div class="form-group">\n'
        html += f'<label class="form-label">{label}</label>\n'
        html += f'<textarea class="form-textarea"{name_attr} rows="4" placeholder="{placeholder}"></textarea>\n'
        html += "</div>\n"

        return html

    text = re.sub(pattern, replace_textarea, text, flags=re.MULTILINE)

    return text


def parse_selects(text: str) -> str:
    """
    Parse dropdown/select with options

    Inline syntax: Select: Label | Option1 | Option2 | Option3
    With name:     Select: Label | Option1 | Option2 [name:field]

    Multi-line syntax:
    Select: Label
    - Option 1
    - Option 2
    - Option 3

    Uses semantic class names - styling provided by theme CSS.
    """

    # Helper to extract name from options string
    def extract_name_from_options(options_str):
        """Extract [name:xxx] from end of options string"""
        name_match = re.search(r"\s*\[name:(\w+)\]\s*$", options_str)
        if name_match:
            name = name_match.group(1)
            clean = re.sub(r"\s*\[name:\w+\]\s*$", "", options_str)
            return f' name="{name}"', clean
        return "", options_str

    # First try inline syntax with pipe separator
    pattern1 = r"^Select: (.+?) \| (.+)$"

    def replace_select_inline(match):
        label = match.group(1).strip()
        options_str = match.group(2)

        # Check for name attribute at end
        name_attr, options_str = extract_name_from_options(options_str)

        options = [opt.strip() for opt in options_str.split("|")]

        html = '<div class="form-group">\n'
        html += f'<label class="form-label">{label}</label>\n'
        html += f'<select class="form-select"{name_attr}>\n'
        html += "<option selected disabled>Select one...</option>\n"
        for option in options:
            if option:  # Skip empty options
                html += f'<option value="{option.lower().replace(" ", "_")}">{option}</option>\n'
        html += "</select>\n"
        html += "</div>\n"

        return html

    text = re.sub(pattern1, replace_select_inline, text, flags=re.MULTILINE)

    # Then try multi-line syntax with list items
    pattern2 = r"^Select: (.+?)(?: \[name:(\w+)\])?\n((?:- .+\n?)+)"

    def replace_select_multiline(match):
        label = match.group(1).strip()
        name = match.group(2)
        options_text = match.group(3)

        name_attr = f' name="{name}"' if name else ""

        # Extract list items
        options = re.findall(r"^- (.+)$", options_text, re.MULTILINE)

        html = '<div class="form-group">\n'
        html += f'<label class="form-label">{label}</label>\n'
        html += f'<select class="form-select"{name_attr}>\n'
        html += "<option selected disabled>Select one...</option>\n"
        for option in options:
            opt = option.strip()
            html += f'<option value="{opt.lower().replace(" ", "_")}">{opt}</option>\n'
        html += "</select>\n"
        html += "</div>\n"

        return html

    text = re.sub(pattern2, replace_select_multiline, text, flags=re.MULTILINE)

    # Finally, simple select without options (backward compatibility)
    pattern3 = r"^Select: (.+)$"

    def replace_select_simple(match):
        label = match.group(1)

        # Check for name in label
        name_attr = ""
        name_match = re.search(r"\s*\[name:(\w+)\]", label)
        if name_match:
            name_attr = f' name="{name_match.group(1)}"'
            label = re.sub(r"\s*\[name:\w+\]", "", label)

        html = '<div class="form-group">\n'
        html += f'<label class="form-label">{label}</label>\n'
        html += f'<select class="form-select"{name_attr}>\n'
        html += "<option selected>Select one...</option>\n"
        html += "</select>\n"
        html += "</div>\n"

        return html

    text = re.sub(pattern3, replace_select_simple, text, flags=re.MULTILINE)

    return text


def parse_accordion_blocks(text: str) -> str:
    """
    Parse :::accordion
    Question 1
    ---
    Answer 1
    ---
    Question 2
    ---
    Answer 2
    :::

    Creates accordion with semantic class names.
    Uses pure CSS/JS for framework-agnostic implementation.
    """
    pattern = r":::accordion\n(.*?)\n:::(?!\w)"

    accordion_counter = 0

    def replace_accordion(match):
        nonlocal accordion_counter
        accordion_counter += 1
        accordion_id = f"accordion{accordion_counter}"

        content = match.group(1)

        # Split by --- but skip --- inside code blocks
        # First extract code blocks temporarily
        temp_code_blocks = []

        def save_temp_code(m):
            temp_code_blocks.append(m.group(0))
            return f"__TEMP_CODE_{len(temp_code_blocks)-1}__"

        content_safe = re.sub(r"```.*?```", save_temp_code, content, flags=re.DOTALL)

        # Now split safely
        parts = [p.strip() for p in content_safe.split("\n---\n")]

        # Restore code blocks in each part
        for i in range(len(parts)):
            for j, code in enumerate(temp_code_blocks):
                parts[i] = parts[i].replace(f"__TEMP_CODE_{j}__", code)

        # Parse pairs of (question, answer)
        items = []
        for i in range(0, len(parts), 2):
            if i < len(parts):
                question = parts[i] if i < len(parts) else f"Item {i//2 + 1}"
                answer = parts[i + 1] if i + 1 < len(parts) else ""
                items.append({"question": question, "answer": answer})

        # Generate accordion HTML with semantic classes
        html = f'<div class="accordion" id="{accordion_id}">\n'
        for idx, item in enumerate(items):
            collapse_id = f"{accordion_id}-collapse{idx}"
            open_attr = " open" if idx == 0 else ""

            html += f'<details class="accordion-item"{open_attr}>\n'
            html += f'<summary class="accordion-header">{item["question"]}</summary>\n'
            html += '<div class="accordion-body">\n'
            html += render_markdown_content(item["answer"]) + "\n"
            html += "</div>\n"
            html += "</details>\n"
        html += "</div>\n"

        return html

    return re.sub(pattern, replace_accordion, text, flags=re.DOTALL)


def parse_checkboxes(text: str) -> str:
    """
    Parse [] Label - unchecked checkbox
    Parse [x] Label - checked checkbox

    Uses semantic class names - styling provided by theme CSS.
    """
    # Unchecked checkbox
    pattern1 = r"^\[\] (.+)$"

    def replace_unchecked(match):
        label = match.group(1)
        html = '<div class="form-check">\n'
        html += f'<input class="form-checkbox" type="checkbox" id="checkbox-{hash(label)}">\n'
        html += f'<label class="form-check-label" for="checkbox-{hash(label)}">{label}</label>\n'
        html += "</div>\n"
        return html

    text = re.sub(pattern1, replace_unchecked, text, flags=re.MULTILINE)

    # Checked checkbox
    pattern2 = r"^\[x\] (.+)$"

    def replace_checked(match):
        label = match.group(1)
        html = '<div class="form-check">\n'
        html += f'<input class="form-checkbox" type="checkbox" id="checkbox-{hash(label)}" checked>\n'
        html += f'<label class="form-check-label" for="checkbox-{hash(label)}">{label}</label>\n'
        html += "</div>\n"
        return html

    text = re.sub(pattern2, replace_checked, text, flags=re.MULTILINE)

    return text


def parse_radio_buttons(text: str) -> str:
    """
    Parse () Label - unselected radio
    Parse (*) Label - selected radio

    Uses semantic class names - styling provided by theme CSS.
    """
    # Unselected radio
    pattern1 = r"^\(\) (.+)$"

    def replace_unselected(match):
        label = match.group(1)
        html = '<div class="form-check">\n'
        html += f'<input class="form-radio" type="radio" name="radioGroup" id="radio-{hash(label)}">\n'
        html += f'<label class="form-check-label" for="radio-{hash(label)}">{label}</label>\n'
        html += "</div>\n"
        return html

    text = re.sub(pattern1, replace_unselected, text, flags=re.MULTILINE)

    # Selected radio
    pattern2 = r"^\(\*\) (.+)$"

    def replace_selected(match):
        label = match.group(1)
        html = '<div class="form-check">\n'
        html += f'<input class="form-radio" type="radio" name="radioGroup" id="radio-{hash(label)}" checked>\n'
        html += f'<label class="form-check-label" for="radio-{hash(label)}">{label}</label>\n'
        html += "</div>\n"
        return html

    text = re.sub(pattern2, replace_selected, text, flags=re.MULTILINE)

    return text


def parse_badges(text: str) -> str:
    """
    Parse !!Text!! - default badge
    Parse !!Text:primary!! - colored badge (primary, secondary, success, danger, warning, info, light, dark)

    Uses semantic class names - styling provided by theme CSS.
    """
    # Colored badge
    pattern1 = r"!!(.+?):(.+?)!!"

    def replace_colored(match):
        badge_text = match.group(1)
        color = match.group(2)
        return f'<span class="badge badge-{color}">{badge_text}</span>'

    text = re.sub(pattern1, replace_colored, text)

    # Default badge
    pattern2 = r"!!(.+?)!!"

    def replace_default(match):
        badge_text = match.group(1)
        return f'<span class="badge badge-secondary">{badge_text}</span>'

    text = re.sub(pattern2, replace_default, text)

    return text


def parse_progress_bars(text: str) -> str:
    """
    Parse [progress 75%] - default progress bar
    Parse [progress 50% success] - colored progress bar

    Uses semantic class names - styling provided by theme CSS.
    """
    # Colored progress bar
    pattern1 = r"\[progress (\d+)% (\w+)\]"

    def replace_colored(match):
        value = match.group(1)
        color = match.group(2)
        html = '<div class="progress">\n'
        html += f'<div class="progress-bar progress-{color}" role="progressbar" '
        html += f'style="width: {value}%" aria-valuenow="{value}" aria-valuemin="0" aria-valuemax="100">'
        html += f"{value}%</div>\n"
        html += "</div>\n"
        return html

    text = re.sub(pattern1, replace_colored, text)

    # Default progress bar
    pattern2 = r"\[progress (\d+)%\]"

    def replace_default(match):
        value = match.group(1)
        html = '<div class="progress">\n'
        html += '<div class="progress-bar" role="progressbar" '
        html += f'style="width: {value}%" aria-valuenow="{value}" aria-valuemin="0" aria-valuemax="100">'
        html += f"{value}%</div>\n"
        html += "</div>\n"
        return html

    text = re.sub(pattern2, replace_default, text)

    return text


def parse_breadcrumbs(text: str) -> str:
    """
    Parse >> Home > Products > Category > Item
    Creates breadcrumb navigation.

    Uses semantic class names - styling provided by theme CSS.
    """
    pattern = r"^>> (.+)$"

    def replace_breadcrumb(match):
        items_text = match.group(1)
        items = [item.strip() for item in items_text.split(">")]

        html = '<nav class="breadcrumb-nav" aria-label="breadcrumb">\n'
        html += '<ol class="breadcrumb">\n'
        for idx, item in enumerate(items):
            if idx == len(items) - 1:
                # Last item is active
                html += f'<li class="breadcrumb-item active" aria-current="page">{item}</li>\n'
            else:
                html += f'<li class="breadcrumb-item"><a href="#">{item}</a></li>\n'
        html += "</ol>\n"
        html += "</nav>\n"

        return html

    text = re.sub(pattern, replace_breadcrumb, text, flags=re.MULTILINE)

    return text


def parse_pagination(text: str) -> str:
    """
    Parse << 1 2 3 4 5 >>
    Creates pagination component.

    Uses semantic class names - styling provided by theme CSS.
    """
    pattern = r"^<< (.+) >>$"

    def replace_pagination(match):
        pages_text = match.group(1)
        pages = [page.strip() for page in pages_text.split()]

        html = '<nav class="pagination-nav" aria-label="Page navigation">\n'
        html += '<ul class="pagination">\n'
        html += (
            '<li class="page-item"><a class="page-link" href="#">Previous</a></li>\n'
        )
        for page in pages:
            html += (
                f'<li class="page-item"><a class="page-link" href="#">{page}</a></li>\n'
            )
        html += '<li class="page-item"><a class="page-link" href="#">Next</a></li>\n'
        html += "</ul>\n"
        html += "</nav>\n"

        return html

    text = re.sub(pattern, replace_pagination, text, flags=re.MULTILINE)

    return text
