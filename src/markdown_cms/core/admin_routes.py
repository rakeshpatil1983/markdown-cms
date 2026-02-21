"""Admin routes for user and content management."""

import os
from datetime import datetime
from pathlib import Path

from fasthtml.common import *

from .auth import create_user, get_user_by_session, hash_password, require_role
from .config import get_config
from .database import get_db_context
from .forms import (
    Form,
    FormField,
    ValidationRule,
    email_validator,
    flash,
    min_length_validator,
    render_flash_messages,
)
from .models import Content, ContentStatus, DataSource, User, UserRole
from .parser import MarkdownParser
from .registry import get_registry


def setup_admin_routes(app):
    # Initialize parser for preview
    _parser = MarkdownParser()
    """Setup admin routes."""

    def get_current_user(request):
        """Get current user from session cookie."""
        session_id = request.cookies.get("cms_session")
        if not session_id:
            return None
        return get_user_by_session(session_id)

    def require_admin(request):
        """Check if user is admin, redirect to login if not."""
        user = get_current_user(request)
        if not user:
            return RedirectResponse("/login", status_code=307)
        if not require_role(user, [UserRole.ADMIN]):
            return Response("Access Denied", status_code=403)
        return None

    @app.get("/admin")
    def admin_dashboard(request):
        """Admin dashboard."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        user = get_current_user(request)

        # Get statistics
        with get_db_context() as db:
            total_users = db.query(User).count()
            total_content = db.query(Content).count()
            published_content = (
                db.query(Content).filter_by(status=ContentStatus.PUBLISHED).count()
            )
            total_datasources = db.query(DataSource).count()
            active_datasources = db.query(DataSource).filter_by(is_active=True).count()

        # Count uploaded files
        config = get_config()
        uploads_dir = config.static_path / "uploads"
        total_files = len(list(uploads_dir.glob("*"))) if uploads_dir.exists() else 0

        return Html(
            Head(
                Title("Admin Dashboard - Markdown CMS"),
                Link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
                ),
                Script(
                    src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"
                ),
            ),
            Body(
                Div(cls="container mt-5")(
                    H1("Admin Dashboard"),
                    P(f"Welcome, {user.full_name or user.username}!"),
                    NotStr(render_flash_messages()),
                    Div(cls="row mt-4")(
                        Div(cls="col-md-4")(
                            Div(cls="card")(
                                Div(cls="card-body")(
                                    H5(cls="card-title")("Users"),
                                    P(cls="card-text")(f"{total_users} total users"),
                                    A(href="/admin/users", cls="btn btn-primary")(
                                        "Manage Users"
                                    ),
                                )
                            )
                        ),
                        Div(cls="col-md-4")(
                            Div(cls="card")(
                                Div(cls="card-body")(
                                    H5(cls="card-title")("Content"),
                                    P(cls="card-text")(
                                        f"{published_content}/{total_content} published"
                                    ),
                                    A(href="/admin/content", cls="btn btn-primary")(
                                        "Manage Content"
                                    ),
                                )
                            )
                        ),
                        Div(cls="col-md-4")(
                            Div(cls="card")(
                                Div(cls="card-body")(
                                    H5(cls="card-title")("Files"),
                                    P(cls="card-text")(f"{total_files} uploaded files"),
                                    A(href="/admin/files", cls="btn btn-primary")(
                                        "Manage Files"
                                    ),
                                )
                            )
                        ),
                    ),
                    Div(cls="row mt-4")(
                        Div(cls="col-md-4")(
                            Div(cls="card")(
                                Div(cls="card-body")(
                                    H5(cls="card-title")("Data Sources"),
                                    P(cls="card-text")(
                                        f"{active_datasources}/{total_datasources} active"
                                    ),
                                    A(href="/admin/datasources", cls="btn btn-primary")(
                                        "Manage Data Sources"
                                    ),
                                )
                            )
                        ),
                        Div(cls="col-md-4")(
                            Div(cls="card")(
                                Div(cls="card-body")(
                                    H5(cls="card-title")("Settings"),
                                    P(cls="card-text")("System settings and info"),
                                    A(href="/admin/settings", cls="btn btn-primary")(
                                        "View Settings"
                                    ),
                                )
                            )
                        ),
                    ),
                    Div(cls="mt-4")(
                        A(href="/", cls="btn btn-secondary")("Back to Site"),
                        Span(" "),
                        A(href="/admin/settings", cls="btn btn-info")("Settings"),
                        Span(" "),
                        A(href="/logout", cls="btn btn-danger")("Logout"),
                    ),
                )
            ),
        )

    @app.get("/admin/users")
    def admin_users_list(request):
        """List all users."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        with get_db_context() as db:
            users = db.query(User).all()
            db.expunge_all()

        rows = []
        for user in users:
            rows.append(
                Tr(
                    Td(user.username),
                    Td(user.email),
                    Td(user.full_name or "-"),
                    Td(user.role.value),
                    Td("Active" if user.is_active else "Inactive"),
                    Td(
                        A(
                            href=f"/admin/users/{user.id}/edit",
                            cls="btn btn-sm btn-primary",
                        )("Edit"),
                        " ",
                        A(
                            href=f"/admin/users/{user.id}/delete",
                            cls="btn btn-sm btn-danger",
                        )("Delete"),
                    ),
                )
            )

        return Html(
            Head(
                Title("Manage Users - Admin"),
                Link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
                ),
            ),
            Body(
                Div(cls="container mt-5")(
                    H1("Manage Users"),
                    NotStr(render_flash_messages()),
                    Div(cls="mb-3")(
                        A(href="/admin/users/new", cls="btn btn-success")(
                            "Add New User"
                        ),
                    ),
                    Table(cls="table table-striped")(
                        Thead(
                            Tr(
                                Th("Username"),
                                Th("Email"),
                                Th("Full Name"),
                                Th("Role"),
                                Th("Status"),
                                Th("Actions"),
                            )
                        ),
                        Tbody(*rows),
                    ),
                    A(href="/admin", cls="btn btn-secondary")("Back to Dashboard"),
                )
            ),
        )

    @app.get("/admin/users/new")
    def admin_users_new(request):
        """Create new user form."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        # Define form
        form = Form(
            [
                FormField(
                    name="username",
                    label="Username",
                    required=True,
                    validators=[
                        ValidationRule(
                            "min_length",
                            "Username must be at least 3 characters",
                            min_length_validator(3),
                        ),
                    ],
                    placeholder="Enter username",
                ),
                FormField(
                    name="email",
                    label="Email",
                    field_type="email",
                    required=True,
                    validators=[
                        ValidationRule(
                            "email", "Invalid email format", email_validator
                        ),
                    ],
                    placeholder="user@example.com",
                ),
                FormField(
                    name="password",
                    label="Password",
                    field_type="password",
                    required=True,
                    validators=[
                        ValidationRule(
                            "min_length",
                            "Password must be at least 6 characters",
                            min_length_validator(6),
                        ),
                    ],
                    placeholder="Enter password",
                ),
                FormField(
                    name="full_name",
                    label="Full Name",
                    required=False,
                    placeholder="Enter full name",
                ),
                FormField(
                    name="role",
                    label="Role",
                    field_type="select",
                    required=True,
                    options=[
                        ("viewer", "Viewer"),
                        ("editor", "Editor"),
                        ("admin", "Admin"),
                    ],
                ),
            ]
        )

        return Html(
            Head(
                Title("Add New User - Admin"),
                Link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
                ),
            ),
            Body(
                Div(cls="container mt-5")(
                    H1("Add New User"),
                    NotStr(render_flash_messages()),
                    Form(method="post", action="/admin/users/create")(
                        NotStr(form.render()),
                        Button(type="submit", cls="btn btn-primary")("Create User"),
                        Span(" "),
                        A(href="/admin/users", cls="btn btn-secondary")("Cancel"),
                    ),
                )
            ),
        )

    @app.post("/admin/users/create")
    async def admin_users_create(request):
        """Create new user."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        form_data = await request.form()
        data = dict(form_data)

        # Validate form
        form = Form(
            [
                FormField(
                    name="username",
                    label="Username",
                    required=True,
                    validators=[
                        ValidationRule(
                            "min_length",
                            "Username must be at least 3 characters",
                            min_length_validator(3),
                        )
                    ],
                ),
                FormField(
                    name="email",
                    label="Email",
                    field_type="email",
                    required=True,
                    validators=[
                        ValidationRule("email", "Invalid email format", email_validator)
                    ],
                ),
                FormField(
                    name="password",
                    label="Password",
                    field_type="password",
                    required=True,
                    validators=[
                        ValidationRule(
                            "min_length",
                            "Password must be at least 6 characters",
                            min_length_validator(6),
                        )
                    ],
                ),
                FormField(name="full_name", label="Full Name", required=False),
                FormField(
                    name="role", label="Role", field_type="select", required=True
                ),
            ]
        )

        validated = form.validate(data, csrf_token=data.get("csrf_token"))

        if not validated.is_valid:
            flash("Please correct the errors below", "danger")
            # TODO: Re-render form with errors
            return RedirectResponse("/admin/users/new", status_code=303)

        # Create user
        try:
            role_map = {
                "viewer": UserRole.VIEWER,
                "editor": UserRole.EDITOR,
                "admin": UserRole.ADMIN,
            }
            role = role_map.get(data.get("role"), UserRole.VIEWER)

            user = create_user(
                username=data.get("username"),
                email=data.get("email"),
                password=data.get("password"),
                full_name=data.get("full_name") or None,
                role=role,
            )

            flash(f"User '{user.username}' created successfully", "success")
            return RedirectResponse("/admin/users", status_code=303)

        except ValueError as e:
            flash(str(e), "danger")
            return RedirectResponse("/admin/users/new", status_code=303)

    @app.get("/admin/users/{user_id}/edit")
    def admin_users_edit(request, user_id: int):
        """Edit user form."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        with get_db_context() as db:
            user = db.query(User).filter_by(id=user_id).first()
            if not user:
                flash("User not found", "danger")
                return RedirectResponse("/admin/users", status_code=303)
            db.expunge(user)

        # Define form with current values
        form = Form(
            [
                FormField(
                    name="username",
                    label="Username",
                    required=True,
                    default_value=user.username,
                    validators=[
                        ValidationRule(
                            "min_length",
                            "Username must be at least 3 characters",
                            min_length_validator(3),
                        ),
                    ],
                ),
                FormField(
                    name="email",
                    label="Email",
                    field_type="email",
                    required=True,
                    default_value=user.email,
                    validators=[
                        ValidationRule(
                            "email", "Invalid email format", email_validator
                        ),
                    ],
                ),
                FormField(
                    name="full_name",
                    label="Full Name",
                    required=False,
                    default_value=user.full_name or "",
                ),
                FormField(
                    name="role",
                    label="Role",
                    field_type="select",
                    required=True,
                    options=[
                        ("viewer", "Viewer"),
                        ("editor", "Editor"),
                        ("admin", "Admin"),
                    ],
                    default_value=user.role.value,
                ),
                FormField(
                    name="is_active",
                    label="Status",
                    field_type="select",
                    required=True,
                    options=[
                        ("true", "Active"),
                        ("false", "Inactive"),
                    ],
                    default_value="true" if user.is_active else "false",
                ),
                FormField(
                    name="new_password",
                    label="New Password (leave blank to keep current)",
                    field_type="password",
                    required=False,
                    placeholder="Enter new password",
                ),
            ]
        )

        return Html(
            Head(
                Title(f"Edit User: {user.username} - Admin"),
                Link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
                ),
            ),
            Body(
                Div(cls="container mt-5")(
                    H1(f"Edit User: {user.username}"),
                    NotStr(render_flash_messages()),
                    NotStr(
                        f'<form method="post" action="/admin/users/{user_id}/update">{form.render()}<button type="submit" class="btn btn-primary">Update User</button> <a href="/admin/users" class="btn btn-secondary">Cancel</a></form>'
                    ),
                )
            ),
        )

    @app.post("/admin/users/{user_id}/update")
    async def admin_users_update(request, user_id: int):
        """Update user."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        current_user = get_current_user(request)
        form_data = await request.form()
        data = dict(form_data)

        # Validate form
        form = Form(
            [
                FormField(
                    name="username",
                    label="Username",
                    required=True,
                    validators=[
                        ValidationRule(
                            "min_length",
                            "Username must be at least 3 characters",
                            min_length_validator(3),
                        )
                    ],
                ),
                FormField(
                    name="email",
                    label="Email",
                    field_type="email",
                    required=True,
                    validators=[
                        ValidationRule("email", "Invalid email format", email_validator)
                    ],
                ),
                FormField(name="full_name", label="Full Name", required=False),
                FormField(
                    name="role", label="Role", field_type="select", required=True
                ),
                FormField(
                    name="is_active", label="Status", field_type="select", required=True
                ),
                FormField(
                    name="new_password",
                    label="New Password",
                    field_type="password",
                    required=False,
                ),
            ]
        )

        validated = form.validate(data, csrf_token=data.get("csrf_token"))

        if not validated.is_valid:
            flash("Please correct the errors below", "danger")
            return RedirectResponse(f"/admin/users/{user_id}/edit", status_code=303)

        # Update user
        try:
            role_map = {
                "viewer": UserRole.VIEWER,
                "editor": UserRole.EDITOR,
                "admin": UserRole.ADMIN,
            }

            with get_db_context() as db:
                user = db.query(User).filter_by(id=user_id).first()
                if not user:
                    flash("User not found", "danger")
                    return RedirectResponse("/admin/users", status_code=303)

                # Check if username changed and conflicts with another user
                if user.username != data.get("username"):
                    existing = (
                        db.query(User).filter_by(username=data.get("username")).first()
                    )
                    if existing:
                        flash(
                            f"Username '{data.get('username')}' already exists",
                            "danger",
                        )
                        return RedirectResponse(
                            f"/admin/users/{user_id}/edit", status_code=303
                        )

                # Check if email changed and conflicts with another user
                if user.email != data.get("email"):
                    existing = db.query(User).filter_by(email=data.get("email")).first()
                    if existing:
                        flash(f"Email '{data.get('email')}' already exists", "danger")
                        return RedirectResponse(
                            f"/admin/users/{user_id}/edit", status_code=303
                        )

                # Prevent removing admin role from yourself
                new_role = role_map.get(data.get("role"), UserRole.VIEWER)
                if current_user.id == user_id and new_role != UserRole.ADMIN:
                    flash("You cannot remove admin role from yourself", "danger")
                    return RedirectResponse(
                        f"/admin/users/{user_id}/edit", status_code=303
                    )

                # Prevent deactivating yourself
                new_is_active = data.get("is_active") == "true"
                if current_user.id == user_id and not new_is_active:
                    flash("You cannot deactivate your own account", "danger")
                    return RedirectResponse(
                        f"/admin/users/{user_id}/edit", status_code=303
                    )

                # Update user fields
                user.username = data.get("username")
                user.email = data.get("email")
                user.full_name = data.get("full_name") or None
                user.role = new_role
                user.is_active = new_is_active

                # Update password if provided
                new_password = data.get("new_password")
                if new_password and len(new_password) >= 6:
                    user.password_hash = hash_password(new_password)
                elif new_password and len(new_password) < 6:
                    flash("Password must be at least 6 characters", "danger")
                    return RedirectResponse(
                        f"/admin/users/{user_id}/edit", status_code=303
                    )

                db.commit()

            flash(f"User '{data.get('username')}' updated successfully", "success")
            return RedirectResponse("/admin/users", status_code=303)

        except Exception as e:
            flash(f"Error updating user: {str(e)}", "danger")
            return RedirectResponse(f"/admin/users/{user_id}/edit", status_code=303)

    @app.get("/admin/users/{user_id}/delete")
    def admin_users_delete(request, user_id: int):
        """Delete user (with confirmation)."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        current_user = get_current_user(request)

        # Prevent self-deletion
        if current_user.id == user_id:
            flash("You cannot delete your own account", "danger")
            return RedirectResponse("/admin/users", status_code=303)

        with get_db_context() as db:
            user = db.query(User).filter_by(id=user_id).first()
            if not user:
                flash("User not found", "danger")
                return RedirectResponse("/admin/users", status_code=303)

            username = user.username
            db.delete(user)
            db.commit()

        flash(f"User '{username}' deleted successfully", "success")
        return RedirectResponse("/admin/users", status_code=303)

    @app.get("/admin/content")
    def admin_content_list(request):
        """List all content - both markdown files and database content."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        config = get_config()
        pages_path = config.pages_path

        # Collect all markdown pages from the pages directory
        def collect_pages(folder: Path, base_path: Path) -> list[dict]:
            """Recursively collect all markdown pages."""
            pages = []
            if not folder.is_dir():
                return pages

            for entry in sorted(folder.iterdir()):
                if entry.name.startswith(".") or entry.name.startswith("_"):
                    continue

                if entry.is_dir():
                    # Skip images directories
                    if entry.name.lower() == "images":
                        continue
                    pages.extend(collect_pages(entry, base_path))

                elif entry.is_file() and entry.suffix == ".md":
                    # Extract frontmatter for title
                    title = entry.stem.replace("-", " ").replace("_", " ").title()
                    try:
                        with open(entry, encoding="utf-8") as f:
                            content = f.read(2000)  # Read first 2KB for frontmatter
                            import re

                            fm_match = re.match(
                                r"^---\s*\n(.*?)\n---", content, re.DOTALL
                            )
                            if fm_match:
                                for line in fm_match.group(1).strip().split("\n"):
                                    if line.strip().startswith("title:"):
                                        title = (
                                            line.split(":", 1)[1]
                                            .strip()
                                            .strip('"')
                                            .strip("'")
                                        )
                                        break
                    except Exception:
                        pass

                    # Get relative path for URL
                    rel_path = entry.relative_to(base_path)
                    url_path = "/" + str(rel_path.with_suffix("")).replace("\\", "/")

                    # Get file stats
                    stat = entry.stat()
                    modified = datetime.fromtimestamp(stat.st_mtime)

                    pages.append(
                        {
                            "title": title,
                            "path": str(rel_path).replace("\\", "/"),
                            "url": url_path,
                            "modified": modified,
                            "size": stat.st_size,
                            "file_path": str(entry),
                        }
                    )

            return pages

        # Get all markdown pages
        markdown_pages = (
            collect_pages(pages_path, pages_path) if pages_path.exists() else []
        )

        # Sort by path
        markdown_pages.sort(key=lambda x: x["path"])

        # Build rows for markdown files
        rows = []
        for page in markdown_pages:
            size_str = f"{page['size'] / 1024:.1f} KB"
            rows.append(
                Tr(
                    Td(page["title"]),
                    Td(Code(page["path"])),
                    Td(Span("File", cls="badge bg-info")),
                    Td(page["modified"].strftime("%Y-%m-%d %H:%M")),
                    Td(size_str),
                    Td(
                        A(href=page["url"], target="_blank", cls="btn btn-sm btn-info")(
                            "View"
                        ),
                        " ",
                        A(
                            href=f"/admin/content/edit-file?path={page['path']}",
                            cls="btn btn-sm btn-primary",
                        )("Edit"),
                    ),
                )
            )

        # Also get database content
        with get_db_context() as db:
            from sqlalchemy.orm import joinedload

            content_items = db.query(Content).options(joinedload(Content.author)).all()

            for item in content_items:
                rows.append(
                    Tr(
                        Td(item.title),
                        Td(Code(f"/db/{item.slug}")),
                        Td(
                            Span(
                                item.status.value.title(),
                                cls=f"badge bg-{'success' if item.status.value == 'published' else 'warning' if item.status.value == 'draft' else 'secondary'}",
                            )
                        ),
                        Td(
                            item.updated_at.strftime("%Y-%m-%d %H:%M")
                            if item.updated_at
                            else "-"
                        ),
                        Td("-"),
                        Td(
                            A(
                                href=f"/content/{item.slug}",
                                target="_blank",
                                cls="btn btn-sm btn-info",
                            )("View"),
                            " ",
                            A(
                                href=f"/admin/content/{item.id}/edit",
                                cls="btn btn-sm btn-primary",
                            )("Edit"),
                            " ",
                            A(
                                href=f"/admin/content/{item.id}/delete",
                                cls="btn btn-sm btn-danger",
                            )("Delete"),
                        ),
                    )
                )

        return Html(
            Head(
                Title("Manage Content - Admin"),
                Link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
                ),
            ),
            Body(
                Div(cls="container mt-5")(
                    H1("Manage Content"),
                    NotStr(render_flash_messages()),
                    Div(cls="alert alert-info")(
                        Strong("Content Sources: "),
                        "Markdown files from ",
                        Code("pages/"),
                        " directory and database-stored content are listed below.",
                    ),
                    Div(cls="mb-3")(
                        A(href="/admin/content/new-file", cls="btn btn-success")(
                            "New Page"
                        ),
                        " ",
                        A(href="/admin/content/new", cls="btn btn-outline-success")(
                            "New DB Content"
                        ),
                    ),
                    Table(cls="table table-striped")(
                        Thead(
                            Tr(
                                Th("Title"),
                                Th("Path"),
                                Th("Type"),
                                Th("Modified"),
                                Th("Size"),
                                Th("Actions"),
                            )
                        ),
                        (
                            Tbody(*rows)
                            if rows
                            else Tbody(
                                Tr(
                                    Td(colspan="6", cls="text-center")(
                                        "No content found. Create your first page!"
                                    )
                                )
                            )
                        ),
                    ),
                    A(href="/admin", cls="btn btn-secondary")("Back to Dashboard"),
                )
            ),
        )

    @app.get("/admin/content/new")
    def admin_content_new(request):
        """Create new content form."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        user = get_current_user(request)

        # Define form
        form = Form(
            [
                FormField(
                    name="title",
                    label="Title",
                    required=True,
                    placeholder="Enter content title",
                ),
                FormField(
                    name="slug",
                    label="Slug",
                    required=True,
                    validators=[
                        ValidationRule(
                            "pattern",
                            "Slug must be lowercase alphanumeric with hyphens",
                            lambda x: bool(
                                __import__("re").match(r"^[a-z0-9-]+$", str(x))
                            ),
                        ),
                    ],
                    placeholder="url-friendly-slug",
                ),
                FormField(
                    name="markdown_content",
                    label="Content (Markdown)",
                    field_type="textarea",
                    required=True,
                    placeholder="# Your markdown content here...",
                ),
                FormField(
                    name="status",
                    label="Status",
                    field_type="select",
                    required=True,
                    options=[
                        ("draft", "Draft"),
                        ("published", "Published"),
                        ("archived", "Archived"),
                    ],
                    default_value="draft",
                ),
            ]
        )

        # Get uploaded files for file browser
        config = get_config()
        uploads_dir = config.static_path / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)

        files = []
        if uploads_dir.exists():
            for file_path in uploads_dir.iterdir():
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    is_image = ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]
                    files.append(
                        {
                            "name": file_path.name,
                            "url": f"/static/uploads/{file_path.name}",
                            "is_image": is_image,
                        }
                    )
        files.sort(key=lambda x: x["name"])

        return Html(
            Head(
                Title("Add New Content - Admin"),
                Link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
                ),
                Script(
                    src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"
                ),
                Style(
                    """
                    textarea { font-family: monospace; }
                    .preview-pane {
                        border: 1px solid #ddd;
                        padding: 15px;
                        border-radius: 4px;
                        min-height: 400px;
                        background: #f8f9fa;
                    }
                    .file-item {
                        cursor: pointer;
                        padding: 10px;
                        border: 1px solid #ddd;
                        margin: 5px;
                        border-radius: 4px;
                        display: inline-block;
                        text-align: center;
                    }
                    .file-item:hover {
                        background: #f0f0f0;
                    }
                    .file-item img {
                        max-width: 100px;
                        max-height: 100px;
                    }
                """
                ),
            ),
            Body(
                Div(cls="container mt-5")(
                    H1("Add New Content"),
                    NotStr(render_flash_messages()),
                    # File browser button
                    Div(cls="mb-3")(
                        Button(
                            "Browse/Upload Files",
                            cls="btn btn-info",
                            **{
                                "data-bs-toggle": "modal",
                                "data-bs-target": "#fileBrowserModal",
                            },
                        ),
                    ),
                    Div(cls="row")(
                        Div(cls="col-md-6")(
                            H4("Editor"),
                            NotStr(
                                f'<form method="post" action="/admin/content/create" id="contentForm">{form.render()}<button type="submit" class="btn btn-primary">Create Content</button> <a href="/admin/content" class="btn btn-secondary">Cancel</a></form>'
                            ),
                        ),
                        Div(cls="col-md-6")(
                            H4("Preview"),
                            Div(cls="preview-pane", id="preview")(
                                P("Preview will appear here...")
                            ),
                        ),
                    ),
                    # File browser modal
                    Div(cls="modal fade", id="fileBrowserModal", tabindex="-1")(
                        Div(cls="modal-dialog modal-lg")(
                            Div(cls="modal-content")(
                                Div(cls="modal-header")(
                                    H5("File Browser", cls="modal-title"),
                                    Button(
                                        type="button",
                                        cls="btn-close",
                                        **{"data-bs-dismiss": "modal"},
                                    ),
                                ),
                                Div(cls="modal-body")(
                                    # Upload form
                                    NotStr(
                                        """
                                        <form method="post" action="/admin/upload" enctype="multipart/form-data" id="uploadForm">
                                            <div class="mb-3">
                                                <label class="form-label">Upload File:</label>
                                                <input type="file" name="file" class="form-control" required>
                                            </div>
                                            <button type="submit" class="btn btn-primary">Upload</button>
                                        </form>
                                        <hr>
                                        <h6>Click a file to insert into editor:</h6>
                                        <div id="fileList">
                                    """
                                    ),
                                    *[
                                        Div(
                                            cls="file-item",
                                            **{
                                                "data-url": f["url"],
                                                "data-name": f["name"],
                                                "data-is-image": str(
                                                    f["is_image"]
                                                ).lower(),
                                            },
                                        )(
                                            (
                                                Img(src=f["url"])
                                                if f["is_image"]
                                                else Div()(f["name"])
                                            ),
                                            Br(),
                                            Small(f["name"]),
                                        )
                                        for f in files
                                    ],
                                    NotStr("</div>"),
                                ),
                                Div(cls="modal-footer")(
                                    Button(
                                        "Close",
                                        cls="btn btn-secondary",
                                        **{"data-bs-dismiss": "modal"},
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                Script(
                    """
                    const textarea = document.querySelector('textarea[name="markdown_content"]');
                    const preview = document.getElementById('preview');

                    // Markdown preview
                    if (textarea) {
                        textarea.addEventListener('input', function() {
                            let text = this.value;
                            text = text.replace(/^### (.*$)/gim, '<h3>$1</h3>');
                            text = text.replace(/^## (.*$)/gim, '<h2>$1</h2>');
                            text = text.replace(/^# (.*$)/gim, '<h1>$1</h1>');
                            text = text.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');
                            text = text.replace(/\\*(.+?)\\*/g, '<em>$1</em>');
                            text = text.replace(/\\[(.+?)\\]\\((.+?)\\)/g, '<a href="$2">$1</a>');
                            text = text.replace(/\\n/g, '<br>');
                            preview.innerHTML = text || '<p>Preview will appear here...</p>';
                        });

                        // Trigger preview on load
                        textarea.dispatchEvent(new Event('input'));
                    }

                    // File browser - insert markdown link on click
                    document.querySelectorAll('.file-item').forEach(item => {
                        item.addEventListener('click', function() {
                            const url = this.dataset.url;
                            const name = this.dataset.name;
                            const isImage = this.dataset.isImage === 'true';

                            // Generate markdown link
                            const link = isImage ? `![${name}](${url})` : `[${name}](${url})`;

                            // Insert at cursor position
                            const start = textarea.selectionStart;
                            const end = textarea.selectionEnd;
                            const text = textarea.value;
                            textarea.value = text.substring(0, start) + link + text.substring(end);

                            // Update preview
                            textarea.dispatchEvent(new Event('input'));

                            // Close modal
                            const modal = bootstrap.Modal.getInstance(document.getElementById('fileBrowserModal'));
                            if (modal) modal.hide();

                            // Focus textarea
                            textarea.focus();
                            textarea.selectionStart = textarea.selectionEnd = start + link.length;
                        });
                    });
                """
                ),
            ),
        )

    @app.post("/admin/content/create")
    async def admin_content_create(request):
        """Create new content."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        user = get_current_user(request)
        form_data = await request.form()
        data = dict(form_data)

        # Validate form
        form = Form(
            [
                FormField(name="title", label="Title", required=True),
                FormField(name="slug", label="Slug", required=True),
                FormField(
                    name="markdown_content",
                    label="Content",
                    field_type="textarea",
                    required=True,
                ),
                FormField(
                    name="status", label="Status", field_type="select", required=True
                ),
            ]
        )

        validated = form.validate(data, csrf_token=data.get("csrf_token"))

        if not validated.is_valid:
            flash("Please correct the errors below", "danger")
            return RedirectResponse("/admin/content/new", status_code=303)

        # Create content
        try:
            from datetime import UTC, datetime

            status_map = {
                "draft": ContentStatus.DRAFT,
                "published": ContentStatus.PUBLISHED,
                "archived": ContentStatus.ARCHIVED,
            }
            status = status_map.get(data.get("status"), ContentStatus.DRAFT)

            with get_db_context() as db:
                # Check if slug already exists
                existing = db.query(Content).filter_by(slug=data.get("slug")).first()
                if existing:
                    flash(
                        f"Content with slug '{data.get('slug')}' already exists",
                        "danger",
                    )
                    return RedirectResponse("/admin/content/new", status_code=303)

                content = Content(
                    title=data.get("title"),
                    slug=data.get("slug"),
                    markdown_content=data.get("markdown_content"),
                    status=status,
                    author_id=user.id,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )

                if status == ContentStatus.PUBLISHED:
                    content.published_at = datetime.now(UTC)

                db.add(content)
                db.commit()

            flash(f"Content '{data.get('title')}' created successfully", "success")
            return RedirectResponse("/admin/content", status_code=303)

        except Exception as e:
            flash(f"Error creating content: {str(e)}", "danger")
            return RedirectResponse("/admin/content/new", status_code=303)

    @app.get("/admin/content/{content_id}/edit")
    def admin_content_edit(request, content_id: int):
        """Edit content form."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        with get_db_context() as db:
            content = db.query(Content).filter_by(id=content_id).first()
            if not content:
                flash("Content not found", "danger")
                return RedirectResponse("/admin/content", status_code=303)

            db.expunge(content)

        # Define form with current values
        form = Form(
            [
                FormField(
                    name="title",
                    label="Title",
                    required=True,
                    default_value=content.title,
                ),
                FormField(
                    name="slug",
                    label="Slug",
                    required=True,
                    default_value=content.slug,
                ),
                FormField(
                    name="markdown_content",
                    label="Content (Markdown)",
                    field_type="textarea",
                    required=True,
                    default_value=content.markdown_content,
                ),
                FormField(
                    name="status",
                    label="Status",
                    field_type="select",
                    required=True,
                    options=[
                        ("draft", "Draft"),
                        ("published", "Published"),
                        ("archived", "Archived"),
                    ],
                    default_value=content.status.value,
                ),
            ]
        )

        # Get uploaded files for file browser
        config = get_config()
        uploads_dir = config.static_path / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)

        files = []
        if uploads_dir.exists():
            for file_path in uploads_dir.iterdir():
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    is_image = ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]
                    files.append(
                        {
                            "name": file_path.name,
                            "url": f"/static/uploads/{file_path.name}",
                            "is_image": is_image,
                        }
                    )
        files.sort(key=lambda x: x["name"])

        return Html(
            Head(
                Title(f"Edit: {content.title} - Admin"),
                Link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
                ),
                Script(
                    src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"
                ),
                Style(
                    """
                    textarea { font-family: monospace; }
                    .preview-pane {
                        border: 1px solid #ddd;
                        padding: 15px;
                        border-radius: 4px;
                        min-height: 400px;
                        background: #f8f9fa;
                    }
                    .file-item {
                        cursor: pointer;
                        padding: 10px;
                        border: 1px solid #ddd;
                        margin: 5px;
                        border-radius: 4px;
                        display: inline-block;
                        text-align: center;
                    }
                    .file-item:hover {
                        background: #f0f0f0;
                    }
                    .file-item img {
                        max-width: 100px;
                        max-height: 100px;
                    }
                """
                ),
            ),
            Body(
                Div(cls="container mt-5")(
                    H1(f"Edit: {content.title}"),
                    NotStr(render_flash_messages()),
                    # File browser button
                    Div(cls="mb-3")(
                        Button(
                            "Browse/Upload Files",
                            cls="btn btn-info",
                            **{
                                "data-bs-toggle": "modal",
                                "data-bs-target": "#fileBrowserModal",
                            },
                        ),
                    ),
                    Div(cls="row")(
                        Div(cls="col-md-6")(
                            H4("Editor"),
                            NotStr(
                                f'<form method="post" action="/admin/content/{content_id}/update">{form.render()}<button type="submit" class="btn btn-primary">Update Content</button> <a href="/admin/content" class="btn btn-secondary">Cancel</a></form>'
                            ),
                        ),
                        Div(cls="col-md-6")(
                            H4("Preview"),
                            Div(cls="preview-pane", id="preview")(
                                P("Preview will appear here...")
                            ),
                        ),
                    ),
                    # File browser modal
                    Div(cls="modal fade", id="fileBrowserModal", tabindex="-1")(
                        Div(cls="modal-dialog modal-lg")(
                            Div(cls="modal-content")(
                                Div(cls="modal-header")(
                                    H5("File Browser", cls="modal-title"),
                                    Button(
                                        type="button",
                                        cls="btn-close",
                                        **{"data-bs-dismiss": "modal"},
                                    ),
                                ),
                                Div(cls="modal-body")(
                                    # Upload form
                                    NotStr(
                                        """
                                        <form method="post" action="/admin/upload" enctype="multipart/form-data" id="uploadForm">
                                            <div class="mb-3">
                                                <label class="form-label">Upload File:</label>
                                                <input type="file" name="file" class="form-control" required>
                                            </div>
                                            <button type="submit" class="btn btn-primary">Upload</button>
                                        </form>
                                        <hr>
                                        <h6>Click a file to insert into editor:</h6>
                                        <div id="fileList">
                                    """
                                    ),
                                    *[
                                        Div(
                                            cls="file-item",
                                            **{
                                                "data-url": f["url"],
                                                "data-name": f["name"],
                                                "data-is-image": str(
                                                    f["is_image"]
                                                ).lower(),
                                            },
                                        )(
                                            (
                                                Img(src=f["url"])
                                                if f["is_image"]
                                                else Div()(f["name"])
                                            ),
                                            Br(),
                                            Small(f["name"]),
                                        )
                                        for f in files
                                    ],
                                    NotStr("</div>"),
                                ),
                                Div(cls="modal-footer")(
                                    Button(
                                        "Close",
                                        cls="btn btn-secondary",
                                        **{"data-bs-dismiss": "modal"},
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                Script(
                    """
                    const textarea = document.querySelector('textarea[name="markdown_content"]');
                    const preview = document.getElementById('preview');

                    if (textarea) {
                        updatePreview();
                        textarea.addEventListener('input', updatePreview);

                        function updatePreview() {
                            let text = textarea.value;
                            text = text.replace(/^### (.*$)/gim, '<h3>$1</h3>');
                            text = text.replace(/^## (.*$)/gim, '<h2>$1</h2>');
                            text = text.replace(/^# (.*$)/gim, '<h1>$1</h1>');
                            text = text.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');
                            text = text.replace(/\\*(.+?)\\*/g, '<em>$1</em>');
                            text = text.replace(/\\[(.+?)\\]\\((.+?)\\)/g, '<a href="$2">$1</a>');
                            text = text.replace(/\\n/g, '<br>');
                            preview.innerHTML = text || '<p>Preview will appear here...</p>';
                        }
                    }

                    // File browser - insert markdown link on click
                    document.querySelectorAll('.file-item').forEach(item => {
                        item.addEventListener('click', function() {
                            const url = this.dataset.url;
                            const name = this.dataset.name;
                            const isImage = this.dataset.isImage === 'true';

                            // Generate markdown link
                            const link = isImage ? `![${name}](${url})` : `[${name}](${url})`;

                            // Insert at cursor position
                            const start = textarea.selectionStart;
                            const end = textarea.selectionEnd;
                            const text = textarea.value;
                            textarea.value = text.substring(0, start) + link + text.substring(end);

                            // Update preview
                            updatePreview();

                            // Close modal
                            const modal = bootstrap.Modal.getInstance(document.getElementById('fileBrowserModal'));
                            if (modal) modal.hide();

                            // Focus textarea
                            textarea.focus();
                            textarea.selectionStart = textarea.selectionEnd = start + link.length;
                        });
                    });
                """
                ),
            ),
        )

    @app.post("/admin/content/{content_id}/update")
    async def admin_content_update(request, content_id: int):
        """Update content."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        form_data = await request.form()
        data = dict(form_data)

        # Validate form
        form = Form(
            [
                FormField(name="title", label="Title", required=True),
                FormField(name="slug", label="Slug", required=True),
                FormField(
                    name="markdown_content",
                    label="Content",
                    field_type="textarea",
                    required=True,
                ),
                FormField(
                    name="status", label="Status", field_type="select", required=True
                ),
            ]
        )

        validated = form.validate(data, csrf_token=data.get("csrf_token"))

        if not validated.is_valid:
            flash("Please correct the errors below", "danger")
            return RedirectResponse(
                f"/admin/content/{content_id}/edit", status_code=303
            )

        # Update content
        try:
            from datetime import UTC, datetime

            status_map = {
                "draft": ContentStatus.DRAFT,
                "published": ContentStatus.PUBLISHED,
                "archived": ContentStatus.ARCHIVED,
            }
            new_status = status_map.get(data.get("status"), ContentStatus.DRAFT)

            with get_db_context() as db:
                content = db.query(Content).filter_by(id=content_id).first()
                if not content:
                    flash("Content not found", "danger")
                    return RedirectResponse("/admin/content", status_code=303)

                # Check if slug changed and conflicts with another content
                if content.slug != data.get("slug"):
                    existing = (
                        db.query(Content).filter_by(slug=data.get("slug")).first()
                    )
                    if existing:
                        flash(
                            f"Content with slug '{data.get('slug')}' already exists",
                            "danger",
                        )
                        return RedirectResponse(
                            f"/admin/content/{content_id}/edit", status_code=303
                        )

                old_status = content.status
                content.title = data.get("title")
                content.slug = data.get("slug")
                content.markdown_content = data.get("markdown_content")
                content.status = new_status
                content.updated_at = datetime.now(UTC)

                # Set published_at if transitioning to published
                if (
                    new_status == ContentStatus.PUBLISHED
                    and old_status != ContentStatus.PUBLISHED
                ):
                    content.published_at = datetime.now(UTC)

                db.commit()

            flash(f"Content '{data.get('title')}' updated successfully", "success")
            return RedirectResponse("/admin/content", status_code=303)

        except Exception as e:
            flash(f"Error updating content: {str(e)}", "danger")
            return RedirectResponse(
                f"/admin/content/{content_id}/edit", status_code=303
            )

    @app.get("/admin/content/{content_id}/delete")
    def admin_content_delete(request, content_id: int):
        """Delete content."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        with get_db_context() as db:
            content = db.query(Content).filter_by(id=content_id).first()
            if not content:
                flash("Content not found", "danger")
                return RedirectResponse("/admin/content", status_code=303)

            title = content.title
            db.delete(content)
            db.commit()

        flash(f"Content '{title}' deleted successfully", "success")
        return RedirectResponse("/admin/content", status_code=303)

    # =====================
    # Markdown File Management
    # =====================

    @app.get("/admin/content/new-file")
    def admin_content_new_file(request):
        """Create new markdown file form."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        config = get_config()
        pages_path = config.pages_path

        # Get existing folders for dropdown
        folders = [""]  # Root
        if pages_path.exists():
            for entry in sorted(pages_path.iterdir()):
                if (
                    entry.is_dir()
                    and not entry.name.startswith(".")
                    and not entry.name.startswith("_")
                ):
                    if entry.name.lower() != "images":  # Skip images folder
                        folders.append(entry.name)
                        # Also add subfolders
                        for subentry in sorted(entry.iterdir()):
                            if subentry.is_dir() and not subentry.name.startswith("."):
                                folders.append(f"{entry.name}/{subentry.name}")

        # Build folder options HTML
        folder_options_html = "\n".join(
            [f'<option value="{f}">{f if f else "(root)"}</option>' for f in folders]
        )

        return Html(
            Head(
                Title("Create New Page - Admin"),
                Link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
                ),
                Script(
                    src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"
                ),
                # EasyMDE for better markdown editing
                Link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.css",
                ),
                Script(src="https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.js"),
                Style(
                    """
                    .editor-wrapper { display: flex; gap: 20px; height: 500px; }
                    .editor-pane { flex: 1; display: flex; flex-direction: column; }
                    .preview-pane {
                        flex: 1;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        background: #fff;
                        display: flex;
                        flex-direction: column;
                    }
                    .preview-pane iframe {
                        flex: 1;
                        width: 100%;
                        border: none;
                        border-radius: 4px;
                    }
                    .preview-header {
                        background: #f8f9fa;
                        padding: 8px 12px;
                        border-bottom: 1px solid #ddd;
                        font-weight: 500;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }
                    .preview-status { font-size: 12px; color: #666; }
                    .EasyMDEContainer { flex: 1; display: flex; flex-direction: column; }
                    .EasyMDEContainer .CodeMirror { flex: 1; min-height: 400px; }
                """
                ),
            ),
            Body(
                Div(cls="container-fluid mt-4")(
                    H1("Create New Page"),
                    NotStr(render_flash_messages()),
                    NotStr(
                        f"""
                    <form method="post" action="/admin/content/create-file">
                        <div class="row mb-3">
                            <div class="col-md-4">
                                <label class="form-label">Folder</label>
                                <select name="folder" class="form-select">
                                    {folder_options_html}
                                </select>
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">Filename (without .md)</label>
                                <input type="text" name="filename" class="form-control" placeholder="my-new-page" required>
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">Sidebar Position</label>
                                <input type="number" name="sidebar_position" class="form-control" placeholder="1">
                            </div>
                        </div>

                        <div class="mb-3">
                            <label class="form-label">Title</label>
                            <input type="text" name="title" class="form-control" placeholder="Page Title" required>
                        </div>

                        <div class="editor-wrapper">
                            <div class="editor-pane">
                                <label class="form-label">Content (Markdown)</label>
                                <textarea name="content" id="markdown-editor" placeholder="# Your content here..."></textarea>
                            </div>
                            <div class="preview-pane">
                                <div class="preview-header">
                                    <span>Live Preview</span>
                                    <span class="preview-status" id="preview-status">Ready</span>
                                </div>
                                <iframe id="preview-frame" srcdoc="<p style='color:#666;padding:15px;'>Start typing to see preview...</p>"></iframe>
                            </div>
                        </div>

                        <div class="mt-3">
                            <button type="submit" class="btn btn-success">Create Page</button>
                            <a href="/admin/content" class="btn btn-secondary">Cancel</a>
                        </div>
                    </form>
                    """
                    ),
                ),
                Script(
                    """
                    // Initialize EasyMDE editor
                    const easyMDE = new EasyMDE({
                        element: document.getElementById('markdown-editor'),
                        spellChecker: false,
                        autosave: { enabled: false },
                        toolbar: ["bold", "italic", "heading", "|", "quote", "unordered-list", "ordered-list", "|", "link", "image", "table", "|", "fullscreen", "|", "guide"],
                        sideBySideFullscreen: false,
                        status: false,
                        placeholder: "# Your content here...",
                    });

                    // Live preview using actual parser
                    const previewFrame = document.getElementById('preview-frame');
                    const previewStatus = document.getElementById('preview-status');
                    let previewTimeout = null;

                    async function updatePreview() {
                        const content = easyMDE.value();
                        if (!content.trim()) {
                            previewFrame.srcdoc = "<p style='color:#666;padding:15px;'>Start typing to see preview...</p>";
                            previewStatus.textContent = 'Ready';
                            return;
                        }

                        previewStatus.textContent = 'Updating...';

                        try {
                            const formData = new FormData();
                            formData.append('content', content);

                            const response = await fetch('/admin/preview', {
                                method: 'POST',
                                body: formData
                            });

                            if (response.ok) {
                                const html = await response.text();
                                previewFrame.srcdoc = html;
                                previewStatus.textContent = 'Updated';
                            } else {
                                previewStatus.textContent = 'Error';
                            }
                        } catch (err) {
                            previewStatus.textContent = 'Error: ' + err.message;
                        }
                    }

                    // Debounce preview updates (500ms delay)
                    function debouncedPreview() {
                        clearTimeout(previewTimeout);
                        previewStatus.textContent = 'Typing...';
                        previewTimeout = setTimeout(updatePreview, 500);
                    }

                    easyMDE.codemirror.on('change', debouncedPreview);
                """
                ),
            ),
        )

    @app.post("/admin/content/create-file")
    async def admin_content_create_file(request):
        """Create new markdown file."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        form_data = await request.form()
        folder = form_data.get("folder", "")
        filename = form_data.get("filename", "").strip()
        title = form_data.get("title", "").strip()
        sidebar_position = form_data.get("sidebar_position", "").strip()
        content = form_data.get("content", "")

        if not filename or not title:
            flash("Filename and title are required", "danger")
            return RedirectResponse("/admin/content/new-file", status_code=303)

        # Sanitize filename
        import re

        filename = re.sub(r"[^a-zA-Z0-9_-]", "-", filename.lower())
        filename = re.sub(r"-+", "-", filename).strip("-")

        if not filename:
            flash("Invalid filename", "danger")
            return RedirectResponse("/admin/content/new-file", status_code=303)

        config = get_config()
        pages_path = config.pages_path

        # Build file path
        if folder:
            file_path = pages_path / folder / f"{filename}.md"
        else:
            file_path = pages_path / f"{filename}.md"

        # Check if file already exists
        if file_path.exists():
            flash(f"File '{filename}.md' already exists in this folder", "danger")
            return RedirectResponse("/admin/content/new-file", status_code=303)

        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Build frontmatter
        frontmatter = f"---\ntitle: {title}\n"
        if sidebar_position:
            frontmatter += f"sidebar_position: {sidebar_position}\n"
        frontmatter += "---\n\n"

        # Write file
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(frontmatter + content)

            flash(f"Page '{title}' created successfully", "success")
            return RedirectResponse("/admin/content", status_code=303)

        except Exception as e:
            flash(f"Error creating file: {str(e)}", "danger")
            return RedirectResponse("/admin/content/new-file", status_code=303)

    @app.get("/admin/content/edit-file")
    def admin_content_edit_file(request):
        """Edit markdown file form."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        file_path_param = request.query_params.get("path", "")
        if not file_path_param:
            flash("No file specified", "danger")
            return RedirectResponse("/admin/content", status_code=303)

        config = get_config()
        pages_path = config.pages_path
        file_path = pages_path / file_path_param

        # Security check - ensure file is within pages directory
        try:
            file_path.resolve().relative_to(pages_path.resolve())
        except ValueError:
            flash("Invalid file path", "danger")
            return RedirectResponse("/admin/content", status_code=303)

        if not file_path.exists():
            flash("File not found", "danger")
            return RedirectResponse("/admin/content", status_code=303)

        # Read file content
        try:
            with open(file_path, encoding="utf-8") as f:
                file_content = f.read()
        except Exception as e:
            flash(f"Error reading file: {str(e)}", "danger")
            return RedirectResponse("/admin/content", status_code=303)

        # Extract frontmatter and content
        import re

        title = ""
        sidebar_position = ""
        content_body = file_content

        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", file_content, re.DOTALL)
        if fm_match:
            frontmatter_text = fm_match.group(1)
            content_body = file_content[fm_match.end() :]

            for line in frontmatter_text.split("\n"):
                if line.strip().startswith("title:"):
                    title = line.split(":", 1)[1].strip().strip('"').strip("'")
                elif line.strip().startswith("sidebar_position:"):
                    sidebar_position = line.split(":", 1)[1].strip()

        # Escape content for HTML
        import html

        escaped_content = html.escape(content_body)
        escaped_title = html.escape(title)

        return Html(
            Head(
                Title(f"Edit: {title or file_path_param} - Admin"),
                Link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
                ),
                Script(
                    src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"
                ),
                # EasyMDE for better markdown editing
                Link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.css",
                ),
                Script(src="https://cdn.jsdelivr.net/npm/easymde/dist/easymde.min.js"),
                Style(
                    """
                    .editor-wrapper { display: flex; gap: 20px; height: 600px; }
                    .editor-pane { flex: 1; display: flex; flex-direction: column; }
                    .preview-pane {
                        flex: 1;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        background: #fff;
                        display: flex;
                        flex-direction: column;
                    }
                    .preview-pane iframe {
                        flex: 1;
                        width: 100%;
                        border: none;
                        border-radius: 4px;
                    }
                    .preview-header {
                        background: #f8f9fa;
                        padding: 8px 12px;
                        border-bottom: 1px solid #ddd;
                        font-weight: 500;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }
                    .preview-status { font-size: 12px; color: #666; }
                    .EasyMDEContainer { flex: 1; display: flex; flex-direction: column; }
                    .EasyMDEContainer .CodeMirror { flex: 1; min-height: 500px; }
                """
                ),
            ),
            Body(
                Div(cls="container-fluid mt-4")(
                    H1(f"Edit: {title or file_path_param}"),
                    P(cls="text-muted")(f"File: {file_path_param}"),
                    NotStr(render_flash_messages()),
                    NotStr(
                        f"""
                    <form method="post" action="/admin/content/update-file">
                        <input type="hidden" name="path" value="{file_path_param}">

                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label class="form-label">Title</label>
                                <input type="text" name="title" class="form-control" value="{escaped_title}" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Sidebar Position</label>
                                <input type="number" name="sidebar_position" class="form-control" value="{sidebar_position}">
                            </div>
                        </div>

                        <div class="editor-wrapper">
                            <div class="editor-pane">
                                <label class="form-label">Content (Markdown)</label>
                                <textarea name="content" id="markdown-editor">{escaped_content}</textarea>
                            </div>
                            <div class="preview-pane">
                                <div class="preview-header">
                                    <span>Live Preview</span>
                                    <span class="preview-status" id="preview-status">Ready</span>
                                </div>
                                <iframe id="preview-frame" srcdoc="<p style='color:#666;padding:15px;'>Loading preview...</p>"></iframe>
                            </div>
                        </div>

                        <div class="mt-3">
                            <button type="submit" class="btn btn-primary">Save Changes</button>
                            <a href="/admin/content" class="btn btn-secondary">Cancel</a>
                            <a href="/{file_path_param.replace('.md', '')}" target="_blank" class="btn btn-info">View Page</a>
                        </div>
                    </form>
                    """
                    ),
                ),
                Script(
                    """
                    console.log('[Editor] Starting initialization...');

                    // Initialize EasyMDE editor
                    const easyMDE = new EasyMDE({
                        element: document.getElementById('markdown-editor'),
                        spellChecker: false,
                        autosave: { enabled: false },
                        toolbar: ["bold", "italic", "heading", "|", "quote", "unordered-list", "ordered-list", "|", "link", "image", "table", "|", "fullscreen", "|", "guide"],
                        sideBySideFullscreen: false,
                        status: false,
                        // Don't use EasyMDE's built-in preview - we use our own iframe preview
                        previewRender: function(plainText) { return ''; },
                    });

                    console.log('[Editor] EasyMDE initialized');

                    // Live preview using actual parser (our iframe on the right side)
                    const previewFrame = document.getElementById('preview-frame');
                    const previewStatus = document.getElementById('preview-status');

                    if (!previewFrame) {
                        console.error('[Editor] ERROR: preview-frame element not found!');
                    }
                    if (!previewStatus) {
                        console.error('[Editor] ERROR: preview-status element not found!');
                    }

                    let previewTimeout = null;

                    async function updatePreview() {
                        const content = easyMDE.value();
                        console.log('[Preview] Content length:', content.length);
                        console.log('[Preview] Has :::card:', content.includes(':::card'));
                        previewStatus.textContent = 'Updating...';

                        try {
                            const formData = new FormData();
                            formData.append('content', content);

                            console.log('[Preview] Sending POST to /admin/preview');
                            const response = await fetch('/admin/preview', {
                                method: 'POST',
                                body: formData
                            });

                            console.log('[Preview] Response status:', response.status);

                            if (response.ok) {
                                const html = await response.text();
                                console.log('[Preview] Received HTML length:', html.length);
                                console.log('[Preview] Has card div:', html.includes('class="card"'));
                                previewFrame.srcdoc = html;
                                previewStatus.textContent = 'Updated';
                            } else {
                                console.error('[Preview] Error response:', response.status);
                                previewStatus.textContent = 'Error: ' + response.status;
                            }
                        } catch (err) {
                            console.error('[Preview] Fetch error:', err);
                            previewStatus.textContent = 'Error: ' + err.message;
                        }
                    }

                    // Debounce preview updates (500ms delay)
                    function debouncedPreview() {
                        clearTimeout(previewTimeout);
                        previewStatus.textContent = 'Typing...';
                        previewTimeout = setTimeout(updatePreview, 500);
                    }

                    easyMDE.codemirror.on('change', debouncedPreview);

                    // Initial preview
                    console.log('[Preview] Triggering initial preview...');
                    updatePreview();
                """
                ),
            ),
        )

    @app.post("/admin/content/update-file")
    async def admin_content_update_file(request):
        """Update markdown file."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        form_data = await request.form()
        file_path_param = form_data.get("path", "")
        title = form_data.get("title", "").strip()
        sidebar_position = form_data.get("sidebar_position", "").strip()
        content = form_data.get("content", "")

        if not file_path_param or not title:
            flash("Path and title are required", "danger")
            return RedirectResponse("/admin/content", status_code=303)

        config = get_config()
        pages_path = config.pages_path
        file_path = pages_path / file_path_param

        # Security check
        try:
            file_path.resolve().relative_to(pages_path.resolve())
        except ValueError:
            flash("Invalid file path", "danger")
            return RedirectResponse("/admin/content", status_code=303)

        if not file_path.exists():
            flash("File not found", "danger")
            return RedirectResponse("/admin/content", status_code=303)

        # Build frontmatter
        frontmatter = f"---\ntitle: {title}\n"
        if sidebar_position:
            frontmatter += f"sidebar_position: {sidebar_position}\n"
        frontmatter += "---\n\n"

        # Write file
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(frontmatter + content)

            flash(f"Page '{title}' updated successfully", "success")
            return RedirectResponse("/admin/content", status_code=303)

        except Exception as e:
            flash(f"Error saving file: {str(e)}", "danger")
            return RedirectResponse(
                f"/admin/content/edit-file?path={file_path_param}", status_code=303
            )

    @app.post("/admin/preview")
    async def admin_preview(request):
        """Render markdown preview using the actual parser."""
        import sys

        form_data = await request.form()
        markdown_content = form_data.get("content", "")

        print("[PREVIEW] === Preview Request ===", file=sys.stderr, flush=True)
        print(
            f"[PREVIEW] Input length: {len(markdown_content)}",
            file=sys.stderr,
            flush=True,
        )
        print(
            f"[PREVIEW] Contains :::card: {':::card' in markdown_content}",
            file=sys.stderr,
            flush=True,
        )
        print(
            f"[PREVIEW] Has CR (\\r): {chr(13) in markdown_content}",
            file=sys.stderr,
            flush=True,
        )
        print(
            f"[PREVIEW] First 300 chars repr: {repr(markdown_content[:300])}",
            file=sys.stderr,
            flush=True,
        )

        # Parse using our full markdown parser
        try:
            result = _parser.parse(markdown_content)
            html_content = result.get("html", "")
            print(f"[PREVIEW] Output length: {len(html_content)}", file=sys.stderr)
            print(
                f"[PREVIEW] Has card class: {'class=\"card\"' in html_content}",
                file=sys.stderr,
            )
            print(
                f"[PREVIEW] First 500 chars of output: {html_content[:500]}",
                file=sys.stderr,
            )
        except Exception as e:
            import traceback

            traceback.print_exc()
            print(f"[PREVIEW] ERROR: {str(e)}", file=sys.stderr)
            html_content = f"<div class='text-danger'>Preview error: {str(e)}</div>"

        # Load theme CSS for proper styling
        config = get_config()
        theme_css_path = config.themes_path / config.theme / "styles.css"
        theme_css = ""
        if theme_css_path.exists():
            theme_css = theme_css_path.read_text(encoding="utf-8")

        # Return complete HTML document for iframe
        return Response(
            content=f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    <style>
        body {{ padding: 15px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; }}
        {theme_css}
    </style>
</head>
<body>
    <div class="content">
        {html_content}
    </div>
</body>
</html>""",
            media_type="text/html",
        )

    @app.get("/admin/settings")
    def admin_settings(request):
        """Admin settings page."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        user = get_current_user(request)

        # Get system info
        with get_db_context() as db:
            total_users = db.query(User).count()
            active_users = db.query(User).filter_by(is_active=True).count()
            total_content = db.query(Content).count()
            published = (
                db.query(Content).filter_by(status=ContentStatus.PUBLISHED).count()
            )
            drafts = db.query(Content).filter_by(status=ContentStatus.DRAFT).count()

        return Html(
            Head(
                Title("Settings - Admin"),
                Link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
                ),
                Script(
                    src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"
                ),
            ),
            Body(
                Div(cls="container mt-5")(
                    H1("Settings"),
                    NotStr(render_flash_messages()),
                    Div(cls="row mt-4")(
                        Div(cls="col-md-6")(
                            Div(cls="card")(
                                Div(cls="card-header")(H5("System Information")),
                                Div(cls="card-body")(
                                    Table(cls="table table-sm")(
                                        Tbody(
                                            Tr(
                                                Td("Total Users:"), Td(str(total_users))
                                            ),
                                            Tr(
                                                Td("Active Users:"),
                                                Td(str(active_users)),
                                            ),
                                            Tr(
                                                Td("Total Content:"),
                                                Td(str(total_content)),
                                            ),
                                            Tr(Td("Published:"), Td(str(published))),
                                            Tr(Td("Drafts:"), Td(str(drafts))),
                                        )
                                    ),
                                ),
                            ),
                        ),
                        Div(cls="col-md-6")(
                            Div(cls="card")(
                                Div(cls="card-header")(H5("Current User")),
                                Div(cls="card-body")(
                                    P(f"Username: {user.username}"),
                                    P(f"Email: {user.email}"),
                                    P(f"Role: {user.role.value.title()}"),
                                    P(f"Full Name: {user.full_name or 'Not set'}"),
                                ),
                            ),
                        ),
                    ),
                    Div(cls="row mt-4")(
                        Div(cls="col-md-12")(
                            Div(cls="card")(
                                Div(cls="card-header")(H5("Quick Actions")),
                                Div(cls="card-body")(
                                    A(href="/admin/users/new", cls="btn btn-primary")(
                                        "Add New User"
                                    ),
                                    Span(" "),
                                    A(href="/admin/content/new", cls="btn btn-success")(
                                        "Create Content"
                                    ),
                                    Span(" "),
                                    A(href="/admin/datasources", cls="btn btn-info")(
                                        "Manage Data Sources"
                                    ),
                                ),
                            ),
                        ),
                    ),
                    Div(cls="mt-4")(
                        A(href="/admin", cls="btn btn-secondary")("Back to Dashboard"),
                    ),
                )
            ),
        )

    @app.get("/admin/files")
    def admin_files_list(request):
        """List uploaded files."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        config = get_config()
        uploads_dir = config.static_path / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)

        # Get all files in uploads directory
        files = []
        if uploads_dir.exists():
            for file_path in uploads_dir.iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append(
                        {
                            "name": file_path.name,
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime),
                            "url": f"/static/uploads/{file_path.name}",
                        }
                    )

        # Sort by modified date (newest first)
        files.sort(key=lambda x: x["modified"], reverse=True)

        rows = []
        for file in files:
            size_kb = file["size"] / 1024
            size_str = (
                f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
            )

            # Determine file type
            ext = Path(file["name"]).suffix.lower()
            file_type = (
                "Image"
                if ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]
                else "File"
            )

            rows.append(
                Tr(
                    Td(
                        Img(
                            src=file["url"], style="max-width: 100px; max-height: 50px;"
                        )
                        if file_type == "Image"
                        else file["name"]
                    ),
                    Td(file["name"]),
                    Td(file_type),
                    Td(size_str),
                    Td(file["modified"].strftime("%Y-%m-%d %H:%M")),
                    Td(
                        Button(
                            "Copy Link",
                            cls="btn btn-sm btn-primary copy-link",
                            **{
                                "data-link": (
                                    f"![{file['name']}]({file['url']})"
                                    if file_type == "Image"
                                    else f"[{file['name']}]({file['url']})"
                                )
                            },
                        ),
                        " ",
                        A(href=file["url"], target="_blank", cls="btn btn-sm btn-info")(
                            "View"
                        ),
                        " ",
                        A(
                            href=f"/admin/files/{file['name']}/delete",
                            cls="btn btn-sm btn-danger",
                        )("Delete"),
                    ),
                )
            )

        return Html(
            Head(
                Title("Manage Files - Admin"),
                Link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
                ),
                Script(
                    src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"
                ),
            ),
            Body(
                Div(cls="container mt-5")(
                    H1("Manage Files"),
                    NotStr(render_flash_messages()),
                    Div(cls="mb-3")(
                        NotStr(
                            """
                        <form method="post" action="/admin/upload" enctype="multipart/form-data" class="d-inline-block">
                            <input type="file" name="file" class="form-control d-inline-block" style="width: auto; display: inline-block;" required>
                            <button type="submit" class="btn btn-success">Upload File</button>
                        </form>
                        """
                        ),
                    ),
                    Table(cls="table table-striped")(
                        Thead(
                            Tr(
                                Th("Preview"),
                                Th("Filename"),
                                Th("Type"),
                                Th("Size"),
                                Th("Uploaded"),
                                Th("Actions"),
                            )
                        ),
                        (
                            Tbody(*rows)
                            if rows
                            else Tbody(Tr(Td(colspan="6")("No files uploaded yet")))
                        ),
                    ),
                    A(href="/admin", cls="btn btn-secondary")("Back to Dashboard"),
                ),
                Script(
                    """
                    // Copy markdown link to clipboard
                    document.querySelectorAll('.copy-link').forEach(button => {
                        button.addEventListener('click', function() {
                            const link = this.getAttribute('data-link');
                            navigator.clipboard.writeText(link).then(() => {
                                const originalText = this.textContent;
                                this.textContent = 'Copied!';
                                setTimeout(() => {
                                    this.textContent = originalText;
                                }, 2000);
                            });
                        });
                    });
                """
                ),
            ),
        )

    @app.post("/admin/upload")
    async def admin_upload_file(request):
        """Upload a file."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        try:
            form = await request.form()
            file = form.get("file")

            if not file or not hasattr(file, "filename"):
                flash("No file selected", "danger")
                return RedirectResponse("/admin/files", status_code=303)

            # Get uploads directory
            config = get_config()
            uploads_dir = config.static_path / "uploads"
            uploads_dir.mkdir(parents=True, exist_ok=True)

            # Sanitize filename
            filename = file.filename
            # Remove any path components
            filename = Path(filename).name
            # Replace spaces with hyphens
            filename = filename.replace(" ", "-")

            # Check if file already exists
            file_path = uploads_dir / filename
            if file_path.exists():
                # Add timestamp to make unique
                name, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{name}_{timestamp}{ext}"
                file_path = uploads_dir / filename

            # Save file
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            flash(f"File '{filename}' uploaded successfully", "success")
            return RedirectResponse("/admin/files", status_code=303)

        except Exception as e:
            flash(f"Error uploading file: {str(e)}", "danger")
            return RedirectResponse("/admin/files", status_code=303)

    @app.get("/admin/files/{filename}/delete")
    def admin_delete_file(request, filename: str):
        """Delete an uploaded file."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        try:
            config = get_config()
            file_path = config.static_path / "uploads" / filename

            # Security check - ensure file is in uploads directory
            if not file_path.resolve().is_relative_to(config.static_path / "uploads"):
                flash("Invalid file path", "danger")
                return RedirectResponse("/admin/files", status_code=303)

            if file_path.exists():
                file_path.unlink()
                flash(f"File '{filename}' deleted successfully", "success")
            else:
                flash("File not found", "warning")

            return RedirectResponse("/admin/files", status_code=303)

        except Exception as e:
            flash(f"Error deleting file: {str(e)}", "danger")
            return RedirectResponse("/admin/files", status_code=303)

    # =====================
    # Data Source Management
    # =====================

    @app.get("/admin/datasources")
    def admin_datasources_list(request):
        """List all data sources."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        with get_db_context() as db:
            datasources = db.query(DataSource).all()
            db.expunge_all()

        # Get registry to show which are loaded
        registry = get_registry()
        loaded_sources = set(registry.list_all())

        rows = []
        for ds in datasources:
            is_loaded = ds.name in loaded_sources
            rows.append(
                Tr(
                    Td(ds.name),
                    Td(ds.description or "-"),
                    Td(ds.function_path),
                    Td(
                        Span("Active", cls="badge bg-success")
                        if ds.is_active
                        else Span("Inactive", cls="badge bg-secondary")
                    ),
                    Td("Yes" if ds.requires_auth else "No"),
                    Td(ds.allowed_roles or "All"),
                    Td(
                        Span("Loaded", cls="badge bg-info")
                        if is_loaded
                        else Span("Not Loaded", cls="badge bg-warning")
                    ),
                    Td(
                        A(
                            href=f"/admin/datasources/{ds.id}/edit",
                            cls="btn btn-sm btn-primary",
                        )("Edit"),
                        " ",
                        A(
                            href=f"/admin/datasources/{ds.id}/delete",
                            cls="btn btn-sm btn-danger",
                        )("Delete"),
                    ),
                )
            )

        return Html(
            Head(
                Title("Manage Data Sources - Admin"),
                Link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
                ),
            ),
            Body(
                Div(cls="container mt-5")(
                    H1("Manage Data Sources"),
                    NotStr(render_flash_messages()),
                    P(cls="text-muted")(
                        "Data sources provide dynamic data for the :::table component. ",
                        "Each source must reference a Python function path.",
                    ),
                    Div(cls="mb-3")(
                        A(href="/admin/datasources/new", cls="btn btn-success")(
                            "Add New Data Source"
                        ),
                        " ",
                        A(href="/admin/datasources/reload", cls="btn btn-info")(
                            "Reload Registry"
                        ),
                    ),
                    Table(cls="table table-striped")(
                        Thead(
                            Tr(
                                Th("Name"),
                                Th("Description"),
                                Th("Function Path"),
                                Th("Status"),
                                Th("Auth Required"),
                                Th("Allowed Roles"),
                                Th("Loaded"),
                                Th("Actions"),
                            )
                        ),
                        (
                            Tbody(*rows)
                            if rows
                            else Tbody(
                                Tr(Td(colspan="8")("No data sources defined yet"))
                            )
                        ),
                    ),
                    A(href="/admin", cls="btn btn-secondary")("Back to Dashboard"),
                )
            ),
        )

    @app.get("/admin/datasources/new")
    def admin_datasources_new(request):
        """Create new data source form."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        form = Form(
            [
                FormField(
                    name="name",
                    label="Name",
                    required=True,
                    placeholder="my_data_source",
                    validators=[
                        ValidationRule(
                            "pattern",
                            "Name must be lowercase alphanumeric with underscores",
                            lambda x: bool(
                                __import__("re").match(r"^[a-z0-9_]+$", str(x))
                            ),
                        ),
                    ],
                ),
                FormField(
                    name="description",
                    label="Description",
                    required=False,
                    placeholder="Description of what this data source provides",
                ),
                FormField(
                    name="function_path",
                    label="Function Path",
                    required=True,
                    placeholder="markdown_cms.core.queries.get_all_content",
                ),
                FormField(
                    name="is_active",
                    label="Status",
                    field_type="select",
                    required=True,
                    options=[
                        ("true", "Active"),
                        ("false", "Inactive"),
                    ],
                    default_value="true",
                ),
                FormField(
                    name="requires_auth",
                    label="Requires Authentication",
                    field_type="select",
                    required=True,
                    options=[
                        ("true", "Yes"),
                        ("false", "No"),
                    ],
                    default_value="true",
                ),
                FormField(
                    name="allowed_roles",
                    label="Allowed Roles (comma-separated, leave empty for all)",
                    required=False,
                    placeholder="admin,editor",
                ),
            ]
        )

        return Html(
            Head(
                Title("Add New Data Source - Admin"),
                Link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
                ),
            ),
            Body(
                Div(cls="container mt-5")(
                    H1("Add New Data Source"),
                    NotStr(render_flash_messages()),
                    Div(cls="alert alert-info")(
                        Strong("Function Path Format: "),
                        "Use the full Python import path to your function, e.g., ",
                        Code("markdown_cms.core.queries.get_published_content"),
                    ),
                    NotStr(
                        f'<form method="post" action="/admin/datasources/create">{form.render()}<button type="submit" class="btn btn-primary">Create Data Source</button> <a href="/admin/datasources" class="btn btn-secondary">Cancel</a></form>'
                    ),
                )
            ),
        )

    @app.post("/admin/datasources/create")
    async def admin_datasources_create(request):
        """Create new data source."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        form_data = await request.form()
        data = dict(form_data)

        # Validate form
        form = Form(
            [
                FormField(name="name", label="Name", required=True),
                FormField(name="description", label="Description", required=False),
                FormField(name="function_path", label="Function Path", required=True),
                FormField(
                    name="is_active", label="Status", field_type="select", required=True
                ),
                FormField(
                    name="requires_auth",
                    label="Auth Required",
                    field_type="select",
                    required=True,
                ),
                FormField(name="allowed_roles", label="Allowed Roles", required=False),
            ]
        )

        validated = form.validate(data, csrf_token=data.get("csrf_token"))

        if not validated.is_valid:
            flash("Please correct the errors below", "danger")
            return RedirectResponse("/admin/datasources/new", status_code=303)

        try:
            with get_db_context() as db:
                # Check if name already exists
                existing = db.query(DataSource).filter_by(name=data.get("name")).first()
                if existing:
                    flash(f"Data source '{data.get('name')}' already exists", "danger")
                    return RedirectResponse("/admin/datasources/new", status_code=303)

                ds = DataSource(
                    name=data.get("name"),
                    description=data.get("description") or None,
                    function_path=data.get("function_path"),
                    is_active=data.get("is_active") == "true",
                    requires_auth=data.get("requires_auth") == "true",
                    allowed_roles=data.get("allowed_roles") or None,
                )
                db.add(ds)
                db.commit()

            # Reload registry to pick up new source
            registry = get_registry()
            registry.reload()

            flash(f"Data source '{data.get('name')}' created successfully", "success")
            return RedirectResponse("/admin/datasources", status_code=303)

        except Exception as e:
            flash(f"Error creating data source: {str(e)}", "danger")
            return RedirectResponse("/admin/datasources/new", status_code=303)

    @app.get("/admin/datasources/{ds_id}/edit")
    def admin_datasources_edit(request, ds_id: int):
        """Edit data source form."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        with get_db_context() as db:
            ds = db.query(DataSource).filter_by(id=ds_id).first()
            if not ds:
                flash("Data source not found", "danger")
                return RedirectResponse("/admin/datasources", status_code=303)
            db.expunge(ds)

        form = Form(
            [
                FormField(
                    name="name",
                    label="Name",
                    required=True,
                    default_value=ds.name,
                ),
                FormField(
                    name="description",
                    label="Description",
                    required=False,
                    default_value=ds.description or "",
                ),
                FormField(
                    name="function_path",
                    label="Function Path",
                    required=True,
                    default_value=ds.function_path,
                ),
                FormField(
                    name="is_active",
                    label="Status",
                    field_type="select",
                    required=True,
                    options=[
                        ("true", "Active"),
                        ("false", "Inactive"),
                    ],
                    default_value="true" if ds.is_active else "false",
                ),
                FormField(
                    name="requires_auth",
                    label="Requires Authentication",
                    field_type="select",
                    required=True,
                    options=[
                        ("true", "Yes"),
                        ("false", "No"),
                    ],
                    default_value="true" if ds.requires_auth else "false",
                ),
                FormField(
                    name="allowed_roles",
                    label="Allowed Roles (comma-separated, leave empty for all)",
                    required=False,
                    default_value=ds.allowed_roles or "",
                ),
            ]
        )

        return Html(
            Head(
                Title(f"Edit Data Source: {ds.name} - Admin"),
                Link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
                ),
            ),
            Body(
                Div(cls="container mt-5")(
                    H1(f"Edit Data Source: {ds.name}"),
                    NotStr(render_flash_messages()),
                    NotStr(
                        f'<form method="post" action="/admin/datasources/{ds_id}/update">{form.render()}<button type="submit" class="btn btn-primary">Update Data Source</button> <a href="/admin/datasources" class="btn btn-secondary">Cancel</a></form>'
                    ),
                )
            ),
        )

    @app.post("/admin/datasources/{ds_id}/update")
    async def admin_datasources_update(request, ds_id: int):
        """Update data source."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        form_data = await request.form()
        data = dict(form_data)

        try:
            with get_db_context() as db:
                ds = db.query(DataSource).filter_by(id=ds_id).first()
                if not ds:
                    flash("Data source not found", "danger")
                    return RedirectResponse("/admin/datasources", status_code=303)

                # Check if name changed and conflicts with another
                if ds.name != data.get("name"):
                    existing = (
                        db.query(DataSource).filter_by(name=data.get("name")).first()
                    )
                    if existing:
                        flash(
                            f"Data source '{data.get('name')}' already exists", "danger"
                        )
                        return RedirectResponse(
                            f"/admin/datasources/{ds_id}/edit", status_code=303
                        )

                ds.name = data.get("name")
                ds.description = data.get("description") or None
                ds.function_path = data.get("function_path")
                ds.is_active = data.get("is_active") == "true"
                ds.requires_auth = data.get("requires_auth") == "true"
                ds.allowed_roles = data.get("allowed_roles") or None

                db.commit()

            # Reload registry
            registry = get_registry()
            registry.reload()

            flash(f"Data source '{data.get('name')}' updated successfully", "success")
            return RedirectResponse("/admin/datasources", status_code=303)

        except Exception as e:
            flash(f"Error updating data source: {str(e)}", "danger")
            return RedirectResponse(f"/admin/datasources/{ds_id}/edit", status_code=303)

    @app.get("/admin/datasources/{ds_id}/delete")
    def admin_datasources_delete(request, ds_id: int):
        """Delete data source."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        with get_db_context() as db:
            ds = db.query(DataSource).filter_by(id=ds_id).first()
            if not ds:
                flash("Data source not found", "danger")
                return RedirectResponse("/admin/datasources", status_code=303)

            name = ds.name
            db.delete(ds)
            db.commit()

        # Reload registry
        registry = get_registry()
        registry.reload()

        flash(f"Data source '{name}' deleted successfully", "success")
        return RedirectResponse("/admin/datasources", status_code=303)

    @app.get("/admin/datasources/reload")
    def admin_datasources_reload(request):
        """Reload data source registry."""
        auth_check = require_admin(request)
        if auth_check:
            return auth_check

        registry = get_registry()
        registry.reload()

        flash("Data source registry reloaded successfully", "success")
        return RedirectResponse("/admin/datasources", status_code=303)
