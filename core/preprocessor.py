import re
import logging
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import settings

logger = logging.getLogger(__name__)

class TextCleaner:
    @staticmethod
    def clean_ocr_text(text: str) -> str:
        if not isinstance(text, str) or not text.strip():
            return ""
            
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        text = re.sub(r'([a-zA-Z]+)-\s+([a-zA-Z]+)', r'\1\2', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

class ChunkingStrategy:
    def __init__(self):
        self.chunk_size = settings.processing.chunk_size
        self.chunk_overlap = settings.processing.chunk_overlap
        self.min_length = settings.processing.min_length
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "(?<=\. )", " ", ""]
        )
        
        logger.info(f"Chunking initial successful: Size={self.chunk_size}, Overlap={self.chunk_overlap}")

    def process_document(self, text: str) -> List[str]:
        cleaned_text = TextCleaner.clean_ocr_text(text)
        
        if len(cleaned_text) < self.min_length:
            return []
        chunks = self.splitter.split_text(cleaned_text)
        return chunks

if __name__ == "__main__":
    sample_noisy_text = """
    CONFIDENTIAL MEMORANDUM
    
    This is highly con-
    fidential infor- mation regarding the event.
    There are   too many \t spaces here.
    """
    
    print(sample_noisy_text)
    
    cleaner = TextCleaner()
    cleaned = cleaner.clean_ocr_text(sample_noisy_text)
    print(cleaned)
    
    print("\nTEST CHUNKING")
    settings.processing.chunk_size = 50
    settings.processing.chunk_overlap = 10
    
    chunker = ChunkingStrategy()
    chunks = chunker.process_document(sample_noisy_text)
    
    for i, c in enumerate(chunks):
        print(f"Chunk {i+1} (Len: {len(c)}): {c}")