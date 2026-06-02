import logging

from collectors.base import ModelRecord
from collectors.http_client import http_get
from config import COLLECTOR_LIMIT

logger = logging.getLogger(__name__)

CIVITAI_API = "https://civitai.com/api/v1/models"

TYPE_MAP = {
    "Checkpoint": "checkpoint",
    "LORA": "lora",
    "LoCon": "lora",
    "VAE": "vae",
    "Workflows": "workflow",
}


def _map_type(model_type: str) -> str:
    return TYPE_MAP.get(model_type, model_type.lower() if model_type else "model")


def collect() -> list[ModelRecord]:
    records: list[ModelRecord] = []
    params = {"sort": "Newest", "limit": COLLECTOR_LIMIT}

    try:
        resp = http_get(CIVITAI_API, params=params)
        resp.raise_for_status()
        items = resp.json().get("items", [])
    except Exception as e:
        logger.error("Civitai fetch failed: %s", e)
        return records

    for item in items:
        model_id = item.get("id")
        name = item.get("name", "")
        if not name:
            continue

        creator = item.get("creator", {}) or {}
        author = creator.get("username", "")
        model_type = _map_type(item.get("type", ""))
        tags = item.get("tags", []) or []

        records.append(
            ModelRecord(
                model_name=name,
                author=author,
                source_platform="civitai",
                model_type=model_type,
                download_url=f"https://civitai.com/models/{model_id}",
                description=item.get("description", "") or "",
                tags=[t if isinstance(t, str) else t.get("name", "") for t in tags],
            )
        )

    return records
