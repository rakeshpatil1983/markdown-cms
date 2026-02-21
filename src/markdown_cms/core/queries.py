"""
Data source query functions.

These functions are registered as data sources and can be used in :::table components.
Each function should return a list of dictionaries with consistent keys.
"""

from typing import Any

from .database import get_db_context
from .models import Content, ContentStatus, Session, User


def get_all_users(**kwargs) -> list[dict[str, Any]]:
    """
    Get all users.

    Returns:
        List of user dictionaries
    """
    with get_db_context() as db:
        users = db.query(User).all()

        return [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name or "",
                "role": user.role.value,
                "is_active": "Yes" if user.is_active else "No",
                "created_at": user.created_at.strftime("%Y-%m-%d %H:%M"),
                "last_login": (
                    user.last_login.strftime("%Y-%m-%d %H:%M")
                    if user.last_login
                    else "Never"
                ),
            }
            for user in users
        ]


def get_active_users(**kwargs) -> list[dict[str, Any]]:
    """
    Get active users only.

    Returns:
        List of active user dictionaries
    """
    with get_db_context() as db:
        users = db.query(User).filter_by(is_active=True).all()

        return [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name or "",
                "role": user.role.value,
                "created_at": user.created_at.strftime("%Y-%m-%d"),
                "last_login": (
                    user.last_login.strftime("%Y-%m-%d") if user.last_login else "Never"
                ),
            }
            for user in users
        ]


def get_published_content(**kwargs) -> list[dict[str, Any]]:
    """
    Get all published content.

    Returns:
        List of published content dictionaries
    """
    with get_db_context() as db:
        content_items = (
            db.query(Content).filter_by(status=ContentStatus.PUBLISHED).all()
        )

        return [
            {
                "id": item.id,
                "title": item.title,
                "slug": item.slug,
                "author": item.author.username if item.author else "Unknown",
                "published_at": (
                    item.published_at.strftime("%Y-%m-%d") if item.published_at else ""
                ),
                "updated_at": item.updated_at.strftime("%Y-%m-%d %H:%M"),
            }
            for item in content_items
        ]


def get_all_content(**kwargs) -> list[dict[str, Any]]:
    """
    Get all content (published, draft, archived).

    Returns:
        List of content dictionaries
    """
    with get_db_context() as db:
        content_items = db.query(Content).all()

        return [
            {
                "id": item.id,
                "title": item.title,
                "slug": item.slug,
                "status": item.status.value,
                "author": item.author.username if item.author else "Unknown",
                "created_at": item.created_at.strftime("%Y-%m-%d"),
                "updated_at": item.updated_at.strftime("%Y-%m-%d"),
            }
            for item in content_items
        ]


def get_draft_content(**kwargs) -> list[dict[str, Any]]:
    """
    Get draft content only.

    Returns:
        List of draft content dictionaries
    """
    with get_db_context() as db:
        content_items = db.query(Content).filter_by(status=ContentStatus.DRAFT).all()

        return [
            {
                "id": item.id,
                "title": item.title,
                "slug": item.slug,
                "author": item.author.username if item.author else "Unknown",
                "created_at": item.created_at.strftime("%Y-%m-%d"),
                "updated_at": item.updated_at.strftime("%Y-%m-%d %H:%M"),
            }
            for item in content_items
        ]


def get_active_sessions(**kwargs) -> list[dict[str, Any]]:
    """
    Get active sessions.

    Returns:
        List of active session dictionaries
    """
    with get_db_context() as db:
        sessions = db.query(Session).filter_by(is_active=True).all()

        return [
            {
                "id": session.id,
                "user": session.user.username if session.user else "Unknown",
                "ip_address": session.ip_address or "Unknown",
                "created_at": session.created_at.strftime("%Y-%m-%d %H:%M"),
                "last_activity": session.last_activity.strftime("%Y-%m-%d %H:%M"),
                "expires_at": session.expires_at.strftime("%Y-%m-%d %H:%M"),
            }
            for session in sessions
        ]


def get_user_count(**kwargs) -> list[dict[str, Any]]:
    """
    Get user statistics.

    Returns:
        List with single dictionary containing user counts
    """
    with get_db_context() as db:
        total = db.query(User).count()
        active = db.query(User).filter_by(is_active=True).count()
        admins = db.query(User).filter_by(role="admin").count()
        editors = db.query(User).filter_by(role="editor").count()
        viewers = db.query(User).filter_by(role="viewer").count()

        return [
            {
                "metric": "Total Users",
                "value": total,
            },
            {
                "metric": "Active Users",
                "value": active,
            },
            {
                "metric": "Administrators",
                "value": admins,
            },
            {
                "metric": "Editors",
                "value": editors,
            },
            {
                "metric": "Viewers",
                "value": viewers,
            },
        ]


def get_content_count(**kwargs) -> list[dict[str, Any]]:
    """
    Get content statistics.

    Returns:
        List with dictionary containing content counts
    """
    with get_db_context() as db:
        total = db.query(Content).count()
        published = db.query(Content).filter_by(status=ContentStatus.PUBLISHED).count()
        draft = db.query(Content).filter_by(status=ContentStatus.DRAFT).count()
        archived = db.query(Content).filter_by(status=ContentStatus.ARCHIVED).count()

        return [
            {
                "metric": "Total Content",
                "value": total,
            },
            {
                "metric": "Published",
                "value": published,
            },
            {
                "metric": "Drafts",
                "value": draft,
            },
            {
                "metric": "Archived",
                "value": archived,
            },
        ]
