import sys
import os
import time
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings
from core.ingestion import DataIngestionPipeline
from core.preprocessor import ChunkingStrategy
from core.embedder import VectorEmbedder
from core.vector_store import VectorStore

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_etl_pipeline():
    logger.info("=== STARTING ETL PIPELINE ===")
    start_time = time.time()

    # 1. Initialize all modules
    ingestion = DataIngestionPipeline()
    chunker = ChunkingStrategy()
    embedder = VectorEmbedder()
    vector_store = VectorStore()

    # 2. Open data stream
    data_stream = ingestion.get_data_stream()
    
    batch_texts = []
    batch_metadata = []
    total_chunks_processed = 0
    total_docs_processed = 0

    logger.info("Processing data stream. PRESS CTRL+C.")

    try:
        # 3. Iterate through the stream
        for doc in data_stream:
            text_content = doc.get('text', '')
            doc_id = doc.get('id', str(total_docs_processed))
            
            if not text_content:
                continue

            # Chunk the document
            chunks = chunker.process_document(text_content)
            
            for chunk_idx, chunk in enumerate(chunks):
                batch_texts.append(chunk)
                batch_metadata.append({
                    "doc_id": doc_id,
                    "chunk_idx": chunk_idx,
                    "text": chunk
                })

                # 4. If batch is full, embed and store
                if len(batch_texts) >= settings.processing.batch_size:
                    embeddings = embedder.embed_batch(batch_texts)
                    vector_store.add_batch(embeddings, batch_metadata)
                    
                    total_chunks_processed += len(batch_texts)
                    logger.info(f"Indexed {total_chunks_processed} chunks so far...")

                    batch_texts.clear()
                    batch_metadata.clear()
                    
            total_docs_processed += 1

    except KeyboardInterrupt:
        logger.warning("\n[!] Process interrupted by user (Ctrl+C). Initiating graceful shutdown...")

    finally:
        
        # 5. Process any remaining chunks in the final incomplete batch
        if batch_texts:
            try:
                embeddings = embedder.embed_batch(batch_texts)
                vector_store.add_batch(embeddings, batch_metadata)
                total_chunks_processed += len(batch_texts)
            except Exception as e:
                logger.error(f"Error processing final batch during shutdown: {e}")

        # 6. Save the final index
        vector_store.save()

        elapsed_time = time.time() - start_time
        logger.info("=== ETL PIPELINE HALTED & SAVED SUCCESSFULLY")
        logger.info(f"Total documents processed: {total_docs_processed}")
        logger.info(f"Total chunks indexed: {total_chunks_processed}")
        logger.info(f"Total time elapsed: {elapsed_time / 60:.2f} minutes")

if __name__ == "__main__":
    run_etl_pipeline()