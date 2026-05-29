import logging

import requests

from collectors.base import ModelRecord
from config import COLLECTOR_LIMIT, GITHUB_KEYWORDS, GITHUB_TOKEN, REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com/search/repositories"


def _headers() -> dict:
    h = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h


def _search_repos(query: str) -> list[dict]:
    params = {
        "q": query,
        "sort": "updated",
        "order": "desc",
        "per_page": min(COLLECTOR_LIMIT, 30),
    }
    resp = requests.get(
        GITHUB_API, params=params, headers=_headers(), timeout=REQUEST_TIMEOUT
    )
    resp.raise_for_status()
    return resp.json().get("items", [])


def collect() -> list[ModelRecord]:
    records: list[ModelRecord] = []
    seen_urls: set[str] = set()

    for keyword in GITHUB_KEYWORDS:
        try:
            items = _search_repos(keyword)
            for item in items:
                url = item.get("html_url", "")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                full_name = item.get("full_name", "")
                owner = item.get("owner", {}).get("login", "")
                description = item.get("description") or ""
                topics = item.get("topics", [])

                is_gguf = (
                    "gguf" in keyword.lower()
                    or "gguf" in full_name.lower()
                    or "gguf" in description.lower()
                    or any("gguf" in t.lower() for t in topics)
                )

                records.append(
                    ModelRecord(
                        model_name=full_name,
                        author=owner,
                        source_platform="github",
                        model_type="gguf" if is_gguf else "repo",
                        is_gguf=1 if is_gguf else 0,
                        download_url=url,
                        description=description,
                        tags=topics,
                    )
                )
        except Exception as e:
            logger.error("GitHub search '%s' failed: %s", keyword, e)

    return records
