import os
import faiss
import pickle
import logging
import numpy as np
from typing import List, Dict, Any, Tuple
from core.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.index_dir = settings.storage.index_dir
        self.metadata_path = settings.storage.metadata_path
        self.dimension = settings.embedding.dimension
        self.m_links = 32 
        
        self.index = None
        self.metadata: List[Dict[str, Any]] = []
        
        self._initialize_index()

    def _initialize_index(self):
        logger.info(f"Initializing FAISS HNSW index with dimension: {self.dimension}")

        self.index = faiss.IndexHNSWFlat(self.dimension, self.m_links, faiss.METRIC_INNER_PRODUCT)
        logger.info("FAISS index created successfully.")

    def add_batch(self, embeddings: np.ndarray, batch_metadata: List[Dict[str, Any]]):

        if embeddings.shape[0] != len(batch_metadata):
            logger.error("Mismatch between number of embeddings and metadata records.")
            raise ValueError("Embeddings and metadata must have the same length.")

        embeddings_fp32 = np.asarray(embeddings, dtype=np.float32)
        self.index.add(embeddings_fp32)
        self.metadata.extend(batch_metadata)
        logger.debug(f"Added batch of {len(batch_metadata)} vectors. Total index size: {self.index.ntotal}")

    def save(self):
        logger.info(f"Saving FAISS index to {self.index_dir}...")
        os.makedirs(self.index_dir, exist_ok=True)
        
        index_file = os.path.join(self.index_dir, "vector_index.faiss")
        faiss.write_index(self.index, index_file)
        
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
            
        logger.info(f"Successfully saved {self.index.ntotal} vectors and metadata.")

    def load(self):
        index_file = os.path.join(self.index_dir, "vector_index.faiss")
        if not os.path.exists(index_file) or not os.path.exists(self.metadata_path):
            logger.error("Index or metadata files not found.")
            raise FileNotFoundError("Run the indexing script before loading.")

        logger.info(f"Loading FAISS index from {index_file}...")

        self.index = faiss.read_index(index_file)
        
        with open(self.metadata_path, 'rb') as f:
            self.metadata = pickle.load(f)
            
        logger.info(f"Loaded index with {self.index.ntotal} vectors onto CPU.")

    def search(self, query_vector: np.ndarray) -> List[Tuple[Dict[str, Any], float]]:
        top_k = settings.retrieval.top_k
        score_threshold = settings.retrieval.score_threshold
        rerank_top_k = settings.retrieval.rerank_top_k

        query_fp32 = np.asarray(query_vector, dtype=np.float32).reshape(1, -1)
        distances, indices = self.index.search(query_fp32, top_k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1 and float(dist) >= score_threshold:
                results.append((self.metadata[idx], float(dist)))

        results = sorted(results, key=lambda x: x[1], reverse=True)[:rerank_top_k]
        
        return results