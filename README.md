# Financial Analyst Q&A Bot - RAG Project

A sophisticated AI-powered Q&A system that can answer specific questions about company financial reports (10-K filings) using Retrieval-Augmented Generation (RAG).

## 🎯 Project Overview

This project solves a real business problem: financial analysts need to quickly find specific information from hundreds-page-long 10-K reports. Our solution uses RAG to:

1. **Load & Chunk**: Split financial documents into manageable text chunks
2. **Embed & Store**: Convert chunks to embeddings and store in a vector database
3. **Retrieve**: Find relevant chunks when you ask questions
4. **Generate**: Use LLM to synthesize accurate answers from retrieved information

## 🚀 Features

- **Multi-format Support**: Handles both PDF 10-K reports and XBRL filings
- **Intelligent Chunking**: Optimized text splitting for financial documents
- **Vector Search**: Fast similarity search using FAISS
- **RAG Pipeline**: Combines retrieval and generation for accurate answers
- **Web Interface**: User-friendly Streamlit app
- **CLI Interface**: Command-line tool for batch processing
- **Confidence Scoring**: Provides confidence levels for answers

## 📋 Requirements

- Python 3.10+
- OpenAI API key
- Required packages (see requirements.txt)

## 🛠️ Installation

### Using Poetry (Recommended)
```bash
poetry install
```

### Using pip
```bash
pip install -r requirements.txt
```

## 🔧 Setup

1. **Set up environment variables**:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

2. **Create .env file** (optional):
   ```
   OPENAI_API_KEY=your-openai-api-key
   ```

## 📖 Usage

### Web Interface (Streamlit)

```bash
streamlit run src/financial_qa_bot.py
```

1. Upload a financial document (PDF or XBRL)
2. Process the document to build the vector store
3. Ask questions in natural language
4. View answers with confidence scores and sources

### Command Line Interface

```bash
# Process a document
python src/cli.py --file data/aapl-10k.pdf

# Ask a question
python src/cli.py --question "What were the main risks cited in the report?"

# Interactive mode
python src/cli.py --interactive

# Load existing vector store
python src/cli.py --load-store --interactive
```

### Example Questions

- "What were the main risks cited in the report?"
- "How much was spent on R&D in the last fiscal year?"
- "What is the company's revenue for the current year?"
- "What are the key financial metrics mentioned?"
- "What is the company's debt structure?"
- "What are the main business segments?"

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Document      │    │   Vector Store   │    │   RAG Pipeline  │
│   Processor     │───▶│   (FAISS)        │───▶│   (Retrieve +   │
│   (PDF/XBRL)   │    │   Embeddings     │    │    Generate)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Components

- **DocumentProcessor**: Handles PDF and XBRL file parsing
- **VectorStore**: Manages embeddings and similarity search
- **RAGPipeline**: Combines retrieval and generation
- **FinancialQABot**: Main application orchestrator

## 📊 Data Processing

### PDF Processing
- Extracts text from PDF pages
- Cleans and chunks text optimally
- Preserves page and source information

### XBRL Processing
- Parses structured financial data
- Groups facts by category (us-gaap, dei, etc.)
- Formats data into readable text chunks

## 🔍 Vector Search

- Uses sentence-transformers for embeddings
- FAISS for fast similarity search
- Cosine similarity for relevance scoring
- Configurable chunk size and overlap

## 🤖 LLM Integration

- OpenAI GPT models for answer generation
- Context-aware prompting for financial analysis
- Confidence scoring based on retrieval quality
- Source attribution and citation

## 📁 Project Structure

```
financial-analyst-qa-bot-RAG-project/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── document_processor.py  # PDF/XBRL processing
│   ├── vector_store.py        # Embedding and search
│   ├── rag_pipeline.py        # RAG implementation
│   ├── financial_qa_bot.py    # Main Streamlit app
│   └── cli.py                 # Command-line interface
├── data/                      # Document storage
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Poetry configuration
└── README.md                  # This file
```

## 🎯 Sample Data

The project includes a sample AAPL 10-K XBRL filing for testing:
- `data/aapl-20240928_htm.xml` - Apple's 10-K filing
- `data/aapl-10k-facts.csv` - Extracted financial facts

## 🔧 Configuration

Key settings in `src/config.py`:
- `CHUNK_SIZE`: Text chunk size (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- `TOP_K_RESULTS`: Number of relevant chunks to retrieve (default: 5)
- `EMBEDDING_MODEL`: Sentence transformer model (default: all-MiniLM-L6-v2)

## 🚀 Advanced Usage

### Custom Embedding Models
```python
# In config.py
EMBEDDING_MODEL = "all-mpnet-base-v2"  # More accurate but slower
```

### Batch Processing
```python
# Process multiple documents
bot = FinancialQABot()
for file in document_files:
    bot.process_document(file)
bot.save_vector_store()
```

### Custom Questions
```python
# Ask programmatic questions
result = bot.ask_question("What is the company's market share?")
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']}")
```

## 🐛 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure `OPENAI_API_KEY` is set in environment
   - Check API key validity and credits

2. **Document Processing Errors**
   - Verify file format is supported (PDF, XML, HTM)
   - Check file is not corrupted
   - Ensure sufficient disk space

3. **Vector Store Issues**
   - Delete `vector_store.faiss*` files to rebuild
   - Check FAISS installation

### Performance Tips

- Use smaller embedding models for faster processing
- Adjust chunk size based on document type
- Limit context length for faster responses

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Hugging Face for sentence transformers
- FAISS for vector search
- Streamlit for web interface

---

**Built with ❤️ for financial analysts and AI enthusiasts**
