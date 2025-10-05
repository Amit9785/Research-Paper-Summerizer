# 📚 Research Document Summarizer (RAG System)

**Created by:** Amit, Naman, Shivangi

## 📋 Project Overview

This is a Retrieval-Augmented Generation (RAG) system that allows users to upload PDF documents and interact with them through an intelligent chatbot interface. The system uses advanced natural language processing to understand and answer questions about your documents.

## 🎯 Key Features

- ✅ **PDF Upload** - Upload PDFs locally or via URLs (including arXiv papers)
- ✅ **AI-Powered Chat** - Intelligent chat interface using Groq API with Llama models
- ✅ **Vector Search** - Fast and accurate search using FAISS and HuggingFace embeddings
- ✅ **Modern Web Interface** - Beautiful and responsive Streamlit web interface
- ✅ **Document Processing** - Automatic text extraction and chunking for optimal retrieval

## 🏗️ Architecture

The system uses a RAG (Retrieval-Augmented Generation) architecture that combines:
- **Vector Database** (FAISS) for efficient document retrieval
- **Embeddings** (sentence-transformers) for semantic understanding
- **LLM** (Groq Llama) for natural language generation

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd RAG_Research_summerizer
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables

Create a `.env` file in the project root with the following configuration:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL_NAME=llama-3.1-8b-instant
TEMPERATURE=0.3
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=2000
CHUNK_OVERLAP=200
SIMILARITY_SEARCH_K=2
```

### 5. Get Groq API Key

1. Visit: [https://console.groq.com/](https://console.groq.com/)
2. Sign up for a free account
3. Generate an API key
4. Add it to your `.env` file

### 6. Run the Application

```bash
streamlit run main.py
```

The application will open in your default web browser at `http://localhost:8501`

## 🚀 Usage

1. **Start the application**: Run `streamlit run main.py`
2. **Upload documents**: Use the sidebar to upload PDFs or enter URLs
3. **Process documents**: Click "Process PDF" to create the vector index
4. **Chat**: Ask questions about your documents using the chat interface

## 📁 Project Structure

```
RAG_Research_summerizer/
├── app.py                 # Application logic
├── main.py                # Entry point
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not tracked)
├── Flow_Diagram.png       # System architecture diagram
├── config/                # Configuration files
├── data/                  # Data storage
├── faiss_index/          # FAISS vector index
├── src/                   # Source code
│   ├── ui_components.py  # UI components
│   └── pdf_processor.py  # PDF processing logic
└── utils/                 # Utility functions
```

## 🛠️ Technologies Used

- **Streamlit** - Web interface framework
- **LangChain** - LLM framework for RAG implementation
- **FAISS** - Vector similarity search
- **Groq** - Fast LLM inference
- **Sentence Transformers** - Text embeddings
- **PyPDF2** - PDF text extraction

## 🐛 Troubleshooting

### Common Issues

**ModuleNotFoundError**
- Solution: Make sure you've activated the virtual environment and installed all dependencies

**"Model decommissioned" error**
- Solution: Update the `GROQ_MODEL_NAME` in your `.env` file to a currently available model

**"No text extracted" error**
- Solution: Check if the PDF is corrupted or password-protected

**"FAISS index not found" error**
- Solution: Process at least one PDF first before trying to chat

**API Key errors**
- Solution: Verify your Groq API key is correctly set in the `.env` file

## 📝 License

This project is created for educational purposes.

## 👥 Contributors

- Amit
- Naman
- Shivangi

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## 📧 Contact

For questions or support, please reach out to the project creators.

---

**Note:** Make sure to keep your API keys secure and never commit them to version control!
