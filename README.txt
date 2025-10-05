================================================================================
                    RESEARCH DOCU SUMMARIZER (RAG SYSTEM)
                         Created by: Amit, Naman, Shivangi
================================================================================

📋 PROJECT OVERVIEW
================================================================================

This is a Retrieval-Augmented Generation (RAG) system that allows users to upload 
PDF documents and interact with them through an intelligent chatbot interface.

🎯 KEY FEATURES
================================================================================

✅ Upload PDFs locally or via URLs (including arXiv papers)
✅ AI-powered chat interface using Groq API with Llama models
✅ Vector-based search using FAISS and HuggingFace embeddings
✅ Modern Streamlit web interface

🔧 INSTALLATION & SETUP
================================================================================

1. CLONE THE REPOSITORY
   git clone <repository-url>
   cd RAG_Research_summerizer

2. CREATE VIRTUAL ENVIRONMENT
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. INSTALL DEPENDENCIES
   pip install -r requirements.txt

4. SETUP ENVIRONMENT VARIABLES
   Create a .env file in the project root:
   
   GROQ_API_KEY= your_groq_api_key_here
   GROQ_MODEL_NAME=llama-3.1-8b-instant
   TEMPERATURE=0.3
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   CHUNK_SIZE=2000
   CHUNK_OVERLAP=200
   SIMILARITY_SEARCH_K=2

5. GET GROQ API KEY
   • Visit: https://console.groq.com/
   • Sign up for a free account
   • Generate an API key
   • Add it to your .env file

6. RUN THE APPLICATION
   streamlit run main.py

🚀 USAGE
================================================================================

1. Start the app: streamlit run main.py
2. Upload PDFs or enter URLs in the sidebar
3. Click "Process PDF" to create the vector index
4. Chat with your documents using the interface

🛠️ TROUBLESHOOTING
================================================================================

• "ModuleNotFoundError": Activate virtual environment
• "Model decommissioned": Update GROQ_MODEL_NAME in .env
• "No text extracted": Check if PDF is corrupted
• "FAISS index not found": Process a PDF first

================================================================================
                              END OF SETUP GUIDE
================================================================================
