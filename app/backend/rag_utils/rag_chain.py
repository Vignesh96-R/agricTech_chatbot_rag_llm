from app.backend.rag_utils.rag_module import get_rag_chain
from app.config import ROLE_DOCS_MAPPING
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Role-specific blocking patterns - each role can only access their domain
def validate_query_for_role(question: str, role: str) -> bool:
    ROLE_BLOCKING_PATTERNS = {
        "Admin": [],  # Admin can access everything
        "Agriculture Expert": [
            "employee salary", "personnel records", "hr policies", "financial statements",
            "investment portfolio", "budget allocation", "sales commission", "market pricing",
            "supply chain costs", "crop insurance claims", "farmer payment details",
            "field worker wages", "expert consultation fees", "hr hiring", "payroll",
            "performance review", "market analysis", "supply chain logistics"
        ],
        "Farmer": [
            "employee salary", "personnel records", "hr policies", "financial statements",
            "investment portfolio", "budget allocation", "sales commission", "market pricing",
            "supply chain costs", "crop insurance claims", "field worker wages",
            "expert consultation fees", "hr hiring", "payroll", "performance review",
            "market analysis", "supply chain logistics", "hr recruitment"
        ],
        "Field Worker": [
            "employee salary", "personnel records", "hr policies", "financial statements",
            "investment portfolio", "budget allocation", "sales commission", "market pricing",
            "supply chain costs", "crop insurance claims", "farmer payment details",
            "expert consultation fees", "hr hiring", "payroll", "performance review",
            "market analysis", "supply chain logistics", "hr recruitment"
        ],
        "Finance Officer": [
            "employee salary", "personnel records", "hr policies", "hr hiring",
            "hr recruitment", "performance review", "sales commission", "market pricing",
            "crop insurance claims", "farmer payment details", "field worker wages",
            "expert consultation fees", "agriculture techniques", "crop management",
            "soil fertility", "pest control", "irrigation methods", "harvest techniques"
        ],
        "HR": [
            "financial statements", "investment portfolio", "budget allocation",
            "sales commission", "market pricing", "supply chain costs", "crop insurance",
            "agriculture techniques", "crop management", "soil fertility", "pest control",
            "irrigation methods", "harvest techniques", "crop rotation", "fertilizer",
            "pesticide management", "livestock care", "dairy management"
        ],
        "Market Analysis": [
            "employee salary", "personnel records", "hr policies", "hr hiring",
            "hr recruitment", "payroll", "performance review", "sales commission",
            "crop insurance claims", "farmer payment details", "field worker wages",
            "expert consultation fees", "agriculture techniques", "crop management",
            "soil fertility", "pest control", "irrigation methods", "harvest techniques"
        ],
        "Sales Person": [
            "employee salary", "personnel records", "hr policies", "hr hiring",
            "hr recruitment", "payroll", "performance review", "financial statements",
            "investment portfolio", "budget allocation", "crop insurance claims",
            "farmer payment details", "field worker wages", "expert consultation fees",
            "agriculture techniques", "crop management", "soil fertility", "pest control",
            "irrigation methods", "harvest techniques", "crop rotation"
        ],
        "Supply Chain Manager": [
            "employee salary", "personnel records", "hr policies", "hr hiring",
            "hr recruitment", "payroll", "performance review", "sales commission",
            "market pricing", "crop insurance claims", "farmer payment details",
            "field worker wages", "expert consultation fees", "agriculture techniques",
            "crop management", "soil fertility", "pest control", "irrigation methods",
            "harvest techniques", "crop rotation", "fertilizer management"
        ]
    }

    question_lower = question.lower()
    
    # Get blocking patterns for the user's role
    blocking_patterns = ROLE_BLOCKING_PATTERNS.get(role, [])
    
    # Check if question contains any blocking patterns for this role
    for pattern in blocking_patterns:
        if pattern in question_lower:
            logger.warning(f"User '{role}' attempted to access restricted information: {question}")
            return False
    
    return True

async def ask_rag(question: str, role: str, cohere_api_key: str = None) -> dict:
    # Validate query for role
    if not validate_query_for_role(question, role):
        return {
            "answer": f"Sorry, you don't have permission to access this type of information. As a {role} user, you can only access documents related to your role. Please contact your administrator if you need access to other information."
        }
    
    # Log the query for security auditing
    logger.info(f"RAG query from role '{role}': {question}")
    
    # Get RAG chain with role-based filtering
    try:
        chain = get_rag_chain(user_role=role, cohere_api_key=cohere_api_key)
        result = chain({"input": question})
        return {"answer": result.get("answer", "No answer generated.")}
    except Exception as e:
        logger.error(f"RAG pipeline failed: {e}")
        return {"answer": "Sorry, the AI service is temporarily unavailable. Please try again in a moment."}