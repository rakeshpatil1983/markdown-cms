"""Authentication routes for login/logout."""

from typing import Optional

from fasthtml.common import *

from .auth import (
    authenticate_user,
    create_initial_admin,
    create_session,
    get_user_by_session,
    invalidate_session,
    is_setup_required,
)
from .models import User

# Session cookie name
SESSION_COOKIE_NAME = "cms_session"
SESSION_COOKIE_MAX_AGE = 7 * 24 * 60 * 60  # 7 days in seconds


def get_current_user(request) -> Optional[User]:
    """
    Get current authenticated user from request.

    Args:
        request: FastHTML request object

    Returns:
        User object if authenticated, None otherwise
    """
    # Get session cookie
    session_id = request.cookies.get(SESSION_COOKIE_NAME)

    if not session_id:
        return None

    # Get user from session
    user = get_user_by_session(session_id)
    return user


def require_auth(request):
    """
    Decorator/middleware to require authentication.

    Usage:
        @app.get("/admin")
        def admin_page(request):
            user = require_auth(request)
            if not user:
                return RedirectResponse("/login")
            # ... rest of handler
    """
    user = get_current_user(request)
    return user


def require_role(request, allowed_roles: list[str]):
    """
    Require specific role(s) for access.

    Args:
        request: FastHTML request object
        allowed_roles: List of allowed role names (e.g., ["admin", "editor"])

    Returns:
        User if authenticated and has role, None otherwise
    """
    user = get_current_user(request)

    if not user:
        return None

    if user.role.value not in allowed_roles:
        return None

    return user


def setup_auth_routes(app):
    """Setup authentication routes."""

    @app.get("/login")
    def login_page(request):
        """Login page."""
        # Check if setup is required (no admin exists)
        if is_setup_required():
            return RedirectResponse("/setup")

        # Check if already logged in
        user = get_current_user(request)
        if user:
            return RedirectResponse("/admin")

        # Get error message if any
        error = request.query_params.get("error")
        error_msg = None
        if error == "invalid":
            error_msg = "Invalid username or password"
        elif error == "missing":
            error_msg = "Please enter username and password"

        # Render login form
        return Html(
            Head(
                Title("Login - Markdown CMS"),
                Meta(charset="utf-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1"),
                Link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
                ),
                Style(
                    """
                    body {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    .login-card {
                        background: white;
                        border-radius: 15px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                        padding: 3rem;
                        width: 100%;
                        max-width: 400px;
                    }
                    .login-card h1 {
                        color: #667eea;
                        margin-bottom: 2rem;
                        text-align: center;
                    }
                    .btn-login {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border: none;
                        padding: 12px;
                        font-weight: 600;
                    }
                    .btn-login:hover {
                        opacity: 0.9;
                    }
                    .error-message {
                        background: #fee;
                        border: 1px solid #fcc;
                        border-radius: 8px;
                        padding: 12px;
                        margin-bottom: 1rem;
                        color: #c33;
                    }
                """
                ),
            ),
            Body(
                Div(cls="login-card")(
                    H1("Markdown CMS"),
                    Div(cls="error-message")(error_msg) if error_msg else None,
                    Form(
                        method="post",
                        action="/login",
                    )(
                        Div(cls="mb-3")(
                            Label("Username", cls="form-label", for_="username"),
                            Input(
                                type="text",
                                cls="form-control",
                                id="username",
                                name="username",
                                required=True,
                                autofocus=True,
                            ),
                        ),
                        Div(cls="mb-3")(
                            Label("Password", cls="form-label", for_="password"),
                            Input(
                                type="password",
                                cls="form-control",
                                id="password",
                                name="password",
                                required=True,
                            ),
                        ),
                        Button(
                            "Login",
                            type="submit",
                            cls="btn btn-primary btn-login w-100",
                        ),
                    ),
                ),
            ),
        )

    @app.get("/setup")
    def setup_page(request):
        """Initial setup page - create first admin account."""
        # Only allow setup if no admin exists
        if not is_setup_required():
            return RedirectResponse("/login")

        # Get error message if any
        error = request.query_params.get("error")
        error_messages = {
            "missing": "All fields are required",
            "password_mismatch": "Passwords do not match",
            "password_weak": "Password must be at least 8 characters",
            "exists": "Admin account already exists",
        }
        error_msg = error_messages.get(error)

        # Render setup form
        return Html(
            Head(
                Title("Setup - Markdown CMS"),
                Meta(charset="utf-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1"),
                Link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
                ),
                Style(
                    """
                    body {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    .setup-card {
                        background: white;
                        border-radius: 15px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                        padding: 3rem;
                        width: 100%;
                        max-width: 450px;
                    }
                    .setup-card h1 {
                        color: #667eea;
                        margin-bottom: 0.5rem;
                        text-align: center;
                    }
                    .setup-card .subtitle {
                        color: #666;
                        text-align: center;
                        margin-bottom: 2rem;
                    }
                    .btn-setup {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border: none;
                        padding: 12px;
                        font-weight: 600;
                    }
                    .btn-setup:hover {
                        opacity: 0.9;
                    }
                    .error-message {
                        background: #fee;
                        border: 1px solid #fcc;
                        border-radius: 8px;
                        padding: 12px;
                        margin-bottom: 1rem;
                        color: #c33;
                    }
                    .info-box {
                        background: #e8f4fc;
                        border: 1px solid #b8daff;
                        border-radius: 8px;
                        padding: 12px;
                        margin-bottom: 1.5rem;
                        color: #004085;
                        font-size: 0.9rem;
                    }
                """
                ),
            ),
            Body(
                Div(cls="setup-card")(
                    H1("Welcome!"),
                    P("Create your admin account to get started.", cls="subtitle"),
                    Div(cls="info-box")(
                        "This is the first-time setup. The account you create will have full administrator access."
                    ),
                    Div(cls="error-message")(error_msg) if error_msg else None,
                    Form(
                        method="post",
                        action="/setup",
                    )(
                        Div(cls="mb-3")(
                            Label("Username", cls="form-label", for_="username"),
                            Input(
                                type="text",
                                cls="form-control",
                                id="username",
                                name="username",
                                required=True,
                                autofocus=True,
                                placeholder="Choose a username",
                            ),
                        ),
                        Div(cls="mb-3")(
                            Label("Email", cls="form-label", for_="email"),
                            Input(
                                type="email",
                                cls="form-control",
                                id="email",
                                name="email",
                                required=True,
                                placeholder="admin@example.com",
                            ),
                        ),
                        Div(cls="mb-3")(
                            Label(
                                "Full Name (optional)",
                                cls="form-label",
                                for_="full_name",
                            ),
                            Input(
                                type="text",
                                cls="form-control",
                                id="full_name",
                                name="full_name",
                                placeholder="Your name",
                            ),
                        ),
                        Div(cls="mb-3")(
                            Label("Password", cls="form-label", for_="password"),
                            Input(
                                type="password",
                                cls="form-control",
                                id="password",
                                name="password",
                                required=True,
                                placeholder="Minimum 8 characters",
                            ),
                        ),
                        Div(cls="mb-3")(
                            Label(
                                "Confirm Password",
                                cls="form-label",
                                for_="password_confirm",
                            ),
                            Input(
                                type="password",
                                cls="form-control",
                                id="password_confirm",
                                name="password_confirm",
                                required=True,
                                placeholder="Re-enter password",
                            ),
                        ),
                        Button(
                            "Create Admin Account",
                            type="submit",
                            cls="btn btn-primary btn-setup w-100",
                        ),
                    ),
                ),
            ),
        )

    @app.post("/setup")
    async def setup_submit(request):
        """Handle setup form submission."""
        print("[DEBUG] Setup form submitted")

        # Only allow setup if no admin exists
        if not is_setup_required():
            print("[DEBUG] Setup not required - admin exists")
            return RedirectResponse("/login?error=exists", status_code=303)

        # Parse form data
        form = await request.form()
        username = form.get("username", "").strip()
        email = form.get("email", "").strip()
        full_name = form.get("full_name", "").strip() or None
        password = form.get("password", "")
        password_confirm = form.get("password_confirm", "")

        print(f"[DEBUG] Creating admin: {username}, {email}")

        # Validate
        if not username or not email or not password:
            print("[DEBUG] Missing required fields")
            return RedirectResponse("/setup?error=missing", status_code=303)

        if password != password_confirm:
            print("[DEBUG] Password mismatch")
            return RedirectResponse("/setup?error=password_mismatch", status_code=303)

        if len(password) < 8:
            print("[DEBUG] Password too short")
            return RedirectResponse("/setup?error=password_weak", status_code=303)

        try:
            # Create admin user
            print("[DEBUG] Calling create_initial_admin...")
            admin = create_initial_admin(username, email, password, full_name)
            print(f"[DEBUG] Admin created with ID: {admin.id}")

            # Create session and log in
            ip_address = request.client.host if hasattr(request, "client") else None
            user_agent = request.headers.get("user-agent")
            session = create_session(admin.id, ip_address, user_agent)
            print(f"[DEBUG] Session created: {session.session_id}")

            # Set session cookie and redirect to admin
            response = RedirectResponse("/admin", status_code=303)
            response.set_cookie(
                key=SESSION_COOKIE_NAME,
                value=session.session_id,
                max_age=SESSION_COOKIE_MAX_AGE,
                httponly=True,
                samesite="lax",
            )

            print("[DEBUG] Redirecting to /admin")
            return response

        except ValueError as e:
            print(f"[DEBUG] ValueError: {e}")
            # Handle validation errors
            if "already exists" in str(e).lower():
                return RedirectResponse("/setup?error=exists", status_code=303)
            return RedirectResponse("/setup?error=missing", status_code=303)
        except Exception as e:
            print(f"[DEBUG] Unexpected error: {type(e).__name__}: {e}")
            import traceback

            traceback.print_exc()
            return RedirectResponse("/setup?error=missing", status_code=303)

    @app.post("/login")
    async def login_submit(request):
        """Handle login form submission."""
        # Parse form data
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if not username or not password:
            return RedirectResponse("/login?error=missing", status_code=303)

        # Authenticate user
        user = authenticate_user(username, password)

        if not user:
            return RedirectResponse("/login?error=invalid", status_code=303)

        # Create session
        ip_address = request.client.host if hasattr(request, "client") else None
        user_agent = request.headers.get("user-agent")
        session = create_session(user.id, ip_address, user_agent)

        # Set session cookie
        response = RedirectResponse("/admin", status_code=303)
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=session.session_id,
            max_age=SESSION_COOKIE_MAX_AGE,
            httponly=True,
            samesite="lax",
        )

        return response

    @app.get("/logout")
    def logout(request):
        """Logout route."""
        # Get session cookie
        session_id = request.cookies.get(SESSION_COOKIE_NAME)

        if session_id:
            # Invalidate session
            invalidate_session(session_id)

        # Clear cookie and redirect
        response = RedirectResponse("/login", status_code=303)
        response.delete_cookie(SESSION_COOKIE_NAME)

        return response

    @app.get("/admin")
    def admin_dashboard(request):
        """Admin dashboard - requires authentication."""
        # Check if setup is required first
        if is_setup_required():
            return RedirectResponse("/setup")

        user = get_current_user(request)

        if not user:
            return RedirectResponse("/login")

        # Render admin dashboard
        return Html(
            Head(
                Title("Admin Dashboard - Markdown CMS"),
                Meta(charset="utf-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1"),
                Link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
                ),
            ),
            Body(
                Nav(cls="navbar navbar-dark bg-primary")(
                    Div(cls="container-fluid")(
                        A("Markdown CMS", cls="navbar-brand", href="/admin"),
                        Div(cls="d-flex")(
                            Span(cls="text-white me-3")(
                                f"👤 {user.username} ({user.role.value})"
                            ),
                            A(
                                "Logout",
                                cls="btn btn-outline-light btn-sm",
                                href="/logout",
                            ),
                        ),
                    ),
                ),
                Div(cls="container mt-4")(
                    H1("Admin Dashboard"),
                    Div(cls="row mt-4")(
                        Div(cls="col-md-4")(
                            Div(cls="card")(
                                Div(cls="card-body")(
                                    H5("Content", cls="card-title"),
                                    P("Manage your content", cls="card-text"),
                                    A(
                                        "View Content",
                                        cls="btn btn-primary",
                                        href="/admin/content",
                                    ),
                                ),
                            ),
                        ),
                        Div(cls="col-md-4")(
                            Div(cls="card")(
                                Div(cls="card-body")(
                                    H5("Users", cls="card-title"),
                                    P("Manage users and permissions", cls="card-text"),
                                    A(
                                        "View Users",
                                        cls=(
                                            "btn btn-primary"
                                            if user.is_admin()
                                            else "btn btn-secondary disabled"
                                        ),
                                        href="/admin/users" if user.is_admin() else "#",
                                    ),
                                ),
                            ),
                        ),
                        Div(cls="col-md-4")(
                            Div(cls="card")(
                                Div(cls="card-body")(
                                    H5("Settings", cls="card-title"),
                                    P("Configure your CMS", cls="card-text"),
                                    A(
                                        "View Settings",
                                        cls=(
                                            "btn btn-primary"
                                            if user.is_admin()
                                            else "btn btn-secondary disabled"
                                        ),
                                        href=(
                                            "/admin/settings"
                                            if user.is_admin()
                                            else "#"
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                    Div(cls="mt-4")(
                        A("← Back to Site", cls="btn btn-outline-primary", href="/"),
                    ),
                ),
            ),
        )
