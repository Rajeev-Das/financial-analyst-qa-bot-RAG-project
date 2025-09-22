"""
Vector store implementation using FAISS for document embeddings
"""
import os
import pickle
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Tuple
from config import Config

class VectorStore:
    """Manages document embeddings and similarity search using FAISS"""
    
    def __init__(self):
        self.config = Config()
        self.embedding_model = SentenceTransformer(self.config.EMBEDDING_MODEL)
        self.index = None
        self.documents = []
        self.metadata = []
        
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to the vector store
        
        Args:
            documents: List of document chunks with text and metadata
        """
        if not documents:
            return
            
        # Extract text and metadata
        texts = [doc['text'] for doc in documents]
        metadata = [{k: v for k, v in doc.items() if k != 'text'} for doc in documents]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        
        # Initialize index if it doesn't exist
        if self.index is None:
            self.index = faiss.IndexFlatIP(self.config.EMBEDDING_DIMENSION)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings.astype('float32'))
        
        # Store documents and metadata
        self.documents.extend(texts)
        self.metadata.extend(metadata)
        
        print(f"Added {len(documents)} documents to vector store. Total: {len(self.documents)}")
    
    def search(self, query: str, top_k: int = None) -> List[Tuple[str, Dict[str, Any], float]]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of tuples (text, metadata, similarity_score)
        """
        if self.index is None or len(self.documents) == 0:
            return []
        
        if top_k is None:
            top_k = self.config.TOP_K_RESULTS
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.documents):
                results.append((
                    self.documents[idx],
                    self.metadata[idx],
                    float(score)
                ))
        
        return results
    
    def save(self, file_path: str = None) -> None:
        """Save the vector store to disk"""
        if file_path is None:
            file_path = self.config.VECTOR_STORE_PATH
        
        if self.index is None:
            print("No index to save")
            return
        
        # Save FAISS index
        faiss.write_index(self.index, f"{file_path}.index")
        
        # Save documents and metadata
        with open(f"{file_path}.pkl", 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata
            }, f)
        
        print(f"Vector store saved to {file_path}")
    
    def load(self, file_path: str = None) -> bool:
        """Load the vector store from disk"""
        if file_path is None:
            file_path = self.config.VECTOR_STORE_PATH
        
        index_path = f"{file_path}.index"
        data_path = f"{file_path}.pkl"
        
        if not os.path.exists(index_path) or not os.path.exists(data_path):
            print(f"Vector store files not found at {file_path}")
            return False
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(index_path)
            
            # Load documents and metadata
            with open(data_path, 'rb') as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.metadata = data['metadata']
            
            print(f"Vector store loaded from {file_path}. Documents: {len(self.documents)}")
            return True
            
        except Exception as e:
            print(f"Error loading vector store: {str(e)}")
            return False
    
    def clear(self) -> None:
        """Clear the vector store"""
        self.index = None
        self.documents = []
        self.metadata = []
        print("Vector store cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        return {
            'total_documents': len(self.documents),
            'embedding_dimension': self.config.EMBEDDING_DIMENSION,
            'embedding_model': self.config.EMBEDDING_MODEL,
            'index_type': 'FAISS IndexFlatIP' if self.index else 'None'
        }
