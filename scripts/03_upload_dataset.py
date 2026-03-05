import os
import logging
from huggingface_hub import HfApi
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def upload_database_to_hf():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(BASE_DIR, '.env')
    
    logger.info(f"Đang nạp biến môi trường từ: {env_path}")
    load_dotenv()

    HF_TOKEN = os.getenv("HF_TOKEN")

    if not HF_TOKEN:
        logger.error("CRITICAL: Không tìm thấy biến HF_TOKEN trong môi trường (hoặc tệp .env).")
        return

    api = HfApi()
    DATASET_REPO_ID = "khangbkk23/epstein-faiss-database"

    faiss_path = "./data/faiss_index/vector_index.faiss"
    metadata_path = "./data/faiss_index/metadata.pkl"
    
    if not os.path.exists(faiss_path) or not os.path.exists(metadata_path):
        logger.error("Files cannot be found! Vui lòng kiểm tra lại đường dẫn.")
        return

    try:
        logger.info(f"Đang tiến hành đẩy tệp FAISS lên kho dữ liệu: {DATASET_REPO_ID}...")
        api.upload_file(
            path_or_fileobj=faiss_path,
            path_in_repo="vector_index.faiss",
            repo_id=DATASET_REPO_ID,
            repo_type="dataset", # Đảm bảo bạn đang lưu lên Hugging Face Datasets
            token=HF_TOKEN
        )
        logger.info("Uploading FAISS successfully!")

        logger.info("Đang tiến hành đẩy tệp metadata.pkl...")
        api.upload_file(
            path_or_fileobj=metadata_path,
            path_in_repo="metadata.pkl",
            repo_id=DATASET_REPO_ID,
            repo_type="dataset",
            token=HF_TOKEN
        )        
        logger.info("Uploading process is successful")
        
    except Exception as e:
        logger.error(f"Đã xảy ra lỗi trong quá trình giao tiếp với Hugging Face API: {e}")

if __name__ == "__main__":
    upload_database_to_hf()