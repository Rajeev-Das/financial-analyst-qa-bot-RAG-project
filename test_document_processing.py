"""
Test script for document processing without requiring OpenAI API
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from document_processor import DocumentProcessor
from vector_store import VectorStore

def test_document_processing():
    """Test document processing and vector store functionality"""
    print("🧪 Testing Document Processing")
    print("=" * 50)
    
    # Test document processor
    print("1. Testing document processor...")
    processor = DocumentProcessor()
    print("✓ Document processor initialized")
    
    # Test XBRL processing
    xbrl_file = "data/aapl-20240928_htm.xml"
    if os.path.exists(xbrl_file):
        print(f"\n2. Processing XBRL file: {xbrl_file}")
        try:
            chunks = processor.process_document(xbrl_file)
            print(f"✓ Successfully processed {len(chunks)} chunks")
            
            # Show sample chunks
            print("\n3. Sample chunks:")
            for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                print(f"   Chunk {i+1}:")
                print(f"   - Text preview: {chunk['text'][:100]}...")
                print(f"   - Document type: {chunk['document_type']}")
                print(f"   - Category: {chunk.get('category', 'N/A')}")
                print()
            
            # Test vector store
            print("4. Testing vector store...")
            vector_store = VectorStore()
            vector_store.add_documents(chunks)
            print(f"✓ Added {len(chunks)} documents to vector store")
            
            # Test search
            print("\n5. Testing vector search...")
            test_query = "revenue"
            results = vector_store.search(test_query, top_k=3)
            print(f"✓ Search for '{test_query}' returned {len(results)} results")
            
            for i, (text, metadata, score) in enumerate(results):
                print(f"   Result {i+1} (score: {score:.3f}):")
                print(f"   - Preview: {text[:100]}...")
                print(f"   - Category: {metadata.get('category', 'N/A')}")
                print()
            
            # Test vector store stats
            stats = vector_store.get_stats()
            print(f"✓ Vector store stats: {stats}")
            
            print("\n🎉 Document processing test passed!")
            
        except Exception as e:
            print(f"✗ Error processing document: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print(f"✗ Test file not found: {xbrl_file}")

if __name__ == "__main__":
    test_document_processing()
