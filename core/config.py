import yaml
import os
from pydantic import BaseModel, Field

class DatasetConfig(BaseModel):
    name: str
    split: str = "train"
    streaming: bool = True

class StorageConfig(BaseModel):
    index_dir: str
    metadata_path: str

class ProcessingConfig(BaseModel):
    chunk_size: int = Field(gt=0, description="Kích thước tối đa của mỗi chunk")
    chunk_overlap: int = Field(ge=0, description="Độ gối lên nhau giữa các chunk")
    min_length: int = Field(ge=0, description="Độ dài tối thiểu để giữ lại chunk")
    batch_size: int = Field(gt=0, description="Số lượng chunk xử lý đồng thời")

class EmbeddingConfig(BaseModel):
    model_name: str
    dimension: int = Field(gt=0, description="Số chiều của vector")
    device: str
    normalize: bool = True

class RetrievalConfig(BaseModel):
    top_k: int = Field(gt=0, description="Số lượng kết quả truy xuất")
    score_threshold: float = Field(ge=0.0, le=1.0, description="Ngưỡng điểm tương đồng")

class AppConfig(BaseModel):
    dataset: DatasetConfig
    storage: StorageConfig
    processing: ProcessingConfig
    embedding: EmbeddingConfig
    retrieval: RetrievalConfig
    
    @classmethod
    def load_from_yaml(cls, path: str = "../config.yaml") -> "AppConfig":
        if not os.path.exists(path):
            raise FileNotFoundError(f"Cannot find config file at {path}")
            
        with open(path, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)
            
        return cls(**yaml_data)

settings = AppConfig.load_from_yaml()

if __name__ == "__main__":
    print(f"Dataset name: {settings.dataset.name}")
    print(f"Embedding model: {settings.embedding.model_name}")
    print(f"Storage path: {settings.storage.index_dir}")