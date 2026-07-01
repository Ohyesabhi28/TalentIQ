"""
Embedding Service.

Wraps the sentence-transformers library to provide batch embedding generation.
Initializes the model lazily as a singleton to avoid high memory overhead.
"""

from __future__ import annotations

import numpy as np

from app.exceptions import AppError
from app.logging_config import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """
    Service for generating embeddings using a pre-trained local model.
    """
    
    _model = None

    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5") -> None:
        self.model_name = model_name

    def _get_model(self):
        """
        Lazy-load the SentenceTransformer model.
        """
        if EmbeddingService._model is None:
            logger.info("Loading SentenceTransformer model: %s", self.model_name)
            try:
                from sentence_transformers import SentenceTransformer
                # Load the model directly
                EmbeddingService._model = SentenceTransformer(self.model_name)
                logger.info("Successfully loaded model: %s", self.model_name)
            except ImportError:
                logger.error("sentence-transformers is not installed.")
                raise AppError(
                    error_code="MISSING_DEPENDENCY",
                    message="sentence-transformers is not installed.",
                    status_code=500
                )
            except Exception as e:
                logger.exception("Failed to load model %s", self.model_name)
                raise AppError(
                    error_code="MODEL_LOAD_ERROR",
                    message=f"Failed to load model {self.model_name}: {e}",
                    status_code=500
                )
        return EmbeddingService._model

    def generate_embeddings(self, texts: list[str]) -> np.ndarray:
        """
        Generate L2-normalized embeddings for a list of texts.

        Args:
            texts: List of strings to embed.

        Returns:
            A numpy array of shape (N, D) containing the embeddings.
        """
        if not texts:
            # Return an empty array with the correct dtype
            return np.array([], dtype=np.float32)

        model = self._get_model()
        logger.debug("Generating embeddings for %d texts.", len(texts))
        
        try:
            # encode returns a numpy array if convert_to_numpy=True (default)
            embeddings = model.encode(texts, normalize_embeddings=True)
            return embeddings
        except Exception as e:
            logger.exception("Error generating embeddings.")
            raise AppError(
                error_code="EMBEDDING_GENERATION_FAILED",
                message="Failed to generate embeddings from text.",
                status_code=500
            ) from e

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate an L2-normalized embedding for a single string.
        """
        return self.generate_embeddings([text])[0]
