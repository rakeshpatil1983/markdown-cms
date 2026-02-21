"""Authentication and authorization utilities."""

import hashlib
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from .database import get_db_context
from .models import Session, User, UserRole

# JWT settings - load from environment with secure fallback
SECRET_KEY = os.getenv("SECRET_KEY", os.getenv("JWT_SECRET", secrets.token_hex(32)))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SESSION_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    """
    Hash a password using SHA256 with salt.

    Format: salt$hash
    """
    salt = secrets.token_hex(32)
    password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${password_hash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        salt, expected_hash = hashed_password.split("$")
        password_hash = hashlib.sha256((salt + plain_password).encode()).hexdigest()
        return password_hash == expected_hash
    except ValueError:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_session_id() -> str:
    """Generate a secure random session ID."""
    return secrets.token_urlsafe(32)


def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticate a user by username and password.

    Returns:
        User object if authentication successful, None otherwise.
    """
    with get_db_context() as db:
        user = db.query(User).filter_by(username=username).first()

        if not user:
            return None

        if not user.is_active:
            return None

        if not verify_password(password, user.password_hash):
            return None

        # Update last login time
        user.last_login = datetime.utcnow()
        db.commit()

        # Refresh the user object to get updated values
        db.refresh(user)

        # Important: Make user object available outside session
        db.expunge(user)

        return user


def create_session(
    user_id: int,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    expires_in_days: int = SESSION_EXPIRE_DAYS,
) -> Session:
    """
    Create a new session for a user.

    Args:
        user_id: User ID
        ip_address: Client IP address
        user_agent: Client user agent
        expires_in_days: Session expiration in days

    Returns:
        Session object
    """
    with get_db_context() as db:
        session_id = generate_session_id()
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        session = Session(
            session_id=session_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            is_active=True,
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        # Make session available outside db context
        db.expunge(session)

        return session


def get_session_by_id(session_id: str) -> Optional[Session]:
    """
    Get a session by session ID.

    Returns:
        Session object if found and valid, None otherwise.
    """
    with get_db_context() as db:
        session = db.query(Session).filter_by(session_id=session_id).first()

        if not session:
            return None

        if session.is_expired():
            return None

        # Update last activity
        session.last_activity = datetime.utcnow()
        db.commit()
        db.refresh(session)

        # Make session available outside db context
        db.expunge(session)

        return session


def get_user_by_session(session_id: str) -> Optional[User]:
    """
    Get user associated with a session.

    Returns:
        User object if session valid, None otherwise.
    """
    with get_db_context() as db:
        session = db.query(Session).filter_by(session_id=session_id).first()

        if not session:
            return None

        if session.is_expired():
            return None

        # Update last activity
        session.last_activity = datetime.utcnow()
        db.commit()

        # Get user
        user = session.user

        if not user or not user.is_active:
            return None

        # Make objects available outside db context
        db.expunge(user)

        return user


def invalidate_session(session_id: str) -> bool:
    """
    Invalidate a session (logout).

    Returns:
        True if session invalidated, False if not found.
    """
    with get_db_context() as db:
        session = db.query(Session).filter_by(session_id=session_id).first()

        if not session:
            return False

        session.is_active = False
        db.commit()

        return True


def invalidate_all_user_sessions(user_id: int) -> int:
    """
    Invalidate all sessions for a user.

    Returns:
        Number of sessions invalidated.
    """
    with get_db_context() as db:
        sessions = db.query(Session).filter_by(user_id=user_id, is_active=True).all()

        count = 0
        for session in sessions:
            session.is_active = False
            count += 1

        db.commit()

        return count


def cleanup_expired_sessions() -> int:
    """
    Clean up expired sessions from database.

    Returns:
        Number of sessions deleted.
    """
    with get_db_context() as db:
        now = datetime.utcnow()
        expired = db.query(Session).filter(Session.expires_at < now).all()

        count = len(expired)
        for session in expired:
            db.delete(session)

        db.commit()

        return count


def create_user(
    username: str,
    email: str,
    password: str,
    full_name: Optional[str] = None,
    role: UserRole = UserRole.VIEWER,
) -> User:
    """
    Create a new user.

    Args:
        username: Username (must be unique)
        email: Email address (must be unique)
        password: Plain text password (will be hashed)
        full_name: Full name (optional)
        role: User role (default: VIEWER)

    Returns:
        Created User object
    """
    with get_db_context() as db:
        # Check if username or email already exists
        existing = (
            db.query(User)
            .filter((User.username == username) | (User.email == email))
            .first()
        )

        if existing:
            if existing.username == username:
                raise ValueError(f"Username '{username}' already exists")
            if existing.email == email:
                raise ValueError(f"Email '{email}' already exists")

        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role=role,
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # Make user available outside db context
        db.expunge(user)

        return user


def update_user_password(user_id: int, new_password: str) -> bool:
    """
    Update user password.

    Args:
        user_id: User ID
        new_password: New plain text password (will be hashed)

    Returns:
        True if password updated, False if user not found
    """
    with get_db_context() as db:
        user = db.query(User).filter_by(id=user_id).first()

        if not user:
            return False

        user.password_hash = hash_password(new_password)
        db.commit()

        return True


def check_permission(user: User, permission: str) -> bool:
    """
    Check if user has a specific permission.

    Args:
        user: User object
        permission: Permission name (e.g., 'read', 'write', 'delete')

    Returns:
        True if user has permission, False otherwise
    """
    if not user or not user.is_active:
        return False

    return user.has_permission(permission)


def require_role(user: Optional[User], required_roles: list[UserRole]) -> bool:
    """
    Check if user has one of the required roles.

    Args:
        user: User object
        required_roles: List of required roles

    Returns:
        True if user has one of the roles, False otherwise
    """
    if not user or not user.is_active:
        return False

    return user.role in required_roles


def is_setup_required() -> bool:
    """
    Check if initial setup is required (no admin user exists).

    Returns:
        True if setup is required, False otherwise.
    """
    try:
        with get_db_context() as db:
            admin_exists = (
                db.query(User).filter_by(role=UserRole.ADMIN, is_active=True).first()
            )
            return admin_exists is None
    except Exception:
        # Database might not exist yet, setup is definitely required
        return True


def create_initial_admin(
    username: str, email: str, password: str, full_name: Optional[str] = None
) -> User:
    """
    Create the initial admin user during setup.

    Args:
        username: Admin username
        email: Admin email
        password: Admin password
        full_name: Admin full name (optional)

    Returns:
        Created admin User object

    Raises:
        ValueError: If admin already exists or validation fails
    """
    with get_db_context() as db:
        # Check if any admin already exists
        existing_admin = db.query(User).filter_by(role=UserRole.ADMIN).first()
        if existing_admin:
            raise ValueError("Admin user already exists. Setup can only be done once.")

        # Validate password strength
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Create admin user
        admin = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role=UserRole.ADMIN,
            is_active=True,
            must_change_password=False,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)
        db.expunge(admin)

        return admin
