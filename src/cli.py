"""
Command-line interface for the Financial Q&A Bot
"""
import argparse
import os

from financial_qa_bot import FinancialQABot

def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(description="Financial Analyst Q&A Bot")
    parser.add_argument("--file", "-f", help="Path to financial document to process")
    parser.add_argument("--question", "-q", help="Question to ask")
    parser.add_argument("--interactive", "-i", action="store_true", help="Start interactive mode")
    parser.add_argument("--load-store", action="store_true", help="Load existing vector store")
    
    args = parser.parse_args()
    
    # Initialize bot
    bot = FinancialQABot()
    
    # Load existing vector store if requested
    if args.load_store:
        print("Loading existing vector store...")
        if bot.load_vector_store():
            print("✓ Vector store loaded successfully")
            bot.initialize_rag_pipeline()
        else:
            print("✗ No existing vector store found")
            return
    
    # Process file if provided
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File {args.file} not found")
            return
        
        print(f"Processing document: {args.file}")
        result = bot.process_document(args.file)
        
        if result['success']:
            print(f"✓ {result['message']}")
            bot.initialize_rag_pipeline()
            bot.save_vector_store()
        else:
            print(f"✗ {result['message']}")
            return
    
    # Ask question if provided
    if args.question:
        if not bot.rag_pipeline:
            print("Error: No documents processed. Please provide a file first.")
            return
        
        print(f"Question: {args.question}")
        print("Thinking...")
        
        result = bot.ask_question(args.question)
        
        if result['success']:
            print(f"\nAnswer: {result['answer']}")
            print(f"Confidence: {result['confidence']:.2f}")
            print(f"Sources used: {result['context_used']}")
        else:
            print(f"Error: {result['message']}")
    
    # Interactive mode
    if args.interactive:
        print("\n🤖 Financial Q&A Bot - Interactive Mode")
        print("Type 'quit' to exit, 'stats' for vector store statistics")
        
        if not bot.rag_pipeline:
            print("No documents loaded. Please process a document first.")
            return
        
        while True:
            try:
                question = input("\n❓ Your question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if question.lower() == 'stats':
                    stats = bot.get_vector_store_stats()
                    print(f"Vector Store Stats: {stats}")
                    continue
                
                if not question:
                    continue
                
                print("Thinking...")
                result = bot.ask_question(question)
                
                if result['success']:
                    print(f"\n🤖 Answer: {result['answer']}")
                    print(f"📊 Confidence: {result['confidence']:.2f}")
                    print(f"📚 Sources used: {result['context_used']}")
                else:
                    print(f"❌ Error: {result['message']}")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
