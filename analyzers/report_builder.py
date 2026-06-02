from datetime import date

from jinja2 import Environment, FileSystemLoader, select_autoescape

from analyzers.classifier import (
    CATEGORY_IMAGE_TO_IMAGE,
    CATEGORY_IMAGE_TO_VIDEO,
    CATEGORY_TEXT_LLM,
    CATEGORY_TEXT_TO_IMAGE,
    CATEGORY_TEXT_TO_VIDEO,
    classify,
)
from analyzers.gguf_analyzer import analyze_gguf
from analyzers.model_enricher import enrich_model_card
from config import MAX_MODELS_PER_CATEGORY, REPORT_TEMPLATE_DIR

CATEGORIES = [
    (CATEGORY_TEXT_LLM, "一、文本大模型", "text_llm_models"),
    (CATEGORY_TEXT_TO_IMAGE, "二、文生图模型", "text_to_image_models"),
    (CATEGORY_IMAGE_TO_IMAGE, "三、图生图模型", "image_to_image_models"),
    (CATEGORY_TEXT_TO_VIDEO, "四、文生视频模型", "text_to_video_models"),
    (CATEGORY_IMAGE_TO_VIDEO, "五、图生视频模型", "image_to_video_models"),
]


def _dict_to_record(d: dict):
    from collectors.base import ModelRecord

    return ModelRecord(
        model_name=d.get("model_name", ""),
        author=d.get("author", ""),
        source_platform=d.get("source_platform", ""),
        model_type=d.get("model_type", "unknown"),
        model_size=d.get("model_size", ""),
        is_gguf=d.get("is_gguf", 0),
        quant_method=d.get("quant_method", ""),
        vae=d.get("vae", ""),
        clip=d.get("clip", ""),
        workflow=d.get("workflow", ""),
        download_url=d.get("download_url", ""),
        description=d.get("description", ""),
        tags=[],
    )


def _record_to_dict(record) -> dict:
    return {
        "model_name": record.model_name,
        "author": record.author,
        "source_platform": record.source_platform,
        "model_type": record.model_type,
        "model_size": record.model_size,
        "is_gguf": record.is_gguf,
        "quant_method": record.quant_method,
        "download_url": record.download_url,
        "description": record.description,
        "category": record.model_type,
    }


def enrich_model(model: dict) -> dict:
    record = classify(analyze_gguf(_dict_to_record(model)))
    base = _record_to_dict(record)
    return enrich_model_card(base)


REPORT_MODE_LABELS = {
    "new": "今日新增模型",
    "digest": "今日暂无全新模型，以下为本次采集到的最新模型精选",
    "recent": "今日采集未成功，以下为库内最近收录的模型（请检查网络/代理）",
    "empty": "暂无模型数据，请检查网络连接或平台接口",
}


def build_report_context(
    models: list[dict],
    report_date: date | None = None,
    report_mode: str = "new",
) -> dict:
    report_date = report_date or date.today()
    enriched = [enrich_model(m) for m in models]

    by_category: dict[str, list[dict]] = {cat: [] for cat, _, _ in CATEGORIES}
    for m in enriched:
        cat = m.get("category", CATEGORY_TEXT_LLM)
        if cat in by_category:
            by_category[cat].append(m)

    sections = []
    summary_counts = {}
    for cat_id, title, _ in CATEGORIES:
        items = by_category[cat_id][:MAX_MODELS_PER_CATEGORY]
        summary_counts[cat_id] = len(by_category[cat_id])
        sections.append({
            "id": cat_id,
            "title": title,
            "models": items,
            "total": len(by_category[cat_id]),
            "shown": len(items),
        })

    return {
        "report_date": report_date.isoformat(),
        "report_mode": report_mode,
        "report_mode_label": REPORT_MODE_LABELS.get(report_mode, ""),
        "sections": sections,
        "summary": {
            "text_llm": summary_counts.get(CATEGORY_TEXT_LLM, 0),
            "text_to_image": summary_counts.get(CATEGORY_TEXT_TO_IMAGE, 0),
            "image_to_image": summary_counts.get(CATEGORY_IMAGE_TO_IMAGE, 0),
            "text_to_video": summary_counts.get(CATEGORY_TEXT_TO_VIDEO, 0),
            "image_to_video": summary_counts.get(CATEGORY_IMAGE_TO_VIDEO, 0),
            "total_count": len(enriched),
        },
        "has_new_models": len(enriched) > 0,
    }


def render_html_report(context: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(REPORT_TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("daily_report.html")
    return template.render(**context)
