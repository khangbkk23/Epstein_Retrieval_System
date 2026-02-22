from attr import dataclass
import yaml
from pydantic import BaseModel

@dataclass
class DatasetConfig(BaseModel):
    name: str
    index_dir: str

@dataclass
class ChunkingConfig(BaseModel):
    chunk_size: int
    chunk_overlap: int
    
@dataclass
class EmbeddingConfig(BaseModel):
    model_name: str
    vector_dimension: int
    device: str
    batch_size: int

class AppConfig(BaseModel):
    dataset: DatasetConfig
    chunking: ChunkingConfig
    embedding: EmbeddingConfig
    
    @classmethod
    def load_from_yaml(cls, path: str = "../config.yaml") -> "AppConfig":
        with open(path, 'r') as f:
            yaml_data = yaml.safe_load(f)
        return cls(**yaml_data)
    

settings = AppConfig.load_from_yaml()
        
    