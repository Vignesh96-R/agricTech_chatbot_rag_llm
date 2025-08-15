from openai import OpenAI
import os
import re
from app.backend.rag_utils.secrets import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def _heuristic_detect_query_type(question: str) -> str:
    q = (question or "").lower()
    sql_keywords = [
        "average", "sum", "total", "count", "how many", "filter",
        "greater than", "less than", "top ", "group by", "order by",
        "max", "min", "median", "mean", "percent", "between",
        "where", "select", "from", "join", "table", "dataset",
        "list all", "show all", "number of", "details of"
    ]
    if any(kw in q for kw in sql_keywords):
        return "SQL"
    return "RAG"

def detect_query_type_llm(question: str) -> str:
    # Fast local heuristic first to avoid latency and external dependency
    heuristic = _heuristic_detect_query_type(question)

    # If no API key or client unavailable, use heuristic
    if not OPENAI_API_KEY or client is None:
        return heuristic

    try:
        prompt = f"""
You are a classifier that decides if a user's question should be handled by structured SQL query logic or by unstructured document search (RAG).

If the question contains terms related to structured data analysis (e.g., average, sum, total, count, how many, filter, greater than, less than, top 5, group by, details of employee etc.), classify it as:
SQL

If the question is more about general understanding, summarization, definitions, or cannot be answered from structured tabular data, classify it as:
RAG

Respond with only one word: either SQL or RAG.

Question: "{question}"
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            timeout=20,
        )

        label = (response.choices[0].message.content or "").strip().upper()
        if label in {"SQL", "RAG"}:
            return label
        return heuristic
    except Exception:
        # Network/model errors → graceful fallback
        return heuristic
