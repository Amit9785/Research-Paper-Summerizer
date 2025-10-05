import os
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from typing import List, Dict
from config.settings import Config, PROMPT_TEMPLATES
from src.vector_store import vector_store_manager

class ChatHandler:
    def __init__(self):
        self.config = Config()
        self.chain = self._create_conversational_chain()
        self.summarization_chain = self._create_summarization_chain()
    
    def _create_conversational_chain(self):
        """Build QA chain with Groq LLM"""
        llm = ChatGroq(
            groq_api_key=self.config.GROQ_API_KEY,
            model_name=self.config.GROQ_MODEL_NAME,
            temperature=self.config.TEMPERATURE,
        )
        
        prompt = PromptTemplate(
            template=PROMPT_TEMPLATES["qa_template"],
            input_variables=["context", "question", "chat_history"]
        )
        
        return load_qa_chain(llm=llm, chain_type="stuff", prompt=prompt)
    
    def _create_summarization_chain(self):
        """Build summarization chain with Groq LLM"""
        llm = ChatGroq(
            groq_api_key=self.config.GROQ_API_KEY,
            model_name=self.config.GROQ_MODEL_NAME,
            temperature=0.1,  # Lower temperature for more consistent summaries
        )
        
        prompt = PromptTemplate(
            template=PROMPT_TEMPLATES["summarization_template"],
            input_variables=["context"]
        )
        
        return load_qa_chain(llm=llm, chain_type="stuff", prompt=prompt)
    
    def _format_chat_history(self, chat_history: List[Dict[str, str]]) -> str:
        """Format chat history as a string"""
        chat_history_str = ""
        for entry in chat_history:
            chat_history_str += f"User: {entry['user']}\nAssistant: {entry['assistant']}\n"
        return chat_history_str
    
    def handle_user_query(self, user_question: str, chat_history: List[Dict[str, str]]) -> str:
        """Handle user query against FAISS index and maintain chat history"""
        try:
            # Perform similarity search
            docs = vector_store_manager.similarity_search(user_question)
            
            # Format chat history
            chat_history_str = self._format_chat_history(chat_history)
            
            # Get response from chain
            response = self.chain(
                {
                    "input_documents": docs,
                    "question": user_question,
                    "chat_history": chat_history_str
                },
                return_only_outputs=True
            )
            
            return response["output_text"]
        
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    def summarize_research_papers(self) -> str:
        """Generate a comprehensive summary of all research papers in the vector store"""
        try:
            # Get all documents from the vector store (use a broad query to get more content)
            docs = vector_store_manager.similarity_search("research paper abstract methodology results findings", k=10)
            
            if not docs:
                return "No research papers found in the processed documents. Please process some PDFs first."
            
            # Get response from summarization chain
            response = self.summarization_chain(
                {
                    "input_documents": docs,
                    "question": "summarize"  # Dummy question for the chain
                },
                return_only_outputs=True
            )
            
            return response["output_text"]
        
        except Exception as e:
            return f"Error generating summary: {str(e)}"

# Global instance
chat_handler = ChatHandler()