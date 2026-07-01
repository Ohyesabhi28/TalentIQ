"""
Tests for VectorService (Module 5).
"""

from __future__ import annotations

import numpy as np
import pytest
from app.services.vector import VectorService

def test_vector_service_initialization():
    service = VectorService(dimension=384)
    assert service.total_vectors == 0
    assert service.dimension == 384

def test_vector_addition_and_search():
    service = VectorService(dimension=3)
    
    # Create 3 normalized vectors
    vecs = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ], dtype=np.float32)
    
    source_ids = ["id1", "id2", "id3"]
    
    service.add_vectors(vecs, source_ids)
    assert service.total_vectors == 3
    
    # Search with something close to id1
    query = np.array([0.9, 0.1, 0.0], dtype=np.float32)
    results = service.search(query, top_k=2)
    
    assert len(results) == 2
    assert results[0][0] == "id1"
    # Cosine similarity (inner product) for id1 = 0.9*1 + 0.1*0 + 0 = 0.9
    assert np.isclose(results[0][1], 0.9)

def test_rebuild_index():
    service = VectorService(dimension=3)
    vecs = np.array([[1.0, 0.0, 0.0]], dtype=np.float32)
    service.add_vectors(vecs, ["id1"])
    assert service.total_vectors == 1
    
    service.rebuild_index()
    assert service.total_vectors == 0
