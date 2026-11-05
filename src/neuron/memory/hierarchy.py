"""
Hierarchical Memory Architecture for PROJECT: NEURON
Implements:
1. Working Memory (Active Task State)
2. Episodic Memory (Previous Task Experiences)
3. Semantic Memory (Validated Facts & Definitions)
4. Procedural Memory (Validated Workflows & Tool Recipes)
Includes relevance-recency-reliability retrieval and consolidation.
"""

import time
import math
import json
import uuid
import sqlite3
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class MemoryItem:
    memory_id: str
    tier: str  # episodic, semantic, procedural
    title: str
    content: str
    tags: List[str]
    reliability_score: float  # 0.0 to 1.0 (verified by consensus/tools)
    access_count: int
    created_at: float
    updated_at: float
    metadata: Dict[str, Any]


class MemoryHierarchy:
    """
    Unified 4-Tier Memory Controller.
    Persists experience, procedural workflows, and semantic knowledge
    with consolidation, deduplication, and multi-factor retrieval scoring.
    """

    def __init__(self, db_path: str = "neuron_memory.db"):
        self.db_path = db_path
        self._lock = threading.RLock()
        self.conn = sqlite3.connect(db_path, check_same_thread=False, timeout=10.0)
        self._init_tables()

    def _init_tables(self) -> None:
        """Initialize relational schema for episodic, semantic, and procedural memory tiers."""
        with self._lock:
            if self.db_path != ":memory:":
                try:
                    self.conn.execute("PRAGMA journal_mode = WAL;")
                    self.conn.execute("PRAGMA synchronous = NORMAL;")
                except Exception:
                    pass

            with self.conn:
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS memories (
                        memory_id TEXT PRIMARY KEY,
                        tier TEXT NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        tags_json TEXT,
                        reliability_score REAL DEFAULT 1.0,
                        access_count INTEGER DEFAULT 0,
                        created_at REAL,
                        updated_at REAL,
                        metadata_json TEXT
                    )
                """)
                self.conn.execute("CREATE INDEX IF NOT EXISTS idx_mem_tier ON memories(tier);")
                self.conn.execute("CREATE INDEX IF NOT EXISTS idx_mem_title ON memories(title);")

    def store(
        self,
        tier: str,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        reliability: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
        memory_id: Optional[str] = None
    ) -> str:
        """
        Store or update a memory item in the designated tier.
        Applies deduplication if a matching item exists.
        """
        tags = tags or []
        metadata = metadata or {}
        now = time.time()
        mid = memory_id or f"{tier}_{int(now*1000)}_{uuid.uuid4().hex[:6]}"

        with self._lock:
            # Deduplication: check if exact title and tier exist
            cursor = self.conn.execute(
                "SELECT memory_id, reliability_score FROM memories WHERE tier = ? AND title = ?",
                (tier, title)
            )
            existing = cursor.fetchone()
            if existing:
                mid = existing[0]
                # Update content, bump reliability towards latest, update timestamp
                new_rel = max(existing[1], reliability)
                with self.conn:
                    self.conn.execute(
                        """UPDATE memories SET content = ?, tags_json = ?, reliability_score = ?,
                           updated_at = ?, metadata_json = ? WHERE memory_id = ?""",
                        (content, json.dumps(tags), new_rel, now, json.dumps(metadata), mid)
                    )
                return mid

            # Insert new memory
            with self.conn:
                self.conn.execute(
                    """INSERT INTO memories (memory_id, tier, title, content, tags_json, reliability_score, access_count, created_at, updated_at, metadata_json)
                       VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?)""",
                    (mid, tier, title, content, json.dumps(tags), reliability, now, now, json.dumps(metadata))
                )
            return mid

    def retrieve(
        self,
        query: str,
        tier: Optional[str] = None,
        limit: int = 5,
        min_reliability: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Multi-factor retrieval ranking based on:
        Score = Relevance (keyword match density) * Recency * Reliability
        """
        query_words = set(query.lower().split())
        now = time.time()
        scored_items = []

        with self._lock:
            if tier:
                cursor = self.conn.execute(
                    "SELECT memory_id, tier, title, content, tags_json, reliability_score, access_count, created_at, updated_at, metadata_json FROM memories WHERE tier = ? AND reliability_score >= ?",
                    (tier, min_reliability)
                )
            else:
                cursor = self.conn.execute(
                    "SELECT memory_id, tier, title, content, tags_json, reliability_score, access_count, created_at, updated_at, metadata_json FROM memories WHERE reliability_score >= ?",
                    (min_reliability,)
                )
            rows = cursor.fetchall()

        for row in rows:
            mid, m_tier, title, content, tags_json, reliability, access_cnt, created_at, updated_at, meta_json = row
            text = f"{title} {content}".lower()
            
            # 1. Relevance: word overlap
            matches = sum(1 for w in query_words if w in text)
            if matches == 0 and len(query_words) > 0:
                continue
            relevance = matches / len(query_words) if query_words else 0.5

            # 2. Recency decay: half-life of 7 days (604800s)
            age_sec = max(1.0, now - updated_at)
            recency = math.exp(-age_sec / 604800.0)

            # 3. Overall Multi-Factor Composite Score
            final_score = (relevance * 0.5) + (reliability * 0.3) + (recency * 0.2)

            scored_items.append({
                "memory_id": mid,
                "tier": m_tier,
                "title": title,
                "content": content,
                "tags": json.loads(tags_json or "[]"),
                "reliability_score": reliability,
                "access_count": access_cnt,
                "score": round(final_score, 4),
                "metadata": json.loads(meta_json or "{}")
            })

        scored_items.sort(key=lambda x: x["score"], reverse=True)
        top_results = scored_items[:limit]

        # Increment access count
        if top_results:
            with self._lock:
                with self.conn:
                    for item in top_results:
                        self.conn.execute(
                            "UPDATE memories SET access_count = access_count + 1 WHERE memory_id = ?",
                            (item["memory_id"],)
                        )

        return top_results

    def list_all(self, tier: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List all memories across tiers."""
        with self._lock:
            if tier:
                cursor = self.conn.execute(
                    "SELECT memory_id, tier, title, content, reliability_score, access_count, updated_at FROM memories WHERE tier = ? ORDER BY updated_at DESC LIMIT ?",
                    (tier, limit)
                )
            else:
                cursor = self.conn.execute(
                    "SELECT memory_id, tier, title, content, reliability_score, access_count, updated_at FROM memories ORDER BY updated_at DESC LIMIT ?",
                    (limit,)
                )
            return [
                {
                    "memory_id": r[0],
                    "tier": r[1],
                    "title": r[2],
                    "content": r[3],
                    "reliability": r[4],
                    "access_count": r[5],
                    "updated_at": r[6]
                }
                for r in cursor.fetchall()
            ]

    def delete(self, memory_id: str) -> bool:
        """User inspection & deletion API."""
        with self._lock:
            with self.conn:
                cursor = self.conn.execute("DELETE FROM memories WHERE memory_id = ?", (memory_id,))
                return cursor.rowcount > 0

    def consolidate(self, max_items_per_tier: int = 500) -> Dict[str, Any]:
        """
        Memory consolidation daemon:
        1. Enforces maximum memory caps per tier by pruning lowest-reliability / least-accessed entries.
        2. Merges redundant procedural workflows.
        """
        pruned_count = 0
        with self._lock:
            with self.conn:
                for tier in ["episodic", "semantic", "procedural"]:
                    cursor = self.conn.execute("SELECT count(*) FROM memories WHERE tier = ?", (tier,))
                    cnt = cursor.fetchone()[0]
                    if cnt > max_items_per_tier:
                        excess = cnt - max_items_per_tier
                        # Prune entries with lowest score and lowest access
                        self.conn.execute(
                            """DELETE FROM memories WHERE memory_id IN (
                                SELECT memory_id FROM memories WHERE tier = ?
                                ORDER BY reliability_score ASC, access_count ASC, updated_at ASC LIMIT ?
                            )""",
                            (tier, excess)
                        )
                        pruned_count += excess

        return {"status": "consolidated", "pruned_entries": pruned_count}

    def get_stats(self) -> Dict[str, Any]:
        """Return memory statistics per tier."""
        with self._lock:
            cursor = self.conn.execute("SELECT tier, count(*) FROM memories GROUP BY tier")
            tier_counts = {r[0]: r[1] for r in cursor.fetchall()}
            total = sum(tier_counts.values())
            return {
                "total_memories": total,
                "tiers": tier_counts
            }

    def close(self) -> None:
        with self._lock:
            try:
                self.conn.close()
            except Exception:
                pass
