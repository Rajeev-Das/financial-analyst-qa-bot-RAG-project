"""
Setup script to help configure OpenAI API key
"""
import os

def setup_api_key():
    """Interactive setup for OpenAI API key"""
    print("🔑 OpenAI API Key Setup")
    print("=" * 40)
    
    # Check if already set
    if os.getenv('OPENAI_API_KEY'):
        print("✅ OPENAI_API_KEY is already set!")
        return True
    
    print("Please choose how to set your OpenAI API key:")
    print("1. Set environment variable for current session")
    print("2. Create .env file")
    print("3. Enter API key interactively")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        api_key = input("Enter your OpenAI API key: ").strip()
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            print("✅ API key set for current session!")
            print("Note: This will only last for this terminal session.")
            return True
    
    elif choice == "2":
        api_key = input("Enter your OpenAI API key: ").strip()
        if api_key:
            with open('.env', 'w') as f:
                f.write(f"OPENAI_API_KEY={api_key}\n")
            print("✅ API key saved to .env file!")
            return True
    
    elif choice == "3":
        api_key = input("Enter your OpenAI API key: ").strip()
        if api_key:
            print(f"\nTo set this permanently, run:")
            print(f"export OPENAI_API_KEY='{api_key}'")
            print(f"\nOr add it to your shell profile (.bashrc, .zshrc, etc.)")
            return True
    
    else:
        print("❌ Invalid choice")
        return False

if __name__ == "__main__":
    setup_api_key()
