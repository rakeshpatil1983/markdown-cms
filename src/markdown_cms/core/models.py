"""Database models for Markdown CMS."""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class UserRole(enum.Enum):
    """User role enumeration."""

    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(
        String(80), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(120))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.VIEWER, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)
    must_change_password: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Relationships
    sessions: Mapped[list["Session"]] = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )
    content_items: Mapped[list["Content"]] = relationship(
        "Content", back_populates="author", foreign_keys="Content.author_id"
    )

    def __repr__(self):
        return f"<User {self.username} ({self.role.value})>"

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        permissions_map = {
            UserRole.ADMIN: [
                "read",
                "write",
                "delete",
                "manage_users",
                "manage_settings",
            ],
            UserRole.EDITOR: ["read", "write"],
            UserRole.VIEWER: ["read"],
        }
        return permission in permissions_map.get(self.role, [])

    def can_edit(self) -> bool:
        """Check if user can edit content."""
        return self.role in [UserRole.ADMIN, UserRole.EDITOR]

    def can_delete(self) -> bool:
        """Check if user can delete content."""
        return self.role == UserRole.ADMIN

    def is_admin(self) -> bool:
        """Check if user is an administrator."""
        return self.role == UserRole.ADMIN


class Session(Base):
    """Session model for user authentication sessions."""

    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_activity: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<Session {self.session_id[:8]}... for user {self.user_id}>"

    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() > self.expires_at or not self.is_active


class ContentStatus(enum.Enum):
    """Content status enumeration."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Content(Base):
    """Content model for storing markdown content in database."""

    __tablename__ = "content"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    markdown_content: Mapped[str] = mapped_column(Text, nullable=False)
    html_content: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[ContentStatus] = mapped_column(
        Enum(ContentStatus), default=ContentStatus.DRAFT, nullable=False
    )
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    layout: Mapped[str] = mapped_column(String(50), default="default", nullable=False)
    meta_title: Mapped[Optional[str]] = mapped_column(String(255))
    meta_description: Mapped[Optional[str]] = mapped_column(String(500))
    meta_keywords: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    author: Mapped["User"] = relationship(
        "User", back_populates="content_items", foreign_keys=[author_id]
    )

    def __repr__(self):
        return f"<Content {self.slug} ({self.status.value})>"

    def is_published(self) -> bool:
        """Check if content is published."""
        return self.status == ContentStatus.PUBLISHED

    def publish(self):
        """Publish the content."""
        self.status = ContentStatus.PUBLISHED
        self.published_at = datetime.utcnow()

    def unpublish(self):
        """Unpublish the content."""
        self.status = ContentStatus.DRAFT
        self.published_at = None


class DataSource(Base):
    """Data source model for registering Python functions as data sources."""

    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    description: Mapped[Optional[str]] = mapped_column(String(255))
    function_path: Mapped[str] = mapped_column(
        String(255), nullable=False
    )  # e.g., "apps.users.queries.get_all_users"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    requires_auth: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    allowed_roles: Mapped[Optional[str]] = mapped_column(
        String(255)
    )  # Comma-separated roles
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self):
        return f"<DataSource {self.name}>"

    def get_allowed_roles(self) -> list[str]:
        """Get list of allowed roles."""
        if not self.allowed_roles:
            return []
        return [role.strip() for role in self.allowed_roles.split(",")]
