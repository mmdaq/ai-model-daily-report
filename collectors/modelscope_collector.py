import json
import logging

from collectors.base import ModelRecord
from collectors.http_client import http_put
from config import COLLECTOR_LIMIT, MODELSCOPE_API, MODELSCOPE_ORGS

logger = logging.getLogger(__name__)


def _fetch_org_models(org: str) -> list[dict]:
    per_org = max(5, COLLECTOR_LIMIT // len(MODELSCOPE_ORGS))
    payload = json.dumps(
        {"Path": org, "PageNumber": 1, "PageSize": per_org}
    )
    resp = http_put(
        MODELSCOPE_API,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    resp.raise_for_status()
    data = resp.json().get("Data") or resp.json().get("data") or {}
    return data.get("Models") or data.get("models") or []


def collect() -> list[ModelRecord]:
    records: list[ModelRecord] = []
    seen: set[str] = set()

    for org in MODELSCOPE_ORGS:
        try:
            items = _fetch_org_models(org)
        except Exception as e:
            logger.error("ModelScope org '%s' fetch failed: %s", org, e)
            continue

        for item in items:
            name = item.get("Name") or item.get("name") or ""
            if not name:
                continue

            model_id = item.get("Path") or item.get("ModelId") or f"{org}/{name}"
            if model_id in seen:
                continue
            seen.add(model_id)

            chinese_name = item.get("ChineseName") or ""
            description = item.get("Description") or item.get("description") or chinese_name
            task = item.get("Task") or item.get("task") or ""
            tags = item.get("Tags") or item.get("tags") or []

            model_type = "model"
            text = f"{name} {description} {task}".lower()
            if "video" in text or "视频" in text:
                model_type = "video"
            elif "lora" in text:
                model_type = "lora"

            records.append(
                ModelRecord(
                    model_name=name,
                    author=org,
                    source_platform="modelscope",
                    model_type=model_type,
                    download_url=f"https://www.modelscope.cn/models/{model_id}",
                    description=description or task,
                    tags=tags if isinstance(tags, list) else [],
                )
            )

    return records
