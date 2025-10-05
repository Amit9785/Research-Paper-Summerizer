import re
from typing import List, Optional

def clean_text(text: str) -> str:
    """Clean and normalize extracted text"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

def estimate_tokens(text: str) -> int:
    """Rough estimation of token count"""
    # Simple approximation: ~4 characters per token
    return len(text) // 4

def truncate_text(text: str, max_tokens: int = 4000) -> str:
    """Truncate text to fit within token limits"""
    estimated_tokens = estimate_tokens(text)
    if estimated_tokens <= max_tokens:
        return text
    
    # Calculate approximate character limit
    char_limit = max_tokens * 4
    return text[:char_limit] + "..."

def extract_keywords(text: str, top_k: int = 10) -> List[str]:
    """Extract top keywords from text (simple frequency-based)"""
    # Simple keyword extraction - can be enhanced with NLP libraries
    words = re.findall(r'\b\w{4,}\b', text.lower())
    
    # Common stop words to filter out
    stop_words = {
        'this', 'that', 'with', 'have', 'will', 'from', 'they', 'know',
        'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when',
        'come', 'here', 'just', 'like', 'long', 'make', 'many', 'over',
        'such', 'take', 'than', 'them', 'well', 'were', 'what', 'your'
    }
    
    # Filter and count
    filtered_words = [word for word in words if word not in stop_words]
    word_freq = {}
    for word in filtered_words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:top_k]]