import pandas as pd
from pathlib import Path
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_core.documents import Document

from app.config import (
    AVAILABLE_ROLES, ROLE_DOCS_MAPPING, ALLOWED_EXTENSIONS, 
    MAX_FILE_SIZE, UPLOADS_DIR, RESOURCES_DIR
)
from app.models import ChatRequest, ChatResponse, UploadResponse, AvailableDocsResponse, LoginResponse, HealthCheck
from app.auth import authenticate_user, require_c_level_access, get_user_role_dependencies
from app.database import get_db_manager
from app.rag_utils.rag_module import run_indexer, vectorstore, get_rag_chain
from app.rag_utils.query_classifier import detect_query_type_llm
from app.rag_utils.csv_query import ask_csv
from app.rag_utils.rag_chain import ask_rag

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agriculture RBAC-Project API",
    description="Role-Based Access Control System with RAG and SQL Querying for Agriculture Domain",
    version="1.0.0"
)

# -------------------------
# === ROUTES ===
# -------------------------
@app.get("/login", response_model=LoginResponse)
def login(user=Depends(authenticate_user)):
    return {
        "message": f"Welcome {user.username}!",
        "role": user.role,
        "username": user.username
    }

@app.get("/roles")
def get_roles(user=Depends(authenticate_user)):
    return {"roles": AVAILABLE_ROLES}

@app.get("/available-docs", response_model=AvailableDocsResponse)
def get_available_docs(role_info=Depends(get_user_role_dependencies)):
    """Get available documents for the user's role"""
    user_role = role_info["user_role"]
    allowed_roles = role_info["allowed_roles"]
    
    docs = []
    
    for role in allowed_roles:
        # Map role names to folder names in resources_2
        role_folder_mapping = {
            "Agriculture Expert": "agriculture expert",
            "Farmer": "farmer",
            "Field Worker": "field worker", 
            "Finance Officer": "finance officer",
            "HR": "hr",
            "Market Analysis": "market analysis",
            "Sales Person": "salesperson",
            "Supply Chain Manager": "supply chain manager"
        }
        
        folder_name = role_folder_mapping.get(role, role.lower())
        
        # Reverse mapping for uploads directory (original role names with spaces)
        uploads_role_mapping = {
            "Agriculture Expert": "Agriculture Expert",
            "Farmer": "Farmer",
            "Field Worker": "Field Worker", 
            "Finance Officer": "Finance Officer",
            "HR": "HR",
            "Market Analysis": "Market Analysis",
            "Sales Person": "Sales Person",
            "Supply Chain Manager": "Supply Chain Manager"
        }
        
        uploads_folder_name = uploads_role_mapping.get(role, role)
        
        # Process documents from resources_2 directory
        role_path = RESOURCES_DIR / folder_name
        if role_path.exists():
            for file_path in role_path.iterdir():
                if file_path.is_file():
                    try:
                        file_size = file_path.stat().st_size if file_path.exists() else None
                    except (OSError, AttributeError):
                        file_size = None
                    
                    docs.append({
                        "filename": file_path.name,
                        "role": role,
                        "filepath": str(file_path),
                        "file_type": file_path.suffix.lower(),
                        "size": file_size,
                        "uploaded_at": None,
                        "source": "resources_2"
                    })
        
        # Process uploaded documents from static/uploads directory
        uploads_role_path = UPLOADS_DIR / uploads_folder_name
        if uploads_role_path.exists():
            for file_path in uploads_role_path.iterdir():
                if file_path.is_file():
                    # Get file creation time for uploaded_at
                    try:
                        stat = file_path.stat()
                        uploaded_at = stat.st_ctime if hasattr(stat, 'st_ctime') else None
                        file_size = stat.st_size if file_path.exists() else None
                        # Convert timestamp to string if it exists
                        if uploaded_at is not None:
                            from datetime import datetime
                            uploaded_at = datetime.fromtimestamp(uploaded_at).isoformat()
                    except (OSError, AttributeError):
                        uploaded_at = None
                        file_size = None
                    
                    docs.append({
                        "filename": file_path.name,
                        "role": role,
                        "filepath": str(file_path),
                        "file_type": file_path.suffix.lower(),
                        "size": file_size,
                        "uploaded_at": uploaded_at,
                        "source": "uploads"
                    })
    
    return {
        "documents": docs,
        "user_role": user_role,
        "allowed_roles": allowed_roles
    }

@app.post("/upload-docs", response_model=UploadResponse)
async def upload_docs(
    file: UploadFile = File(...), 
    role: str = Form(...), 
    user=Depends(require_c_level_access)
):
    """Upload documents (Admin only)"""
    try:
        filename = file.filename
        extension = Path(filename).suffix.lower()
        
        # Validate file type
        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Validate file size
        if file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
            )

        # Prepare storage
        role_dir = UPLOADS_DIR / role
        role_dir.mkdir(parents=True, exist_ok=True)
        filepath = role_dir / filename

        # Read content and save file
        data = await file.read()
        
        with open(filepath, "wb") as f:
            f.write(data)

        # Handle CSV files - create database table
        if extension == ".csv":
            try:
                df = pd.read_csv(filepath)
                table_name = Path(filename).stem.replace("-", "_")
                
                # Create table in database
                db_manager = get_db_manager()
                success = db_manager.create_table_from_dataframe(table_name, df, role)
                
                if not success:
                    raise HTTPException(
                        status_code=500, 
                        detail="Failed to create database table"
                    )
                    
            except Exception as e:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to process CSV file: {str(e)}"
                )
        
        # Index documents for RAG
        run_indexer()
        
        return UploadResponse(
            message=f"{filename} uploaded successfully for role '{role}'",
            filename=filename,
            role=role,
            filepath=str(filepath)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, user=Depends(authenticate_user)):
    """Handle chat queries with automatic mode detection and role-based access control"""
    role = user.role
    username = user.username
    question = req.question

    # Log the query attempt
    db_manager = get_db_manager()
    
    try:
        # Role-based access validation - More intelligent approach
        from app.config import ROLE_DOCS_MAPPING
        
        # Check if user's role has access to the type of information they're asking for
        allowed_roles = ROLE_DOCS_MAPPING.get(role, [])
        
        # Only block access if the question is clearly trying to access information
        # that is completely outside the user's role domain
        question_lower = question.lower()
        
        # Define clear cross-role access patterns that should be blocked
        # These are more specific patterns that indicate intentional cross-role access attempts
        
        # Finance-specific queries (blocked for non-finance roles unless they're agriculture-related)
        finance_blocking_patterns = [
            "quarterly financial report",
            "revenue analysis",
            "profit margins",
            "budget allocation",
            "investment portfolio",
            "financial statements",
            "cost analysis report"
        ]
        
        # Market analysis specific queries (blocked for non-market roles unless agriculture-related)
        market_blocking_patterns = [
            "market competition analysis",
            "demand forecasting report",
            "supply chain market analysis",
            "competitive pricing analysis"
        ]
        
        # HR specific queries (blocked for non-HR roles)
        hr_blocking_patterns = [
            "employee salary",
            "personnel records",
            "staffing budget",
            "compensation structure",
            "recruitment pipeline"
        ]
        
        # Supply chain specific queries (blocked for non-supply chain roles unless agriculture-related)
        supply_chain_blocking_patterns = [
            "warehouse inventory levels",
            "logistics cost analysis",
            "distribution network optimization",
            "transportation contracts"
        ]
        
        # Check for blocking patterns only if they're not agriculture-related
        # Allow agriculture-related questions for all roles EXCEPT HR
        agriculture_context_indicators = [
            "crop", "soil", "farming", "agriculture", "harvest", "irrigation", 
            "fertilizer", "pesticide", "field", "plant", "seed", "yield", "rice", "wheat",
            "corn", "vegetables", "fruits", "livestock", "poultry", "dairy", "organic",
            "pest control", "weed management", "soil fertility", "crop rotation"
        ]
        
        has_agriculture_context = any(indicator in question_lower for indicator in agriculture_context_indicators)
        
        # HR users should NOT be able to ask agricultural questions
        if role == "HR" and has_agriculture_context:
            db_manager.log_query(username, role, "BLOCKED", question, False, "HR agricultural access denied")
            raise HTTPException(
                status_code=403, 
                detail="Sorry, you don't have permission to access agricultural information. As an HR user, you can only access HR-related documents. If you need farming advice, please contact an agriculture expert or farmer."
            )
        
        # Only block if there's a clear cross-role access attempt without agriculture context
        if not has_agriculture_context:
            # Check finance blocking patterns
            if role not in ["Finance Officer", "Admin"]:
                if any(pattern in question_lower for pattern in finance_blocking_patterns):
                    db_manager.log_query(username, role, "BLOCKED", question, False, "Finance access denied")
                    raise HTTPException(
                        status_code=403, 
                        detail="Sorry, you don't have permission to access financial information. This type of data is restricted to finance officers only. Please contact the finance department if you need this information."
                    )
            
            # Check market analysis blocking patterns
            if role not in ["Market Analysis", "Admin"]:
                if any(pattern in question_lower for pattern in market_blocking_patterns):
                    db_manager.log_query(username, role, "BLOCKED", question, False, "Market analysis access denied")
                    raise HTTPException(
                        status_code=403, 
                        detail="Sorry, you don't have permission to access market analysis information. This data is restricted to market analysts only. Please contact the marketing department if you need this information."
                    )
            
            # Check HR blocking patterns
            if role not in ["HR", "Admin"]:
                if any(pattern in question_lower for pattern in hr_blocking_patterns):
                    db_manager.log_query(username, role, "BLOCKED", question, False, "HR access denied")
                    raise HTTPException(
                        status_code=403, 
                        detail="Sorry, you don't have permission to access HR information. This data is restricted to HR personnel only. Please contact the HR department if you need this information."
                    )
            
            # Check supply chain blocking patterns
            if role not in ["Supply Chain Manager", "Admin"]:
                if any(pattern in question_lower for pattern in supply_chain_blocking_patterns):
                    db_manager.log_query(username, role, "BLOCKED", question, False, "Supply chain access denied")
                    raise HTTPException(
                        status_code=403, 
                        detail="Sorry, you don't have permission to access supply chain information. This data is restricted to supply chain managers only. Please contact the supply chain department if you need this information."
                    )
        
        # 1. Detect mode: SQL or RAG
        mode = detect_query_type_llm(question)
        logger.info(f"Query mode detected: {mode} for question: {question}")
        
        result = {}
        fallback_used = False

        # 2. Route to appropriate handler
        if mode == "SQL":
            logger.info(f"Routing to SQL handler for question: {question}")
            try:
                result = await ask_csv(question, role, username, return_sql=True)

                # Check if SQL query failed or returned an error
                if result.get("error") or not result.get("answer", "").strip() or "Only SELECT queries are allowed" in result.get("answer", ""):
                    raise ValueError("SQL query blocked or failed")
                
                # Log successful SQL query
                db_manager.log_query(username, role, "SQL", question, True)

            except Exception as e:
                logger.info(f"SQL query failed, falling back to RAG: {str(e)}")
                # Log failed SQL query
                db_manager.log_query(username, role, "SQL", question, False, str(e))
                
                # Fallback to RAG
                result = await ask_rag(question, role)
                fallback_used = True
                mode = "SQL → fallback to RAG"
                
                # Log fallback RAG query
                db_manager.log_query(username, role, "RAG_FALLBACK", question, True)

        else:
            logger.info(f"Routing to RAG handler for question: {question}")
            result = await ask_rag(question, role)
            # Log RAG query
            db_manager.log_query(username, role, "RAG", question, True)

        return ChatResponse(
            user=username,
            role=role,
            mode=mode,
            fallback=fallback_used,
            answer=result["answer"],
            sql=result.get("sql")
        )

    except HTTPException as http_ex:
        # Handle 403 Forbidden errors with user-friendly messages
        if http_ex.status_code == 403:
            # Log the blocked query
            try:
                db_manager.log_query(username, role, "BLOCKED", question, False, "Access denied by role validation")
            except Exception as log_error:
                logger.error(f"Failed to log blocked query: {log_error}")
            
            # Return user-friendly error message
            return ChatResponse(
                user=username,
                role=role,
                mode="BLOCKED",
                fallback=False,
                answer=f"you don't have permission to access this type of information. As a {role} user, you can only access documents related to your role. Please contact your administrator if you need access to other information.",
                sql=None
            )
        else:
            # Re-raise other HTTP exceptions
            raise
    except Exception as e:
        # Log failed query
        try:
            db_manager.log_query(username, role, "UNKNOWN", question, False, str(e))
        except Exception as log_error:
            logger.error(f"Failed to log failed query: {log_error}")
        
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.get("/health", response_model=HealthCheck)
def health_check():
    """Health check endpoint"""
    from datetime import datetime
    return HealthCheck(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
