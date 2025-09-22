"""
Demo script for the Financial Q&A Bot
This script demonstrates the core functionality without requiring OpenAI API key
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from document_processor import DocumentProcessor
from vector_store import VectorStore

def demo_document_processing():
    """Demonstrate document processing and search capabilities"""
    print("🚀 Financial Q&A Bot Demo")
    print("=" * 60)
    print("This demo shows how the system processes financial documents")
    print("and performs semantic search without requiring OpenAI API key.")
    print()
    
    # Initialize components
    print("📋 Initializing components...")
    processor = DocumentProcessor()
    vector_store = VectorStore()
    print("✓ Components initialized")
    
    # Process the AAPL 10-K XBRL file
    xbrl_file = "data/aapl-20240928_htm.xml"
    print(f"\n📄 Processing document: {xbrl_file}")
    
    if not os.path.exists(xbrl_file):
        print(f"❌ File not found: {xbrl_file}")
        print("Please ensure the AAPL XBRL file is in the data directory")
        return
    
    # Process document
    chunks = processor.process_document(xbrl_file)
    print(f"✓ Processed {len(chunks)} text chunks")
    
    # Add to vector store
    vector_store.add_documents(chunks)
    print(f"✓ Added {len(chunks)} documents to vector store")
    
    # Demonstrate search capabilities
    print("\n🔍 Demonstrating semantic search capabilities:")
    print("-" * 50)
    
    demo_queries = [
        "revenue",
        "research and development",
        "debt",
        "market share",
        "risk factors",
        "cash flow",
        "inventory",
        "employees"
    ]
    
    for query in demo_queries:
        print(f"\n🔎 Searching for: '{query}'")
        results = vector_store.search(query, top_k=2)
        
        if results:
            for i, (text, metadata, score) in enumerate(results, 1):
                print(f"   Result {i} (similarity: {score:.3f}):")
                print(f"   📊 Category: {metadata.get('category', 'N/A')}")
                print(f"   📝 Preview: {text[:150]}...")
                print()
        else:
            print("   No results found")
    
    # Show vector store statistics
    print("\n📊 Vector Store Statistics:")
    print("-" * 30)
    stats = vector_store.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n🎉 Demo completed successfully!")
    print("\n💡 Next steps:")
    print("   1. Set your OPENAI_API_KEY environment variable")
    print("   2. Run: streamlit run src/financial_qa_bot.py")
    print("   3. Upload documents and ask questions!")
    print("   4. Or use CLI: python src/cli.py --interactive")

if __name__ == "__main__":
    demo_document_processing()
