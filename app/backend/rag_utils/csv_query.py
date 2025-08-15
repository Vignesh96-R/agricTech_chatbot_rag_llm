import re
import tabulate
from openai import OpenAI
import pandas as pd
from pathlib import Path
import logging

from app.config import OPENAI_API_KEY, OPENAI_MODEL, FORBIDDEN_SQL_KEYWORDS
from app.backend.database import get_db_manager

# Configure logging
logger = logging.getLogger(__name__)

# OpenAI setup
client = OpenAI(api_key=OPENAI_API_KEY)

def get_allowed_tables_for_role(role: str) -> list[str]:
    """Get tables that a role can access."""
    db_manager = get_db_manager()
    return db_manager.get_allowed_tables_for_role(role)

def extract_tables_from_sql(sql: str) -> list[str]:
    # Extract tables used in FROM and JOIN clauses
    return re.findall(r'FROM\s+(\w+)|JOIN\s+(\w+)', sql, flags=re.IGNORECASE)

def flatten_matches(matches: list[tuple]) -> list[str]:
    return [item for tup in matches for item in tup if item]

def is_safe_query(sql: str) -> bool:
    """Check if a SQL query is safe to execute."""
    lowered = sql.strip().lower().rstrip(";")
    return lowered.startswith("select") and all(word not in lowered for word in FORBIDDEN_SQL_KEYWORDS)

def translate_nl_to_sql(question: str, allowed_tables: list[str]) -> str:
    print("translate_nl_to_sql() called")
    
    # Get schemas from agriculture resources folder
    resources_path = Path("resources_2")
    schemas = []
    
    # Check each agriculture role folder for CSV files
    role_folders = [
        "agriculture expert", "farmer", "field worker", "finance officer", 
        "hr", "market analysis", "salesperson", "supply chain manager"
    ]
    
    for role in role_folders:
        role_path = resources_path / role
        if role_path.exists():
            for file_path in role_path.iterdir():
                if file_path.suffix.lower() == ".csv":
                    try:
                        table_name = Path(file_path.name).stem.replace("-", "_")
                        # Read CSV to get headers
                        df = pd.read_csv(file_path)
                        cols = ", ".join(df.columns.tolist())
                        schemas.append(f"Table: {table_name}\nColumns: {cols}")
                        print(f"Added schema for {table_name}: {cols}")
                    except Exception as e:
                        print(f"❌ Error while building schema for {file_path}: {e}")

    print("Schemas:", schemas)

    schema_block = "\n\n".join(schemas)
    print("schema_block:\n", schema_block)

    # Prompt for LLM
    prompt = f"""
    You are an agriculture expert assistant that converts natural language questions into safe SQL SELECT queries.

    Use only the following schemas:
    {schema_block}

    Constraints:
    - Use only the tables listed above.
    - Use the exact column names as-is (including hyphens, underscores, casing).
    - Return only a SELECT query (no INSERT/UPDATE/DELETE).
    - Focus on agriculture-related data analysis.
    - If asked about 'employee name', consider alternatives like 'full-name', 'last-name'.
    - If asked about 'position', consider synonyms like 'role', 'designation'.
    - Do not mix aggregate functions (like COUNT(*)) with *. Use either a grouped summary or return them separately."
    Natural Language Question: "{question}"

    SQL:
    """

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        logger.info("LLM call successful")
        
        response_text = response.choices[0].message.content.strip()
        
        logger.debug(f"Raw SQL from LLM: {response_text}")

        return response_text

    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return "Error generating SQL"

async def ask_csv(question: str, role: str, username: str, return_sql: bool = False) -> dict:
    allowed_tables = get_allowed_tables_for_role(role)

    try:
        sql = translate_nl_to_sql(question, allowed_tables)
        print(f"[SQL GENERATED]:\n{sql}")

        if not is_safe_query(sql):
            return {"answer": "Only SELECT queries are allowed.", "error": True}

        raw_matches = extract_tables_from_sql(sql)
        referenced_tables = flatten_matches(raw_matches)

        for table in referenced_tables:
            if table not in allowed_tables:
                return {"answer": f"Access denied to table: {table}", "error": True}

        db_manager = get_db_manager()
        result = db_manager.execute_query_with_columns(sql)
        output = [list(row) for row in result["data"]]
        columns = result["columns"]

        markdown_table = tabulate.tabulate(output, headers=columns, tablefmt="github")
        response = {
            "answer": markdown_table if output else "Query executed, but no results found."
        }

        if return_sql:
            response["sql"] = sql

        return response

    except Exception as e:
        logger.error(f"Error in ask_csv: {e}")
        return {"answer": f"❌ Error: {str(e)}", "error": True}
