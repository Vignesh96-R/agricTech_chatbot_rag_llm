from pathlib import Path
import os
import logging
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks

from app.config import (
    AVAILABLE_ROLES, ALLOWED_EXTENSIONS, 
    MAX_FILE_SIZE, UPLOADS_DIR, RESOURCES_DIR
)

from app.backend.models import ChatRequest, ChatResponse, UploadResponse, AvailableDocsResponse, LoginResponse, HealthCheck, QueryType
from app.backend.auth import authenticate_user, require_c_level_access, get_user_role_dependencies
from app.backend.database import get_db_manager
from app.backend.rag_utils.rag_module import run_indexer, vectorstore, get_rag_chain
from app.backend.rag_utils.query_classifier import detect_query_type_llm
from app.backend.rag_utils.csv_query import ask_csv
from app.backend.rag_utils.rag_chain import ask_rag
from app.backend.role_validator import validate_role_access

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

@app.post("/upload-docs", response_model=UploadResponse)
async def upload_docs(
    background_tasks: BackgroundTasks,
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
        
        # Prepare storage
        role_dir = UPLOADS_DIR / role
        role_dir.mkdir(parents=True, exist_ok=True)
        filepath = role_dir / filename

        # Stream upload to disk to limit memory usage and enforce size cap
        total_bytes = 0
        try:
            with open(filepath, "wb") as f:
                while True:
                    chunk = await file.read(1024 * 1024)
                    if not chunk:
                        break
                    total_bytes += len(chunk)
                    if total_bytes > MAX_FILE_SIZE:
                        try:
                            f.close()
                        finally:
                            try:
                                os.remove(filepath)
                            except Exception:
                                pass
                        raise HTTPException(
                            status_code=400,
                            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
                        )
                    f.write(chunk)
        finally:
            await file.close()

        # Handle CSV files - create database table
        if extension == ".csv":
            try:
                # Generate a safe table name
                raw_name = Path(filename).stem.replace("-", "_")
                table_name = "".join(ch if (ch.isalnum() or ch == "_") else "_" for ch in raw_name)
                # Create table in database using DuckDB's CSV reader for performance
                db_manager = get_db_manager()
                success = db_manager.create_table_from_csv_path(table_name, str(filepath), role)
                if not success:
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to create database table"
                    )
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to process CSV file: {str(e)}"
                )
        
        # Index documents for RAG in the background to reduce request latency
        try:
            background_tasks.add_task(run_indexer)
        except Exception:
            # Fallback to synchronous indexing if background scheduling fails
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
        # Role-based access validation
        validate_role_access(question, role, username, db_manager)
        
        # 1. Detect mode: SQL or RAG
        mode = detect_query_type_llm(question)
        logger.info(f"Query mode detected: {mode.value} for question: {question}")
        
        result = {}
        fallback_used = False

        # 2. Route to appropriate handler
        if mode == QueryType.SQL:
            logger.info(f"Routing to SQL handler for question: {question}")
            try:
                result = await ask_csv(question, role, username, return_sql=True)

                # Check if SQL query failed or returned an error
                if result.get("error") or not result.get("answer", "").strip() or "Only SELECT queries are allowed" in result.get("answer", ""):
                    raise ValueError("SQL query blocked or failed")
                
                # Log successful SQL query
                db_manager.log_query(username, role, QueryType.SQL.value, question, True)

            except Exception as e:
                logger.info(f"SQL query failed, falling back to RAG: {str(e)}")
                # Log failed SQL query
                db_manager.log_query(username, role, QueryType.SQL.value, question, False, str(e))
                
                # Fallback to RAG
                result = await ask_rag(question, role)
                fallback_used = True
                mode = QueryType.UNKNOWN  # Use UNKNOWN for fallback cases
                
                # Log fallback RAG query
                db_manager.log_query(username, role, "RAG_FALLBACK", question, True)

        else:
            logger.info(f"Routing to RAG handler for question: {question}")
            result = await ask_rag(question, role)
            # Log RAG query
            db_manager.log_query(username, role, QueryType.RAG.value, question, True)

        return ChatResponse(
            user=username,
            role=role,
            mode=mode.value,
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
                mode=QueryType.UNKNOWN.value,
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
            db_manager.log_query(username, role, QueryType.UNKNOWN.value, question, False, str(e))
        except Exception as log_error:
            logger.error(f"Failed to log failed query: {log_error}")
        
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.get("/health", response_model=HealthCheck)
def health_check():
    """Health check endpoint"""
    return HealthCheck(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
