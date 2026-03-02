import logging
from datasets import load_dataset, IterableDataset
from core.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataIngestionPipeline:
    def __init__(self):
        self.dataset_name = settings.dataset.name
        self.split = settings.dataset.split
        self.streaming = settings.dataset.streaming

    def get_data_stream(self) -> IterableDataset:
        logger.info(f"Hugging Face Dataset: {self.dataset_name}")
        logger.info(f"Streaming: {self.streaming} | Split: {self.split}")
        
        try:
            dataset = load_dataset(
                path=self.dataset_name,
                split=self.split,
                streaming=self.streaming,
                trust_remote_code=True
            )
            logger.info("Connect successfully")
            return dataset
        except Exception as e:
            logger.error(f"Error in dataset: {e}")
            raise

if __name__ == "__main__":
    ingestion = DataIngestionPipeline()
    stream = ingestion.get_data_stream()
    
    data_iterator = iter(stream)
    
    for i in range(2):
        record = next(data_iterator)
        print(f"\n[Record {i+1}]")
        print(f"keys: {list(record.keys())}")
        
        text_content = record.get('text', 'Cannot found text field')