"""
Database operations and connection management for the RBAC-Project application.

This module handles DuckDB connections, table operations, and data management.
"""

import duckdb
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from app.config import DUCKDB_PATH, DUCKDB_DIR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages DuckDB database operations and connections."""
    
    def __init__(self, db_path: Path = DUCKDB_PATH):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to the DuckDB database file
        """
        self.db_path = db_path
        self.connection = None
        self._connection_closed = False
        self._ensure_db_directory()
        self._initialize_database()
    
    def _ensure_db_directory(self):
        """Ensure the database directory exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _initialize_database(self):
        """Initialize the database with required tables."""
        try:
            # Try to connect with WAL recovery options
            try:
                self.connection = duckdb.connect(str(self.db_path))
                self._connection_closed = False
            except Exception as e:
                if "WAL file" in str(e) or "Binder Error" in str(e):
                    logger.warning(f"WAL corruption detected, attempting recovery: {e}")
                    # Try to remove WAL file and reconnect
                    import os
                    wal_path = str(self.db_path) + ".wal"
                    if os.path.exists(wal_path):
                        try:
                            os.remove(wal_path)
                            logger.info("Removed corrupted WAL file")
                        except Exception as remove_error:
                            logger.warning(f"Could not remove WAL file: {remove_error}")
                    
                    # Try to connect again
                    self.connection = duckdb.connect(str(self.db_path))
                    self._connection_closed = False
                else:
                    raise e
            
            self._create_tables()
            logger.info(f"Database initialized successfully at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        try:
            # Create tables_metadata table
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS tables_metadata (
                    table_name TEXT PRIMARY KEY,
                    role TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create documents table for tracking uploaded documents
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY,
                    filename TEXT NOT NULL,
                    role TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_size INTEGER,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    uploaded_by TEXT
                )
            """)
            
            # Create query_log table for auditing with auto-incrementing ID
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS query_log (
                    id BIGINT PRIMARY KEY,
                    username TEXT NOT NULL,
                    role TEXT NOT NULL,
                    query_type TEXT NOT NULL,
                    query_text TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN,
                    error_message TEXT
                )
            """)
            
            # Add sequence for auto-incrementing ID if it doesn't exist
            self.connection.execute("""
                CREATE SEQUENCE IF NOT EXISTS query_log_id_seq
            """)
            
            # Set the default value for id to use the sequence
            try:
                self.connection.execute("""
                    ALTER TABLE query_log 
                    ALTER COLUMN id SET DEFAULT nextval('query_log_id_seq')
                """)
            except Exception:
                # Column might already have default, ignore error
                pass
            
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """
        Get the database connection.
        
        Returns:
            DuckDB connection object
        """
        if self.connection is None or self._connection_closed:
            try:
                self.connection = duckdb.connect(str(self.db_path))
                self._connection_closed = False
            except Exception as e:
                logger.error(f"Failed to create new database connection: {e}")
                raise
        return self.connection
    
    def execute_query(self, query: str, params: Optional[List[Any]] = None) -> List[tuple]:
        """
        Execute a SQL query and return results.
        
        Args:
            query: SQL query to execute
            params: Query parameters (optional)
            
        Returns:
            List of result tuples
        """
        try:
            conn = self.get_connection()
            if params:
                result = conn.execute(query, params).fetchall()
            else:
                result = conn.execute(query).fetchall()
            return result
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_query_with_columns(self, query: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """
        Execute a SQL query and return results with column information.
        
        Args:
            query: SQL query to execute
            params: Query parameters (optional)
            
        Returns:
            Dictionary with 'data' and 'columns' keys
        """
        try:
            conn = self.get_connection()
            if params:
                result = conn.execute(query, params)
            else:
                result = conn.execute(query)
            
            data = result.fetchall()
            columns = [desc[0] for desc in result.description]
            
            return {
                "data": data,
                "columns": columns
            }
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def create_table_from_dataframe(self, table_name: str, df: pd.DataFrame, role: str) -> bool:
        """
        Create a table from a pandas DataFrame.
        
        Args:
            table_name: Name of the table to create
            df: Pandas DataFrame containing the data
            role: Role associated with this table
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            
            # Create or replace the table
            conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")
            
            # Update metadata
            self._upsert_table_metadata(table_name, role)
            
            logger.info(f"Table {table_name} created successfully for role {role}")
            return True
        except Exception as e:
            logger.error(f"Failed to create table {table_name}: {e}")
            return False
    
    def _upsert_table_metadata(self, table_name: str, role: str):
        """
        Insert or update table metadata.
        
        Args:
            table_name: Name of the table
            role: Role associated with the table
        """
        try:
            conn = self.get_connection()
            conn.execute("""
                INSERT INTO tables_metadata (table_name, role, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT (table_name) 
                DO UPDATE SET 
                    role = excluded.role,
                    updated_at = CURRENT_TIMESTAMP
            """, [table_name, role])
        except Exception as e:
            logger.error(f"Failed to update table metadata: {e}")
    
    def get_allowed_tables_for_role(self, role: str) -> List[str]:
        """
        Get tables that a role can access.
        
        Args:
            role: The user's role
            
        Returns:
            List of accessible table names
        """
        try:
            if role.lower() == "Admin":
                query = "SELECT table_name FROM tables_metadata"
                result = self.execute_query(query)
            elif role.lower() == "general":
                query = "SELECT table_name FROM tables_metadata WHERE role = 'general'"
                result = self.execute_query(query)
            else:
                query = """
                SELECT table_name FROM tables_metadata
                WHERE role = ? OR role = 'general'
                """
                result = self.execute_query(query, [role])
            
            return [row[0] for row in result]
        except Exception as e:
            logger.error(f"Failed to get allowed tables for role {role}: {e}")
            return []
    
    def is_connection_valid(self) -> bool:
        """
        Check if the current database connection is valid.
        
        Returns:
            True if connection is valid, False otherwise
        """
        if self.connection is None or self._connection_closed:
            return False
        
        try:
            # Try a simple query to test the connection
            self.connection.execute("SELECT 1")
            return True
        except Exception:
            self._connection_closed = True
            return False
    
    def is_database_healthy(self) -> bool:
        """
        Check if the database is in a healthy state.
        
        Returns:
            True if database is healthy, False otherwise
        """
        try:
            if self.connection is None or self._connection_closed:
                return False
            
            # Try a simple query to test the connection
            self.connection.execute("SELECT 1")
            return True
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            return False
    
    def log_query(self, username: str, role: str, query_type: str, query_text: str, 
                  success: bool, error_message: Optional[str] = None):
        """
        Log a query for auditing purposes.
        
        Args:
            username: Username of the user
            role: Role of the user
            query_type: Type of query (SQL/RAG)
            query_text: The actual query text
            success: Whether the query was successful
            error_message: Error message if query failed
        """
        try:
            # Check if database is healthy before logging
            if not self.is_database_healthy():
                logger.warning("Database not healthy, attempting to recover for logging")
                try:
                    self.safe_reset_connection()
                except Exception as recovery_error:
                    logger.error(f"Database recovery failed during logging: {recovery_error}")
                    # Log to console as fallback
                    logger.info(f"FALLBACK LOG: {username} ({role}) - {query_type}: {query_text} - Success: {success} - Error: {error_message}")
                    return
            
            conn = self.get_connection()
            
            # Try to insert with auto-incrementing ID first
            try:
                conn.execute("""
                    INSERT INTO query_log (username, role, query_type, query_text, success, error_message)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, [username, role, query_type, query_text, success, error_message])
            except Exception as id_error:
                # If auto-increment fails, try to manually generate ID
                logger.warning(f"Auto-increment failed, trying manual ID generation: {id_error}")
                try:
                    # Get the next available ID
                    result = conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM query_log").fetchone()
                    next_id = result[0] if result else 1
                    
                    conn.execute("""
                        INSERT INTO query_log (id, username, role, query_type, query_text, success, error_message)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, [next_id, username, role, query_type, query_text, success, error_message])
                except Exception as manual_error:
                    logger.error(f"Manual ID generation also failed: {manual_error}")
                    # Log to console as final fallback
                    logger.info(f"FALLBACK LOG: {username} ({role}) - {query_type}: {query_text} - Success: {success} - Error: {error_message}")
                    return
            
            logger.debug(f"Query logged successfully: {username} ({role}) - {query_type}")
            
        except Exception as e:
            logger.error(f"Failed to log query: {e}")
            # Log to console as fallback
            logger.info(f"FALLBACK LOG: {username} ({role}) - {query_type}: {query_text} - Success: {success} - Error: {error_message}")
            # Don't raise the exception - logging failure shouldn't break the main functionality
    
    def get_table_schema(self, table_name: str) -> Optional[List[str]]:
        """
        Get the schema (column names) of a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of column names or None if table doesn't exist
        """
        try:
            conn = self.get_connection()
            result = conn.execute(f"DESCRIBE {table_name}")
            columns = [row[0] for row in result.fetchall()]
            return columns
        except Exception as e:
            logger.error(f"Failed to get schema for table {table_name}: {e}")
            return None
    
    def reset_connection(self):
        """Reset the database connection."""
        try:
            if self.connection:
                self.connection.close()
        except Exception:
            pass  # Ignore errors when closing
        finally:
            self.connection = None
            self._connection_closed = False
    
    def safe_reset_connection(self):
        """Safely reset the database connection, handling WAL corruption."""
        try:
            if self.connection:
                self.connection.close()
        except Exception:
            pass  # Ignore errors when closing
        finally:
            self.connection = None
            self._connection_closed = False
        
        # Try to remove any corrupted WAL files
        try:
            import os
            wal_path = str(self.db_path) + ".wal"
            if os.path.exists(wal_path):
                os.remove(wal_path)
                logger.info("Removed potentially corrupted WAL file during reset")
        except Exception as e:
            logger.warning(f"Could not remove WAL file during reset: {e}")
        
        # Reinitialize the database
        self._initialize_database()
    
    def close_connection(self):
        """Close the database connection."""
        if self.connection and not self._connection_closed:
            try:
                self.connection.close()
                self._connection_closed = True
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
                self._connection_closed = True
    
    def cleanup_corrupted_files(self):
        """Clean up corrupted database files and WAL files."""
        try:
            import os
            
            # Remove WAL file if it exists
            wal_path = str(self.db_path) + ".wal"
            if os.path.exists(wal_path):
                os.remove(wal_path)
                logger.info("Removed corrupted WAL file")
            
            # Remove lock file if it exists
            lock_path = str(self.db_path) + ".lock"
            if os.path.exists(lock_path):
                os.remove(lock_path)
                logger.info("Removed database lock file")
            
            # Remove temporary files
            temp_path = str(self.db_path) + ".tmp"
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.info("Removed temporary database file")
                
        except Exception as e:
            logger.error(f"Failed to cleanup corrupted files: {e}")
    
    def reset_database(self):
        """Reset the entire database by removing all files and reinitializing."""
        try:
            import os
            
            # Close current connection
            if self.connection:
                self.connection.close()
                self.connection = None
                self._connection_closed = True
            
            # Remove all database files
            self.cleanup_corrupted_files()
            
            # Remove main database file
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
                logger.info("Removed main database file")
            
            # Reinitialize
            self._initialize_database()
            logger.info("Database reset completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to reset database: {e}")
            raise
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_connection()

# Global database manager instance - lazy initialization
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """
    Get the global database manager instance.
    
    Returns:
        DatabaseManager instance
    """
    global _db_manager
    
    if _db_manager is None:
        try:
            _db_manager = DatabaseManager()
        except Exception as e:
            logger.error(f"Failed to initialize database manager: {e}")
            # Try to recover from WAL corruption
            if "WAL file" in str(e) or "Binder Error" in str(e):
                logger.info("Attempting to recover from WAL corruption...")
                try:
                    # Remove corrupted WAL file
                    import os
                    db_path = DUCKDB_PATH
                    wal_path = str(db_path) + ".wal"
                    if os.path.exists(wal_path):
                        os.remove(wal_path)
                        logger.info("Removed corrupted WAL file")
                    
                    # Try to initialize again
                    _db_manager = DatabaseManager()
                    logger.info("Successfully recovered from WAL corruption")
                except Exception as recovery_error:
                    logger.error(f"Recovery failed: {recovery_error}")
                    # Create a minimal database manager for basic operations
                    _db_manager = DatabaseManager.__new__(DatabaseManager)
                    _db_manager.db_path = DUCKDB_PATH
                    _db_manager.connection = None
                    _db_manager._connection_closed = True
                    logger.warning("Created minimal database manager due to initialization failure")
            else:
                # For other errors, create a minimal manager
                _db_manager = DatabaseManager.__new__(DatabaseManager)
                _db_manager.db_path = DUCKDB_PATH
                _db_manager.connection = None
                _db_manager._connection_closed = True
                logger.warning("Created minimal database manager due to initialization failure")
    
    return _db_manager
