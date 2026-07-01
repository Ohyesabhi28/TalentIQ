"""
Vector Service.

Wraps FAISS to provide efficient vector indexing and similarity search.
Currently relies on faiss.IndexFlatIP for Inner Product (Cosine Similarity on normalized vectors).
"""

from __future__ import annotations

import faiss
import numpy as np

from app.logging_config import get_logger

logger = get_logger(__name__)


class VectorService:
    """
    Manages FAISS index operations.
    """

    def __init__(self, dimension: int = 384) -> None:
        """
        Initialize the FAISS index.
        bge-small-en-v1.5 has an embedding dimension of 384.
        Using IndexFlatIP (Inner Product). If vectors are L2-normalized,
        Inner Product is equivalent to Cosine Similarity.
        """
        self.dimension = dimension
        
        # We need an ID map to map FAISS's sequential integer IDs to our string/UUID IDs.
        # But FAISS IndexFlatIP doesn't natively support arbitrary IDs easily without IndexIDMap.
        # For simplicity in this in-memory implementation, we'll keep a side mapping.
        
        self.index = faiss.IndexFlatIP(self.dimension)
        self._id_map: dict[int, str] = {}
        self._current_id: int = 0

    def add_vectors(self, vectors: np.ndarray, source_ids: list[str]) -> None:
        """
        Add a batch of vectors to the FAISS index.

        Args:
            vectors: Numpy array of shape (N, D).
            source_ids: List of N string identifiers corresponding to the vectors.
        """
        if len(vectors) != len(source_ids):
            raise ValueError("Number of vectors must match number of source IDs.")
        
        if len(vectors) == 0:
            return

        # Ensure vectors are float32 (FAISS requirement)
        if vectors.dtype != np.float32:
            vectors = vectors.astype(np.float32)

        n = len(vectors)
        self.index.add(vectors)
        
        for i in range(n):
            self._id_map[self._current_id + i] = source_ids[i]
            
        self._current_id += n
        logger.info("Added %d vectors to FAISS index. Total: %d", n, self.index.ntotal)

    def search(self, query_vector: np.ndarray, top_k: int = 10) -> list[tuple[str, float]]:
        """
        Search for the top-k most similar vectors.

        Args:
            query_vector: A single embedding of shape (D,).
            top_k: Number of results to return.

        Returns:
            A list of tuples (source_id, similarity_score).
        """
        if self.index.ntotal == 0:
            return []

        # Ensure query is float32 and shape (1, D)
        query = query_vector.astype(np.float32)
        if len(query.shape) == 1:
            query = query.reshape(1, -1)

        # faiss search returns distances (scores) and indices
        scores, indices = self.index.search(query, min(top_k, self.index.ntotal))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:  # -1 means not enough results
                source_id = self._id_map[idx]
                score = float(scores[0][i])
                results.append((source_id, score))
                
        return results

    def rebuild_index(self) -> None:
        """
        Clear the index completely.
        """
        self.index = faiss.IndexFlatIP(self.dimension)
        self._id_map.clear()
        self._current_id = 0
        logger.info("FAISS index rebuilt (cleared).")

    @property
    def total_vectors(self) -> int:
        return self.index.ntotal
