import os
from huggingface_hub import HfApi
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def upload_database_to_hf():
    api = HfApi()

    HF_TOKEN = os.getenv("HF_TOKEN")
    if not HF_TOKEN:
        logger.error("HF_TOKEN environment variable not found!")
        return

    DATASET_REPO_ID = "khangbkk23/epstein-rag-portfolio"

    faiss_path = "./data/faiss_index/vector_index.faiss"
    metadata_path = "./data/faiss_index/metadata.pkl"
    
    if not os.path.exists(faiss_path) or not os.path.exists(metadata_path):
        logger.error("Files cannot be found!")
        return

    try:
        api.upload_file(
            path_or_fileobj=faiss_path,
            path_in_repo="vector_index.faiss",
            repo_id=DATASET_REPO_ID,
            repo_type="dataset",
            token=HF_TOKEN
        )
        logger.info("Uploading FAISS successfully!")

        api.upload_file(
            path_or_fileobj=metadata_path,
            path_in_repo="metadata.pkl",
            repo_id=DATASET_REPO_ID,
            repo_type="dataset",
            token=HF_TOKEN
        )
        logger.info("Uploading process is successful")
        
    except Exception as e:
        logger.error(f"{e}")

if __name__ == "__main__":
    upload_database_to_hf()