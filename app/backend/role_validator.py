"""
Role-based access validation module.
"""

from fastapi import HTTPException
from app.backend.constants import (
    FINANCE_BLOCKING_PATTERNS,
    MARKET_BLOCKING_PATTERNS,
    HR_BLOCKING_PATTERNS,
    SUPPLY_CHAIN_BLOCKING_PATTERNS,
    AGRICULTURE_CONTEXT_INDICATORS,
)


def validate_role_access(question: str, role: str, username: str, db_manager) -> None:
    """
    Validate role-based access control for user queries.
    """
    from app.config import ROLE_DOCS_MAPPING
    
    # Check if user's role has access to the type of information they're asking for
    allowed_roles = ROLE_DOCS_MAPPING.get(role, [])
    
    # Only block access if the question is clearly trying to access information
    # that is completely outside the user's role domain
    question_lower = question.lower()
    
    # Define clear cross-role access patterns that should be blocked
    # These are more specific patterns that indicate intentional cross-role access attempts
    
    # Finance-specific queries (blocked for non-finance roles unless they're agriculture-related)
    has_agriculture_context = any(indicator in question_lower for indicator in AGRICULTURE_CONTEXT_INDICATORS)
    
    # HR users should NOT be able to ask agricultural questions
    if role == "HR" and has_agriculture_context:
        db_manager.log_query(username, role, "BLOCKED", question, False, "HR agricultural access denied")
        raise HTTPException(
            status_code=403, 
            detail="Sorry, you don't have permission to access agricultural information. As an HR user, you can only access HR-related documents. If you need farming advice, please contact an agriculture expert or farmer."
        )
    
    # Only block if there's a clear cross-role access attempt without agriculture context
    if not has_agriculture_context:
        _check_finance_access(question_lower, role, username, question, db_manager)
        _check_market_analysis_access(question_lower, role, username, question, db_manager)
        _check_hr_access(question_lower, role, username, question, db_manager)
        _check_supply_chain_access(question_lower, role, username, question, db_manager)


def _check_finance_access(question_lower: str, role: str, username: str, question: str, db_manager) -> None:
    """Check if user is trying to access finance-related information without permission."""
    if role not in ["Finance Officer", "Admin"]:
        if any(pattern in question_lower for pattern in FINANCE_BLOCKING_PATTERNS):
            db_manager.log_query(username, role, "BLOCKED", question, False, "Finance access denied")
            raise HTTPException(
                status_code=403, 
                detail="Sorry, you don't have permission to access financial information. This type of data is restricted to finance officers only. Please contact the finance department if you need this information."
            )


def _check_market_analysis_access(question_lower: str, role: str, username: str, question: str, db_manager) -> None:
    """Check if user is trying to access market analysis information without permission."""
    if role not in ["Market Analysis", "Admin"]:
        if any(pattern in question_lower for pattern in MARKET_BLOCKING_PATTERNS):
            db_manager.log_query(username, role, "BLOCKED", question, False, "Market analysis access denied")
            raise HTTPException(
                status_code=403, 
                detail="Sorry, you don't have permission to access market analysis information. This data is restricted to market analysts only. Please contact the marketing department if you need this information."
            )


def _check_hr_access(question_lower: str, role: str, username: str, question: str, db_manager) -> None:
    """Check if user is trying to access HR information without permission."""
    if role not in ["HR", "Admin"]:
        if any(pattern in question_lower for pattern in HR_BLOCKING_PATTERNS):
            db_manager.log_query(username, role, "BLOCKED", question, False, "HR access denied")
            raise HTTPException(
                status_code=403, 
                detail="Sorry, you don't have permission to access HR information. This data is restricted to HR personnel only. Please contact the HR department if you need this information."
            )


def _check_supply_chain_access(question_lower: str, role: str, username: str, question: str, db_manager) -> None:
    """Check if user is trying to access supply chain information without permission."""
    if role not in ["Supply Chain Manager", "Admin"]:
        if any(pattern in question_lower for pattern in SUPPLY_CHAIN_BLOCKING_PATTERNS):
            db_manager.log_query(username, role, "BLOCKED", question, False, "Supply chain access denied")
            raise HTTPException(
                status_code=403, 
                detail="Sorry, you don't have permission to access supply chain information. This data is restricted to supply chain managers only. Please contact the supply chain department if you need this information."
            )


def is_agriculture_context(question: str) -> bool:
    """
    Check if a question has agriculture-related context.
    """
    question_lower = question.lower()
    return any(indicator in question_lower for indicator in AGRICULTURE_CONTEXT_INDICATORS)


def get_allowed_roles_for_user(role: str) -> list:
    """
    Get the list of roles that a user can access.
    """
    from app.config import ROLE_DOCS_MAPPING
    return ROLE_DOCS_MAPPING.get(role, [])
