import logging

from collectors.base import ModelRecord
from collectors.http_client import http_get
from config import COLLECTOR_LIMIT, HF_SEARCH_TERMS

logger = logging.getLogger(__name__)

HF_API = "https://huggingface.co/api/models"


def _is_gguf_model(item: dict) -> bool:
    model_id = item.get("id", "").lower()
    tags = [t.lower() for t in item.get("tags", [])]
    siblings = item.get("siblings", [])
    if "gguf" in tags or "gguf" in model_id:
        return True
    for s in siblings:
        filename = s.get("rfilename", "").lower()
        if filename.endswith(".gguf"):
            return True
    return False


def _extract_size_gb(item: dict) -> str:
    siblings = item.get("siblings", [])
    for s in siblings:
        size = s.get("size")
        if size and s.get("rfilename", "").lower().endswith(".gguf"):
            gb = size / (1024**3)
            return f"{gb:.1f}GB"
    return ""


def _fetch_hf_models(params: dict) -> list[dict]:
    resp = http_get(HF_API, params=params)
    resp.raise_for_status()
    return resp.json()


def collect() -> list[ModelRecord]:
    records: list[ModelRecord] = []
    seen_ids: set[str] = set()

    base_params = {
        "sort": "lastModified",
        "direction": "-1",
        "limit": COLLECTOR_LIMIT,
    }

    try:
        items = _fetch_hf_models(base_params)
        for item in items:
            model_id = item.get("id", "")
            if not model_id or model_id in seen_ids:
                continue
            seen_ids.add(model_id)

            author = model_id.split("/")[0] if "/" in model_id else ""
            is_gguf = _is_gguf_model(item)
            tags = item.get("tags", [])

            records.append(
                ModelRecord(
                    model_name=model_id,
                    author=author,
                    source_platform="huggingface",
                    model_type="gguf" if is_gguf else "model",
                    model_size=_extract_size_gb(item),
                    is_gguf=1 if is_gguf else 0,
                    download_url=f"https://huggingface.co/{model_id}",
                    description=item.get("pipeline_tag", "") or "",
                    tags=tags,
                )
            )
    except Exception as e:
        logger.error("HuggingFace base fetch failed: %s", e)

    for term in HF_SEARCH_TERMS:
        try:
            items = _fetch_hf_models({**base_params, "search": term})
            for item in items:
                model_id = item.get("id", "")
                if not model_id or model_id in seen_ids:
                    continue
                seen_ids.add(model_id)

                author = model_id.split("/")[0] if "/" in model_id else ""
                is_gguf = _is_gguf_model(item)
                tags = item.get("tags", [])

                records.append(
                    ModelRecord(
                        model_name=model_id,
                        author=author,
                        source_platform="huggingface",
                        model_type="gguf" if is_gguf else term,
                        model_size=_extract_size_gb(item),
                        is_gguf=1 if is_gguf else 0,
                        download_url=f"https://huggingface.co/{model_id}",
                        description=item.get("pipeline_tag", "") or "",
                        tags=tags,
                    )
                )
        except Exception as e:
            logger.error("HuggingFace search '%s' failed: %s", term, e)

    return records
