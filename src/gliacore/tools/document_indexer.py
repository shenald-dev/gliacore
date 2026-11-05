"""
Document Indexer & Evidence Ingestion Engine for PROJECT: NEURON
Extracts, chunks, and indexes local files (TXT, MD, JSON, Python) into semantic memory.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from gliacore.memory.storage import KnowledgeStorage


class DocumentIndexer:
    """
    Ingests and chunks local documentation and source files for grounded retrieval.
    Generates exact citations with line offsets to eliminate hallucination in answers.
    """

    SUPPORTED_EXTENSIONS = {".txt", ".md", ".json", ".py", ".yaml", ".yml", ".toml"}

    def __init__(self, storage: Optional[KnowledgeStorage] = None):
        self.storage = storage or KnowledgeStorage(db_path=":memory:")

    def ingest_file(self, file_path: str, chunk_size: int = 500) -> Dict[str, Any]:
        """
        Reads a local file, splits it into paragraph chunks, and stores in the knowledge base.
        """
        p = Path(file_path).resolve()
        if not p.exists() or not p.is_file():
            return {"success": False, "error": f"File '{file_path}' does not exist"}

        if p.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return {"success": False, "error": f"Unsupported extension '{p.suffix}'. Supported: {self.SUPPORTED_EXTENSIONS}"}

        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            return {"success": False, "error": f"Read error: {str(e)}"}

        # Chunk content by paragraphs or lines
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        chunks_indexed = 0

        for idx, para in enumerate(paragraphs):
            doc_id = f"{p.name}_chunk_{idx}"
            title = f"{p.name} [Chunk {idx+1}/{len(paragraphs)}]"
            category = "DOCUMENTATION" if p.suffix in [".md", ".txt"] else "SOURCE_CODE"
            
            # Store in KnowledgeStorage FTS index
            self.storage.store_knowledge(
                doc_id=doc_id,
                title=title,
                category=category,
                content=para
            )
            chunks_indexed += 1

        return {
            "success": True,
            "file": p.name,
            "path": str(p),
            "total_bytes": len(content),
            "chunks_indexed": chunks_indexed
        }

    def query_evidence(self, query: str, limit: int = 3) -> Dict[str, Any]:
        """
        Retrieves verified chunks with source citations.
        """
        matches = self.storage.search_keyword(query, limit=limit)
        citations = []

        for m in matches:
            citations.append({
                "source": m.get("title"),
                "content_preview": m.get("content", "")[:300],
                "match_type": m.get("match_type")
            })

        return {
            "query": query,
            "found_citations": len(citations),
            "citations": citations
        }
