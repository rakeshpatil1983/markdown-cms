"""Form processing and validation framework."""

import secrets
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional


@dataclass
class ValidationRule:
    """Validation rule for form fields."""

    name: str
    error_message: str
    validator: Callable[[Any], bool]


@dataclass
class FormField:
    """Form field definition with validation rules."""

    name: str
    label: str
    field_type: str = "text"  # text, email, password, number, select, textarea, etc.
    required: bool = True
    validators: list[ValidationRule] = field(default_factory=list)
    default_value: Any = None
    placeholder: str = ""
    options: list[tuple[str, str]] = field(default_factory=list)  # For select fields

    def validate(self, value: Any) -> list[str]:
        """
        Validate field value against all rules.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Check required
        if self.required and (value is None or value == ""):
            errors.append(f"{self.label} is required")
            return errors

        # Skip other validations if not required and empty
        if not self.required and (value is None or value == ""):
            return errors

        # Run custom validators
        for rule in self.validators:
            if not rule.validator(value):
                errors.append(rule.error_message)

        return errors


@dataclass
class FormData:
    """Container for form submission data."""

    data: dict[str, Any]
    errors: dict[str, list[str]] = field(default_factory=dict)
    is_valid: bool = True
    csrf_token: Optional[str] = None

    def get(self, field: str, default: Any = None) -> Any:
        """Get field value."""
        return self.data.get(field, default)

    def has_errors(self) -> bool:
        """Check if form has any errors."""
        return len(self.errors) > 0


class Form:
    """Form handler with validation and CSRF protection."""

    def __init__(self, fields: list[FormField], csrf_enabled: bool = True):
        """
        Initialize form.

        Args:
            fields: List of form fields
            csrf_enabled: Enable CSRF protection
        """
        self.fields = {field.name: field for field in fields}
        self.csrf_enabled = csrf_enabled

    def validate(
        self, data: dict[str, Any], csrf_token: Optional[str] = None
    ) -> FormData:
        """
        Validate form data.

        Args:
            data: Form submission data
            csrf_token: CSRF token from form

        Returns:
            FormData object with validation results
        """
        form_data = FormData(data=data, csrf_token=csrf_token)

        # Validate CSRF token
        if self.csrf_enabled and csrf_token:
            if not verify_csrf_token(csrf_token):
                form_data.errors["_csrf"] = ["Invalid or expired CSRF token"]
                form_data.is_valid = False

        # Validate each field
        for field_name, field in self.fields.items():
            value = data.get(field_name)
            errors = field.validate(value)

            if errors:
                form_data.errors[field_name] = errors
                form_data.is_valid = False

        return form_data

    def render_field(
        self, field_name: str, value: Any = None, errors: list[str] = None
    ) -> str:
        """
        Render form field HTML.

        Args:
            field_name: Name of field to render
            value: Current field value
            errors: List of error messages

        Returns:
            HTML string
        """
        if field_name not in self.fields:
            return ""

        field = self.fields[field_name]
        errors = errors or []
        value = value if value is not None else field.default_value or ""

        # Build error HTML
        error_html = ""
        if errors:
            error_html = (
                '<div class="invalid-feedback d-block">'
                + "<br>".join(errors)
                + "</div>"
            )

        # Build field HTML based on type
        if field.field_type == "textarea":
            html = f"""
<div class="mb-3">
    <label for="{field.name}" class="form-label">{field.label}</label>
    <textarea class="form-control {'is-invalid' if errors else ''}"
              id="{field.name}"
              name="{field.name}"
              placeholder="{field.placeholder}"
              {'required' if field.required else ''}>{value}</textarea>
    {error_html}
</div>
"""
        elif field.field_type == "select":
            options_html = '<option value="">Select...</option>\n'
            for opt_value, opt_label in field.options:
                selected = "selected" if str(value) == str(opt_value) else ""
                options_html += (
                    f'<option value="{opt_value}" {selected}>{opt_label}</option>\n'
                )

            html = f"""
<div class="mb-3">
    <label for="{field.name}" class="form-label">{field.label}</label>
    <select class="form-select {'is-invalid' if errors else ''}"
            id="{field.name}"
            name="{field.name}"
            {'required' if field.required else ''}>
        {options_html}
    </select>
    {error_html}
</div>
"""
        else:  # text, email, password, number, etc.
            html = f"""
<div class="mb-3">
    <label for="{field.name}" class="form-label">{field.label}</label>
    <input type="{field.field_type}"
           class="form-control {'is-invalid' if errors else ''}"
           id="{field.name}"
           name="{field.name}"
           value="{value}"
           placeholder="{field.placeholder}"
           {'required' if field.required else ''}>
    {error_html}
</div>
"""

        return html

    def render(
        self, data: dict[str, Any] = None, errors: dict[str, list[str]] = None
    ) -> str:
        """
        Render entire form.

        Args:
            data: Current form data
            errors: Validation errors by field

        Returns:
            HTML string
        """
        data = data or {}
        errors = errors or {}

        html = ""
        for field_name in self.fields:
            html += self.render_field(
                field_name, value=data.get(field_name), errors=errors.get(field_name)
            )

        # Add CSRF token field
        if self.csrf_enabled:
            token = generate_csrf_token()
            html += f'<input type="hidden" name="csrf_token" value="{token}">\n'

        return html


# CSRF Token Management

_csrf_tokens: dict[str, datetime] = {}
CSRF_TOKEN_EXPIRY = timedelta(hours=1)


def generate_csrf_token() -> str:
    """
    Generate a new CSRF token.

    Returns:
        CSRF token string
    """
    token = secrets.token_urlsafe(32)
    _csrf_tokens[token] = datetime.utcnow()

    # Clean up expired tokens
    cleanup_expired_csrf_tokens()

    return token


def verify_csrf_token(token: str) -> bool:
    """
    Verify CSRF token is valid and not expired.

    Args:
        token: CSRF token to verify

    Returns:
        True if valid, False otherwise
    """
    if token not in _csrf_tokens:
        return False

    created_at = _csrf_tokens[token]

    # Check if expired
    if datetime.utcnow() - created_at > CSRF_TOKEN_EXPIRY:
        del _csrf_tokens[token]
        return False

    return True


def cleanup_expired_csrf_tokens():
    """Remove expired CSRF tokens from memory."""
    now = datetime.utcnow()
    expired = [
        token
        for token, created_at in _csrf_tokens.items()
        if now - created_at > CSRF_TOKEN_EXPIRY
    ]

    for token in expired:
        del _csrf_tokens[token]


# Common Validators


def email_validator(value: str) -> bool:
    """Validate email format."""
    import re

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, str(value)))


def min_length_validator(min_len: int) -> Callable[[str], bool]:
    """Create validator for minimum string length."""

    def validator(value: str) -> bool:
        return len(str(value)) >= min_len

    return validator


def max_length_validator(max_len: int) -> Callable[[str], bool]:
    """Create validator for maximum string length."""

    def validator(value: str) -> bool:
        return len(str(value)) <= max_len

    return validator


def min_value_validator(min_val: float) -> Callable[[Any], bool]:
    """Create validator for minimum numeric value."""

    def validator(value: Any) -> bool:
        try:
            return float(value) >= min_val
        except (ValueError, TypeError):
            return False

    return validator


def max_value_validator(max_val: float) -> Callable[[Any], bool]:
    """Create validator for maximum numeric value."""

    def validator(value: Any) -> bool:
        try:
            return float(value) <= max_val
        except (ValueError, TypeError):
            return False

    return validator


def pattern_validator(pattern: str) -> Callable[[str], bool]:
    """Create validator for regex pattern matching."""
    import re

    compiled = re.compile(pattern)

    def validator(value: str) -> bool:
        return bool(compiled.match(str(value)))

    return validator


def in_choices_validator(choices: list[str]) -> Callable[[str], bool]:
    """Create validator to check if value is in allowed choices."""

    def validator(value: str) -> bool:
        return str(value) in choices

    return validator


# Flash Message System

_flash_messages: list[tuple[str, str]] = []  # (type, message)


def flash(message: str, category: str = "info"):
    """
    Add a flash message.

    Args:
        message: Message text
        category: Message type (success, info, warning, danger)
    """
    _flash_messages.append((category, message))


def get_flashed_messages() -> list[tuple[str, str]]:
    """
    Get and clear all flash messages.

    Returns:
        List of (category, message) tuples
    """
    global _flash_messages
    messages = _flash_messages.copy()
    _flash_messages.clear()
    return messages


def render_flash_messages() -> str:
    """
    Render flash messages as Bootstrap alerts.

    Returns:
        HTML string
    """
    messages = get_flashed_messages()

    if not messages:
        return ""

    html = '<div class="flash-messages">\n'
    for category, message in messages:
        html += f'<div class="alert alert-{category} alert-dismissible fade show" role="alert">\n'
        html += f"  {message}\n"
        html += '  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>\n'
        html += "</div>\n"
    html += "</div>\n"

    return html
