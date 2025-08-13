from app.rag_utils.rag_module import get_rag_chain
from app.config import ROLE_DOCS_MAPPING
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_query_for_role(question: str, role: str) -> bool:
    """
    Validate if a query is appropriate for the user's role.
    This adds an extra layer of security beyond document filtering.
    
    Args:
        question: The user's question
        role: The user's role
        
    Returns:
        True if query is valid for the role, False otherwise
    """
    # Convert role to match config format - handle special cases
    if role.lower() == "Admin":
        role_converted = "Admin"
    elif role.upper() in ["HR", "HR_USER"]:
        role_converted = "HR"
    elif role.upper() in ["FINANCE", "FINANCE_USER"]:
        role_converted = "Finance Officer"
    elif role.upper() in ["MARKETING", "MARKETING_USER"]:
        role_converted = "Market Analysis"
    elif role.upper() in ["ENGINEERING", "ENGINEERING_USER"]:
        role_converted = "Agriculture Expert"
    elif role.upper() in ["GENERAL", "GENERAL_USER"]:
        role_converted = "General"
    else:
        role_converted = role.title()
    
    # Get allowed document roles for this user
    allowed_roles = ROLE_DOCS_MAPPING.get(role_converted, [])
    
    # Define agriculture-related indicators
    agriculture_context_indicators = [
        "crop", "soil", "farming", "agriculture", "harvest", "irrigation", 
        "fertilizer", "pesticide", "field", "plant", "seed", "yield", "rice", "wheat",
        "corn", "vegetables", "fruits", "livestock", "poultry", "dairy", "organic",
        "pest control", "weed management", "soil fertility", "crop rotation"
    ]
    
    question_lower = question.lower()
    has_agriculture_context = any(indicator in question_lower for indicator in agriculture_context_indicators)
    
    # HR users should NOT be able to ask agricultural questions
    if role_converted == "HR" and has_agriculture_context:
        logger.warning(f"HR user attempted to access agricultural information: {question}")
        return False
    
    # For non-HR roles, allow agriculture-related questions (maintain existing behavior)
    if has_agriculture_context and role_converted != "HR":
        return True
    
    # Only block very specific non-agriculture queries that are clearly cross-role
    blocking_patterns = [
        "employee salary information",
        "personnel records",
        "financial statements",
        "investment portfolio",
        "marketing campaign budget",
        "engineering architecture"
    ]
    
    # Check if question contains blocking patterns
    for pattern in blocking_patterns:
        if pattern in question_lower:
            if role_converted not in ["Admin"]:
                logger.warning(f"User '{role_converted}' attempted to access restricted information: {question}")
                return False
    
    return True

async def ask_rag(question: str, role: str, cohere_api_key: str = None) -> dict:
    """
    Ask a question using RAG with role-based access control.
    
    Args:
        question: The user's question
        role: The user's role
        cohere_api_key: Optional Cohere API key for reranking
        
    Returns:
        Dictionary containing the answer
        
    Raises:
        ValueError: If the query is not appropriate for the user's role
    """
    # Validate query for role
    if not validate_query_for_role(question, role):
        return {
            "answer": f"Sorry, you don't have permission to access this type of information. As a {role} user, you can only access documents related to your role. Please contact your administrator if you need access to other information."
        }
    
    # Log the query for security auditing
    logger.info(f"RAG query from role '{role}': {question}")
    
    # Get RAG chain with role-based filtering
    chain = get_rag_chain(user_role=role, cohere_api_key=cohere_api_key)
    result = chain({"input": question})
    
    return {"answer": result["answer"]}