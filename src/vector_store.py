import streamlit as st
import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from typing import List
from config.settings import Config

class VectorStoreManager:
    def __init__(self):
        self.config = Config()
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.config.EMBEDDING_MODEL
        )
    
    @st.cache_resource
    def create_vector_store(_self, text_chunks: List[str]):
        """Convert chunks into embeddings and store in FAISS"""
        vector_store = FAISS.from_texts(
            texts=text_chunks, 
            embedding=_self.embeddings
        )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(_self.config.FAISS_INDEX_PATH), exist_ok=True)
        
        vector_store.save_local(_self.config.FAISS_INDEX_PATH)
        return vector_store
    
    def load_vector_store(self):
        """Load existing FAISS vector store"""
        if not os.path.exists(self.config.FAISS_INDEX_PATH):
            raise FileNotFoundError("FAISS index not found. Please process a PDF first.")
        
        return FAISS.load_local(
            self.config.FAISS_INDEX_PATH,
            self.embeddings,
            allow_dangerous_deserialization=True
        )
    
    def similarity_search(self, query: str, k: int = None):
        """Perform similarity search on vector store"""
        if k is None:
            k = self.config.SIMILARITY_SEARCH_K
        
        vector_store = self.load_vector_store()
        return vector_store.similarity_search(query, k=k)

# Global instance
vector_store_manager = VectorStoreManager()