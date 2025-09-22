"""
Main Financial Q&A Bot application
"""
import os
import streamlit as st

from typing import Dict, Any
from config import Config
from document_processor import DocumentProcessor
from vector_store import VectorStore
from rag_pipeline import RAGPipeline

class FinancialQABot:
    """Main application class for the Financial Q&A Bot"""
    
    def __init__(self):
        self.config = Config()
        self.document_processor = DocumentProcessor()
        self.vector_store = VectorStore()
        self.rag_pipeline = None
        
    def initialize_rag_pipeline(self):
        """Initialize the RAG pipeline"""
        if self.rag_pipeline is None:
            self.rag_pipeline = RAGPipeline(self.vector_store)
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process a document and add it to the vector store"""
        try:
            # Process the document
            chunks = self.document_processor.process_document(file_path)
            
            if not chunks:
                return {
                    'success': False,
                    'message': 'No content could be extracted from the document'
                }
            
            # Add to vector store
            self.vector_store.add_documents(chunks)
            
            return {
                'success': True,
                'message': f'Successfully processed {len(chunks)} chunks from {os.path.basename(file_path)}',
                'chunks_count': len(chunks)
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error processing document: {str(e)}'
            }
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """Ask a question and get an answer"""
        if not self.rag_pipeline:
            return {
                'success': False,
                'message': 'RAG pipeline not initialized. Please process a document first.'
            }
        
        try:
            result = self.rag_pipeline.query(question)
            return {
                'success': True,
                **result
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error processing question: {str(e)}'
            }
    
    def get_vector_store_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        return self.vector_store.get_stats()
    
    def save_vector_store(self):
        """Save the vector store to disk"""
        self.vector_store.save()
    
    def load_vector_store(self) -> bool:
        """Load the vector store from disk"""
        return self.vector_store.load()

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title=Config.PAGE_TITLE,
        page_icon=Config.PAGE_ICON,
        layout="wide"
    )
    
    st.title("📊 Financial Analyst Q&A Bot")
    st.markdown("Ask questions about financial documents using AI-powered retrieval and generation")
    
    # Initialize session state
    if 'bot' not in st.session_state:
        st.session_state.bot = FinancialQABot()
    
    if 'vector_store_loaded' not in st.session_state:
        st.session_state.vector_store_loaded = False
    
    bot = st.session_state.bot
    
    # Sidebar for document upload
    with st.sidebar:
        st.header("📁 Document Management")
        
        # Try to load existing vector store
        if not st.session_state.vector_store_loaded:
            if st.button("Load Existing Vector Store"):
                with st.spinner("Loading vector store..."):
                    if bot.load_vector_store():
                        st.success("Vector store loaded successfully!")
                        st.session_state.vector_store_loaded = True
                        bot.initialize_rag_pipeline()
                    else:
                        st.warning("No existing vector store found")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload Financial Document",
            type=['pdf', 'xml', 'htm'],
            help="Upload a 10-K report (PDF) or XBRL filing (XML/HTM)"
        )
        
        if uploaded_file is not None:
            # Save uploaded file
            file_path = os.path.join(Config.DATA_DIRECTORY, uploaded_file.name)
            os.makedirs(Config.DATA_DIRECTORY, exist_ok=True)
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Process document
            if st.button("Process Document"):
                with st.spinner("Processing document..."):
                    result = bot.process_document(file_path)
                    
                    if result['success']:
                        st.success(result['message'])
                        st.session_state.vector_store_loaded = True
                        bot.initialize_rag_pipeline()
                        
                        # Save vector store
                        bot.save_vector_store()
                    else:
                        st.error(result['message'])
        
        # Vector store stats
        if st.session_state.vector_store_loaded:
            st.header("📊 Vector Store Stats")
            stats = bot.get_vector_store_stats()
            st.json(stats)
    
    # Main content area
    if not st.session_state.vector_store_loaded:
        st.info("👈 Please upload and process a document to get started")
        
        # Show sample questions
        st.header("💡 Sample Questions You Can Ask")
        sample_questions = [
            "What were the main risks cited in the report?",
            "How much was spent on R&D in the last fiscal year?",
            "What is the company's revenue for the current year?",
            "What are the key financial metrics mentioned?",
            "What is the company's debt structure?",
            "What are the main business segments?",
            "What is the company's market share?",
            "What are the recent acquisitions or divestitures?"
        ]
        
        for i, question in enumerate(sample_questions, 1):
            st.write(f"{i}. {question}")
    
    else:
        # Chat interface
        st.header("💬 Ask Questions")
        
        # Question input
        question = st.text_input(
            "Enter your question:",
            placeholder="e.g., What were the main risks cited in the report?"
        )
        
        if st.button("Ask Question") and question:
            with st.spinner("Thinking..."):
                result = bot.ask_question(question)
                
                if result['success']:
                    # Display answer
                    st.subheader("🤖 Answer")
                    st.write(result['answer'])
                    
                    # Display confidence
                    confidence = result['confidence']
                    confidence_color = "green" if confidence > 0.7 else "orange" if confidence > 0.4 else "red"
                    st.markdown(f"**Confidence:** :{confidence_color}[{confidence:.2f}]")
                    
                    # Display sources
                    if result['sources']:
                        st.subheader("📚 Sources")
                        for i, source in enumerate(result['sources'], 1):
                            with st.expander(f"Source {i} (Similarity: {source['similarity_score']:.3f})"):
                                st.write("**Preview:**")
                                st.write(source['text_preview'])
                                st.write("**Metadata:**")
                                st.json(source['metadata'])
                else:
                    st.error(result['message'])
        
        # Batch questions
        st.header("📝 Batch Questions")
        batch_questions = st.text_area(
            "Enter multiple questions (one per line):",
            height=100,
            placeholder="What were the main risks?\nHow much was spent on R&D?\nWhat is the revenue?"
        )
        
        if st.button("Process Batch Questions") and batch_questions:
            questions = [q.strip() for q in batch_questions.split('\n') if q.strip()]
            
            if questions:
                with st.spinner("Processing batch questions..."):
                    results = []
                    for question in questions:
                        result = bot.ask_question(question)
                        results.append({
                            'question': question,
                            **result
                        })
                    
                    # Display results
                    for result in results:
                        st.subheader(f"❓ {result['question']}")
                        if result['success']:
                            st.write(result['answer'])
                            st.markdown(f"**Confidence:** {result['confidence']:.2f}")
                        else:
                            st.error(result['message'])
                        st.divider()

if __name__ == "__main__":
    main()
