import os
import glob
import re
from typing import List, Dict, Any

class PolicyRAGRetriever:
    def __init__(self, docs_dir: str = None):
        if docs_dir is None:
            # Default to docs/knowledge-base relative to project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            docs_dir = os.path.abspath(os.path.join(current_dir, "../../../docs/knowledge-base"))
        self.docs_dir = docs_dir
        self.chunks: List[Dict[str, Any]] = []
        self._load_and_chunk_documents()

    def _load_and_chunk_documents(self):
        self.chunks = []
        if not os.path.exists(self.docs_dir):
            print(f"Warning: RAG docs directory not found at {self.docs_dir}")
            return

        pattern = os.path.join(self.docs_dir, "*.md")
        files = glob.glob(pattern)
        
        for file_path in files:
            doc_name = os.path.basename(file_path)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Split document into sections based on headers (## or #)
                raw_sections = re.split(r'\n(?=#{1,3}\s)', content)
                for section in raw_sections:
                    cleaned_section = section.strip()
                    if not cleaned_section:
                        continue
                    
                    # Extract header title if present
                    header_match = re.match(r'^(#{1,3})\s+(.+)$', cleaned_section, re.MULTILINE)
                    section_title = header_match.group(2) if header_match else doc_name

                    self.chunks.append({
                        "doc_name": doc_name,
                        "title": section_title,
                        "content": cleaned_section,
                        "lower_content": cleaned_section.lower()
                    })
            except Exception as e:
                print(f"Error loading document {file_path}: {e}")

    def query(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search policy chunks using keyword relevance scoring.
        Returns top_k most relevant policy sections with metadata.
        """
        if not self.chunks:
            self._load_and_chunk_documents()

        query_terms = [term.lower() for term in re.findall(r'\w+', query) if len(term) > 2]
        if not query_terms:
            return self.chunks[:top_k]

        scored_chunks = []
        for chunk in self.chunks:
            score = 0
            lower_text = chunk["lower_content"]
            
            # Match query terms against policy content
            for term in query_terms:
                if term in lower_text:
                    # Give higher weight if term appears in title
                    if term in chunk["title"].lower():
                        score += 5
                    else:
                        score += chunk["lower_content"].count(term)
            
            if score > 0:
                scored_chunks.append((score, chunk))

        # Sort descending by score
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        results = [item[1] for item in scored_chunks[:top_k]]
        
        # If no direct keyword matches, return standard top policy chunks
        if not results and self.chunks:
            return self.chunks[:top_k]
            
        return results

# Singleton instance for simple usage across tools
policy_rag = PolicyRAGRetriever()
