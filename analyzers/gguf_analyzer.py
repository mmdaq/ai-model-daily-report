import re
from typing import Optional

from collectors.base import ModelRecord

QUANT_PATTERN = re.compile(
    r"\b(IQ\d+_[A-Z0-9]+|Q\d+_[A-Z0-9_]+|Q\d+\.\d+_[A-Z0-9_]+|Q\d+_[KMST]+|Q\d+)\b",
    re.IGNORECASE,
)

SIZE_GB_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*gb", re.IGNORECASE)
SIZE_MB_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*mb", re.IGNORECASE)


def extract_quant(text: str) -> str:
    if not text:
        return ""
    match = QUANT_PATTERN.search(text)
    return match.group(1).upper() if match else ""


def extract_size_gb(text: str) -> Optional[float]:
    if not text:
        return None
    gb_match = SIZE_GB_PATTERN.search(text)
    if gb_match:
        return float(gb_match.group(1))
    mb_match = SIZE_MB_PATTERN.search(text)
    if mb_match:
        return float(mb_match.group(1)) / 1024
    return None


def analyze_gguf(record: ModelRecord) -> ModelRecord:
    combined = " ".join(
        [
            record.model_name,
            record.model_size,
            record.description,
            " ".join(record.tags),
        ]
    )

    if record.is_gguf or ".gguf" in combined.lower() or "gguf" in combined.lower():
        record.is_gguf = 1
        record.model_type = "gguf"

    if not record.quant_method:
        record.quant_method = extract_quant(combined)

    if not record.model_size:
        size_gb = extract_size_gb(combined)
        if size_gb is not None:
            record.model_size = f"{size_gb:.1f}GB"

    return record
