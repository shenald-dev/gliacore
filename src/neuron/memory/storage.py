"""
Long-Term Memory & Knowledge Storage for NEURON
SQLite-backed persistent knowledge base with full-text search and vector retrieval.
"""

import sqlite3
import math
import json
from typing import List, Dict, Any, Optional, Tuple


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Computes exact cosine similarity between two float vectors."""
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class KnowledgeStorage:
    """
    Persistent long-term memory engine.
    Stores domain knowledge, code indices, and validated task histories.
    """

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_schema()

    def _init_schema(self) -> None:
        """Create tables for knowledge, vectors, and execution history."""
        with self.conn:
            # 1. Structured Knowledge Table
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 2. Validated Execution Histories
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS task_history (
                    task_id TEXT PRIMARY KEY,
                    prompt TEXT NOT NULL,
                    category TEXT NOT NULL,
                    plan_summary TEXT,
                    final_output TEXT NOT NULL,
                    verification_status TEXT NOT NULL,
                    latency_ms REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 3. Create full-text search index if supported
            try:
                self.conn.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
                        id, title, content, tokenize='porter'
                    )
                """)
            except Exception:
                # Fallback if fts5 module is disabled in sqlite3
                pass

    def store_knowledge(self, doc_id: str, title: str, category: str, content: str, embedding: Optional[List[float]] = None) -> None:
        """Store a document with optional vector embedding."""
        emb_json = json.dumps(embedding) if embedding else None
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO knowledge (id, title, category, content, embedding_json) VALUES (?, ?, ?, ?, ?)",
                (doc_id, title, category, content, emb_json)
            )
            try:
                self.conn.execute(
                    "INSERT OR REPLACE INTO knowledge_fts (id, title, content) VALUES (?, ?, ?)",
                    (doc_id, title, content)
                )
            except Exception:
                pass

    def search_keyword(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search knowledge using FTS5 or LIKE query."""
        results = []
        try:
            cursor = self.conn.execute(
                "SELECT id, title, content FROM knowledge_fts WHERE knowledge_fts MATCH ? LIMIT ?",
                (query, limit)
            )
            for row in cursor.fetchall():
                results.append({"id": row[0], "title": row[1], "content": row[2], "match_type": "fts5"})
        except Exception:
            # Fallback to standard LIKE
            cursor = self.conn.execute(
                "SELECT id, title, content FROM knowledge WHERE content LIKE ? OR title LIKE ? LIMIT ?",
                (f"%{query}%", f"%{query}%", limit)
            )
            for row in cursor.fetchall():
                results.append({"id": row[0], "title": row[1], "content": row[2], "match_type": "like"})
        return results

    def search_vector(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Perform exact cosine similarity search across stored vector embeddings."""
        cursor = self.conn.execute("SELECT id, title, category, content, embedding_json FROM knowledge WHERE embedding_json IS NOT NULL")
        scored_docs = []

        for row in cursor.fetchall():
            doc_id, title, category, content, emb_str = row
            try:
                doc_vec = json.loads(emb_str)
                score = cosine_similarity(query_vector, doc_vec)
                scored_docs.append({
                    "id": doc_id,
                    "title": title,
                    "category": category,
                    "content": content,
                    "similarity": round(score, 4)
                })
            except Exception:
                continue

        scored_docs.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_docs[:limit]

    def record_task_history(self, task_id: str, prompt: str, category: str, plan: str, output: str, status: str, latency_ms: float) -> None:
        """Record verified task execution history."""
        with self.conn:
            self.conn.execute(
                """INSERT OR REPLACE INTO task_history 
                   (task_id, prompt, category, plan_summary, final_output, verification_status, latency_ms)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (task_id, prompt, category, plan, output, status, latency_ms)
            )

    def close(self) -> None:
        """Close connection."""
        self.conn.close()
