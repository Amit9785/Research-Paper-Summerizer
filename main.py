import streamlit as st
import os
from dotenv import load_dotenv
from src.ui_components import setup_page_config, render_sidebar, render_chat_interface
from src.pdf_processor import process_pdfs
from config.settings import UI_CONFIG

# Load environment variables
load_dotenv()

def main():
    """Main application entry point"""
    # Setup page configuration
    setup_page_config()
    
    # Render sidebar for PDF upload/processing
    pdf_docs = render_sidebar()
    
    # Check if FAISS index exists
    index_exists = os.path.exists("data/faiss_index")
    
    # Render main chat interface
    render_chat_interface(index_exists)

if __name__ == "__main__":
    main()