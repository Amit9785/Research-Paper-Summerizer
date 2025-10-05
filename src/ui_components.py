import streamlit as st
import requests
import tempfile
import os
from typing import List, BinaryIO, Optional
from config.settings import UI_CONFIG
from src.pdf_processor import process_pdfs
from src.vector_store import vector_store_manager
from src.chat_handler import chat_handler
from utils.file_utils import download_pdf_from_url, search_arxiv

def setup_page_config():
    """Setup Streamlit page configuration"""
    st.set_page_config(
        page_title=UI_CONFIG["page_title"],
        page_icon=UI_CONFIG["page_icon"],
        layout=UI_CONFIG["layout"],
        initial_sidebar_state="expanded"
    )
    
    # Enhanced Custom CSS - Respects light/dark mode
    st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Global Styling */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        /* Main header with gradient - always has white text */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
            margin-bottom: 2rem;
            text-align: center;
            animation: fadeIn 0.6s ease-in;
        }
        
        .main-header h1 {
            color: white !important;
            font-size: 3rem;
            font-weight: 700;
            margin: 0;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
            letter-spacing: -0.5px;
        }
        
        .main-header p {
            color: white !important;
            font-size: 1.2rem;
            margin-top: 0.8rem;
            font-weight: 500;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        }
        
        .creator-badge {
            background: rgba(255,255,255,0.25);
            padding: 0.5rem 1.5rem;
            border-radius: 50px;
            margin-top: 1rem;
            display: inline-block;
            color: white !important;
            font-weight: 600;
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255,255,255,0.3);
        }
        
        /* Sidebar styling - let Streamlit handle colors */
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 2rem;
        }
        
        /* Improve heading visibility */
        h1, h2, h3, h4, h5, h6 {
            font-weight: 700 !important;
        }
        
        /* Tab styling - respect theme */
        .stTabs [data-baseweb="tab"] {
            font-weight: 600 !important;
            border-radius: 10px;
            padding: 0.75rem 1.5rem;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
        }
        
        /* Enhanced buttons - always white text on gradient */
        .stButton>button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 1.5rem;
            font-weight: 600 !important;
            font-size: 1rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            width: 100%;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
        }
        
        .stButton>button:active {
            transform: translateY(0);
        }
        
        /* File uploader styling */
        [data-testid="stFileUploader"] {
            border-radius: 15px;
            padding: 1.5rem;
            border: 2px dashed #667eea;
            transition: all 0.3s ease;
        }
        
        [data-testid="stFileUploader"]:hover {
            border-color: #764ba2;
        }
        
        /* Text area and input - let theme handle colors */
        .stTextArea textarea,
        .stTextInput input {
            border-radius: 12px;
            border: 2px solid rgba(102, 126, 234, 0.3);
            padding: 1rem;
            font-size: 0.95rem;
            transition: all 0.3s ease;
        }
        
        .stTextArea textarea:focus,
        .stTextInput input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        /* Chat messages - let theme handle colors */
        .stChatMessage {
            border-radius: 15px;
            padding: 1.2rem;
            margin: 0.8rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            animation: slideIn 0.3s ease;
        }
        
        /* Info/success/warning boxes - enhanced */
        .stAlert {
            border-radius: 12px;
            border: none;
            padding: 1rem 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            font-weight: 500 !important;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            border-radius: 12px;
            font-weight: 600 !important;
            padding: 1rem;
            transition: all 0.3s ease;
        }
        
        .streamlit-expanderHeader:hover {
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
        }
        
        /* Chat input */
        .stChatInput {
            border-radius: 25px;
            border: 2px solid rgba(102, 126, 234, 0.3);
            padding: 0.5rem;
        }
        
        .stChatInput:focus-within {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        /* Metrics - use accent color */
        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: #667eea !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-weight: 600 !important;
        }
        
        /* Progress bars */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
        }
        
        /* Divider */
        hr {
            margin: 2rem 0;
            border: none;
            height: 1px;
            opacity: 0.3;
        }
        
        /* Container styling */
        [data-testid="stContainer"] {
            border-radius: 15px;
        }
        
        /* Spinner */
        .stSpinner > div {
            border-color: #667eea #667eea #667eea transparent !important;
        }
        
        /* Download button - white text on gradient */
        .stDownloadButton button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            font-weight: 600 !important;
            border-radius: 10px;
        }
        
        /* Improve label visibility - bold but respect theme color */
        label {
            font-weight: 600 !important;
        }
        
        /* Animations */
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-10px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        /* Caption text - slight transparency */
        .stCaption {
            font-weight: 500 !important;
            opacity: 0.8;
        }
        
        /* Markdown bold text */
        .stMarkdown strong,
        .stMarkdown b {
            font-weight: 700 !important;
        }
        
        /* Number input */
        .stNumberInput input {
            border-radius: 10px;
            border: 2px solid rgba(102, 126, 234, 0.3);
        }
        
        /* Checkbox and radio */
        .stCheckbox label,
        .stRadio label {
            font-weight: 500 !important;
        }
        
        /* Remove forced background colors to respect theme */
        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(102, 126, 234, 0.2);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Beautiful animated header
    st.markdown(
        f"""
        <div class="main-header">
            <h1>{UI_CONFIG["page_icon"]} {UI_CONFIG["page_title"]}</h1>
            <p>📚 Upload research papers, extract insights, and chat with AI-powered intelligence</p>
            <div class="creator-badge">✨ Created by: {UI_CONFIG["creator"]}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_sidebar() -> List[BinaryIO]:
    """Render sidebar for PDF upload and processing"""
    with st.sidebar:
        st.markdown("### 📂 Document Management")
        st.markdown("---")
        
        # Create tabs for better organization
        tab1, tab2, tab3 = st.tabs(["📤 Upload", "🔗 URLs", "🔬 arXiv"])
        
        uploaded_files = None
        pdf_urls_input = None
        
        # Tab 1: File Upload
        with tab1:
            st.markdown("##### 📁 Local PDF Files")
            uploaded_files = st.file_uploader(
                "Drag and drop or browse",
                accept_multiple_files=True,
                type=["pdf"],
                help="Upload one or more PDF files from your computer",
                label_visibility="collapsed"
            )
            
            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)} file(s) ready")
                with st.expander("📋 View files", expanded=False):
                    for i, file in enumerate(uploaded_files, 1):
                        file_size = file.size / 1024 / 1024  # Convert to MB
                        st.markdown(f"**{i}.** `{file.name}` ({file_size:.2f} MB)")
        
        # Tab 2: URL Input
        with tab2:
            st.markdown("##### 🌐 Enter PDF URLs")
            pdf_urls_input = st.text_area(
                "URLs",
                height=150,
                placeholder="https://arxiv.org/pdf/2301.00001.pdf\nhttps://example.com/paper.pdf",
                help="Enter PDF URLs, one per line or comma-separated",
                label_visibility="collapsed"
            )
            
            if pdf_urls_input:
                url_count = len([url.strip() for url in pdf_urls_input.replace(',', '\n').split('\n') if url.strip()])
                st.info(f"🔗 {url_count} URL(s) detected")

        # Tab 3: arXiv Search
        with tab3:
            st.markdown("##### 🔍 Search Research Papers")
            
            # Initialize session state
            if "arxiv_search_results" not in st.session_state:
                st.session_state["arxiv_search_results"] = []
            if "selected_arxiv_pdfs" not in st.session_state:
                st.session_state["selected_arxiv_pdfs"] = []
            
            col1, col2 = st.columns([3, 1])
            with col1:
                search_query = st.text_input(
                    "Search query",
                    placeholder="e.g., 'transformers NLP'",
                    help="Search for papers on arXiv",
                    label_visibility="collapsed"
                )
            with col2:
                max_results = st.number_input("Max", 1, 20, 5, label_visibility="collapsed")
            
            if st.button("🔎 Search", use_container_width=True, key="search_arxiv"):
                if search_query.strip():
                    with st.spinner("🔍 Searching arXiv..."):
                        search_results = search_arxiv(search_query, max_results=max_results)
                        if not search_results:
                            st.warning("No results found. Try a different query.")
                        else:
                            st.session_state["arxiv_search_results"] = search_results
                            st.success(f"✅ Found {len(search_results)} papers")
                else:
                    st.warning("Please enter a search query")

            # Display search results with better UI
            if st.session_state["arxiv_search_results"]:
                st.markdown(f"**📄 {len(st.session_state['arxiv_search_results'])} Results:**")
                
                for i, item in enumerate(st.session_state["arxiv_search_results"]):
                    with st.container():
                        # Paper title and checkbox
                        col1, col2 = st.columns([5, 1])
                        with col1:
                            st.markdown(f"**{i+1}. {item['title'][:60]}...**" if len(item['title']) > 60 else f"**{i+1}. {item['title']}**")
                        with col2:
                            checkbox_key = f"select_{i}_{item['id']}"
                            is_selected = st.checkbox("✓", key=checkbox_key, label_visibility="collapsed")
                        
                        # Authors and summary
                        st.caption(f"👥 {item['authors'][:80]}..." if len(item['authors']) > 80 else f"👥 {item['authors']}")
                        
                        # Summary in expander
                        with st.expander("📖 Abstract"):
                            st.write(item['summary'])
                            st.markdown(f"[View on arXiv]({item['abs_url']}) • [Download PDF]({item['pdf_url']})")
                        
                        # Update selection
                        if is_selected and item['pdf_url'] not in st.session_state["selected_arxiv_pdfs"]:
                            st.session_state["selected_arxiv_pdfs"].append(item['pdf_url'])
                        elif not is_selected and item['pdf_url'] in st.session_state["selected_arxiv_pdfs"]:
                            st.session_state["selected_arxiv_pdfs"].remove(item['pdf_url'])
                        
                        st.markdown("---")

            # Show selected papers summary
            if st.session_state["selected_arxiv_pdfs"]:
                st.success(f"✅ {len(st.session_state['selected_arxiv_pdfs'])} paper(s) selected")
                if st.button("🗑️ Clear Selection", use_container_width=True):
                    st.session_state["selected_arxiv_pdfs"] = []
                    st.rerun()
        
        st.markdown("---")
        
        # Process URLs and combine all sources
        pdf_urls = []
        if pdf_urls_input:
            pdf_urls = [
                url.strip() 
                for url in pdf_urls_input.replace(',', '\n').split('\n') 
                if url.strip()
            ]

        # Add selected arXiv PDFs
        if "selected_arxiv_pdfs" in st.session_state and st.session_state["selected_arxiv_pdfs"]:
            pdf_urls = list(dict.fromkeys(pdf_urls + st.session_state["selected_arxiv_pdfs"]))

        # Download PDFs from URLs
        url_pdf_files = []
        
        # Combine all PDFs
        pdf_docs = []
        if uploaded_files:
            pdf_docs.extend(uploaded_files)

        # Show processing summary with metrics
        total_files = len(uploaded_files) if uploaded_files else 0
        total_urls = len(pdf_urls)
        total_arxiv = len(st.session_state.get("selected_arxiv_pdfs", []))
        
        if total_files > 0 or total_urls > 0:
            st.markdown("### 📊 Processing Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📄 Files", total_files)
            with col2:
                st.metric("🔗 URLs", total_urls)
            with col3:
                st.metric("🔬 arXiv", total_arxiv)
            
            st.markdown(f"**Total: {total_files + total_urls} document(s)**")

        # Process PDFs button with enhanced UI
        process_disabled = (total_files == 0 and total_urls == 0)
        
        if st.button(
            "🚀 Process All Documents",
            use_container_width=True,
            disabled=process_disabled,
            type="primary"
        ):
            # Download PDFs from URLs first
            if pdf_urls:
                progress_text = "📥 Downloading PDFs from URLs..."
                progress_bar = st.progress(0, text=progress_text)
                
                for idx, url in enumerate(pdf_urls):
                    st.caption(f"Downloading {idx + 1}/{len(pdf_urls)}...")
                    pdf_path = download_pdf_from_url(url)
                    if pdf_path:
                        url_pdf_files.append(open(pdf_path, "rb"))
                    progress_bar.progress((idx + 1) / len(pdf_urls), text=progress_text)
                
                pdf_docs.extend(url_pdf_files)
            
            if pdf_docs:
                with st.spinner("⚙️ Processing documents..."):
                    progress_bar = st.progress(0, text="Starting...")
                    
                    # Extract text
                    progress_bar.progress(0.2, text="📖 Extracting text...")
                    text_chunks = process_pdfs(pdf_docs)
                    
                    if text_chunks:
                        # Create vector store
                        progress_bar.progress(0.7, text="🧠 Creating embeddings...")
                        vector_store_manager.create_vector_store(text_chunks)
                        
                        progress_bar.progress(1.0, text="✅ Complete!")
                        st.success(f"✅ Successfully processed {len(pdf_docs)} document(s)!")
                        st.balloons()
                        
                        # Show statistics
                        st.info(f"📊 Created {len(text_chunks)} text chunks for AI analysis")
                        
                        # Clear selections
                        if "selected_arxiv_pdfs" in st.session_state:
                            st.session_state["selected_arxiv_pdfs"] = []
                    else:
                        st.error("❌ Failed to extract text from documents")
        
        if process_disabled:
            st.info("👆 Upload files or add URLs to get started")
        
        st.markdown("---")
        
        # Help section with tips
        with st.expander("💡 Help & Tips"):
            st.markdown("""
            **Quick Guide:**
            
            1️⃣ **Upload Documents**
            - Drag & drop PDF files
            - Enter PDF URLs
            - Search & select from arXiv
            
            2️⃣ **Process**
            - Click "Process All Documents"
            - Wait for completion
            
            3️⃣ **Chat**
            - Ask questions about your papers
            - Use quick actions for summaries
            - Export or clear chat history
            
            **Tips:**
            - ✨ You can mix local files, URLs, and arXiv papers
            - 🔄 Use Clear Chat to start fresh
            - 📋 Use Summarize for quick overviews
            - 💾 Processing creates a searchable database
            """)
        
        # Status indicator
        index_exists = os.path.exists("data/faiss_index")
        st.markdown("### 📊 System Status")
        if index_exists:
            st.success("✅ Vector database ready")
        else:
            st.info("ℹ️ No documents processed yet")

        return pdf_docs

def render_chat_interface(index_exists: bool):
    """Render the main chat interface"""
    
    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if index_exists:
        # Header with stats
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown("### 💬 AI Chat Assistant")
            st.caption("Ask questions and get instant answers from your documents")
        with col2:
            if st.session_state.chat_history:
                st.metric("Messages", len(st.session_state.chat_history) * 2)
        
        st.markdown("---")
        
        # Quick action buttons
        st.markdown("#### ⚡ Quick Actions")
        quick_cols = st.columns(5)
        
        quick_actions = [
            ("📋 Summarize", "Please provide a comprehensive summary of all the documents"),
            ("🎯 Main Topics", "What are the main topics discussed in these documents?"),
            ("💡 Key Findings", "What are the key findings and important results?"),
            ("🔬 Methodology", "Explain the research methodology or approach used"),
            ("📊 Conclusions", "What are the main conclusions and implications?")
        ]
        
        for idx, (label, question) in enumerate(quick_actions):
            with quick_cols[idx]:
                if st.button(label, key=f"quick_{idx}", help=f"Ask: {question}"):
                    # Process the quick question
                    with st.spinner("🤔 AI is thinking..."):
                        try:
                            response = chat_handler.handle_user_query(question, st.session_state.chat_history)
                            st.session_state.chat_history.append({
                                "user": question,
                                "assistant": response
                            })
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
        
        st.markdown("---")
        
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("### 📜 Conversation History")
            
            # Container for chat messages
            chat_container = st.container()
            
            with chat_container:
                for idx, entry in enumerate(st.session_state.chat_history):
                    # User message
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(entry["user"])
                    
                    # Assistant message
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(entry["assistant"])
            
            st.markdown("---")
        else:
            st.info("👋 Start a conversation by typing a question below or using the quick actions above!")
        
        # Action buttons row
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col2:
            if st.button("📋 Full Summary", use_container_width=True, help="Generate comprehensive summary"):
                with st.spinner("📝 Generating detailed summary..."):
                    try:
                        summary = chat_handler.summarize_research_papers()
                        st.session_state.chat_history.append({
                            "user": "Generate a comprehensive summary of all research papers",
                            "assistant": summary
                        })
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        with col3:
            if st.button("🗑️ Clear Chat", use_container_width=True, help="Clear conversation history"):
                st.session_state.chat_history = []
                st.rerun()
        
        with col4:
            if st.button("📥 Export", use_container_width=True, help="Export chat history"):
                if st.session_state.chat_history:
                    # Create export text
                    export_text = "# Chat History Export\n\n"
                    for idx, entry in enumerate(st.session_state.chat_history, 1):
                        export_text += f"## Q{idx}: {entry['user']}\n\n"
                        export_text += f"**A{idx}:** {entry['assistant']}\n\n"
                        export_text += "---\n\n"
                    
                    st.download_button(
                        label="💾 Download",
                        data=export_text,
                        file_name="chat_history.md",
                        mime="text/markdown"
                    )
                else:
                    st.warning("No chat history to export")
        
        # Main chat input
        user_query = st.chat_input("💭 Type your question here and press Enter...")
        
        # Handle pending question (from quick actions)
        if "pending_question" in st.session_state:
            user_query = st.session_state.pending_question
            del st.session_state.pending_question
        
        if user_query:
            with st.spinner("🤔 AI is analyzing your question..."):
                try:
                    response = chat_handler.handle_user_query(
                        user_query,
                        st.session_state.chat_history
                    )
                    
                    # Store the new exchange
                    st.session_state.chat_history.append({
                        "user": user_query,
                        "assistant": response
                    })
                    
                    # Rerun to display the new message
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error processing your question: {str(e)}")
                    st.info("💡 Tip: Try rephrasing your question or check if the documents are properly processed")
    
    else:
        # Welcome screen when no documents are processed
        st.markdown("### 👋 Welcome to Research Document Summarizer!")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style='text-align: center; padding: 2rem;'>
                <h2 style='color: #667eea;'>🚀 Get Started in 3 Easy Steps</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Step-by-step guide
            st.markdown("""
            <div style='background: white; padding: 1.5rem; border-radius: 15px; margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                <h3 style='color: #667eea;'>1️⃣ Upload Documents</h3>
                <p>Use the sidebar to upload PDF files, enter URLs, or search arXiv for research papers</p>
            </div>
            
            <div style='background: white; padding: 1.5rem; border-radius: 15px; margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                <h3 style='color: #667eea;'>2️⃣ Process & Analyze</h3>
                <p>Click "Process All Documents" to extract text and create AI-powered embeddings</p>
            </div>
            
            <div style='background: white; padding: 1.5rem; border-radius: 15px; margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                <h3 style='color: #667eea;'>3️⃣ Chat & Explore</h3>
                <p>Ask questions, get summaries, and discover insights from your research papers</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Features showcase
        st.markdown("### ✨ Powerful Features")
        
        feat_col1, feat_col2, feat_col3 = st.columns(3)
        
        with feat_col1:
            st.markdown("""
            **📚 Multi-Source Support**
            - Local PDF files
            - Direct URLs
            - arXiv integration
            - Batch processing
            """)
        
        with feat_col2:
            st.markdown("""
            **🤖 AI-Powered Chat**
            - Context-aware answers
            - Quick action buttons
            - Chat history tracking
            - Export conversations
            """)
        
        with feat_col3:
            st.markdown("""
            **🔍 Smart Analysis**
            - Auto-summarization
            - Key findings extraction
            - Methodology analysis
            - Citation-ready outputs
            """)
        
        st.markdown("---")
        
        # Example questions
        st.markdown("### 🎯 Example Questions You Can Ask")
        
        ex_col1, ex_col2 = st.columns(2)
        
        with ex_col1:
            st.markdown("""
            - "What is the main contribution of this research?"
            - "Summarize the methodology used"
            - "What are the experimental results?"
            - "Compare findings across documents"
            """)
        
        with ex_col2:
            st.markdown("""
            - "What datasets were used?"
            - "What are the limitations?"
            - "What future work is suggested?"
            - "Explain the key concepts"
            """)
        
        st.markdown("---")
        
        # Call to action
        st.info("👈 **Ready to start?** Use the sidebar to upload your first document!")
        
        # Tips section
        with st.expander("💡 Pro Tips for Best Results"):
            st.markdown("""
            **Getting Better Answers:**
            - Be specific with your questions
            - Reference particular sections if needed
            - Use follow-up questions for deeper insights
            - Try the quick action buttons for common queries
            
            **Document Processing:**
            - Ensure PDFs are text-based (not scanned images)
            - Process related papers together for better context
            - Wait for complete processing before asking questions
            
            **Maximizing Features:**
            - Use arXiv search to find latest research
            - Export chat history for future reference
            - Clear chat to start fresh on new topics
            - Combine multiple sources for comprehensive analysis
            """)