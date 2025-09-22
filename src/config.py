"""
Configuration settings for the Financial Analyst Q&A Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the Financial Analyst Q&A Bot"""
    
    # OpenAI API Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-3.5-turbo"  # Can be changed to gpt-4 for better results
    
    # Embedding Configuration
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast and efficient embedding model
    EMBEDDING_DIMENSION = 384
    
    # Vector Store Configuration
    VECTOR_STORE_PATH = "vector_store.faiss"
    CHUNK_SIZE = 1000  # Size of text chunks
    CHUNK_OVERLAP = 200  # Overlap between chunks
    
    # RAG Configuration
    TOP_K_RESULTS = 5  # Number of relevant chunks to retrieve
    MAX_TOKENS = 1000  # Maximum tokens for LLM response
    
    # File Processing Configuration
    SUPPORTED_FILE_TYPES = [".pdf", ".xml", ".htm"]
    DATA_DIRECTORY = "data"
    
    # Streamlit Configuration
    PAGE_TITLE = "Financial Analyst Q&A Bot"
    PAGE_ICON = "📊"
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        return True
