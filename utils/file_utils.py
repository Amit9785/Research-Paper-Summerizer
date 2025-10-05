import requests
import tempfile
import streamlit as st
from typing import Optional, List, Dict
import xml.etree.ElementTree as ET

def download_pdf_from_url(url: str) -> Optional[str]:
    """Download PDF from online link and return local file path"""
    try:
        # Handle arXiv URLs - convert to direct PDF URL
        if 'arxiv.org/abs/' in url:
            # Convert from https://arxiv.org/abs/1512.03385 to https://arxiv.org/pdf/1512.03385.pdf
            paper_id = url.split('/abs/')[-1].replace('.pdf', '')
            url = f"https://arxiv.org/pdf/{paper_id}.pdf"
            st.info(f"Converting arXiv URL to direct PDF link: {url}")
        
        # Handle other common academic paper URLs
        elif 'arxiv.org/pdf/' not in url and 'arxiv.org' in url:
            # Handle other arXiv URL formats
            if '/abs/' in url:
                paper_id = url.split('/abs/')[-1].replace('.pdf', '')
                url = f"https://arxiv.org/pdf/{paper_id}.pdf"
                st.info(f"Converting arXiv URL to direct PDF link: {url}")
        
        # Handle other common academic paper URL patterns
        elif 'researchgate.net' in url and '/publication/' in url:
            st.warning("ResearchGate URLs may not work directly. Please try to find the direct PDF link or upload the file manually.")
        
        elif 'academia.edu' in url:
            st.warning("Academia.edu URLs may not work directly. Please try to find the direct PDF link or upload the file manually.")
        
        elif 'scholar.google.com' in url:
            st.warning("Google Scholar URLs are not direct PDF links. Please find the actual PDF URL or upload the file manually.")
        
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        response.raise_for_status()
        
        # Validate content type
        content_type = response.headers.get('content-type', '').lower()
        if 'application/pdf' not in content_type:
            st.warning(f"Warning: URL may not be a PDF file (Content-Type: {content_type})")
            # Still try to process it as it might be a valid PDF with wrong content-type
        
        # Validate PDF content by checking magic bytes
        if not response.content.startswith(b'%PDF'):
            st.error(f"Downloaded content is not a valid PDF file from {url}")
            return None
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            tmp_pdf.write(response.content)
            return tmp_pdf.name
            
    except requests.RequestException as e:
        st.error(f"Failed to download PDF from {url}: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error downloading PDF: {e}")
        return None

def cleanup_temp_files(file_paths: list):
    """Clean up temporary files"""
    import os
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            st.warning(f"Could not clean up temporary file {file_path}: {e}")


def search_arxiv(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Search arXiv for research papers and return basic metadata.

    Returns a list of dicts with: title, authors, summary, abs_url, pdf_url, published, id
    """
    if not query or not query.strip():
        return []

    try:
        base_url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
        headers = {
            "User-Agent": "RAG-Research-Summarizer/1.0 (https://example.com)"
        }

        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()

        # Parse Atom XML
        root = ET.fromstring(response.text)
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }

        results: List[Dict[str, str]] = []
        for entry in root.findall("atom:entry", ns):
            paper_id = entry.findtext("atom:id", default="", namespaces=ns)
            title = entry.findtext("atom:title", default="", namespaces=ns).strip()
            summary = entry.findtext("atom:summary", default="", namespaces=ns).strip()
            published = entry.findtext("atom:published", default="", namespaces=ns)

            # Authors
            authors: List[str] = []
            for author in entry.findall("atom:author", ns):
                name = author.findtext("atom:name", default="", namespaces=ns)
                if name:
                    authors.append(name)

            # Links
            abs_url = ""
            pdf_url = ""
            for link in entry.findall("atom:link", ns):
                rel = link.attrib.get("rel", "")
                href = link.attrib.get("href", "")
                title_attr = link.attrib.get("title", "")
                if rel == "alternate" and "arxiv.org/abs/" in href:
                    abs_url = href
                if title_attr.lower() == "pdf" or (rel == "related" and href.endswith(".pdf")):
                    pdf_url = href

            # Derive pdf_url if missing
            if not pdf_url and abs_url:
                paper_code = abs_url.split("/abs/")[-1]
                pdf_url = f"https://arxiv.org/pdf/{paper_code}.pdf"

            results.append({
                "id": paper_id,
                "title": title,
                "authors": ", ".join(authors),
                "summary": summary,
                "published": published,
                "abs_url": abs_url,
                "pdf_url": pdf_url,
            })

        return results
    except Exception as e:
        st.error(f"Failed to search arXiv: {e}")
        return []