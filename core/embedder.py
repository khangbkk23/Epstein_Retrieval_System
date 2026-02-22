import logging
import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
from core.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorEmbedder:
    def __init__(self):
        self.model_name = settings.embedding.model_name
        self.device = settings.embedding.device
        self.batch_size = settings.processing.batch_size
        self.normalize = settings.embedding.normalize
        self.dimension = settings.embedding.dimension
        
        logger.info(f"Initializing Embedding Model: {self.model_name} on {self.device.upper()}")
        try:

            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info("Embedding model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        if not texts:
            logger.warning("Received empty list for embedding. Returning empty array.")
            return np.array([])

        try:
            embeddings = self.model.encode(
                texts,
                batch_size=self.batch_size,
                show_progress_bar=False, 
                normalize_embeddings=self.normalize
            )
            return embeddings
        except Exception as e:
            logger.error(f"Error during batch embedding: {e}")
            raise

if __name__ == "__main__":
    embedder = VectorEmbedder()
    sample_chunks = [
        "CONFIDENTIAL MEMORANDUM This is highly confidential information regarding the event.",
        "There are too many spaces here.",
        "Epstein's financial records from 2005 indicate offshore transfers."
    ]
    
    logger.info(f"Processing batch of {len(sample_chunks)} chunks...")
    vectors = embedder.embed_batch(sample_chunks)
    
    print("\nEMBEDDING RESULTS")
    print(f"Data type: {type(vectors)}")
    print(f"Matrix shape: {vectors.shape}")

    assert vectors.shape[1] == embedder.dimension, "Dimension mismatch between model output and config!"

    print(f"Vector 1: {vectors[0][:5]}")