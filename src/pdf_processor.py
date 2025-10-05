import streamlit as st
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, BinaryIO
from config.settings import Config

class PDFProcessor:
    def __init__(self):
        self.config = Config()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP
        )
    
    def extract_text_from_pdfs(self, pdf_files: List[BinaryIO]) -> str:
        """Extract text from uploaded PDFs"""
        text = ""
        for pdf in pdf_files:
            try:
                # Reset file pointer to beginning
                pdf.seek(0)
                
                # Check if file is empty
                if pdf.read(1) == b'':
                    st.warning(f"File {getattr(pdf, 'name', 'unknown')} is empty")
                    continue
                
                # Reset file pointer again
                pdf.seek(0)
                
                pdf_reader = PdfReader(pdf)
                
                # Check if PDF has pages
                if len(pdf_reader.pages) == 0:
                    st.warning(f"PDF {getattr(pdf, 'name', 'unknown')} has no pages")
                    continue
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text += page_text + "\n"
                    except Exception as page_error:
                        st.warning(f"Error extracting text from page {page_num + 1} of {getattr(pdf, 'name', 'unknown')}: {page_error}")
                        continue
                        
            except Exception as e:
                error_msg = str(e)
                if "EOF marker not found" in error_msg:
                    st.error(f"Corrupted PDF file: {getattr(pdf, 'name', 'unknown')}. The file may be incomplete or damaged.")
                elif "not a PDF file" in error_msg.lower():
                    st.error(f"Invalid PDF file: {getattr(pdf, 'name', 'unknown')}. The file is not a valid PDF.")
                else:
                    st.error(f"Error reading {getattr(pdf, 'name', 'unknown')}: {e}")
        return text
    
    def split_text_into_chunks(self, text: str) -> List[str]:
        """Split long text into smaller chunks"""
        return self.text_splitter.split_text(text)
    
    def process_pdfs(self, pdf_files: List[BinaryIO]) -> List[str]:
        """Complete PDF processing pipeline"""
        if not pdf_files:
            return []
        
        # Extract text
        raw_text = self.extract_text_from_pdfs(pdf_files)
        
        if not raw_text.strip():
            st.warning("No text could be extracted from the PDFs.")
            return []
        
        # Split into chunks
        text_chunks = self.split_text_into_chunks(raw_text)
        return text_chunks

# Global instance
pdf_processor = PDFProcessor()

def process_pdfs(pdf_files: List[BinaryIO]) -> List[str]:
    """Process PDFs and return text chunks"""
    return pdf_processor.process_pdfs(pdf_files)