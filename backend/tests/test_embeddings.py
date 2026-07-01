"""
Tests for EmbeddingService (Module 5).
"""

from __future__ import annotations

import numpy as np
import pytest
from app.services.embedding import EmbeddingService

def test_embedding_service_initialization():
    service = EmbeddingService()
    # It should not load until generate is called
    assert EmbeddingService._model is None

def test_embedding_generation_mocked(monkeypatch):
    """
    Since we don't want to download the real 120MB model in quick tests,
    we mock the SentenceTransformer.
    """
    class MockModel:
        def encode(self, texts, normalize_embeddings=True):
            # Return fake embeddings (N, 384)
            shape = (len(texts), 384)
            arr = np.random.rand(*shape).astype(np.float32)
            if normalize_embeddings:
                norms = np.linalg.norm(arr, axis=1, keepdims=True)
                arr = arr / norms
            return arr

    service = EmbeddingService()
    EmbeddingService._model = MockModel()

    vecs = service.generate_embeddings(["test text 1", "test text 2"])
    
    assert vecs.shape == (2, 384)
    # Check L2 normalization (sum of squares ~ 1)
    assert np.allclose(np.linalg.norm(vecs, axis=1), 1.0)
