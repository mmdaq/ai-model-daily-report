from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ModelRecord:
    model_name: str
    author: str
    source_platform: str
    model_type: str = "unknown"
    model_size: str = ""
    is_gguf: int = 0
    quant_method: str = ""
    vae: str = ""
    clip: str = ""
    workflow: str = ""
    download_url: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)

    def dedup_key(self) -> str:
        if self.download_url:
            return f"{self.source_platform}|{self.download_url}"
        return f"{self.source_platform}|{self.model_name}|{self.author}"
