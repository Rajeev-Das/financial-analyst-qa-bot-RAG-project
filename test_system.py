"""
Test script for the Financial Q&A Bot system
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from financial_qa_bot import FinancialQABot

def test_system():
    """Test the basic functionality of the system"""
    print("🧪 Testing Financial Q&A Bot System")
    print("=" * 50)
    
    # Initialize bot
    print("1. Initializing bot...")
    bot = FinancialQABot()
    print("✓ Bot initialized")
    
    # Test document processing
    print("\n2. Testing document processing...")
    xbrl_file = "data/aapl-20240928_htm.xml"
    
    if os.path.exists(xbrl_file):
        print(f"   Processing {xbrl_file}...")
        result = bot.process_document(xbrl_file)
        
        if result['success']:
            print(f"✓ {result['message']}")
            print(f"  Chunks processed: {result['chunks_count']}")
            
            # Initialize RAG pipeline
            bot.initialize_rag_pipeline()
            print("✓ RAG pipeline initialized")
            
            # Test vector store stats
            stats = bot.get_vector_store_stats()
            print(f"✓ Vector store stats: {stats['total_documents']} documents")
            
            # Test question answering
            print("\n3. Testing question answering...")
            test_questions = [
                "What is Apple's revenue?",
                "What are the main business segments?",
                "What is the company's market share?"
            ]
            
            for question in test_questions:
                print(f"\n   Question: {question}")
                result = bot.ask_question(question)
                
                if result['success']:
                    print(f"   ✓ Answer: {result['answer'][:100]}...")
                    print(f"   ✓ Confidence: {result['confidence']:.2f}")
                    print(f"   ✓ Sources used: {result['context_used']}")
                else:
                    print(f"   ✗ Error: {result['message']}")
            
            # Test vector store saving
            print("\n4. Testing vector store persistence...")
            bot.save_vector_store()
            print("✓ Vector store saved")
            
            print("\n🎉 All tests passed! System is working correctly.")
            
        else:
            print(f"✗ Document processing failed: {result['message']}")
    else:
        print(f"✗ Test file not found: {xbrl_file}")
        print("   Please ensure the AAPL XBRL file is in the data directory")

if __name__ == "__main__":
    test_system()
