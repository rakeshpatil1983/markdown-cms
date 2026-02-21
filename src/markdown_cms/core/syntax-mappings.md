# Pure Text Syntax Mappings

**Philosophy: Write WHAT you want, not HOW it looks**

This markdown file defines how pure text syntax is converted to HTML.
Users can customize these mappings by placing `syntax-mappings.md` in their project root.

---

## Buttons

### Simple Button
**Pattern:** `^=> (.+)$`
**Template:** `<button class="btn btn-primary">{text}</button>`
**Flags:** MULTILINE
**Description:** Simple button with primary style
**Example:** `=> Click Me`

### Typed Button
**Pattern:** `^=> (.+?) \((primary|secondary|success|danger|warning|info|light|dark)\)$`
**Template:** `<button class="btn btn-{type}">{text}</button>`
**Flags:** MULTILINE
**Description:** Button with semantic type (success, danger, etc.)
**Example:** `=> Save (success)`

---

## Button Links

### Simple Button Link
**Pattern:** `\[(.+?)\]\((.+?)\) \(button\)`
**Template:** `<a href="{url}" class="btn btn-primary">{text}</a>`
**Description:** Link styled as button
**Example:** `[Home](/) (button)`

### Typed Button Link
**Pattern:** `\[(.+?)\]\((.+?)\) \(button (primary|secondary|success|danger|warning|info)\)`
**Template:** `<a href="{url}" class="btn btn-{type}">{text}</a>`
**Description:** Link styled as colored button
**Example:** `[Get Started](/start) (button success)`

---

## Cards

### Simple Card
**Pattern:** `:::card\n((?:(?!--- header ---|--- body ---|--- footer ---).)*)\n:::`
**Template:** `<div class="card"><div class="card-body">\n{content}\n</div></div>`
**Flags:** DOTALL
**Description:** Simple card container
**Example:**
```
:::card
# Card Title
Content here
:::
```

### Card with Sections
**Pattern:** `:::card\n(.*?)\n:::`
**Flags:** DOTALL
**Description:** Card with header/body/footer sections
**Sections:**
- **header:** `--- header ---` → `<div class="card-header">{content}</div>`
- **body:** `--- body ---` → `<div class="card-body">\n{content}\n</div>`
- **footer:** `--- footer ---` → `<div class="card-footer text-muted">{content}</div>`

**Example:**
```
:::card
--- header ---
Featured Item
--- body ---
# Special Offer
Content here
--- footer ---
Footer text
:::
```

---

## Panels

### Simple Panel
**Pattern:** `:::panel\n(.*?)\n:::`
**Template:** `<div class="panel p-4 bg-light rounded">\n{content}\n</div>`
**Flags:** DOTALL
**Description:** Panel/container for grouping content
**Example:**
```
:::panel
# Panel Title
Content here
:::
```

---

## Sections

### Simple Section
**Pattern:** `:::section\n(.*?)\n:::`
**Template:** `<section class="p-4 border-bottom">\n{content}\n</section>\n`
**Flags:** DOTALL
**Description:** Section divider
**Example:**
```
:::section
# Section Title
Content here
:::
```

---

## Columns/Grid

### Multi-Column Layout
**Pattern:** `:::columns (\d+)\n(.*?)\n:::`
**Flags:** DOTALL
**Description:** Multi-column grid layout
**Separator:** `---`
**Grid Classes:**
- 2 columns: `col-md-6`
- 3 columns: `col-md-4`
- 4 columns: `col-md-3`
- 6 columns: `col-md-2`

**Example:**
```
:::columns 2
Left content
---
Right content
:::
```

---

## Stats Dashboard

### Stats Block
**Pattern:** `:::stats\n(.*?)\n:::`
**Flags:** DOTALL
**Description:** Statistics dashboard
**Item Separator:** `|`
**Item Template:**
```html
<div class="stat">
<h3>{value}</h3>
<p><strong>{label}</strong>{description}</p>
</div>
```

**Example:**
```
:::stats
1,234 | Total Users | ↑ 12% growth
567 | Active Now | 🟢 Online
:::
```

---

## Carousel

### Carousel Container
**Pattern:** `:::carousel\n(.*?)\n:::`
**Flags:** DOTALL
**Description:** Image/content carousel with slides
**Slide Separator:** `---`
**Template:**
```html
<div id="carousel{id}" class="carousel slide" data-bs-ride="carousel">
  <div class="carousel-indicators">...</div>
  <div class="carousel-inner">
    <div class="carousel-item active">
      <div class="carousel-caption">{slide_content}</div>
    </div>
  </div>
  <button class="carousel-control-prev">...</button>
  <button class="carousel-control-next">...</button>
</div>
```

**Example:**
```
:::carousel
# Slide 1
First slide content
=> Next
---
# Slide 2
Second slide content
=> Learn More
---
# Slide 3
Third slide content
:::
```

---

## Tabs

### Tab Container
**Pattern:** `:::tabs\n(.*?)\n:::`
**Flags:** DOTALL
**Description:** Tabbed content with Bootstrap tabs
**Separator:** `---` between title and content pairs
**Template:**
```html
<ul class="nav nav-tabs">
  <li class="nav-item">
    <button class="nav-link active">{tab_title}</button>
  </li>
</ul>
<div class="tab-content">
  <div class="tab-pane fade show active">{tab_content}</div>
</div>
```

**Example:**
```
:::tabs
Overview
---
This is the overview content
---
Features
---
List of features here
---
Pricing
---
Pricing information
:::
```

---

## Accordion

### Accordion Container
**Pattern:** `:::accordion\n(.*?)\n:::`
**Flags:** DOTALL
**Description:** Collapsible accordion sections (perfect for FAQs)
**Separator:** `---` between question and answer pairs
**Template:**
```html
<div class="accordion">
  <div class="accordion-item">
    <h2 class="accordion-header">
      <button class="accordion-button">{question}</button>
    </h2>
    <div class="accordion-collapse collapse show">
      <div class="accordion-body">{answer}</div>
    </div>
  </div>
</div>
```

**Example:**
```
:::accordion
What is this?
---
This is an answer to the question
---
How does it work?
---
It works by using Bootstrap accordion
:::
```

---

## Inputs

### Text Input
**Pattern:** `^\? (.+?) \((text|email|password|tel|url|date|time)\)(?: \[(.+?)\])?$`
**Template:**
```html
<div class="mb-3">
<label class="form-label">{label}</label>
<input type="{type}" class="form-control" placeholder="{placeholder}">
</div>
```
**Flags:** MULTILINE
**Description:** Text input field with optional custom placeholder
**Examples:**
- `? Your Name (text)` - default placeholder
- `? Email Address (email) [you@example.com]` - custom placeholder
- `? Phone (tel) [+1 (555) 123-4567]`
- `? Website (url) [https://example.com]`
- `? Birth Date (date)`

### Number/Range Input
**Pattern:** `^\? (.+?) \((number|range) (\d+)-(\d+)\)(?: \[(.+?)\])?$`
**Template:**
```html
<div class="mb-3">
<label class="form-label">{label}</label>
<input type="{type}" class="form-control" min="{min}" max="{max}" placeholder="{placeholder}">
</div>
```
**Flags:** MULTILINE
**Description:** Number or range input with min/max and optional custom placeholder
**Examples:**
- `? Age (number 1-100)` - default placeholder
- `? Rating (range 1-10) [Rate from 1-10]` - custom placeholder

---

## Textarea

### Multi-line Text
**Pattern:** `^\?\? (.+?)(?: \[(.+?)\])?$`
**Template:**
```html
<div class="mb-3">
<label class="form-label">{label}</label>
<textarea class="form-control" rows="4" placeholder="{placeholder}"></textarea>
</div>
```
**Flags:** MULTILINE
**Description:** Multi-line text area with optional custom placeholder
**Examples:**
- `?? Your Message` - default placeholder
- `?? Comments [Tell us what you think...]` - custom placeholder

---

## Select/Dropdown

### Dropdown Select with Options

**Inline Syntax Pattern:** `^Select: (.+?) \| (.+)$`
**Multi-line Syntax Pattern:** `^Select: (.+)\n((?:- .+\n?)+)`
**Simple Syntax Pattern:** `^Select: (.+)$`

**Template:**
```html
<div class="mb-3">
<label class="form-label">{label}</label>
<select class="form-select">
<option selected disabled>Select one...</option>
<option>{option1}</option>
<option>{option2}</option>
...
</select>
</div>
```
**Flags:** MULTILINE
**Description:** Dropdown select with options (inline or multi-line)

**Examples:**

**Inline syntax (pipe-separated):**
```
Select: Choose Country | USA | Canada | Mexico | UK
```

**Multi-line syntax (list format):**
```
Select: Choose Language
- English
- Spanish
- French
- German
```

**Simple syntax (empty dropdown):**
```
Select: Choose an option
```

---

## Checkboxes

### Checkbox Input
**Pattern:** `^\[\] (.+)$` (unchecked) or `^\[x\] (.+)$` (checked)
**Template:**
```html
<div class="form-check">
<input class="form-check-input" type="checkbox" id="{id}">
<label class="form-check-label" for="{id}">{label}</label>
</div>
```
**Flags:** MULTILINE
**Description:** Checkbox input for multi-select options

**Examples:**
```
[] Unchecked item
[x] Checked item
```

---

## Radio Buttons

### Radio Input
**Pattern:** `^\(\) (.+)$` (unselected) or `^\(\*\) (.+)$` (selected)
**Template:**
```html
<div class="form-check">
<input class="form-check-input" type="radio" name="radioGroup" id="{id}">
<label class="form-check-label" for="{id}">{label}</label>
</div>
```
**Flags:** MULTILINE
**Description:** Radio button for single-select options

**Examples:**
```
() Unselected option
(*) Selected option
```

---

## Badges

### Badge Label
**Pattern:** `!!(.+?)!!` (default) or `!!(.+?):(.+?)!!` (colored)
**Template:** `<span class="badge bg-{color}">{text}</span>`
**Description:** Inline badge/label for status, tags, counters

**Examples:**
```
!!New!!
!!Success:success!!
!!Danger:danger!!
!!Primary:primary!!
!!Warning:warning!!
!!Info:info!!
```

**Available Colors:** primary, secondary, success, danger, warning, info, light, dark

---

## Progress Bars

### Progress Indicator
**Pattern:** `\[progress (\d+)%\]` (default) or `\[progress (\d+)% (\w+)\]` (colored)
**Template:**
```html
<div class="progress mb-3">
<div class="progress-bar bg-{color}" role="progressbar"
style="width: {value}%" aria-valuenow="{value}"
aria-valuemin="0" aria-valuemax="100">{value}%</div>
</div>
```
**Description:** Progress bar for completion, loading states

**Examples:**
```
[progress 75%]
[progress 50% success]
[progress 30% warning]
[progress 90% info]
```

---

## Breadcrumbs

### Breadcrumb Navigation
**Pattern:** `^>> (.+)$`
**Template:**
```html
<nav aria-label="breadcrumb">
<ol class="breadcrumb">
<li class="breadcrumb-item"><a href="#">{item}</a></li>
<li class="breadcrumb-item active" aria-current="page">{last_item}</li>
</ol>
</nav>
```
**Flags:** MULTILINE
**Description:** Breadcrumb navigation trail
**Separator:** `>`

**Example:**
```
>> Home > Products > Category > Item
```

---

## Pagination

### Page Navigation
**Pattern:** `^<< (.+) >>$`
**Template:**
```html
<nav aria-label="Page navigation">
<ul class="pagination">
<li class="page-item"><a class="page-link" href="#">Previous</a></li>
<li class="page-item"><a class="page-link" href="#">{page}</a></li>
...
<li class="page-item"><a class="page-link" href="#">Next</a></li>
</ul>
</nav>
```
**Flags:** MULTILINE
**Description:** Pagination for multi-page content

**Example:**
```
<< 1 2 3 4 5 >>
```

---

## Alerts

### Callout Alerts
**Pattern:** `> \[!(SUCCESS|WARNING|ERROR|INFO|DANGER)\]\n((?:> .+\n?)+)`
**Template:** `<div class="alert alert-{type}">{message}</div>`
**Flags:** MULTILINE
**Type Mapping:**
- SUCCESS → success
- WARNING → warning
- ERROR → danger
- DANGER → danger
- INFO → info

**Example:**
```
> [!SUCCESS]
> Your changes saved!
```

---

## Navbar

### Navigation Bar
**Pattern:** `:::navbar\n(.*?)\n:::`
**Template:** `<nav class="navbar navbar-expand-lg">\n{content}\n</nav>`
**Flags:** DOTALL
**Description:** Navigation bar

---

## Sidenav

### Left Sidenav
**Pattern:** `:::sidenav left\n(.*?)\n:::`
**Template:** `<aside class="sidenav sidenav-left">\n{content}\n</aside>`
**Flags:** DOTALL

### Right Sidenav
**Pattern:** `:::sidenav right\n(.*?)\n:::`
**Template:** `<aside class="sidenav sidenav-right">\n{content}\n</aside>`
**Flags:** DOTALL

### Default Sidenav
**Pattern:** `:::sidenav\n(.*?)\n:::`
**Template:** `<aside class="sidenav">\n{content}\n</aside>`
**Flags:** DOTALL

---

## Header/Footer

### Page Header
**Pattern:** `:::header\n(.*?)\n:::`
**Template:** `<header class="header">\n{content}\n</header>`
**Flags:** DOTALL
**Description:** Page header

### Page Footer
**Pattern:** `:::footer\n(.*?)\n:::`
**Template:** `<footer class="footer">\n{content}\n</footer>`
**Flags:** DOTALL
**Description:** Page footer

---

## Processing Order

Components are processed in this order (blocks before inline):

**Block-level elements:**
1. cards (Cards first)
2. panels (Then panels)
3. sections (Then sections)
4. stats (Then stats)
5. carousel (Then carousel)
6. tabs (Then tabs)
7. accordion (Then accordion)
8. navbar (Then navbar)
9. sidenav (Then sidenav)
10. header (Then header)
11. footer (Then footer)
12. columns (Grid layouts last - so nested blocks are already processed)

**Inline elements:**
13. alerts (Callout alerts)
14. buttons (Action buttons)
15. button_links (Button-styled links)
16. inputs (Text/number/date inputs)
17. textarea (Multi-line inputs)
18. select (Dropdown selects)
19. checkboxes (Checkbox inputs)
20. radio_buttons (Radio inputs)
21. badges (Inline labels/tags)
22. progress_bars (Progress indicators)
23. breadcrumbs (Navigation trails)
24. pagination (Page navigation)

---

---

## Standard Markdown Elements

All standard markdown syntax is fully supported:

### Code

**Inline code:** `` `code here` ``
**Code blocks:**
```
\`\`\`python
def hello():
    print("Hello")
\`\`\`
```

### Blockquotes

```
> This is a blockquote
> It can span multiple lines
```

### Lists

**Unordered:**
```
- Item 1
- Item 2
  - Nested item
```

**Ordered:**
```
1. First
2. Second
3. Third
```

### Tables (GFM)

```
| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
```

### Text Formatting

- **Bold:** `**text**` or `__text__`
- *Italic:* `*text*` or `_text_`
- ~~Strikethrough:~~ `~~text~~`

### Links and Images

- Links: `[text](url)`
- Images: `![alt](url)`

### Horizontal Rules

```
---
```

---

**Note:** To customize pure text syntax mappings, copy this file to your project root as `syntax-mappings.md` and edit the patterns and templates. Standard markdown features are handled by the markdown renderer and cannot be customized through this file.
