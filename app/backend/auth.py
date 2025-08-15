"""
Authentication and authorization module for the RBAC-Project application.

This module handles user authentication, role-based access control,
and security-related functionality.
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.hash import bcrypt
from typing import Dict, Optional
import secrets

from app.config import STATIC_USERS, ROLE_DOCS_MAPPING
from app.backend.models import UserInfo

# Security scheme
security = HTTPBasic()

def get_user_info(username: str) -> Optional[UserInfo]:
    """
    Get user information from static users configuration.
    
    Args:
        username: The username to look up
        
    Returns:
        UserInfo object if user exists, None otherwise
    """
    if username in STATIC_USERS:
        user_data = STATIC_USERS[username]
        return UserInfo(
            username=username,
            role=user_data["role"],
            password_hash=user_data["password"]
        )
    return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hash.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to check against
        
    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.verify(plain_password, hashed_password)

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)) -> UserInfo:
    """
    Authenticate a user based on HTTP Basic Auth credentials.
    
    Args:
        credentials: HTTP Basic Auth credentials
        
    Returns:
        UserInfo object for authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    username = credentials.username
    password = credentials.password
    
    # Get user info
    user_info = get_user_info(username)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Verify password
    if not verify_password(password, user_info.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return user_info

def require_role(required_role: str):
    """
    Dependency to require a specific role for access.
    
    Args:
        required_role: The role required for access
        
    Returns:
        Dependency function that checks role access
    """
    def role_checker(user: UserInfo = Depends(authenticate_user)) -> UserInfo:
        if user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        return user
    return role_checker

def require_c_level_access():
    """
    Dependency to require Admin access.
    
    Returns:
        Dependency function that checks Admin access
    """
    return require_role("Admin")

def get_user_role_dependencies(user: UserInfo = Depends(authenticate_user)) -> Dict[str, list]:
    """
    Get the document access dependencies for a user's role.
    
    Args:
        user: The authenticated user
        
    Returns:
        Dictionary containing user role and allowed document roles
    """
    user_role = user.role
    allowed_roles = ROLE_DOCS_MAPPING.get(user_role, [])
    
    return {
        "user_role": user_role,
        "allowed_roles": allowed_roles
    }

def can_access_document(user_role: str, document_role: str) -> bool:
    """
    Check if a user can access a document based on role hierarchy.
    
    Args:
        user_role: The user's role
        document_role: The document's assigned role
        
    Returns:
        True if access is allowed, False otherwise
    """
    allowed_roles = ROLE_DOCS_MAPPING.get(user_role, [])
    return document_role in allowed_roles

def hash_password(plain_password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    Args:
        plain_password: The plain text password to hash
        
    Returns:
        The hashed password
    """
    return bcrypt.hash(plain_password)

def create_user(username: str, password: str, role: str) -> UserInfo:
    """
    Create a new user (for admin purposes).
    
    Args:
        username: The username for the new user
        password: The plain text password
        role: The role for the new user
        
    Returns:
        UserInfo object for the new user
        
    Raises:
        ValueError: If username already exists or role is invalid
    """
    if username in STATIC_USERS:
        raise ValueError(f"Username '{username}' already exists")
    
    if role not in ROLE_DOCS_MAPPING:
        raise ValueError(f"Invalid role: {role}")
    
    hashed_password = hash_password(password)
    
    # In a real application, this would be stored in a database
    # For now, we'll just return the user info
    return UserInfo(
        username=username,
        role=role,
        password_hash=hashed_password
    )
