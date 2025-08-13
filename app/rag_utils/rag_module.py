# ========== CONFIG ==========
from pathlib import Path
import os
import pandas as pd
from collections import defaultdict
from langchain_core.documents import Document

from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereRerank

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set environment variables from .env file
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "RAG"

# ==============================
# ====Split,load,embed==========
# ==============================

openai_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(
    collection_name="my_collection",
    persist_directory="chroma_db",
    embedding_function=openai_embeddings
)

def embed_documents_to_vectorstore(docs):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    vectorstore.add_documents(splits)
    
    print("Documents embedded and saved to vectorstore.")
    print("Total documents:", len(vectorstore.get()["documents"]))

def load_file(filepath, role):
    ext = Path(filepath).suffix.lower()
    try:
        if ext == ".csv":
            df1 = pd.read_csv(filepath)
            documents = []
            for row in df1.to_dict(orient="records"):
                content = "\n".join(f"{k}: {v}" for k, v in row.items())
                documents.append(
                    Document(
                        page_content=content,
                        metadata={"role": role.lower(), "source": Path(filepath).name, "file_type": "csv"}
                    )
                )
            return documents  # Return a list of documents

        elif ext == ".md":
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            return [
                Document(
                    page_content=content,
                    metadata={"role": role.lower(), "source": Path(filepath).name, "file_type": "markdown"}
                )
            ]
        else:
            return None

    except Exception as e:
        print(f"Failed to process {filepath}: {e}")
        return None

def run_indexer():
    """Load and index documents from the agriculture resources folder and uploaded files"""
    resources_path = Path("resources_2")
    uploads_path = Path("static/uploads")
    all_docs = []
    
    # Define agriculture role folders for resources_2
    role_folders = {
        "agriculture expert": resources_path / "agriculture expert",
        "farmer": resources_path / "farmer", 
        "field worker": resources_path / "field worker",
        "finance officer": resources_path / "finance officer",
        "hr": resources_path / "hr",
        "market analysis": resources_path / "market analysis",
        "salesperson": resources_path / "salesperson",
        "supply chain manager": resources_path / "supply chain manager"
    }
    
    # Process documents from resources_2 directory
    for role, folder_path in role_folders.items():
        if folder_path.exists():
            print(f"Processing {role} documents from resources_2...")
            for file_path in folder_path.iterdir():
                if file_path.is_file():
                    docs = load_file(file_path, role)
                    if docs:
                        if isinstance(docs, list):
                            all_docs.extend(docs)
                        else:
                            all_docs.append(docs)
                        print(f"Loaded {file_path.name} for role {role}")
    
    # Process uploaded documents from static/uploads directory
    if uploads_path.exists():
        print("Processing uploaded documents...")
        for role_folder in uploads_path.iterdir():
            if role_folder.is_dir():
                role_name = role_folder.name.lower()
                print(f"Processing uploaded documents for role: {role_name}")
                for file_path in role_folder.iterdir():
                    if file_path.is_file():
                        docs = load_file(file_path, role_name)
                        if docs:
                            if isinstance(docs, list):
                                all_docs.extend(docs)
                            else:
                                all_docs.append(docs)
                            print(f"Loaded uploaded file {file_path.name} for role {role_name}")

    if all_docs:
        embed_documents_to_vectorstore(all_docs)
        print(f"Indexed {len(all_docs)} document chunks.")
    else:
        print("No documents found to index.")

# ==============================
# ========== ROLE VALIDATION ==========
# ==============================
def validate_role_access(user_role: str, allowed_roles: list = None) -> bool:
    """
    Validate if a user role has access to specific document roles.
    
    Args:
        user_role: The user's role
        allowed_roles: List of roles the user can access (defaults to user_role)
        
    Returns:
        True if access is valid, False otherwise
    """
    if not allowed_roles:
        if user_role.lower() == "Admin":
            allowed_roles = ["agriculture expert", "farmer", "field worker", "finance officer", "hr", "market analysis", "salesperson", "supply chain manager"]
        else:
            allowed_roles = [user_role.lower()]
    
    return True  # This function can be extended for more complex validation

def get_role_filter(user_role: str) -> dict:
    """
    Get the appropriate ChromaDB filter for a user role.
    
    Args:
        user_role: The user's role
        
    Returns:
        ChromaDB filter dictionary
    """
    # Map authentication role names to metadata role names
    role_mapping = {
        "Admin": "Admin",
        "agriculture expert": "agriculture expert",
        "farmer": "farmer",
        "field worker": "field worker",
        "finance officer": "finance officer",
        "hr": "hr",
        "market analysis": "market analysis",
        "sales person": "salesperson",
        "supply chain manager": "supply chain manager"
    }
    
    # Convert to lowercase and map to metadata role name
    user_role_lower = user_role.lower()
    metadata_role = role_mapping.get(user_role_lower, user_role_lower)
    
    if metadata_role == "Admin":
        # Admin sees everything - no filter
        return {}
    else:
        # All other roles see only their specific documents
        return {"role": metadata_role}

# ==============================
# ========== PROMPT TEMPLATE ==========
# ==============================
system_prompt = (
    "You are an agriculture expert assistant for summarizing and answering queries from agriculture-related documents.\n"
    "Always use the retrieved context to answer the query, even if partial.\n"
    "Do not guess. If data is not found, explain what you searched for.\n"
    "When responding:\n"
    "- Add **Source** from document metadata if possible.\n"
    "- Use headers\n"
    "- Use bullet points\n"
    "- For CSV-style data, format in table with two columns\n"
    "- Focus on agriculture-specific terminology and best practices\n"
    "\n{context}"
)

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

# ==============================
# ========== MODEL ==========
# ==============================
model = ChatOpenAI(
    model="gpt-4o",  
    temperature=0.2
)

question_answering_chain = create_stuff_documents_chain(model, chat_prompt)

# ==============================
# Add a Reranker
# ==============================
def wrap_with_reranker(retriever, cohere_api_key, top_n=4):
    #print("[INFO] Using Cohere reranker.")
    reranker = CohereRerank(cohere_api_key=cohere_api_key, top_n=top_n)
    return ContextualCompressionRetriever(
        base_compressor=reranker,
        base_retriever=retriever
    )

def get_rag_chain(user_role: str,cohere_api_key: str = None):
    user_role = user_role.lower()
    
    # Validate role access
    if not validate_role_access(user_role):
        raise ValueError(f"Invalid role access for user role: {user_role}")
    
    # Get appropriate role filter
    role_filter = get_role_filter(user_role)
    
    # Create retriever with role-based filtering
    if role_filter:
        retriever = vectorstore.as_retriever(search_kwargs={
            "k": 4,
            "filter": role_filter
        })
    else:
        # No filter for Admin users
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    # wrap with reranker
    if cohere_api_key:
        print("Using cohere reranker")
        retriever = wrap_with_reranker(retriever, cohere_api_key)

    # Create the retrieval chain using the new LangChain syntax
    def create_chain(input_dict):
        # Get the question from input
        question = input_dict["input"]
        
        # Retrieve relevant documents
        docs = retriever.get_relevant_documents(question)
        
        # Generate answer using the question answering chain
        answer = question_answering_chain.invoke({
            "context": docs,
            "input": question
        })
        
        # Handle different response formats
        if isinstance(answer, dict) and "answer" in answer:
            answer_text = answer["answer"]
        elif isinstance(answer, str):
            answer_text = answer
        else:
            answer_text = str(answer)
        
        return {
            "context": docs,
            "answer": answer_text
        }
    
    return create_chain


"""
# ========== MAIN EXECUTION ==========
if __name__ == "__main__":
    run_indexer() 
"""
    # ========== EXAMPLE USAGE ==========
"""
    user_role = "hr" 
    rag_chain = get_rag_chain(user_role)

    
    query = "give me Campaign Highlights from marketing summary."
    response = rag_chain.invoke({"input": query})

    print((response["answer"]))
    for doc in response.get("context", []):
        print(f"Source: {doc.metadata['source']}, Role: {doc.metadata.get('role')}")

"""

