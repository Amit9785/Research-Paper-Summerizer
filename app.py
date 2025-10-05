import streamlit as st
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
import requests
import tempfile
import os
from dotenv import load_dotenv
load_dotenv()

# ----------------- Streamlit Setup -----------------
st.set_page_config(
    page_title="PDF AI Summarizer & Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Card styling for chat messages */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        border: 2px dashed #667eea;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 10px;
        border-left: 5px solid #667eea;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: white;
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Chat input */
    .stChatInput {
        border-radius: 25px;
    }
    
    /* Status messages */
    .status-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    </style>
""", unsafe_allow_html=True)

# Header with improved design
st.markdown("""
    <div class="main-header">
        <h1>🤖 PDF AI Summarizer & Chat</h1>
        <p>Upload PDFs, extract insights, and chat with your documents using AI</p>
    </div>
""", unsafe_allow_html=True)

# ----------------- Helper Functions -----------------
def get_pdf_text(pdf_files):
    """Extract text from uploaded PDFs"""
    text = ""
    for pdf in pdf_files:
        try:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                if page.extract_text():
                    text += page.extract_text()
        except Exception as e:
            st.error(f"Error reading {pdf.name}: {e}")
    return text

def get_text_chunks(text):
    """Split long text into smaller chunks"""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    return text_splitter.split_text(text)

@st.cache_resource
def get_vector_store(text_chunks):
    """Convert chunks into embeddings and store in FAISS"""
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")
    return vector_store

def get_conversational_chain():
    """Build QA chain with Groq LLM"""
    prompt_template = """
    You are a helpful PDF assistant. Use the provided context to answer the user's questions.
    If the answer is not in the provided context, just say, 
    "answer is not available in the provided context." 
    Do not provide a wrong answer.

    Chat History:
    {chat_history}

    Context: {context}
    Question: {question}
    Answer:
    """
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="openai/gpt-oss-20b",
        temperature=0.3,
    )
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question", "chat_history"])
    return load_qa_chain(llm=llm, chain_type="stuff", prompt=prompt)

def user_input(user_question, chat_history):
    """Handle user query against FAISS index and maintain chat history"""
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    index_path = "faiss_index"
    if not os.path.exists(index_path):
        st.error("FAISS index not found. Please process a PDF first.")
        return ""
    vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    docs = vector_store.similarity_search(user_question, k=2)  # Limit to top 2 chunks
    chain = get_conversational_chain()
    # Format chat history as a string
    chat_history_str = ""
    for entry in chat_history:
        chat_history_str += f"User: {entry['user']}\nAssistant: {entry['assistant']}\n"
    response = chain(
        {
            "input_documents": docs,
            "question": user_question,
            "chat_history": chat_history_str
        },
        return_only_outputs=True
    )
    return response["output_text"]

def download_pdf_from_url(url):
    """Download PDF from online link and return local file path"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            tmp_pdf.write(response.content)
            return tmp_pdf.name
    except Exception as e:
        st.error(f"Failed to download PDF: {e}")
        return None

# ----------------- Streamlit UI -----------------
with st.sidebar:
    st.markdown("### 📂 Upload & Process PDFs")
    st.markdown("---")
    
    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["📤 Upload Files", "🔗 From URLs"])
    
    with tab1:
        st.markdown("##### Local PDF Files")
        uploaded_files = st.file_uploader(
            "Drag and drop or click to upload",
            accept_multiple_files=True,
            type=["pdf"],
            help="Upload one or more PDF files"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
            with st.expander("📋 View uploaded files"):
                for i, file in enumerate(uploaded_files, 1):
                    st.text(f"{i}. {file.name}")
    
    with tab2:
        st.markdown("##### PDF URLs")
        pdf_urls_input = st.text_area(
            "Enter URLs (one per line or comma-separated)",
            height=120,
            placeholder="https://example.com/paper1.pdf\nhttps://example.com/paper2.pdf",
            help="Add multiple PDF URLs, separated by commas or newlines"
        )
    
    st.markdown("---")
    
    # Process URLs
    pdf_urls = []
    if pdf_urls_input:
        pdf_urls = [url.strip() for url in pdf_urls_input.replace(',', '\n').split('\n') if url.strip()]

    # Download PDFs from URLs
    url_pdf_files = []
    if pdf_urls:
        with st.expander(f"🔗 {len(pdf_urls)} URL(s) detected"):
            for i, url in enumerate(pdf_urls, 1):
                st.text(f"{i}. {url[:50]}...")

    # Combine all PDFs
    pdf_docs = []
    if uploaded_files:
        pdf_docs.extend(uploaded_files)
    
    # Show summary before processing
    if pdf_docs or pdf_urls:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📄 Files", len(uploaded_files) if uploaded_files else 0)
        with col2:
            st.metric("🔗 URLs", len(pdf_urls))
    
    # Process button with better styling
    process_button = st.button(
        "🚀 Process All PDFs",
        use_container_width=True,
        type="primary"
    )
    
    if process_button and (pdf_docs or pdf_urls):
        # Download PDFs from URLs first
        if pdf_urls:
            progress_bar = st.progress(0)
            st.info("📥 Downloading PDFs from URLs...")
            for idx, url in enumerate(pdf_urls):
                pdf_path = download_pdf_from_url(url)
                if pdf_path:
                    url_pdf_files.append(open(pdf_path, "rb"))
                progress_bar.progress((idx + 1) / len(pdf_urls))
            pdf_docs.extend(url_pdf_files)
        
        if pdf_docs:
            with st.spinner("⚙️ Processing PDFs... Please wait"):
                progress_bar = st.progress(0)
                
                # Extract text
                st.info("📖 Extracting text from PDFs...")
                progress_bar.progress(0.3)
                raw_text = get_pdf_text(pdf_docs)
                
                if raw_text.strip():
                    # Create chunks
                    st.info("✂️ Splitting text into chunks...")
                    progress_bar.progress(0.6)
                    text_chunks = get_text_chunks(raw_text)
                    
                    # Create vector store
                    st.info("🧠 Creating vector embeddings...")
                    progress_bar.progress(0.9)
                    get_vector_store(text_chunks)
                    
                    progress_bar.progress(1.0)
                    st.success("✅ Processing completed successfully!")
                    st.balloons()
                    
                    # Show statistics
                    st.info(f"📊 Processed {len(pdf_docs)} PDF(s) with {len(text_chunks)} text chunks")
                else:
                    st.error("❌ No text could be extracted from the PDFs")
    
    elif process_button:
        st.warning("⚠️ Please upload PDFs or enter URLs first")
    
    st.markdown("---")
    
    # Add helpful tips
    with st.expander("💡 Tips & Help"):
        st.markdown("""
        **How to use:**
        1. Upload PDF files or enter URLs
        2. Click 'Process All PDFs'
        3. Start chatting with your documents
        
        **Features:**
        - 📚 Multiple PDF support
        - 🔗 Direct URL loading
        - 💬 Conversational AI chat
        - 🧠 Context-aware responses
        - 📝 Chat history tracking
        """)
    
    # Show current status
    index_exists = os.path.exists("faiss_index")
    if index_exists:
        st.success("✅ Vector database ready")
    else:
        st.info("ℹ️ No PDFs processed yet")

index_exists = os.path.exists("faiss_index")

# Main chat interface with improved design
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    if index_exists:
        st.markdown("### 💬 Chat with Your Documents")
        st.markdown("Ask questions and get AI-powered answers from your PDFs")
        
        # Quick action buttons for common questions
        st.markdown("#### ⚡ Quick Actions")
        quick_cols = st.columns(5)
        
        quick_questions = [
            ("📋 Summarize", "Please provide a comprehensive summary of the document"),
            ("🎯 Main Topic", "What is the main topic discussed in this document?"),
            ("💡 Key Points", "What are the key points and findings?"),
            ("🔍 Methodology", "Explain the methodology or approach used"),
            ("📊 Conclusions", "What are the main conclusions?")
        ]
        
        for idx, (label, question) in enumerate(quick_questions):
            with quick_cols[idx]:
                if st.button(label, key=f"quick_{idx}", use_container_width=True):
                    # Set the question to be processed
                    st.session_state.pending_question = question
                    st.rerun()
    else:
        st.markdown("### 👋 Welcome!")
        st.info("📌 Upload and process PDFs using the sidebar to get started")
        
        # Show sample questions
        st.markdown("#### 🎯 Example Questions You Can Ask:")
        example_questions = [
            "What is the main topic of this document?",
            "Summarize the key findings",
            "What are the conclusions?",
            "Explain the methodology used",
            "What are the limitations mentioned?"
        ]
        
        cols = st.columns(2)
        for idx, question in enumerate(example_questions):
            with cols[idx % 2]:
                st.markdown(f"- {question}")

st.divider()

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history with improved styling
if st.session_state.chat_history:
    st.markdown("### 📜 Chat History")
    
    for idx, entry in enumerate(st.session_state.chat_history):
        # User message
        with st.container():
            col1, col2 = st.columns([1, 20])
            with col1:
                st.markdown("👤")
            with col2:
                st.markdown(f"**You:** {entry['user']}")
        
        # Assistant message
        with st.container():
            col1, col2 = st.columns([1, 20])
            with col1:
                st.markdown("🤖")
            with col2:
                st.markdown(f"**AI Assistant:**")
                st.info(entry['assistant'])
        
        st.markdown("<br>", unsafe_allow_html=True)

# Chat input and controls
if index_exists:
    # Action buttons
    col1, col2, col3 = st.columns([4, 1, 1])
    
    with col2:
        if st.button("🔄 Clear Chat", use_container_width=True, help="Clear all chat history"):
            st.session_state.chat_history = []
            st.rerun()
    
    with col3:
        if st.button("📊 Stats", use_container_width=True, help="Show statistics"):
            if st.session_state.chat_history:
                st.info(f"💬 Total messages: {len(st.session_state.chat_history) * 2}")
            else:
                st.info("No messages yet")
    
    # Main chat input
    user_query = st.chat_input("💭 Type your question here and press Enter...")
    
    if user_query:
        with st.spinner("🤔 AI is thinking..."):
            try:
                response = user_input(user_query, st.session_state.chat_history)
                
                # Store the new exchange in chat history
                st.session_state.chat_history.append({
                    "user": user_query,
                    "assistant": response
                })
                
                # Rerun to display the new message
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Try rephrasing your question or processing the PDF again")
else:
    st.warning("⚠️ Please process at least one PDF to start chatting")
    
    # Quick start guide
    with st.expander("🚀 Quick Start Guide"):
        st.markdown("""
        ### Getting Started:
        
        1. **Upload PDFs**
           - Use the sidebar to upload local PDF files
           - Or enter PDF URLs directly
        
        2. **Process Documents**
           - Click the 'Process All PDFs' button
           - Wait for the processing to complete
        
        3. **Start Chatting**
           - Ask questions about your documents
           - Get instant AI-powered answers
           - Review your chat history anytime
        
        ### Tips for Best Results:
        - Be specific with your questions
        - You can ask follow-up questions
        - The AI remembers the conversation context
        - Clear chat history to start fresh
        """)
